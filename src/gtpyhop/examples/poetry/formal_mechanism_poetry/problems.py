"""
Problem definitions for the Formal Mechanism Poetry HTN Domain.
-- Generated 2026-02-18

This file defines initial states for formal mechanism analysis workflows
that model the LLM's implicit rhyme planning as an HTN decomposition and
validate it with systematic knockout/injection experiments.

The workflow demonstrates coordination between 3 servers:
  - Local computation: Hypothesis formulation, evaluation, report compilation
  - Server 1 (inference_server): Forward passes, probability measurement
  - Server 2 (clt_server): CLT feature knockout/injection experiments

Scenarios:
  - scenario_1_full_mechanism:    All 5 stages, Gemma 2 2B  -> 19 actions
  - scenario_2_commitment_focus:  Group commitment only      ->  7 actions
  - scenario_3_three_stage:       3 key stages               -> 13 actions

Plan length formula: 4 + 3N
  Where N = number of stages tested
  init + locate + baseline + (formulate + experiment + evaluate) x N + report
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

def h_create_base_mechanism_state(name: str) -> State:
    """Create a base state with common mechanism analysis workflow properties."""
    state = State(name)
    # Analysis configuration (set per scenario)
    state.model_name = ""
    state.prompt_text = ""
    state.stages_to_test = []
    # Model specification (set by a_initialize_analysis)
    state.model_spec = {}
    state.num_stages = 0
    # Planning site (set by a_locate_planning_site)
    state.planning_site_position = -1
    # Baseline (set by a_record_baseline)
    state.baseline_rhyme_probability = 0.0
    # Hypothesis tracking (set by a_formulate_stage)
    state.hypothesized_stages = {}
    state.num_stages_formulated = 0
    # Experiment tracking (set by a_run_experiment, a_evaluate_stage)
    state.experiment_results = {}
    state.stage_evaluations = {}
    state.num_stages_validated = 0
    # Workflow enablers (all initially False)
    state.analysis_initialized = False
    state.planning_site_identified = False
    state.baseline_recorded = False
    state.hypothesis_complete = False
    state.validation_complete = False
    state.report_compiled = False
    # Report output (set by a_compile_report)
    state.mechanism_model = {}
    state.correspondence_score = 0.0
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: formal_mechanism_poetry

# BEGIN: Scenario: scenario_1_full_mechanism
# Configuration
_model = "Gemma_2_2B"
_prompt = "The wind blows hard across the town,\nThe clouds roll in, the sun goes down.\nThe autumn leaves begin to fall,\n"
_stages = [
    "context_activation",
    "expectation_propagation",
    "group_commitment",
    "attention_routing",
    "vocabulary_projection",
]

# State
initial_state_scenario_1 = h_create_base_mechanism_state('scenario_1_full_mechanism')
initial_state_scenario_1.model_name = _model
initial_state_scenario_1.prompt_text = _prompt
initial_state_scenario_1.stages_to_test = _stages

# Problem
problems['scenario_1_full_mechanism'] = (
    initial_state_scenario_1,
    [('m_model_implicit_planning', _model, _prompt)],
    f'Full mechanism analysis ({len(_stages)} stages) on {_model} -> 19 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_commitment_focus
# Configuration
_model = "Gemma_2_2B"
_prompt = "The wind blows hard across the town,\nThe clouds roll in, the sun goes down.\nThe autumn leaves begin to fall,\n"
_stages = ["group_commitment"]

# State
initial_state_scenario_2 = h_create_base_mechanism_state('scenario_2_commitment_focus')
initial_state_scenario_2.model_name = _model
initial_state_scenario_2.prompt_text = _prompt
initial_state_scenario_2.stages_to_test = _stages

# Problem
problems['scenario_2_commitment_focus'] = (
    initial_state_scenario_2,
    [('m_model_implicit_planning', _model, _prompt)],
    f'Commitment-only analysis ({len(_stages)} stage) on {_model} -> 7 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_three_stage
# Configuration
_model = "Gemma_2_2B"
# Different prompt to test generalization: -out rhyme group (from melometis experiments)
_prompt = "The stars were twinkling all about,\nThe children laughed and gave a shout.\nThe evening air began to cool,\n"
_stages = [
    "context_activation",
    "group_commitment",
    "attention_routing",
]

# State
initial_state_scenario_3 = h_create_base_mechanism_state('scenario_3_three_stage')
initial_state_scenario_3.model_name = _model
initial_state_scenario_3.prompt_text = _prompt
initial_state_scenario_3.stages_to_test = _stages

# Problem
problems['scenario_3_three_stage'] = (
    initial_state_scenario_3,
    [('m_model_implicit_planning', _model, _prompt)],
    f'Three-stage analysis ({len(_stages)} stages) on {_model} -> 13 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
