# Replanning Poetry HTN Domain

## Overview

This example demonstrates **post-generation evaluation and steering/revision** for neuro-symbolic poetry generation using GTPyhop 1.9.0+. After initial line generation and verification, an evaluation step may determine that the line needs a better target word. This triggers replanning: the planner backtracks and tries a revision path that steers to a new target and completely regenerates the line.

This models Anthropic's "Planning in Poems" (March 2025) finding that **injecting an alternative planned word causes the model to restructure the entire line** in 70% of test poems. The planned end-word acts as a "control knob" for the whole line — changing it doesn't just patch the ending, it cascades through the entire downstream text.

## Difference from Structured Poetry

| Aspect | Structured Poetry | Replanning Poetry |
|--------|------------------|-------------------|
| Actions | 6 | 8 (+a_evaluate_line, +a_steer_target) |
| Methods | 8 | 10 (+m_accept_line, +m_revise_line) |
| Rhymed line cycle | 3 actions (select + generate + verify) | 4 actions + evaluation (select + generate + verify + evaluate/revise) |
| Backtracking | None | m_evaluate_and_replan (2 methods) |
| Actions per accepted line | 3 | 4 (select + generate + verify + evaluate) |
| Actions per revised line | N/A | 6 (select + generate + verify + steer + generate + verify) |
| Couplet plan length | 8 | 12 |
| Limerick plan length | 17 | 28 |
| Sonnet plan length | 44 | 72 |

## Benchmarking Scenarios

| Scenario | Form | Topic | Revised Lines | Actions | Status |
|----------|------|-------|---------------|---------|--------|
| `scenario_1_couplet_stars` | Couplet | stars in the night sky | {1} | 12 | VALID (requires backtracking) |
| `scenario_2_limerick_cat` | Limerick | a clever cat | {1, 3, 4} | 28 | VALID (requires backtracking) |
| `scenario_3_haiku_ocean` | Haiku | the ocean at dawn | none | 8 | VALID (any strategy) |

### Plan Length Formulas

Lines **without** revision: 4 actions (select + generate + verify + evaluate)
Lines **with** revision: 6 actions (select + generate + verify + steer + generate + verify)
Free lines (haiku): 2 actions (generate + verify)

| Form | Formula | Actions |
|------|---------|---------|
| Couplet | 2 + (1x4 + 1x6) | 12 |
| Limerick | 2 + (2x4 + 3x6) | 28 |
| Haiku | 2 + (3x2) | 8 |
| Sonnet | 2 + (7x4 + 7x6) | 72 |

Where: `init + assemble + (accepted_lines x 4 + revised_lines x 6)` for rhymed forms, and `init + assemble + (free_lines x 2)` for unrhymed forms (haiku).

### Revision Trigger

Lines requiring revision are computed deterministically by `a_initialize_poem` from the rhyme scheme: **subsequent uses of each rhyme label require revision** (the first line to establish a label is accepted, but lines forced to rhyme with an existing word need steering to a better target).

| Form | Rhyme Scheme | Lines Requiring Revision |
|------|-------------|-------------------------|
| Couplet | A A | {1} |
| Limerick | A A B B A | {1, 3, 4} |
| Haiku | - - - | (none) |
| Sonnet | A B A B C D C D E F E F G G | {2, 3, 6, 7, 10, 11, 13} |

## Backtracking Mechanism

The domain uses **action-level failure triggering method-level backtracking**, the same mechanism as the backtracking_poetry domain but at the evaluation level rather than the line composition level.

`m_evaluate_and_replan` has two registered methods:

1. **m_accept_line** (tried first): decomposes into `[a_evaluate_line]`. If the line doesn't need revision, the action succeeds and the line is accepted.

2. **m_revise_line** (fallback): decomposes into `[a_steer_target, a_generate_line, a_verify_line]`. Replaces the target word and completely regenerates the line.

```
m_write_rhymed_line(line_idx=1, "A", 8)
+-- a_select_rhyme_target(1, "A")     OK
+-- a_generate_line(1, 8)             OK
+-- a_verify_line(1)                  OK
+-- m_evaluate_and_replan(1, "A", 8)
    +-- TRY m_accept_line(1, "A", 8)
    |   +-- a_evaluate_line(1)        FAILS (line 1 needs revision)
    |                                 -> BACKTRACK
    +-- TRY m_revise_line(1, "A", 8)
        +-- a_steer_target(1, "A")    OK (new target, reset flags)
        +-- a_generate_line(1, 8)     OK (regenerate with new target)
        +-- a_verify_line(1)          OK (re-verify)
```

## Planning Strategy Requirement

**This example requires a backtracking-capable planning strategy.** It does NOT work with the default `iterative_greedy` strategy.

The reason: `m_evaluate_and_replan` registers two methods (`m_accept_line` and `m_revise_line`). The iterative greedy planner commits irrevocably to the first applicable method (`m_accept_line`). When its `a_evaluate_line` action subsequently fails for lines requiring revision, the greedy planner has no mechanism to backtrack and try `m_revise_line` — so it reports failure.

Both backtracking-capable strategies work correctly:
- `"recursive_dfs"` — backtracking via Python call stack
- `"iterative_dfs_backtracking"` — backtracking via explicit stack (added in GTPyhop 1.9.0)

```python
# Either of these strategies works:
with gtpyhop.PlannerSession(domain=the_domain, strategy="recursive_dfs") as session:
    result = session.find_plan(state, tasks)

with gtpyhop.PlannerSession(domain=the_domain, strategy="iterative_dfs_backtracking") as session:
    result = session.find_plan(state, tasks)
```

This is the same requirement as the `backtracking_poetry` example, which also relies on action-level failure triggering method-level backtracking.

## Two-Server Architecture

1. **Server 1: phonetics-server** (Rhyme Selection, Steering & Verification)
   - `select_rhyme_target`: Choose or look up a rhyme target word
   - `steer_target`: Replace target with an alternative rhyme word
   - `verify_line`: Check syllable count, meter, and rhyme constraints

2. **Server 2: llm-server** (Text Generation & Line Evaluation)
   - `generate_line`: Generate text constrained by target word and meter
   - `generate_line_free`: Free generation with syllable constraint only
   - `evaluate_line`: Evaluate quality, determine if revision needed

## HTN Decomposition

### Couplet (AA, 12 actions)
```
m_write_poem("couplet", topic)
+-- a_initialize_poem("couplet", topic)
+-- m_compose_couplet
|   +-- m_write_rhymed_line(0, "A", 8)                  [accepted: 4 actions]
|   |   +-- a_select_rhyme_target(0, "A")
|   |   +-- a_generate_line(0, 8)
|   |   +-- a_verify_line(0)
|   |   +-- m_evaluate_and_replan(0, "A", 8)
|   |       +-- m_accept_line -> a_evaluate_line(0)      [OK: line 0 not in revision set]
|   +-- m_write_rhymed_line(1, "A", 8)                   [revised: 6 actions]
|       +-- a_select_rhyme_target(1, "A")
|       +-- a_generate_line(1, 8)
|       +-- a_verify_line(1)
|       +-- m_evaluate_and_replan(1, "A", 8)
|           +-- m_accept_line -> a_evaluate_line(1)      [FAIL: line 1 in revision set]
|           +-- m_revise_line(1, "A", 8)
|               +-- a_steer_target(1, "A")
|               +-- a_generate_line(1, 8)
|               +-- a_verify_line(1)
+-- a_assemble_poem
```

### Haiku (5-7-5, 8 actions)
```
m_write_poem("haiku", topic)
+-- a_initialize_poem("haiku", topic)
+-- m_compose_haiku
|   +-- m_write_free_line(0, 5)
|   |   +-- a_generate_line_no_rhyme(0, 5)
|   |   +-- a_verify_line(0)
|   +-- m_write_free_line(1, 7)
|   |   +-- a_generate_line_no_rhyme(1, 7)
|   |   +-- a_verify_line(1)
|   +-- m_write_free_line(2, 5)
|       +-- a_generate_line_no_rhyme(2, 5)
|       +-- a_verify_line(2)
+-- a_assemble_poem
```

## File Structure

```
replanning_poetry/
+-- domain.py       # Domain definition with 8 actions and 10 methods
+-- problems.py     # Initial state definitions (3 scenarios)
+-- __init__.py     # Package initialization with get_problems()
+-- README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 8
- **Methods**: 10
- **Servers**: 2 (phonetics-server, llm-server)
- **Scenarios**: 3
- **Supported Forms**: 4 (couplet, limerick, haiku, sonnet)

## State Properties

### Poem Configuration
- `poem_form`: Poetic form name (str)
- `topic`: Poem topic/theme (str)
- `form_spec`: Full form specification dictionary (Dict)
- `num_lines`: Number of lines in the poem (int)
- `rhyme_scheme`: Rhyme labels per line (List)
- `meter`: Meter type (str)
- `syllables_per_line`: Target syllable counts (List[int])

### Workflow State
- `poem_initialized`: Initialization complete (bool) [ENABLER]
- `poem_complete`: Poem assembly complete (bool) [ENABLER]

### Rhyme Management
- `rhyme_registry`: Maps rhyme labels to target words (Dict[str, str])
- `line_targets`: Planned end-words per line (List[Optional[str]])
- `rhyme_target_selected`: Per-line target selection flags (Dict[int, bool])

### Revision Management (new in this domain)
- `lines_requiring_revision`: Lines that need steering (Set[int]) [DATA]
- `line_evaluated`: Per-line evaluation flags (Dict[int, bool]) [ENABLER]
- `line_steered`: Per-line steering flags (Dict[int, bool]) [ENABLER]

### Line Generation
- `lines`: Generated line texts (List[str])
- `line_generated`: Per-line generation flags (Dict[int, bool])
- `line_verified`: Per-line verification flags (Dict[int, bool])
- `verification_errors`: Per-line error lists (Dict[int, List[str]])

### Output
- `final_poem`: Assembled poem text (str)

## Actions Summary

### Initialization (1 action)
1. **a_initialize_poem**: Load form specification, initialize buffers, rhyme registry, and compute `lines_requiring_revision`

### Phonetics Server Actions (3 actions)
2. **a_select_rhyme_target**: Select or look up a rhyme target word for a line
3. **a_steer_target**: Replace target with an alternative rhyme word, reset generation flags
4. **a_verify_line**: Verify syllable count, meter, and rhyme constraints

### LLM Server Actions (3 actions)
5. **a_generate_line**: Generate a line constrained by target word and meter
6. **a_generate_line_no_rhyme**: Generate an unrhymed line (syllable constraint only)
7. **a_evaluate_line**: Evaluate quality; FAILS for lines requiring revision (triggers backtracking)

### Assembly (1 action)
8. **a_assemble_poem**: Join all verified lines into the final poem text

## Methods Summary

### Top-Level (1 method)
1. **m_write_poem**: Entry point -- initialize, compose by form, assemble

### Form-Specific Composition (4 methods)
2. **m_compose_couplet**: AA scheme, 2 lines
3. **m_compose_limerick**: AABBA scheme, 5 lines
4. **m_compose_haiku**: 5-7-5 syllables, 3 unrhymed lines
5. **m_compose_sonnet**: ABAB CDCD EFEF GG, 14 lines (3 quatrains + couplet)

### Structural Sub-Methods (1 method)
6. **m_write_quatrain**: ABAB cross-rhyme pattern, 4 lines

### Line-Level Methods (2 methods)
7. **m_write_rhymed_line**: select target -> generate -> verify -> evaluate/replan (3 actions + 1 sub-method)
8. **m_write_free_line**: generate freely -> verify (2 actions)

### Evaluation and Replanning Methods (2 methods, backtracking point)
9. **m_accept_line**: 1st method for m_evaluate_and_replan: a_evaluate_line (may fail)
10. **m_revise_line**: 2nd method for m_evaluate_and_replan: steer -> generate -> verify

## Workflow Enablers

The domain uses **workflow enabler** properties to ensure correct sequencing:

1. **Initialization**: `poem_initialized` must be True before any line operations
2. **Target Selection**: `rhyme_target_selected[i]` must be True before generating line `i`
3. **Generation**: `line_generated[i]` must be True before verifying line `i`
4. **Verification**: `line_verified[i]` must be True before evaluating line `i`
5. **Evaluation**: Either:
   - ACCEPT PATH: `line_evaluated[i]` = True (line accepted)
   - REVISE PATH: `line_steered[i]` = True -> regenerate -> re-verify
6. **Assembly**: All `line_verified[i]` must be True before assembling the poem

## Usage Examples

### Using PlannerSession (Recommended)

**Important:** This domain requires a backtracking-capable strategy (see [Planning Strategy Requirement](#planning-strategy-requirement)).

```python
import gtpyhop
from gtpyhop.examples.poetry.replanning_poetry import the_domain, problems

# Create planner session with backtracking strategy
with gtpyhop.PlannerSession(domain=the_domain, strategy="recursive_dfs", verbose=1) as session:
    # Get problem instance
    state, tasks, desc = problems.get_problems()['scenario_1_couplet_stars']

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
python benchmarking.py replanning_poetry
```

## Key Features

### 1. Post-Generation Evaluation and Revision
- After the standard select-generate-verify cycle, lines are evaluated
- Lines requiring revision trigger backtracking to a revision path
- The revision path steers to a new target and completely regenerates the line
- This models the paper's finding that the planned word is a "control knob"

### 2. HTN Backtracking for Replanning
- `m_evaluate_and_replan` has two registered methods (backtracking point)
- The planner tries `m_accept_line` first, falls back to `m_revise_line`
- Same mechanism as backtracking_poetry but at the evaluation level

### 3. Deterministic Revision Trigger
- `lines_requiring_revision` computed from rhyme scheme by `a_initialize_poem`
- Subsequent uses of each rhyme label require revision
- Ensures predictable plan lengths for benchmarking

### 4. GTPyhop 1.9.0+ Structure
- Single `domain.py` file with all actions and methods
- `problems.py` with Unified Scenario Block format (Configuration -> State -> Problem)
- `__init__.py` with `get_problems()` function for automatic discovery

### 5. Complete Docstrings
All actions and methods include complete documentation following the style guide

### 6. Code Markers
Actions use structured markers:
- `# BEGIN/END: Type Checking`
- `# BEGIN/END: State-Type Checks`
- `# BEGIN/END: Preconditions`
- `# BEGIN/END: Effects`

Methods use:
- `# BEGIN/END: Task Decomposition`

### 7. State Property Map
Comprehensive documentation of all state properties with:
- (E) for Effects, (P) for Preconditions
- [ENABLER] for workflow gates
- [DATA] for informational properties

## References

- **GTPyhop Documentation**: https://github.com/PCfVW/GTPyhop
- **Anthropic "Planning in Poems"**: Anthropic Research, March 2025
- **Structured Poetry Domain**: `examples/poetry/structured_poetry/`
- **Backtracking Poetry Domain**: `examples/poetry/backtracking_poetry/`
- **MCP Protocol**: https://modelcontextprotocol.io/

---
*Generated 2026-02-12*
