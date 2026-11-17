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

Each requirement is then split into atoms -- the conjuncts of its negation
normal form, see _requirement_atoms -- so a report can name the single
conjunct that did not hold rather than the whole boolean expression.

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


# Nodes whose `return`s belong to some other function, not to the action.
_OTHER_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)

_NONE_REQUIRED = frozenset()


def _is_bail(stmt):
    """True for `return`, `return None`, `return False`: the action failing."""
    return isinstance(stmt, ast.Return) and _returns_falsey([stmt])


def _may_return_success(stmt):
    """True if any `return` in this statement could hand back something other than a bail."""
    pending = [stmt]
    while pending:
        node = pending.pop()
        if isinstance(node, ast.Return) and not _is_bail(node):
            return True
        pending.extend(child for child in ast.iter_child_nodes(node)
                       if not isinstance(child, _OTHER_SCOPES))
    return False


def _required_on_success(stmts, after):
    """
    Which `if` requirements hold on every path through `stmts` that succeeds.

    `after` describes what runs once `stmts` falls through, in the same form
    as the result: (may_succeed, required), where `required` is a set of
    (if_node, negated) pairs -- `negated` True when it is `not if_node.test`
    that every succeeding path needs, False when it is the test itself.
    "Succeeds" means returns anything but False or None, which is all the
    explainer ever needs: it only analyses actions the planner recorded as
    not applicable, so an atom is honest exactly when every *other* outcome
    implies it.

    Both halves err in the safe direction. `may_succeed` may say True of a
    block that cannot succeed (that only loses atoms, at an `if` that must
    then keep both branches), and `required` holds only what is necessary --
    so the result never contains a requirement some succeeding path skips.

    The statement kinds, walking backwards from the end of the action:

        return False / return None / return / raise   cannot succeed
        any other return                                succeeds, needs nothing
        if T: A else: B
            A cannot succeed                  ->  `not T`, plus what B needs
            B cannot succeed                  ->  `T`, plus what A needs
            both can                          ->  only what both need
        anything else (loops, with, try, ...) ->  what follows needs, unless a
                                                  success return is inside it

    Nothing inside a loop, `with` or `try` is ever required. A loop body may
    run zero times -- `for o in objs: if blocked[o]: return False` needs
    nothing when `objs` is empty -- and its guards read loop variables no
    trace binds; `try` and `with` may leave their body part way through.
    Function and class definitions nested in the action are never entered:
    their `return`s are not the action's.
    """
    may_succeed, required = after
    for stmt in reversed(stmts):
        if isinstance(stmt, ast.Return):
            if _is_bail(stmt):
                may_succeed, required = False, _NONE_REQUIRED
            else:
                may_succeed, required = True, _NONE_REQUIRED
        elif isinstance(stmt, ast.Raise):
            may_succeed, required = False, _NONE_REQUIRED
        elif isinstance(stmt, ast.If):
            here = (may_succeed, required)
            body_ok, body_req = _required_on_success(stmt.body, here)
            else_ok, else_req = _required_on_success(stmt.orelse, here)
            if not body_ok and not else_ok:
                may_succeed, required = False, _NONE_REQUIRED
            elif not body_ok:
                may_succeed, required = True, else_req | {(stmt, True)}
            elif not else_ok:
                may_succeed, required = True, body_req | {(stmt, False)}
            else:
                may_succeed, required = True, body_req & else_req
        elif isinstance(stmt, _OTHER_SCOPES):
            continue
        elif _may_return_success(stmt):
            may_succeed, required = True, _NONE_REQUIRED
        # Any other statement falls through to what follows, so leaves it as is.
    return may_succeed, required


def _requirement_atoms(test, negated):
    """
    Split one requirement into atoms whose conjunction is exactly it.

    The requirement is `test` itself when `negated` is False, and `not test`
    when it is True (the `if` bails). Only a *conjunction* may be split: each
    conjunct is then necessary on its own, so whichever one evaluates false
    really did block the action. A disjunction may not -- with `A or B` it is
    the combination that fails, so naming one side as "the blocking
    precondition" would be a lie -- and it is kept whole as a single atom.

    Which `and`s and `or`s count as a conjunction depends on the polarity, by
    De Morgan's law:

        requirement `A and B`         ->  A, B
        requirement `not (A or B)`    ->  not A, not B
        requirement `not (A and B)`   ->  kept whole (it is `not A or not B`)
        requirement `A or B`          ->  kept whole

    and `not` flips the polarity of what it wraps. That is the negation normal
    form of the requirement, split at its top-level `and`s -- one rule for
    both idioms, so a bail on `A and B` cannot be split as if its requirement
    were `not A and not B`.

    Returns [(node, negated), ...], every node a sub-expression of `test`, so
    each atom can still be rendered from and evaluated as the domain's own
    source. A `not` is only looked through when that actually splits
    something, except directly under a bail, where it is the double negation
    of `if not (...): return False` and the positive requirement is the clearer
    thing to report.
    """
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        inner = _requirement_atoms(test.operand, not negated)
        if negated or len(inner) > 1:
            return inner
        return [(test, negated)]
    splits_on = ast.Or if negated else ast.And
    if isinstance(test, ast.BoolOp) and isinstance(test.op, splits_on):
        atoms = []
        for value in test.values:
            atoms.extend(_requirement_atoms(value, negated))
        return atoms
    return [(test, negated)]


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

    # An `if` names a precondition exactly when every path on which the action
    # succeeds passes it, and always the same way; the analysis says which
    # way. Both idioms above are instances: a bail forces `not T`, a wrapping
    # guard whose failure falls off the end forces `T`. So do shapes neither
    # spells out, such as `if T: <effects> else: return state` followed by a
    # bail. Without this, a bail nested in another `if` (`if C: if T: return
    # False` requires `not (C and T)`, not `not T`), one of several
    # alternative success branches, or a bail after an earlier `return
    # state`, would each yield an atom that can be false while the action
    # applies. Falling off the end returns None, so the action's own
    # continuation cannot succeed.
    _, on_every_success = _required_on_success(func.body, (False, _NONE_REQUIRED))
    negated_at = dict(on_every_success)

    atoms = []
    for node in ast.walk(func):
        if node not in negated_at:
            continue
        # Under a bail, the dominant form `if not (A and B): return False`
        # requires plainly `A and B`, which _requirement_atoms unwraps and
        # splits so a report can say which of A or B failed. A bail on
        # `A or B` requires `not A and not B` and is split into both; a bail
        # on `A and B` requires only `not (A and B)` and is kept whole.
        for test, negated in _requirement_atoms(node.test, negated_at[node]):
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
