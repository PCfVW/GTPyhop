"""
Join an action's static precondition guards with the state it actually failed
against, and name the ones that did not hold.

The two halves this brings together:

  * `gtpyhop.diagnostics.guards` reads the domain source and yields the
    *candidate* preconditions of an action. On its own that is all a static
    analysis can offer -- for `pickup` it lists three guards and cannot say
    which one blocked the plan.
  * `TraceEvent.state` (gtpyhop-core 2.0.0, `find_plan(..., trace_state=True)`)
    supplies the state the action was evaluated on.

Evaluating each atom against that snapshot is what turns "here are three
candidate preconditions" into "clear['a'] was False".

Why evaluate rather than pattern-match: a `TraceEvent`'s item tuple carries
the action's *actual arguments* -- ('pickup', 'a') -- and the FunctionDef
carries its parameter names. Binding those together lets each conjunct be
executed exactly as the planner would have, which handles comparisons,
helper calls and arbitrary expressions that no reasonable amount of pattern
matching would cover.

On executing domain code: `find_plan` has already called these very
functions, so evaluating a sub-expression of one of their guards adds no
exposure that planning did not. Nothing here is a sandbox, and it is not
meant to be one -- if a domain is untrusted, it was already untrusted when
it was planned with.
"""

import ast
import os

from .guards import extract_action_guards, parse_source

__all__ = ["AtomResult", "DeadEndReport", "explain_dead_end", "load_guards"]

# TraceEvent statuses that mean "an action's preconditions did not hold".
# None and False both land on not_applicable as of gtpyhop-core 2.0.0.
_PRECONDITION_FAILURE = ("not_applicable",)
_REFINEMENT_DEAD_ENDS = (
    "task_exhausted", "goal_exhausted", "multigoal_exhausted",
)


class AtomResult(object):
    """One precondition atom, evaluated (or not) against the snapshot."""

    __slots__ = ("atom", "held", "reason")

    def __init__(self, atom, held, reason=None):
        self.atom = atom
        self.held = held          # True, False, or None when not evaluated
        self.reason = reason      # why it could not be evaluated, if so

    @property
    def source(self):
        return self.atom.source

    @property
    def state_vars(self):
        return self.atom.state_vars

    def __repr__(self):
        if self.held is None:
            return "AtomResult({!r}, unevaluated: {})".format(self.source, self.reason)
        return "AtomResult({!r}, held={})".format(self.source, self.held)


class DeadEndReport(object):
    """
    Why the search stopped where it did.

    `blocking` is the answer most callers want: the precondition atoms that
    were false in the state the action was tried on. `candidates` is every
    atom found, and `unevaluated` those that could not be decided -- kept
    separate so an inconclusive result never masquerades as a clean one.
    """

    __slots__ = ("event", "action", "args", "candidates", "unevaluated",
                 "status", "note")

    def __init__(self, event, action, args, candidates, unevaluated, status, note=None):
        self.event = event
        self.action = action
        self.args = args
        self.candidates = candidates
        self.unevaluated = unevaluated
        self.status = status
        self.note = note

    @property
    def blocking(self):
        """Atoms that evaluated false -- the preconditions that did not hold."""
        return [r for r in self.candidates if r.held is False]

    @property
    def blocking_vars(self):
        """State variable names mentioned by the blocking atoms, in order."""
        seen = []
        for result in self.blocking:
            for var in result.state_vars:
                if var not in seen:
                    seen.append(var)
        return seen

    def summary(self):
        """A one-line human-readable explanation."""
        if self.action is None:
            return self.note or "no dead end recorded"
        if not self.blocking:
            detail = self.note or "no precondition atom evaluated false"
            return "{}{} -- {}".format(self.action, _fmt_args(self.args), detail)
        parts = "; ".join(r.source for r in self.blocking)
        return "{}{} was blocked by: {}".format(
            self.action, _fmt_args(self.args), parts)

    def __repr__(self):
        return "DeadEndReport({})".format(self.summary())


def _fmt_args(args):
    if not args:
        return "()"
    return "(" + ", ".join(repr(a) for a in args) + ")"


def load_guards(source):
    """
    Build {action_name: (ActionGuards, source_text)} from a file or directory.

    A directory is walked for *.py, so a caller can point at a whole example
    collection without knowing which file defines which action. Files that do
    not parse are skipped rather than raising: one broken module in a tree
    should not stop the rest from being analysed.
    """
    paths = []
    if os.path.isdir(source):
        for root, _dirs, names in os.walk(source):
            if "__pycache__" in root:
                continue
            for name in names:
                if name.endswith(".py"):
                    paths.append(os.path.join(root, name))
    else:
        paths.append(source)

    table = {}
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
            functions = parse_source(text, filename=path)
        except (OSError, SyntaxError, ValueError):
            continue
        for name, (node, src) in functions.items():
            if name in table:
                continue          # first definition wins; see docstring
            guards = extract_action_guards(node, src)
            if guards is not None:
                table[name] = guards
    return table


def _evaluate(atom, state_param, snapshot, bindings, namespace):
    """
    Evaluate one atom against the snapshot.

    Returns (held, reason). `held` is None when the atom could not be
    decided -- an unresolvable helper, or an expression that raised -- and
    `reason` then says why. Guessing would be worse than abstaining: a
    wrong "this precondition failed" sends the reader to the wrong line.
    """
    env = dict(namespace)
    env.update(bindings)
    env[state_param] = snapshot

    try:
        code = compile(ast.Expression(body=atom.node), "<guard>", "eval")
    except (SyntaxError, ValueError, TypeError) as exc:   # pragma: no cover
        return None, "could not compile: {}".format(exc)

    try:
        value = eval(code, env)      # noqa: S307 - see module docstring
    except NameError as exc:
        return None, "unresolved name ({})".format(exc)
    except Exception as exc:
        return None, "raised {}: {}".format(type(exc).__name__, exc)

    truth = bool(value)
    # A guard-and-bail atom is a *bail* condition: it firing means the
    # requirement did not hold.
    held = (not truth) if atom.negated else truth
    return held, None


def explain_dead_end(trace, source, namespace=None):
    """
    Explain the first terminal event in `trace`.

    Args:
        trace: a PlanTrace, from find_plan(..., trace=True, trace_state=True).
        source: path to the domain's .py file, or a directory to search.
        namespace: optional dict of globals for resolving helper functions an
            action's guard calls (e.g. simple_htn's `is_a`). Pass a module's
            __dict__ -- typically `vars(sys.modules[TheDomain.__module__])`.
            Without it, atoms calling such helpers are reported unevaluated
            rather than guessed at.

    Returns a DeadEndReport. Every degraded case is reported rather than
    raised, since a diagnostic tool that blows up on an unusual domain is
    worse than one that says what it could not determine.
    """
    if trace is None:
        return DeadEndReport(None, None, (), [], [], status=None,
                             note="no trace: pass find_plan(..., trace=True, trace_state=True)")

    event = trace.dead_end
    if event is None:
        return DeadEndReport(None, None, (), [], [], status=None,
                             note="no dead end recorded: the search did not abandon any item")

    if event.status in _REFINEMENT_DEAD_ENDS:
        return DeadEndReport(
            event, None, (), [], [], status=event.status,
            note=("refinement dead end ({}): every candidate method for {!r} was tried "
                  "and none led to a plan. Precondition attribution does not apply -- "
                  "no single action's guard is at fault.".format(event.status, event.item)))

    if not isinstance(event.item, (tuple, list)) or not event.item:
        return DeadEndReport(event, None, (), [], [], status=event.status,
                             note="dead-end item is not an action tuple: {!r}".format(event.item))

    action = event.item[0]
    args = tuple(event.item[1:])

    if event.status not in _PRECONDITION_FAILURE:
        return DeadEndReport(
            event, action, args, [], [], status=event.status,
            note=("dead end is {!r}, not a precondition failure. detail: {}"
                  .format(event.status, event.detail)))

    table = load_guards(source)
    guards = table.get(action)
    if guards is None:
        return DeadEndReport(event, action, args, [], [], status=event.status,
                             note="no source found for action {!r} under {}".format(action, source))

    if not guards.atoms:
        return DeadEndReport(
            event, action, args, [], [], status=event.status,
            note=("no precondition guard found in {!r}. Either it has none (some "
                  "actions are unconditional), or it delegates its check to another "
                  "function, or it guards in a shape this analyser does not yet read."
                  .format(action)))

    # Bind the action's declared parameters to the arguments the trace
    # recorded, skipping the leading state parameter.
    bindings = {}
    for name, value in zip(guards.params[1:], args):
        bindings[name] = value

    snapshot = event.state
    if snapshot is None:
        results = [AtomResult(atom, None, "no state snapshot: pass find_plan(..., trace_state=True)")
                   for atom in guards.atoms]
        return DeadEndReport(
            event, action, args, results, list(results), status=event.status,
            note=("candidate preconditions only -- without trace_state=True there is no "
                  "state to test them against"))

    ns = dict(namespace) if namespace else {}
    results = []
    for atom in guards.atoms:
        held, reason = _evaluate(atom, guards.state_param, snapshot, bindings, ns)
        results.append(AtomResult(atom, held, reason))

    unevaluated = [r for r in results if r.held is None]
    note = None
    if not [r for r in results if r.held is False]:
        note = ("no atom evaluated false against the snapshot"
                + (" ({} could not be evaluated)".format(len(unevaluated)) if unevaluated else ""))
    return DeadEndReport(event, action, args, results, unevaluated,
                         status=event.status, note=note)
