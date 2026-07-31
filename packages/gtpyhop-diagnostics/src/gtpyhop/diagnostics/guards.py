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

Each requirement is then split on `and` into atoms, so a report can name the
single conjunct that did not hold rather than the whole boolean expression.

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


def _split_conjuncts(test):
    """Break `a and b and c` into [a, b, c]; anything else stays whole.

    `or` is deliberately NOT split: with a disjunction it is the combination
    that fails, so naming one side as "the blocking precondition" would be a
    lie. The whole expression is kept as a single atom instead.
    """
    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
        atoms = []
        for value in test.values:
            atoms.extend(_split_conjuncts(value))
        return atoms
    return [test]


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
            #
            # The dominant form is `if not (A and B): return False`, where
            # the requirement is plainly `A and B` -- so unwrap the `not`
            # first and split *that*. Otherwise the whole conjunction would
            # be reported as one opaque atom and the report could only say
            # "not (A and B) failed", when it could say which of A or B did.
            if isinstance(node.test, ast.UnaryOp) and isinstance(node.test.op, ast.Not):
                for conjunct in _split_conjuncts(node.test.operand):
                    atoms.append(_atom_from(conjunct, source, state_param, negated=False))
            else:
                # e.g. `if state.broken[x]: return False` -- the requirement
                # is the negation, which cannot be decomposed further.
                for conjunct in _split_conjuncts(node.test):
                    atoms.append(_atom_from(conjunct, source, state_param, negated=True))
        elif _returns_name(node.body, state_param):
            # Wrapping guard: the test itself is the requirement. Not split
            # by `or` (see _split_conjuncts) and not descended into further.
            for conjunct in _split_conjuncts(node.test):
                atoms.append(_atom_from(conjunct, source, state_param, negated=False))

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
