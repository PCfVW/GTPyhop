# Bidirectional Planning Poetry HTN Domain

## Overview

This example demonstrates **decomposed line construction** for neuro-symbolic poetry generation using GTPyhop 1.9.0+. Instead of treating line generation as a black box (as in the structured_poetry domain), this domain splits it into two explicit steps: backward transition planning and surface text generation.

This models Anthropic's "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" (March 2025) finding that Claude 3.5 Haiku uses **backward reasoning** from the planned end-word to determine intermediate words in a line. For example, the word "like" in "His hunger was like a starving rabbit" is determined by backward reasoning from the target "rabbit". The model builds a structural skeleton before generating fluent text.

## Difference from Structured Poetry

| Aspect | Structured Poetry | Bidirectional Planning Poetry |
|--------|------------------|------------------------------|
| Actions | 6 | 7 (+plan_transition, +generate_surface_text, -generate_line) |
| Line generation | 1 action (`a_generate_line`) | 2 actions (plan transition + generate surface text) |
| Actions per rhymed line | 3 (select + generate + verify) | 4 (select + transition + surface + verify) |
| Couplet plan length | 8 | 10 |
| Limerick plan length | 17 | 22 |
| Sonnet plan length | 44 | 58 |

## Benchmarking Scenarios

| Scenario | Form | Topic | Actions | Status |
|----------|------|-------|---------|--------|
| `scenario_1_couplet_stars` | Couplet | stars in the night sky | 10 | VALID |
| `scenario_2_limerick_cat` | Limerick | a clever cat | 22 | VALID |
| `scenario_3_haiku_ocean` | Haiku | the ocean at dawn | 8 | VALID |

### Plan Length Formulas

| Form | Formula | Actions |
|------|---------|---------|
| Couplet | 2 + (4 x 2) | 10 |
| Limerick | 2 + (4 x 5) | 22 |
| Haiku | 2 + (2 x 3) | 8 |
| Sonnet | 2 + (4 x 14) | 58 |

Where: `init + assemble + (select + transition + surface + verify) x lines` for rhymed forms, and `init + assemble + (generate + verify) x lines` for unrhymed forms (haiku).

## Two-Server Architecture

1. **Server 1: phonetics-server** (Rhyme Selection & Verification)
   - `select_rhyme_target`: Choose or look up a rhyme target word
   - `verify_line`: Check syllable count, meter, and rhyme constraints

2. **Server 2: llm-server** (Transition Planning & Text Generation)
   - `plan_transition`: Backward-plan intermediate words from target end-word
   - `generate_surface_text`: Produce fluent text from structural skeleton
   - `generate_line_free`: Free generation with syllable constraint only

## HTN Decomposition

### Couplet (AA, 10 actions)
```
m_write_poem("couplet", topic)
+-- a_initialize_poem("couplet", topic)
+-- m_compose_couplet
|   +-- m_write_rhymed_line(0, "A", 8)
|   |   +-- a_select_rhyme_target(0, "A")          [Server 1: forward planning]
|   |   +-- a_plan_transition(0)                    [Server 2: backward planning]
|   |   +-- a_generate_surface_text(0, 8)           [Server 2: surface generation]
|   |   +-- a_verify_line(0)                        [Server 1: check constraints]
|   +-- m_write_rhymed_line(1, "A", 8)
|       +-- a_select_rhyme_target(1, "A")          [Server 1: rhymes with line 0]
|       +-- a_plan_transition(1)                    [Server 2: backward planning]
|       +-- a_generate_surface_text(1, 8)           [Server 2: surface generation]
|       +-- a_verify_line(1)                        [Server 1: check constraints]
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
bidirectional_planning_poetry/
+-- domain.py       # Domain definition with 7 actions and 8 methods
+-- problems.py     # Initial state definitions (3 scenarios)
+-- __init__.py     # Package initialization with get_problems()
+-- README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 7
- **Methods**: 8
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

### Transition Planning (new in this domain)
- `transition_plan`: Planned intermediate words/phrases per line (Dict[int, str])
- `transition_planned`: Per-line transition planning flags (Dict[int, bool])

### Line Generation
- `lines`: Generated line texts (List[str])
- `line_generated`: Per-line generation flags (Dict[int, bool])
- `line_verified`: Per-line verification flags (Dict[int, bool])
- `verification_errors`: Per-line error lists (Dict[int, List[str]])

### Output
- `final_poem`: Assembled poem text (str)

## Actions Summary

### Initialization (1 action)
1. **a_initialize_poem**: Load form specification, initialize buffers, rhyme registry, and transition plan buffers

### Phonetics Server Actions (2 actions)
2. **a_select_rhyme_target**: Select or look up a rhyme target word for a line
3. **a_verify_line**: Verify syllable count, meter, and rhyme constraints

### LLM Server Actions (3 actions)
4. **a_plan_transition**: Backward-plan intermediate words from target end-word
5. **a_generate_surface_text**: Generate fluent text from transition plan + target
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

### Line-Level Methods (2 methods)
7. **m_write_rhymed_line**: select target -> plan transition -> generate surface text -> verify (4 actions)
8. **m_write_free_line**: generate freely -> verify (2 actions)

## Usage Examples

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.poetry.bidirectional_planning_poetry import the_domain, problems

# Create planner session
with gtpyhop.PlannerSession(domain=the_domain, verbose=1) as session:
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
python benchmarking.py bidirectional_planning_poetry
```

## Workflow Enablers

The domain uses **workflow enabler** properties to ensure correct sequencing:

1. **Initialization**: `poem_initialized` must be True before any line operations
2. **Target Selection**: `rhyme_target_selected[i]` must be True before planning transition for line `i`
3. **Transition Planning**: `transition_planned[i]` must be True before generating surface text for line `i`
4. **Surface Generation**: `line_generated[i]` must be True before verifying line `i`
5. **Assembly**: All `line_verified[i]` must be True before assembling the poem

## Key Features

### 1. Bidirectional Construction Pipeline
- Replaces the single `a_generate_line` with a 2-action pipeline
- Models the LLM's backward reasoning from the target word to plan intermediate words
- `a_plan_transition` reasons backward: target word -> structural skeleton
- `a_generate_surface_text` fills forward: skeleton -> fluent text

### 2. GTPyhop 1.9.0+ Structure
- Single `domain.py` file with all actions and methods
- `problems.py` with Unified Scenario Block format (Configuration -> State -> Problem)
- `__init__.py` with `get_problems()` function for automatic discovery

### 3. Complete Docstrings
All actions and methods include complete documentation following the style guide

### 4. Code Markers
Actions use structured markers:
- `# BEGIN/END: Type Checking`
- `# BEGIN/END: State-Type Checks`
- `# BEGIN/END: Preconditions`
- `# BEGIN/END: Effects`

Methods use:
- `# BEGIN/END: Task Decomposition`

### 5. State Property Map
Comprehensive documentation of all state properties with:
- (E) for Effects, (P) for Preconditions
- [ENABLER] for workflow gates
- [DATA] for informational properties

## References

- **GTPyhop Documentation**: https://github.com/PCfVW/GTPyhop
- **Anthropic "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)"**: Anthropic Research, March 2025
- **Structured Poetry Domain**: `examples/poetry/structured_poetry/`
- **MCP Protocol**: https://modelcontextprotocol.io/

---
*Generated 2026-02-12*
