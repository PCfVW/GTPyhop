# Trunk Thumper Benchmarking — Quick Start Guide

## Overview

The benchmarking script (`benchmarking.py`) runs all scenarios in any Trunk Thumper sub-folder and reports planning performance. It uses a `TrunkThumperBenchmark` class that extends the shared benchmarking infrastructure from `ipc-2020-total-order/` to support task-list-based goals (the same pattern poetry uses).

## Prerequisites

- **GTPyhop 1.9.6+** installed
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

## Available Sub-Folders

The naming `sNN_<topic>` matches Section 12.NN of Troy Humphreys' chapter "Exploring HTN Planners through Example" in *Game AI Pro* (Steve Rabin, ed., CRC Press, 2015). Open the matching folder while reading the corresponding chapter section.

| # | Sub-folder | Chapter section | Scenarios | Strategy required |
|---|---|---|---|---|
| 1 | `s03_basic_attack_or_patrol` | §12.3 baseline | 2 | Any |
| 2 | `s06_recursive_trunk_replacement` | §12.6 recursion | 3 | Any |
| 3 | `s07_expected_effects_chase` | §12.7 expected effects | 3 (incl. 1 negative control that *should fail*) | Any |
| 4 | `s08_priority_methods` | §12.8 multi-method priority + WsIsTired | 4 | Any |
| 5 | `s09_simultaneous_navigation_and_guard` | §12.9 simultaneous behaviors | 3 | Any |
| 6 | `s10_partial_plans` | §12.10 partial-plan splits | 3 | Any |

**Total**: 18 scenarios across 6 sub-folders.

Strategy notes: every sub-folder works with the default `iterative_greedy` strategy because all required backtracking is encoded as method-precondition gates (rather than relying on downstream-failure backtracking). The `--strategy iterative_dfs_backtracking` option produces identical results in this collection and is useful for verifying the planner's robustness.

## Running the Benchmarking Script

### Basic Usage

```bash
cd src/gtpyhop/examples/trunk_thumper

# List available sub-folders
python benchmarking.py --list-domains

# Run a specific sub-folder
python benchmarking.py s03_basic_attack_or_patrol
python benchmarking.py s06_recursive_trunk_replacement
python benchmarking.py s07_expected_effects_chase
python benchmarking.py s08_priority_methods
python benchmarking.py s09_simultaneous_navigation_and_guard
python benchmarking.py s10_partial_plans
```

### Strategy Selection

```bash
# Default (iterative_greedy)
python benchmarking.py s08_priority_methods

# Full backtracking
python benchmarking.py s08_priority_methods --strategy iterative_dfs_backtracking

# Recursive DFS
python benchmarking.py s08_priority_methods --strategy recursive_dfs
```

### Command-Line Options

```bash
# Quiet output
python benchmarking.py s06_recursive_trunk_replacement --verbose 0

# Detailed planner output
python benchmarking.py s06_recursive_trunk_replacement --verbose 2

# Show import source (PyPI vs. local install)
python benchmarking.py --show-imports
```

### Expected Results

The s07 collection includes a deliberate negative-control scenario that **demonstrates expected-effects-related plan failure**:

- `scenario_3_expected_effects_negative_control` in `s07_expected_effects_chase/`

This scenario invokes a teaching variant (`a_nav_to_last_enemy_loc_demo_no_ee`) that omits the `[EXPECTED_EFFECT]` on `can_see_enemy`. The plan correctly fails, demonstrating *why* expected effects are needed. The benchmarking script reports this as `FAIL` — that's the intended behavior. See `s07_expected_effects_chase/README.md` for the full discussion.

All other 17 scenarios should report `PASS`.

## Running All Sub-Folders at Once

There's no built-in "run everything" command, but a shell loop works:

```bash
cd src/gtpyhop/examples/trunk_thumper
for d in s03_* s06_* s07_* s08_* s09_* s10_*; do
    echo "=== $d ==="
    python benchmarking.py "$d" --verbose 0
done
```

PowerShell equivalent:

```powershell
cd src/gtpyhop/examples/trunk_thumper
Get-ChildItem -Directory -Filter "s*" | ForEach-Object {
    Write-Host "=== $($_.Name) ==="
    python benchmarking.py $_.Name --verbose 0
}
```

## Running Doctests for All Sub-Folders

Each sub-folder's `problems.py` has comprehensive doctests:

```bash
python -m doctest src/gtpyhop/examples/trunk_thumper/s03_basic_attack_or_patrol/problems.py
python -m doctest src/gtpyhop/examples/trunk_thumper/s06_recursive_trunk_replacement/problems.py
python -m doctest src/gtpyhop/examples/trunk_thumper/s07_expected_effects_chase/problems.py
python -m doctest src/gtpyhop/examples/trunk_thumper/s08_priority_methods/problems.py
python -m doctest src/gtpyhop/examples/trunk_thumper/s09_simultaneous_navigation_and_guard/problems.py
python -m doctest src/gtpyhop/examples/trunk_thumper/s10_partial_plans/problems.py
```

A successful run produces no output (verbose mode `-v` shows each test).

## Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, pp. 149–167.

---
*Generated 2026-05-15*
