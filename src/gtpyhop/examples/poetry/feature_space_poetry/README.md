# Feature Space Poetry HTN Domain

## Overview

This example demonstrates **Architecture 6: HTN Operates in Feature Space (The Wild One)** from the `htn-roles-for-planning-in-poems.md` analysis. The HTN's state space IS the CLT activation space. Actions are feature-level operations on the residual stream. The "world" is the residual stream at the planning site.

The key insight: the HTN doesn't plan *text*; it plans *interventions on the model's internal representations*. The domain knowledge encoded in methods captures the suppress+inject protocol from melometis Version D. Backtracking over candidate features automates what was done manually in the experiments -- the plan itself becomes a scientific artifact recording the automated intervention.

| Dimension | Other poetry examples | This example |
|-----------|----------------------|--------------|
| State space | Text, rhyme labels | CLT activation space |
| Actions modify | Poem structure | Residual stream & features |
| Plan purpose | Generate poetry | Execute suppress+inject protocol |
| Backtracking over | Rhyme strategies | Injection candidate features |

## Benchmarking Scenarios

Scenario 0 is **ground truth** -- it replicates what actually happened in Version D. Scenarios 1-3 are **counterfactual what-ifs** exploring departures from reality.

| Scenario | Description | From -> To | Layers (L) | Threshold | Backtracking | Actions | Status |
|----------|-------------|-----------|------------|-----------|-------------|---------|--------|
| `scenario_0_version_d_star_result` | Ground truth | out -> ound | 26 (all) | 0.40 | No | 34 | VALID |
| `scenario_1_cheapest_first` | What if around wasn't first? | out -> ound | 26 (all) | 0.40 | Yes (2 failures) | 34 | VALID |
| `scenario_2_planning_layer_only` | What if only planning layer? | out -> ound | 1 ([16]) | 0.40 | No | 9 | VALID |
| `scenario_3_different_group` | What if different group? | oo -> ound | 2 ([16,25]) | 0.02 | Yes (1 failure) | 10 | VALID |

### Plan Length Formula

| Layers (L) | Formula | Actions |
|-----------|---------|---------|
| 1 | 1 + 8 | 9 |
| 2 | 2 + 8 | 10 |
| 26 | 26 + 8 | 34 |

Where: `(encode x L) + init + locate + baseline + suppress + inject + measure + evaluate + report`

### Planner Behavior

| Scenario | Greedy | Iterative DFS |
|----------|--------|---------------|
| scenario_0 (around first, P=0.483 >= 0.40) | SUCCESS | SUCCESS |
| scenario_1 (around last, first two fail threshold) | FAIL | SUCCESS |
| scenario_2 (around only, P=0.483 >= 0.40) | SUCCESS | SUCCESS |
| scenario_3 (around second, first fails threshold) | FAIL | SUCCESS |

Scenarios 1 and 3 require backtracking because the first candidate's measured probability falls below the threshold, causing `a_evaluate_threshold` to fail and triggering the planner to try the next injection candidate.

## Empirical Grounding (from melometis v1.3.0 Version D)

### Measured Probabilities (from suppress_inject_sweep.json)

The Version D experiment tested 136 suppress+inject pairs (34 alternative groups x 4 prompts). Feature L22:10243 ("around") was measured on all 4 prompts:

| Prompt | Suppress | P(around) after intervention | Source line |
|--------|----------|------------------------------|-------------|
| -out/about | -out | **48.29%** (star result) | 10138 |
| -out/shout | -out | **33.86%** | 16592 |
| -oo/who | -oo | **5.67%** | 23356 |
| -ow/so | -ow | **3.36%** | 3844 |

Other candidates (L16:7712 "ground", L25:3298 "round") were **not tested** in the Version D sweep -- only one feature per alternative group was tested. Their probabilities are estimated from CLT decoder vector analysis.

### Rhyme Groups

| Group | ARPAbet | Key words | Experimental role |
|-------|---------|-----------|-------------------|
| `-out` | AW1-T | about, out, shout | Primary suppression target (2 of 4 Version D prompts) |
| `-ound` | AW1-N-D | around, found, ground, round | Cross-group injection target; L22:10243 achieved 48.3% |
| `-ow` | OW1 | go, grow, know, so, though | Natural group on 1 Version D prompt |
| `-oo` | UW1 | do, new, ou, to, two, who | Natural group on 1 Version D prompt; 157,000x ratio |

### Version D Protocol
- **Suppress**: Negative strength on ALL features from natural group across all downstream layers
- **Inject**: Positive strength on single feature from alternative group
- **Result**: 95/136 pairs (70%) show planning-site max above threshold
- **Star result**: "around" (L22:10243) achieved 48.3% redirect probability

## Three-Server Architecture

1. **Local computation** (Initialize, Suppress, Evaluate, Report)
   - `a_initialize_intervention`: Setup model, tracking structures
   - `a_suppress_group`: Zero out from_group features, reconstruct residual
   - `a_evaluate_threshold`: Check measured_probability >= probability_threshold (BACKTRACKING TRIGGER)
   - `a_compile_intervention_report`: Assemble complete intervention record

2. **Server 1: inference_server** (Forward Passes & Probability)
   - `a_locate_planning_site`: Find planning site, extract residual stream
   - `a_measure_baseline`: Measure P(from_group) before intervention
   - `a_measure_effect`: Measure P(to_group) after intervention, look up simulated probability

3. **Server 2: clt_server** (CLT Encode/Decode & Feature Injection)
   - `a_encode_residual`: Run CLT encoder at one layer
   - `a_inject_feature`: Add decoder vector to residual stream

## HTN Decomposition

### Scenario 0: Version D Star Result (26 layers, no backtracking, 34 actions)
```
m_redirect_rhyme("Gemma_2_2B", prompt)
+-- a_initialize_intervention("Gemma_2_2B", prompt)
+-- a_locate_planning_site                                [inference_server]
+-- a_measure_baseline                                    [inference_server]
+-- m_encode_all_layers
|   +-- a_encode_residual(0)                              [clt_server]
|   +-- a_encode_residual(1)                              [clt_server]
|   +-- ... (24 more layers)
|   +-- a_encode_residual(25)                             [clt_server]
+-- a_suppress_group("out")
+-- m_find_best_injection("ound")
|   +-- [TRY 1: m_find_best_injection_try_1]
|       +-- a_inject_feature("L22:10243", 1.0)            [clt_server]
|       +-- a_measure_effect                               [inference_server]
|       +-- a_evaluate_threshold                           [SUCCEEDS: 0.483 >= 0.40]
+-- a_compile_intervention_report
```

### Scenario 1: Cheapest First (26 layers, backtracking, 34 actions)
```
m_redirect_rhyme("Gemma_2_2B", prompt)
+-- ... (same init/locate/baseline/encode/suppress as scenario 0)
+-- m_find_best_injection("ound")
|   +-- [TRY 1: m_find_best_injection_try_1]
|   |   +-- a_inject_feature("L25:3298", 1.0)             [clt_server]
|   |   +-- a_measure_effect                               [inference_server]
|   |   +-- a_evaluate_threshold                           [FAILS: 0.001 < 0.40]
|   |                                           [BACKTRACK -> restore state]
|   +-- [TRY 2: m_find_best_injection_try_2]
|   |   +-- a_inject_feature("L16:7712", 1.0)             [clt_server]
|   |   +-- a_measure_effect                               [inference_server]
|   |   +-- a_evaluate_threshold                           [FAILS: 0.003 < 0.40]
|   |                                           [BACKTRACK -> restore state]
|   +-- [TRY 3: m_find_best_injection_try_3]
|       +-- a_inject_feature("L22:10243", 1.0)            [clt_server]
|       +-- a_measure_effect                               [inference_server]
|       +-- a_evaluate_threshold                           [SUCCEEDS: 0.483 >= 0.40]
+-- a_compile_intervention_report
```

### Scenario 2: Planning Layer Only (1 layer, no backtracking, 9 actions)
```
m_redirect_rhyme("Gemma_2_2B", prompt)
+-- a_initialize_intervention("Gemma_2_2B", prompt)
+-- a_locate_planning_site                                [inference_server]
+-- a_measure_baseline                                    [inference_server]
+-- m_encode_all_layers
|   +-- a_encode_residual(16)                             [clt_server]
+-- a_suppress_group("out")                               [clt_server]
+-- m_find_best_injection("ound")
|   +-- [TRY 1: m_find_best_injection_try_1]
|       +-- a_inject_feature("L22:10243", 1.0)            [clt_server]
|       +-- a_measure_effect                               [inference_server]
|       +-- a_evaluate_threshold                           [SUCCEEDS: 0.483 >= 0.40]
+-- a_compile_intervention_report
```

## File Structure

```
feature_space_poetry/
+-- domain.py       # Domain definition with 9 actions and 6 methods
+-- problems.py     # Initial state definitions (4 scenarios)
+-- __init__.py     # Package initialization with get_problems()
+-- README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 9
- **Methods**: 6 (3 backtracking alternatives for m_find_best_injection)
- **Servers**: 3 (local, inference_server, clt_server)
- **Scenarios**: 4 (1 ground truth + 3 what-ifs)
- **Rhyme Groups**: 4 (empirically validated from Version D)

## State Properties

### Intervention Configuration
- `model_name`: Transformer model identifier (str)
- `prompt_text`: Poetry prompt for intervention (str)
- `from_group`: Rhyme group to suppress (str)
- `to_group`: Rhyme group to inject toward (str)
- `candidate_features`: Ranked feature IDs for injection (List[str])
- `layers_to_encode`: Which layers to CLT-encode (List[int])
- `injection_strength`: Strength multiplier for injection (float)
- `probability_threshold`: P(target) threshold for success (float)
- `candidate_probabilities`: Per-candidate P(target) for this scenario (Dict[str, float])
- `model_spec`: Model specification from KNOWN_MODELS (Dict)

### Activation Space (the "World")
- `active_features`: Per-layer feature activations (Dict[int, str])
- `residual_stream`: Current residual at planning site (str)
- `target_distribution`: P(word) for target group (str/Dict)
- `injection_history`: Log of (feature_id, strength) pairs (List)
- `suppressed_features`: Features zeroed per layer (Dict/str)

### Workflow State
- `intervention_initialized`: Intervention setup complete (bool) [ENABLER]
- `planning_site_located`: Planning site found (bool) [ENABLER]
- `planning_site_position`: Token position of planning site (str)
- `baseline_measured`: Baseline P(from_group) recorded (bool) [ENABLER]
- `baseline_probability`: P(from_group) without intervention (str)

### Encoding & Suppression
- `num_layers_encoded`: Count of encoded layers (int)
- `encoding_complete`: All layers encoded (bool) [ENABLER]
- `suppression_complete`: From_group features zeroed (bool) [ENABLER]

### Injection & Evaluation
- `num_candidates_tried`: Count of injection attempts (int)
- `measured_probability`: P(target) from most recent injection (float)
- `injection_complete`: Feature injected (bool) [ENABLER]
- `effect_measured`: P(to_group) measured (bool) [ENABLER]
- `threshold_met`: Redirect probability sufficient (bool) [ENABLER]

### Report
- `intervention_report`: Complete intervention record (Dict)
- `intervention_complete`: Workflow complete (bool) [ENABLER]

## Actions Summary (by server)

### Initialization (1 action)
1. **a_initialize_intervention**: Setup model, activation space, tracking structures

### Inference Server Actions (3 actions)
2. **a_locate_planning_site**: Find planning site, extract residual stream
3. **a_measure_baseline**: Measure P(from_group) before intervention
4. **a_measure_effect**: Measure P(to_group) after intervention, look up simulated probability

### CLT Server Actions (2 actions)
5. **a_encode_residual**: Run CLT encoder at one layer
6. **a_inject_feature**: Add decoder vector to residual stream

### Local Computation (3 actions)
7. **a_suppress_group**: Zero out from_group features, reconstruct residual
8. **a_evaluate_threshold**: Compare measured_probability >= probability_threshold (BACKTRACKING TRIGGER)
9. **a_compile_intervention_report**: Assemble complete intervention record

## Methods Summary

### Top-Level (1 method)
1. **m_redirect_rhyme**: Entry point -- init, locate, baseline, encode, suppress, inject, report

### Layer Encoding (1 method)
2. **m_encode_all_layers**: Dynamically encode all configured layers

### Injection Search (3 methods, backtracking)
3. **m_find_best_injection_try_1**: Try first candidate (index 0)
4. **m_find_best_injection_try_2**: Try second candidate (index 1)
5. **m_find_best_injection_try_3**: Try third candidate (index 2)

## Workflow Enablers

The domain uses **workflow enabler** properties to ensure correct sequencing:

1. **Initialization**: `intervention_initialized` must be True before locating planning site
2. **Planning site**: `planning_site_located` must be True before measuring baseline
3. **Baseline**: `baseline_measured` must be True before encoding layers
4. **Encoding**: `encoding_complete` must be True before suppressing group
5. **Suppression**: `suppression_complete` must be True before injecting features
6. **Injection**: `injection_complete` must be True before measuring effect
7. **Effect**: `effect_measured` must be True before evaluating threshold
8. **Threshold**: `threshold_met` must be True before compiling report

## Backtracking Mechanism

The `m_find_best_injection` task has 3 alternative methods registered:
```python
declare_task_methods('m_find_best_injection',
                     m_find_best_injection_try_1,   # first candidate
                     m_find_best_injection_try_2,   # second candidate
                     m_find_best_injection_try_3)   # third candidate
```

### Probability-Based Evaluation

When `a_measure_effect` runs, it looks up the injected candidate's known probability from `state.candidate_probabilities` (populated per-scenario from Version D experiments where measured, CLT analysis where estimated). Then `a_evaluate_threshold` compares `state.measured_probability` against `state.probability_threshold`. If the probability is insufficient, the action returns False, GTPyhop backtracks and tries the next method.

### State Restoration on Backtrack

GTPyhop performs a **full state copy** (deep copy) before each method attempt. When `a_evaluate_threshold` returns False, the planner restores the state snapshot taken before the failed method's decomposition began. This means:

- `state.residual_stream` reverts to the post-suppression value (the injected decoder vector from the failed attempt is undone)
- `state.injection_history` reverts to `[]` (the failed injection is removed)
- `state.injection_complete`, `state.effect_measured` revert to `False`
- `state.measured_probability` reverts to `0.0`
- `state.num_candidates_tried` reverts to `0`

The final plan contains **only the successful path's actions**. The `intervention_report` therefore records only the injection that succeeded, with `num_candidates_tried` reflecting only the successful execution -- not the total number of attempts.

**Portability warning**: This domain depends on GTPyhop's copy-on-backtrack semantics. Porting to a planner that does NOT deep-copy state before trying alternative methods will cause silent corruption: the `residual_stream` would retain the failed injection's decoder vector, and `injection_history` would accumulate entries from all attempts.

## Key Features

### 1. Activation Space as HTN State
The HTN's state IS the CLT activation space. `state.residual_stream` is the "world," `state.active_features` are per-layer feature activations, and actions modify these representations directly.

### 2. Automated Version D Protocol
The suppress+inject protocol from melometis Version D is fully captured as HTN task decomposition: encode layers, suppress natural group, search for best injection candidate.

### 3. Probability-Based Backtracking
Backtracking is driven by actual probability comparisons: `a_measure_effect` looks up the candidate's known P(target) from `candidate_probabilities`, then `a_evaluate_threshold` compares against the scenario's threshold. This replaces an earlier index-based mechanism with a genuine empirical criterion.

### 4. Ground Truth + What-If Scenarios
Scenario 0 replicates the actual Version D star result (L22:10243 "around" at 48.29%). Scenarios 1-3 explore counterfactual departures: different candidate ordering, fewer layers, different suppression group. The star result probability is **measured**; other candidate probabilities are **estimated** from CLT analysis.

### 5. Dynamic Layer Encoding
`m_encode_all_layers` reads `state.layers_to_encode` to generate per-layer encoding actions, enabling scenarios from 1 layer (9 actions) to all 26 layers (34 actions).

### 6. Scientific Artifact
The plan records the complete intervention protocol: which layers were encoded, which features suppressed, which candidate injected, and what effect was measured. This is mechanistic interpretability formalized as classical planning.

## Usage Examples

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.poetry.feature_space_poetry import the_domain, problems

# Create planner session (use iterative_dfs_backtracking for scenarios with backtracking)
with gtpyhop.PlannerSession(domain=the_domain, verbose=1,
                            strategy='iterative_dfs_backtracking') as session:
    # Get problem instance
    state, tasks, desc = problems.get_problems()['scenario_0_version_d_star_result']

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
python benchmarking.py feature_space_poetry
```

## Scientific Context

This domain implements the "genuinely novel" use of an HTN planner identified in the architecture analysis:

> "The HTN doesn't plan text; it plans interventions on the model's internal representations. The domain knowledge encoded in methods captures the suppress+inject protocol. Backtracking over candidate features is exactly what was done manually in the melometis experiments -- automating it as HTN search."

The plan itself is a formal model of mechanistic interpretability as planning: "what sequence of feature-level operations redirects the model's rhyme plan?"

## References

- **Architecture 6**: `htn-roles-for-planning-in-poems.md`, Section "TIER 2: Architectures Requiring New (But Plausible) Capabilities"
- **Melometis v1.3.0 Version D Results**: Suppress+inject protocol, 48.3% max redirect, 155M-fold ratio
- **Version D Experimental Data**: `plip-rs/outputs/suppress_inject_sweep.json` (136 pairs, 4 prompts)
- **CLT 426K Resolution**: 425,984 features on Gemma 2 2B, 35 rhyme groups discovered
- **Anthropic "Planning in Poems"**: Anthropic Research, March 2025
- **GTPyhop Documentation**: https://github.com/PCfVW/GTPyhop

---
*Generated 2026-02-18*
