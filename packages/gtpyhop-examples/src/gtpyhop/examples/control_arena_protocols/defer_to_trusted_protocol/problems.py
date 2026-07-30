"""
Defer to Trusted Protocol - Problem Definitions for GTPyhop

This file defines 6 scenarios for the Defer to Trusted micro-protocol,
varying suspicion scores and thresholds to exercise both accept and
defer routing paths.

All plans are 5 actions:
  a_initialize_episode -> a_run_untrusted_policy -> a_run_monitor ->
  (a_accept_output | a_defer_to_trusted) -> a_score_trajectory

Scenarios where suspicion > threshold require backtracking (greedy fails).
Scenarios where suspicion <= threshold succeed with any planner.

-- Generated 2026-03-31
"""

import sys
import os

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

def h_create_base_protocol_state(name: str) -> State:
    """Create a base state with common Defer to Trusted protocol properties."""
    state = State(name)

    # Configuration (set per scenario)
    state.task_id = ""
    state.config_suspicion_score = 0.0
    state.config_suspicion_threshold = 0.7

    # Pipeline state
    state.episode_initialized = False
    state.agent_output = ""
    state.untrusted_has_run = False
    state.suspicion_score = 0.0
    state.monitor_evaluation_complete = False
    state.output_accepted = False
    state.deferred_to_trusted = False
    state.trusted_output = ""
    state.trajectory_scored = False

    # Audit trail
    state.audit_log = []

    return state


# ============================================================================
# PROBLEM DEFINITIONS
# ============================================================================

problems = {}

# BEGIN: Domain: defer_to_trusted_protocol

# BEGIN: Scenario: scenario_1_low_suspicion
# Configuration
_suspicion, _threshold, _task_id = 0.2, 0.7, 'task_001'

# State
initial_state_scenario_1 = h_create_base_protocol_state('scenario_1_low_suspicion')
initial_state_scenario_1.task_id = _task_id
initial_state_scenario_1.config_suspicion_score = _suspicion
initial_state_scenario_1.config_suspicion_threshold = _threshold

# Problem
problems['scenario_1_low_suspicion'] = (
    initial_state_scenario_1,
    [('m_run_defer_to_trusted_protocol', _task_id)],
    f'Suspicion {_suspicion} <= threshold {_threshold} -> accept (5 actions)'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_high_suspicion
# Configuration
_suspicion, _threshold, _task_id = 0.9, 0.7, 'task_002'

# State
initial_state_scenario_2 = h_create_base_protocol_state('scenario_2_high_suspicion')
initial_state_scenario_2.task_id = _task_id
initial_state_scenario_2.config_suspicion_score = _suspicion
initial_state_scenario_2.config_suspicion_threshold = _threshold

# Problem
problems['scenario_2_high_suspicion'] = (
    initial_state_scenario_2,
    [('m_run_defer_to_trusted_protocol', _task_id)],
    f'Suspicion {_suspicion} > threshold {_threshold} -> defer (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_at_threshold
# Configuration
_suspicion, _threshold, _task_id = 0.7, 0.7, 'task_003'

# State
initial_state_scenario_3 = h_create_base_protocol_state('scenario_3_at_threshold')
initial_state_scenario_3.task_id = _task_id
initial_state_scenario_3.config_suspicion_score = _suspicion
initial_state_scenario_3.config_suspicion_threshold = _threshold

# Problem
problems['scenario_3_at_threshold'] = (
    initial_state_scenario_3,
    [('m_run_defer_to_trusted_protocol', _task_id)],
    f'Suspicion {_suspicion} <= threshold {_threshold} -> accept at boundary (5 actions)'
)
# END: Scenario

# BEGIN: Scenario: scenario_4_just_above
# Configuration
_suspicion, _threshold, _task_id = 0.71, 0.7, 'task_004'

# State
initial_state_scenario_4 = h_create_base_protocol_state('scenario_4_just_above')
initial_state_scenario_4.task_id = _task_id
initial_state_scenario_4.config_suspicion_score = _suspicion
initial_state_scenario_4.config_suspicion_threshold = _threshold

# Problem
problems['scenario_4_just_above'] = (
    initial_state_scenario_4,
    [('m_run_defer_to_trusted_protocol', _task_id)],
    f'Suspicion {_suspicion} > threshold {_threshold} -> defer just above (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_5_tight_threshold
# Configuration
_suspicion, _threshold, _task_id = 0.4, 0.3, 'task_005'

# State
initial_state_scenario_5 = h_create_base_protocol_state('scenario_5_tight_threshold')
initial_state_scenario_5.task_id = _task_id
initial_state_scenario_5.config_suspicion_score = _suspicion
initial_state_scenario_5.config_suspicion_threshold = _threshold

# Problem
problems['scenario_5_tight_threshold'] = (
    initial_state_scenario_5,
    [('m_run_defer_to_trusted_protocol', _task_id)],
    f'Suspicion {_suspicion} > threshold {_threshold} -> defer with tight threshold (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_6_loose_threshold
# Configuration
_suspicion, _threshold, _task_id = 0.4, 0.9, 'task_006'

# State
initial_state_scenario_6 = h_create_base_protocol_state('scenario_6_loose_threshold')
initial_state_scenario_6.task_id = _task_id
initial_state_scenario_6.config_suspicion_score = _suspicion
initial_state_scenario_6.config_suspicion_threshold = _threshold

# Problem
problems['scenario_6_loose_threshold'] = (
    initial_state_scenario_6,
    [('m_run_defer_to_trusted_protocol', _task_id)],
    f'Suspicion {_suspicion} <= threshold {_threshold} -> accept with loose threshold (5 actions)'
)
# END: Scenario

# END: Domain

# ============================================================================
# PROBLEM DISCOVERY
# ============================================================================

def get_problems():
    """
    Return all problem definitions for the Defer to Trusted protocol.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.control_arena_protocols.defer_to_trusted_protocol import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    6

    Scenario 1 -- Low suspicion (0.2 <= 0.7), accepted. Both planners succeed.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(*probs['scenario_1_low_suspicion'][:2])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 5)
    >>> ('a_accept_output', 'task_001') in r1.plan
    True

    Scenario 2 -- High suspicion (0.9 > 0.7), deferred. Greedy FAILS.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(*probs['scenario_2_high_suspicion'][:2])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_002') in r2.plan
    True

    Greedy planner fails on scenario 2 (cannot backtrack from accept to defer).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g2 = s.find_plan(*probs['scenario_2_high_suspicion'][:2])
    >>> sys.stdout = _o
    >>> g2.success
    False

    Scenario 3 -- At threshold (0.7 <= 0.7), accepted. Both planners succeed.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(*probs['scenario_3_at_threshold'][:2])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 5)
    >>> ('a_accept_output', 'task_003') in r3.plan
    True

    Scenario 4 -- Just above (0.71 > 0.7), deferred. Greedy FAILS.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r4 = s.find_plan(*probs['scenario_4_just_above'][:2])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_004') in r4.plan
    True

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g4 = s.find_plan(*probs['scenario_4_just_above'][:2])
    >>> sys.stdout = _o
    >>> g4.success
    False

    Scenario 5 -- Tight threshold (0.4 > 0.3), deferred. Greedy FAILS.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r5 = s.find_plan(*probs['scenario_5_tight_threshold'][:2])
    >>> sys.stdout = _o
    >>> r5.success, len(r5.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_005') in r5.plan
    True

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g5 = s.find_plan(*probs['scenario_5_tight_threshold'][:2])
    >>> sys.stdout = _o
    >>> g5.success
    False

    Scenario 6 -- Loose threshold (0.4 <= 0.9), accepted. Both planners succeed.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r6 = s.find_plan(*probs['scenario_6_loose_threshold'][:2])
    >>> sys.stdout = _o
    >>> r6.success, len(r6.plan)
    (True, 5)
    >>> ('a_accept_output', 'task_006') in r6.plan
    True

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
