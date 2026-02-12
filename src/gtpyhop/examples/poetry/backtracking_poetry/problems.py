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

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
