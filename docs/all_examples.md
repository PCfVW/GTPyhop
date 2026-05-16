# GTPyhop 1.9.7 HTN Planning Examples

This document provides pedagogical details about all HTN Planning examples included with GTPyhop 1.9.7. Each example demonstrates different aspects of hierarchical task network planning, from basic concepts to advanced techniques.

## Table of Contents

1. [Learning Path](#-learning-path)
2. [Simple Examples](#-simple-examples-basic-concepts)
3. [Complex Block World Examples](#-complex-block-world-examples-advanced-scenarios)
4. [IPC 2020 Total Order Examples](#-ipc-2020-total-order-examples)
5. [MCP Orchestration Examples](#-mcp-orchestration-examples)
6. [Memory Tracking Examples](#-memory-tracking-examples-180)
7. [Poetry Examples](#-poetry-examples-190)
8. [Control Arena Protocol Examples](#-control-arena-protocol-examples-194)
9. [Cybersecurity Attack Planning Example](#-cybersecurity-attack-planning-example-195)
10. [Android: Netrunner Run Planning Example](#-android-netrunner-run-planning-example-196)
11. [Trunk Thumper Game-AI Examples](#-trunk-thumper-game-ai-examples-196)
12. [Colt Express Game-AI Examples](#-colt-express-game-ai-examples-197)
13. [Running the Examples](#-running-the-examples)
14. [Pedagogical Recommendations](#-pedagogical-recommendations)

---

## Learning Path

**Recommended order for learning:**
1. **simple_htn.py** - Start here for basic HTN concepts
2. **simple_hgn.py** - Learn goal-oriented planning
3. **backtracking_htn.py** - Understand method failure and backtracking
4. **simple_htn_acting_error.py** - Error handling and replanning
5. **logistics_hgn.py** - Multi-goal planning scenarios
6. **pyhop_simple_travel_example.py** - Classic Pyhop compatibility
7. **blocks_htn/** - Advanced HTN methods
8. **blocks_hgn/** - Advanced goal decomposition
9. **blocks_gtn/** - Mixed task/goal planning
10. **blocks_goal_splitting/** - Built-in goal splitting methods

---

## Simple Examples (Basic Concepts)

### simple_htn.py - Basic Hierarchical Task Networks
**Purpose:** Introduction to HTN planning fundamentals
**Domain:** Travel planning (home to park via taxi/walking)
**Key Learning Points:**
- Domain creation and state representation
- Action definitions with preconditions and effects
- Task method decomposition
- Hierarchical planning from high-level tasks to primitive actions
- Verbosity levels and debugging output

**Core Concepts Demonstrated:**
- **Actions:** `walk`, `call_taxi`, `ride_taxi`, `pay_driver`
- **Tasks:** `travel`, `travel_by_foot`, `travel_by_taxi`
- **State Variables:** locations, cash, debts
- **Planning Strategy:** Decompose travel task into appropriate subtasks

**Educational Value:** Perfect starting point for understanding how HTN planning breaks down complex tasks into manageable subtasks.

### simple_hgn.py - Basic Hierarchical Goal Networks
**Purpose:** Introduction to goal-oriented planning
**Domain:** Same travel domain as simple_htn but using goals
**Key Learning Points:**
- Goal vs. task distinction
- Goal method definitions
- State-based goal achievement
- Goal decomposition strategies

**Core Concepts Demonstrated:**
- **Goals:** `loc` (location goals)
- **Goal Methods:** Methods that achieve specific state conditions
- **Comparison:** Shows how the same domain can be modeled with goals vs. tasks

**Educational Value:** Demonstrates the difference between task-oriented and goal-oriented planning approaches.

### backtracking_htn.py - Backtracking Demonstration
**Purpose:** Understanding method failure and alternative exploration
**Domain:** Simple abstract domain with multiple method choices
**Key Learning Points:**
- Method failure handling
- Backtracking through alternative methods
- Search space exploration
- Planning strategy comparison (recursive DFS vs. iterative greedy vs. iterative DFS backtracking)

**Core Concepts Demonstrated:**
- **Multiple Methods:** Several methods for the same task
- **Failure Conditions:** Methods that can fail under certain conditions
- **Backtracking:** How the planner explores alternatives
- **Strategy Differences:** Recursive DFS and iterative DFS backtracking find plans; iterative greedy fails when the first method's path is a dead end

**Educational Value:** Critical for understanding how HTN planners handle uncertainty and multiple solution paths. See also the `backtracking_poetry` example (1.9.0+) for a more realistic backtracking scenario.

### simple_htn_acting_error.py - Error Handling Patterns
**Purpose:** Execution failures and replanning strategies
**Domain:** Travel domain with potential execution failures
**Key Learning Points:**
- Action execution failures
- Replanning after failures
- Robust planning strategies
- Error recovery mechanisms

**Educational Value:** Shows how real-world planning systems must handle execution uncertainties.

### logistics_hgn.py - Multi-Goal Planning
**Purpose:** Complex logistics domain with multiple objectives
**Domain:** Package delivery with trucks and airplanes
**Key Learning Points:**
- Multi-goal planning scenarios
- Resource management (trucks, planes, packages)
- Spatial reasoning (cities, airports)
- Goal interaction and dependencies

**Core Concepts Demonstrated:**
- **Actions:** `drive_truck`, `fly_airplane`, `load_truck`, `load_airplane`, `unload_truck`, `unload_airplane`
- **Goals:** Package location goals
- **Resources:** Trucks, airplanes, packages, locations

**Educational Value:** Demonstrates how HTN planning scales to realistic logistics problems.

### pyhop_simple_travel_example.py - Classic Pyhop Compatibility
**Purpose:** Compatibility with original Pyhop examples
**Domain:** Simple travel domain from original Pyhop
**Key Learning Points:**
- Migration from Pyhop to GTPyhop
- Backward compatibility
- Classic HTN planning patterns

**Educational Value:** Helps users familiar with Pyhop understand GTPyhop's enhanced capabilities.

---

## Complex Block World Examples (Advanced Scenarios)

### blocks_htn/ - Advanced Hierarchical Task Networks
**Purpose:** Complex HTN methods for blocks world manipulation
**Domain:** Classic blocks world with stacking operations
**Key Learning Points:**
- Complex task decomposition strategies
- Block manipulation primitives
- Stack management
- Advanced HTN method design

**Core Concepts Demonstrated:**
- **Actions:** `pickup`, `putdown`, `stack`, `unstack`
- **Tasks:** `move_blocks`, `get_block`, `put_block`
- **Complex Methods:** Multi-step block manipulation strategies
- **State Management:** Block positions, clear blocks, table space

**Educational Value:** Shows how HTN planning handles complex manipulation domains with intricate preconditions.

### blocks_hgn/ - Advanced Hierarchical Goal Networks
**Purpose:** Goal-oriented approach to blocks world planning
**Domain:** Blocks world using goal decomposition
**Key Learning Points:**
- Goal decomposition in complex domains
- Multi-goal achievement strategies
- Goal interaction management
- State-based planning

**Core Concepts Demonstrated:**
- **Goals:** Block position goals, stacking goals
- **Goal Methods:** Methods to achieve specific block configurations
- **Goal Dependencies:** How achieving one goal affects others

**Educational Value:** Demonstrates sophisticated goal-oriented planning in a well-understood domain.

### blocks_gtn/ - Goal Task Networks (Mixed Planning)
**Purpose:** Near-optimal blocks world planning algorithm
**Domain:** Blocks world with mixed task/goal approach
**Key Learning Points:**
- Hybrid task/goal planning
- Optimal planning strategies
- Algorithm implementation from research literature
- Performance optimization

**Reference:** Based on Gupta & Nau (1992) "On the complexity of blocks-world planning"

**Educational Value:** Shows how research algorithms can be implemented in GTPyhop for optimal performance.

### blocks_goal_splitting/ - Built-in Goal Decomposition
**Purpose:** Using GTPyhop's built-in goal splitting methods
**Domain:** Blocks world with automatic goal decomposition
**Key Learning Points:**
- Built-in `m_split_multigoal` method
- Automatic goal ordering
- Deleted-condition interactions
- Limitations of naive goal splitting

**Core Concepts Demonstrated:**
- **Multigoal Splitting:** Automatic decomposition of complex goals
- **Sequential Achievement:** Achieving goals one by one
- **Interaction Problems:** How goals can interfere with each other

**Educational Value:** Illustrates both the power and limitations of automatic goal decomposition methods.

---

## IPC 2020 Total Order Examples

### Blocksworld-GTOHP and Childsnack Domains
**Purpose:** Competition-grade planning domains
**Location:** `src/gtpyhop/examples/ipc-2020-total-order/`
**Key Learning Points:**
- Competition-standard domain modeling
- Performance benchmarking
- Scalable planning problems
- Real-world domain complexity

**Domains Available:**
- **Blocksworld-GTOHP:** Advanced blocks world with competition problems
- **Childsnack:** Resource management in childcare setting

**Educational Value:** Shows how GTPyhop handles competition-grade planning problems.

**Documentation:** [Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/benchmarking_quickstart.md)

---

## MCP Orchestration Examples

**Location:** `src/gtpyhop/examples/mcp-orchestration/`

MCP (Model Context Protocol) is an open-source standard from Anthropic for connecting AI applications to external systems.

### Bio-Opentrons PCR Workflow (1.6.0+)
**Purpose:** PCR workflow automation with Opentrons Flex robots
**Location:** `mcp-orchestration/bio_opentrons/`
**Scenarios:** 6 scenarios (4 to 96 samples)

**Key Learning Points:**
- Multi-server robot coordination
- Dynamic sample scaling
- Laboratory automation workflows

**Core Concepts Demonstrated:**
- **Three-Server Architecture:** Deck, pipette, and protocol servers
- **Actions (18):** Tip handling, liquid transfers, thermal cycling
- **Methods (15):** PCR workflow orchestration

**Documentation:** [Bio-Opentrons README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/bio_opentrons/README.md)

### Cross-Server Orchestration (1.5.0+)
**Purpose:** Cross-server coordination with HTN planning
**Location:** `mcp-orchestration/cross_server/`
**Scenarios:** 2 scenarios (9-15 actions)

**Key Learning Points:**
- Multi-server coordination using HTN planning
- Robot manipulation task decomposition
- Cross-server action orchestration

**Core Concepts Demonstrated:**
- **Three-Server Architecture:** HTN planning, robot gripper, motion planning
- **Actions (9):** Server initialization, gripper control, motion planning
- **Methods (5):** Pick-and-place orchestration

**Documentation:** [Cross-Server README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/cross_server/README.md)

### Drug Target Discovery (1.7.0+)
**Purpose:** Drug target discovery pipeline using OpenTargets platform
**Location:** `mcp-orchestration/drug_target_discovery/`
**Scenarios:** 3 scenarios (8 actions each)

**Key Learning Points:**
- Scientific workflow orchestration
- External platform integration
- Drug discovery pipelines

**Core Concepts Demonstrated:**
- **Workflow Stages:** Data retrieval, analysis, ranking
- **Actions (8):** Query, analyze, rank targets
- **Methods (3):** Discovery pipeline orchestration

**Documentation:** [Drug Target Discovery README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/drug_target_discovery/README.md)

### Omega HDQ DNA Extraction (1.6.0+)
**Purpose:** DNA extraction workflow with Opentrons Flex 96-channel
**Location:** `mcp-orchestration/omega_hdq_dna_bacteria_flex_96_channel/`
**Scenarios:** 3 scenarios (89-129 actions)

**Key Learning Points:**
- Complex laboratory automation
- Magnetic bead purification protocols
- Four-server architecture coordination

**Core Concepts Demonstrated:**
- **Four-Server Architecture:** Deck, pipette, magnetic, protocol servers
- **Actions (17):** Magnetic separation, wash cycles, elution
- **Methods (14):** DNA extraction orchestration

**Documentation:** [Omega HDQ README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/omega_hdq_dna_bacteria_flex_96_channel/README.md)

### TNF Cancer Modelling (1.5.0+)
**Purpose:** Multiscale cancer modeling with systems biology integration
**Location:** `mcp-orchestration/tnf_cancer_modelling/`
**Scenarios:** 1 scenario (12 actions)

**Key Learning Points:**
- Scientific workflow orchestration
- Multi-scale biological modeling
- Integration with external tools (Neko, SBML, PhysiCell)

**Core Concepts Demonstrated:**
- **Workflow Stages:** Network creation, Boolean model, SBML, simulation
- **Actions (12):** Network creation, analysis, model building, simulation
- **Methods (3):** Workflow orchestration

**Documentation:** [TNF Cancer Modelling README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/tnf_cancer_modelling/README.md)

---

## Memory Tracking Examples (1.8.0+)

**Location:** `src/gtpyhop/examples/memory_tracking/`

These examples demonstrate GTPyhop's memory tracking capabilities using the `psutil` library.

### Scalable Data Processing
**Purpose:** Memory scaling via data volume
**Location:** `memory_tracking/scalable_data_processing/`
**Scenarios:** 20 scenarios (10K to 1M items)

**Key Learning Points:**
- Memory behavior with varying data sizes
- Data type impact on memory (int, string, dict)
- Transformation passes and accumulation effects

**Core Concepts Demonstrated:**
- **Data Types:** `int` (~28 bytes), `string` (~500 bytes), `dict` (~1KB+)
- **Configuration:** `num_transforms`, `accumulate`, `cleanup`
- **Memory Range:** 1 MB to 300+ MB

**Use Case:** Understanding how state payload size affects memory consumption.

**Documentation:** [Scalable Data Processing README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_data_processing/README.md)

### Scalable Recursive Decomposition
**Purpose:** Memory scaling via structural complexity
**Location:** `memory_tracking/scalable_recursive_decomposition/`
**Scenarios:** 12 scenarios (depth 4 to 14)

**Key Learning Points:**
- Memory behavior with varying recursion depths
- Exponential task growth (2^k tasks for depth k)
- HTN planning complexity (PSPACE-complete)

**Core Concepts Demonstrated:**
- **Binary Recursive Decomposition:** Depth k yields 2^k leaf tasks
- **Payload Scaling:** 100B to 100KB per task
- **Memory Formula:** `2^depth x payload_size`

**Reference:** Based on Alford et al. (2015) "Tight Bounds for HTN Planning"

**Use Case:** Understanding how HTN decomposition structure affects memory consumption.

**Documentation:** [Scalable Recursive Decomposition README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md)

### Running Memory Benchmarks

```bash
cd src/gtpyhop/examples/memory_tracking

# Run data processing scenarios
python benchmarking.py --example data

# Run recursive decomposition scenarios
python benchmarking.py --example recursive

# Accurate peak measurement
python benchmarking.py --example recursive --scenario scenario_10 \
    --disable-gc --sampling-interval 0.001

# List available scenarios
python benchmarking.py --list-scenarios --example recursive
```

**Documentation:** [Memory Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/benchmarking_quickstart.md)

---

## Poetry Examples (1.9.0+)

**Location:** `src/gtpyhop/examples/poetry/`

These examples demonstrate HTN-planned poetry generation where the planner produces structural plans (form, rhyme scheme, meter constraints) and leaf-level actions are delegated to external MCP servers for text generation and phonetic verification. The collection is motivated by Anthropic's "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" (March 2025) discovery that Claude 3.5 Haiku plans ahead when writing rhyming poetry.

**Progression:** The seven examples form a progression. Examples 1-5 model text-generation poetry workflows; examples 6-7 model the underlying planning mechanisms and feature-space interventions:

| # | Example | Key Extension | Actions | Methods | Strategy |
|---|---------|---------------|---------|---------|----------|
| 1 | Structured Poetry | Baseline (select → generate → verify) | 6 | 8 | Any |
| 2 | Backtracking Poetry | Strict/relaxed methods with backtracking | 7 | 9 | Backtracking |
| 3 | Candidate Planning Poetry | Multi-candidate target selection pipeline | 8 | 8 | Any |
| 4 | Bidirectional Planning Poetry | Decomposed backward line construction | 7 | 8 | Any |
| 5 | Replanning Poetry | Post-generation evaluation and revision | 8 | 10 | Backtracking |
| 6 | Formal Mechanism Poetry | Three planning mechanisms from the paper | 7 | 6 | Any |
| 7 | Feature Space Poetry | Feature-space interventions with measured data | 9 | 5 | Backtracking |

### 1. Structured Poetry
**Purpose:** HTN-planned poetry with MCP-delegated generation
**Location:** `poetry/structured_poetry/`
**Scenarios:** 6 scenarios (couplet, limerick, haiku, sonnet)

**Key Learning Points:**
- Hierarchical decomposition of poetic forms
- Forward planning for rhyme target selection
- Backward planning for constrained text generation
- MCP server delegation for phonetics and LLM generation

**Core Concepts Demonstrated:**
- **Form Hierarchy:** `m_write_poem` → `m_compose_<form>` → `m_write_rhymed_line` / `m_write_free_line`
- **Actions (6):** `a_initialize_poem`, `a_select_rhyme_target`, `a_generate_line`, `a_generate_line_no_rhyme`, `a_verify_line`, `a_assemble_poem`
- **Methods (8):** One method per task (no backtracking needed)

**Plan Lengths:** Couplet: 8, Limerick: 17, Haiku: 8, Sonnet: 44

**Educational Value:** Demonstrates the core HTN decomposition pattern for poetry generation. Serves as the baseline for the four extensions that follow.

### 2. Backtracking Poetry
**Purpose:** HTN backtracking for rhyme selection with multiple methods
**Location:** `poetry/backtracking_poetry/`
**Scenarios:** 3 scenarios (couplet, limerick, haiku)

**Key Learning Points:**
- Multiple methods for the same task (strict vs. relaxed rhyme selection)
- How iterative greedy planning fails when the first method leads to a dead end
- How iterative DFS backtracking recovers by trying alternative methods
- Strategy comparison across all three planning strategies

**Core Concepts Demonstrated:**
- **Two Methods for `m_write_rhymed_line`:**
  - `m_write_rhymed_line_strict` (tried first; uses exact rhyme; fails when rhyme label has 2+ lines)
  - `m_write_rhymed_line_relaxed` (fallback; uses near-rhyme; always succeeds)
- **Backtracking Trigger:** In AABBA limerick, line 4 is the 3rd use of label A → strict selection fails → planner must backtrack to relaxed method
- **Actions (7):** Same as structured poetry plus `a_select_rhyme_target_strict` and `a_select_rhyme_target_relaxed` (replacing the single `a_select_rhyme_target`)

**Strategy Comparison:**

| Strategy | Couplet (8) | Limerick (17) | Haiku (8) |
|----------|:-----------:|:-------------:|:---------:|
| Recursive DFS | Finds plan | Finds plan | Finds plan |
| Iterative greedy | Finds plan | **Fails** | Finds plan |
| Iterative DFS BT | Finds plan | Finds plan | Finds plan |

**Educational Value:** The primary example for understanding the practical difference between the three planning strategies. Demonstrates a realistic scenario where backtracking is required for correctness.

### 3. Candidate Planning Poetry
**Purpose:** Multi-candidate rhyme target selection pipeline
**Location:** `poetry/candidate_planning_poetry/`
**Scenarios:** 3 scenarios (couplet, limerick, haiku)

**Key Learning Points:**
- Replacing a single action with a multi-step pipeline
- Modeling the LLM's simultaneous consideration of multiple end-words
- Forward planning with candidate generation, ranking, and commitment

**Core Concepts Demonstrated:**
- **3-Action Pipeline for rhyme selection:** `a_generate_rhyme_candidates` → `a_rank_candidates` → `a_commit_rhyme_target` (replacing the single `a_select_rhyme_target`)
- **Actions (8):** 6 from structured poetry + 3 candidate pipeline actions - 1 original selection action
- **Methods (8):** One method per task (no backtracking needed)

**Plan Lengths:** Couplet: 12, Limerick: 27, Haiku: 8, Sonnet: 72

**Educational Value:** Shows how a single action can be decomposed into a more detailed pipeline to model the underlying cognitive process more faithfully.

### 4. Bidirectional Planning Poetry
**Purpose:** Decomposed backward line construction
**Location:** `poetry/bidirectional_planning_poetry/`
**Scenarios:** 3 scenarios (couplet, limerick, haiku)

**Key Learning Points:**
- Splitting line generation into backward transition planning and forward surface text generation
- Modeling the LLM's backward reasoning from the planned end-word to determine intermediate words
- Two-step line construction: structural skeleton → fluent text

**Core Concepts Demonstrated:**
- **2-Action Line Generation:** `a_plan_transition` (backward: target word → structural skeleton) + `a_generate_surface_text` (forward: skeleton → fluent text), replacing the single `a_generate_line`
- **Actions (7):** 6 from structured poetry + 2 decomposed actions - 1 original generation action
- **Methods (8):** One method per task (no backtracking needed)

**Plan Lengths:** Couplet: 10, Limerick: 22, Haiku: 8, Sonnet: 58

**Educational Value:** Models the paper's finding that the LLM builds a structural skeleton before generating fluent text — the word "like" in "His hunger was like a starving rabbit" is determined by backward reasoning from "rabbit".

### 5. Replanning Poetry
**Purpose:** Post-generation evaluation and steering/revision
**Location:** `poetry/replanning_poetry/`
**Scenarios:** 3 scenarios (couplet, limerick, haiku)

**Key Learning Points:**
- Adding an evaluation step after generation that may trigger replanning
- Using HTN backtracking to model line revision with a steered target word
- How action-level failure triggers method-level backtracking at the evaluation level
- Deterministic revision triggers computed from the rhyme scheme

**Core Concepts Demonstrated:**
- **Two Methods for `m_evaluate_and_replan`:**
  - `m_accept_line` (tried first; `a_evaluate_line` fails if line needs revision)
  - `m_revise_line` (fallback; `a_steer_target` → `a_generate_line` → `a_verify_line`)
- **Backtracking Trigger:** `a_evaluate_line` fails for lines in `lines_requiring_revision` — subsequent uses of each rhyme label need revision
- **Actions (8):** 6 from structured poetry + `a_evaluate_line` + `a_steer_target`
- **Methods (10):** 8 from structured poetry + `m_accept_line` + `m_revise_line`

**Strategy Comparison:**

| Strategy | Couplet (12) | Limerick (28) | Haiku (8) |
|----------|:------------:|:-------------:|:---------:|
| Recursive DFS | Finds plan | Finds plan | Finds plan |
| Iterative greedy | **Fails** | **Fails** | Finds plan |
| Iterative DFS BT | Finds plan | Finds plan | Finds plan |

**Plan Lengths:** Couplet: 12, Limerick: 28, Haiku: 8, Sonnet: 72

**Educational Value:** Models the paper's finding that injecting an alternative planned word causes the model to restructure the entire line in 70% of test poems. Also demonstrates that backtracking can be required at different decomposition levels — compare with backtracking_poetry which backtracks at the line composition level.

### 6. Formal Mechanism Poetry
**Purpose:** Three planning mechanisms from Anthropic's "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" paper as explicit HTN decompositions
**Location:** `poetry/formal_mechanism_poetry/`
**Scenarios:** 3 scenarios (full mechanism, commitment focus, three-stage)

**Key Learning Points:**
- Separating pre-commitment candidate generation from verified commitment
- Couplet commitment for multi-line rhyme coordination
- How multiple methods can exist for a task without requiring backtracking (if candidate ordering is favorable)

**Core Concepts Demonstrated:**
- **Three Mechanisms from the Paper:**
  - Candidate activation: generate multiple end-word candidates
  - Commitment: verify and commit to a single candidate
  - Couplet commitment: coordinate rhyme targets across line pairs
- **Three Methods for `m_select_end_word`:** Try each candidate in order; `a_verify_phonetic_match` fails for weak candidates
- **Actions (7):** Candidate generation, phonetic verification, commitment, line writing
- **Methods (6):** Three try-methods for candidate selection, plus form-level decomposition

**Plan Lengths:** Full mechanism: 19, Commitment focus: 7, Three-stage: 13

**Educational Value:** All current scenarios succeed with any strategy because the strongest candidate is tried first. The domain has backtracking capability (3 methods for `m_select_end_word`) but the current scenarios don't exercise it — compare with feature_space_poetry where candidate reordering forces backtracking.

### 7. Feature Space Poetry
**Purpose:** HTN planning for feature-space interventions on neural network representations
**Location:** `poetry/feature_space_poetry/`
**Scenarios:** 12 scenarios (4 Gemma 2 2B 426K + 4 Llama 3.2 1B 524K + 4 Gemma 2 2B 2.5M)

**Key Learning Points:**
- Planning in CLT activation space rather than text space
- Probability-based backtracking using measured experimental data
- Ground truth + counterfactual scenario structure
- Three-server coordination (local, inference, CLT)
- Cross-model comparison (forward planning vs. late selection)
- Cross-resolution comparison (426K vs. 2.5M CLT on same model)

**Core Concepts Demonstrated:**
- **Suppress+Inject Protocol:** Suppress natural rhyme group features, inject alternative group feature, measure probability shift
- **Probability-Based Backtracking:** `a_evaluate_threshold` compares `measured_probability` against `probability_threshold`; failure triggers backtracking to the next candidate
- **Three Methods for `m_find_best_injection`:** Each tries a different CLT feature; `a_evaluate_threshold` fails when the injected feature's probability is below threshold
- **Actions (9):** Initialize, locate planning site, measure baseline, encode layers, suppress features, inject feature, measure effect, evaluate threshold, compile report
- **Methods (5):** Three try-methods for candidate selection, plus workflow orchestration

**Scenario Structure:**

Gemma 2 2B (scenarios 0-3): forward planning model, 26 layers, CLT 426K

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 0: Version D star result | Ground truth (what actually happened) | 34 | No | SUCCESS |
| 1: Cheapest first | What if candidates were reordered? | 34 | Yes (2 failures) | **FAIL** |
| 2: Planning layer only | What if only 1 layer was needed? | 9 | No | SUCCESS |
| 3: Different group | What if we redirected oo→ound? | 10 | Yes (1 failure) | **FAIL** |

Llama 3.2 1B (scenarios 4-7): late selection model, 16 layers, CLT 524K

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 4: Llama star result | Ground truth (ee→at, "that" at 77.7%) | 24 | No | SUCCESS |
| 5: Llama sat first | What if "sat" was tried before "that"? | 24 | Yes (1 failure) | **FAIL** |
| 6: Llama output layer | What if only L15 was encoded? | 9 | No | SUCCESS |
| 7: Llama different group | What if we redirected at→ore? | 10 | Yes (2 failures) | **FAIL** |

Gemma 2 2B + CLT 2.5M (scenarios 8-11): word-level planning model, 26 layers, CLT 2.5M

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 8: 2.5M star result | Ground truth (out→an, "can" at 48.2%) | 34 | No | SUCCESS |
| 9: 2.5M weakest first | What if "plan" was tried before "can"? | 34 | Yes (2 failures) | **FAIL** |
| 10: 2.5M planning layer | What if only L25 was encoded? | 9 | No | SUCCESS |
| 11: 2.5M different group | What if we redirected oo→an? | 10 | Yes (1 failure) | **FAIL** |

**Educational Value:** Scenario 0 anchors the domain in reality (the actual Version D experiment result), making scenarios 1-3 pedagogically meaningful as counterfactual explorations. Scenarios 4-7 replicate the same protocol on Llama 3.2 1B (Version L), demonstrating that the HTN domain generalizes across models with different planning architectures. Scenarios 8-11 repeat the pattern with CLT 2.5M (98,304 features/layer), demonstrating word-level precision on the same Gemma 2 2B model. Probability data comes from measured experimental sweeps (`suppress_inject_sweep.json` for Gemma 426K, `suppress_inject_sweep_llama_v2.json` for Llama, `outputs/2.5M/suppress_inject_sweep.json` for Gemma 2.5M), not artificial thresholds.

### Running the Poetry Benchmarks

```bash
cd src/gtpyhop/examples/poetry

# List all available poetry domains
python benchmarking.py --list-domains

# Examples 1, 3, 4, 6 work with default strategy
python benchmarking.py structured_poetry
python benchmarking.py candidate_planning_poetry
python benchmarking.py bidirectional_planning_poetry
python benchmarking.py formal_mechanism_poetry

# Examples 2, 5, 7 require a backtracking strategy
python benchmarking.py backtracking_poetry --strategy recursive_dfs
python benchmarking.py replanning_poetry --strategy iterative_dfs_backtracking
python benchmarking.py feature_space_poetry --strategy iterative_dfs_backtracking
```

**Documentation:** [Poetry Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/benchmarking_quickstart.md)

---

## Control Arena Protocol Examples (1.9.4+)

These examples formalize **AI safety micro-protocols** from the [Control Arena](https://github.com/UKGovernmentBEIS/control-arena) framework (Greenblatt et al. 2024) using GTPyhop HTN planning. Control Arena designs protocols that prevent unsafe actions by AI systems, even if those systems are misaligned. A micro-protocol orchestrates an untrusted model, a monitor, and routing logic (accept vs. defer) — mapped to GTPyhop actions, methods, and backtracking.

All three examples use `MCP_Tool: None` (purely symbolic, no external MCP servers).

**Overview:** [Control Arena Protocols README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/control_arena_protocols/README.md)

### 1. Defer to Trusted Protocol

**Purpose:** Model the simplest micro-protocol: propose output, monitor suspiciousness, accept if low or defer to trusted model if high.

**Key Mechanism:** Backtracking at the routing decision. Two methods compete for `m_route_output`: `m_accept_if_low_suspicion` decomposes to `a_accept_output` (which fails if suspicion > threshold), and `m_defer_to_trusted_fallback` always succeeds as the backtracking fallback.

| Scenario | Suspicion | Threshold | Outcome | Actions | Greedy |
|----------|-----------|-----------|---------|---------|--------|
| 1: low suspicion | 0.2 | 0.7 | Accept | 5 | SUCCESS |
| 2: high suspicion | 0.9 | 0.7 | Defer | 5 | **FAIL** |
| 3: at threshold | 0.7 | 0.7 | Accept | 5 | SUCCESS |
| 4: just above | 0.71 | 0.7 | Defer | 5 | **FAIL** |
| 5: tight threshold | 0.4 | 0.3 | Defer | 5 | **FAIL** |
| 6: loose threshold | 0.4 | 0.9 | Accept | 5 | SUCCESS |

**Domain:** 6 actions, 4 methods (2 for `m_route_output`), 6 scenarios, 48 doctests.

**Educational Value:** Demonstrates how HTN backtracking naturally models protocol routing decisions. The greedy planner fails on defer scenarios because it commits to the accept method and cannot recover — illustrating why backtracking is essential for protocols with conditional gates.

### 2. Defer to Resample Protocol

**Purpose:** Extend Defer to Trusted with recursive multi-sample generation. When suspicion is high, generate additional samples instead of immediately deferring. Accept the first low-suspicion sample, or defer after exhausting the sample budget.

**Key Mechanism:** Recursive method decomposition combined with backtracking. `m_resample_loop` returns a decomposition containing `m_route_or_resample` with an incremented sample counter (recursive self-reference). Three methods compete for `m_route_or_resample`: accept, resample (recursive), defer (fallback).

| Scenario | Scores | Max | Threshold | Outcome | Actions | Greedy |
|----------|--------|-----|-----------|---------|---------|--------|
| 1: first accepted | [0.2] | 3 | 0.7 | Accept sample 0 | 5 | SUCCESS |
| 2: second accepted | [0.9, 0.3] | 3 | 0.7 | Accept sample 1 | 7 | **FAIL** |
| 3: third accepted | [0.9, 0.8, 0.4] | 3 | 0.7 | Accept sample 2 | 9 | **FAIL** |
| 4: all high defer | [0.9, 0.8, 0.85] | 3 | 0.7 | Defer | 9 | **FAIL** |
| 5: single sample | [0.9] | 1 | 0.7 | Defer | 5 | **FAIL** |
| 6: five samples | [0.9, 0.8, 0.85, 0.75, 0.3] | 5 | 0.7 | Accept sample 4 | 13 | **FAIL** |

**Domain:** 6 actions, 5 methods (3 for `m_route_or_resample`), 6 scenarios, 40 doctests.

**Educational Value:** Demonstrates recursive HTN decomposition for variable-length plans, mirroring the Bio-Opentrons pattern where loop counts depend on configuration. The plan length formula `2*S + 3` (S = samples tried) shows how recursive depth maps to plan size.

### 3. Adversarial Protocol (1.9.4 baseline, extended in 1.9.7)

**Version note**: The Adversarial Protocol shipped in 1.9.4 with 8 scenarios, 7 actions, 7 methods covering honest-vs-attack routing with calibrated subtlety-based detection rates. It was **extended in 1.9.7** with three additions, each marked below in its corresponding section:
- nested-dict detection-rate schema enabling **threat-model variety** (3 new threat types)
- the **`[EXPECTED_EFFECT]` marker** (first use in the `control_arena_protocols/` collection)
- a **negative-control scenario** demonstrating why the marker is load-bearing

**Purpose:** Extend Defer to Trusted with adversarial analysis. The untrusted model may operate honestly or embed a side task with varying subtlety. A monitor maps `(threat_model, subtlety)` to suspicion via nested calibrated detection rates. Analysis identifies whether the protocol catches attacks across different threat models (code sabotage, data poisoning, research sabotage).

**Key Mechanism:** Method alternatives for output generation (`m_honest_output` vs. `m_attack_output`, deterministic per scenario) combined with backtracking at routing. The monitor's nested `detection_rates: Dict[threat_model, Dict[subtlety, float]]` is the symbolic model's calibration point. The `[EXPECTED_EFFECT]` tag (first use in this collection, added in 1.9.7) records downstream side-task firing on `a_accept_output`.

#### Original 8 scenarios (1.9.4 baseline; threat_model = 'generic' or 'none')

| Scenario | Mode | Subtlety | Suspicion | Threshold | Outcome | Security |
|----------|------|----------|-----------|-----------|---------|----------|
| 1: honest accepted | Honest | - | 0.10 | 0.7 | Accept | SAFE |
| 2: obvious caught | Attack | obvious | 0.95 | 0.7 | Defer | SAFE |
| 3: subtle evades | Attack | subtle | 0.25 | 0.7 | Accept | **VULNERABILITY** |
| 4: subtle caught tight | Attack | subtle | 0.25 | 0.2 | Defer | SAFE |
| 5: moderate caught | Attack | moderate | 0.60 | 0.5 | Defer | SAFE |
| 6: moderate evades | Attack | moderate | 0.60 | 0.7 | Accept | **VULNERABILITY** |
| 7: honest tight | Honest | - | 0.10 | 0.05 | Defer | OVER-SENSITIVE |
| 8: obvious loose | Attack | obvious | 0.95 | 0.99 | Accept | **VULNERABILITY** |

#### Threat-model variety scenarios (added in 1.9.7)

| Scenario | Threat model | Subtlety | Suspicion | Threshold | Outcome | Security |
|----------|--------------|----------|-----------|-----------|---------|----------|
| 9: code sabotage subtle evades | code_sabotage | subtle | 0.20 | 0.7 | Accept | **VULNERABILITY** |
| 10: code sabotage obvious caught | code_sabotage | obvious | 0.92 | 0.7 | Defer | SAFE |
| 11: data poisoning subtle evades | data_poisoning | subtle | 0.15 | 0.7 | Accept | **VULNERABILITY** |
| 12: data poisoning obvious caught | data_poisoning | obvious | 0.85 | 0.7 | Defer | SAFE |
| 13: research sabotage subtle evades | research_sabotage | subtle | 0.10 | 0.7 | Accept | **VULNERABILITY** |
| 14: research sabotage obvious caught | research_sabotage | obvious | 0.80 | 0.7 | Defer | SAFE |

Detection rates encode the empirical pattern that generic monitors are systematically weaker against data-distribution and research-output attacks than against code-level sabotage at the same subtlety (subtle: code 0.20 > data 0.15 > research 0.10).

#### `[EXPECTED_EFFECT]` negative-control scenario (added in 1.9.7)

| Scenario | Note | Plan length |
|----------|------|-------------|
| 15: [EXPECTED_EFFECT] negative control | Manual task list uses `a_accept_output_demo_no_expected_effect` (byte-identical to `a_accept_output` except the `[EXPECTED_EFFECT]` block is omitted). Plan succeeds but `state.side_task_observed` is never set. | 5 |

**Domain (1.9.4 baseline -> 1.9.7 extended):** actions 7 -> 8 (added negative-control variant `a_accept_output_demo_no_expected_effect` in 1.9.7), methods 7 -> 7 (unchanged), scenarios 8 -> 15 (+6 threat-typed + 1 negative control in 1.9.7), doctests 56 -> 92. Tags `[DATA]`, `[ENABLER]`, `[CONFIG]` from 1.9.4; `[EXPECTED_EFFECT]` added in 1.9.7 (first use in the `control_arena_protocols/` collection).

**Educational Value:** Demonstrates how HTN planning can formalize adversarial analysis of safety protocols. Scenarios 3 vs. 4 show the safety-usefulness tradeoff (tightening the threshold catches subtle attacks but scenario 7 shows it causes false positives on honest output). Scenarios 9–14 add a *second axis* of variation: holding subtlety constant, threat type drives detectability — a "tighten the threshold" mitigation tuned for code sabotage may still miss subtle research sabotage. Scenario 15 demonstrates the `[EXPECTED_EFFECT]` tag's role: it makes deployment-executor side-task firing observable in `state.side_task_observed`. The teaching-variant action that omits the block produces an otherwise-identical plan but leaves the safety violation silently unrecorded — empirical evidence for why the tag is load-bearing.

### Running the Control Arena Benchmarks

```bash
cd src/gtpyhop/examples/control_arena_protocols

# Run all scenarios for each example
python benchmarking.py --example defer
python benchmarking.py --example resample
python benchmarking.py --example adversarial

# Run specific scenario
python benchmarking.py --example adversarial --scenario scenario_3_subtle_evades

# List available scenarios
python benchmarking.py --list-scenarios --example adversarial

# Run doctests
python -m doctest -v src/gtpyhop/examples/control_arena_protocols/defer_to_trusted_protocol/problems.py
python -m doctest -v src/gtpyhop/examples/control_arena_protocols/defer_to_resample_protocol/problems.py
python -m doctest -v src/gtpyhop/examples/control_arena_protocols/adversarial_protocol/problems.py
```

**Documentation:**
- [Control Arena Protocols README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/control_arena_protocols/README.md) — architectural overview, Concept Mapping, Benchmark Outcome Labels, Three Levels of Integration framing
- [Control Arena Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/control_arena_protocols/benchmarking_quickstart.md) — batch-running scenarios across all three protocol examples, with per-scenario expected-plan-length tables (added in 1.9.7)

---

## Cybersecurity Attack Planning Example (1.9.5+)

Models insider attacks against a network Document Management System, based on the BAMS (Behavioral Adversary Modeling System) domain. Together with the Control Arena Protocol examples, this covers **both sides** of AI safety/security: attacker (this example) and defender (Control Arena).

**Purpose:** Generate attack plans that help network administrators identify vulnerabilities in their systems.

**Core concepts demonstrated:**
- Multi-phase attack decomposition (credentials, system access, document access, exfiltration)
- Backtracking across alternative attack strategies (physical vs. cyber, DMS vs. malware)
- Greedy planner failure when countermeasures block the first-choice path
- Two top-level strategies: legitimate DMS access vs. covert malware relay

### `cybersecurity_attack_planning/`

| Aspect | Value |
|--------|-------|
| Actions | 21 (Physical: 5, Process: 4, Network: 2, DMS: 6, Malware: 4) |
| Methods | 16 (5 backtracking points) |
| Scenarios | 9 (4 require backtracking, 5 greedy-OK) |
| Doctests | 71 |
| `MCP_Tool:` | `None` |

**Scenarios:**
- **S1-S3**: Three credential paths (direct, shoulder surfing, network sniffing)
- **S4**: Locked door blocks shoulder surfing, planner backtracks to sniffing
- **S5**: Firewall would block sniffing, but surfing succeeds first
- **S6**: Admin ACL change via sniffed admin password
- **S7-S9**: Malware relay attacks when legitimate DMS access is blocked

**Run doctests:**

```bash
python -m doctest -v src/gtpyhop/examples/cybersecurity_attack_planning/problems.py
```

**Documentation:** [Cybersecurity Attack Planning README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/cybersecurity_attack_planning/README.md)

---

## Android: Netrunner Run Planning Example (1.9.6+)

Models a single Runner-side **run** against a configured Corporation server stack, using the published mechanics of Fantasy Flight Games' *Android: Netrunner* (2012 core set rulebook). The flagship scenario faithfully replicates the worked run example on **page 19 of the core rulebook**.

**Purpose:** Demonstrate that HTN planning can faithfully encode the mechanics of a published Living Card Game, with per-card fidelity for 14 named cards from the core set.

**Core concepts demonstrated:**
- Per-card fidelity: each card's distinctive mechanic is preserved (Crypsis end-of-encounter clause, Gordian Blade's run-scoped pump, Wyrm's `ice_strength_le_zero` break predicate, Akitaro Watanabe's rez-cost discount, Jinteki Personal Evolution's on-steal net damage)
- Three coexisting state scopes: encounter (resets after each ice), run (resets after the run), persistent
- 6 backtracking points: icebreaker selection (matched vs. AI × full vs. partial = 8 alternatives), Crypsis end-of-encounter cleanup (4 alternatives), Data Raven on-encounter ability (2), ambush firing (2), asset/upgrade trash decisions (2 each)
- Per-scenario Corp policy as configured environmental state: rez plan, ambush firing, trace budget, ambush trash priorities

### `android_netrunner/`

| Aspect | Value |
|--------|-------|
| Actions | 24 (Setup: 3, Run flow: 4, Encounter: 5, Sub resolution: 5, Cleanup: 3, Access: 4) |
| Methods | 31 method functions across 17 task names |
| Backtracking points | 6 |
| Scenarios | 8 (5 require backtracking, 2 designed greedy failures) |
| Doctests | 64 |
| `MCP_Tool:` | `None` |
| Card subset | 14 named cards from the core set |

**Card subset:**
- **Corp ice (4):** Ice Wall, Wall of Thorns, Enigma, Data Raven
- **Corp non-ice (4):** AstroScript Pilot Program, Nisei MK II, Aggressive Secretary, Akitaro Watanabe
- **Corp identity:** Jinteki Personal Evolution
- **Runner icebreakers (4):** Corroder, Gordian Blade, Wyrm, Crypsis
- **Runner hardware/resources (2):** The Toolbox, Sacrificial Construct

**Scenarios:**
- **S1-S2:** Baseline run mechanics (empty server, single barrier)
- **S3** (**flagship, greedy fails**): Rulebook p.19 replication. Partial-break Enigma with Gordian, pass Ice Wall, pump-and-partial Wall of Thorns with Crypsis, save Crypsis with Sacrificial Construct, steal Nisei MK II (Jinteki PE does 1 net damage on steal). Plan length 13 — `a_pass_ice` and `a_resolve_lose_click` are idempotent in context and elided
- **S4:** Sentry needs AI fallback — Corroder/Gordian fail subtype match, Crypsis (AI) succeeds against Data Raven
- **S5:** Wyrm drain path — pump + drain + breaks on Wall of Thorns
- **S6** (**greedy fails**): Accept net damage to save credits — greedy full-breaks Wall of Thorns and runs out for Enigma; backtracking takes 2 net damage
- **S7:** Crypsis cleanup chain falls through to trash (no virus counter, no SC)
- **S8:** Aggressive Secretary ambush trashes Corroder on access

**Run doctests:**

```bash
python -m doctest -v src/gtpyhop/examples/android_netrunner/problems.py
```

**Tip:** When investigating shorter-than-expected plans, run with `verbose=3` to see actions annotated as `applied` or `idempotent`. GTPyhop elides idempotent actions from `result.plan` even though it processes them.

**Reference:** Garfield, R. (designer), and Litzsinger, L. (developer). *Android: Netrunner — The Card Game, Rules of Play* (Fantasy Flight Games, 2012).

**Documentation:** [Android: Netrunner README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/android_netrunner/README.md)

---

## Trunk Thumper Game-AI Examples (1.9.6+)

A progressive collection of HTN planning examples based on **Troy Humphreys' chapter "Exploring HTN Planners through Example"** in *Game AI Pro 1* (Steve Rabin, ed., CRC Press, 2015, pp. 149–167). The chapter is the canonical pedagogical reference for HTN in game NPC behavior selection, based on the production system used in *Transformers: Fall of Cybertron* (HighMoon Studios / Activision, 2012). It describes a **total-order forward-decomposition planner with DFS backtracking** — i.e., GTPyhop's exact architecture; the pseudocode on pp.155–156 reads almost line-for-line like GTPyhop's `iterative_dfs_backtracking` strategy.

**Purpose:** Fill a real gap in GTPyhop's example library by providing a first-class **game AI developer** example. HTN planning's historical industrial home is game NPC behavior; this collection translates the canonical chapter into runnable code.

**Core concepts demonstrated:**
- Baseline domain construction (§12.3)
- Recursion via compound-task self-reference (§12.6)
- The new `[EXPECTED_EFFECT]` tag for sensor-driven state changes (§12.7), with an empirical negative-control scenario
- Multi-method priority via method ordering (§12.8) plus the chapter's WsIsTired fix for premature whirlwind combos
- Single-planner simultaneous behaviors via non-blocking navigation (§12.9)
- Manual method-split partial plans for reactivity (§12.10)
- How `MTR` (runtime priority comparison) and plan-runner concerns are *out of scope* and why

### Collection structure

Sub-folder names map to chapter section numbers (`sNN_<topic>` ↔ §12.NN) so readers of the book can find the matching code instantly:

| Folder | Chapter | Actions | Methods | Scenarios |
|---|---|---|---|---|
| `s03_basic_attack_or_patrol/` | §12.3 | 5 | 2 | 2 |
| `s06_recursive_trunk_replacement/` | §12.6 | 8 | 4 | 3 |
| `s07_expected_effects_chase/` | §12.7 | 11 | 5 | 3 (incl. 1 negative control) |
| `s08_priority_methods/` | §12.8 | 9 | 5 | 4 |
| `s09_simultaneous_navigation_and_guard/` | §12.9 | 4 | 4 | 3 |
| `s10_partial_plans/` | §12.10 | 2 | 3 | 3 |

**Totals:** 33 actions across 6 sub-folders, 18 scenarios, ~85 doctests, plus collection-level `benchmarking.py` and `benchmarking_quickstart.md`.

**Scenarios highlight:**
- s07's `scenario_3_expected_effects_negative_control` deliberately **fails**: it uses a teaching-variant action that omits the `[EXPECTED_EFFECT]` on `can_see_enemy`, and the plan correctly cannot satisfy the downstream `a_regain_los_roar` precondition. This is the empirical demonstration of *why* the tag is needed.
- s08's `scenario_4_tired_blocks_whirlwind_combo` exercises the chapter's recommended `WsIsTired` fix that prevents whirlwind combos from chaining directly off a slam.

### Running scenarios

**Per-sub-folder:**

```bash
# Doctests for a single sub-folder
python -m doctest -v src/gtpyhop/examples/trunk_thumper/s07_expected_effects_chase/problems.py

# Programmatic execution
python -c "
import copy, gtpyhop
from gtpyhop.examples.trunk_thumper.s06_recursive_trunk_replacement import the_domain, get_problems
for name, (state, tasks, _) in get_problems().items():
    state_copy = copy.deepcopy(state)
    with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
            strategy='iterative_dfs_backtracking') as s:
        r = s.find_plan(state_copy, tasks)
    print(f'{name}: success={r.success}, len={len(r.plan)}')
"
```

**Across all sub-folders (via the collection-level benchmarking script):**

```bash
cd src/gtpyhop/examples/trunk_thumper
python benchmarking.py --list-domains
python benchmarking.py s03_basic_attack_or_patrol
python benchmarking.py s07_expected_effects_chase
python benchmarking.py s08_priority_methods --strategy iterative_dfs_backtracking
```

See `src/gtpyhop/examples/trunk_thumper/benchmarking_quickstart.md` for the full guide.

### Style guide update

Section 8 of `docs/gtpyhop_domain_style_guide.md` was renamed "Metadata Tags: DATA, ENABLER, and EXPECTED_EFFECT" and gained a new subsection 8.4 documenting the `[EXPECTED_EFFECT]` tag introduced by this collection.

### Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, pp. 149–167.

**Documentation:** [Trunk Thumper Collection README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/trunk_thumper/README.md)

---

## Colt Express Game-AI Examples (1.9.7+)

A progressive collection of HTN planning examples applied to the **Colt Express** board game (Christophe Raimbault / Jordi Valbuena, Ludonaute 2014). The collection mirrors the structural template of the trunk_thumper collection — each sub-folder demonstrates one HTN concept with a direct lineage to a trunk_thumper sub-folder, but applied to a richer multi-bandit / Marshal-driven domain. Together with trunk_thumper, it forms a two-tier teaching arc: trunk_thumper introduces each HTN pattern in a toy game-AI scenario; colt_express shows the same pattern operating in a more complex published board game.

**Purpose:** Pair with trunk_thumper to demonstrate that the HTN pattern catalog scales from toy game-AI to published board games, with character-specific abilities, sensor-driven world reactions (the Marshal forced-escape), and end-of-round events.

**Scope:** Only the **Stealin' phase** is modeled. The programmed deck is pre-encoded in `state.deck` and the planner resolves it action-by-action, filling in the parameter choices the rules leave open (Move direction, Fire target, Robbery pick). The Schemin' phase (strategic card selection under imperfect information) is out of scope for classical HTN.

**Core concepts demonstrated:**
- Canonical state schema shared byte-identically across all 5 sub-folders (`h_create_base_state`, `h_sample_car_loot`, `COLT_EXPRESS_LOOT_DISTRIBUTION`)
- Priority methods baseline (s1)
- Recursion via `state.deck` head-pop with hostage-taking event resolution (s2)
- The `[EXPECTED_EFFECT]` tag for the Marshal forced-escape rule, with an empirical negative-control scenario (s3)
- Priority-method ladder for 4 of 6 character abilities — Belle / Tuco / Django / Cheyenne (s4)
- Manual method-split partial plans for movement strategy (s5)

### Collection structure

Sub-folder names `sN_<topic>` reflect **build order** (`s1 → s3 → s2 → s4 → s5`, with `s3` built second to lock the Marshal-aware state shape early). See the **Pattern source** column for each sub-folder's trunk_thumper lineage:

| Folder | Pattern source | Actions | Methods | Scenarios |
|---|---|---|---|---|
| `s1_minimal_turn/` | trunk_thumper s03 (priority methods) | 3 | 2 | 3 |
| `s3_marshal_expected_effects/` | trunk_thumper s07 (`[EXPECTED_EFFECT]`) | 6 | 2 | 3 (incl. 1 negative control) |
| `s2_recursive_round/` | trunk_thumper s06 (recursion) | 4 | 4 | 3 |
| `s4_character_priorities/` | trunk_thumper s08 (priority ladder) | 8 | 6 | 4 |
| `s5_partial_plan_movement/` | trunk_thumper s10 (method-split) | 5 | 5 | 3 |

**Totals:** 26 actions across 5 sub-folders, 16 scenarios, 124 doctests, plus collection-level `benchmarking.py` and `benchmarking_quickstart.md`.

trunk_thumper's `s09` (simultaneous behaviors via non-blocking navigation) has no Colt Express analog — bandits play exactly one card per turn — so the pattern is not represented in this collection.

**Scenarios highlight:**
- s3's `scenario_3_expected_effects_negative_control` deliberately **fails**: it uses a teaching-variant action `a_move_demo_no_marshal_trigger` that omits the `[EXPECTED_EFFECT]` block on the Marshal forced-escape, and the downstream `a_fire` action's precondition (shooter on roof) cannot be satisfied. This is the empirical demonstration of *why* the `[EXPECTED_EFFECT]` tag is needed — structurally identical to trunk_thumper s07 scenario 3.
- s4's `scenario_1_belle_immunity_redirects_fire` demonstrates the Belle-immunity priority method: when Tuco fires at Belle and an alternative target exists, the higher-priority method redirects the shot. Structural twin of trunk_thumper s08's WsIsTired fix (a higher-priority precondition guard preventing a generic action from firing in a rule-defined situation).
- s5's scenarios 1 and 2 use the **same initial state** but different task names (`m_resolve_move_full_plan` vs. `m_resolve_move_partial_plan`), producing plan lengths 2 and 1 respectively — exactly the trunk_thumper s10 idiom for demonstrating the partial-plan reactivity argument.

### Running scenarios

**Per-sub-folder:**

```bash
# Doctests for a single sub-folder
python -m doctest -v src/gtpyhop/examples/colt_express/s3_marshal_expected_effects/problems.py

# Programmatic execution
python -c "
import copy, gtpyhop
from gtpyhop.examples.colt_express.s2_recursive_round import the_domain, get_problems
for name, (state, tasks, _) in get_problems().items():
    state_copy = copy.deepcopy(state)
    with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
            strategy='iterative_dfs_backtracking') as s:
        r = s.find_plan(state_copy, tasks)
    print(f'{name}: success={r.success}, len={len(r.plan) if r.plan else 0}')
"
```

**Across all sub-folders (via the collection-level benchmarking script):**

```bash
cd src/gtpyhop/examples/colt_express
python benchmarking.py --list-domains
python benchmarking.py s1_minimal_turn
python benchmarking.py s3_marshal_expected_effects --strategy iterative_dfs_backtracking
python benchmarking.py s4_character_priorities
```

See `src/gtpyhop/examples/colt_express/benchmarking_quickstart.md` for the full guide (including a per-scenario expected-plan-length table).

### Reference

Raimbault, C., and Valbuena, J. *Colt Express*. Ludonaute / Asmodee, 2014. <http://www.coltexpress.ludonaute.fr>

**Documentation:** [Colt Express Collection README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/colt_express/README.md)

---

## Running the Examples

### Command-Line Interface
All examples support both legacy and session modes:

```bash
# Legacy mode (backward compatible)
python -m gtpyhop.examples.simple_htn

# Session mode (thread-safe, recommended)
python -m gtpyhop.examples.simple_htn --session

# With custom verbosity and no pauses
python -m gtpyhop.examples.simple_htn --session --verbose 2 --no-pauses
```

### Available Arguments
- `--session`: Enable thread-safe session mode
- `--verbose N`: Set verbosity level (0-3)
- `--no-pauses`: Skip interactive pauses for automated testing

### Regression Testing
```bash
# Test all examples
python -m gtpyhop.examples.regression_tests

# Session-based testing
python -m gtpyhop.examples.regression_tests --session
```

---

## Pedagogical Recommendations

### For Beginners
1. Start with `simple_htn.py` to understand basic concepts
2. Compare with `simple_hgn.py` to see goal vs. task approaches
3. Use high verbosity (`--verbose 3`) to see detailed planning traces
4. Experiment with different initial states and goals

### For Advanced Users
1. Study the blocks world examples to understand complex domains
2. Examine the IPC domains for competition-grade problems
3. Use session mode for concurrent planning experiments
4. Analyze planning logs programmatically using the structured logging system

### For Researchers
1. Use the examples as templates for new domains
2. Study the method design patterns in complex examples
3. Benchmark performance using the IPC and memory tracking domains
4. Extend examples with new planning techniques

---

## Related Documentation
- [Running Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/running_examples.md) - Detailed execution instructions
- [Structured Logging](https://github.com/PCfVW/GTPyhop/blob/pip/docs/logging.md) - Analyzing planning traces
- [Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md) - Concurrent planning patterns
- [Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md) - How to write new examples
- [Domain Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_domain_style_guide.md) - Conventions for domain files
- [Problems Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md) - Conventions for problem files
