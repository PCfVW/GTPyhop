# Backtracking Poetry HTN Domain

## Overview

This example extends the Structured Poetry domain to demonstrate **HTN backtracking** in GTPyhop. The domain provides two methods for writing a rhymed line — strict (exact rhyme) and relaxed (near-rhyme) — and the planner must backtrack from strict to relaxed when the exact rhyme family is exhausted.

This domain is designed as a **test harness** for comparing three planning strategies:

| Strategy | Limerick Result | Mechanism |
|----------|----------------|-----------|
| Recursive DFS | 17 actions (succeeds) | Backtracks via Python call stack |
| Iterative greedy | False (fails) | Commits to strict, cannot recover |
| Iterative DFS backtracking | 17 actions (succeeds) | Backtracks via explicit stack |

## Backtracking Mechanism

### The Problem
The `a_select_rhyme_target_strict` action fails when a rhyme label has already been used by 2+ lines (controlled by `MAX_STRICT_RHYME_USES = 2`). This simulates exhaustion of an exact rhyme family.

### The Trigger
In a limerick (AABBA), label "A" is used by lines 0, 1, and 4. When the planner reaches line 4:
- `a_select_rhyme_target_strict(4, "A")` counts 2 existing uses of "A" (lines 0, 1)
- Count >= `MAX_STRICT_RHYME_USES` -> returns `False`
- The planner must backtrack to try `m_write_rhymed_line_relaxed`

### The Recovery
`a_select_rhyme_target_relaxed` has no saturation check and always succeeds, using near-rhyme (slant rhyme) when the exact rhyme family is exhausted.

### Where Backtracking Does NOT Occur
- **Couplet (AA)**: Each label used max 2 times -> strict succeeds for both
- **Haiku**: No rhyme labels -> free lines only
- **Sonnet (ABAB CDCD EFEF GG)**: Each label used exactly 2 times -> strict succeeds

## Benchmarking Scenarios

| Scenario | Form | Topic | Actions | Backtracking? |
|----------|------|-------|---------|---------------|
| `scenario_1_couplet_stars` | Couplet | stars in the night sky | 8 | No |
| `scenario_2_limerick_cat` | Limerick | a clever cat | 17 | Yes (line 4) |
| `scenario_3_haiku_ocean` | Haiku | the ocean at dawn | 8 | No |

### Expected Results by Strategy

| Scenario | Recursive DFS | Iterative Greedy | Iterative DFS BT |
|----------|--------------|-----------------|------------------|
| scenario_1_couplet_stars | 8 actions | 8 actions | 8 actions |
| scenario_2_limerick_cat | 17 actions | **False** | 17 actions |
| scenario_3_haiku_ocean | 8 actions | 8 actions | 8 actions |

### Plan Length Formulas

| Form | Formula | Actions |
|------|---------|---------|
| Couplet | 2 + (3 x 2) | 8 |
| Limerick | 2 + (3 x 5) | 17 |
| Haiku | 2 + (2 x 3) | 8 |
| Sonnet | 2 + (3 x 14) | 44 |

Where: `init + assemble + (select + generate + verify) x lines` for rhymed forms, and `init + assemble + (generate + verify) x lines` for unrhymed forms (haiku).

## Two-Server Architecture

1. **Server 1: phonetics-server** (Rhyme Selection & Verification)
   - `select_rhyme_target` (strict): Exact rhyme, fails when label saturated
   - `select_rhyme_target` (relaxed): Near-rhyme, always succeeds
   - `verify_line`: Check syllable count, meter, and rhyme constraints

2. **Server 2: llm-server** (Text Generation via LLM)
   - `generate_line`: Constrained generation with rhyme target and meter
   - `generate_line_free`: Free generation with syllable constraint only

## HTN Decomposition

### Limerick (AABBA, 17 actions, backtracking at line 4)
```
m_write_poem("limerick", topic)
+-- a_initialize_poem("limerick", topic)
+-- m_compose_limerick
|   +-- m_write_rhymed_line(0, "A", 8)
|   |   +-- [strict] a_select_rhyme_target_strict(0, "A")  -> OK (1st A)
|   |   +-- a_generate_line(0, 8)
|   |   +-- a_verify_line(0)
|   +-- m_write_rhymed_line(1, "A", 8)
|   |   +-- [strict] a_select_rhyme_target_strict(1, "A")  -> OK (2nd A)
|   |   +-- a_generate_line(1, 8)
|   |   +-- a_verify_line(1)
|   +-- m_write_rhymed_line(2, "B", 5)
|   |   +-- [strict] a_select_rhyme_target_strict(2, "B")  -> OK (1st B)
|   |   +-- a_generate_line(2, 5)
|   |   +-- a_verify_line(2)
|   +-- m_write_rhymed_line(3, "B", 5)
|   |   +-- [strict] a_select_rhyme_target_strict(3, "B")  -> OK (2nd B)
|   |   +-- a_generate_line(3, 5)
|   |   +-- a_verify_line(3)
|   +-- m_write_rhymed_line(4, "A", 8)
|       +-- [strict FAILS] a_select_rhyme_target_strict(4, "A") -> FAIL (3rd A)
|       +-- [BACKTRACK to relaxed]
|       +-- [relaxed] a_select_rhyme_target_relaxed(4, "A") -> OK (near-rhyme)
|       +-- a_generate_line(4, 8)
|       +-- a_verify_line(4)
+-- a_assemble_poem
```

### Couplet (AA, 8 actions, no backtracking)
```
m_write_poem("couplet", topic)
+-- a_initialize_poem("couplet", topic)
+-- m_compose_couplet
|   +-- m_write_rhymed_line(0, "A", 8)
|   |   +-- [strict] a_select_rhyme_target_strict(0, "A")  -> OK (1st A)
|   |   +-- a_generate_line(0, 8)
|   |   +-- a_verify_line(0)
|   +-- m_write_rhymed_line(1, "A", 8)
|       +-- [strict] a_select_rhyme_target_strict(1, "A")  -> OK (2nd A)
|       +-- a_generate_line(1, 8)
|       +-- a_verify_line(1)
+-- a_assemble_poem
```

### Haiku (5-7-5, 8 actions, no backtracking)
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
backtracking_poetry/
+-- domain.py       # Domain definition with 7 actions and 9 methods
+-- problems.py     # Initial state definitions (3 scenarios)
+-- __init__.py     # Package initialization with get_problems()
+-- README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 7
- **Methods**: 9
- **Servers**: 2 (phonetics-server, llm-server)
- **Scenarios**: 3
- **Supported Forms**: 4 (couplet, limerick, haiku, sonnet)
- **Backtracking Points**: 1 (m_write_rhymed_line: strict vs. relaxed)

## Difference from Structured Poetry

| Aspect | Structured Poetry | Backtracking Poetry |
|--------|------------------|-------------------|
| Actions | 6 | 7 (+strict, +relaxed, -generic) |
| Methods | 8 | 9 (+strict, +relaxed, -generic) |
| Methods per `m_write_rhymed_line` | 1 | 2 (strict, relaxed) |
| Backtracking needed? | No | Yes (limerick) |
| Planning strategy matters? | No (identical plans) | Yes (greedy fails on limerick) |

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
- `rhyme_target_selected`: Per-line rhyme selection flags (Dict[int, bool])

### Line Generation
- `lines`: Generated line texts (List[str])
- `line_generated`: Per-line generation flags (Dict[int, bool])
- `line_verified`: Per-line verification flags (Dict[int, bool])
- `verification_errors`: Per-line error lists (Dict[int, List[str]])

### Output
- `final_poem`: Assembled poem text (str)

## Actions Summary

### Initialization (1 action)
1. **a_initialize_poem**: Load form specification, initialize buffers and rhyme registry

### Phonetics Server Actions (3 actions)
2. **a_select_rhyme_target_strict**: Select exact rhyme target; **fails** when label has 2+ uses
3. **a_select_rhyme_target_relaxed**: Select near-rhyme target; **always succeeds**
4. **a_verify_line**: Verify syllable count, meter, and rhyme constraints

### LLM Server Actions (2 actions)
5. **a_generate_line**: Generate a rhyme-constrained line of poetry
6. **a_generate_line_no_rhyme**: Generate an unrhymed line (syllable constraint only)

### Assembly (1 action)
7. **a_assemble_poem**: Join all verified lines into the final poem text

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

### Line-Level Methods (3 methods)
7. **m_write_rhymed_line_strict**: strict select -> generate -> verify (3 actions)
8. **m_write_rhymed_line_relaxed**: relaxed select -> generate -> verify (3 actions)
9. **m_write_free_line**: generate freely -> verify (2 actions)

## Usage Examples

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.poetry.backtracking_poetry import the_domain, problems

# Create planner session with recursive planning (supports backtracking)
with gtpyhop.PlannerSession(domain=the_domain, recursive=True, verbose=1) as session:
    # Get the limerick problem (requires backtracking)
    state, tasks, desc = problems.get_problems()['scenario_2_limerick_cat']

    # Find plan -- recursive planner will backtrack from strict to relaxed
    result = session.find_plan(state, tasks)

    if result.success:
        print(f"Plan found with {len(result.plan)} actions:")
        for i, action in enumerate(result.plan, 1):
            print(f"  {i}. {action[0]}")
```

### Using the benchmarking script

```bash
cd src/gtpyhop/examples/poetry
python benchmarking.py backtracking_poetry
```

## Workflow Enablers

The domain uses **workflow enabler** properties to ensure correct sequencing:

1. **Initialization**: `poem_initialized` must be True before any line operations
2. **Rhyme Selection**: `rhyme_target_selected[i]` must be True before generating rhymed line `i`
3. **Line Generation**: `line_generated[i]` must be True before verifying line `i`
4. **Assembly**: All `line_verified[i]` must be True before assembling the poem

## Key Features

### 1. HTN Backtracking Test Harness
- `m_write_rhymed_line` has TWO methods registered (strict, relaxed)
- Strict fails on 3rd+ use of a rhyme label, triggering backtracking
- Limerick (AABBA) is the key scenario: label A used 3 times

### 2. Strategy Comparison
- Greedy planner fails on limerick (no backtracking)
- Recursive DFS and iterative DFS BT both succeed (backtracking)
- Couplet and haiku succeed with all strategies (regression tests)

### 3. GTPyhop 1.8.0+ Structure
- Single `domain.py` file with all actions and methods
- `problems.py` with Unified Scenario Block format (Configuration -> State -> Problem)
- `__init__.py` with `get_problems()` function for automatic discovery

### 4. Complete Docstrings
All actions and methods include complete documentation following the style guide

### 5. Code Markers
Actions use structured markers:
- `# BEGIN/END: Type Checking`
- `# BEGIN/END: State-Type Checks`
- `# BEGIN/END: Preconditions`
- `# BEGIN/END: Effects`

Methods use:
- `# BEGIN/END: Task Decomposition`

## References

- **GTPyhop Documentation**: https://github.com/PCfVW/GTPyhop
- **Backtracking Design Report**: `gitignore/iterative_backtracking_find_plan.md`
- **Structured Poetry Domain**: `examples/poetry/structured_poetry/`
- **Anthropic "Planning in Poems"**: Anthropic Research, March 2025
- **MCP Protocol**: https://modelcontextprotocol.io/

---
*Generated 2026-02-11*
