"""
Static extraction of an action's precondition guards from domain source.

GTPyhop domains express preconditions in two structurally *inverted*
idioms, and this module handles both:

  Negative guard-and-bail -- the shape this project's domain style guide
  teaches, and what the newer bundled collections use::

      def a_open_door(state, door):
          if not (hasattr(state, 'door_unlocked') and state.door_unlocked[door]):
              return False
          state.door_open[door] = True
          return state

  The `if` *bails*, so the requirement is the negation of its test.

  Positive wrapping guard -- GTPyhop's original idiom, used by every one of
  the nine Dana Nau collections::

      def pickup(s, x):
          if s.pos[x] == 'table' and s.clear[x] == True and s.holding['hand'] == False:
              s.pos[x] = 'hand'
              return s

  The `if` *wraps the effects*, so the requirement is the test itself, and
  failure falls off the end of the function as None.

Each requirement is then split on its `and`s into atoms, so a report can name
the single conjunct that did not hold rather than the whole boolean
expression. A bail's test is the *negation* of the requirement, so it is not
split on its own `and`s; see _requirement_atoms.

Rendering uses ast.get_source_segment (3.8+) rather than ast.unparse (3.9+),
for the same reason this package parses with stdlib ast instead of LibCST:
gtpyhop-core declares requires-python = ">=3.8".
"""

import ast

__all__ = ["GuardAtom", "ActionGuards", "extract_action_guards", "parse_source"]


class GuardAtom(object):
    """
    One conjunct of an action's precondition, with everything needed to
    evaluate it later and to describe it to a human.

    `negated` records which idiom it came from: an atom lifted from a
    guard-and-bail `if` must be inverted to become a requirement, and the
    evaluator needs to know that to decide whether the atom held.
    """

    __slots__ = ("source", "state_vars", "negated", "node", "lineno")

    def __init__(self, source, state_vars, negated, node, lineno):
        self.source = source
        self.state_vars = tuple(state_vars)
        self.negated = negated
        self.node = node
        self.lineno = lineno

    def __repr__(self):
        shape = "not ({})" if self.negated else "{}"
        return "GuardAtom({!r}, vars={}, line={})".format(
            shape.format(self.source), list(self.state_vars), self.lineno)


class ActionGuards(object):
    """Every precondition atom found for one action, plus its signature."""

    __slots__ = ("name", "params", "state_param", "atoms", "lineno")

    def __init__(self, name, params, state_param, atoms, lineno):
        self.name = name
        self.params = tuple(params)
        self.state_param = state_param
        self.atoms = list(atoms)
        self.lineno = lineno

    def __repr__(self):
        return "ActionGuards({!r}, params={}, {} atom(s))".format(
            self.name, list(self.params), len(self.atoms))


def _returns_falsey(node):
    """True if this statement list bails, i.e. `return False` / `return None`."""
    for stmt in node:
        if isinstance(stmt, ast.Return):
            if stmt.value is None:
                return True
            if isinstance(stmt.value, ast.Constant) and stmt.value.value in (False, None):
                return True
    return False


def _returns_name(node, name):
    """True if this statement list returns the given name (the state param)."""
    for stmt in ast.walk(ast.Module(body=list(node), type_ignores=[])):
        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Name) \
                and stmt.value.id == name:
            return True
    return False


def _requirement_atoms(test, negated):
    """
    Split one requirement into atoms whose conjunction is exactly it.

    The requirement is `test` itself when `negated` is False, and `not test`
    when it is True (the `if` bails). Only a *conjunction* may be split: each
    conjunct is then necessary on its own, so whichever one evaluates false
    really did block the action. Anything else is kept whole as one atom.

        requirement `A and B`         ->  A, B
        requirement `not (not X)`     ->  the atoms of X  (`if not X: return False`)
        requirement `not (A and B)`   ->  kept whole: it is `not A or not B`,
                                          so neither negation is required alone
        requirement `A or B`          ->  kept whole: with a disjunction it is
                                          the combination that fails, and naming
                                          one side would be a lie

    The third line is why a bail's test must not be split on its `and`s: a
    bail on `A and B` fires only when both hold, so splitting it as if its
    requirement were `not A and not B` reports atoms the action never needed.

    Returns [(node, negated), ...], every node a sub-expression of `test`, so
    each atom can still be rendered from and evaluated as the domain's own
    source.
    """
    if negated:
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            return _requirement_atoms(test.operand, False)
        return [(test, True)]
    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
        atoms = []
        for value in test.values:
            atoms.extend(_requirement_atoms(value, False))
        return atoms
    return [(test, False)]


def _state_vars_in(node, state_param):
    """
    Collect the state variables an expression reads.

    Recognises the forms GTPyhop domains actually use:
        state.X            attribute access
        state.X[k]         subscript on a state variable
        state.X.get(k)     dict-style access
        hasattr(state,'X') existence check, where X is a literal
    """
    found = []

    for sub in ast.walk(node):
        # hasattr(state, 'X')
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
                and sub.func.id == "hasattr" and len(sub.args) == 2:
            target, attr = sub.args
            if isinstance(target, ast.Name) and target.id == state_param \
                    and isinstance(attr, ast.Constant) and isinstance(attr.value, str):
                if attr.value not in found:
                    found.append(attr.value)
        # state.X  (also the base of state.X[k] and state.X.get(k))
        if isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name) \
                and sub.value.id == state_param:
            if sub.attr not in found and sub.attr != "get":
                found.append(sub.attr)

    return found


def _atom_from(test, source, state_param, negated):
    text = ast.get_source_segment(source, test)
    if text is None:                      # pragma: no cover - defensive
        text = "<unavailable>"
    return GuardAtom(
        source=" ".join(text.split()),
        state_vars=_state_vars_in(test, state_param),
        negated=negated,
        node=test,
        lineno=getattr(test, "lineno", -1),
    )


def extract_action_guards(func, source):
    """
    Pull the precondition atoms out of one action FunctionDef.

    Returns an ActionGuards, or None if the function takes no arguments at
    all (it cannot be a GTPyhop action -- every action takes the state).
    """
    args = [a.arg for a in func.args.args]
    if not args:
        return None
    state_param = args[0]

    atoms = []
    for node in ast.walk(func):
        if not isinstance(node, ast.If):
            continue

        if _returns_falsey(node.body):
            # Guard-and-bail: the requirement is the negation of the test.
            # In the dominant form, `if not (A and B): return False`, that is
            # plainly `A and B`, which _requirement_atoms unwraps and splits so
            # a report can say which of A or B failed. A bail on `A and B`
            # itself requires only `not (A and B)` and is kept whole.
            requirement = (node.test, True)
        elif _returns_name(node.body, state_param):
            # Wrapping guard: the test itself is the requirement. Not
            # descended into further.
            requirement = (node.test, False)
        elif node.orelse and _returns_falsey(node.orelse):
            # `if <cond>: <something> else: return False` -- the else bails,
            # so the test is the requirement, exactly as for a wrapping guard.
            #
            # Reached only when neither branch above fired, which is what
            # keeps it from double-counting: in the common
            # `if cond: ...; return s else: return False`, the body already
            # returns the state and was handled above, and adding the test a
            # second time here would report the same atom twice. No action in
            # the bundled examples needs this branch today -- every `else:
            # return False` there has a body the earlier cases already
            # recognise -- but the shape is legal and appears in generated
            # domains, which are what this package exists to diagnose.
            requirement = (node.test, False)
        else:
            continue

        for test, negated in _requirement_atoms(*requirement):
            atoms.append(_atom_from(test, source, state_param, negated=negated))

    return ActionGuards(
        name=func.name, params=args, state_param=state_param,
        atoms=atoms, lineno=func.lineno,
    )


def parse_source(text, filename="<domain>"):
    """
    Index every top-level and nested function in a source file by name.

    Returns {name: (FunctionDef, source_text)}. Actions are matched by name
    because GTPyhop registers an action under its function's __name__
    (`declare_actions` does `{act.__name__: act for act in actions}`), which
    is exactly what a TraceEvent's item tuple carries.
    """
    tree = ast.parse(text, filename=filename)
    return dict(
        (node.name, (node, text))
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    )
