"""
Defer to Resample Protocol - Problem Definitions for GTPyhop

This file defines 6 scenarios for the Defer to Resample micro-protocol,
varying per-sample suspicion scores and max_samples to exercise
accept-on-Nth-sample and defer-after-exhaustion paths.

Plan length formula (S = number of samples tried):
  Accept on 0-indexed sample N: 2*(N+1) + 3 actions (S = N+1)
  Defer after max_samples: 2*max_samples + 3 actions (S = max_samples)

All scenarios except scenario_1 require backtracking (greedy fails).

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

def h_create_base_resample_state(name: str) -> State:
    """Create a base state with common Defer to Resample protocol properties."""
    state = State(name)

    # Configuration (set per scenario)
    state.task_id = ""
    state.config_suspicion_scores = [0.0]
    state.config_suspicion_threshold = 0.7
    state.config_max_samples = 1

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

# BEGIN: Domain: defer_to_resample_protocol

# BEGIN: Scenario: scenario_1_first_accepted
# Configuration
_scores, _max, _threshold, _task_id = [0.2], 3, 0.7, 'task_001'

# State
initial_state_scenario_1 = h_create_base_resample_state('scenario_1_first_accepted')
initial_state_scenario_1.task_id = _task_id
initial_state_scenario_1.config_suspicion_scores = _scores
initial_state_scenario_1.config_max_samples = _max
initial_state_scenario_1.config_suspicion_threshold = _threshold

# Problem
problems['scenario_1_first_accepted'] = (
    initial_state_scenario_1,
    [('m_run_resample_protocol', _task_id)],
    f'Scores {_scores}, max {_max}, threshold {_threshold} -> accept on sample 0 (5 actions)'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_second_accepted
# Configuration
_scores, _max, _threshold, _task_id = [0.9, 0.3], 3, 0.7, 'task_002'

# State
initial_state_scenario_2 = h_create_base_resample_state('scenario_2_second_accepted')
initial_state_scenario_2.task_id = _task_id
initial_state_scenario_2.config_suspicion_scores = _scores
initial_state_scenario_2.config_max_samples = _max
initial_state_scenario_2.config_suspicion_threshold = _threshold

# Problem
problems['scenario_2_second_accepted'] = (
    initial_state_scenario_2,
    [('m_run_resample_protocol', _task_id)],
    f'Scores {_scores}, max {_max}, threshold {_threshold} -> accept on sample 1 (7 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_third_accepted
# Configuration
_scores, _max, _threshold, _task_id = [0.9, 0.8, 0.4], 3, 0.7, 'task_003'

# State
initial_state_scenario_3 = h_create_base_resample_state('scenario_3_third_accepted')
initial_state_scenario_3.task_id = _task_id
initial_state_scenario_3.config_suspicion_scores = _scores
initial_state_scenario_3.config_max_samples = _max
initial_state_scenario_3.config_suspicion_threshold = _threshold

# Problem
problems['scenario_3_third_accepted'] = (
    initial_state_scenario_3,
    [('m_run_resample_protocol', _task_id)],
    f'Scores {_scores}, max {_max}, threshold {_threshold} -> accept on sample 2 (9 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_4_all_high_defer
# Configuration
_scores, _max, _threshold, _task_id = [0.9, 0.8, 0.85], 3, 0.7, 'task_004'

# State
initial_state_scenario_4 = h_create_base_resample_state('scenario_4_all_high_defer')
initial_state_scenario_4.task_id = _task_id
initial_state_scenario_4.config_suspicion_scores = _scores
initial_state_scenario_4.config_max_samples = _max
initial_state_scenario_4.config_suspicion_threshold = _threshold

# Problem
problems['scenario_4_all_high_defer'] = (
    initial_state_scenario_4,
    [('m_run_resample_protocol', _task_id)],
    f'Scores {_scores}, max {_max}, threshold {_threshold} -> defer after exhaustion (9 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_5_single_sample
# Configuration
_scores, _max, _threshold, _task_id = [0.9], 1, 0.7, 'task_005'

# State
initial_state_scenario_5 = h_create_base_resample_state('scenario_5_single_sample')
initial_state_scenario_5.task_id = _task_id
initial_state_scenario_5.config_suspicion_scores = _scores
initial_state_scenario_5.config_max_samples = _max
initial_state_scenario_5.config_suspicion_threshold = _threshold

# Problem
problems['scenario_5_single_sample'] = (
    initial_state_scenario_5,
    [('m_run_resample_protocol', _task_id)],
    f'Scores {_scores}, max {_max}, threshold {_threshold} -> defer immediately (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_6_five_samples
# Configuration
_scores, _max, _threshold, _task_id = [0.9, 0.8, 0.85, 0.75, 0.3], 5, 0.7, 'task_006'

# State
initial_state_scenario_6 = h_create_base_resample_state('scenario_6_five_samples')
initial_state_scenario_6.task_id = _task_id
initial_state_scenario_6.config_suspicion_scores = _scores
initial_state_scenario_6.config_max_samples = _max
initial_state_scenario_6.config_suspicion_threshold = _threshold

# Problem
problems['scenario_6_five_samples'] = (
    initial_state_scenario_6,
    [('m_run_resample_protocol', _task_id)],
    f'Scores {_scores}, max {_max}, threshold {_threshold} -> accept on sample 4 (13 actions, backtracking)'
)
# END: Scenario

# END: Domain

# ============================================================================
# PROBLEM DISCOVERY
# ============================================================================

def get_problems():
    """
    Return all problem definitions for the Defer to Resample protocol.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.control_arena_protocols.defer_to_resample_protocol import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    6

    Scenario 1 -- First sample accepted (0.2 <= 0.7). Both planners succeed.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(*probs['scenario_1_first_accepted'][:2])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 5)
    >>> ('a_accept_output', 'task_001') in r1.plan
    True

    Scenario 2 -- Second sample accepted (scores=[0.9, 0.3]). Greedy FAILS.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(*probs['scenario_2_second_accepted'][:2])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 7)
    >>> ('a_accept_output', 'task_002') in r2.plan
    True

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g2 = s.find_plan(*probs['scenario_2_second_accepted'][:2])
    >>> sys.stdout = _o
    >>> g2.success
    False

    Scenario 3 -- Third sample accepted (scores=[0.9, 0.8, 0.4]).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(*probs['scenario_3_third_accepted'][:2])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 9)
    >>> ('a_accept_output', 'task_003') in r3.plan
    True

    Scenario 4 -- All high, defer after exhaustion (scores=[0.9, 0.8, 0.85]).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r4 = s.find_plan(*probs['scenario_4_all_high_defer'][:2])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 9)
    >>> ('a_defer_to_trusted', 'task_004') in r4.plan
    True

    Scenario 5 -- Single sample, high suspicion -> defer (5 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r5 = s.find_plan(*probs['scenario_5_single_sample'][:2])
    >>> sys.stdout = _o
    >>> r5.success, len(r5.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_005') in r5.plan
    True

    Scenario 6 -- Five samples, accepted on fifth (13 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r6 = s.find_plan(*probs['scenario_6_five_samples'][:2])
    >>> sys.stdout = _o
    >>> r6.success, len(r6.plan)
    (True, 13)
    >>> ('a_accept_output', 'task_006') in r6.plan
    True

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
