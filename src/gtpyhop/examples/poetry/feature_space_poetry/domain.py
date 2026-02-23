# ============================================================================
# Feature Space Poetry HTN Domain
# HTN Operates in Feature Space (The Wild One)
# ============================================================================
#
# MOTIVATION:
# The melometis v1.3.0 Version D experiments proved that suppress+inject
# at the CLT feature level can redirect a model's rhyme plan. The "around"
# feature (L22:10243) achieved 48.3% redirect probability -- a 155-million-
# fold spike at the planning site. This domain automates that protocol:
# the HTN's state space IS the CLT activation space, actions are feature-
# level operations, and the "world" is the residual stream.
#
# ARCHITECTURE (Architecture 6 from htn-roles-for-planning-in-poems.md):
#   HTN Planner (GTPyhop)     ->  plans interventions on internal representations
#   Inference Server (MCP)    ->  forward passes, probability measurement
#   CLT Server (MCP)          ->  encode/decode features, inject decoder vectors
#
# THE SUPPRESS+INJECT PROTOCOL (modeled as HTN decomposition):
#   m_redirect_rhyme(from_group, to_group)
#     -> a_initialize_intervention         // setup model, tracking
#     -> a_locate_planning_site            // find the newline token
#     -> a_measure_baseline                // P(from_group) before intervention
#     -> m_encode_all_layers               // CLT encode at each layer
#     -> a_suppress_group(from_group)      // zero out from_group features
#     -> m_find_best_injection(to_group)   // backtracking search over candidates
#     -> a_compile_intervention_report     // assemble results
#
# BACKTRACKING:
#   m_find_best_injection has 3 alternative methods (try_1, try_2, try_3),
#   each trying a different ranked candidate feature. a_evaluate_threshold
#   returns False when the candidate is below the success threshold, causing
#   GTPyhop to backtrack and try the next candidate. This mirrors the manual
#   experimental search in melometis Version D.
#
# PLAN LENGTH FORMULA:
#   L + 8  [init + locate + baseline + (encode x L layers) + suppress +
#           inject + measure + evaluate + report]
#   1 layer:   1 + 8 =  9 actions
#   2 layers:  2 + 8 = 10 actions
#   26 layers: 26 + 8 = 34 actions
#
# SCIENTIFIC VALUE:
#   "The HTN doesn't plan text; it plans interventions on the model's
#   internal representations. The plan itself is a scientific artifact."
#   This is mechanistic interpretability formalized as classical planning.
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - Constants (known models, rhyme groups, feature candidates)
#   - State Property Map (Feature Space Intervention Workflow)
#   - Actions (9)
#   - Methods (5)
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple, Dict

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    # Graceful degradation: supports direct domain.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("feature_space_poetry")
set_current_domain(the_domain)

# ============================================================================
# CONSTANTS -- Model, Rhyme Group, and Feature Specifications
# ============================================================================

# Known transformer models with CLT support
KNOWN_MODELS = {
    "Gemma_2_2B": {
        "num_layers": 26,
        "clt_resolution": "426K",
        "planning_features_identified": True,
    },
    "Llama_3_2_1B": {
        "num_layers": 16,
        "clt_resolution": "524K",
        "planning_features_identified": True,
    },
}

# Experimentally validated rhyme groups from melometis suppress+inject experiments.
# Gemma 2 2B groups (Version D): 4 natural groups on the 4 Version D prompts.
# Gemma 2 2B + CLT 2.5M (Version D 2.5M): 1 word-level injection target group.
# Llama 3.2 1B groups (Version L): 4 groups from corpus/prompts_llama.json.
RHYME_GROUPS = {
    # --- Gemma 2 2B (Version D) ---
    "out": {
        "arpabet": "AW1-T",
        "words": ["about", "out", "shout"],
        "model": "Gemma_2_2B",
        "description": "Primary suppression target on 2 of 4 Version D prompts",
    },
    "ound": {
        "arpabet": "AW1-N-D",
        "words": ["around", "found", "ground", "round"],
        "model": "Gemma_2_2B",
        "description": "Target for cross-group injection; L22:10243 achieved 48.3% redirect",
    },
    "ow": {
        "arpabet": "OW1",
        "words": ["go", "grow", "know", "slow", "snow", "so", "though"],
        "model": "Gemma_2_2B",
        "description": "Natural group on 1 Version D prompt; 7 words with CLT features",
    },
    "oo": {
        "arpabet": "UW1",
        "words": ["do", "new", "ou", "to", "too", "two", "who"],
        "model": "Gemma_2_2B",
        "description": "Natural group on 1 Version D prompt; L25:ou achieved 157,000x ratio",
    },
    # --- Gemma 2 2B + CLT 2.5M (Version D 2.5M) ---
    "an": {
        "arpabet": "AE1-N",
        "words": ["can", "man", "plan"],
        "model": "Gemma_2_2B",
        "description": "Word-level injection target (2.5M CLT); L25:82839 'can' achieved 48.2% redirect",
    },
    # --- Llama 3.2 1B (Version L) ---
    "ee": {
        "arpabet": "IY1",
        "words": ["he", "be", "ne", "we"],
        "model": "Llama_3_2_1B",
        "description": "Natural group on -ee prompt; 4 words, 82% features at L15",
    },
    "at": {
        "arpabet": "AE1-T",
        "words": ["that", "sat"],
        "model": "Llama_3_2_1B",
        "description": "Injection target; L14:13043 'that' achieved 77.7% redirect",
    },
    "ore": {
        "arpabet": "AO1-R",
        "words": ["for", "or", "more"],
        "model": "Llama_3_2_1B",
        "description": "Injection target on -at prompt; L1:5297 'for' at 0.9%",
    },
}

# Ranked injection candidates per target group (strongest first).
# Feature IDs from CLT 426K or 2.5M resolution on Gemma 2 2B, CLT 524K on Llama 3.2 1B.
# Each candidate is a dict: feature_id, layer, top_token, planning_site_ratio, max_probability.
FEATURE_CANDIDATES = {
    "ound": [
        # MEASURED: 48.29% on -out/about, 33.86% on -out/shout, 5.67% on -oo/who
        {"feature_id": "L22:10243", "layer": 22, "top_token": "around",
         "planning_site_ratio": "155M x", "max_probability": 0.48286605,
         "source": "measured_version_d"},
        # ESTIMATED from CLT decoder vector analysis (not tested in Version D sweep)
        {"feature_id": "L16:7712", "layer": 16, "top_token": "ground",
         "planning_site_ratio": "~29M x", "max_probability": 0.003,
         "source": "estimated_clt"},
        {"feature_id": "L25:3298", "layer": 25, "top_token": "round",
         "planning_site_ratio": "~600 x", "max_probability": 0.001,
         "source": "estimated_clt"},
    ],
    "out": [
        # MEASURED: 2.74e-6 on -ow/so prompt (suppress_inject_sweep.json)
        {"feature_id": "L16:13725", "layer": 16, "top_token": "about",
         "planning_site_ratio": "160,379 x", "max_probability": 0.00000274,
         "source": "measured_version_d"},
        {"feature_id": "L25:out_a", "layer": 25, "top_token": "out",
         "planning_site_ratio": "2,200 x", "max_probability": 0.001,
         "source": "estimated_clt"},
        {"feature_id": "L25:out_b", "layer": 25, "top_token": "shout",
         "planning_site_ratio": "10,900 x", "max_probability": 0.005,
         "source": "estimated_clt"},
    ],
    "ow": [
        {"feature_id": "L25:go", "layer": 25, "top_token": "go",
         "planning_site_ratio": "610 x", "max_probability": 0.001,
         "source": "estimated_clt"},
        {"feature_id": "L22:know", "layer": 22, "top_token": "know",
         "planning_site_ratio": "774 x", "max_probability": 0.002,
         "source": "estimated_clt"},
        {"feature_id": "L20:though", "layer": 20, "top_token": "though",
         "planning_site_ratio": "57 x", "max_probability": 0.0005,
         "source": "estimated_clt"},
    ],
    "oo": [
        {"feature_id": "L25:ou", "layer": 25, "top_token": "ou",
         "planning_site_ratio": "157,000 x", "max_probability": 0.01,
         "source": "estimated_clt"},
        {"feature_id": "L23:new", "layer": 23, "top_token": "new",
         "planning_site_ratio": "719 x", "max_probability": 0.002,
         "source": "estimated_clt"},
        {"feature_id": "L19:two", "layer": 19, "top_token": "two",
         "planning_site_ratio": "1,285 x", "max_probability": 0.003,
         "source": "estimated_clt"},
    ],
    # --- Gemma 2 2B + CLT 2.5M (Version D 2.5M) ---
    "an": [
        # MEASURED: 48.20% on -out/about, 42.49% on -out/shout, 40.02% on -oo/who
        {"feature_id": "L25:82839", "layer": 25, "top_token": "can",
         "planning_site_ratio": "160B x", "max_probability": 0.48201,
         "source": "measured_version_d_2_5m"},
        # ESTIMATED from 2.5M CLT decoder vector analysis (not tested in sweep)
        {"feature_id": "L25:45672", "layer": 25, "top_token": "man",
         "planning_site_ratio": "~500 x", "max_probability": 0.002,
         "source": "estimated_clt_2_5m"},
        {"feature_id": "L25:71041", "layer": 25, "top_token": "plan",
         "planning_site_ratio": "~200 x", "max_probability": 0.001,
         "source": "estimated_clt_2_5m"},
    ],
    # --- Llama 3.2 1B (Version L) ---
    "at": [
        # MEASURED: 77.7% on -ee prompt, 45.2% on -oo prompt
        {"feature_id": "L14:13043", "layer": 14, "top_token": "that",
         "planning_site_ratio": "133,879 x", "max_probability": 0.777,
         "source": "measured_version_l"},
        # ESTIMATED from CLT decoder analysis (cosine 0.32, not tested in sweep)
        {"feature_id": "L14:6132", "layer": 14, "top_token": "sat",
         "planning_site_ratio": "~1,700 x", "max_probability": 0.01,
         "source": "estimated_clt"},
    ],
    "ore": [
        # MEASURED: 0.9% on -at prompt (suppress_inject_sweep_llama_v2.json)
        {"feature_id": "L1:5297", "layer": 1, "top_token": "for",
         "planning_site_ratio": "2,447 x", "max_probability": 0.009,
         "source": "measured_version_l"},
        # ESTIMATED from CLT decoder analysis
        {"feature_id": "L3:22663", "layer": 3, "top_token": "or",
         "planning_site_ratio": "~200 x", "max_probability": 0.001,
         "source": "estimated_clt"},
        {"feature_id": "L10:18203", "layer": 10, "top_token": "more",
         "planning_site_ratio": "~400 x", "max_probability": 0.002,
         "source": "estimated_clt"},
    ],
}

# Default parameters from Version D protocol
DEFAULT_INJECTION_STRENGTH = 1.0
DEFAULT_PROBABILITY_THRESHOLD = 0.40

# ============================================================================
# STATE PROPERTY MAP (Feature Space Intervention Workflow)
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Server 1: inference_server (Forward Passes & Probability Measurement)
# Server 2: clt_server (CLT Encode/Decode & Feature Injection)
#
# --- INITIALIZATION ---
# a_initialize_intervention
#  (P) model_name: str [DATA] - transformer model to analyze
#  (P) prompt_text: str [DATA] - poetry prompt for intervention
#  (P) from_group: str [DATA] - rhyme group to suppress
#  (P) to_group: str [DATA] - rhyme group to inject
#  (P) candidate_features: List[str] [DATA] - ranked feature IDs for injection
#  (P) layers_to_encode: List[int] [DATA] - which layers to CLT-encode
#  (P) injection_strength: float [DATA] - strength multiplier for injection
#  (P) probability_threshold: float [DATA] - P(target) threshold for success
#  (P) candidate_probabilities: Dict[str, float] [DATA] - per-candidate measured/estimated P(target)
#  (E) model_spec: Dict [DATA] - model specification from KNOWN_MODELS
#  (E) active_features: Dict [DATA] - per-layer feature activations (initially empty)
#  (E) residual_stream: str [DATA] - current residual at planning site
#  (E) target_distribution: Dict [DATA] - P(word) for target group (initially empty)
#  (E) injection_history: List [DATA] - injection log (initially empty)
#  (E) suppressed_features: Dict [DATA] - zeroed features (initially empty)
#  (E) num_layers_encoded: int [DATA] - count of encoded layers
#  (E) num_candidates_tried: int [DATA] - count of injection attempts
#  (E) intervention_initialized: True [ENABLER]
#
# --- INFERENCE SERVER ACTIONS (Server 1) ---
# a_locate_planning_site
#  (P) intervention_initialized == True [ENABLER]
#  (E) planning_site_position: str [DATA] - token position of planning site
#  (E) residual_stream: str [DATA] - residual stream extracted at planning site
#  (E) planning_site_located: True [ENABLER]
#
# a_measure_baseline
#  (P) planning_site_located == True [ENABLER]
#  (E) baseline_probability: str [DATA] - P(from_group) without intervention
#  (E) baseline_measured: True [ENABLER]
#
# a_measure_effect
#  (P) injection_complete == True [ENABLER]
#  (E) target_distribution: str [DATA] - P(to_group) after intervention
#  (E) measured_probability: float [DATA] - simulated P(target) from candidate_probabilities
#  (E) effect_measured: True [ENABLER]
#
# --- CLT SERVER ACTIONS (Server 2) ---
# a_encode_residual
#  (P) planning_site_located == True [ENABLER]
#  (P) layer in layers_to_encode
#  (E) active_features[layer]: str [DATA] - feature activations at this layer
#  (E) num_layers_encoded: int [DATA] - count incremented
#  (E) encoding_complete: True [ENABLER] (when all layers encoded)
#
# a_inject_feature
#  (P) suppression_complete == True [ENABLER]
#  (P) feature_id in candidate_features
#  (E) residual_stream: str [DATA] - updated with decoder vector
#  (E) injection_history: List [DATA] - feature+strength appended
#  (E) num_candidates_tried: int [DATA] - count incremented
#  (E) injection_complete: True [ENABLER]
#
# --- LOCAL COMPUTATION ---
# a_suppress_group
#  (P) encoding_complete == True [ENABLER]
#  (P) group_name == state.from_group
#  (E) suppressed_features: Dict [DATA] - features zeroed per layer
#  (E) residual_stream: str [DATA] - reconstructed after suppression
#  (E) suppression_complete: True [ENABLER]
#
# a_evaluate_threshold
#  (P) effect_measured == True [ENABLER]
#  (P) measured_probability >= probability_threshold (BACKTRACKING TRIGGER)
#  (E) threshold_met: True [ENABLER]
#
# --- REPORT ---
# a_compile_intervention_report
#  (P) threshold_met == True [ENABLER]
#  (E) intervention_report: Dict [DATA] - complete intervention record
#  (E) intervention_complete: True [ENABLER]
# ============================================================================


# ============================================================================
# ACTIONS (9)
# ============================================================================

def a_initialize_intervention(state: State, model_name: str, prompt_text: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:initialize_intervention

    Action signature:
        a_initialize_intervention(state, model_name, prompt_text)

    Action parameters:
        model_name: Transformer model identifier (e.g., 'Gemma_2_2B')
        prompt_text: Poetry prompt for feature-space intervention

    Action purpose:
        Initialize the feature-space intervention with model specification,
        prompt, and empty tracking structures for the suppress+inject protocol

    Preconditions:
        - model_name must be a known model with CLT support
        - from_group, to_group must be pre-configured and valid
        - candidate_features, layers_to_encode must be pre-configured

    Effects:
        - Model specification loaded (state.model_spec) [DATA]
        - Activation space initialized (state.active_features, etc.) [DATA]
        - Tracking counters reset (state.num_layers_encoded, etc.) [DATA]
        - Intervention initialized flag set (state.intervention_initialized) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model_name, str): return False
    if not isinstance(prompt_text, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model_name.strip(): return False
    if not prompt_text.strip(): return False
    if model_name not in KNOWN_MODELS: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # from_group and to_group must be pre-configured and valid
    if not (hasattr(state, 'from_group') and isinstance(state.from_group, str)):
        return False
    if not (hasattr(state, 'to_group') and isinstance(state.to_group, str)):
        return False
    if state.from_group not in RHYME_GROUPS: return False
    if state.to_group not in RHYME_GROUPS: return False
    if state.from_group == state.to_group: return False
    # candidate_features must be pre-configured
    if not (hasattr(state, 'candidate_features') and isinstance(state.candidate_features, list)):
        return False
    if len(state.candidate_features) == 0: return False
    # layers_to_encode must be pre-configured
    if not (hasattr(state, 'layers_to_encode') and isinstance(state.layers_to_encode, list)):
        return False
    if len(state.layers_to_encode) == 0: return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Model and prompt configuration
    state.model_name = model_name
    state.prompt_text = prompt_text
    state.model_spec = KNOWN_MODELS[model_name]

    # [DATA] Activation space (the "world" -- initially empty)
    state.active_features = {}
    state.residual_stream = "uninitialized"
    state.target_distribution = {}
    state.injection_history = []
    state.suppressed_features = {}

    # [DATA] Tracking counters
    state.num_layers_encoded = 0
    state.num_candidates_tried = 0

    # [DATA] Workflow flags (initially False)
    state.planning_site_located = False
    state.baseline_measured = False
    state.encoding_complete = False
    state.suppression_complete = False
    state.injection_complete = False
    state.effect_measured = False
    state.threshold_met = False
    state.intervention_complete = False

    # [ENABLER] Gates all subsequent actions
    state.intervention_initialized = True
    # END: Effects

    return state


def a_locate_planning_site(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: inference_server:locate_planning_site

    Action signature:
        a_locate_planning_site(state)

    Action parameters:
        None

    Action purpose:
        Identify the planning site token position and extract the residual
        stream at that position. The planning site is the newline token
        between lines 3 and 4, where the residual stream encodes the rhyme
        decision. The extracted residual becomes the "world" for all
        subsequent feature-level operations.

    Preconditions:
        - Intervention must be initialized (state.intervention_initialized)

    Effects:
        - Planning site position recorded (state.planning_site_position) [DATA]
        - Residual stream extracted at planning site (state.residual_stream) [DATA]
        - Planning site located flag set (state.planning_site_located) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'intervention_initialized') and state.intervention_initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Planning site position (populated by inference server at runtime)
    state.planning_site_position = (
        f"${{locate_planning_site:model={state.model_name},"
        f"prompt={state.prompt_text}}}"
    )

    # [DATA] Residual stream extracted at the planning site
    # This is the "world" for all feature-level operations
    state.residual_stream = (
        f"${{extract_residual:model={state.model_name},"
        f"prompt={state.prompt_text},"
        f"position={state.planning_site_position}}}"
    )

    # [ENABLER] Gates baseline measurement, encoding, and all experiments
    state.planning_site_located = True
    # END: Effects

    return state


def a_measure_baseline(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: inference_server:measure_group_probability

    Action signature:
        a_measure_baseline(state)

    Action parameters:
        None

    Action purpose:
        Measure the baseline probability of the natural rhyme group (from_group)
        at the planning site with no intervention. This establishes the
        reference point. The melometis results showed ~78% baseline rhyme
        rate with priming context.

    Preconditions:
        - Planning site must be located (state.planning_site_located)

    Effects:
        - Baseline probability recorded (state.baseline_probability) [DATA]
        - Baseline measured flag set (state.baseline_measured) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'planning_site_located') and state.planning_site_located):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Baseline probability (populated by inference server at runtime)
    state.baseline_probability = (
        f"${{measure_group_probability:model={state.model_name},"
        f"residual={state.residual_stream},"
        f"group={state.from_group}}}"
    )

    # [ENABLER] Gates encoding and all subsequent steps
    state.baseline_measured = True
    # END: Effects

    return state


def a_encode_residual(state: State, layer: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: clt_server:encode_residual

    Action signature:
        a_encode_residual(state, layer)

    Action parameters:
        layer: Layer index to encode (0-25 for Gemma 2 2B)

    Action purpose:
        Run the CLT sparse autoencoder encoder at one layer, populating
        active_features[layer] with the feature activations. Each layer
        is encoded as a separate plan action, making the plan a faithful
        record of the per-layer encoding cost.

    Preconditions:
        - Planning site must be located (state.planning_site_located)
        - layer must be in layers_to_encode
        - layer must not already be encoded

    Effects:
        - Feature activations recorded (state.active_features[layer]) [DATA]
        - Encoding count incremented (state.num_layers_encoded) [DATA]
        - Encoding complete flag set when all layers done (state.encoding_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(layer, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if layer < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'planning_site_located') and state.planning_site_located):
        return False
    if layer not in state.layers_to_encode:
        return False
    if layer in state.active_features:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Feature activations at this layer (populated by CLT server at runtime)
    state.active_features[layer] = (
        f"${{clt_encode:model={state.model_name},"
        f"residual={state.residual_stream},"
        f"layer={layer}}}"
    )

    # [DATA] Track encoding progress
    state.num_layers_encoded = state.num_layers_encoded + 1

    # [ENABLER] Gates suppression when all layers are encoded
    if state.num_layers_encoded == len(state.layers_to_encode):
        state.encoding_complete = True
    # END: Effects

    return state


def a_suppress_group(state: State, group_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: clt_server:suppress_group

    Action signature:
        a_suppress_group(state, group_name)

    Action parameters:
        group_name: Rhyme group to suppress (e.g., 'out', 'ow')

    Action purpose:
        Zero out all CLT features belonging to the specified rhyme group
        across all encoded layers, then reconstruct the residual stream
        from the modified activations. This is the "suppress" half of the
        suppress+inject protocol from Version D.

    Preconditions:
        - All layers must be encoded (state.encoding_complete)
        - group_name must match from_group
        - group_name must be a valid rhyme group

    Effects:
        - Features zeroed per layer recorded (state.suppressed_features) [DATA]
        - Residual stream reconstructed (state.residual_stream) [DATA]
        - Suppression complete flag set (state.suppression_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(group_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not group_name.strip(): return False
    if group_name not in RHYME_GROUPS: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'encoding_complete') and state.encoding_complete):
        return False
    if group_name != state.from_group:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Record which features were suppressed at each layer
    state.suppressed_features = (
        f"${{suppress_group_features:model={state.model_name},"
        f"group={group_name},"
        f"active_features={list(state.active_features.keys())}}}"
    )

    # [DATA] Reconstruct residual stream from modified activations
    state.residual_stream = (
        f"${{reconstruct_residual:model={state.model_name},"
        f"active_features={list(state.active_features.keys())},"
        f"suppressed_group={group_name}}}"
    )

    # [ENABLER] Gates injection
    state.suppression_complete = True
    # END: Effects

    return state


def a_inject_feature(state: State, feature_id: str, strength: float) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: clt_server:inject_feature

    Action signature:
        a_inject_feature(state, feature_id, strength)

    Action parameters:
        feature_id: CLT feature ID to inject (e.g., 'L22:10243')
        strength: Injection strength multiplier (typically 1.0)

    Action purpose:
        Add a decoder vector to the residual stream. This is the "inject"
        half of the suppress+inject protocol. The decoder vector for the
        specified feature is scaled by strength and added to the residual
        stream, steering the model toward the target rhyme group.

    Preconditions:
        - Suppression must be complete (state.suppression_complete)
        - feature_id must be in the scenario's candidate_features list

    Effects:
        - Residual stream updated with decoder vector (state.residual_stream) [DATA]
        - Injection logged (state.injection_history) [DATA]
        - Candidates tried count incremented (state.num_candidates_tried) [DATA]
        - Injection complete flag set (state.injection_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(feature_id, str): return False
    if not isinstance(strength, (int, float)): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not feature_id.strip(): return False
    if strength <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'suppression_complete') and state.suppression_complete):
        return False
    if feature_id not in state.candidate_features:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Add decoder vector to residual stream (populated by CLT server at runtime)
    state.residual_stream = (
        f"${{inject_decoder_vector:model={state.model_name},"
        f"residual={state.residual_stream},"
        f"feature_id={feature_id},"
        f"strength={strength}}}"
    )

    # [DATA] Log the injection
    state.injection_history = state.injection_history + [(feature_id, strength)]

    # [DATA] Track injection attempts
    state.num_candidates_tried = state.num_candidates_tried + 1

    # [ENABLER] Gates effect measurement
    state.injection_complete = True
    # END: Effects

    return state


def a_measure_effect(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: inference_server:measure_group_probability

    Action signature:
        a_measure_effect(state)

    Action parameters:
        None

    Action purpose:
        Run a forward pass from the modified residual stream and measure
        P(to_group) at the planning site. This determines whether the
        suppress+inject intervention successfully redirected the model's
        rhyme plan toward the target group.

    Preconditions:
        - Injection must be complete (state.injection_complete)

    Effects:
        - Target distribution recorded (state.target_distribution) [DATA]
        - Measured probability recorded (state.measured_probability) [DATA]
        - Effect measured flag set (state.effect_measured) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'injection_complete') and state.injection_complete):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Target distribution (populated by inference server at runtime)
    state.target_distribution = (
        f"${{measure_group_probability:model={state.model_name},"
        f"residual={state.residual_stream},"
        f"group={state.to_group}}}"
    )

    # [DATA] Simulated measurement: look up the injected candidate's known
    # probability from the per-scenario candidate_probabilities map.
    # Values come from Version D experiments (measured) or CLT analysis (estimated).
    last_feature = state.injection_history[-1][0]
    state.measured_probability = state.candidate_probabilities.get(last_feature, 0.0)

    # [ENABLER] Gates threshold evaluation
    state.effect_measured = True
    # END: Effects

    return state


def a_evaluate_threshold(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:evaluate_threshold

    Action signature:
        a_evaluate_threshold(state)

    Action parameters:
        None (reads measured_probability and probability_threshold from state)

    Action purpose:
        Evaluate whether the injection achieved sufficient P(to_group).
        This is the BACKTRACKING TRIGGER: returns False when the measured
        probability (set by a_measure_effect from the candidate's known
        experimental/estimated value) is below the scenario's probability
        threshold. When this action fails, GTPyhop backtracks the
        m_find_best_injection_try_N decomposition and tries the next
        candidate method.

    Preconditions:
        - Effect must be measured (state.effect_measured)
        - Measured probability must meet or exceed threshold
          (BACKTRACKING TRIGGER: fails otherwise)

    Effects:
        - Threshold met flag set (state.threshold_met) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'effect_measured') and state.effect_measured):
        return False

    # BACKTRACKING TRIGGER: measured probability must meet or exceed the
    # scenario's threshold. Probabilities come from Version D experiments
    # (measured) or CLT analysis (estimated), stored in state by a_measure_effect.
    if state.measured_probability < state.probability_threshold:
        return False  # Insufficient redirect -- triggers backtracking
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Gates report compilation
    state.threshold_met = True
    # END: Effects

    return state


def a_compile_intervention_report(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:compile_report

    Action signature:
        a_compile_intervention_report(state)

    Action parameters:
        None

    Action purpose:
        Assemble the complete intervention report documenting the
        suppress+inject protocol: which features were suppressed, which
        feature was injected, the baseline and post-intervention probabilities,
        and the full injection history. The report is a scientific artifact
        recording the automated feature-level intervention.

    Preconditions:
        - Threshold must be met (state.threshold_met)

    Effects:
        - Intervention report assembled (state.intervention_report) [DATA]
        - Intervention complete flag set (state.intervention_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'threshold_met') and state.threshold_met):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Complete intervention report
    state.intervention_report = {
        "model_name": state.model_name,
        "prompt_text": state.prompt_text,
        "from_group": state.from_group,
        "to_group": state.to_group,
        "planning_site_position": state.planning_site_position,
        "baseline_probability": state.baseline_probability,
        "layers_encoded": list(state.active_features.keys()),
        "suppressed_features": state.suppressed_features,
        "injection_history": state.injection_history,
        "target_distribution": state.target_distribution,
        "num_candidates_tried": state.num_candidates_tried,
    }

    # [ENABLER] Workflow complete
    state.intervention_complete = True
    # END: Effects

    return state


# ============================================================================
# METHODS (5)
# ============================================================================

# ============================================================================
# TOP-LEVEL ENTRY POINT
# ============================================================================

def m_redirect_rhyme(state: State, model_name: str, prompt_text: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_redirect_rhyme(state, model_name, prompt_text)

    Method parameters:
        model_name: Transformer model to analyze (e.g., 'Gemma_2_2B')
        prompt_text: Poetry prompt for feature-space intervention

    Method purpose:
        Top-level entry point for the suppress+inject protocol. Initializes
        the intervention, locates the planning site, measures baseline,
        encodes all layers, suppresses the natural rhyme group, finds the
        best injection candidate (with backtracking), and compiles a report.

    Preconditions:
        - model_name must be a known model
        - from_group, to_group, candidate_features, layers_to_encode must
          be pre-configured on state

    Task decomposition:
        - a_initialize_intervention: Setup model, tracking structures
        - a_locate_planning_site: Find planning site, extract residual
        - a_measure_baseline: Measure P(from_group) before intervention
        - m_encode_all_layers: CLT encode at each configured layer
        - a_suppress_group: Zero out from_group features
        - m_find_best_injection: Search for best injection candidate
        - a_compile_intervention_report: Assemble intervention report

    Returns:
        Task decomposition if successful, False otherwise

    Hierarchical Decomposition:
        m_redirect_rhyme
        +-- a_initialize_intervention
        +-- a_locate_planning_site              [inference_server]
        +-- a_measure_baseline                  [inference_server]
        +-- m_encode_all_layers
        |   +-- a_encode_residual(layer_0)      [clt_server]
        |   +-- a_encode_residual(layer_1)      [clt_server]
        |   +-- ...
        +-- a_suppress_group(from_group)        [clt_server]
        +-- m_find_best_injection(to_group)
        |   +-- [backtracking: try_1 / try_2 / try_3]
        |       +-- a_inject_feature(...)       [clt_server]
        |       +-- a_measure_effect()          [inference_server]
        |       +-- a_evaluate_threshold(idx)
        +-- a_compile_intervention_report
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model_name, str): return False
    if not isinstance(prompt_text, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if model_name not in KNOWN_MODELS: return False
    if not prompt_text.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'from_group') and isinstance(state.from_group, str)):
        return False
    if not (hasattr(state, 'to_group') and isinstance(state.to_group, str)):
        return False
    if not (hasattr(state, 'candidate_features') and isinstance(state.candidate_features, list)):
        return False
    if not (hasattr(state, 'layers_to_encode') and isinstance(state.layers_to_encode, list)):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_intervention", model_name, prompt_text),
        ("a_locate_planning_site",),
        ("a_measure_baseline",),
        ("m_encode_all_layers",),
        ("a_suppress_group", state.from_group),
        ("m_find_best_injection", state.to_group),
        ("a_compile_intervention_report",),
    ]
    # END: Task Decomposition


def m_encode_all_layers(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_encode_all_layers(state)

    Method parameters:
        None (reads state.layers_to_encode)

    Method auxiliary parameters:
        layers_to_encode: List[int] (from state.layers_to_encode)

    Method purpose:
        Encode the residual stream at all configured layers using the CLT
        sparse autoencoder. Each layer is encoded as a separate action,
        making the plan a faithful record of the per-layer encoding cost.
        Layers are processed in ascending order (0 -> 25).

    Preconditions:
        - Baseline must be measured (state.baseline_measured)

    Task decomposition:
        - a_encode_residual x L (one per layer in layers_to_encode)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if not (hasattr(state, 'layers_to_encode') and isinstance(state.layers_to_encode, list)):
        return False
    layers_to_encode = state.layers_to_encode
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'baseline_measured') and state.baseline_measured):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Encode layers in ascending order
    ordered_layers = sorted(layers_to_encode)
    return [("a_encode_residual", layer) for layer in ordered_layers]
    # END: Task Decomposition


# ============================================================================
# INJECTION CANDIDATE SEARCH (with backtracking)
# ============================================================================
# Three alternative methods for m_find_best_injection, tried in order.
# Each method tries a different ranked candidate feature. When
# a_evaluate_threshold returns False (measured_probability < probability_threshold),
# GTPyhop backtracks and tries the next method.
#
# PROBABILITY-BASED BACKTRACKING:
#   a_measure_effect looks up the injected candidate's known probability
#   from state.candidate_probabilities (populated per-scenario from Version D
#   experiments where measured, CLT analysis where estimated). Then
#   a_evaluate_threshold compares state.measured_probability against
#   state.probability_threshold. This replaces the earlier index-based
#   mechanism with a genuine probability comparison.
#
# STATE RESTORATION ON BACKTRACK:
#   GTPyhop performs full state copy before each method attempt. When
#   a_evaluate_threshold returns False, the planner restores the state
#   snapshot taken before the failed method's decomposition began. This
#   means:
#
#   - state.residual_stream reverts to the post-suppression value
#     (the injected decoder vector from the failed attempt is undone)
#   - state.injection_history reverts to [] (the failed injection is removed)
#   - state.injection_complete, state.effect_measured revert to False
#   - state.measured_probability reverts to 0.0
#   - state.num_candidates_tried reverts to 0
#
#   The final plan contains ONLY the successful path's actions. The
#   intervention_report therefore records only the injection that succeeded,
#   with num_candidates_tried reflecting only the successful execution.
#
#   IMPORTANT: This domain depends on GTPyhop's copy-on-backtrack semantics.
#   Porting to a planner that does NOT deep-copy state before trying
#   alternative methods will cause silent corruption: the residual_stream
#   would retain the failed injection's decoder vector, and injection_history
#   would accumulate entries from all attempts.
# ============================================================================

def m_find_best_injection_try_1(state: State, target_group: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_find_best_injection_try_1(state, target_group)

    Method parameters:
        target_group: Rhyme group to inject toward (e.g., 'ound')

    Method purpose:
        Try the first candidate feature (index 0) for injection.
        If a_evaluate_threshold fails (measured probability below
        threshold), the planner backtracks to try_2.

    Preconditions:
        - Suppression must be complete (state.suppression_complete)
        - At least 1 candidate feature must be available
        - target_group must match to_group

    Task decomposition:
        - a_inject_feature: Inject candidate 0 with configured strength
        - a_measure_effect: Measure P(to_group) and look up simulated probability
        - a_evaluate_threshold: Compare measured_probability >= probability_threshold

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(target_group, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not target_group.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'suppression_complete') and state.suppression_complete):
        return False
    if len(state.candidate_features) < 1:
        return False
    if target_group != state.to_group:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_inject_feature", state.candidate_features[0], state.injection_strength),
        ("a_measure_effect",),
        ("a_evaluate_threshold",),
    ]
    # END: Task Decomposition


def m_find_best_injection_try_2(state: State, target_group: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_find_best_injection_try_2(state, target_group)

    Method parameters:
        target_group: Rhyme group to inject toward (e.g., 'ound')

    Method purpose:
        Try the second candidate feature (index 1) for injection.
        This is the backtracking fallback from try_1. If a_evaluate_threshold
        still fails (measured probability below threshold), the planner
        backtracks to try_3.

    Preconditions:
        - Suppression must be complete (state.suppression_complete)
        - At least 2 candidate features must be available
        - target_group must match to_group

    Task decomposition:
        - a_inject_feature: Inject candidate 1 with configured strength
        - a_measure_effect: Measure P(to_group) and look up simulated probability
        - a_evaluate_threshold: Compare measured_probability >= probability_threshold

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(target_group, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not target_group.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'suppression_complete') and state.suppression_complete):
        return False
    if len(state.candidate_features) < 2:
        return False
    if target_group != state.to_group:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_inject_feature", state.candidate_features[1], state.injection_strength),
        ("a_measure_effect",),
        ("a_evaluate_threshold",),
    ]
    # END: Task Decomposition


def m_find_best_injection_try_3(state: State, target_group: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_find_best_injection_try_3(state, target_group)

    Method parameters:
        target_group: Rhyme group to inject toward (e.g., 'ound')

    Method purpose:
        Try the third candidate feature (index 2) for injection. This is
        the final backtracking fallback. If this also fails (measured
        probability below threshold), the planner reports no plan found.

    Preconditions:
        - Suppression must be complete (state.suppression_complete)
        - At least 3 candidate features must be available
        - target_group must match to_group

    Task decomposition:
        - a_inject_feature: Inject candidate 2 with configured strength
        - a_measure_effect: Measure P(to_group) and look up simulated probability
        - a_evaluate_threshold: Compare measured_probability >= probability_threshold

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(target_group, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not target_group.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'suppression_complete') and state.suppression_complete):
        return False
    if len(state.candidate_features) < 3:
        return False
    if target_group != state.to_group:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_inject_feature", state.candidate_features[2], state.injection_strength),
        ("a_measure_effect",),
        ("a_evaluate_threshold",),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_initialize_intervention,
    a_locate_planning_site,
    a_measure_baseline,
    a_encode_residual,
    a_suppress_group,
    a_inject_feature,
    a_measure_effect,
    a_evaluate_threshold,
    a_compile_intervention_report,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Top-level entry point
declare_task_methods('m_redirect_rhyme', m_redirect_rhyme)

# Layer encoding
declare_task_methods('m_encode_all_layers', m_encode_all_layers)

# Injection candidate search (backtracking: try strongest first, fallback to weaker)
declare_task_methods('m_find_best_injection',
                     m_find_best_injection_try_1,
                     m_find_best_injection_try_2,
                     m_find_best_injection_try_3)

# ============================================================================
# END OF FILE
# ============================================================================
