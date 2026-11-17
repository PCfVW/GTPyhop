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


# --- the same invariant, over control flow ------------------------------------
#
# The case above fixes the shape and varies the guard. This one varies the
# shape: random action bodies of nested ifs, elifs, elses, loops, bails, raises
# and success returns, over the same four leaves plus whether a loop runs.
# Truth comes from *running* the generated action on every assignment, so the
# check does not share any reasoning with the extractor: whenever the action
# succeeds (returns anything but False or None), every atom must hold.

CF_TESTS = ['state.p[x]', 'state.q[x]', 'state.r[x]', 'state.s[x]',
            'not state.p[x]', 'not state.q[x]',
            'state.p[x] and state.q[x]', 'state.r[x] or state.s[x]']


def generate_body(rng, depth, indent, in_loop=False):
    pad = '    ' * indent
    lines = []
    for _ in range(rng.choice([1, 1, 2, 3])):
        roll = rng.random()
        if depth > 0 and roll < 0.45:
            lines.append('{}if {}:'.format(pad, rng.choice(CF_TESTS)))
            lines += generate_body(rng, depth - 1, indent + 1, in_loop)
            tail = rng.random()
            if tail < 0.25:
                lines.append('{}elif {}:'.format(pad, rng.choice(CF_TESTS)))
                lines += generate_body(rng, depth - 1, indent + 1, in_loop)
            if tail < 0.10 or 0.25 <= tail < 0.45:
                lines.append('{}else:'.format(pad))
                lines += generate_body(rng, depth - 1, indent + 1, in_loop)
        elif depth > 0 and roll < 0.55 and not in_loop:
            lines.append('{}for o in state.objs:'.format(pad))
            lines += generate_body(rng, depth - 1, indent + 1, True)
        elif roll < 0.70:
            lines.append('{}state.done[x] += 1'.format(pad))
        elif roll < 0.82:
            lines.append('{}return {}'.format(pad, rng.choice(['False', 'None', ''])).rstrip())
            break
        elif roll < 0.86:
            lines.append('{}raise ValueError(x)'.format(pad))
            break
        else:
            lines.append('{}return state'.format(pad))
            break
    return lines


def cf_states():
    for bits in itertools.product([False, True], repeat=len(LEAVES) + 1):
        state = _S()
        state.p, state.q, state.r, state.s = ({'x': b} for b in bits[:4])
        state.objs = ['x'] if bits[4] else []
        state.done = {'x': 0}
        yield state


def succeeds(fn, state):
    try:
        result = fn(state, 'x')
    except ValueError:
        return False
    return result is not False and result is not None


@case('every atom holds whenever the action succeeds, over generated control flow')
def _():
    rng = random.Random(20261117)
    bodies, atoms_seen = set(), 0
    while len(bodies) < 1500:
        lines = generate_body(rng, rng.choice([1, 2, 3]), 1)
        if rng.random() < 0.7 and not lines[-1].lstrip().startswith(('return', 'raise')):
            lines.append('    return state')
        bodies.add('\n'.join(lines))
    for body in sorted(bodies, key=lambda b: (len(b), b)):          # shortest counterexample first
        src = 'def a(state, x):\n' + body + '\n'
        namespace = {}
        exec(compile(src, '<cf>', 'exec'), namespace)                    # noqa: S102
        atoms = extract_action_guards(ast.parse(src).body[0], src).atoms
        atoms_seen += len(atoms)
        for state in cf_states():
            before = {'state': state, 'x': 'x'}
            held = [truth(a.node, before) != a.negated for a in atoms]
            if succeeds(namespace['a'], state) and not all(held):
                bad = [a for a, h in zip(atoms, held) if not h]
                return False, ("the action succeeds, yet atom {} is reported false -- it is "
                               "not a precondition:\n{}".format(bad[0], src))
    return True, "{} action bodies, {} atoms, 32 states each".format(len(bodies), atoms_seen)


@case('shapes with one path to success keep every atom: elif bails, nested wrapping guards')
def _():
    elif_bails = atoms_of("def a(s, x):\n    if s.p[x]:\n        return False\n"
                          "    elif s.q[x]:\n        return False\n    return s\n")
    nested_wrap = atoms_of("def a(s, x):\n    if s.p[x]:\n        if s.q[x]:\n"
                           "            return s\n")
    got = (elif_bails, nested_wrap)
    want = ([('s.p[x]', True), ('s.q[x]', True)], [('s.p[x]', False), ('s.q[x]', False)])
    return got == want, got


@case('a guard only some successful paths pass is not an atom')
def _():
    shapes = {
        'bail nested in another if': (
            "def a(s, x):\n    if s.p[x]:\n        if s.q[x]:\n            return False\n"
            "    return s\n", []),
        'alternative success branches': (
            "def a(s, x):\n    if s.p[x]:\n        return s\n    if s.q[x]:\n"
            "        return s\n", []),
        'bail after an earlier return of the state': (
            "def a(s, x):\n    if s.p[x]:\n        return s\n    if s.q[x]:\n"
            "        return False\n    return s\n", []),
        'bail in a loop that may run zero times': (
            "def a(s, x):\n    for o in s.objs:\n        if s.q[o]:\n            return False\n"
            "    return s\n", []),
        'guards before the fork still count': (
            "def a(s, x):\n    if not s.r[x]:\n        return False\n    if s.p[x]:\n"
            "        if s.q[x]:\n            return False\n    return s\n", [('s.r[x]', False)]),
    }
    wrong = dict((name, atoms_of(src)) for name, (src, want) in shapes.items()
                 if atoms_of(src) != want)
    return not wrong, wrong or "{} shapes".format(len(shapes))


# Completeness, the converse: when no two tests are related and no success
# return sits inside a loop, every literal that all successful runs share must
# be an atom. Each `if` reads its own variable, so "related" cannot happen, and
# the necessary literals again come from running the action on every state.

def generate_independent(rng, depth, indent, fresh, in_loop=False):
    pad = '    ' * indent
    lines = []
    for _ in range(rng.choice([1, 1, 2, 3])):
        roll = rng.random()
        if depth > 0 and roll < 0.45 and fresh:
            lines.append('{}if {}state.{}[x]:'.format(pad, rng.choice(['', 'not ']), fresh.pop()))
            lines += generate_independent(rng, depth - 1, indent + 1, fresh, in_loop)
            if rng.random() < 0.45:
                lines.append('{}else:'.format(pad))
                lines += generate_independent(rng, depth - 1, indent + 1, fresh, in_loop)
        elif depth > 0 and roll < 0.55 and not in_loop:
            lines.append('{}for o in state.objs:'.format(pad))
            lines += generate_independent(rng, depth - 1, indent + 1, fresh, True)
        elif roll < 0.70:
            lines.append('{}state.done[x] += 1'.format(pad))
        elif roll < 0.85:
            lines.append('{}return {}'.format(pad, rng.choice(['False', 'None', ''])).rstrip())
            break
        elif not in_loop:
            lines.append('{}return state'.format(pad))
            break
    return lines or ['{}pass'.format(pad)]


@case('every literal all successful runs share is an atom, when tests are independent')
def _():
    rng = random.Random(20261118)
    names = ['v{}'.format(i) for i in range(6)]
    bodies, atoms_seen = set(), 0
    while len(bodies) < 1500:
        lines = generate_independent(rng, rng.choice([1, 2, 3]), 1, list(names))
        if rng.random() < 0.6 and not lines[-1].lstrip().startswith('return'):
            lines.append('    return state')
        bodies.add('\n'.join(lines))
    for body in sorted(bodies, key=lambda b: (len(b), b)):
        src = 'def a(state, x):\n' + body + '\n'
        namespace = {}
        exec(compile(src, '<complete>', 'exec'), namespace)              # noqa: S102
        atoms = extract_action_guards(ast.parse(src).body[0], src).atoms
        atoms_seen += len(atoms)
        winners = []
        for bits in itertools.product([False, True], repeat=len(names) + 1):
            state = _S()
            for name, bit in zip(names, bits):
                setattr(state, name, {'x': bit})
            state.objs = ['x'] if bits[-1] else []
            state.done = {'x': 0}
            if succeeds(namespace['a'], state):
                winners.append(dict(zip(names, bits)))
        used = [n for n in names if 'state.{}['.format(n) in body]
        want = set((n, v) for n in used for v in (False, True)
                   if winners and all(w[n] == v for w in winners))
        got = set()
        for a in atoms:
            var, probe = a.state_vars[0], _S()
            setattr(probe, var, {'x': True})
            got.add((var, truth(a.node, {'state': probe, 'x': 'x'}) != a.negated))
        if got != want:
            return False, "atoms {} but every success shares {}:\n{}".format(
                sorted(got), sorted(want), src)
    return True, "{} action bodies, {} atoms, 128 states each".format(len(bodies), atoms_seen)


@case('a requirement no bail spells out is still found: the failure falls through')
def _():
    src = ("def a(s, x):\n    if s.p[x]:\n        s.done[x] = 1\n    else:\n"
           "        return s\n    return False\n")
    got = atoms_of(src)
    return got == [('s.p[x]', True)], got


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


@case('a bail on `A or B` names each side: it requires `not A and not B`')
def _():
    got = atoms_of("def a(s, x):\n    if s.p[x] < 4 or s.p[x] > 95:\n        return False\n    return s\n")
    want = [('s.p[x] < 4', True), ('s.p[x] > 95', True)]
    return got == want, got


@case('a wrapping `not (A or B)` splits the same way; a lone `not X` stays as written')
def _():
    got = atoms_of("def a(s, x):\n    if not (s.p[x] or s.q[x]) and not s.r[x]:\n        return s\n")
    want = [('s.p[x]', True), ('s.q[x]', True), ('not s.r[x]', False)]
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


CF_REPRO = '''
import gtpyhop
domain = gtpyhop.Domain('guard_check_cf_repro')

def a_submit(state, name, processes_per_node):
    if not state.server_ready:
        return False
    launcher = state.job_launcher.get(name)
    if launcher is not None:           # only an MPI job needs mpirun and ranks
        if launcher != 'mpirun':
            return False
        if processes_per_node < 1:
            return False
    state.submitted[name] = True
    return state

gtpyhop.declare_actions(a_submit)
'''


@case('nested-bail reproduction: a non-MPI job is not blamed for its rank count')
def _():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'domain.py')
        with open(path, 'w') as handle:
            handle.write(CF_REPRO)
        namespace = {}
        quiet(exec, compile(CF_REPRO, path, 'exec'), namespace)
        state = gtpyhop.State('s')
        state.server_ready, state.job_launcher, state.submitted = False, {}, {}
        with quiet(gtpyhop.PlannerSession, domain=namespace['domain'], verbose=0) as session:
            result = quiet(session.find_plan, state, [('a_submit', 'job', 0)],
                           trace=True, trace_state=True)
        report = explain_dead_end(result.trace, path)
    want = "a_submit('job', 0) was blocked by: state.server_ready"
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


@case('bundled rikyu_hpc a_submit_job: the MPI checks under `launcher is not None` are not atoms')
def _():
    table = load_guards(os.path.join(EXAMPLES, 'mcp-orchestration', 'rikyu_hpc'))
    got = [s for s, _ in ((a.source, a.negated) for a in table['a_submit_job'].atoms)]
    nested = [s for s in got if s in ("launcher != 'mpirun'", 'processes_per_node < 1',
                                      'arch != state.cluster_arch')]
    return not nested and 'directory in state.remote_dirs' in got, got


@case('bundled bio_opentrons a_open_thermocycler_lid: its early `return state` is no guard')
def _():
    table = load_guards(os.path.join(EXAMPLES, 'mcp-orchestration', 'bio_opentrons'))
    got = [(a.source, a.negated) for a in table['a_open_thermocycler_lid'].atoms]
    want = [('isinstance(state, State)', False),
            ("hasattr(state, 'module_server_ready')", False), ('state.module_server_ready', False)]
    return got == want, got


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
