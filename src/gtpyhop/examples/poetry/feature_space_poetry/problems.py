"""
Problem definitions for the Feature Space Poetry HTN Domain.
-- Generated 2026-02-18, updated 2026-02-23

This file defines initial states for feature-space intervention workflows
that automate the suppress+inject protocol from melometis. The HTN plans
interventions on the model's internal representations (CLT activation
space), not text generation.

The workflow demonstrates coordination between 3 servers:
  - Local computation: Initialize, suppress, evaluate threshold, compile report
  - Server 1 (inference_server): Forward passes, probability measurement
  - Server 2 (clt_server): CLT encode/decode, feature injection

Three configurations are covered:
  - Gemma 2 2B (26 layers, CLT 426K): forward planning model (Version D)
  - Llama 3.2 1B (16 layers, CLT 524K): late selection model (Version L)
  - Gemma 2 2B (26 layers, CLT 2.5M): word-level planning model (Version D 2.5M)

Scenario structure:
  Gemma 2 2B (scenarios 0-3): ground truth + counterfactual what-ifs
    - scenario_0_version_d_star_result:  Ground truth -- Version D star result
    - scenario_1_cheapest_first:         What if 'around' wasn't tried first?
    - scenario_2_planning_layer_only:    What if we only needed the planning layer?
    - scenario_3_different_group:        What if we redirected a different group?
  Llama 3.2 1B (scenarios 4-7): replication on a late-selection model
    - scenario_4_llama_star_result:      Llama star result -- ee -> at, "that"
    - scenario_5_llama_sat_first:        What if 'sat' was tried before 'that'?
    - scenario_6_llama_output_layer:     What if we only encoded L15?
    - scenario_7_llama_different_group:  What if we redirected at -> ore?
  Gemma 2 2B + CLT 2.5M (scenarios 8-11): word-level planning model
    - scenario_8_version_d_2_5m_star:     2.5M star result -- out -> an, "can" word-level
    - scenario_9_2_5m_weakest_first:      What if "plan" was tried first?
    - scenario_10_2_5m_planning_layer:    What if we only needed L25?
    - scenario_11_2_5m_different_group:   What if we redirected from -oo?

Plan length formula: L + 8
  Where L = number of layers to encode
  init + locate + baseline + (encode x L) + suppress + inject + measure +
  evaluate + report

Probability provenance:
  Gemma 2 2B (Version D):
  - L22:10243 ("around"): MEASURED in Version D (suppress_inject_sweep.json)
    - 0.483 on -out/about prompt, 0.057 on -oo/who prompt
  - L16:7712 ("ground"), L25:3298 ("round"): ESTIMATED from CLT decoder analysis
  Llama 3.2 1B (Version L):
  - L14:13043 ("that"): MEASURED in Version L (suppress_inject_sweep_llama_v2.json)
    - 0.777 on -ee prompt, 0.452 on -oo prompt
  - L14:6132 ("sat"): ESTIMATED from CLT decoder analysis (cosine 0.32)
  - L1:5297 ("for"): MEASURED on -at prompt (0.009)
  - L3:22663 ("or"), L10:18203 ("more"): ESTIMATED from CLT decoder analysis
  Gemma 2 2B (Version D 2.5M):
  - L25:82839 ("can"): MEASURED in 2.5M sweep (outputs/2.5M/suppress_inject_sweep.json)
    - 0.482 on -out/about prompt, 0.425 on -out/shout prompt, 0.400 on -oo/who prompt
  - L25:45672 ("man"), L25:71041 ("plan"): ESTIMATED from 2.5M CLT decoder analysis
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
# PROMPTS — Gemma 2 2B (Version D, from suppress_inject_sweep.rs)
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

# -out/shout prompt (sailor variant, used with 2.5M CLT): planning site position 34
PROMPT_OUT_SHOUT = (
    "A sailor sailed across the bay,\n"
    "And dreamed of home throughout the day.\n"
    "He raised his voice and gave a shout,\n"
    "The truth was struggling to come "
)

# ============================================================================
# PROMPTS — Llama 3.2 1B (Version L, from corpus/prompts_llama.json)
# ============================================================================

# -ee prompt: selection site position 30
PROMPT_EE_LLAMA = (
    "The birds were singing in the tree,\n"
    "And everything was wild and free.\n"
    "The river ran down to the sea,\n"
    "There is so much we cannot"
)

# -oo prompt: selection site position 30
PROMPT_OO_LLAMA = (
    "The morning sky was painted blue,\n"
    "The garden sparkled bright with dew.\n"
    "The world had started fresh and new,\n"
    "And there was nothing left to"
)

# -at prompt: selection site position 32
PROMPT_AT_LLAMA = (
    "The old man wore a tattered hat,\n"
    "Upon the porch he always sat.\n"
    "He told the tale of this and that,\n"
    "And in the corner slept the"
)


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: feature_space_poetry

# ----------------------------------------------------------------------------
# Gemma 2 2B scenarios (0-3): forward planning model, 26 layers, CLT 426K
# Source: melometis Version D (suppress_inject_sweep.json, 136 pairs)
# ----------------------------------------------------------------------------

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

# ----------------------------------------------------------------------------
# Llama 3.2 1B scenarios (4-7): late selection model, 16 layers, CLT 524K
# Source: melometis Version L (suppress_inject_sweep_llama_v2.json, 44 pairs)
# Key difference: 82% of planning features at L15 (last layer), no forward
# planning. CLT features are causally effective but only at the output
# boundary. Same HTN protocol, different model = different story.
# ----------------------------------------------------------------------------

# BEGIN: Scenario: scenario_4_llama_star_result
# Llama ground truth: suppress -ee, inject -at "that" (L14:13043) -> 77.7% redirect
# "that" is the strongest candidate across all Llama experiments
# Prompt: -ee quatrain from corpus/prompts_llama.json
_model = "Llama_3_2_1B"
_prompt = PROMPT_EE_LLAMA
_from_group = "ee"
_to_group = "at"
_candidates = ["L14:13043", "L14:6132"]
_layers = list(range(16))
# Probabilities: L14:13043 MEASURED (0.777), L14:6132 ESTIMATED from CLT analysis
_probs = {"L14:13043": 0.777, "L14:6132": 0.01}

# State
initial_state_scenario_4 = h_create_base_intervention_state('scenario_4_llama_star_result')
initial_state_scenario_4.model_name = _model
initial_state_scenario_4.prompt_text = _prompt
initial_state_scenario_4.from_group = _from_group
initial_state_scenario_4.to_group = _to_group
initial_state_scenario_4.candidate_features = _candidates
initial_state_scenario_4.layers_to_encode = _layers
initial_state_scenario_4.candidate_probabilities = _probs

# Problem
problems['scenario_4_llama_star_result'] = (
    initial_state_scenario_4,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Llama star result ({_from_group} -> {_to_group}, {len(_layers)} layers, no backtracking) -> 24 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_5_llama_sat_first
# What-if: what if "sat" (weaker feature) was tried before "that"?
# Same prompt and threshold as scenario 4, but candidates reordered:
# L14:6132 "sat" (estimated 0.01) FAILS -> backtrack, L14:13043 "that" (0.777) SUCCEEDS
# Contrast with Gemma scenario_1: Gemma had 3 candidates and 2 backtracks;
# Llama has only 2 candidates in the -at group (vocabulary poverty)
_model = "Llama_3_2_1B"
_prompt = PROMPT_EE_LLAMA
_from_group = "ee"
_to_group = "at"
_candidates = ["L14:6132", "L14:13043"]  # sat first, that second
_layers = list(range(16))
_probs = {"L14:13043": 0.777, "L14:6132": 0.01}

# State
initial_state_scenario_5 = h_create_base_intervention_state('scenario_5_llama_sat_first')
initial_state_scenario_5.model_name = _model
initial_state_scenario_5.prompt_text = _prompt
initial_state_scenario_5.from_group = _from_group
initial_state_scenario_5.to_group = _to_group
initial_state_scenario_5.candidate_features = _candidates
initial_state_scenario_5.layers_to_encode = _layers
initial_state_scenario_5.candidate_probabilities = _probs

# Problem
problems['scenario_5_llama_sat_first'] = (
    initial_state_scenario_5,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Llama sat first ({_from_group} -> {_to_group}, {len(_layers)} layers, backtracking) -> 24 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_6_llama_output_layer
# What-if: what if we only encoded L15 (where 82% of planning features live)?
# In Gemma, scenario_2 used only L16 as the "planning layer" -- a meaningful
# simplification from 26 layers. In Llama, encoding only L15 is barely a
# simplification because the circuit is already concentrated there.
_model = "Llama_3_2_1B"
_prompt = PROMPT_EE_LLAMA
_from_group = "ee"
_to_group = "at"
_candidates = ["L14:13043"]
_layers = [15]
# Same probability: L14:13043 MEASURED at 0.777 on -ee prompt
_probs = {"L14:13043": 0.777}

# State
initial_state_scenario_6 = h_create_base_intervention_state('scenario_6_llama_output_layer')
initial_state_scenario_6.model_name = _model
initial_state_scenario_6.prompt_text = _prompt
initial_state_scenario_6.from_group = _from_group
initial_state_scenario_6.to_group = _to_group
initial_state_scenario_6.candidate_features = _candidates
initial_state_scenario_6.layers_to_encode = _layers
initial_state_scenario_6.candidate_probabilities = _probs

# Problem
problems['scenario_6_llama_output_layer'] = (
    initial_state_scenario_6,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Llama output layer only ({_from_group} -> {_to_group}, {len(_layers)} layer, no backtracking) -> 9 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_7_llama_different_group
# What-if: what if we redirected a different group pair on a different prompt?
# Suppress -at (on the -at prompt), inject -ore (AO1 R) group
# The -ore group has 3 candidates: "or" (L3), "more" (L10), "for" (L1)
# Effects are much weaker on this prompt (max P=0.009 for "for")
# Threshold lowered to 0.005 (paralleling Gemma scenario_3's 0.02)
# Candidates tried cheapest-layer-first: "or" FAILS, "more" FAILS, "for" SUCCEEDS
_model = "Llama_3_2_1B"
_prompt = PROMPT_AT_LLAMA
_from_group = "at"
_to_group = "ore"
_candidates = ["L3:22663", "L10:18203", "L1:5297"]  # or, more, for (weakest first)
_layers = [1, 14]  # feature source layers
# L1:5297 "for" MEASURED on -at prompt (suppress_inject_sweep_llama_v2.json)
# L3:22663 "or" and L10:18203 "more" ESTIMATED from CLT decoder analysis
_probs = {"L1:5297": 0.009, "L3:22663": 0.001, "L10:18203": 0.002}

# State
initial_state_scenario_7 = h_create_base_intervention_state('scenario_7_llama_different_group')
initial_state_scenario_7.model_name = _model
initial_state_scenario_7.prompt_text = _prompt
initial_state_scenario_7.from_group = _from_group
initial_state_scenario_7.to_group = _to_group
initial_state_scenario_7.candidate_features = _candidates
initial_state_scenario_7.layers_to_encode = _layers
initial_state_scenario_7.probability_threshold = 0.005
initial_state_scenario_7.candidate_probabilities = _probs

# Problem
problems['scenario_7_llama_different_group'] = (
    initial_state_scenario_7,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Llama different group ({_from_group} -> {_to_group}, {len(_layers)} layers, backtracking) -> 10 actions'
)
# END: Scenario

# ----------------------------------------------------------------------------
# Gemma 2 2B + CLT 2.5M scenarios (8-11): word-level planning model, 26 layers
# Source: melometis Version D 2.5M (outputs/2.5M/suppress_inject_sweep.json, 264 pairs)
# Key upgrade: 2.5M CLT provides word-level features (98,304 features/layer).
# Each word has its own dedicated feature (209/209 ranked #1 in own feature).
# Same model (Gemma 2 2B), finer CLT = word-level control.
# domain.py provides RHYME_GROUPS["an"] and FEATURE_CANDIDATES["an"] for these scenarios.
# ----------------------------------------------------------------------------

# BEGIN: Scenario: scenario_8_version_d_2_5m_star
# Ground truth: 2.5M word-level star result
# Suppress -out, inject -an "can" (L25:82839) -> 48.20% redirect
# "can" is the strongest 2.5M candidate and is tried first -> succeeds immediately
# This is the 2.5M analog of scenario 0, demonstrating word-level precision
_model = "Gemma_2_2B"
_prompt = PROMPT_OUT_ABOUT
_from_group = "out"
_to_group = "an"
_candidates = ["L25:82839", "L25:45672", "L25:71041"]
_layers = list(range(26))
# Probabilities: L25:82839 MEASURED (0.482), others ESTIMATED from 2.5M CLT analysis
_probs = {"L25:82839": 0.482, "L25:45672": 0.002, "L25:71041": 0.001}

# State
initial_state_scenario_8 = h_create_base_intervention_state('scenario_8_version_d_2_5m_star')
initial_state_scenario_8.model_name = _model
initial_state_scenario_8.prompt_text = _prompt
initial_state_scenario_8.from_group = _from_group
initial_state_scenario_8.to_group = _to_group
initial_state_scenario_8.candidate_features = _candidates
initial_state_scenario_8.layers_to_encode = _layers
initial_state_scenario_8.candidate_probabilities = _probs

# Problem
problems['scenario_8_version_d_2_5m_star'] = (
    initial_state_scenario_8,
    [('m_redirect_rhyme', _model, _prompt)],
    f'Version D 2.5M star result ({_from_group} -> {_to_group}, {len(_layers)} layers, no backtracking) -> 34 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_9_2_5m_weakest_first
# What-if: what if we tried candidates in weakest-first order?
# Same prompt and threshold as scenario 8, but candidates reordered:
# L25:71041 "plan" (0.001) FAILS -> backtrack, L25:45672 "man" (0.002) FAILS ->
# backtrack, L25:82839 "can" (0.482) SUCCEEDS
_model = "Gemma_2_2B"
_prompt = PROMPT_OUT_ABOUT
_from_group = "out"
_to_group = "an"
_candidates = ["L25:71041", "L25:45672", "L25:82839"]  # weakest-first order
_layers = list(range(26))
_probs = {"L25:82839": 0.482, "L25:45672": 0.002, "L25:71041": 0.001}

# State
initial_state_scenario_9 = h_create_base_intervention_state('scenario_9_2_5m_weakest_first')
initial_state_scenario_9.model_name = _model
initial_state_scenario_9.prompt_text = _prompt
initial_state_scenario_9.from_group = _from_group
initial_state_scenario_9.to_group = _to_group
initial_state_scenario_9.candidate_features = _candidates
initial_state_scenario_9.layers_to_encode = _layers
initial_state_scenario_9.candidate_probabilities = _probs

# Problem
problems['scenario_9_2_5m_weakest_first'] = (
    initial_state_scenario_9,
    [('m_redirect_rhyme', _model, _prompt)],
    f'2.5M weakest first ({_from_group} -> {_to_group}, {len(_layers)} layers, backtracking) -> 34 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_10_2_5m_planning_layer
# What-if: what if we only encoded the planning layer?
# L25 is the dominant planning layer in the 2.5M CLT (best features at L25).
# Sailor/shout prompt variant; single candidate "can" (P=0.425 on this prompt).
_model = "Gemma_2_2B"
_prompt = PROMPT_OUT_SHOUT
_from_group = "out"
_to_group = "an"
_candidates = ["L25:82839"]
_layers = [25]
# L25:82839 MEASURED on -out/shout prompt (outputs/2.5M/suppress_inject_sweep.json)
_probs = {"L25:82839": 0.425}

# State
initial_state_scenario_10 = h_create_base_intervention_state('scenario_10_2_5m_planning_layer')
initial_state_scenario_10.model_name = _model
initial_state_scenario_10.prompt_text = _prompt
initial_state_scenario_10.from_group = _from_group
initial_state_scenario_10.to_group = _to_group
initial_state_scenario_10.candidate_features = _candidates
initial_state_scenario_10.layers_to_encode = _layers
initial_state_scenario_10.candidate_probabilities = _probs

# Problem
problems['scenario_10_2_5m_planning_layer'] = (
    initial_state_scenario_10,
    [('m_redirect_rhyme', _model, _prompt)],
    f'2.5M planning layer only ({_from_group} -> {_to_group}, {len(_layers)} layer, no backtracking) -> 9 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_11_2_5m_different_group
# What-if: what if we redirected a different group pair?
# Suppress -oo (instead of -out), inject "can" on the -oo/who prompt
# P("can") = 0.400 on this prompt. Threshold lowered to 0.35.
# "plan" tried first (estimated P=0.001) -> FAILS, "can" (P=0.400) -> SUCCEEDS
_model = "Gemma_2_2B"
_prompt = PROMPT_OO_WHO
_from_group = "oo"
_to_group = "an"
_candidates = ["L25:71041", "L25:82839"]
_layers = [16, 25]
_probs = {"L25:82839": 0.400, "L25:71041": 0.001}

# State
initial_state_scenario_11 = h_create_base_intervention_state('scenario_11_2_5m_different_group')
initial_state_scenario_11.model_name = _model
initial_state_scenario_11.prompt_text = _prompt
initial_state_scenario_11.from_group = _from_group
initial_state_scenario_11.to_group = _to_group
initial_state_scenario_11.candidate_features = _candidates
initial_state_scenario_11.layers_to_encode = _layers
initial_state_scenario_11.probability_threshold = 0.35
initial_state_scenario_11.candidate_probabilities = _probs

# Problem
problems['scenario_11_2_5m_different_group'] = (
    initial_state_scenario_11,
    [('m_redirect_rhyme', _model, _prompt)],
    f'2.5M different group ({_from_group} -> {_to_group}, {len(_layers)} layers, backtracking) -> 10 actions'
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
    12

    --- Gemma 2 2B scenarios (0-3) ---

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

    Greedy planner fails on Gemma backtracking scenarios (1 and 3).

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

    --- Llama 3.2 1B scenarios (4-7) ---

    Scenario 4 — Llama star result (24 actions, no backtracking).
    L14:13043 "that" at 77.7% on -ee prompt succeeds immediately.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r4 = s.find_plan(*probs['scenario_4_llama_star_result'][:2])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 24)

    Scenario 5 — Llama sat first (24 actions, backtracking).
    L14:6132 "sat" (0.01) fails, L14:13043 "that" (0.777) succeeds.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r5 = s.find_plan(*probs['scenario_5_llama_sat_first'][:2])
    >>> sys.stdout = _o
    >>> r5.success, len(r5.plan)
    (True, 24)
    >>> [a for a in r5.plan if a[0] == 'a_inject_feature'][0][1]
    'L14:13043'

    Scenario 6 — Llama output layer only (9 actions, no backtracking).
    Same as scenario 4 but encoding only L15 (where 82% of features live).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r6 = s.find_plan(*probs['scenario_6_llama_output_layer'][:2])
    >>> sys.stdout = _o
    >>> r6.success, len(r6.plan)
    (True, 9)

    Scenario 7 — Llama different group (10 actions, at -> ore, backtracking).
    L3:22663 "or" (0.001) and L10:18203 "more" (0.002) fail threshold 0.005,
    L1:5297 "for" (0.009) succeeds.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r7 = s.find_plan(*probs['scenario_7_llama_different_group'][:2])
    >>> sys.stdout = _o
    >>> r7.success, len(r7.plan)
    (True, 10)
    >>> [a for a in r7.plan if a[0] == 'a_inject_feature'][0][1]
    'L1:5297'

    Greedy planner fails on Llama backtracking scenarios (5 and 7).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g5 = s.find_plan(*probs['scenario_5_llama_sat_first'][:2])
    >>> sys.stdout = _o
    >>> g5.success
    False

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g7 = s.find_plan(*probs['scenario_7_llama_different_group'][:2])
    >>> sys.stdout = _o
    >>> g7.success
    False

    --- Gemma 2 2B + CLT 2.5M scenarios (8-11) ---

    Scenario 8 — 2.5M star result (34 actions, no backtracking).
    L25:82839 "can" at 48.20% succeeds on first try (threshold 0.40).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r8 = s.find_plan(*probs['scenario_8_version_d_2_5m_star'][:2])
    >>> sys.stdout = _o
    >>> r8.success, len(r8.plan)
    (True, 34)

    Scenario 9 — 2.5M weakest first (34 actions, backtracking).
    L25:71041 "plan" (0.001) and L25:45672 "man" (0.002) fail, L25:82839 "can" (0.482) succeeds.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r9 = s.find_plan(*probs['scenario_9_2_5m_weakest_first'][:2])
    >>> sys.stdout = _o
    >>> r9.success, len(r9.plan)
    (True, 34)
    >>> [a for a in r9.plan if a[0] == 'a_inject_feature'][0][1]
    'L25:82839'

    Scenario 10 — 2.5M planning layer only (9 actions, no backtracking).
    Same as scenario 8 but encoding only L25 (sailor/shout prompt, P=0.425).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r10 = s.find_plan(*probs['scenario_10_2_5m_planning_layer'][:2])
    >>> sys.stdout = _o
    >>> r10.success, len(r10.plan)
    (True, 9)

    Scenario 11 — 2.5M different group (10 actions, oo -> an, backtracking).
    L25:71041 "plan" (0.001) fails threshold 0.35, L25:82839 "can" (0.400) succeeds.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r11 = s.find_plan(*probs['scenario_11_2_5m_different_group'][:2])
    >>> sys.stdout = _o
    >>> r11.success, len(r11.plan)
    (True, 10)
    >>> [a for a in r11.plan if a[0] == 'a_inject_feature'][0][1]
    'L25:82839'

    Greedy planner fails on 2.5M backtracking scenarios (9 and 11).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g9 = s.find_plan(*probs['scenario_9_2_5m_weakest_first'][:2])
    >>> sys.stdout = _o
    >>> g9.success
    False

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g11 = s.find_plan(*probs['scenario_11_2_5m_different_group'][:2])
    >>> sys.stdout = _o
    >>> g11.success
    False

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
