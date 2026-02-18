# Candidate Planning Poetry HTN Domain

## Overview

This example demonstrates **multi-candidate rhyme selection** for neuro-symbolic poetry generation using GTPyhop 1.9.0+. Instead of selecting a single rhyme target directly (as in the structured_poetry domain), this domain generates N candidate end-words, ranks them by rhyme quality and semantic fit, then commits the top-ranked candidate.

This models Anthropic's "Planning in Poems" (March 2025) finding that Claude 3.5 Haiku **maintains multiple candidate end-of-line words simultaneously** before committing to one. Features at the newline token activate rhyming pattern detectors that propose candidates like "rabbit" and "habit", and the model selects the best fit.

## Difference from Structured Poetry

| Aspect | Structured Poetry | Candidate Planning Poetry |
|--------|------------------|--------------------------|
| Actions | 6 | 8 (+candidates, +rank, +commit, -select) |
| Rhyme selection | 1 action (`a_select_rhyme_target`) | 3 actions (generate → rank → commit) |
| Actions per rhymed line | 3 (select + generate + verify) | 5 (candidates + rank + commit + generate + verify) |
| Couplet plan length | 8 | 12 |
| Limerick plan length | 17 | 27 |
| Sonnet plan length | 44 | 72 |

## Benchmarking Scenarios

| Scenario | Form | Topic | Actions | Status |
|----------|------|-------|---------|--------|
| `scenario_1_couplet_stars` | Couplet | stars in the night sky | 12 | VALID |
| `scenario_2_limerick_cat` | Limerick | a clever cat | 27 | VALID |
| `scenario_3_haiku_ocean` | Haiku | the ocean at dawn | 8 | VALID |

### Plan Length Formulas

| Form | Formula | Actions |
|------|---------|---------|
| Couplet | 2 + (5 x 2) | 12 |
| Limerick | 2 + (5 x 5) | 27 |
| Haiku | 2 + (2 x 3) | 8 |
| Sonnet | 2 + (5 x 14) | 72 |

Where: `init + assemble + (candidates + rank + commit + generate + verify) x lines` for rhymed forms, and `init + assemble + (generate + verify) x lines` for unrhymed forms (haiku).

## Two-Server Architecture

1. **Server 1: phonetics-server** (Candidate Generation, Ranking & Verification)
   - `generate_rhyme_candidates`: Produce N candidate end-words
   - `rank_candidates`: Score by rhyme quality + semantic fit
   - `verify_line`: Check syllable count, meter, and rhyme constraints

2. **Server 2: llm-server** (Text Generation via LLM)
   - `generate_line`: Constrained generation with committed target and meter
   - `generate_line_free`: Free generation with syllable constraint only

## HTN Decomposition

### Couplet (AA, 12 actions)
```
m_write_poem("couplet", topic)
+-- a_initialize_poem("couplet", topic)
+-- m_compose_couplet
|   +-- m_write_rhymed_line(0, "A", 8)
|   |   +-- a_generate_rhyme_candidates(0, "A")   [Server 1: produce 5 candidates]
|   |   +-- a_rank_candidates(0)                   [Server 1: score & sort]
|   |   +-- a_commit_target(0, "A")                [local: commit top candidate]
|   |   +-- a_generate_line(0, 8)                  [Server 2: write toward target]
|   |   +-- a_verify_line(0)                       [Server 1: check constraints]
|   +-- m_write_rhymed_line(1, "A", 8)
|       +-- a_generate_rhyme_candidates(1, "A")   [Server 1: candidates rhyming with A]
|       +-- a_rank_candidates(1)                   [Server 1: score & sort]
|       +-- a_commit_target(1, "A")                [local: commit top candidate]
|       +-- a_generate_line(1, 8)                  [Server 2: write toward target]
|       +-- a_verify_line(1)                       [Server 1: check constraints]
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
candidate_planning_poetry/
+-- domain.py       # Domain definition with 8 actions and 8 methods
+-- problems.py     # Initial state definitions (3 scenarios)
+-- __init__.py     # Package initialization with get_problems()
+-- README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 8
- **Methods**: 8
- **Servers**: 2 (phonetics-server, llm-server)
- **Scenarios**: 3
- **Supported Forms**: 4 (couplet, limerick, haiku, sonnet)
- **Candidates per line**: 5 (configurable via `NUM_CANDIDATES`)

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

### Candidate Management (new in this domain)
- `candidates`: Candidate end-words per line (Dict[int, List[str]])
- `ranked_candidates`: Ranked candidates per line (Dict[int, List[str]])
- `num_candidates`: Number of candidates to generate (int)
- `candidates_generated`: Per-line candidate generation flags (Dict[int, bool])
- `candidates_ranked`: Per-line ranking flags (Dict[int, bool])

### Rhyme Management
- `rhyme_registry`: Maps rhyme labels to target words (Dict[str, str])
- `line_targets`: Committed end-words per line (List[Optional[str]])
- `rhyme_target_selected`: Per-line target commitment flags (Dict[int, bool])

### Line Generation
- `lines`: Generated line texts (List[str])
- `line_generated`: Per-line generation flags (Dict[int, bool])
- `line_verified`: Per-line verification flags (Dict[int, bool])
- `verification_errors`: Per-line error lists (Dict[int, List[str]])

### Output
- `final_poem`: Assembled poem text (str)

## Actions Summary

### Initialization (1 action)
1. **a_initialize_poem**: Load form specification, initialize buffers, rhyme registry, and candidate buffers

### Phonetics Server Actions (3 actions)
2. **a_generate_rhyme_candidates**: Produce N candidate end-words for a line
3. **a_rank_candidates**: Score and sort candidates by rhyme quality + semantic fit
4. **a_verify_line**: Verify syllable count, meter, and rhyme constraints

### Local Actions (1 action)
5. **a_commit_target**: Commit top-ranked candidate as line target, update rhyme registry

### LLM Server Actions (2 actions)
6. **a_generate_line**: Generate a rhyme-constrained line of poetry
7. **a_generate_line_no_rhyme**: Generate an unrhymed line (syllable constraint only)

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
7. **m_write_rhymed_line**: candidates -> rank -> commit -> generate -> verify (5 actions)
8. **m_write_free_line**: generate freely -> verify (2 actions)

## Usage Examples

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.poetry.candidate_planning_poetry import the_domain, problems

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
python benchmarking.py candidate_planning_poetry
```

## Workflow Enablers

The domain uses **workflow enabler** properties to ensure correct sequencing:

1. **Initialization**: `poem_initialized` must be True before any line operations
2. **Candidate Generation**: `candidates_generated[i]` must be True before ranking line `i`
3. **Candidate Ranking**: `candidates_ranked[i]` must be True before committing target for line `i`
4. **Target Commitment**: `rhyme_target_selected[i]` must be True before generating rhymed line `i`
5. **Line Generation**: `line_generated[i]` must be True before verifying line `i`
6. **Assembly**: All `line_verified[i]` must be True before assembling the poem

## Key Features

### 1. Multi-Candidate Pipeline
- Replaces the single `a_select_rhyme_target` with a 3-action pipeline
- Models the LLM's simultaneous consideration of multiple candidate words
- `NUM_CANDIDATES = 5` controls the candidate pool size

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
- **Anthropic "Planning in Poems"**: Anthropic Research, March 2025
- **Structured Poetry Domain**: `examples/poetry/structured_poetry/`
- **MCP Protocol**: https://modelcontextprotocol.io/

---
*Generated 2026-02-12*
