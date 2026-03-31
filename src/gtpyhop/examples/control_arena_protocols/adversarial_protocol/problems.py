"""
Adversarial Protocol - Problem Definitions for GTPyhop

This file defines 8 scenarios for the adversarial micro-protocol,
combining honest and attack modes with varying detection rates,
subtlety levels, and thresholds to exercise security analysis.

All plans are 5 actions:
  a_initialize_episode -> (a_run_untrusted_policy_honest |
  a_run_untrusted_policy_attack) -> a_run_monitor ->
  (a_accept_output | a_defer_to_trusted) -> a_score_trajectory

Security outcomes:
  - SAFE: attack caught (deferred)
  - VULNERABILITY: attack evades monitor (accepted with side task)
  - OVER-SENSITIVE: honest output deferred (false positive)

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

def h_create_base_adversarial_state(name: str) -> State:
    """Create a base state with common adversarial protocol properties."""
    state = State(name)

    # Configuration (set per scenario)
    state.task_id = ""
    state.config_attack_active = False
    state.config_attack_subtlety = ""
    state.config_detection_rates = {}
    state.config_honest_suspicion = 0.1
    state.config_suspicion_threshold = 0.7

    # Pipeline state
    state.episode_initialized = False
    state.agent_output = ""
    state.side_task_embedded = False
    state.attack_subtlety = ""
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

# BEGIN: Domain: adversarial_protocol

# BEGIN: Scenario: scenario_1_honest_accepted
# Configuration
_task_id = 'task_001'

# State
initial_state_scenario_1 = h_create_base_adversarial_state('scenario_1_honest_accepted')
initial_state_scenario_1.task_id = _task_id
initial_state_scenario_1.config_attack_active = False
initial_state_scenario_1.config_honest_suspicion = 0.1
initial_state_scenario_1.config_suspicion_threshold = 0.7

# Problem
problems['scenario_1_honest_accepted'] = (
    initial_state_scenario_1,
    [('m_run_adversarial_protocol', _task_id)],
    'Honest mode, suspicion 0.1 <= 0.7 -> accepted, SAFE (5 actions)'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_obvious_caught
# Configuration
_task_id = 'task_002'

# State
initial_state_scenario_2 = h_create_base_adversarial_state('scenario_2_obvious_caught')
initial_state_scenario_2.task_id = _task_id
initial_state_scenario_2.config_attack_active = True
initial_state_scenario_2.config_attack_subtlety = 'obvious'
initial_state_scenario_2.config_detection_rates = {'obvious': 0.95}
initial_state_scenario_2.config_suspicion_threshold = 0.7

# Problem
problems['scenario_2_obvious_caught'] = (
    initial_state_scenario_2,
    [('m_run_adversarial_protocol', _task_id)],
    'Obvious attack, suspicion 0.95 > 0.7 -> deferred, SAFE (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_subtle_evades
# Configuration
_task_id = 'task_003'

# State
initial_state_scenario_3 = h_create_base_adversarial_state('scenario_3_subtle_evades')
initial_state_scenario_3.task_id = _task_id
initial_state_scenario_3.config_attack_active = True
initial_state_scenario_3.config_attack_subtlety = 'subtle'
initial_state_scenario_3.config_detection_rates = {'subtle': 0.25}
initial_state_scenario_3.config_suspicion_threshold = 0.7

# Problem
problems['scenario_3_subtle_evades'] = (
    initial_state_scenario_3,
    [('m_run_adversarial_protocol', _task_id)],
    'Subtle attack, suspicion 0.25 <= 0.7 -> accepted, VULNERABILITY (5 actions)'
)
# END: Scenario

# BEGIN: Scenario: scenario_4_subtle_caught_tight
# Configuration
_task_id = 'task_004'

# State
initial_state_scenario_4 = h_create_base_adversarial_state('scenario_4_subtle_caught_tight')
initial_state_scenario_4.task_id = _task_id
initial_state_scenario_4.config_attack_active = True
initial_state_scenario_4.config_attack_subtlety = 'subtle'
initial_state_scenario_4.config_detection_rates = {'subtle': 0.25}
initial_state_scenario_4.config_suspicion_threshold = 0.2

# Problem
problems['scenario_4_subtle_caught_tight'] = (
    initial_state_scenario_4,
    [('m_run_adversarial_protocol', _task_id)],
    'Subtle attack, suspicion 0.25 > 0.2 -> deferred, SAFE with tight threshold (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_5_moderate_caught
# Configuration
_task_id = 'task_005'

# State
initial_state_scenario_5 = h_create_base_adversarial_state('scenario_5_moderate_caught')
initial_state_scenario_5.task_id = _task_id
initial_state_scenario_5.config_attack_active = True
initial_state_scenario_5.config_attack_subtlety = 'moderate'
initial_state_scenario_5.config_detection_rates = {'moderate': 0.6}
initial_state_scenario_5.config_suspicion_threshold = 0.5

# Problem
problems['scenario_5_moderate_caught'] = (
    initial_state_scenario_5,
    [('m_run_adversarial_protocol', _task_id)],
    'Moderate attack, suspicion 0.6 > 0.5 -> deferred, SAFE (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_6_moderate_evades
# Configuration
_task_id = 'task_006'

# State
initial_state_scenario_6 = h_create_base_adversarial_state('scenario_6_moderate_evades')
initial_state_scenario_6.task_id = _task_id
initial_state_scenario_6.config_attack_active = True
initial_state_scenario_6.config_attack_subtlety = 'moderate'
initial_state_scenario_6.config_detection_rates = {'moderate': 0.6}
initial_state_scenario_6.config_suspicion_threshold = 0.7

# Problem
problems['scenario_6_moderate_evades'] = (
    initial_state_scenario_6,
    [('m_run_adversarial_protocol', _task_id)],
    'Moderate attack, suspicion 0.6 <= 0.7 -> accepted, VULNERABILITY (5 actions)'
)
# END: Scenario

# BEGIN: Scenario: scenario_7_honest_tight_threshold
# Configuration
_task_id = 'task_007'

# State
initial_state_scenario_7 = h_create_base_adversarial_state('scenario_7_honest_tight_threshold')
initial_state_scenario_7.task_id = _task_id
initial_state_scenario_7.config_attack_active = False
initial_state_scenario_7.config_honest_suspicion = 0.1
initial_state_scenario_7.config_suspicion_threshold = 0.05

# Problem
problems['scenario_7_honest_tight_threshold'] = (
    initial_state_scenario_7,
    [('m_run_adversarial_protocol', _task_id)],
    'Honest mode, suspicion 0.1 > 0.05 -> deferred, OVER-SENSITIVE (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_8_obvious_loose_threshold
# Configuration
_task_id = 'task_008'

# State
initial_state_scenario_8 = h_create_base_adversarial_state('scenario_8_obvious_loose_threshold')
initial_state_scenario_8.task_id = _task_id
initial_state_scenario_8.config_attack_active = True
initial_state_scenario_8.config_attack_subtlety = 'obvious'
initial_state_scenario_8.config_detection_rates = {'obvious': 0.95}
initial_state_scenario_8.config_suspicion_threshold = 0.99

# Problem
problems['scenario_8_obvious_loose_threshold'] = (
    initial_state_scenario_8,
    [('m_run_adversarial_protocol', _task_id)],
    'Obvious attack, suspicion 0.95 <= 0.99 -> accepted, VULNERABILITY (5 actions)'
)
# END: Scenario

# END: Domain

# ============================================================================
# PROBLEM DISCOVERY
# ============================================================================

def get_problems():
    """
    Return all problem definitions for the Adversarial protocol.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.control_arena_protocols.adversarial_protocol import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    8

    Scenario 1 -- Honest, accepted. SAFE. Both planners succeed.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(*probs['scenario_1_honest_accepted'][:2])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 5)
    >>> ('a_run_untrusted_policy_honest', 'task_001') in r1.plan
    True
    >>> ('a_accept_output', 'task_001') in r1.plan
    True

    Scenario 2 -- Obvious attack caught, deferred. SAFE. Greedy FAILS.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(*probs['scenario_2_obvious_caught'][:2])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 5)
    >>> ('a_run_untrusted_policy_attack', 'task_002', 'obvious') in r2.plan
    True
    >>> ('a_defer_to_trusted', 'task_002') in r2.plan
    True

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g2 = s.find_plan(*probs['scenario_2_obvious_caught'][:2])
    >>> sys.stdout = _o
    >>> g2.success
    False

    Scenario 3 -- Subtle attack evades monitor. VULNERABILITY.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(*probs['scenario_3_subtle_evades'][:2])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 5)
    >>> ('a_run_untrusted_policy_attack', 'task_003', 'subtle') in r3.plan
    True
    >>> ('a_accept_output', 'task_003') in r3.plan
    True

    Scenario 4 -- Subtle attack caught with tight threshold. SAFE.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r4 = s.find_plan(*probs['scenario_4_subtle_caught_tight'][:2])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_004') in r4.plan
    True

    Scenario 5 -- Moderate attack caught. SAFE.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r5 = s.find_plan(*probs['scenario_5_moderate_caught'][:2])
    >>> sys.stdout = _o
    >>> r5.success, len(r5.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_005') in r5.plan
    True

    Scenario 6 -- Moderate attack evades. VULNERABILITY.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r6 = s.find_plan(*probs['scenario_6_moderate_evades'][:2])
    >>> sys.stdout = _o
    >>> r6.success, len(r6.plan)
    (True, 5)
    >>> ('a_run_untrusted_policy_attack', 'task_006', 'moderate') in r6.plan
    True
    >>> ('a_accept_output', 'task_006') in r6.plan
    True

    Scenario 7 -- Honest output deferred (overly tight threshold). OVER-SENSITIVE.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r7 = s.find_plan(*probs['scenario_7_honest_tight_threshold'][:2])
    >>> sys.stdout = _o
    >>> r7.success, len(r7.plan)
    (True, 5)
    >>> ('a_run_untrusted_policy_honest', 'task_007') in r7.plan
    True
    >>> ('a_defer_to_trusted', 'task_007') in r7.plan
    True

    Scenario 8 -- Obvious attack accepted (overly loose threshold). VULNERABILITY.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r8 = s.find_plan(*probs['scenario_8_obvious_loose_threshold'][:2])
    >>> sys.stdout = _o
    >>> r8.success, len(r8.plan)
    (True, 5)
    >>> ('a_run_untrusted_policy_attack', 'task_008', 'obvious') in r8.plan
    True
    >>> ('a_accept_output', 'task_008') in r8.plan
    True

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
