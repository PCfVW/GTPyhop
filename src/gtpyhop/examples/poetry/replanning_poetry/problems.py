"""
Problem definitions for the Replanning Poetry HTN Domain.
-- Generated 2026-02-12

This file defines initial states for neuro-symbolic poetry generation workflows
with post-generation evaluation and steering/revision. The workflow demonstrates
coordination between 2 MCP servers:
  - Server 1 (phonetics-server): Rhyme target selection, steering, verification
  - Server 2 (llm-server): Text generation, line evaluation

Scenarios:
  - scenario_1_couplet_stars:  Couplet about stars     -> 12 actions
  - scenario_2_limerick_cat:   Limerick about a cat    -> 28 actions
  - scenario_3_haiku_ocean:    Haiku about the ocean   ->  8 actions

Plan length formulas:
  Lines without revision: 4 actions (select + generate + verify + evaluate)
  Lines with revision:    6 actions (select + generate + verify + steer + generate + verify)
  Free lines (haiku):     2 actions (generate + verify)

  Couplet:  2 + (1x4 + 1x6) = 12  [1 accepted, 1 revised]
  Limerick: 2 + (2x4 + 3x6) = 28  [2 accepted, 3 revised]
  Haiku:    2 + (3x2)        = 8   [no revision needed]
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
    """Create a base state with common replanning poetry workflow properties."""
    state = State(name)
    state.poem_form = ""
    state.topic = ""
    state.form_spec = {}
    state.rhyme_registry = {}
    state.lines = []
    state.line_targets = []
    state.lines_requiring_revision = set()
    state.rhyme_target_selected = {}
    state.line_generated = {}
    state.line_verified = {}
    state.verification_errors = {}
    state.line_evaluated = {}
    state.line_steered = {}
    state.poem_initialized = False
    state.poem_complete = False
    state.final_poem = ""
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: replanning_poetry

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
    f'Rhyming couplet about "{_topic}" -> 12 actions'
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
    f'Limerick about "{_topic}" -> 28 actions'
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
    f'Haiku about "{_topic}" -> 8 actions'
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
