# Formal Mechanism Poetry HTN Domain

## Overview

This example demonstrates **Architecture 12: HTN as Formal Model of the LLM's Implicit Planning** from the `htn-roles-for-planning-in-poems.md` analysis. Instead of using the HTN planner to *steer* the LLM, this domain uses the HTN formalism to **model what the LLM computes internally** during rhyme planning, then validates the model with systematic experiments.

The key insight: Anthropic's "Planning in Poems" (March 2025) and the melometis v1.3.0 results proved that LLMs have an implicit planner for rhyme. At the planning site (the newline token between lines 3 and 4), the residual stream encodes a rhyme decision confirmed by a 155-million-fold probability spike. This domain expresses the *hypothesis about that mechanism* as an HTN task decomposition, where each stage maps to a layer range in the transformer.

This is **computational cognitive science**: using HTN planning theory to model neural network computation. The plan IS the hypothesis, and the plan's execution IS the experimental validation.

## Benchmarking Scenarios

| Scenario | Stages | Model | Actions | Status |
|----------|--------|-------|---------|--------|
| `scenario_1_full_mechanism` | 5 (all) | Gemma 2 2B | 19 | VALID |
| `scenario_2_commitment_focus` | 1 (commitment) | Gemma 2 2B | 7 | VALID |
| `scenario_3_three_stage` | 3 (context, commitment, routing) | Gemma 2 2B | 13 | VALID |

### Plan Length Formula

| Stages (N) | Formula | Actions |
|------------|---------|---------|
| 1 | 4 + 3x1 | 7 |
| 3 | 4 + 3x3 | 13 |
| 5 | 4 + 3x5 | 19 |

Where: `init + locate + baseline + (formulate + experiment + evaluate) x N + report`

## The Hypothesis: 5 Stages of Implicit Rhyme Planning

The HTN decomposition models the transformer's implicit planning as 5 sequential stages:

| Stage | Layers | Function | Experiment | Prediction | Threshold |
|-------|--------|----------|------------|------------|-----------|
| **context_activation** | 0-8 | Attend to priming rhyme context | Knockout | P(rhyme) drops to <10% of baseline | ratio < 0.10 |
| **expectation_propagation** | 9-15 | Build rhyme-group representation | Knockout | Weakens signal by >50% | ratio < 0.50 |
| **group_commitment** | 16 | Planning feature fires | Injection | L16 effect >=100x stronger than L22 | effect_ratio > 100 |
| **attention_routing** | 17-22 | Attention carries signal to output | Knockout | P(rhyme) drops >60% | ratio < 0.40 |
| **vocabulary_projection** | 23-25 | Project onto vocabulary logits | Knockout | P(rhyme) drops >30% | ratio < 0.70 |

### Empirical Grounding (from melometis v1.3.0)

- **Layer 16**: 160,379x probability spike for planning features (strongest signal)
- **Layer 25**: 610x probability spike (weaker but confirmed)
- **Planning site**: Newline token between lines 3 and 4 (position varies by prompt)
- **Baseline**: ~78% rhyme rate with priming context
- **Suppress+inject**: 48.3% max redirect probability at group level

## Three-Server Architecture

1. **Local computation** (Hypothesis Formulation, Evaluation, Report)
   - `initialize_analysis`: Set up model, prompt, tracking structures
   - `formulate_stage`: Record a stage hypothesis (layer range, function, prediction)
   - `evaluate_correspondence`: Compare observed vs predicted effect
   - `compile_report`: Assemble formal model and correspondence score

2. **Server 1: inference_server** (Forward Passes & Probability)
   - `locate_planning_site`: Find the planning site token position
   - `measure_rhyme_probability`: Measure P(rhyme) at the planning site

3. **Server 2: clt_server** (CLT Feature Experiments)
   - `run_experiment`: Knockout or inject features at specified layer range

## HTN Decomposition

### Full Mechanism (5 stages, 19 actions)
```
m_model_implicit_planning("Gemma_2_2B", prompt)
+-- a_initialize_analysis("Gemma_2_2B", prompt)
+-- a_locate_planning_site                                [Server 1]
+-- a_record_baseline                                     [Server 1]
+-- m_formulate_hypothesis
|   +-- a_formulate_stage("context_activation")
|   +-- a_formulate_stage("expectation_propagation")
|   +-- a_formulate_stage("group_commitment")
|   +-- a_formulate_stage("attention_routing")
|   +-- a_formulate_stage("vocabulary_projection")
+-- m_validate_hypothesis
|   +-- m_test_stage("context_activation")
|   |   +-- a_run_experiment("context_activation")        [Server 2]
|   |   +-- a_evaluate_stage("context_activation")
|   +-- m_test_stage("expectation_propagation")
|   |   +-- a_run_experiment("expectation_propagation")   [Server 2]
|   |   +-- a_evaluate_stage("expectation_propagation")
|   +-- m_test_stage("group_commitment")
|   |   +-- a_run_experiment("group_commitment")          [Server 2]
|   |   +-- a_evaluate_stage("group_commitment")
|   +-- m_test_stage("attention_routing")
|   |   +-- a_run_experiment("attention_routing")         [Server 2]
|   |   +-- a_evaluate_stage("attention_routing")
|   +-- m_test_stage("vocabulary_projection")
|       +-- a_run_experiment("vocabulary_projection")     [Server 2]
|       +-- a_evaluate_stage("vocabulary_projection")
+-- a_compile_report
```

### Commitment Focus (1 stage, 7 actions)
```
m_model_implicit_planning("Gemma_2_2B", prompt)
+-- a_initialize_analysis("Gemma_2_2B", prompt)
+-- a_locate_planning_site                                [Server 1]
+-- a_record_baseline                                     [Server 1]
+-- m_formulate_hypothesis
|   +-- a_formulate_stage("group_commitment")
+-- m_validate_hypothesis
|   +-- m_test_stage("group_commitment")
|       +-- a_run_experiment("group_commitment")          [Server 2]
|       +-- a_evaluate_stage("group_commitment")
+-- a_compile_report
```

## File Structure

```
formal_mechanism_poetry/
+-- domain.py       # Domain definition with 7 actions and 4 methods
+-- problems.py     # Initial state definitions (3 scenarios)
+-- __init__.py     # Package initialization with get_problems()
+-- README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 7
- **Methods**: 4
- **Servers**: 3 (local, inference_server, clt_server)
- **Scenarios**: 3
- **Mechanism Stages**: 5 (configurable per scenario)

## State Properties

### Analysis Configuration
- `model_name`: Transformer model identifier (str)
- `prompt_text`: Poetry prompt for analysis (str)
- `stages_to_test`: Which mechanism stages to formulate and test (List[str])
- `model_spec`: Model specification from KNOWN_MODELS (Dict)
- `num_stages`: Count of stages to test (int)

### Workflow State
- `analysis_initialized`: Analysis setup complete (bool) [ENABLER]

### Planning Site
- `planning_site_position`: Token position of the planning site (int)
- `planning_site_identified`: Planning site located (bool) [ENABLER]

### Baseline
- `baseline_rhyme_probability`: P(rhyme) without intervention (float)
- `baseline_recorded`: Baseline measured (bool) [ENABLER]

### Hypothesis Tracking
- `hypothesized_stages`: Stage name -> hypothesis dict incl. threshold (Dict)
- `num_stages_formulated`: Count of formulated stages (int)
- `hypothesis_complete`: All stages formulated (bool) [ENABLER]

### Validation Tracking
- `experiment_results`: Stage name -> observed results (Dict)
- `stage_evaluations`: Stage name -> correspondence assessment incl. threshold_satisfied (Dict)
- `num_stages_validated`: Count of validated stages (int)
- `validation_complete`: All stages validated (bool) [ENABLER]

### Report
- `mechanism_model`: The formal model (Dict)
- `correspondence_score`: Overall match between hypothesis and observation (float)
- `report_compiled`: Report assembled (bool) [ENABLER]

## Actions Summary

### Initialization (1 action)
1. **a_initialize_analysis**: Set up model, prompt, and tracking structures

### Inference Server Actions (2 actions)
2. **a_locate_planning_site**: Identify the planning site token position
3. **a_record_baseline**: Measure baseline P(rhyme) without intervention

### Hypothesis Formulation (1 action)
4. **a_formulate_stage**: Record a stage hypothesis (layer range, function, prediction, threshold)

### CLT Server Actions (1 action)
5. **a_run_experiment**: Knockout or inject features at a stage's layer range

### Evaluation (1 action)
6. **a_evaluate_stage**: Compare observed vs predicted effect against quantitative threshold

### Report (1 action)
7. **a_compile_report**: Assemble formal model and correspondence score

## Methods Summary

### Top-Level (1 method)
1. **m_model_implicit_planning**: Entry point -- initialize, locate, baseline, formulate, validate, report

### Hypothesis Phase (1 method)
2. **m_formulate_hypothesis**: Formulate all N stage hypotheses in canonical order

### Validation Phase (2 methods)
3. **m_validate_hypothesis**: Test all N stages with experiments
4. **m_test_stage**: Test one stage: run experiment -> evaluate correspondence

## Usage Examples

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.poetry.formal_mechanism_poetry import the_domain, problems

# Create planner session
with gtpyhop.PlannerSession(domain=the_domain, verbose=1) as session:
    # Get problem instance
    state, tasks, desc = problems.get_problems()['scenario_1_full_mechanism']

    # Find plan
    result = session.find_plan(state, tasks)

    if result.success:
        print(f"Plan found with {len(result.plan)} actions:")
        for i, action in enumerate(result.plan, 1):
            print(f"  {i}. {action[0]}")
```

### Using the benchmarking script

```bash
cd src/gtpyhop/examples/poetry
python benchmarking.py formal_mechanism_poetry
```

## Workflow Enablers

The domain uses **workflow enabler** properties to ensure correct sequencing:

1. **Initialization**: `analysis_initialized` must be True before locating planning site
2. **Planning site**: `planning_site_identified` must be True before recording baseline
3. **Baseline**: `baseline_recorded` must be True before formulating stages
4. **Hypothesis**: `hypothesis_complete` must be True before validating stages
5. **Validation**: `validation_complete` must be True before compiling report

## Key Features

### 1. Formal Hypothesis as HTN Plan
The HTN decomposition IS the hypothesis about the transformer's computation. Each method decomposition mirrors a hypothesized computational step.

### 2. Configurable Stage Selection
Scenarios can test all 5 stages or a subset, enabling focused investigation of specific layers without re-running the full analysis.

### 3. Dynamic Decomposition
The `m_formulate_hypothesis` and `m_validate_hypothesis` methods read `state.stages_to_test` to construct their decompositions, adapting to the scenario's configuration.

### 4. Canonical Ordering
Stages are always processed in layer order (0 -> 25), mirroring the transformer's forward pass direction.

### 5. Quantitative Thresholds
Each stage carries a falsifiable threshold (metric, direction, value) derived from the melometis data. The `a_evaluate_stage` action records whether the threshold is satisfied, making correspondence evaluation transparent and reproducible.

### 6. Separation of Hypothesis and Experiment
The domain cleanly separates formulating the hypothesis (`a_formulate_stage`) from testing it (`a_run_experiment` + `a_evaluate_stage`), enabling the plan itself to serve as a scientific artifact.

## Scientific Context

This domain implements the "most scientifically novel" use of an HTN planner identified in the comprehensive architecture analysis:

> "We model the transformer's implicit planning process as an HTN task decomposition and empirically validate the correspondence."

The formal comparison between HTN decomposition and neural computation is a contribution to **computational cognitive science** -- using classical AI planning theory to model neural network behavior.

## References

- **Architecture 12**: `htn-roles-for-planning-in-poems.md`, Section "TIER 4: The Wild Ideas"
- **Melometis v1.3.0 Results**: Planning site discovery, 155M-fold probability spike
- **Anthropic "Planning in Poems"**: Anthropic Research, March 2025
- **GTPyhop Documentation**: https://github.com/PCfVW/GTPyhop

---
*Generated 2026-02-18*
