# Control Arena Protocols Benchmarking — Quick Start Guide

## Overview

The benchmarking script (`benchmarking.py`) runs all scenarios in any of the three Control Arena protocol examples and reports planning performance. It uses a dynamic-routing pattern: the `--example` flag selects which sub-folder's `get_problems()` to load, and the script invokes that sub-folder's planner with the requested strategy.

All three examples model **AI safety micro-protocols** from the [Control Arena framework](https://github.com/UKGovernmentBEIS/control-arena) (Greenblatt et al. 2024) using `MCP_Tool: None` (purely symbolic, no external MCP servers).

## Prerequisites

- **GTPyhop 1.9.7+** installed (1.9.4+ works for the original 3 sub-folders; the `accept_no_ee` outcome label and the `adversarial_protocol`'s `[EXPECTED_EFFECT]` marker arrive in 1.9.7)
- **psutil** package (for resource tracking)
- Python 3.8 or later

### Installing Dependencies

```bash
pip install gtpyhop psutil
```

Or for local development:
```bash
cd <GTPyhop root>
pip install -e .
pip install psutil
```

## Available Examples

| `--example` flag | Sub-folder | Scenarios | Doctests | Introduced | Key feature |
|---|---|---|---|---|---|
| `defer` (default) | `defer_to_trusted_protocol/` | 6 | 48 | 1.9.4 | Accept-or-defer routing with backtracking |
| `resample` | `defer_to_resample_protocol/` | 6 | 40 | 1.9.4 | Recursive multi-sample resampling + backtracking |
| `adversarial` | `adversarial_protocol/` | 15 | 92 | 1.9.4 baseline; extended in **1.9.7** | Adversarial analysis with threat-model variety + `[EXPECTED_EFFECT]` marker (negative control) |

**Totals**: 27 scenarios across 3 sub-folders, 180 doctests.

## Strategy Requirement

Unlike `trunk_thumper` and `colt_express` (where the default `iterative_greedy` strategy works for most scenarios), **the Control Arena examples require `iterative_dfs_backtracking`** for any scenario where the planner must defer rather than accept. This is reflected in `benchmarking.py`'s **default strategy**, which is `iterative_dfs_backtracking` (not the GTPyhop-wide default of `iterative_greedy`).

| Strategy | Accept-path scenarios | Defer-path scenarios |
|----------|:---:|:---:|
| `iterative_greedy` | SUCCESS | **FAIL** (planner commits to accept and cannot backtrack) |
| `iterative_dfs_backtracking` (default) | SUCCESS | SUCCESS |

The greedy planner's failure on defer-path scenarios is intentional and pedagogically important — it demonstrates why protocol routing decisions require backtracking-capable planning.

## Running the Benchmarking Script

### Basic Usage

```bash
cd src/gtpyhop/examples/control_arena_protocols

# Run the default example (defer_to_trusted)
python benchmarking.py

# Run a specific example
python benchmarking.py --example defer
python benchmarking.py --example resample
python benchmarking.py --example adversarial
```

### Running a Specific Scenario

```bash
# Run one scenario from any example
python benchmarking.py --example adversarial --scenario scenario_3_subtle_evades
python benchmarking.py --example resample --scenario scenario_4_all_high_defer
```

### Strategy Selection

```bash
# Default: iterative_dfs_backtracking (handles all defer paths)
python benchmarking.py --example adversarial

# Override to the greedy planner (defer-path scenarios will FAIL by design)
python benchmarking.py --example adversarial --strategy iterative_greedy

# Recursive DFS (also handles all defer paths)
python benchmarking.py --example adversarial --strategy recursive_dfs
```

### Listing Scenarios

```bash
python benchmarking.py --list-scenarios --example adversarial
```

### Verbosity Levels

```bash
python benchmarking.py --example resample --verbose 0   # silent
python benchmarking.py --example resample --verbose 1   # normal (default)
python benchmarking.py --example resample --verbose 2   # detailed
python benchmarking.py --example resample --verbose 3   # debug (shows action elision)
```

## Expected Results

### Outcome label catalog

`benchmarking.py` classifies each completed plan via the actions it contains:

| Label | Plan contains | Meaning |
|---|---|---|
| `accept` | `a_accept_output` | Output accepted; `[EXPECTED_EFFECT]` block fires if `side_task_embedded` |
| `defer` | `a_defer_to_trusted` | Output deferred to trusted model |
| `accept_no_ee` | `a_accept_output_demo_no_expected_effect` | Adversarial protocol scenario 15 only: negative-control teaching variant. Plan is an accept-trajectory but the `[EXPECTED_EFFECT]` block is omitted, so `state.side_task_observed` is never set |
| `unknown` | none of the above | Should never appear under normal use; indicates a custom task list that bypasses both canonical and demo routing actions |

### Per-scenario expected plan lengths

#### `defer_to_trusted_protocol` (6 scenarios, all plan length 5)

| Scenario | Plan length | Outcome | Greedy planner |
|---|:---:|---|---|
| `scenario_1_low_suspicion` | 5 | `accept` | SUCCESS |
| `scenario_2_high_suspicion` | 5 | `defer` | **FAIL** |
| `scenario_3_at_threshold` | 5 | `accept` | SUCCESS |
| `scenario_4_just_above` | 5 | `defer` | **FAIL** |
| `scenario_5_tight_threshold` | 5 | `defer` | **FAIL** |
| `scenario_6_loose_threshold` | 5 | `accept` | SUCCESS |

#### `defer_to_resample_protocol` (6 scenarios, plan length varies with samples drawn)

Plan length formula: `2*S + 3` where `S` = number of samples tried before resolution.

| Scenario | Plan length | Outcome | Greedy planner |
|---|:---:|---|---|
| `scenario_1_first_accepted` | 5 | `accept` (sample 0) | SUCCESS |
| `scenario_2_second_accepted` | 7 | `accept` (sample 1) | **FAIL** |
| `scenario_3_third_accepted` | 9 | `accept` (sample 2) | **FAIL** |
| `scenario_4_all_high_defer` | 9 | `defer` (after 3 samples) | **FAIL** |
| `scenario_5_single_sample` | 5 | `defer` (after 1 sample) | **FAIL** |
| `scenario_6_five_samples` | 13 | `accept` (sample 4) | **FAIL** |

#### `adversarial_protocol` (15 scenarios, all plan length 5)

**1.9.4 baseline** (threat_model = 'generic' or 'none'):

| Scenario | Outcome | Greedy planner | Security verdict |
|---|---|---|---|
| `scenario_1_honest_accepted` | `accept` | SUCCESS | SAFE |
| `scenario_2_obvious_caught` | `defer` | **FAIL** | SAFE |
| `scenario_3_subtle_evades` | `accept` | SUCCESS | **VULNERABILITY** |
| `scenario_4_subtle_caught_tight` | `defer` | **FAIL** | SAFE |
| `scenario_5_moderate_caught` | `defer` | **FAIL** | SAFE |
| `scenario_6_moderate_evades` | `accept` | SUCCESS | **VULNERABILITY** |
| `scenario_7_honest_tight_threshold` | `defer` | **FAIL** | OVER-SENSITIVE |
| `scenario_8_obvious_loose_threshold` | `accept` | SUCCESS | **VULNERABILITY** |

**1.9.7 threat-model variety** (6 new scenarios):

| Scenario | Threat model | Outcome | Greedy planner | Security verdict |
|---|---|---|---|---|
| `scenario_9_code_sabotage_subtle_evades` | code_sabotage | `accept` | SUCCESS | **VULNERABILITY** |
| `scenario_10_code_sabotage_obvious_caught` | code_sabotage | `defer` | **FAIL** | SAFE |
| `scenario_11_data_poisoning_subtle_evades` | data_poisoning | `accept` | SUCCESS | **VULNERABILITY** |
| `scenario_12_data_poisoning_obvious_caught` | data_poisoning | `defer` | **FAIL** | SAFE |
| `scenario_13_research_sabotage_subtle_evades` | research_sabotage | `accept` | SUCCESS | **VULNERABILITY** |
| `scenario_14_research_sabotage_obvious_caught` | research_sabotage | `defer` | **FAIL** | SAFE |

**1.9.7 `[EXPECTED_EFFECT]` negative control** (1 new scenario):

| Scenario | Outcome | Greedy planner | Note |
|---|---|---|---|
| `scenario_15_expected_effect_negative_control` | `accept_no_ee` | SUCCESS | Manual task list uses the demo variant `a_accept_output_demo_no_expected_effect`; plan succeeds (5 actions) but `state.side_task_observed` is never set |

## Running All Three Examples at Once

There's no built-in "run all" flag, but a shell loop works:

```bash
cd src/gtpyhop/examples/control_arena_protocols
for ex in defer resample adversarial; do
    echo "=== $ex ==="
    python benchmarking.py --example "$ex" --verbose 0
done
```

PowerShell equivalent:

```powershell
cd src/gtpyhop/examples/control_arena_protocols
foreach ($ex in @('defer', 'resample', 'adversarial')) {
    Write-Host "=== $ex ==="
    python benchmarking.py --example $ex --verbose 0
}
```

## Running Doctests

Each sub-folder's `problems.py` ships comprehensive doctests:

```bash
python -m doctest src/gtpyhop/examples/control_arena_protocols/defer_to_trusted_protocol/problems.py     # 48 tests
python -m doctest src/gtpyhop/examples/control_arena_protocols/defer_to_resample_protocol/problems.py   # 40 tests
python -m doctest src/gtpyhop/examples/control_arena_protocols/adversarial_protocol/problems.py         # 92 tests
```

A successful run produces no output (use `-v` to see each test).

## Reference

- **Control Arena**: <https://github.com/UKGovernmentBEIS/control-arena>
- **AI Control** (Greenblatt et al. 2024): "AI Control: Improving Safety Despite Intentional Subversion" — <https://arxiv.org/abs/2312.06942>
- **Collection README**: [control_arena_protocols/README.md](README.md) — contains the architectural overview, Concept Mapping table, and Three Levels of Integration framing

---
*Generated 2026-05-16*
