# Poetry Examples for GTPyhop

## Overview

This directory contains examples demonstrating **neuro-symbolic poetry generation** using GTPyhop. The examples show hierarchical task network (HTN) planning for structured poetry workflows where the HTN planner produces structural plans (form, rhyme scheme, meter) and leaf-level actions are delegated to external MCP servers (LLM for text generation, phonetics for rhyme selection and verification).

This collection is motivated by Anthropic's "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" (March 2025) discovery that Claude 3.5 Haiku plans ahead when writing rhyming poetry, activating candidate end-of-line words before writing each line. These domains make that implicit planning **explicit** via HTN decomposition.

## Available Examples

| # | Example | Directory | Actions | Methods | Scenarios | Strategy Required |
|---|---------|-----------|---------|---------|-----------|-------------------|
| 1 | **Structured Poetry** | `structured_poetry/` | 6 | 8 | 6 | Any |
| 2 | **Backtracking Poetry** | `backtracking_poetry/` | 7 | 9 | 3 | Backtracking* |
| 3 | **Candidate Planning Poetry** | `candidate_planning_poetry/` | 8 | 8 | 3 | Any |
| 4 | **Bidirectional Planning Poetry** | `bidirectional_planning_poetry/` | 7 | 8 | 3 | Any |
| 5 | **Replanning Poetry** | `replanning_poetry/` | 8 | 10 | 3 | Backtracking* |
| 6 | **Formal Mechanism Poetry** | `formal_mechanism_poetry/` | 7 | 6 | 3 | Any |
| 7 | **Feature Space Poetry** | `feature_space_poetry/` | 9 | 5 | 12 | Backtracking* |

\* Backtracking required: examples 2, 5 for rhymed forms; example 7 for scenarios with multiple candidates.

## Planning Strategy Requirements

GTPyhop 1.9.0 provides three planning strategies. Not all examples work with all strategies:

| Strategy | Backtracking | Examples 1, 3, 4, 6 | Example 2 | Example 5 | Example 7 |
|----------|-------------|----------------------|-----------|-----------|-----------|
| `iterative_greedy` | None | All pass | Limerick **FAILS** | Couplet, Limerick **FAIL** | Scenarios 1, 3, 5, 7, 9, 11 **FAIL** |
| `recursive_dfs` | Via call stack | All pass | All pass | All pass | All pass |
| `iterative_dfs_backtracking` | Via explicit stack | All pass | All pass | All pass | All pass |

**Why do examples 2, 5, and 7 fail with greedy?** They register multiple methods for a single task (a backtracking point). The greedy planner commits irrevocably to the first applicable method. When an action within that method's subtasks subsequently fails, the greedy planner has no mechanism to backtrack and try the next method — so it reports failure.

- **Backtracking Poetry**: `m_write_rhymed_line` has two methods (strict, relaxed). `a_select_rhyme_target_strict` fails on the 3rd+ use of a rhyme label.
- **Replanning Poetry**: `m_evaluate_and_replan` has two methods (accept, revise). `a_evaluate_line` fails for lines requiring revision (subsequent uses of each rhyme label).
- **Feature Space Poetry**: `m_find_best_injection` has three methods (try each feature). `a_evaluate_threshold` fails when `measured_probability < probability_threshold`.

**Note:** Example 6 (formal mechanism) also registers three methods for `m_select_end_word`, but all current scenarios succeed with greedy because the strongest candidate is tried first.

```python
# For examples that require backtracking, use either:
with gtpyhop.PlannerSession(domain=the_domain, strategy="recursive_dfs") as session:
    result = session.find_plan(state, tasks)

with gtpyhop.PlannerSession(domain=the_domain, strategy="iterative_dfs_backtracking") as session:
    result = session.find_plan(state, tasks)
```

### 1. Structured Poetry

Baseline domain for neuro-symbolic poetry generation:
- 6 actions, 8 methods (one method per task)
- 6 scenarios: 2 couplets, 2 limericks, 1 haiku, 1 sonnet
- All three planning strategies produce identical plans

**Use case**: Demonstrates the core HTN decomposition pattern for poetry generation without backtracking concerns.

### 2. Backtracking Poetry

Extension designed as a **test harness** for comparing planning strategies:
- 7 actions, 9 methods (two methods for `m_write_rhymed_line`)
- 3 scenarios: 1 couplet (no BT), 1 limerick (BT required), 1 haiku (no BT)
- Strict rhyme selection fails on 3rd+ use of a label, triggering backtracking to relaxed (near-rhyme)

**Use case**: Verifying that backtracking-capable planners (recursive DFS, iterative DFS BT) succeed where the greedy planner fails.

| Scenario | Recursive DFS | Iterative Greedy | Iterative DFS BT |
|----------|--------------|-----------------|------------------|
| Couplet (AA) | 8 actions | 8 actions | 8 actions |
| Limerick (AABBA) | 17 actions | **False** | 17 actions |
| Haiku (5-7-5) | 8 actions | 8 actions | 8 actions |

### 3. Candidate Planning Poetry

Extension modeling **multi-candidate rhyme selection**:
- 8 actions, 8 methods (one method per task)
- 3 scenarios: 1 couplet, 1 limerick, 1 haiku
- Replaces single rhyme target selection with a 3-action pipeline (generate candidates, rank, commit)

**Use case**: Models the LLM's simultaneous consideration of multiple end-words before committing to one.

| Scenario | Actions |
|----------|---------|
| Couplet (AA) | 12 |
| Limerick (AABBA) | 27 |
| Haiku (5-7-5) | 8 |

### 4. Bidirectional Planning Poetry

Extension modeling **decomposed line construction**:
- 7 actions, 8 methods (one method per task)
- 3 scenarios: 1 couplet, 1 limerick, 1 haiku
- Splits line generation into backward transition planning and surface text generation

**Use case**: Models the LLM's backward reasoning from the planned end-word to determine intermediate words.

| Scenario | Actions |
|----------|---------|
| Couplet (AA) | 10 |
| Limerick (AABBA) | 22 |
| Haiku (5-7-5) | 8 |

### 5. Replanning Poetry

Extension modeling **post-generation evaluation and steering/revision**:
- 8 actions, 10 methods (two methods for `m_evaluate_and_replan`)
- 3 scenarios: 1 couplet, 1 limerick, 1 haiku
- After initial generation, evaluation may trigger replanning with a steered target word

**Use case**: Models the paper's finding that injecting an alternative planned word causes the model to restructure the entire line in 70% of test poems.

| Scenario | Recursive DFS | Iterative Greedy | Iterative DFS BT |
|----------|--------------|-----------------|------------------|
| Couplet (AA) | 12 actions | **False** | 12 actions |
| Limerick (AABBA) | 28 actions | **False** | 28 actions |
| Haiku (5-7-5) | 8 actions | 8 actions | 8 actions |

### 6. Formal Mechanism Poetry

Extension modeling **Anthropic's three planning mechanisms** from the "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" paper:
- 7 actions, 6 methods (three methods for `m_select_end_word`)
- 3 scenarios: full mechanism (19), commitment focus (7), three-stage (13)
- Separates pre-commitment candidate generation from verified commitment, with couplet commitment for multi-line coordination

**Use case**: Makes the three mechanisms from the paper (candidate activation, commitment, couplet commitment) explicit as HTN task decompositions.

| Scenario | Actions | Backtracking |
|----------|---------|-------------|
| Full mechanism | 19 | No |
| Commitment focus | 7 | No |
| Three-stage | 13 | No |

### 7. Feature Space Poetry

Extension operating in **CLT activation space** rather than text space:
- 9 actions, 5 methods (three methods for `m_find_best_injection`)
- 12 scenarios: 4 Gemma 2 2B 426K (Version D) + 4 Llama 3.2 1B 524K (Version L) + 4 Gemma 2 2B 2.5M (Version D 2.5M)
- Plans interventions on neural network internal representations (suppress+inject protocol)
- Probability-based backtracking using measured experimental data

**Use case**: Demonstrates HTN planning for feature-space interventions coordinated across 3 servers (local, inference, CLT). The same HTN protocol applies to all three configurations despite different planning architectures (forward planning vs. late selection) and CLT resolutions (426K vs. 2.5M).

Gemma 2 2B (scenarios 0-3): forward planning model, 26 layers, CLT 426K

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 0: Version D star result | Ground truth (out->ound, 26 layers) | 34 | No | SUCCESS |
| 1: Cheapest first | Reordered candidates | 34 | Yes (2 failures) | **FAIL** |
| 2: Planning layer only | Single layer, single candidate | 9 | No | SUCCESS |
| 3: Different group | oo->ound, lower threshold | 10 | Yes (1 failure) | **FAIL** |

Llama 3.2 1B (scenarios 4-7): late selection model, 16 layers, CLT 524K

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 4: Llama star result | Ground truth (ee->at, "that" at 77.7%) | 24 | No | SUCCESS |
| 5: Llama sat first | "sat" before "that" | 24 | Yes (1 failure) | **FAIL** |
| 6: Llama output layer | Only L15 encoded | 9 | No | SUCCESS |
| 7: Llama different group | at->ore, lower threshold | 10 | Yes (2 failures) | **FAIL** |

Gemma 2 2B + CLT 2.5M (scenarios 8-11): word-level planning model, 26 layers, CLT 2.5M

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 8: 2.5M star result | Ground truth (out->an, "can" at 48.2%) | 34 | No | SUCCESS |
| 9: 2.5M weakest first | "plan" before "can" | 34 | Yes (2 failures) | **FAIL** |
| 10: 2.5M planning layer | Only L25 encoded | 9 | No | SUCCESS |
| 11: 2.5M different group | oo->an, lower threshold | 10 | Yes (1 failure) | **FAIL** |

## Supported Poetic Forms (Examples 1-5)

| Form | Lines | Rhyme Scheme | Meter | Structured | Candidate | Bidirectional | Replanning |
|------|-------|-------------|-------|------------|-----------|---------------|------------|
| Couplet | 2 | AA | Iambic tetrameter | 8 | 12 | 10 | 12 |
| Limerick | 5 | AABBA | Anapestic | 17 | 27 | 22 | 28 |
| Haiku | 3 | None | Syllabic (5-7-5) | 8 | 8 | 8 | 8 |
| Sonnet | 14 | ABAB CDCD EFEF GG | Iambic pentameter | 44 | 72 | 58 | 72 |

## Server Architectures and MCP

### Why MCP?

Every action in these poetry domains is annotated with an `MCP_Tool:` tag in its
docstring, indicating which [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) server and tool should handle that action at execution time. This design
reflects a deliberate **separation of concerns** between the HTN planner and the
services that carry out its decisions:

| Layer | Responsibility | Technology |
|-------|---------------|------------|
| **HTN Planner** (GTPyhop) | *What* to do: decompose the poem into structural steps (form, rhyme scheme, meter, line ordering) | Pure Python, deterministic search |
| **MCP Servers** | *How* to do it: generate text, select rhyme words, verify phonetic constraints, run neural-network experiments | External processes, accessed via MCP |

The planner **never generates text or calls an LLM itself**. It produces a
totally-ordered sequence of leaf actions like `a_select_rhyme_target`,
`a_generate_line`, `a_verify_line`. Each leaf action carries an `MCP_Tool:`
annotation that names the server and tool to call. For example:

```python
def a_select_rhyme_target(state, line_idx, rhyme_label):
    """
    Class: Action
    MCP_Tool: phonetics_server:select_rhyme_target
    ...
    """

def a_generate_line(state, line_idx, target_syllables):
    """
    Class: Action
    MCP_Tool: llm_server:generate_line
    ...
    """
```

### What does MCP bring?

1. **Clean neuro-symbolic boundary.** The planner handles symbolic reasoning
   (form decomposition, rhyme-label tracking, backtracking on failure) while MCP
   servers handle neural or computational tasks (LLM inference, phonetic lookup).
   Neither side needs to know the internals of the other.

2. **Swappable servers.** Because the interface is a standard protocol, the
   phonetics server could be backed by CMU Pronouncing Dictionary today and a
   neural phonetics model tomorrow -- without changing the domain or the planner.

3. **Composable multi-server workflows.** A single HTN plan can orchestrate
   calls to multiple servers in a determined order. Examples 1-5 coordinate two
   servers; examples 6-7 coordinate three. The planner decides the sequencing;
   MCP handles the transport.

4. **Testability without servers.** During planning, the `MCP_Tool:` annotations
   are documentary -- the planner simulates actions via precondition/effect
   updates on the state. Real MCP calls only happen at *execution* time. This
   means all 7 domains can be planned, benchmarked, and tested without any
   running server.

### Server configurations by example

**Examples 1-5** (text-generation domains) use a **two-server** architecture:

| MCP Server | Role | Example tools |
|------------|------|---------------|
| **phonetics_server** | Rhyme candidate selection, steering, syllable counting, verification | `select_rhyme_target`, `generate_rhyme_candidates`, `rank_candidates`, `verify_line`, `steer_target` |
| **llm_server** | Constrained text generation, transition planning, line evaluation | `generate_line`, `generate_line_free`, `plan_transition`, `generate_surface_text`, `evaluate_line` |

Both servers are complemented by **local** actions (`local:initialize_poem`, `local:assemble_poem`) that require no external call.

**Examples 6-7** (mechanistic analysis domains) use a **three-server** architecture:

| MCP Server | Role | Example tools |
|------------|------|---------------|
| **inference_server** | Forward passes through the neural network, probability measurement | `locate_planning_site`, `measure_rhyme_probability`, `measure_group_probability` |
| **clt_server** | CLT (Concept Lattice Topology) feature experiments: encode/decode residual streams, knockout and injection | `run_experiment`, `encode_residual`, `suppress_group`, `inject_feature` |
| **local** | Hypothesis formulation, threshold evaluation, report compilation | `initialize_analysis`, `initialize_intervention`, `formulate_stage`, `evaluate_threshold`, `evaluate_correspondence`, `compile_report` |

### MCP reference summary across files

All 7 `domain.py` files declare their MCP server architecture in a header comment
and annotate every action with `MCP_Tool:`. Four of the 7 `problems.py` files
also mention MCP when describing the server coordination for their scenarios
(structured, candidate, bidirectional, replanning).

## Directory Structure

```
poetry/
+-- __init__.py
+-- benchmarking.py                        # Unified benchmarking script
+-- benchmarking_quickstart.md             # Benchmarking quick start guide
+-- README.md                              # This file
+-- structured_poetry/
|   +-- __init__.py
|   +-- domain.py                          # 6 actions, 8 methods
|   +-- problems.py                        # 6 scenarios
|   +-- README.md
+-- backtracking_poetry/
|   +-- __init__.py
|   +-- domain.py                          # 7 actions, 9 methods
|   +-- problems.py                        # 3 scenarios
|   +-- README.md
+-- candidate_planning_poetry/
|   +-- __init__.py
|   +-- domain.py                          # 8 actions, 8 methods
|   +-- problems.py                        # 3 scenarios
|   +-- README.md
+-- bidirectional_planning_poetry/
|   +-- __init__.py
|   +-- domain.py                          # 7 actions, 8 methods
|   +-- problems.py                        # 3 scenarios
|   +-- README.md
+-- replanning_poetry/
|   +-- __init__.py
|   +-- domain.py                          # 8 actions, 10 methods
|   +-- problems.py                        # 3 scenarios
|   +-- README.md
+-- formal_mechanism_poetry/
|   +-- __init__.py
|   +-- domain.py                          # 7 actions, 6 methods
|   +-- problems.py                        # 3 scenarios
|   +-- README.md
+-- feature_space_poetry/
    +-- __init__.py
    +-- domain.py                          # 9 actions, 5 methods
    +-- problems.py                        # 12 scenarios
    +-- README.md
```

## Quick Start

```bash
cd src/gtpyhop/examples/poetry

# List available domains
python benchmarking.py --list-domains

# Run structured poetry scenarios
python benchmarking.py structured_poetry

# Run backtracking poetry scenarios (requires backtracking strategy)
python benchmarking.py backtracking_poetry --strategy iterative_dfs_backtracking

# Run feature space poetry scenarios (requires backtracking strategy)
python benchmarking.py feature_space_poetry --strategy iterative_dfs_backtracking

# Run with verbose output
python benchmarking.py structured_poetry --verbose 1
```

## Requirements

- GTPyhop 1.9.0+
- Python 3.8+

## See Also

- [structured_poetry/README.md](structured_poetry/README.md) - Baseline domain details
- [backtracking_poetry/README.md](backtracking_poetry/README.md) - Backtracking test harness details
- [candidate_planning_poetry/README.md](candidate_planning_poetry/README.md) - Multi-candidate pipeline details
- [bidirectional_planning_poetry/README.md](bidirectional_planning_poetry/README.md) - Decomposed line construction details
- [replanning_poetry/README.md](replanning_poetry/README.md) - Evaluation and revision details
- [formal_mechanism_poetry/README.md](formal_mechanism_poetry/README.md) - Three planning mechanisms from the paper
- [feature_space_poetry/README.md](feature_space_poetry/README.md) - Feature-space interventions with measured data
- [gitignore/iterative_backtracking_find_plan.md](../../../../gitignore/iterative_backtracking_find_plan.md) - Design report for iterative DFS backtracking

---
*Updated 2026-02-23*
