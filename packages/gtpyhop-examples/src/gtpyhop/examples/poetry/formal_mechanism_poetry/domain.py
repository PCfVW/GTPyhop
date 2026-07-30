# ============================================================================
# Formal Mechanism Poetry HTN Domain
# HTN as Formal Model of the LLM's Implicit Rhyme Planning
# ============================================================================
#
# MOTIVATION:
# Anthropic's "Planning in Poems" (March 2025) and the melometis v1.3.0
# results proved that LLMs have an IMPLICIT planner for rhyme. At the
# planning site (the newline token between lines 3 and 4), the residual
# stream encodes a rhyme decision confirmed by a 155-million-fold
# probability spike. This domain does NOT steer the LLM -- it uses the
# HTN formalism to MODEL what the LLM computes internally, creating a
# testable formal correspondence between HTN task decomposition and
# neural network computation.
#
# ARCHITECTURE (Architecture 12 from htn-roles-for-planning-in-poems.md):
#   HTN Planner (GTPyhop)     ->  formal model of implicit planning stages
#   Inference Server (MCP)    ->  forward passes, probability measurement
#   CLT Server (MCP)          ->  feature knockout/injection experiments
#
# THE HYPOTHESIS (modeled as HTN decomposition):
#   m_plan_rhyme_implicit(residual_stream)
#     -> a_activate_context_features(layers 0-8)    // attend to priming rhyme
#     -> a_propagate_rhyme_expectation(layers 9-15)  // build rhyme-group repr
#     -> a_commit_to_group(layer 16)                 // planning feature fires
#     -> a_route_through_attention(layers 17-22)     // attention carries signal
#     -> a_project_to_vocabulary(layers 23-25)       // final logit computation
#
# TESTING THE HYPOTHESIS:
#   For each stage, run a knockout or injection experiment and compare
#   the observed effect on P(rhyme) to the prediction.
#
# PLAN LENGTH BY STAGE COUNT:
#   Formula: 4 + 3N  [init + locate + baseline + (formulate + experiment +
#                      evaluate) x stages + report]
#   1 stage:   4 + 3  =  7 actions
#   3 stages:  4 + 9  = 13 actions
#   5 stages:  4 + 15 = 19 actions
#
# SCIENTIFIC VALUE:
#   "We model the transformer's implicit planning process as an HTN task
#   decomposition and empirically validate the correspondence."
#   This is computational cognitive science: using HTN planning theory
#   to model neural network computation.
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - Constants (mechanism stages, known models, stage order)
#   - State Property Map (Formal Mechanism Analysis Workflow)
#   - Actions (7)
#   - Methods (4)
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
the_domain = Domain("formal_mechanism_poetry")
set_current_domain(the_domain)

# ============================================================================
# CONSTANTS -- Mechanism Stage Specifications
# ============================================================================

# Known transformer models with CLT support
KNOWN_MODELS = {
    "Gemma_2_2B": {
        "num_layers": 26,
        "clt_resolution": "426K",
        "planning_features_identified": True,
    },
}

# The 5 hypothesized stages of the LLM's implicit rhyme planning mechanism.
# Each stage maps to a layer range in the transformer and has a predicted
# effect when knocked out or injected. Each stage includes a quantitative
# threshold for evaluating experimental correspondence.
MECHANISM_STAGES = {
    "context_activation": {
        "layer_start": 0,
        "layer_end": 8,
        "function": "Attend to priming rhyme context",
        "prediction": "Knockout reduces P(rhyme) to <10% of baseline",
        "threshold": {"metric": "rhyme_probability_ratio", "direction": "below", "value": 0.10},
        "experiment_type": "knockout",
    },
    "expectation_propagation": {
        "layer_start": 9,
        "layer_end": 15,
        "function": "Build rhyme-group representation from context",
        "prediction": "Knockout weakens planning signal by >50%",
        "threshold": {"metric": "rhyme_probability_ratio", "direction": "below", "value": 0.50},
        "experiment_type": "knockout",
    },
    "group_commitment": {
        "layer_start": 16,
        "layer_end": 16,
        "function": "Planning feature fires, committing to rhyme group",
        "prediction": "Injection at L16 produces >=100x stronger planning-site effect than L22 injection",
        "threshold": {"metric": "effect_ratio_vs_L22", "direction": "above", "value": 100.0},
        "experiment_type": "injection",
    },
    "attention_routing": {
        "layer_start": 17,
        "layer_end": 22,
        "function": "Attention heads carry planning signal to output positions",
        "prediction": "Knockout disconnects planning from generation, P(rhyme) drops >60%",
        "threshold": {"metric": "rhyme_probability_ratio", "direction": "below", "value": 0.40},
        "experiment_type": "knockout",
    },
    "vocabulary_projection": {
        "layer_start": 23,
        "layer_end": 25,
        "function": "Project planning signal onto vocabulary logits",
        "prediction": "Knockout prevents rhyme group from affecting word choice, P(rhyme) drops >30%",
        "threshold": {"metric": "rhyme_probability_ratio", "direction": "below", "value": 0.70},
        "experiment_type": "knockout",
    },
}

# Canonical processing order for stages (layers 0 -> 25)
STAGE_ORDER = [
    "context_activation",
    "expectation_propagation",
    "group_commitment",
    "attention_routing",
    "vocabulary_projection",
]

# ============================================================================
# STATE PROPERTY MAP (Formal Mechanism Analysis Workflow)
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Server 1: inference_server (Forward Passes & Probability Measurement)
# Server 2: clt_server (CLT Feature Knockout/Injection Experiments)
#
# --- INITIALIZATION ---
# a_initialize_analysis
#  (P) model_name: str [DATA] - transformer model to analyze
#  (P) prompt_text: str [DATA] - poetry prompt for analysis
#  (P) stages_to_test: List[str] [DATA] - which stages to formulate and test
#  (E) model_spec: Dict [DATA] - model specification from KNOWN_MODELS
#  (E) num_stages: int [DATA] - count of stages to test
#  (E) hypothesized_stages: Dict [DATA] - initialized empty
#  (E) experiment_results: Dict [DATA] - initialized empty
#  (E) stage_evaluations: Dict [DATA] - initialized empty
#  (E) analysis_initialized: True [ENABLER]
#
# --- INFERENCE SERVER ACTIONS (Server 1) ---
# a_locate_planning_site
#  (P) analysis_initialized == True [ENABLER]
#  (E) planning_site_position: int [DATA] - token position of planning site
#  (E) planning_site_identified: True [ENABLER]
#
# a_record_baseline
#  (P) planning_site_identified == True [ENABLER]
#  (E) baseline_rhyme_probability: float [DATA] - P(rhyme) without intervention
#  (E) baseline_recorded: True [ENABLER]
#
# --- LOCAL COMPUTATION ---
# a_formulate_stage
#  (P) baseline_recorded == True [ENABLER]
#  (P) stage_name must be in stages_to_test
#  (E) hypothesized_stages[stage_name]: Dict [DATA] - stage hypothesis (incl. threshold)
#  (E) num_stages_formulated: int [DATA] - count
#  (E) hypothesis_complete: True [ENABLER] (when all stages formulated)
#
# --- CLT SERVER ACTIONS (Server 2) ---
# a_run_experiment
#  (P) hypothesized_stages[stage_name] must exist
#  (E) experiment_results[stage_name]: Dict [DATA] - observed results
#
# --- LOCAL COMPUTATION ---
# a_evaluate_stage
#  (P) experiment_results[stage_name] must exist
#  (E) stage_evaluations[stage_name]: Dict [DATA] - correspondence assessment (incl. threshold_satisfied)
#  (E) num_stages_validated: int [DATA] - count
#  (E) validation_complete: True [ENABLER] (when all stages validated)
#
# --- REPORT ---
# a_compile_report
#  (P) validation_complete == True [ENABLER]
#  (E) mechanism_model: Dict [DATA] - the formal model
#  (E) correspondence_score: float [DATA] - overall match (0.0-1.0)
#  (E) report_compiled: True [ENABLER]
# ============================================================================


# ============================================================================
# ACTIONS (7)
# ============================================================================

def a_initialize_analysis(state: State, model_name: str, prompt_text: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:initialize_analysis

    Action signature:
        a_initialize_analysis(state, model_name, prompt_text)

    Action parameters:
        model_name: Transformer model identifier (e.g., 'Gemma_2_2B')
        prompt_text: Poetry prompt to analyze for implicit planning

    Action purpose:
        Initialize the mechanism analysis with model specification, prompt,
        and empty tracking structures for hypothesis formulation and validation

    Preconditions:
        - model_name must be a known model with CLT support
        - stages_to_test must be pre-configured on state

    Effects:
        - Model specification loaded (state.model_spec) [DATA]
        - Tracking structures initialized (state.hypothesized_stages, etc.) [DATA]
        - Stage count recorded (state.num_stages) [DATA]
        - Analysis initialized flag set (state.analysis_initialized) [ENABLER]

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
    # stages_to_test must be pre-configured on the initial state
    if not (hasattr(state, 'stages_to_test') and isinstance(state.stages_to_test, list)):
        return False
    if len(state.stages_to_test) == 0:
        return False
    # All requested stages must be valid
    for stage in state.stages_to_test:
        if stage not in MECHANISM_STAGES:
            return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Model and prompt configuration
    state.model_name = model_name
    state.prompt_text = prompt_text
    state.model_spec = KNOWN_MODELS[model_name]

    # [DATA] Stage tracking
    state.num_stages = len(state.stages_to_test)
    state.num_stages_formulated = 0
    state.num_stages_validated = 0

    # [DATA] Hypothesis and validation structures (initially empty)
    state.hypothesized_stages = {}
    state.experiment_results = {}
    state.stage_evaluations = {}

    # [DATA] Workflow flags (initially False)
    state.planning_site_identified = False
    state.baseline_recorded = False
    state.hypothesis_complete = False
    state.validation_complete = False
    state.report_compiled = False

    # [ENABLER] Gates all subsequent actions
    state.analysis_initialized = True
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
        Identify the planning site token position in the prompt. The planning
        site is the newline token between lines 3 and 4 of a primed couplet,
        where the residual stream encodes the rhyme decision. Its exact
        token position varies by prompt.

    Preconditions:
        - Analysis must be initialized (state.analysis_initialized)

    Effects:
        - Planning site position recorded (state.planning_site_position) [DATA]
        - Planning site identified flag set (state.planning_site_identified) [ENABLER]

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
    if not (hasattr(state, 'analysis_initialized') and state.analysis_initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Planning site position (populated by inference server at runtime)
    # The inference server tokenizes the prompt and identifies the newline
    # token between lines 3 and 4 of the priming couplet.
    state.planning_site_position = (
        f"${{locate_planning_site:model={state.model_name},"
        f"prompt={state.prompt_text}}}"
    )

    # [ENABLER] Gates baseline measurement and all experiments
    state.planning_site_identified = True
    # END: Effects

    return state


def a_record_baseline(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: inference_server:measure_rhyme_probability

    Action signature:
        a_record_baseline(state)

    Action parameters:
        None

    Action purpose:
        Measure the baseline rhyme probability at the planning site with no
        intervention. This establishes the reference point against which all
        knockout/injection experiments are compared. The melometis results
        showed ~78% baseline rhyme rate with priming context.

    Preconditions:
        - Planning site must be identified (state.planning_site_identified)

    Effects:
        - Baseline rhyme probability recorded (state.baseline_rhyme_probability) [DATA]
        - Baseline recorded flag set (state.baseline_recorded) [ENABLER]

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
    if not (hasattr(state, 'planning_site_identified') and state.planning_site_identified):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Baseline rhyme probability (populated by inference server at runtime)
    # Runs a clean forward pass and measures P(rhyme group) at the planning site.
    state.baseline_rhyme_probability = (
        f"${{measure_rhyme_probability:model={state.model_name},"
        f"prompt={state.prompt_text},"
        f"position={state.planning_site_position},"
        f"intervention=none}}"
    )

    # [ENABLER] Gates hypothesis formulation
    state.baseline_recorded = True
    # END: Effects

    return state


def a_formulate_stage(state: State, stage_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:formulate_stage

    Action signature:
        a_formulate_stage(state, stage_name)

    Action parameters:
        stage_name: Name of the mechanism stage to formulate
                    (e.g., 'context_activation', 'group_commitment')

    Action purpose:
        Record a formal hypothesis for one stage of the implicit planning
        mechanism. The hypothesis specifies the layer range, computational
        function, experiment type (knockout or injection), the predicted
        effect on P(rhyme) when that stage is disrupted, and a quantitative
        threshold for evaluating whether the prediction is satisfied.

    Preconditions:
        - Baseline must be recorded (state.baseline_recorded)
        - stage_name must be in stages_to_test
        - stage_name must not already be formulated

    Effects:
        - Stage hypothesis recorded (state.hypothesized_stages[stage_name]) [DATA]
        - Formulation count incremented (state.num_stages_formulated) [DATA]
        - Hypothesis complete flag set when all stages done (state.hypothesis_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(stage_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not stage_name.strip(): return False
    if stage_name not in MECHANISM_STAGES: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'baseline_recorded') and state.baseline_recorded):
        return False
    if stage_name not in state.stages_to_test:
        return False
    if stage_name in state.hypothesized_stages:
        return False
    # END: Preconditions

    # BEGIN: Effects
    stage_spec = MECHANISM_STAGES[stage_name]

    # [DATA] Stage hypothesis with full specification including threshold
    state.hypothesized_stages[stage_name] = {
        "stage_name": stage_name,
        "layer_start": stage_spec["layer_start"],
        "layer_end": stage_spec["layer_end"],
        "function": stage_spec["function"],
        "prediction": stage_spec["prediction"],
        "threshold": stage_spec["threshold"],
        "experiment_type": stage_spec["experiment_type"],
        "baseline_probability": state.baseline_rhyme_probability,
    }

    # [DATA] Track formulation progress
    state.num_stages_formulated = state.num_stages_formulated + 1

    # [ENABLER] Gates validation phase when all stages formulated
    if state.num_stages_formulated == state.num_stages:
        state.hypothesis_complete = True
    # END: Effects

    return state


def a_run_experiment(state: State, stage_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: clt_server:run_experiment

    Action signature:
        a_run_experiment(state, stage_name)

    Action parameters:
        stage_name: Name of the mechanism stage to test experimentally

    Action purpose:
        Run a knockout or injection experiment at the specified stage's layer
        range. For knockout stages, all CLT features in the layer range are
        zeroed out at the planning site. For injection stages, a rhyme-group
        feature is injected at the specified layer. The resulting P(rhyme)
        is measured and recorded.

    Preconditions:
        - Stage must be formulated (state.hypothesized_stages[stage_name])
        - Stage must not already have experiment results

    Effects:
        - Experiment results recorded (state.experiment_results[stage_name]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(stage_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not stage_name.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'hypothesized_stages') and
            stage_name in state.hypothesized_stages):
        return False
    if stage_name in state.experiment_results:
        return False
    # END: Preconditions

    # BEGIN: Effects
    hypothesis = state.hypothesized_stages[stage_name]
    experiment_type = hypothesis["experiment_type"]
    layer_start = hypothesis["layer_start"]
    layer_end = hypothesis["layer_end"]

    # [DATA] Experiment results (populated by CLT server at runtime)
    # The CLT server performs the knockout/injection, runs a forward pass,
    # and measures P(rhyme) at the planning site under the intervention.
    state.experiment_results[stage_name] = {
        "experiment_type": experiment_type,
        "layer_start": layer_start,
        "layer_end": layer_end,
        "observed_probability": (
            f"${{run_{experiment_type}:model={state.model_name},"
            f"layers={layer_start}-{layer_end},"
            f"position={state.planning_site_position},"
            f"prompt={state.prompt_text}}}"
        ),
        "baseline_probability": state.baseline_rhyme_probability,
    }
    # END: Effects

    return state


def a_evaluate_stage(state: State, stage_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:evaluate_correspondence

    Action signature:
        a_evaluate_stage(state, stage_name)

    Action parameters:
        stage_name: Name of the mechanism stage to evaluate

    Action purpose:
        Compare the observed experimental effect to the predicted effect for
        one stage. Determines whether the HTN hypothesis correctly models
        the transformer's computation at this layer range. Each stage has a
        quantitative threshold (metric, direction, value) that the observed
        result must satisfy for the correspondence to hold.

    Preconditions:
        - Experiment results must exist for this stage
        - Stage must not already be evaluated

    Effects:
        - Stage evaluation recorded (state.stage_evaluations[stage_name]) [DATA]
        - Validation count incremented (state.num_stages_validated) [DATA]
        - Validation complete flag set when all stages done (state.validation_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(stage_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not stage_name.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'experiment_results') and
            stage_name in state.experiment_results):
        return False
    if stage_name in state.stage_evaluations:
        return False
    # END: Preconditions

    # BEGIN: Effects
    hypothesis = state.hypothesized_stages[stage_name]
    results = state.experiment_results[stage_name]

    # [DATA] Correspondence evaluation
    # At runtime, compares numerical observed_probability against the
    # stage's threshold to determine if the hypothesis holds.
    threshold = hypothesis["threshold"]
    state.stage_evaluations[stage_name] = {
        "stage_name": stage_name,
        "function": hypothesis["function"],
        "prediction": hypothesis["prediction"],
        "threshold": threshold,
        "experiment_type": results["experiment_type"],
        "layers": f"{hypothesis['layer_start']}-{hypothesis['layer_end']}",
        "observed_probability": results["observed_probability"],
        "baseline_probability": results["baseline_probability"],
        "threshold_satisfied": (
            f"${{evaluate_threshold:"
            f"metric={threshold['metric']},"
            f"direction={threshold['direction']},"
            f"threshold_value={threshold['value']},"
            f"observed={results['observed_probability']},"
            f"baseline={results['baseline_probability']}}}"
        ),
        "correspondence": (
            f"${{evaluate_correspondence:"
            f"prediction={hypothesis['prediction']},"
            f"observed={results['observed_probability']},"
            f"baseline={results['baseline_probability']},"
            f"threshold_satisfied=${{evaluate_threshold:"
            f"metric={threshold['metric']},"
            f"direction={threshold['direction']},"
            f"threshold_value={threshold['value']},"
            f"observed={results['observed_probability']},"
            f"baseline={results['baseline_probability']}}}}}"
        ),
    }

    # [DATA] Track validation progress
    state.num_stages_validated = state.num_stages_validated + 1

    # [ENABLER] Gates report compilation when all stages validated
    if state.num_stages_validated == state.num_stages:
        state.validation_complete = True
    # END: Effects

    return state


def a_compile_report(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:compile_report

    Action signature:
        a_compile_report(state)

    Action parameters:
        None

    Action purpose:
        Assemble the complete formal mechanism model and correspondence
        report. The model documents each stage (layer range, hypothesized
        function, prediction, observed result) and computes an overall
        correspondence score between the HTN decomposition and the
        transformer's actual computation.

    Preconditions:
        - All stages must be validated (state.validation_complete)

    Effects:
        - Formal mechanism model assembled (state.mechanism_model) [DATA]
        - Overall correspondence score computed (state.correspondence_score) [DATA]
        - Report compiled flag set (state.report_compiled) [ENABLER]

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
    if not (hasattr(state, 'validation_complete') and state.validation_complete):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] The formal mechanism model: a complete record of the hypothesis
    # and its experimental validation
    state.mechanism_model = {
        "model_name": state.model_name,
        "prompt_text": state.prompt_text,
        "planning_site_position": state.planning_site_position,
        "baseline_rhyme_probability": state.baseline_rhyme_probability,
        "stages": state.hypothesized_stages,
        "experimental_results": state.experiment_results,
        "evaluations": state.stage_evaluations,
    }

    # [DATA] Overall correspondence score (computed at runtime)
    # Fraction of stages where observed effect matches prediction.
    state.correspondence_score = (
        f"${{compute_correspondence_score:"
        f"evaluations={list(state.stage_evaluations.keys())}}}"
    )

    # [ENABLER] Workflow complete
    state.report_compiled = True
    # END: Effects

    return state


# ============================================================================
# METHODS (4)
# ============================================================================

# ============================================================================
# TOP-LEVEL ENTRY POINT
# ============================================================================

def m_model_implicit_planning(state: State, model_name: str, prompt_text: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_model_implicit_planning(state, model_name, prompt_text)

    Method parameters:
        model_name: Transformer model to analyze (e.g., 'Gemma_2_2B')
        prompt_text: Poetry prompt for implicit planning analysis

    Method purpose:
        Top-level entry point. Models the LLM's implicit rhyme planning
        mechanism as an HTN decomposition, then validates each stage with
        systematic knockout/injection experiments.

    Preconditions:
        - model_name must be a known model
        - stages_to_test must be pre-configured on state

    Task decomposition:
        - a_initialize_analysis: Set up model, prompt, tracking structures
        - a_locate_planning_site: Find the planning site token position
        - a_record_baseline: Measure P(rhyme) without intervention
        - m_formulate_hypothesis: Define all stage hypotheses
        - m_validate_hypothesis: Test all stages experimentally
        - a_compile_report: Assemble formal model and correspondence score

    Returns:
        Task decomposition if successful, False otherwise

    Hierarchical Decomposition:
        m_model_implicit_planning
        +-- a_initialize_analysis
        +-- a_locate_planning_site
        +-- a_record_baseline
        +-- m_formulate_hypothesis
        |   +-- a_formulate_stage("context_activation")
        |   +-- a_formulate_stage("expectation_propagation")
        |   +-- a_formulate_stage("group_commitment")
        |   +-- a_formulate_stage("attention_routing")
        |   +-- a_formulate_stage("vocabulary_projection")
        +-- m_validate_hypothesis
        |   +-- m_test_stage("context_activation")
        |   |   +-- a_run_experiment("context_activation")
        |   |   +-- a_evaluate_stage("context_activation")
        |   +-- m_test_stage("expectation_propagation")
        |   |   +-- ...
        |   +-- m_test_stage("group_commitment")
        |   |   +-- ...
        |   +-- m_test_stage("attention_routing")
        |   |   +-- ...
        |   +-- m_test_stage("vocabulary_projection")
        |       +-- ...
        +-- a_compile_report
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
    # stages_to_test must be pre-configured on state
    if not (hasattr(state, 'stages_to_test') and isinstance(state.stages_to_test, list)):
        return False
    if len(state.stages_to_test) == 0:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_analysis", model_name, prompt_text),
        ("a_locate_planning_site",),
        ("a_record_baseline",),
        ("m_formulate_hypothesis",),
        ("m_validate_hypothesis",),
        ("a_compile_report",),
    ]
    # END: Task Decomposition


def m_formulate_hypothesis(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_formulate_hypothesis(state)

    Method parameters:
        None (reads state.stages_to_test)

    Method auxiliary parameters:
        stages_to_test: List[str] (from state.stages_to_test)

    Method purpose:
        Formulate the complete hypothesis by defining all mechanism stages.
        Each stage maps a layer range to a computational function and
        a predicted effect. Stages are formulated in canonical order
        (layers 0 -> 25) to mirror the transformer's forward pass.

    Preconditions:
        - Baseline must be recorded (state.baseline_recorded)

    Task decomposition:
        - a_formulate_stage x N (one per stage in stages_to_test)

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
    if not (hasattr(state, 'stages_to_test') and isinstance(state.stages_to_test, list)):
        return False
    stages_to_test = state.stages_to_test
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'baseline_recorded') and state.baseline_recorded):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Formulate stages in canonical order (layer 0 -> 25)
    ordered_stages = [s for s in STAGE_ORDER if s in stages_to_test]
    return [("a_formulate_stage", stage) for stage in ordered_stages]
    # END: Task Decomposition


def m_validate_hypothesis(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_validate_hypothesis(state)

    Method parameters:
        None (reads state.stages_to_test)

    Method auxiliary parameters:
        stages_to_test: List[str] (from state.stages_to_test)

    Method purpose:
        Validate the complete hypothesis by testing each stage with a
        knockout or injection experiment. Each stage is tested independently:
        run the experiment, then evaluate the correspondence between
        observed and predicted effects.

    Preconditions:
        - Hypothesis must be complete (state.hypothesis_complete)

    Task decomposition:
        - m_test_stage x N (one per stage in stages_to_test)

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
    if not (hasattr(state, 'stages_to_test') and isinstance(state.stages_to_test, list)):
        return False
    stages_to_test = state.stages_to_test
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'hypothesis_complete') and state.hypothesis_complete):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Validate stages in canonical order (layer 0 -> 25)
    ordered_stages = [s for s in STAGE_ORDER if s in stages_to_test]
    return [("m_test_stage", stage) for stage in ordered_stages]
    # END: Task Decomposition


def m_test_stage(state: State, stage_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_test_stage(state, stage_name)

    Method parameters:
        stage_name: Name of the mechanism stage to test

    Method purpose:
        Test a single stage of the implicit planning hypothesis. Runs the
        appropriate experiment (knockout or injection) at the stage's layer
        range, then evaluates whether the observed effect matches the
        predicted effect.

    Preconditions:
        - Stage must be formulated (state.hypothesized_stages[stage_name])

    Task decomposition:
        - a_run_experiment: Execute knockout/injection at the stage's layers
        - a_evaluate_stage: Compare observed vs predicted effect

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(stage_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not stage_name.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'hypothesized_stages') and
            stage_name in state.hypothesized_stages):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_run_experiment", stage_name),
        ("a_evaluate_stage", stage_name),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_initialize_analysis,
    a_locate_planning_site,
    a_record_baseline,
    a_formulate_stage,
    a_run_experiment,
    a_evaluate_stage,
    a_compile_report,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Top-level entry point
declare_task_methods('m_model_implicit_planning', m_model_implicit_planning)

# Hypothesis formulation and validation
declare_task_methods('m_formulate_hypothesis', m_formulate_hypothesis)
declare_task_methods('m_validate_hypothesis', m_validate_hypothesis)

# Single-stage testing
declare_task_methods('m_test_stage', m_test_stage)

# ============================================================================
# END OF FILE
# ============================================================================
