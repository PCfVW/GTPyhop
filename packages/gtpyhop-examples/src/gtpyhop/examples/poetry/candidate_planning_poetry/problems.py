"""
Problem definitions for the Candidate Planning Poetry HTN Domain.
-- Generated 2026-02-12

This file defines initial states for neuro-symbolic poetry generation workflows
with multi-candidate rhyme selection. The workflow demonstrates coordination
between 2 MCP servers:
  - Server 1 (phonetics-server): Candidate generation, ranking, verification
  - Server 2 (llm-server): Constrained text generation via LLM

Scenarios:
  - scenario_1_couplet_stars:  Couplet about stars     -> 12 actions
  - scenario_2_limerick_cat:   Limerick about a cat    -> 27 actions
  - scenario_3_haiku_ocean:    Haiku about the ocean   ->  8 actions

Plan length formulas:
  Couplet:  2 + (5 x 2) = 12  [init + assemble + (candidates + rank + commit + generate + verify) x lines]
  Limerick: 2 + (5 x 5) = 27
  Haiku:    2 + (2 x 3) = 8   [no candidate selection step]
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
    state.candidates = {}
    state.ranked_candidates = {}
    state.num_candidates = 5
    state.candidates_generated = {}
    state.candidates_ranked = {}
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

# BEGIN: Domain: candidate_planning_poetry

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
    f'Limerick about "{_topic}" -> 27 actions'
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

    Setup: suppress GTPyhop import messages.

    >>> import sys, io; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.poetry.candidate_planning_poetry import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 — Couplet about stars (12 actions).
    5-step pipeline per rhymed line: candidates + rank + commit + generate + verify.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r1 = s.find_plan(*probs['scenario_1_couplet_stars'][:2])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 12)

    Scenario 2 — Limerick about a cat (27 actions).
    5 lines: AABBA rhyme scheme, each with the 5-step pipeline.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r2 = s.find_plan(*probs['scenario_2_limerick_cat'][:2])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 27)

    Scenario 3 — Haiku about the ocean (8 actions).
    2-step pipeline per free line: generate + verify (no candidate selection).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r3 = s.find_plan(*probs['scenario_3_haiku_ocean'][:2])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 8)

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
