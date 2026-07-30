"""
Problem definitions for the Backtracking Poetry HTN Domain.
-- Generated 2026-02-11

This file defines initial states for poetry generation workflows that test
HTN backtracking. The domain provides two methods for m_write_rhymed_line:
  - m_write_rhymed_line_strict  (tried first, may fail)
  - m_write_rhymed_line_relaxed (fallback, always succeeds)

Planning strategy behavior:
  - Recursive DFS:              backtracks via call stack -> finds plan
  - Iterative greedy:           commits to strict -> fails (no backtracking)
  - Iterative DFS backtracking: backtracks via explicit stack -> finds plan

Scenarios:
  - scenario_1_couplet_stars:    Couplet about stars     ->  8 actions (no BT)
  - scenario_2_limerick_cat:     Limerick about a cat    -> 17 actions (BT required)
  - scenario_3_haiku_ocean:      Haiku about the ocean   ->  8 actions (no BT)

Backtracking analysis:
  Couplet (AA):   label A used 2x -> strict succeeds for both -> no backtracking
  Limerick (AABBA): label A used 3x -> strict fails at line 4 -> backtracking
  Haiku (5-7-5): no rhyme labels -> no backtracking

Plan length formulas (same as structured_poetry):
  Couplet:  2 + (3 x 2) = 8   [init + assemble + (select + generate + verify) x lines]
  Limerick: 2 + (3 x 5) = 17
  Haiku:    2 + (2 x 3) = 8   [no rhyme selection step]
"""

import sys
import os
from typing import Dict, Tuple, List

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    # Graceful degradation: supports direct problems.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def h_create_base_poetry_state(name: str) -> State:
    """Create a base state with common poetry workflow properties."""
    state = State(name)
    state.poem_form = ""
    state.topic = ""
    state.form_spec = {}
    state.rhyme_registry = {}
    state.lines = []
    state.line_targets = []
    state.rhyme_target_selected = {}
    state.line_generated = {}
    state.line_verified = {}
    state.verification_errors = {}
    state.poem_initialized = False
    state.poem_complete = False
    state.final_poem = ""
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: backtracking_poetry

# BEGIN: Scenario: scenario_1_couplet_stars
# Configuration
_form, _topic = "couplet", "stars in the night sky"

# State
initial_state_scenario_1 = h_create_base_poetry_state('scenario_1_couplet_stars')
initial_state_scenario_1.poem_form = _form
initial_state_scenario_1.topic = _topic

# Problem
problems['scenario_1_couplet_stars'] = (
    initial_state_scenario_1,
    [('m_write_poem', _form, _topic)],
    f'Rhyming couplet about "{_topic}" -> 8 actions (no backtracking needed)'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_limerick_cat
# Configuration
_form, _topic = "limerick", "a clever cat"

# State
initial_state_scenario_2 = h_create_base_poetry_state('scenario_2_limerick_cat')
initial_state_scenario_2.poem_form = _form
initial_state_scenario_2.topic = _topic

# Problem
problems['scenario_2_limerick_cat'] = (
    initial_state_scenario_2,
    [('m_write_poem', _form, _topic)],
    f'Limerick about "{_topic}" -> 17 actions (backtracking required at line 4)'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_haiku_ocean
# Configuration
_form, _topic = "haiku", "the ocean at dawn"

# State
initial_state_scenario_3 = h_create_base_poetry_state('scenario_3_haiku_ocean')
initial_state_scenario_3.poem_form = _form
initial_state_scenario_3.topic = _topic

# Problem
problems['scenario_3_haiku_ocean'] = (
    initial_state_scenario_3,
    [('m_write_poem', _form, _topic)],
    f'Haiku about "{_topic}" -> 8 actions (no backtracking needed)'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.poetry.backtracking_poetry import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 — Couplet about stars (8 actions, no backtracking).
    Label A used 2x — within strict limit, so strict succeeds for both lines.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(*probs['scenario_1_couplet_stars'][:2])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 8)

    Scenario 2 — Limerick about a cat (17 actions, backtracking required).
    Label A used 3x — strict fails at line 4 (3rd A), planner backtracks to relaxed.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(*probs['scenario_2_limerick_cat'][:2])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 17)
    >>> [a for a in r2.plan if a[0] == 'a_select_rhyme_target_relaxed']
    [('a_select_rhyme_target_relaxed', 4, 'A')]

    Scenario 3 — Haiku about the ocean (8 actions, no backtracking).
    No rhyme labels — free-form generation only.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(*probs['scenario_3_haiku_ocean'][:2])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 8)

    Greedy planner fails on the limerick (backtracking required).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g2 = s.find_plan(*probs['scenario_2_limerick_cat'][:2])
    >>> sys.stdout = _o
    >>> g2.success
    False

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
