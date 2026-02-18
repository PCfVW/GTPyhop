# Poetry Examples for GTPyhop

## Overview

This directory contains examples demonstrating **neuro-symbolic poetry generation** using GTPyhop. The examples show hierarchical task network (HTN) planning for structured poetry workflows where the HTN planner produces structural plans (form, rhyme scheme, meter) and leaf-level actions are delegated to external MCP servers (LLM for text generation, phonetics for rhyme selection and verification).

This collection is motivated by Anthropic's "Planning in Poems" (March 2025) discovery that Claude 3.5 Haiku plans ahead when writing rhyming poetry, activating candidate end-of-line words before writing each line. These domains make that implicit planning **explicit** via HTN decomposition.

## Available Examples

| # | Example | Directory | Actions | Methods | Scenarios | Strategy Required |
|---|---------|-----------|---------|---------|-----------|-------------------|
| 1 | **Structured Poetry** | `structured_poetry/` | 6 | 8 | 6 | Any |
| 2 | **Backtracking Poetry** | `backtracking_poetry/` | 7 | 9 | 3 | Backtracking* |
| 3 | **Candidate Planning Poetry** | `candidate_planning_poetry/` | 8 | 8 | 3 | Any |
| 4 | **Bidirectional Planning Poetry** | `bidirectional_planning_poetry/` | 7 | 8 | 3 | Any |
| 5 | **Replanning Poetry** | `replanning_poetry/` | 8 | 10 | 3 | Backtracking* |
| 6 | **Formal Mechanism Poetry** | `formal_mechanism_poetry/` | 7 | 6 | 3 | Any |
| 7 | **Feature Space Poetry** | `feature_space_poetry/` | 9 | 7 | 4 | Backtracking* |

\* Backtracking required: examples 2, 5 for rhymed forms; example 7 for scenarios with multiple candidates.

## Planning Strategy Requirements

GTPyhop 1.9.0 provides three planning strategies. Not all examples work with all strategies:

| Strategy | Backtracking | Examples 1, 3, 4, 6 | Example 2 | Example 5 | Example 7 |
|----------|-------------|----------------------|-----------|-----------|-----------|
| `iterative_greedy` | None | All pass | Limerick **FAILS** | Couplet, Limerick **FAIL** | Scenarios 1, 3 **FAIL** |
| `recursive_dfs` | Via call stack | All pass | All pass | All pass | All pass |
| `iterative_dfs_backtracking` | Via explicit stack | All pass | All pass | All pass | All pass |

**Why do examples 2, 5, and 7 fail with greedy?** They register multiple methods for a single task (a backtracking point). The greedy planner commits irrevocably to the first applicable method. When an action within that method's subtasks subsequently fails, the greedy planner has no mechanism to backtrack and try the next method — so it reports failure.

- **Backtracking Poetry**: `m_write_rhymed_line` has two methods (strict, relaxed). `a_select_rhyme_target_strict` fails on the 3rd+ use of a rhyme label.
- **Replanning Poetry**: `m_evaluate_and_replan` has two methods (accept, revise). `a_evaluate_line` fails for lines requiring revision (subsequent uses of each rhyme label).
- **Feature Space Poetry**: `m_try_candidate` has three methods (try each feature). `a_evaluate_threshold` fails when `measured_probability < probability_threshold`.

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

Extension modeling **Anthropic's three planning mechanisms** from the "Planning in Poems" paper:
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
- 9 actions, 7 methods (three methods for `m_try_candidate`)
- 4 scenarios: ground truth + 3 counterfactual what-ifs
- Plans interventions on neural network internal representations (suppress+inject protocol)
- Probability-based backtracking using measured data from Version D experiments

**Use case**: Demonstrates HTN planning for feature-space interventions coordinated across 3 servers (local, inference, CLT). Scenario 0 replicates the actual Version D result; scenarios 1-3 explore counterfactual departures.

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 0: Version D star result | Ground truth (out->ound, 26 layers) | 34 | No | SUCCESS |
| 1: Cheapest first | Reordered candidates | 34 | Yes (2 failures) | **FAIL** |
| 2: Planning layer only | Single layer, single candidate | 9 | No | SUCCESS |
| 3: Different group | oo->ound, lower threshold | 10 | Yes (1 failure) | **FAIL** |

## Supported Poetic Forms (Examples 1-5)

| Form | Lines | Rhyme Scheme | Meter | Structured | Candidate | Bidirectional | Replanning |
|------|-------|-------------|-------|------------|-----------|---------------|------------|
| Couplet | 2 | AA | Iambic tetrameter | 8 | 12 | 10 | 12 |
| Limerick | 5 | AABBA | Anapestic | 17 | 27 | 22 | 28 |
| Haiku | 3 | None | Syllabic (5-7-5) | 8 | 8 | 8 | 8 |
| Sonnet | 14 | ABAB CDCD EFEF GG | Iambic pentameter | 44 | 72 | 58 | 72 |

## Server Architectures

**Examples 1-5** (text-generation domains) use a two-server architecture:
1. **phonetics-server**: Rhyme candidate selection, steering, syllable counting, verification
2. **llm-server**: Constrained text generation, transition planning, line evaluation

**Example 6** (formal mechanism) uses a single **llm-server** for candidate generation, verification, and line writing.

**Example 7** (feature space) uses a three-server architecture:
1. **Local computation**: Initialize, suppress, evaluate threshold, compile report
2. **inference_server**: Forward passes, probability measurement
3. **clt_server**: CLT encode/decode, feature injection

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
    +-- domain.py                          # 9 actions, 7 methods
    +-- problems.py                        # 4 scenarios
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
*Updated 2026-02-18*
