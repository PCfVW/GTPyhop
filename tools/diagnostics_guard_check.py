#!/usr/bin/env python3
"""
Check that every guard atom gtpyhop-diagnostics extracts is a real precondition.

    python tools/diagnostics_guard_check.py

Why this exists. explain_dead_end names as blockers the atoms that evaluate
false against the failing state. That is only honest if every atom is
*necessary*: implied by the requirement it was lifted from, so that its
failing really does block the action. 0.1.0 broke this for a guard-and-bail
on a conjunction. `if A and B: return False` requires only `not (A and B)`,
but the extractor split the test on `and` and negated each part, reporting
`not A` and `not B` as two separate requirements. With A true, B false and
some other guard failing, A was named as a blocker although it blocked
nothing. It was found by a consumer, measuring the package on 436 generated
domains, as false atoms on actions that had in fact been applied.

The first case below is the generic invariant that catches this class
without anyone anticipating the particular shape: for generated guard
expressions in every guard form, the conjunction of the extracted atoms must
be *equivalent* to the requirement, checked by truth table. Equivalence is
two properties at once -- each atom is implied by the requirement (it is
sound), and together they imply it (none was lost). The rest pin the
documented idioms, the reported reproduction end to end, and the bundled
actions the fix changed.
"""

import ast
import io
import itertools
import os
import random
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for pkg in ('gtpyhop-core', 'gtpyhop-diagnostics'):
    sys.path.insert(0, os.path.join(REPO, 'packages', pkg, 'src'))

_stdout = sys.stdout
sys.stdout = io.StringIO()
import gtpyhop                                                    # noqa: E402
from gtpyhop.diagnostics import (explain_dead_end,                 # noqa: E402
                                 extract_action_guards, load_guards)
sys.stdout = _stdout

EXAMPLES = os.path.join(REPO, 'packages', 'gtpyhop-examples', 'src', 'gtpyhop', 'examples')

CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


def quiet(fn, *args, **kwargs):
    """Call fn with stdout suppressed; the planner is chatty."""
    out = sys.stdout
    sys.stdout = io.StringIO()
    try:
        return fn(*args, **kwargs)
    finally:
        sys.stdout = out


def atoms_of(src):
    func = ast.parse(src).body[0]
    return [(a.source, a.negated) for a in extract_action_guards(func, src).atoms]


# --- the generic invariant -------------------------------------------------

LEAVES = ['state.p[x]', 'state.q[x]', 'state.r[x]', 'state.s[x]']

# Every shape the extractor recognises, with whether its requirement is the
# test (False) or the negation of the test (True).
FORMS = [
    ('bail on return False', True,
     "def a(state, x):\n    if {T}:\n        return False\n    state.done[x] = 1\n    return state\n"),
    ('bail on bare return', True,
     "def a(state, x):\n    if {T}:\n        return\n    state.done[x] = 1\n    return state\n"),
    ('wrapping guard', False,
     "def a(state, x):\n    if {T}:\n        state.done[x] = 1\n        return state\n"),
    ('else that bails', False,
     "def a(state, x):\n    if {T}:\n        state.done[x] = 1\n    else:\n        return False\n"
     "    return state\n"),
]


def generate(rng, depth):
    if depth == 0 or rng.random() < 0.3:
        return rng.choice(LEAVES)
    roll = rng.random()
    if roll < 0.25:
        return 'not ' + parenthesise(generate(rng, depth - 1))
    op = ' and ' if roll < 0.62 else ' or '
    return op.join(parenthesise(generate(rng, depth - 1)) for _ in range(rng.choice([2, 2, 3])))


def parenthesise(expr):
    return expr if expr in LEAVES else '(' + expr + ')'


class _S(object):
    pass


def assignments():
    for bits in itertools.product([False, True], repeat=len(LEAVES)):
        state = _S()
        state.p, state.q, state.r, state.s = ({'x': b} for b in bits)
        yield {'state': state, 'x': 'x'}


def truth(node, env):
    return bool(eval(compile(ast.Expression(body=node), '<guard>', 'eval'), env))  # noqa: S307


@case('atoms are exactly the requirement, by truth table (the general invariant)')
def _():
    rng = random.Random(20261116)
    envs = list(assignments())
    expressions, checked, atoms_seen = set(), 0, 0
    while len(expressions) < 400:
        expressions.add(generate(rng, rng.choice([1, 2, 3])))
    for test_src in sorted(expressions):
        for form, negated_req, template in FORMS:
            src = template.format(T=test_src)
            func = ast.parse(src).body[0]
            test = func.body[0].test
            atoms = extract_action_guards(func, src).atoms
            atoms_seen += len(atoms)
            for env in envs:
                required = truth(test, env) != negated_req
                held = [truth(a.node, env) != a.negated for a in atoms]
                if required and not all(held):
                    bad = [a for a, h in zip(atoms, held) if not h]
                    return False, ("{}: `{}` holds, yet atom {} is reported false -- it is "
                                   "not a precondition".format(form, test_src, bad[0]))
                if all(held) and not required:
                    return False, ("{}: `{}` fails, yet every atom holds -- a precondition "
                                   "was lost".format(form, test_src))
            checked += 1
    return True, "{} guards, {} atoms, {} assignments each".format(checked, atoms_seen, len(envs))


# --- the documented idioms --------------------------------------------------

@case('a bail on `A and B` is one atom, not two negations')
def _():
    got = atoms_of("def a(s, x):\n    if s.p[x] and s.q[x]:\n        return False\n    return s\n")
    want = [('s.p[x] and s.q[x]', True)]
    return got == want, got


@case('`if not (A and B): return False` still names A and B separately')
def _():
    got = atoms_of("def a(s, x):\n    if not (s.p[x] and s.q[x]):\n        return False\n    return s\n")
    want = [('s.p[x]', False), ('s.q[x]', False)]
    return got == want, got


@case('a wrapping guard still splits on `and` and keeps `or` whole')
def _():
    got = atoms_of("def a(s, x):\n    if s.p[x] and (s.q[x] or s.r[x]):\n        return s\n")
    want = [('s.p[x]', False), ('s.q[x] or s.r[x]', False)]
    return got == want, got


# --- the reported reproduction, end to end -----------------------------------

REPRO = '''
import gtpyhop
domain = gtpyhop.Domain('guard_check_repro')

def a_go(state, x):
    if state.locked_a[x] and state.locked_b[x]:   # bail only when BOTH are locked
        return False
    if not state.fuel[x] > 0:
        return False
    state.at[x] = 'there'
    return state

gtpyhop.declare_actions(a_go)
'''


@case('reported reproduction: only the fuel guard is named')
def _():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'domain.py')
        with open(path, 'w') as handle:
            handle.write(REPRO)
        namespace = {}
        quiet(exec, compile(REPRO, path, 'exec'), namespace)
        state = gtpyhop.State('s')
        state.locked_a, state.locked_b = {'x': True}, {'x': False}
        state.fuel, state.at = {'x': 0}, {'x': 'here'}
        with quiet(gtpyhop.PlannerSession, domain=namespace['domain'], verbose=0) as session:
            result = quiet(session.find_plan, state, [('a_go', 'x')], trace=True, trace_state=True)
        report = explain_dead_end(result.trace, path)
    want = "a_go('x') was blocked by: state.fuel[x] > 0"
    return report.summary() == want, report.summary()


# --- the bundled actions the fix changed --------------------------------------

@case('bundled cross_server a_open_gripper: its `hasattr and ==` bail stays whole')
def _():
    table = load_guards(os.path.join(EXAMPLES, 'mcp-orchestration', 'cross_server'))
    got = [(a.source, a.negated) for a in table['a_open_gripper'].atoms]
    want = ('hasattr(state, \'gripper_state\') and state.gripper_state == "open"', True)
    if want not in got:
        return False, got
    split = [s for s, n in got if n and s in ("hasattr(state, 'gripper_state')",
                                              'state.gripper_state == "open"')]
    return not split, got


def main():
    print("diagnostics guard check\n")
    failed = 0
    for name, fn in CASES:
        try:
            ok, detail = fn()
        except Exception as exc:                                  # noqa: BLE001
            ok, detail = False, "raised {!r}".format(exc)
        print("  {}  {}".format('PASS' if ok else 'FAIL', name))
        if not ok:
            failed += 1
            print("        {}".format(detail))
    print("\n{}/{} passed".format(len(CASES) - failed, len(CASES)))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
