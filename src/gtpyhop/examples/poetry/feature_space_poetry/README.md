# Feature Space Poetry HTN Domain

## Overview

This example demonstrates **Architecture 6: HTN Operates in Feature Space (The Wild One)** from the `htn-roles-for-planning-in-poems.md` analysis. The HTN's state space IS the CLT activation space. Actions are feature-level operations on the residual stream. The "world" is the residual stream at the planning site.

The key insight: the HTN doesn't plan *text*; it plans *interventions on the model's internal representations*. The domain knowledge encoded in methods captures the suppress+inject protocol from melometis. Backtracking over candidate features automates what was done manually in the experiments -- the plan itself becomes a scientific artifact recording the automated intervention.

Three configurations are covered:
- **Gemma 2 2B** (26 layers, CLT 426K): forward planning model. Version D experiments.
- **Llama 3.2 1B** (16 layers, CLT 524K): late selection model. Version L experiments.
- **Gemma 2 2B** (26 layers, CLT 2.5M): word-level planning model. Version D 2.5M experiments.

| Dimension | Other poetry examples | This example |
|-----------|----------------------|--------------|
| State space | Text, rhyme labels | CLT activation space |
| Actions modify | Poem structure | Residual stream & features |
| Plan purpose | Generate poetry | Execute suppress+inject protocol |
| Backtracking over | Rhyme strategies | Injection candidate features |

## Benchmarking Scenarios

### Gemma 2 2B (scenarios 0-3)

Forward planning model, 26 layers, CLT 426K. Source: melometis Version D (`suppress_inject_sweep.json`, 136 pairs). Scenario 0 is **ground truth**; scenarios 1-3 are **counterfactual what-ifs**.

| Scenario | Description | From -> To | Layers (L) | Threshold | Backtracking | Actions | Status |
|----------|-------------|-----------|------------|-----------|-------------|---------|--------|
| `scenario_0_version_d_star_result` | Ground truth | out -> ound | 26 (all) | 0.40 | No | 34 | VALID |
| `scenario_1_cheapest_first` | What if around wasn't first? | out -> ound | 26 (all) | 0.40 | Yes (2 failures) | 34 | VALID |
| `scenario_2_planning_layer_only` | What if only planning layer? | out -> ound | 1 ([16]) | 0.40 | No | 9 | VALID |
| `scenario_3_different_group` | What if different group? | oo -> ound | 2 ([16,25]) | 0.02 | Yes (1 failure) | 10 | VALID |

### Llama 3.2 1B (scenarios 4-7)

Late selection model, 16 layers, CLT 524K. Source: melometis Version L (`suppress_inject_sweep_llama_v2.json`, 44 pairs). 82% of planning features at L15 (last layer). Same HTN protocol, different model = different story.

| Scenario | Description | From -> To | Layers (L) | Threshold | Backtracking | Actions | Status |
|----------|-------------|-----------|------------|-----------|-------------|---------|--------|
| `scenario_4_llama_star_result` | Llama ground truth | ee -> at | 16 (all) | 0.40 | No | 24 | VALID |
| `scenario_5_llama_sat_first` | What if sat before that? | ee -> at | 16 (all) | 0.40 | Yes (1 failure) | 24 | VALID |
| `scenario_6_llama_output_layer` | What if only L15? | ee -> at | 1 ([15]) | 0.40 | No | 9 | VALID |
| `scenario_7_llama_different_group` | What if different group? | at -> ore | 2 ([1,14]) | 0.005 | Yes (2 failures) | 10 | VALID |

### Gemma 2 2B + CLT 2.5M (scenarios 8-11)

Word-level planning model, 26 layers, CLT 2.5M. Source: melometis Version D 2.5M (`outputs/2.5M/suppress_inject_sweep.json`, 264 pairs). Key upgrade: 98,304 features/layer gives word-level resolution (209/209 words ranked #1 in own feature). Same Gemma 2 2B model, finer CLT = word-level control.

| Scenario | Description | From -> To | Layers (L) | Threshold | Backtracking | Actions | Status |
|----------|-------------|-----------|------------|-----------|-------------|---------|--------|
| `scenario_8_version_d_2_5m_star` | 2.5M star result | out -> an | 26 (all) | 0.40 | No | 34 | VALID |
| `scenario_9_2_5m_weakest_first` | What if plan was tried first? | out -> an | 26 (all) | 0.40 | Yes (2 failures) | 34 | VALID |
| `scenario_10_2_5m_planning_layer` | What if only L25? | out -> an | 1 ([25]) | 0.40 | No | 9 | VALID |
| `scenario_11_2_5m_different_group` | What if different group? | oo -> an | 2 ([16,25]) | 0.35 | Yes (1 failure) | 10 | VALID |

### Plan Length Formula

| Layers (L) | Formula | Actions |
|-----------|---------|---------|
| 1 | 1 + 8 | 9 |
| 2 | 2 + 8 | 10 |
| 16 | 16 + 8 | 24 |
| 26 | 26 + 8 | 34 |

Where: `(encode x L) + init + locate + baseline + suppress + inject + measure + evaluate + report`

### Planner Behavior

| Scenario | Greedy | Iterative DFS |
|----------|--------|---------------|
| scenario_0 (around first, P=0.483 >= 0.40) | SUCCESS | SUCCESS |
| scenario_1 (around last, first two fail threshold) | FAIL | SUCCESS |
| scenario_2 (around only, P=0.483 >= 0.40) | SUCCESS | SUCCESS |
| scenario_3 (around second, first fails threshold) | FAIL | SUCCESS |
| scenario_4 (that first, P=0.777 >= 0.40) | SUCCESS | SUCCESS |
| scenario_5 (sat first, fails threshold) | FAIL | SUCCESS |
| scenario_6 (that only, P=0.777 >= 0.40) | SUCCESS | SUCCESS |
| scenario_7 (or/more fail, for succeeds at 0.009 >= 0.005) | FAIL | SUCCESS |
| scenario_8 (can first, P=0.482 >= 0.40) | SUCCESS | SUCCESS |
| scenario_9 (can last, first two fail threshold) | FAIL | SUCCESS |
| scenario_10 (can only, P=0.425 >= 0.40) | SUCCESS | SUCCESS |
| scenario_11 (plan fails, can succeeds at 0.400 >= 0.35) | FAIL | SUCCESS |

Scenarios 1, 3, 5, 7, 9, and 11 require backtracking because the first candidate's measured probability falls below the threshold, causing `a_evaluate_threshold` to fail and triggering the planner to try the next injection candidate.

## Empirical Grounding

### Gemma 2 2B — Version D (from melometis v1.3.0)

**Measured Probabilities** (from `suppress_inject_sweep.json`):

The Version D experiment tested 136 suppress+inject pairs (34 alternative groups x 4 prompts). Feature L22:10243 ("around") was measured on all 4 prompts:

| Prompt | Suppress | P(around) after intervention | Source line |
|--------|----------|------------------------------|-------------|
| -out/about | -out | **48.29%** (star result) | 10138 |
| -out/shout | -out | **33.86%** | 16592 |
| -oo/who | -oo | **5.67%** | 23356 |
| -ow/so | -ow | **3.36%** | 3844 |

Other candidates (L16:7712 "ground", L25:3298 "round") were **not tested** in the Version D sweep -- only one feature per alternative group was tested. Their probabilities are estimated from CLT decoder vector analysis.

**Rhyme Groups:**

| Group | ARPAbet | Key words | Experimental role |
|-------|---------|-----------|-------------------|
| `-out` | AW1-T | about, out, shout | Primary suppression target (2 of 4 Version D prompts) |
| `-ound` | AW1-N-D | around, found, ground, round | Cross-group injection target; L22:10243 achieved 48.3% |
| `-ow` | OW1 | go, grow, know, so, though | Natural group on 1 Version D prompt |
| `-oo` | UW1 | do, new, ou, to, two, who | Natural group on 1 Version D prompt; 157,000x ratio |

**Version D Protocol:**
- **Suppress**: Negative strength on ALL features from natural group across all downstream layers
- **Inject**: Positive strength on single feature from alternative group
- **Result**: 95/136 pairs (70%) show planning-site max above threshold
- **Star result**: "around" (L22:10243) achieved 48.3% redirect probability

### Llama 3.2 1B — Version L

**Measured Probabilities** (from `suppress_inject_sweep_llama_v2.json`):

The Version L experiment tested 44 suppress+inject pairs across 3 prompts. Feature L14:13043 ("that") was measured on 2 prompts:

| Prompt | Suppress | P(that) after intervention |
|--------|----------|---------------------------|
| -ee (tree/free/sea) | -ee | **77.7%** (star result) |
| -oo (blue/dew/new) | -oo | **45.2%** |

Other candidates (L14:6132 "sat") were **estimated** from CLT decoder analysis (cosine 0.32).

**Rhyme Groups:**

| Group | ARPAbet | Key words | Experimental role |
|-------|---------|-----------|-------------------|
| `-ee` | IY1 | he, be, ne, we | Natural group; 82% of features at L15 |
| `-at` | AE1-T | that, sat | Injection target; L14:13043 achieved 77.7% |
| `-ore` | AO1-R | for, or, more | Injection target on -at prompt; L1:5297 at 0.9% |

**Version L Protocol:**
- Same suppress+inject mechanism as Version D
- Key difference: 82% of planning features concentrated at L15 (last layer)
- No forward planning observed (late selection model)
- **Star result**: "that" (L14:13043) achieved 77.7% redirect probability

### Gemma 2 2B + CLT 2.5M — Version D 2.5M

**Measured Probabilities** (from `outputs/2.5M/suppress_inject_sweep.json`):

The Version D 2.5M experiment tested 264 suppress+inject pairs (same protocol, 6x finer CLT). Feature L25:82839 ("can") was measured on 3 prompts:

| Prompt | Suppress | P(can) after intervention |
|--------|----------|--------------------------|
| -out/about | -out | **48.20%** (star result) |
| -out/shout (sailor) | -out | **42.49%** |
| -oo/who | -oo | **40.02%** |

Other candidates (L25:45672 "man", L25:71041 "plan") are **estimated** from 2.5M CLT decoder analysis.

**Rhyme Groups:**

| Group | ARPAbet | Key words | Experimental role |
|-------|---------|-----------|-------------------|
| `-an` | AE1-N | can, man, plan | Word-level injection target; L25:82839 achieved 48.2% |

**Key upgrade over 426K:**
- 98,304 features/layer (vs 16,384) → word-level resolution
- 209/209 words ranked #1 in own dedicated feature (100% specificity)
- 67 rhyme groups discovered (vs 35 at 426K)
- 264 viable pairs (vs 136 at 426K)
- **Star result**: "can" (L25:82839) achieved 48.2% redirect probability with 160-billion-fold spike

## Three-Server Architecture

1. **Local computation** (Initialize, Evaluate, Report)
   - `a_initialize_intervention`: Setup model, tracking structures
   - `a_evaluate_threshold`: Check measured_probability >= probability_threshold (BACKTRACKING TRIGGER)
   - `a_compile_intervention_report`: Assemble complete intervention record

2. **Server 1: inference_server** (Forward Passes & Probability)
   - `a_locate_planning_site`: Find planning site, extract residual stream
   - `a_measure_baseline`: Measure P(from_group) before intervention
   - `a_measure_effect`: Measure P(to_group) after intervention, look up simulated probability

3. **Server 2: clt_server** (CLT Encode/Decode, Suppression & Feature Injection)
   - `a_encode_residual`: Run CLT encoder at one layer
   - `a_suppress_group`: Zero out from_group features, reconstruct residual
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
+-- a_suppress_group("out")                               [clt_server]
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
+-- domain.py       # Domain definition with 9 actions and 5 methods
+-- problems.py     # Initial state definitions (12 scenarios)
+-- __init__.py     # Package initialization with get_problems()
+-- README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 9
- **Methods**: 5 (3 backtracking alternatives for m_find_best_injection)
- **Servers**: 3 (local, inference_server, clt_server)
- **Scenarios**: 12 (4 Gemma 2 2B 426K + 4 Llama 3.2 1B + 4 Gemma 2 2B 2.5M)
- **Rhyme Groups**: 8 (4 Gemma from Version D + 1 from Version D 2.5M + 3 Llama from Version L)

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

### CLT Server Actions (3 actions)
5. **a_encode_residual**: Run CLT encoder at one layer
6. **a_suppress_group**: Zero out from_group features, reconstruct residual
7. **a_inject_feature**: Add decoder vector to residual stream

### Local Computation (2 actions)
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
Scenario 0 replicates the actual Version D star result (L22:10243 "around" at 48.29%). Scenarios 1-3 explore counterfactual departures: different candidate ordering, fewer layers, different suppression group. Scenarios 8-11 repeat this pattern at 2.5M word-level resolution (L25:82839 "can" at 48.20%). The star result probabilities are **measured**; other candidate probabilities are **estimated** from CLT analysis.

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
- **CLT 2.5M Resolution**: 2,555,904 features on Gemma 2 2B, 67 rhyme groups, word-level specificity (209/209)
- **Version D 2.5M Experimental Data**: `plip-rs/outputs/2.5M/suppress_inject_sweep.json` (264 pairs)
- **Anthropic "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)"**: Anthropic Research, March 2025
- **GTPyhop Documentation**: https://github.com/PCfVW/GTPyhop

## Appendix: State Restoration on Backtrack -- Explained

This appendix provides a pedagogical walkthrough of the [State Restoration on
Backtrack](#state-restoration-on-backtrack) mechanism described above, and
discusses what it means for both the mechanistic interpretability (MI) and AI
planning fields.

### The concrete sequence (Scenario 1)

The planner has already suppressed the `-out` group and needs to inject a feature
from the `-ound` group. Three candidates are registered in order: `L25:3298`,
`L16:7712`, `L22:10243`.

```
State S0 (post-suppression, pre-injection):
  residual_stream = "${suppress...}"    # clean post-suppression residual
  injection_history = []
  injection_complete = False
  measured_probability = 0.0

--- TRY 1: inject L25:3298 ---
  a_inject_feature  -> residual_stream gets decoder vector added
  a_measure_effect  -> measured_probability = 0.001
  a_evaluate_threshold -> 0.001 < 0.40 -> returns False -> BACKTRACK

    | GTPyhop restores state to S0 (the deep copy taken before TRY 1 began)

--- TRY 2: inject L16:7712 ---
  a_inject_feature  -> residual_stream gets decoder vector added
                       (on clean S0, NOT on S0 + L25:3298's decoder vector)
  a_measure_effect  -> measured_probability = 0.003
  a_evaluate_threshold -> 0.003 < 0.40 -> returns False -> BACKTRACK

    | GTPyhop restores state to S0 again

--- TRY 3: inject L22:10243 ---
  a_inject_feature  -> residual_stream gets decoder vector added (on clean S0)
  a_measure_effect  -> measured_probability = 0.483
  a_evaluate_threshold -> 0.483 >= 0.40 -> SUCCEEDS
```

### How GTPyhop implements this

The iterative DFS backtracking planner (`seek_plan_iterative_backtracking` in
`main.py`) works with a stack of *continuation tuples*, each containing a
`(state, todo_list, plan, depth)`. When `_refine_task_and_continue_iterative_bt`
encounters a task like `m_find_best_injection` with 3 applicable methods, it
pushes one continuation per method onto the stack -- and each continuation holds
the **same** state reference: the state as it was *before* any method's subtasks
began executing.

When an action is applied (`_apply_action_and_continue_iterative`), it first
creates a fresh `state.copy()` and applies the action to the copy. If the action
fails (returns `False`), nothing is pushed to the stack. The stack then naturally
falls through to the next continuation, which still holds the unmodified state.

The `State.copy()` method is implemented as `copy.deepcopy(self)`, ensuring that
nested structures (dicts, lists, the symbolic `residual_stream` expression) are
fully independent between branches.

### What this brings to the Mechanistic Interpretability field

**State restoration guarantees experimental isolation between candidate
interventions.** This is the central contribution.

In a suppress+inject experiment, the researcher's workflow is:

1. Take a clean post-suppression residual stream
2. Inject one candidate feature's decoder vector
3. Run a forward pass, measure P(target group)
4. If insufficient -- **undo the injection completely** and try another candidate

Step 4 is where things get dangerous in practice. If the injection is not cleanly
undone, the next candidate's measurement is contaminated: you would be measuring
the effect of candidate 2 *on top of* the leftover decoder vector from candidate
1. The MI result would be scientifically invalid.

The HTN planner's deep-copy-on-backtrack makes this **impossible to get wrong**.
The `residual_stream` automatically reverts to its exact post-suppression value.
No manual bookkeeping required.

This has several concrete implications:

- **The plan is a falsifiable experimental protocol.** Each failed backtracking
  path is a hypothesis ("this feature redirects the rhyme plan") that was tested
  and rejected. The final plan records only the successful hypothesis. The plan
  is not just a recipe -- it is a lab notebook.

- **Counterfactual exploration is systematic.** Scenarios 1-3 are "what-if"
  experiments: what if we try the candidates in a different order? What if we
  only encode the planning layer? What if we suppress a different group? The
  planner's search over methods *is* the experiment's search over hypotheses.

- **Reproducibility is structural.** The deep copy guarantees that re-running
  the same scenario always produces the same sequence of attempts and the same
  result, regardless of which candidates fail. There are no hidden side-effects
  leaking between attempts.

- **The portability warning is a genuine scientific concern.** If someone ports
  this domain to a planner that does *not* deep-copy state, the residual stream
  would silently accumulate decoder vectors from failed injections. The reported
  probabilities would be wrong, and the MI conclusions drawn from them would be
  invalid. The warning makes this dependency explicit.

### What this teaches the AI Planning field

**Planning in a non-physical state space, where backtracking = systematic
experimentation.**

Classical AI planning operates on symbolic descriptions of physical worlds:
blocks on a table, trucks delivering packages, robots navigating rooms. The state
variables are things like `on(block_A, block_B)` or `at(truck, city)`. This
example shows that the **same HTN formalism** works when the "world" is a neural
network's internal activation space -- the state variables are
`residual_stream`, `active_features`, `measured_probability`. This is a genuine
extension of where HTN planning has been applied.

Several specific lessons:

- **Backtracking maps to hypothesis testing.** In classical planning,
  backtracking means "that action sequence didn't lead to the goal state, try
  another decomposition." In this domain, it means "that candidate feature didn't
  produce a sufficient probability shift, try another." The formal mechanism is
  identical; the interpretation shifts from *plan repair* to *experimental
  search*. This suggests that any domain where you systematically try
  alternatives and need clean rollback between attempts is a natural fit for HTN
  planning with backtracking.

- **Deep copy semantics are a correctness requirement, not just an optimization
  choice.** Many planners avoid deep copy for performance: they use undo lists,
  state-variable deltas, or immutable data structures. The feature space domain
  shows a case where none of these lightweight alternatives would be obviously
  correct without careful engineering. The `residual_stream` is a nested symbolic
  expression that accumulates structure with each injection. An undo list would
  need to know exactly what to undo. An immutable approach would need structural
  sharing. GTPyhop's `copy.deepcopy` is the simplest correct implementation --
  but at a cost (26 layers of encoded features get copied on every backtrack).
  This creates a design tension between **correctness** and **efficiency** that
  is exactly the kind of tradeoff the planning community studies.

- **The plan as a scientific artifact.** In classical planning, a plan is a
  recipe: "pick up A, put A on B, pick up C." In this domain, the plan is a
  scientific protocol: "encode 26 layers, suppress -out features, inject
  L22:10243 at strength 1.0, measure P(-ound) = 48.3%, conclude threshold met."
  The plan documents exactly which interventions were performed, in what order, on
  what state. This is a novel use of planning where the output is not an
  instruction sequence for an agent to *do* something -- it is a formal record of
  an experiment that was *conducted*.

- **The greedy planner's failure is informative.** Scenarios 1, 3, 5, 7, 9, and 11 fail with
  the greedy strategy because it commits irrevocably to the first method. In MI
  terms: if the first candidate feature you try doesn't work, and your planner
  cannot backtrack, your experiment stops. The difference between
  `iterative_greedy` (FAIL) and `iterative_dfs_backtracking` (SUCCESS) on the
  same scenario is a direct demonstration that **systematic search matters for
  MI**, just as it matters for classical planning.

---
*Generated 2026-02-18, appendix added 2026-02-19, Llama scenarios added 2026-02-20, 2.5M scenarios added 2026-02-23*
