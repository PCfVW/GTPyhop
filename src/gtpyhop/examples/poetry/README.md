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

\* Backtracking required for rhymed forms (couplet, limerick, sonnet). Haiku works with any strategy.

## Planning Strategy Requirements

GTPyhop 1.9.0 provides three planning strategies. Not all examples work with all strategies:

| Strategy | Backtracking | Examples 1, 3, 4 | Example 2 (backtracking) | Example 5 (replanning) |
|----------|-------------|-------------------|--------------------------|------------------------|
| `iterative_greedy` | None | All scenarios pass | Limerick **FAILS** | Couplet, Limerick **FAIL** |
| `recursive_dfs` | Via call stack | All scenarios pass | All scenarios pass | All scenarios pass |
| `iterative_dfs_backtracking` | Via explicit stack | All scenarios pass | All scenarios pass | All scenarios pass |

**Why do examples 2 and 5 fail with greedy?** Both register two methods for a single task (a backtracking point). The greedy planner commits irrevocably to the first applicable method. When an action within that method's subtasks subsequently fails, the greedy planner has no mechanism to backtrack and try the second method — so it reports failure.

- **Backtracking Poetry**: `m_write_rhymed_line` has two methods (strict, relaxed). `a_select_rhyme_target_strict` fails on the 3rd+ use of a rhyme label.
- **Replanning Poetry**: `m_evaluate_and_replan` has two methods (accept, revise). `a_evaluate_line` fails for lines requiring revision (subsequent uses of each rhyme label).

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

## Supported Poetic Forms

| Form | Lines | Rhyme Scheme | Meter | Structured | Candidate | Bidirectional | Replanning |
|------|-------|-------------|-------|------------|-----------|---------------|------------|
| Couplet | 2 | AA | Iambic tetrameter | 8 | 12 | 10 | 12 |
| Limerick | 5 | AABBA | Anapestic | 17 | 27 | 22 | 28 |
| Haiku | 3 | None | Syllabic (5-7-5) | 8 | 8 | 8 | 8 |
| Sonnet | 14 | ABAB CDCD EFEF GG | Iambic pentameter | 44 | 72 | 58 | 72 |

## Two-Server Architecture

1. **phonetics-server**: Rhyme candidate selection, steering, syllable counting, verification
2. **llm-server**: Constrained text generation, transition planning, line evaluation

## Directory Structure

```
poetry/
+-- __init__.py
+-- benchmarking.py                        # Unified benchmarking script
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
    +-- __init__.py
    +-- domain.py                          # 8 actions, 10 methods
    +-- problems.py                        # 3 scenarios
    +-- README.md
```

## Quick Start

```bash
cd src/gtpyhop/examples/poetry

# List available domains
python benchmarking.py --list-domains

# Run structured poetry scenarios
python benchmarking.py structured_poetry

# Run backtracking poetry scenarios
python benchmarking.py backtracking_poetry

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
- [gitignore/iterative_backtracking_find_plan.md](../../../../gitignore/iterative_backtracking_find_plan.md) - Design report for iterative DFS backtracking

---
*Updated 2026-02-12*
