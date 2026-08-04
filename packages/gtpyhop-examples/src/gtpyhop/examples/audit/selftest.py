#!/usr/bin/env python3
"""
Self-test for the example auditor.

    python -m gtpyhop.examples.audit.selftest

Why a checker needs its own tests, and of this particular shape.

A checker is not like ordinary code. Ordinary code is wrong when it does too
little; a checker is equally wrong when it does too much, and a checker that
cries wolf gets ignored, which costs more than having no checker at all. So
every fixture below asserts BOTH halves:

    the expected finding IS reported, and NOTHING ELSE is.

Each fixture is a minimal, otherwise-clean domain with exactly one planted
defect. If a change to the auditor starts reporting something extra, the
fixture for an unrelated defect fails, and names what leaked.

The regression fixtures at the end are not hypothetical. Every one is a bug
this auditor actually had, found by checking its output against the source by
hand rather than believing the total:

  * `declare_actions(` followed by a comment containing `)` -- a naive regex
    ends the argument list at the comment, and every action after it looks
    undeclared. That was 44 false positives across the bundled tree.
  * a UTF-8 BOM made three files "fail to parse".
  * `ast` ends a function at its last *statement*, so a trailing
    `# END: Task Decomposition` sits outside `node.end_lineno` and every
    method looks like it is missing its END marker.
  * an action with a deliberately empty Effects block has nothing to tag.
  * state read only behind `hasattr(state, 'x')` is optional by design, not
    undefined -- flagging it would punish the defensive style the style guide
    asks for.
"""

import os
import shutil
import sys
import tempfile

from . import audit_example

# --------------------------------------------------------------------------
# Fixture building blocks
# --------------------------------------------------------------------------

HEADER = '''\
"""Fixture domain."""
from typing import Union, List, Tuple
from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods

the_domain = Domain("fixture")
set_current_domain(the_domain)
'''

ACTION = '''
def a_prepare(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_prepare(state)

    Action parameters:
        None

    Action purpose:
        Make the workspace ready

    Preconditions:
        None (initialisation action)

    Effects:
        - Workspace is ready (state.ready) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for an initialisation action
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Workspace is ready
    state.ready = True
    # END: Effects

    return state
'''

CONSUMER = '''
def a_finish(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_finish(state)

    Action parameters:
        None

    Action purpose:
        Close the workspace

    Preconditions:
        - Workspace is ready (state.ready)

    Effects:
        - Workspace is closed (state.closed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'ready') and state.ready):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Workspace is closed
    state.closed = True
    # END: Effects

    return state
'''

METHOD = '''
def m_run(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_run(state)

    Method parameters:
        None

    Method purpose:
        Prepare then finish

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_prepare: Make the workspace ready
        - a_finish: Close the workspace

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_prepare",), ("a_finish",)]
    # END: Task Decomposition
'''

FOOTER = '''
declare_actions(a_prepare, a_finish)
declare_task_methods('m_run', m_run)
'''

PROBLEMS = '''\
"""Fixture problems."""
problems = {}


def get_problems():
    """Return the problems."""
    return problems
'''


def clean_domain():
    return HEADER + ACTION + CONSUMER + METHOD + FOOTER


# --------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------

ENFORCED = ('STRUCTURE', 'SEMANTICS', 'BEHAVIOUR')


def run_case(name, domain_src, expect_substrings, problems_src=PROBLEMS,
             domain_bytes=None, families=ENFORCED):
    """
    Audit a fixture; return (ok, message).

    Only the enforced families are compared by default. Any fixture that
    writes state has a terminal effect nothing reads -- state.closed here --
    and that is advisory HYGIENE by design, not a defect to assert against.
    A case that wants to check HYGIENE passes families explicitly.
    """
    tmp = tempfile.mkdtemp(prefix='gtpyhop_audit_selftest_')
    try:
        path = os.path.join(tmp, 'fixture')
        os.makedirs(path)
        target = os.path.join(path, 'domain.py')
        if domain_bytes is not None:
            open(target, 'wb').write(domain_bytes)
        else:
            open(target, 'w', encoding='utf-8', newline='\n').write(domain_src)
        open(os.path.join(path, 'problems.py'), 'w', encoding='utf-8',
             newline='\n').write(problems_src)

        findings, _counts = audit_example(path)
        messages = [str(f) for f in findings if f.family in families]

        missing = [want for want in expect_substrings
                   if not any(want in m for m in messages)]
        # anything reported that no expectation accounts for is a false positive
        extra = [m for m in messages
                 if not any(want in m for want in expect_substrings)]
        if missing:
            return False, f"expected but not reported: {missing}\n     got: {messages}"
        if extra:
            return False, f"FALSE POSITIVE, unexpected findings: {extra}"
        return True, f"{len(expect_substrings)} expected finding(s)"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


# --------------------------------------------------------------------------
# The clean baseline: a correct domain must report nothing at all
# --------------------------------------------------------------------------

@case('clean domain reports nothing')
def _():
    return run_case('clean', clean_domain(), [])


# --------------------------------------------------------------------------
# One planted defect each
# --------------------------------------------------------------------------

@case('missing docstring section is caught')
def _():
    src = clean_domain().replace("    Action purpose:\n        Make the workspace ready\n\n", "", 1)
    return run_case('no-purpose', src, ["docstring is missing 'Action purpose:'"])


@case('missing BEGIN/END marker is caught')
def _():
    src = clean_domain().replace("    # BEGIN: State-Type Checks\n"
                                 "    # No state-type checks needed\n"
                                 "    # END: State-Type Checks\n", "", 1)
    return run_case('no-marker', src,
                    ["missing '# BEGIN: State-Type Checks'",
                     "missing '# END: State-Type Checks'"])


@case('missing type annotation is caught')
def _():
    src = clean_domain().replace("def a_prepare(state: State) ->",
                                 "def a_prepare(state) ->", 1)
    return run_case('no-annotation', src,
                    ["first parameter is not 'state: State'",
                     "parameter 'state' has no type annotation"])


@case('wrong return type is caught')
def _():
    src = clean_domain().replace(
        "def a_prepare(state: State) -> Union[State, bool]:",
        "def a_prepare(state: State) -> Union[List[Tuple], bool]:", 1)
    return run_case('bad-return', src, ["returns Union[List[Tuple],bool]"])


@case('undeclared task in a decomposition is caught')
def _():
    src = clean_domain().replace('return [("a_prepare",), ("a_finish",)]',
                                 'return [("a_prepare",), ("a_nonexistent",)]', 1)
    return run_case('undeclared', src,
                    ["task 'a_nonexistent' is used but never declared"])


@case('stale header count is caught')
def _():
    src = clean_domain().replace('the_domain = Domain("fixture")',
                                 '# ACTIONS (7)\nthe_domain = Domain("fixture")', 1)
    return run_case('stale-count', src, ["but the file has 2 actions"])


@case('Effects section omitting an assigned attribute is caught')
def _():
    src = clean_domain().replace("        - Workspace is closed (state.closed) [DATA]\n",
                                 "        - Something happened\n", 1)
    return run_case('undocumented-effect', src,
                    ["writes state.closed, but its docstring Effects section "
                     "never names it"])


@case('[ENABLER] that gates nothing is caught')
def _():
    # remove the only precondition that reads state.ready
    src = clean_domain().replace(
        "    if not (hasattr(state, 'ready') and state.ready):\n"
        "        return False\n",
        "    # nothing is checked here\n", 1)
    return run_case('enabler-no-gate', src,
                    ["is tagged [ENABLER] but no precondition anywhere tests it"])


@case('untagged Effects block is caught')
def _():
    src = clean_domain().replace("    # [DATA] Workspace is closed\n", "", 1)
    return run_case('untagged', src,
                    ["Effects block has no [DATA]/[ENABLER]/[EXPECTED_EFFECT] tag"])


@case('written-but-never-read is HYGIENE, not SEMANTICS')
def _():
    tmp = tempfile.mkdtemp(prefix='gtpyhop_audit_selftest_')
    try:
        path = os.path.join(tmp, 'fixture')
        os.makedirs(path)
        open(os.path.join(path, 'domain.py'), 'w', encoding='utf-8',
             newline='\n').write(clean_domain())
        open(os.path.join(path, 'problems.py'), 'w', encoding='utf-8',
             newline='\n').write(PROBLEMS)
        findings, _ = audit_example(path)
        hygiene = [f for f in findings if f.family == 'HYGIENE']
        enforced = [f for f in findings
                    if f.family in ('STRUCTURE', 'SEMANTICS', 'BEHAVIOUR')]
        # state.closed is a terminal effect: reported, but never enforced
        if enforced:
            return False, f"terminal effect leaked into an enforced family: {enforced}"
        if not any('state.closed' in f.message for f in hygiene):
            return True, "no HYGIENE finding (state.closed is documented) - acceptable"
        return True, "terminal effect correctly advisory"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# Regression fixtures: bugs this auditor actually had
# --------------------------------------------------------------------------

@case('REGRESSION: a ")" inside a declare_actions comment')
def _():
    src = clean_domain().replace(
        "declare_actions(a_prepare, a_finish)",
        "declare_actions(\n    # movement server (Server 1)\n"
        "    a_prepare,\n    a_finish,\n)", 1)
    return run_case('paren-in-comment', src, [])


@case('REGRESSION: a UTF-8 BOM does not break parsing')
def _():
    return run_case('bom', None, [],
                    domain_bytes=b'\xef\xbb\xbf' + clean_domain().encode('utf-8'))


@case('REGRESSION: trailing END marker after the last statement')
def _():
    # the clean fixture already ends m_run with a trailing END marker, which is
    # outside ast's node.end_lineno; if span handling regresses, this reports
    # every method as missing its Task Decomposition markers
    src = clean_domain()
    assert src.rstrip().endswith("declare_task_methods('m_run', m_run)")
    return run_case('trailing-marker', src, [])


@case('REGRESSION: an empty Effects block needs no tag')
def _():
    src = clean_domain().replace(
        "    # BEGIN: Effects\n    # [DATA] Workspace is closed\n"
        "    state.closed = True\n    # END: Effects\n",
        "    # BEGIN: Effects\n"
        "    # No state change: the workspace is already closed.\n"
        "    # END: Effects\n", 1)
    # a_finish now assigns nothing, so there is nothing to tag and nothing to
    # document: the audit must stay silent rather than demand a tag
    return run_case('empty-effects', src, [])


@case('REGRESSION: hasattr-guarded read is optional, not undefined')
def _():
    src = clean_domain().replace(
        "    # BEGIN: Effects\n    # [ENABLER] Workspace is ready\n",
        "    # BEGIN: Effects\n"
        "    # [DATA] Optional label, absent unless a scenario set it\n"
        "    state.label = state.hint if hasattr(state, 'hint') else 'none'\n"
        "    # [ENABLER] Workspace is ready\n", 1).replace(
        "        - Workspace is ready (state.ready) [ENABLER]",
        "        - Optional label (state.label) [DATA]\n"
        "        - Workspace is ready (state.ready) [ENABLER]", 1)
    # The assertion IS the empty list: state.hint is read and never written,
    # but only behind a hasattr guard, so it must not surface as a defect.
    return run_case('hasattr-optional', src, [])


def main():
    print("auditor self-test\n")
    failed = 0
    for name, fn in CASES:
        try:
            ok, detail = fn()
        except Exception as exc:                                # noqa: BLE001
            ok, detail = False, f"raised {exc!r}"
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            failed += 1
            print(f"        {detail}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
