"""
Problem definitions for the Feature Space Poetry HTN Domain.
-- Generated 2026-02-18

This file defines initial states for feature-space intervention workflows
that automate the suppress+inject protocol from melometis Version D. The
HTN plans interventions on the model's internal representations (CLT
activation space), not text generation.

The workflow demonstrates coordination between 3 servers:
  - Local computation: Initialize, suppress, evaluate threshold, compile report
  - Server 1 (inference_server): Forward passes, probability measurement
  - Server 2 (clt_server): CLT encode/decode, feature injection

Scenario structure: ground truth + counterfactual what-ifs
  - scenario_0_version_d_star_result:  Ground truth -- what actually happened in Version D
  - scenario_1_cheapest_first:         What if 'around' wasn't tried first?
  - scenario_2_planning_layer_only:    What if we only needed the planning layer?
  - scenario_3_different_group:        What if we redirected a different group?

Plan length formula: L + 8
  Where L = number of layers to encode
  init + locate + baseline + (encode x L) + suppress + inject + measure +
  evaluate + report

Probability provenance:
  - L22:10243 ("around"): MEASURED in Version D (suppress_inject_sweep.json)
    - 0.483 on -out/about prompt, 0.057 on -oo/who prompt
  - L16:7712 ("ground"), L25:3298 ("round"): ESTIMATED from CLT decoder analysis
    - Not tested in the Version D sweep (one feature per group)
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

def h_create_base_intervention_state(name: str) -> State:
    """Create a base state with common feature-space intervention properties."""
    state = State(name)
    # Intervention configuration (set per scenario)
    state.model_name = ""
    state.prompt_text = ""
    state.from_group = ""
    state.to_group = ""
    state.candidate_features = []
    state.layers_to_encode = []
    state.injection_strength = 1.0
    state.probability_threshold = 0.40
    state.candidate_probabilities = {}
    # Model specification (set by a_initialize_intervention)
    state.model_spec = {}
    # The "world" -- activation space (set by actions)
    state.active_features = {}
    state.residual_stream = "uninitialized"
    state.target_distribution = {}
    state.injection_history = []
    state.suppressed_features = {}
    # Tracking counters
    state.num_layers_encoded = 0
    state.num_candidates_tried = 0
    state.measured_probability = 0.0
    # Workflow enablers (all initially False)
    state.intervention_initialized = False
    state.planning_site_located = False
    state.planning_site_position = ""
    state.baseline_measured = False
    state.baseline_probability = ""
    state.encoding_complete = False
    state.suppression_complete = False
    state.injection_complete = False
    state.effect_measured = False
    state.threshold_met = False
    state.intervention_complete = False
    # Report output (set by a_compile_intervention_report)
    state.intervention_report = {}
    return state


# ============================================================================
# PROMPTS (actual Version D prompts from suppress_inject_sweep.rs)
# ============================================================================

# -out/about prompt: planning site position 31
PROMPT_OUT_ABOUT = (
    "The stars were twinkling in the night,\n"
    "The lanterns cast a golden light.\n"
    "She wandered in the dark about,\n"
    "And found a hidden passage"
)

# -oo/who prompt: planning site position 35
PROMPT_OO_WHO = (
    "The sun goes up, the sun goes down,\n"
    "The moon shines bright above the town.\n"
    "Nobody knows or remembers who,\n"
    "Would come to find a way back"
)


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: feature_space_poetry

# BEGIN: Scenario: scenario_0_version_d_star_result
# Ground truth: what actually happened in Version D
# Suppress -out, inject -ound "around" (L22:10243) -> 48.29% redirect
# "around" is the strongest candidate and is tried first -> succeeds immediately
# Prompt: actual Version D -out (about) prompt from suppress_inject_sweep.rs
_model = "Gemma_2_2B"
_prompt = PROMPT_OUT_ABOUT
_from_group = "out"
_to_group = "ound"
_candidates = ["L22:10243", "L16:7712", "L25:3298"]
_layers = list(range(26))
# Probabilities: L22:10243 MEASURED (0.483), others ESTIMATED from CLT analysis
_probs = {"L22:10243": 0.483, "L16:7712": 0.003, "L25:3298": 0.001}

# State
initial_state_scenario_0 = h_create_base_intervention_state('scenario_0_version_d_star_result')
initial_state_scenario_0.model_name = _model
initial_state_scenario_0.prompt_text = _prompt
initial_state_scenario_0.from_group = _from_group
initial_state_scenario_0.to_group = _to_group
initial_state_scenario_0.candidate_features = _candidates
initial_state_scenario_0.layers_to_encode = _layers
initial_state_scenario_0.candidate_probabilities = _probs

# Problem
problems['scenario_0_version_d_star_result'] = (
    initial_state_scenario_0,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Version D star result ({_from_group} -> {_to_group}, {len(_layers)} layers, no backtracking) -> 34 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_1_cheapest_first
# What-if: what if we tried candidates in cheapest-layer-first order?
# Same prompt and threshold as scenario 0, but candidates reordered:
# L25 (closest to output) first, then L16, then L22 (strongest but tried last)
# L25:3298 (0.001) FAILS -> backtrack, L16:7712 (0.003) FAILS -> backtrack,
# L22:10243 (0.483) SUCCEEDS
_model = "Gemma_2_2B"
_prompt = PROMPT_OUT_ABOUT
_from_group = "out"
_to_group = "ound"
_candidates = ["L25:3298", "L16:7712", "L22:10243"]  # cheapest-layer-first order
_layers = list(range(26))
_probs = {"L22:10243": 0.483, "L16:7712": 0.003, "L25:3298": 0.001}

# State
initial_state_scenario_1 = h_create_base_intervention_state('scenario_1_cheapest_first')
initial_state_scenario_1.model_name = _model
initial_state_scenario_1.prompt_text = _prompt
initial_state_scenario_1.from_group = _from_group
initial_state_scenario_1.to_group = _to_group
initial_state_scenario_1.candidate_features = _candidates
initial_state_scenario_1.layers_to_encode = _layers
initial_state_scenario_1.candidate_probabilities = _probs

# Problem
problems['scenario_1_cheapest_first'] = (
    initial_state_scenario_1,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Cheapest first ({_from_group} -> {_to_group}, {len(_layers)} layers, backtracking) -> 34 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_planning_layer_only
# What-if: what if we only needed to encode the planning layer?
# Same prompt and threshold, but only L16 encoded. Single candidate "around".
_model = "Gemma_2_2B"
_prompt = PROMPT_OUT_ABOUT
_from_group = "out"
_to_group = "ound"
_candidates = ["L22:10243"]
_layers = [16]
_probs = {"L22:10243": 0.483}

# State
initial_state_scenario_2 = h_create_base_intervention_state('scenario_2_planning_layer_only')
initial_state_scenario_2.model_name = _model
initial_state_scenario_2.prompt_text = _prompt
initial_state_scenario_2.from_group = _from_group
initial_state_scenario_2.to_group = _to_group
initial_state_scenario_2.candidate_features = _candidates
initial_state_scenario_2.layers_to_encode = _layers
initial_state_scenario_2.candidate_probabilities = _probs

# Problem
problems['scenario_2_planning_layer_only'] = (
    initial_state_scenario_2,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Planning layer only ({_from_group} -> {_to_group}, {len(_layers)} layer, no backtracking) -> 9 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_different_group
# What-if: what if we redirected a different group pair?
# Suppress -oo (instead of -out), still inject -ound "around"
# On the -oo/who prompt, "around" achieves only 5.67% (MEASURED in Version D)
# Threshold lowered to 0.02 (redirect is much weaker on this prompt)
# Candidates: L25:3298 (estimated 0.001) tried first -> FAILS, backtrack to
# L22:10243 (measured 0.057) -> SUCCEEDS
_model = "Gemma_2_2B"
_prompt = PROMPT_OO_WHO
_from_group = "oo"
_to_group = "ound"
_candidates = ["L25:3298", "L22:10243"]
_layers = [16, 25]
# L22:10243 MEASURED on -oo/who prompt (suppress_inject_sweep.json line 23356)
_probs = {"L22:10243": 0.057, "L25:3298": 0.001}

# State
initial_state_scenario_3 = h_create_base_intervention_state('scenario_3_different_group')
initial_state_scenario_3.model_name = _model
initial_state_scenario_3.prompt_text = _prompt
initial_state_scenario_3.from_group = _from_group
initial_state_scenario_3.to_group = _to_group
initial_state_scenario_3.candidate_features = _candidates
initial_state_scenario_3.layers_to_encode = _layers
initial_state_scenario_3.probability_threshold = 0.02
initial_state_scenario_3.candidate_probabilities = _probs

# Problem
problems['scenario_3_different_group'] = (
    initial_state_scenario_3,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Different group ({_from_group} -> {_to_group}, {len(_layers)} layers, backtracking) -> 10 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.poetry.feature_space_poetry import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    4

    Scenario 0 — Version D star result (ground truth, 34 actions).
    L22:10243 "around" at 48.29% succeeds on first try (threshold 0.40).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r0 = s.find_plan(*probs['scenario_0_version_d_star_result'][:2])
    >>> sys.stdout = _o
    >>> r0.success, len(r0.plan)
    (True, 34)

    Scenario 1 — Cheapest first (34 actions, backtracking).
    L25:3298 (0.001) and L16:7712 (0.003) fail, L22:10243 (0.483) succeeds.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(*probs['scenario_1_cheapest_first'][:2])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 34)
    >>> [a for a in r1.plan if a[0] == 'a_inject_feature'][0][1]
    'L22:10243'

    Scenario 2 — Planning layer only (9 actions, no backtracking).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(*probs['scenario_2_planning_layer_only'][:2])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 9)

    Scenario 3 — Different group (10 actions, oo -> ound, backtracking).
    L22:10243 "around" at 5.67% on the -oo/who prompt (threshold 0.02).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(*probs['scenario_3_different_group'][:2])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 10)

    Greedy planner fails on backtracking scenarios (1 and 3).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g1 = s.find_plan(*probs['scenario_1_cheapest_first'][:2])
    >>> sys.stdout = _o
    >>> g1.success
    False

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g3 = s.find_plan(*probs['scenario_3_different_group'][:2])
    >>> sys.stdout = _o
    >>> g3.success
    False

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
