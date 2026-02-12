# Structured Poetry HTN Domain

## Overview

This example demonstrates **neuro-symbolic poetry generation** using GTPyhop 1.8.0+. An HTN planner produces structural plans (form, rhyme scheme, meter constraints) while leaf-level actions are delegated to external MCP servers for text generation and phonetic verification.

This domain is motivated by Anthropic's "Planning in Poems" (March 2025) discovery that Claude 3.5 Haiku plans ahead when writing rhyming poetry, activating candidate end-of-line words before writing each line. This domain makes that implicit planning **explicit** via HTN decomposition.

## Benchmarking Scenarios

| Scenario | Form | Topic | Actions | Status |
|----------|------|-------|---------|--------|
| `scenario_1_couplet_autumn` | Couplet | autumn leaves falling | 8 | VALID |
| `scenario_2_limerick_cat` | Limerick | a clever cat | 17 | VALID |
| `scenario_3_haiku_ocean` | Haiku | the ocean at dawn | 8 | VALID |
| `scenario_4_sonnet_time` | Sonnet | the passage of time | 44 | VALID |
| `scenario_5_couplet_stars` | Couplet | stars in the night sky | 8 | VALID |
| `scenario_6_limerick_code` | Limerick | a programmer debugging code | 17 | VALID |

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
   - `select_rhyme_target`: Select or match rhyme target words
   - `verify_line`: Check syllable count, meter, and rhyme constraints

2. **Server 2: llm-server** (Text Generation via LLM)
   - `generate_line`: Constrained generation with rhyme target and meter
   - `generate_line_free`: Free generation with syllable constraint only

## HTN Decomposition

### Couplet (AA, 8 actions)
```
m_write_poem("couplet", topic)
+-- a_initialize_poem("couplet", topic)
+-- m_compose_couplet
|   +-- m_write_rhymed_line(0, "A", 8)
|   |   +-- a_select_rhyme_target(0, "A")    [Server 1]
|   |   +-- a_generate_line(0, 8)            [Server 2]
|   |   +-- a_verify_line(0)                 [Server 1]
|   +-- m_write_rhymed_line(1, "A", 8)
|       +-- a_select_rhyme_target(1, "A")    [Server 1]
|       +-- a_generate_line(1, 8)            [Server 2]
|       +-- a_verify_line(1)                 [Server 1]
+-- a_assemble_poem
```

### Haiku (5-7-5, 8 actions)
```
m_write_poem("haiku", topic)
+-- a_initialize_poem("haiku", topic)
+-- m_compose_haiku
|   +-- m_write_free_line(0, 5)
|   |   +-- a_generate_line_no_rhyme(0, 5)   [Server 2]
|   |   +-- a_verify_line(0)                 [Server 1]
|   +-- m_write_free_line(1, 7)
|   |   +-- a_generate_line_no_rhyme(1, 7)   [Server 2]
|   |   +-- a_verify_line(1)                 [Server 1]
|   +-- m_write_free_line(2, 5)
|       +-- a_generate_line_no_rhyme(2, 5)   [Server 2]
|       +-- a_verify_line(2)                 [Server 1]
+-- a_assemble_poem
```

## File Structure

```
structured_poetry/
+-- domain.py       # Domain definition with 6 actions and 8 methods
+-- problems.py     # Initial state definitions (6 scenarios)
+-- __init__.py     # Package initialization with get_problems()
+-- README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 6
- **Methods**: 8
- **Servers**: 2 (phonetics-server, llm-server)
- **Scenarios**: 6
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

### Phonetics Server Actions (2 actions)
2. **a_select_rhyme_target**: Select or match a rhyme target word for a line
3. **a_verify_line**: Verify syllable count, meter, and rhyme constraints

### LLM Server Actions (2 actions)
4. **a_generate_line**: Generate a rhyme-constrained line of poetry
5. **a_generate_line_no_rhyme**: Generate an unrhymed line (syllable constraint only)

### Assembly (1 action)
6. **a_assemble_poem**: Join all verified lines into the final poem text

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
7. **m_write_rhymed_line**: select rhyme target -> generate -> verify (3 actions)
8. **m_write_free_line**: generate freely -> verify (2 actions)

## Usage Examples

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.poetry.structured_poetry import the_domain, problems

# Create planner session
with gtpyhop.PlannerSession(domain=the_domain, verbose=1) as session:
    # Get problem instance
    state, tasks, desc = problems.get_problems()['scenario_1_couplet_autumn']

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
python benchmarking.py structured_poetry
```

## Workflow Enablers

The domain uses **workflow enabler** properties to ensure correct sequencing:

1. **Initialization**: `poem_initialized` must be True before any line operations
2. **Rhyme Selection**: `rhyme_target_selected[i]` must be True before generating rhymed line `i`
3. **Line Generation**: `line_generated[i]` must be True before verifying line `i`
4. **Assembly**: All `line_verified[i]` must be True before assembling the poem

## Key Features

### 1. GTPyhop 1.8.0+ Structure
- Single `domain.py` file with all actions and methods
- `problems.py` with Unified Scenario Block format (Configuration -> State -> Problem)
- `__init__.py` with `get_problems()` function for automatic discovery

### 2. Complete Docstrings
All actions and methods include complete documentation following the style guide

### 3. Code Markers
Actions use structured markers:
- `# BEGIN/END: Type Checking`
- `# BEGIN/END: State-Type Checks`
- `# BEGIN/END: Preconditions`
- `# BEGIN/END: Effects`

Methods use:
- `# BEGIN/END: Task Decomposition`

### 4. State Property Map
Comprehensive documentation of all state properties with:
- (E) for Effects, (P) for Preconditions
- [ENABLER] for workflow gates
- [DATA] for informational properties

## References

- **GTPyhop Documentation**: https://github.com/dananau/GTPyhop
- **Anthropic "Planning in Poems"**: Anthropic Research, March 2025
- **MCP Protocol**: https://modelcontextprotocol.io/

---
*Generated 2026-02-11*
