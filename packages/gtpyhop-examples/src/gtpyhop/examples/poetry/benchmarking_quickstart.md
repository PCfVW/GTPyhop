# Poetry Benchmarking - Quick Start Guide

## Overview

The benchmarking script (`benchmarking.py`) runs poetry domain scenarios and reports planning performance. It uses a `PoetryBenchmark` class that extends the shared benchmarking infrastructure from `ipc-2020-total-order/` to support task-list-based goals (rather than goal dictionaries).

## Prerequisites

- **GTPyhop 1.9.0+** installed
- **psutil** package (for resource tracking)
- Python 3.8 or later

### Installing Dependencies

```bash
pip install gtpyhop psutil
```

Or for local development:
```bash
cd C:\Users\Eric JACOPIN\Documents\Code\Source\GTPyhop
pip install -e .
pip install psutil
```

## Available Examples

| # | Example | Description | Scenarios | Actions | Strategy Required |
|---|---------|-------------|-----------|---------|-------------------|
| 1 | `structured_poetry` | Baseline poetry generation with one method per task | 6 (couplet, limerick, haiku, sonnet) | 8-44 | Any |
| 2 | `backtracking_poetry` | Extension testing HTN backtracking for rhyme selection | 3 (couplet, limerick, haiku) | 8-17 | Backtracking* |
| 3 | `candidate_planning_poetry` | Multi-candidate rhyme selection pipeline | 3 (couplet, limerick, haiku) | 8-27 | Any |
| 4 | `bidirectional_planning_poetry` | Decomposed backward line construction | 3 (couplet, limerick, haiku) | 8-22 | Any |
| 5 | `replanning_poetry` | Post-generation evaluation and steering/revision | 3 (couplet, limerick, haiku) | 8-28 | Backtracking* |
| 6 | `formal_mechanism_poetry` | Three planning mechanisms from Anthropic's [paper](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems) | 3 (full, commitment, three-stage) | 7-19 | Any |
| 7 | `feature_space_poetry` | Feature-space interventions with measured data | 12 (3 models x 4 scenarios) | 9-34 | Backtracking* |

\* Backtracking required: examples 2, 5 for rhymed forms; example 7 for scenarios with multiple candidates.

All examples follow the **GTPyhop 1.9.0+ style guide** with unified scenario block format.

## Running the Benchmarking Script

### Basic Usage

```bash
cd src/gtpyhop/examples/poetry

# List available domains
python benchmarking.py --list-domains

# Run structured poetry scenarios (works with default strategy)
python benchmarking.py structured_poetry

# Run candidate planning poetry scenarios (works with default strategy)
python benchmarking.py candidate_planning_poetry

# Run bidirectional planning poetry scenarios (works with default strategy)
python benchmarking.py bidirectional_planning_poetry

# Run formal mechanism poetry scenarios (works with default strategy)
python benchmarking.py formal_mechanism_poetry

# Run backtracking poetry scenarios (requires backtracking strategy)
python benchmarking.py backtracking_poetry --strategy recursive_dfs

# Run replanning poetry scenarios (requires backtracking strategy)
python benchmarking.py replanning_poetry --strategy iterative_dfs_backtracking

# Run feature space poetry scenarios (requires backtracking strategy)
python benchmarking.py feature_space_poetry --strategy iterative_dfs_backtracking
```

### Command-Line Options

```bash
# Run with minimal output (verbosity 0)
python benchmarking.py structured_poetry --verbose 0

# Run with detailed output (verbosity 2)
python benchmarking.py structured_poetry --verbose 2

# Run with maximum debugging output (verbosity 3)
python benchmarking.py backtracking_poetry --strategy recursive_dfs --verbose 3

# Run using legacy mode (global state, not recommended)
python benchmarking.py structured_poetry --legacy-mode

# Combine options
python benchmarking.py replanning_poetry --strategy recursive_dfs --verbose 2
```

### Planning Strategies

The `--strategy` option selects the planning strategy:

| Strategy | Backtracking | Default | When to Use |
|----------|-------------|---------|-------------|
| `iterative_greedy` | None | Yes | Examples 1, 3, 4, 6 (no backtracking needed) |
| `recursive_dfs` | Via call stack | No | Examples 2, 5, 7 (backtracking required) |
| `iterative_dfs_backtracking` | Via explicit stack | No | Examples 2, 5, 7 (backtracking required) |

**Note:** Running examples 2, 5, or 7 without a backtracking strategy will produce `False` for scenarios that require backtracking. This is expected behavior, not a bug.

### Verbosity Levels

- **0**: Silent (only final summary)
- **1**: Normal (default) - shows plan found/not found
- **2**: Detailed - shows task decomposition and method selection
- **3**: Debug - shows all internal planner operations

### Planning Modes

- **session** (default): Uses PlannerSession (thread-safe, recommended for GTPyhop 1.9.0+)
- **legacy**: Uses global state (enabled with `--legacy-mode` flag, not recommended)

## Running with Different Planning Strategies via Python API

For more control, use the Python API directly:

```python
import gtpyhop
from gtpyhop import PlannerSession
from gtpyhop.examples.poetry.replanning_poetry import the_domain, get_problems

problems = get_problems()
state, tasks, desc = problems['scenario_1_couplet_stars']

# Recursive DFS (backtracks via Python call stack)
with PlannerSession(domain=the_domain, strategy="recursive_dfs", verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, tasks)
        print(f"Recursive DFS: {len(result.plan)} actions" if result.success else "Failed")

# Iterative DFS Backtracking (backtracks via explicit stack)
with PlannerSession(domain=the_domain, strategy="iterative_dfs_backtracking", verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, tasks)
        print(f"Iterative DFS BT: {len(result.plan)} actions" if result.success else "Failed")
```

## Expected Results by Strategy

### Examples 1, 3, 4 (No Backtracking Needed)

All three strategies produce identical plans for these examples.

#### Structured Poetry

| Scenario | Actions |
|----------|---------|
| `scenario_1_couplet_autumn` | 8 |
| `scenario_2_limerick_cat` | 17 |
| `scenario_3_haiku_ocean` | 8 |
| `scenario_4_sonnet_time` | 44 |
| `scenario_5_couplet_stars` | 8 |
| `scenario_6_limerick_code` | 17 |

#### Candidate Planning Poetry

| Scenario | Actions |
|----------|---------|
| `scenario_1_couplet_stars` | 12 |
| `scenario_2_limerick_cat` | 27 |
| `scenario_3_haiku_ocean` | 8 |

#### Bidirectional Planning Poetry

| Scenario | Actions |
|----------|---------|
| `scenario_1_couplet_stars` | 10 |
| `scenario_2_limerick_cat` | 22 |
| `scenario_3_haiku_ocean` | 8 |

### Example 2: Backtracking Poetry

| Scenario | Recursive DFS | Iterative Greedy | Iterative DFS BT |
|----------|:---:|:---:|:---:|
| `scenario_1_couplet_stars` | 8 | 8 | 8 |
| `scenario_2_limerick_cat` | 17 | **False** | 17 |
| `scenario_3_haiku_ocean` | 8 | 8 | 8 |

The limerick fails with iterative greedy because label "A" is used 3 times in the AABBA scheme, and `a_select_rhyme_target_strict` fails on the 3rd use. Without backtracking, the planner cannot recover by trying `m_write_rhymed_line_relaxed`.

### Example 5: Replanning Poetry

| Scenario | Recursive DFS | Iterative Greedy | Iterative DFS BT |
|----------|:---:|:---:|:---:|
| `scenario_1_couplet_stars` | 12 | **False** | 12 |
| `scenario_2_limerick_cat` | 28 | **False** | 28 |
| `scenario_3_haiku_ocean` | 8 | 8 | 8 |

The couplet and limerick fail with iterative greedy because `a_evaluate_line` fails for lines requiring revision (subsequent uses of each rhyme label). Without backtracking, the planner cannot recover by trying `m_revise_line` after `m_accept_line` fails.

### Example 6: Formal Mechanism Poetry (No Backtracking Needed)

| Scenario | Actions (all strategies) |
|----------|:---:|
| `scenario_1_full_mechanism` | 19 |
| `scenario_2_commitment_focus` | 7 |
| `scenario_3_three_stage` | 13 |

All scenarios succeed with any strategy. The domain registers three methods for `m_select_end_word`, but all current scenarios place the strongest candidate first, so the greedy planner never needs to backtrack.

### Example 7: Feature Space Poetry

Gemma 2 2B (426K):

| Scenario | Iterative DFS BT | Iterative Greedy |
|----------|:---:|:---:|
| `scenario_0_version_d_star_result` | 34 | 34 |
| `scenario_1_cheapest_first` | 34 | **False** |
| `scenario_2_planning_layer_only` | 9 | 9 |
| `scenario_3_different_group` | 10 | **False** |

Llama 3.2 1B (524K):

| Scenario | Iterative DFS BT | Iterative Greedy |
|----------|:---:|:---:|
| `scenario_4_llama_star_result` | 24 | 24 |
| `scenario_5_llama_sat_first` | 24 | **False** |
| `scenario_6_llama_output_layer` | 9 | 9 |
| `scenario_7_llama_different_group` | 10 | **False** |

Gemma 2 2B (2.5M):

| Scenario | Iterative DFS BT | Iterative Greedy |
|----------|:---:|:---:|
| `scenario_8_version_d_2_5m_star` | 34 | 34 |
| `scenario_9_2_5m_weakest_first` | 34 | **False** |
| `scenario_10_2_5m_planning_layer` | 9 | 9 |
| `scenario_11_2_5m_different_group` | 10 | **False** |

Scenarios 1, 3, 5, 7, 9, and 11 fail with iterative greedy because weaker candidates are tried first. Their measured probabilities fall below the threshold, and the greedy planner cannot backtrack to try the stronger candidate.

## Interpreting Results

### Successful Run Example

```
Loading domain: structured_poetry
Found 6 problems in structured_poetry

Running benchmarks for structured_poetry using Thread-Safe Sessions planning (strategy: iterative_greedy)...
Solving scenario_1_couplet_autumn...
Solving scenario_2_limerick_cat...
Solving scenario_3_haiku_ocean...
Solving scenario_4_sonnet_time...
Solving scenario_5_couplet_stars...
Solving scenario_6_limerick_code...

=== structured_poetry Benchmark Results ===

=== Benchmark Summary ===
Problem                      | Status | Plan Len | Time (s) |  CPU % | Mem D (KB) | Peak Mem (KB)
-----------------------------------------------------------------------------------------------
scenario_1_couplet_autumn    | PASS   |        8 |    0.001s |    0.0% |        ... |          ...
scenario_2_limerick_cat      | PASS   |       17 |    0.001s |    0.0% |        ... |          ...
scenario_3_haiku_ocean       | PASS   |        8 |    0.001s |    0.0% |        ... |          ...
scenario_4_sonnet_time       | PASS   |       44 |    0.002s |    0.0% |        ... |          ...
scenario_5_couplet_stars     | PASS   |        8 |    0.001s |    0.0% |        ... |          ...
scenario_6_limerick_code     | PASS   |       17 |    0.001s |    0.0% |        ... |          ...
```

### Expected Plan Lengths (Structured Poetry Baseline)

| Form | Formula | Actions |
|------|---------|---------|
| Couplet | 2 + (3 x 2) | 8 |
| Limerick | 2 + (3 x 5) | 17 |
| Haiku | 2 + (2 x 3) | 8 |
| Sonnet | 2 + (3 x 14) | 44 |

Where: `init + assemble + (select + generate + verify) x lines` for rhymed forms, and `init + assemble + (generate + verify) x lines` for unrhymed forms (haiku).

## Adding New Poetry Examples

To add a new poetry domain:

1. **Create a new subdirectory** under `poetry/` following the **GTPyhop 1.9.0+ style guide**:
   ```
   poetry/
   +-- your_new_example/
       +-- domain.py             # Required: domain creation + actions + methods
       +-- problems.py           # Required: defines problems with unified scenario blocks
       +-- __init__.py           # Required: exports domain and get_problems()
       +-- README.md             # Required
   ```

2. **Required files**:
   - `domain.py` - Must create domain, define all actions and methods following the [domain style guide](../../../../../../docs/gtpyhop_domain_style_guide.md)
   - `problems.py` - Must define problems using unified scenario blocks following the [problems style guide](../../../../../../docs/gtpyhop_problems_style_guide.md)
   - `__init__.py` - Must export `the_domain` and implement `get_problems()` function

3. **Run the benchmarking script** - It will automatically discover your new example:
   ```bash
   python benchmarking.py your_new_example
   # Or with backtracking if needed:
   python benchmarking.py your_new_example --strategy recursive_dfs
   ```

## Troubleshooting

### "Error: psutil module is required"

**Solution**: Install psutil:
```bash
pip install psutil
```

### "Could not import gtpyhop"

**Solution**: Install GTPyhop:
```bash
pip install gtpyhop
```

### "No module named 'your_domain_name'"

**Solution**: Ensure your domain directory has:
- `__init__.py` with proper exports
- `domain.py` with domain creation
- `problems.py` with unified scenario blocks

### "No plan found" for backtracking_poetry limerick

**This is expected behavior** with the default (iterative greedy) planner. The limerick requires backtracking. Use `--strategy recursive_dfs` or `--strategy iterative_dfs_backtracking`. See the "Planning Strategies" section above.

### "No plan found" for replanning_poetry couplet or limerick

**This is expected behavior** with the default (iterative greedy) planner. These scenarios require backtracking because `a_evaluate_line` fails for lines requiring revision. Use `--strategy recursive_dfs` or `--strategy iterative_dfs_backtracking`. See the "Planning Strategies" section above.

### "No plan found" for feature_space_poetry scenarios 1, 3, 5, 7, 9, or 11

**This is expected behavior** with the default (iterative greedy) planner. These scenarios order candidates so that weaker ones are tried first, and `a_evaluate_threshold` fails when the measured probability is below the threshold. Use `--strategy iterative_dfs_backtracking`. See the "Planning Strategies" section above.

### "No plan found" (other scenarios)

**Possible causes**:
- Initial state doesn't satisfy preconditions
- Methods or actions have bugs
- Task decomposition is incorrect

**Debug steps**:
1. Run with `--verbose 3` to see detailed planner output
2. Check that initial states have all required properties
3. Verify method preconditions match action effects

## Next Steps

- Review individual domain README.md files for detailed documentation
- Examine generated plans to understand task decomposition
- Compare planning strategies on the backtracking_poetry, replanning_poetry, and feature_space_poetry domains
- Add new poetry forms or domains following the style guides

---
*Updated 2026-02-23*
