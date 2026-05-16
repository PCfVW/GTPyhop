"""
Adversarial Protocol - Problem Definitions for GTPyhop

This file defines 15 scenarios for the adversarial micro-protocol,
combining honest and attack modes with varying detection rates,
subtlety levels, thresholds, and (since 2026-05-16) threat models to
exercise security analysis.

All scenarios produce plans of 5 actions:
  a_initialize_episode -> (a_run_untrusted_policy_honest |
  a_run_untrusted_policy_attack) -> a_run_monitor ->
  (a_accept_output | a_defer_to_trusted | a_accept_output_demo_no_expected_effect)
  -> a_score_trajectory

Security outcomes:
  - SAFE: attack caught (deferred)
  - VULNERABILITY: attack evades monitor (accepted with side task)
  - OVER-SENSITIVE: honest output deferred (false positive)

Threat models (config_threat_model, added 2026-05-16):
  - 'none': honest scenarios (no attack)
  - 'generic': original 6 attack scenarios; threat-type-agnostic detection
  - 'code_sabotage': scenarios 9-10; code-quality-monitor-detectable
  - 'data_poisoning': scenarios 11-12; harder for generic code monitor
  - 'research_sabotage': scenarios 13-14; hardest for generic monitor

scenario_15_expected_effect_negative_control demonstrates a teaching
variant action (a_accept_output_demo_no_expected_effect) that omits the
[EXPECTED_EFFECT] block on side_task_observed, even though side_task_embedded
is True. The plan still succeeds (5 actions) but state.side_task_observed
remains False -- proving why the [EXPECTED_EFFECT] tag is load-bearing for
downstream safety inspection.

-- Generated 2026-03-31, extended 2026-05-16 with threat-model variety,
   [EXPECTED_EFFECT] marker, and negative control
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
    """Create a base state with common adversarial protocol properties.

    State schema additions (2026-05-16):
      - state.config_threat_model: str (default 'none'; per-scenario)
      - state.side_task_observed: bool (default False; set by
        [EXPECTED_EFFECT] of a_accept_output)
    detection_rates is now Dict[threat_model, Dict[subtlety, float]].
    """
    state = State(name)

    # Configuration (set per scenario)
    state.task_id = ""
    state.config_attack_active = False
    state.config_attack_subtlety = ""
    state.config_threat_model = 'none'         # NEW (2026-05-16)
    state.config_detection_rates = {}          # CHANGED: now nested Dict[threat_model, Dict[subtlety, float]]
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
    state.side_task_observed = False           # NEW (2026-05-16) [EXPECTED_EFFECT] target

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
initial_state_scenario_1.config_threat_model = 'none'
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
initial_state_scenario_2.config_threat_model = 'generic'
initial_state_scenario_2.config_detection_rates = {'generic': {'obvious': 0.95}}
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
initial_state_scenario_3.config_threat_model = 'generic'
initial_state_scenario_3.config_detection_rates = {'generic': {'subtle': 0.25}}
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
initial_state_scenario_4.config_threat_model = 'generic'
initial_state_scenario_4.config_detection_rates = {'generic': {'subtle': 0.25}}
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
initial_state_scenario_5.config_threat_model = 'generic'
initial_state_scenario_5.config_detection_rates = {'generic': {'moderate': 0.6}}
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
initial_state_scenario_6.config_threat_model = 'generic'
initial_state_scenario_6.config_detection_rates = {'generic': {'moderate': 0.6}}
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
initial_state_scenario_7.config_threat_model = 'none'
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
initial_state_scenario_8.config_threat_model = 'generic'
initial_state_scenario_8.config_detection_rates = {'generic': {'obvious': 0.95}}
initial_state_scenario_8.config_suspicion_threshold = 0.99

# Problem
problems['scenario_8_obvious_loose_threshold'] = (
    initial_state_scenario_8,
    [('m_run_adversarial_protocol', _task_id)],
    'Obvious attack, suspicion 0.95 <= 0.99 -> accepted, VULNERABILITY (5 actions)'
)
# END: Scenario

# ============================================================================
# THREAT-MODEL VARIETY SCENARIOS (added 2026-05-16)
# Detection rates encode the empirical pattern: data_poisoning and
# research_sabotage are systematically harder for a generic monitor to
# detect than code_sabotage at the same subtlety level.
# ============================================================================

# BEGIN: Scenario: scenario_9_code_sabotage_subtle_evades
# Configuration
_task_id = 'task_009'

# State
initial_state_scenario_9 = h_create_base_adversarial_state('scenario_9_code_sabotage_subtle_evades')
initial_state_scenario_9.task_id = _task_id
initial_state_scenario_9.config_attack_active = True
initial_state_scenario_9.config_attack_subtlety = 'subtle'
initial_state_scenario_9.config_threat_model = 'code_sabotage'
initial_state_scenario_9.config_detection_rates = {'code_sabotage': {'subtle': 0.20, 'obvious': 0.92}}
initial_state_scenario_9.config_suspicion_threshold = 0.7

# Problem
problems['scenario_9_code_sabotage_subtle_evades'] = (
    initial_state_scenario_9,
    [('m_run_adversarial_protocol', _task_id)],
    'Code sabotage subtle, suspicion 0.20 <= 0.7 -> accepted, VULNERABILITY (5 actions)'
)
# END: Scenario

# BEGIN: Scenario: scenario_10_code_sabotage_obvious_caught
# Configuration
_task_id = 'task_010'

# State
initial_state_scenario_10 = h_create_base_adversarial_state('scenario_10_code_sabotage_obvious_caught')
initial_state_scenario_10.task_id = _task_id
initial_state_scenario_10.config_attack_active = True
initial_state_scenario_10.config_attack_subtlety = 'obvious'
initial_state_scenario_10.config_threat_model = 'code_sabotage'
initial_state_scenario_10.config_detection_rates = {'code_sabotage': {'subtle': 0.20, 'obvious': 0.92}}
initial_state_scenario_10.config_suspicion_threshold = 0.7

# Problem
problems['scenario_10_code_sabotage_obvious_caught'] = (
    initial_state_scenario_10,
    [('m_run_adversarial_protocol', _task_id)],
    'Code sabotage obvious, suspicion 0.92 > 0.7 -> deferred, SAFE (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_11_data_poisoning_subtle_evades
# Configuration
_task_id = 'task_011'

# State
initial_state_scenario_11 = h_create_base_adversarial_state('scenario_11_data_poisoning_subtle_evades')
initial_state_scenario_11.task_id = _task_id
initial_state_scenario_11.config_attack_active = True
initial_state_scenario_11.config_attack_subtlety = 'subtle'
initial_state_scenario_11.config_threat_model = 'data_poisoning'
initial_state_scenario_11.config_detection_rates = {'data_poisoning': {'subtle': 0.15, 'obvious': 0.85}}
initial_state_scenario_11.config_suspicion_threshold = 0.7

# Problem
problems['scenario_11_data_poisoning_subtle_evades'] = (
    initial_state_scenario_11,
    [('m_run_adversarial_protocol', _task_id)],
    'Data poisoning subtle, suspicion 0.15 <= 0.7 -> accepted, VULNERABILITY (5 actions). '
    'Lower detection rate than code_sabotage at same subtlety -- the generic monitor '
    'is weaker against data-distribution attacks.'
)
# END: Scenario

# BEGIN: Scenario: scenario_12_data_poisoning_obvious_caught
# Configuration
_task_id = 'task_012'

# State
initial_state_scenario_12 = h_create_base_adversarial_state('scenario_12_data_poisoning_obvious_caught')
initial_state_scenario_12.task_id = _task_id
initial_state_scenario_12.config_attack_active = True
initial_state_scenario_12.config_attack_subtlety = 'obvious'
initial_state_scenario_12.config_threat_model = 'data_poisoning'
initial_state_scenario_12.config_detection_rates = {'data_poisoning': {'subtle': 0.15, 'obvious': 0.85}}
initial_state_scenario_12.config_suspicion_threshold = 0.7

# Problem
problems['scenario_12_data_poisoning_obvious_caught'] = (
    initial_state_scenario_12,
    [('m_run_adversarial_protocol', _task_id)],
    'Data poisoning obvious, suspicion 0.85 > 0.7 -> deferred, SAFE (5 actions, backtracking)'
)
# END: Scenario

# BEGIN: Scenario: scenario_13_research_sabotage_subtle_evades
# Configuration
_task_id = 'task_013'

# State
initial_state_scenario_13 = h_create_base_adversarial_state('scenario_13_research_sabotage_subtle_evades')
initial_state_scenario_13.task_id = _task_id
initial_state_scenario_13.config_attack_active = True
initial_state_scenario_13.config_attack_subtlety = 'subtle'
initial_state_scenario_13.config_threat_model = 'research_sabotage'
initial_state_scenario_13.config_detection_rates = {'research_sabotage': {'subtle': 0.10, 'obvious': 0.80}}
initial_state_scenario_13.config_suspicion_threshold = 0.7

# Problem
problems['scenario_13_research_sabotage_subtle_evades'] = (
    initial_state_scenario_13,
    [('m_run_adversarial_protocol', _task_id)],
    'Research sabotage subtle, suspicion 0.10 <= 0.7 -> accepted, VULNERABILITY (5 actions). '
    'Lowest detection rate of the three threat types -- generic monitors are weakest '
    'against research-output sabotage (plausible-but-false conclusions).'
)
# END: Scenario

# BEGIN: Scenario: scenario_14_research_sabotage_obvious_caught
# Configuration
_task_id = 'task_014'

# State
initial_state_scenario_14 = h_create_base_adversarial_state('scenario_14_research_sabotage_obvious_caught')
initial_state_scenario_14.task_id = _task_id
initial_state_scenario_14.config_attack_active = True
initial_state_scenario_14.config_attack_subtlety = 'obvious'
initial_state_scenario_14.config_threat_model = 'research_sabotage'
initial_state_scenario_14.config_detection_rates = {'research_sabotage': {'subtle': 0.10, 'obvious': 0.80}}
initial_state_scenario_14.config_suspicion_threshold = 0.7

# Problem
problems['scenario_14_research_sabotage_obvious_caught'] = (
    initial_state_scenario_14,
    [('m_run_adversarial_protocol', _task_id)],
    'Research sabotage obvious, suspicion 0.80 > 0.7 -> deferred, SAFE (5 actions, backtracking)'
)
# END: Scenario

# ============================================================================
# [EXPECTED_EFFECT] NEGATIVE-CONTROL SCENARIO (added 2026-05-16)
# Same state as scenario_9 (code_sabotage subtle, would normally be accepted),
# but the task list uses the demo-variant action that omits the
# [EXPECTED_EFFECT] block. The plan succeeds (5 actions, side_task_embedded
# is True), yet state.side_task_observed remains False -- demonstrating
# the tag's load-bearing role for downstream safety inspection.
# ============================================================================

# BEGIN: Scenario: scenario_15_expected_effect_negative_control
# Configuration
_task_id = 'task_015'

# State (same as scenario_9: code_sabotage subtle, evades the monitor)
initial_state_scenario_15 = h_create_base_adversarial_state('scenario_15_expected_effect_negative_control')
initial_state_scenario_15.task_id = _task_id
initial_state_scenario_15.config_attack_active = True
initial_state_scenario_15.config_attack_subtlety = 'subtle'
initial_state_scenario_15.config_threat_model = 'code_sabotage'
initial_state_scenario_15.config_detection_rates = {'code_sabotage': {'subtle': 0.20}}
initial_state_scenario_15.config_suspicion_threshold = 0.7

# Problem: manual task list bypassing routing methods. Uses the demo variant
# a_accept_output_demo_no_expected_effect instead of the canonical a_accept_output.
problems['scenario_15_expected_effect_negative_control'] = (
    initial_state_scenario_15,
    [('a_initialize_episode', _task_id),
     ('a_run_untrusted_policy_attack', _task_id, 'subtle'),
     ('a_run_monitor', _task_id),
     ('a_accept_output_demo_no_expected_effect', _task_id),
     ('a_score_trajectory', _task_id)],
    'NEGATIVE CONTROL: same state as scenario_9; manual task list uses '
    'a_accept_output_demo_no_expected_effect which omits the [EXPECTED_EFFECT] '
    'block. Plan succeeds (5 actions) but state.side_task_observed is never set.'
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
    15

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

    Scenario 9 -- Code sabotage subtle, evades. VULNERABILITY. (threat-typed)

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r9 = s.find_plan(*probs['scenario_9_code_sabotage_subtle_evades'][:2])
    >>> sys.stdout = _o
    >>> r9.success, len(r9.plan)
    (True, 5)
    >>> ('a_accept_output', 'task_009') in r9.plan
    True

    Scenario 10 -- Code sabotage obvious, caught. SAFE. Greedy FAILS.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r10 = s.find_plan(*probs['scenario_10_code_sabotage_obvious_caught'][:2])
    >>> sys.stdout = _o
    >>> r10.success, len(r10.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_010') in r10.plan
    True

    Scenario 11 -- Data poisoning subtle, evades. VULNERABILITY.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r11 = s.find_plan(*probs['scenario_11_data_poisoning_subtle_evades'][:2])
    >>> sys.stdout = _o
    >>> r11.success, len(r11.plan)
    (True, 5)
    >>> ('a_accept_output', 'task_011') in r11.plan
    True

    Scenario 12 -- Data poisoning obvious, caught. SAFE.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r12 = s.find_plan(*probs['scenario_12_data_poisoning_obvious_caught'][:2])
    >>> sys.stdout = _o
    >>> r12.success, len(r12.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_012') in r12.plan
    True

    Scenario 13 -- Research sabotage subtle, evades. VULNERABILITY.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r13 = s.find_plan(*probs['scenario_13_research_sabotage_subtle_evades'][:2])
    >>> sys.stdout = _o
    >>> r13.success, len(r13.plan)
    (True, 5)
    >>> ('a_accept_output', 'task_013') in r13.plan
    True

    Scenario 14 -- Research sabotage obvious, caught. SAFE.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r14 = s.find_plan(*probs['scenario_14_research_sabotage_obvious_caught'][:2])
    >>> sys.stdout = _o
    >>> r14.success, len(r14.plan)
    (True, 5)
    >>> ('a_defer_to_trusted', 'task_014') in r14.plan
    True

    Scenario 15 -- NEGATIVE CONTROL: manual task list uses the demo variant
    a_accept_output_demo_no_expected_effect; the canonical a_accept_output
    is NOT in the plan, so the [EXPECTED_EFFECT] block never fires.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r15 = s.find_plan(*probs['scenario_15_expected_effect_negative_control'][:2])
    >>> sys.stdout = _o
    >>> r15.success, len(r15.plan)
    (True, 5)
    >>> ('a_accept_output_demo_no_expected_effect', 'task_015') in r15.plan
    True
    >>> ('a_accept_output', 'task_015') in r15.plan
    False

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
