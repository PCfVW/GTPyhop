"""
Problem definitions for the Structured Poetry HTN Domain.
-- Generated 2026-02-11

This file defines initial states for neuro-symbolic poetry generation workflows.
The workflow demonstrates coordination between 2 MCP servers:
  - Server 1 (phonetics-server): Rhyme candidate selection, syllable counting, verification
  - Server 2 (llm-server): Constrained text generation via LLM

Scenarios:
  - scenario_1_couplet_autumn:  Rhyming couplet about autumn       ->  8 actions
  - scenario_2_limerick_cat:    Limerick about a cat               -> 17 actions
  - scenario_3_haiku_ocean:     Haiku about the ocean              ->  8 actions
  - scenario_4_sonnet_time:     Shakespearean sonnet about time    -> 44 actions
  - scenario_5_couplet_stars:   Rhyming couplet about stars        ->  8 actions
  - scenario_6_limerick_code:   Limerick about coding              -> 17 actions

Plan length formulas:
  Couplet:  2 + (3 x 2) = 8   [init + assemble + (select + generate + verify) x lines]
  Limerick: 2 + (3 x 5) = 17
  Haiku:    2 + (2 x 3) = 8   [no rhyme selection step]
  Sonnet:   2 + (3 x 14) = 44
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

# BEGIN: Domain: structured_poetry

# BEGIN: Scenario: scenario_1_couplet_autumn
# Configuration
_form, _topic = "couplet", "autumn leaves falling"

# State
initial_state_scenario_1 = h_create_base_poetry_state('scenario_1_couplet_autumn')
initial_state_scenario_1.poem_form = _form
initial_state_scenario_1.topic = _topic

# Problem
problems['scenario_1_couplet_autumn'] = (
    initial_state_scenario_1,
    [('m_write_poem', _form, _topic)],
    f'Rhyming couplet about "{_topic}" -> 8 actions'
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
    f'Limerick about "{_topic}" -> 17 actions'
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

# BEGIN: Scenario: scenario_4_sonnet_time
# Configuration
_form, _topic = "sonnet", "the passage of time"

# State
initial_state_scenario_4 = h_create_base_poetry_state('scenario_4_sonnet_time')
initial_state_scenario_4.poem_form = _form
initial_state_scenario_4.topic = _topic

# Problem
problems['scenario_4_sonnet_time'] = (
    initial_state_scenario_4,
    [('m_write_poem', _form, _topic)],
    f'Shakespearean sonnet about "{_topic}" -> 44 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_5_couplet_stars
# Configuration
_form, _topic = "couplet", "stars in the night sky"

# State
initial_state_scenario_5 = h_create_base_poetry_state('scenario_5_couplet_stars')
initial_state_scenario_5.poem_form = _form
initial_state_scenario_5.topic = _topic

# Problem
problems['scenario_5_couplet_stars'] = (
    initial_state_scenario_5,
    [('m_write_poem', _form, _topic)],
    f'Rhyming couplet about "{_topic}" -> 8 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_6_limerick_code
# Configuration
_form, _topic = "limerick", "a programmer debugging code"

# State
initial_state_scenario_6 = h_create_base_poetry_state('scenario_6_limerick_code')
initial_state_scenario_6.poem_form = _form
initial_state_scenario_6.topic = _topic

# Problem
problems['scenario_6_limerick_code'] = (
    initial_state_scenario_6,
    [('m_write_poem', _form, _topic)],
    f'Limerick about "{_topic}" -> 17 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.poetry.structured_poetry import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    6

    Scenario 1 — Couplet about autumn (8 actions).
    3-step pipeline per rhymed line: select + generate + verify.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r1 = s.find_plan(*probs['scenario_1_couplet_autumn'][:2])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 8)

    Scenario 2 — Limerick about a cat (17 actions).
    5 lines: AABBA rhyme scheme, 8-8-5-5-8 syllables.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r2 = s.find_plan(*probs['scenario_2_limerick_cat'][:2])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 17)

    Scenario 3 — Haiku about the ocean (8 actions).
    2-step pipeline per free line: generate + verify (no rhyme selection).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r3 = s.find_plan(*probs['scenario_3_haiku_ocean'][:2])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 8)

    Scenario 4 — Shakespearean sonnet about time (44 actions).
    14 lines: ABAB CDCD EFEF GG, iambic pentameter (10 syllables).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r4 = s.find_plan(*probs['scenario_4_sonnet_time'][:2])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 44)

    Scenario 5 — Couplet about stars (8 actions).
    Same form as scenario 1, different topic.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r5 = s.find_plan(*probs['scenario_5_couplet_stars'][:2])
    >>> sys.stdout = _o
    >>> r5.success, len(r5.plan)
    (True, 8)

    Scenario 6 — Limerick about coding (17 actions).
    Same form as scenario 2, different topic.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     r6 = s.find_plan(*probs['scenario_6_limerick_code'][:2])
    >>> sys.stdout = _o
    >>> r6.success, len(r6.plan)
    (True, 17)

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
