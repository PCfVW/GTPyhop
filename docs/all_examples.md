# GTPyhop 1.9.1 HTN Planning Examples

This document provides pedagogical details about all HTN Planning examples included with GTPyhop 1.9.1. Each example demonstrates different aspects of hierarchical task network planning, from basic concepts to advanced techniques.

## Table of Contents

1. [Learning Path](#-learning-path)
2. [Simple Examples](#-simple-examples-basic-concepts)
3. [Complex Block World Examples](#-complex-block-world-examples-advanced-scenarios)
4. [IPC 2020 Total Order Examples](#-ipc-2020-total-order-examples)
5. [MCP Orchestration Examples](#-mcp-orchestration-examples)
6. [Memory Tracking Examples](#-memory-tracking-examples-180)
7. [Poetry Examples](#-poetry-examples-190)
8. [Running the Examples](#-running-the-examples)
9. [Pedagogical Recommendations](#-pedagogical-recommendations)

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

These examples demonstrate HTN-planned poetry generation where the planner produces structural plans (form, rhyme scheme, meter constraints) and leaf-level actions are delegated to external MCP servers for text generation and phonetic verification. The collection is motivated by Anthropic's "Planning in Poems" (March 2025) discovery that Claude 3.5 Haiku plans ahead when writing rhyming poetry.

**Progression:** The seven examples form a progression. Examples 1-5 model text-generation poetry workflows; examples 6-7 model the underlying planning mechanisms and feature-space interventions:

| # | Example | Key Extension | Actions | Methods | Strategy |
|---|---------|---------------|---------|---------|----------|
| 1 | Structured Poetry | Baseline (select → generate → verify) | 6 | 8 | Any |
| 2 | Backtracking Poetry | Strict/relaxed methods with backtracking | 7 | 9 | Backtracking |
| 3 | Candidate Planning Poetry | Multi-candidate target selection pipeline | 8 | 8 | Any |
| 4 | Bidirectional Planning Poetry | Decomposed backward line construction | 7 | 8 | Any |
| 5 | Replanning Poetry | Post-generation evaluation and revision | 8 | 10 | Backtracking |
| 6 | Formal Mechanism Poetry | Three planning mechanisms from the paper | 7 | 6 | Any |
| 7 | Feature Space Poetry | Feature-space interventions with measured data | 9 | 7 | Backtracking |

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
**Purpose:** Three planning mechanisms from Anthropic's paper as explicit HTN decompositions
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
**Scenarios:** 4 scenarios (ground truth + 3 counterfactual what-ifs)

**Key Learning Points:**
- Planning in CLT activation space rather than text space
- Probability-based backtracking using measured experimental data
- Ground truth + counterfactual scenario structure
- Three-server coordination (local, inference, CLT)

**Core Concepts Demonstrated:**
- **Suppress+Inject Protocol:** Suppress natural rhyme group features, inject alternative group feature, measure probability shift
- **Probability-Based Backtracking:** `a_evaluate_threshold` compares `measured_probability` against `probability_threshold`; failure triggers backtracking to the next candidate
- **Three Methods for `m_try_candidate`:** Each tries a different CLT feature; `a_evaluate_threshold` fails when the injected feature's probability is below threshold
- **Actions (9):** Initialize, locate planning site, measure baseline, encode layers, suppress features, inject feature, measure effect, evaluate threshold, compile report
- **Methods (7):** Three try-methods for candidate selection, plus workflow orchestration

**Scenario Structure:**

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 0: Version D star result | Ground truth (what actually happened) | 34 | No | SUCCESS |
| 1: Cheapest first | What if candidates were reordered? | 34 | Yes (2 failures) | **FAIL** |
| 2: Planning layer only | What if only 1 layer was needed? | 9 | No | SUCCESS |
| 3: Different group | What if we redirected oo→ound? | 10 | Yes (1 failure) | **FAIL** |

**Educational Value:** Scenario 0 anchors the domain in reality (the actual Version D experiment result), making scenarios 1-3 pedagogically meaningful as counterfactual explorations. Probability data comes from measured Version D experiments (`suppress_inject_sweep.json`), not artificial thresholds. Demonstrates that the same domain can test both greedy and backtracking strategies depending on candidate ordering.

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
