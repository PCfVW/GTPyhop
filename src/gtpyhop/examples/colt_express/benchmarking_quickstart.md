# Colt Express Benchmarking — Quick Start Guide

## Overview

The benchmarking script (`benchmarking.py`) runs all scenarios in any Colt Express sub-folder and reports planning performance. It uses a `ColtExpressBenchmark` class that extends the shared benchmarking infrastructure from `ipc-2020-total-order/` to support task-list-based goals (the same pattern trunk_thumper and poetry use).

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

The naming `sN_<topic>` matches the build-order milestones of the collection. The numeric suffix is NOT a chapter section number — see the **Pattern source** column for the trunk_thumper sub-folder each one inherits its HTN pattern from. (For the canonical structural reference, see [`trunk_thumper/`](../trunk_thumper/) and its [chapter cross-walk](../trunk_thumper/README.md).)

| # | Sub-folder | Pattern source | Scenarios | Strategy required |
|---|---|---|---|---|
| 1 | `s1_minimal_turn` | trunk_thumper `s03` (baseline priority methods) | 3 | Any |
| 2 | `s3_marshal_expected_effects` | trunk_thumper `s07` (expected effects + negative control) | 3 (incl. 1 negative control that *should fail*) | Any |
| 3 | `s2_recursive_round` | trunk_thumper `s06` (recursion) | 3 | Any |
| 4 | `s4_character_priorities` | trunk_thumper `s08` (priority-method ladder) | 4 | Any |
| 5 | `s5_partial_plan_movement` | trunk_thumper `s10` (method-split partial plans) | 3 | Any |

**Total**: 16 scenarios across 5 sub-folders.

**Build order note**: the sub-folder numeric prefixes (`s1`, `s2`, `s3`, `s4`, `s5`) reflect the **build order** during initial development (`s1 → s3 → s2 → s4 → s5`, with s3 built second to lock the Marshal-aware state shape early). The folders are alphabetically `s1`/`s2`/`s3`/`s4`/`s5` and may be read in any order, but the natural reading order matches the pattern-source progression: s1 → s3 → s2 → s4 → s5.

Strategy notes: every sub-folder works with the default `iterative_greedy` strategy because all required dispatching is encoded as method-precondition gates (rather than relying on downstream-failure backtracking). The `--strategy iterative_dfs_backtracking` option produces identical results in this collection and is useful for verifying the planner's robustness.

## Running the Benchmarking Script

### Basic Usage

```bash
cd src/gtpyhop/examples/colt_express

# List available sub-folders
python benchmarking.py --list-domains

# Run a specific sub-folder
python benchmarking.py s1_minimal_turn
python benchmarking.py s3_marshal_expected_effects
python benchmarking.py s2_recursive_round
python benchmarking.py s4_character_priorities
python benchmarking.py s5_partial_plan_movement
```

### Strategy Selection

```bash
# Default (iterative_greedy)
python benchmarking.py s4_character_priorities

# Full backtracking
python benchmarking.py s4_character_priorities --strategy iterative_dfs_backtracking

# Recursive DFS
python benchmarking.py s4_character_priorities --strategy recursive_dfs
```

### Command-Line Options

```bash
# Quiet output
python benchmarking.py s2_recursive_round --verbose 0

# Detailed planner output
python benchmarking.py s2_recursive_round --verbose 2

# Show import source (PyPI vs. local install)
python benchmarking.py --show-imports
```

### Expected Results

The s3 collection includes a deliberate negative-control scenario that **demonstrates expected-effects-related plan failure**:

- `scenario_3_expected_effects_negative_control` in `s3_marshal_expected_effects/`

This scenario invokes a teaching variant (`a_move_demo_no_marshal_trigger`) that omits the `[EXPECTED_EFFECT]` block on the Marshal forced-escape. The plan correctly fails because the downstream `a_fire` action's precondition (shooter on roof) cannot be satisfied — demonstrating *why* `[EXPECTED_EFFECT]` is needed. The benchmarking script reports this as `FAIL (None)` — that's the intended behavior. See `s3_marshal_expected_effects/README.md` for the full discussion.

All other 15 scenarios should report `PASS` with the following plan lengths:

| Scenario | Plan length |
|---|---|
| `s1_minimal_turn/scenario_1_rob_loot_at_position` | 1 |
| `s1_minimal_turn/scenario_2_move_forward_no_loot` | 1 |
| `s1_minimal_turn/scenario_3_descend_and_rob` | 2 |
| `s3_marshal_expected_effects/scenario_1_move_into_marshal_then_fire_from_roof` | 2 |
| `s3_marshal_expected_effects/scenario_2_marshal_action_pushes_bandit` | 2 |
| `s2_recursive_round/scenario_1_one_round_three_turns` | 3 |
| `s2_recursive_round/scenario_2_longer_deck_resolution` | 6 |
| `s2_recursive_round/scenario_3_round_with_hostage_taking_event` | 4 |
| `s4_character_priorities/scenario_1_belle_immunity_redirects_fire` | 1 |
| `s4_character_priorities/scenario_2_tuco_fires_through_floor` | 1 |
| `s4_character_priorities/scenario_3_django_knockback_fire` | 1 |
| `s4_character_priorities/scenario_4_cheyenne_keeps_punched_purse` | 1 |
| `s5_partial_plan_movement/scenario_1_full_plan_long_horizon` | 2 |
| `s5_partial_plan_movement/scenario_2_partial_plan_pursue_strongbox` | 1 |
| `s5_partial_plan_movement/scenario_3_partial_plan_flee_marshal` | 1 |

## Running All Sub-Folders at Once

There's no built-in "run everything" command, but a shell loop works:

```bash
cd src/gtpyhop/examples/colt_express
for d in s1_* s2_* s3_* s4_* s5_*; do
    echo "=== $d ==="
    python benchmarking.py "$d" --verbose 0
done
```

PowerShell equivalent:

```powershell
cd src/gtpyhop/examples/colt_express
Get-ChildItem -Directory -Filter "s*" | ForEach-Object {
    Write-Host "=== $($_.Name) ==="
    python benchmarking.py $_.Name --verbose 0
}
```

## Running Doctests for All Sub-Folders

Each sub-folder's `problems.py` has comprehensive doctests:

```bash
python -m doctest src/gtpyhop/examples/colt_express/s1_minimal_turn/problems.py
python -m doctest src/gtpyhop/examples/colt_express/s2_recursive_round/problems.py
python -m doctest src/gtpyhop/examples/colt_express/s3_marshal_expected_effects/problems.py
python -m doctest src/gtpyhop/examples/colt_express/s4_character_priorities/problems.py
python -m doctest src/gtpyhop/examples/colt_express/s5_partial_plan_movement/problems.py
```

A successful run produces no output (verbose mode `-v` shows each test). The collection ships **124 doctests** total: 26 + 25 + 22 + 27 + 24.

## Reference

- Pattern catalog: [trunk_thumper collection](../trunk_thumper/) (Game AI Pro Chapter 12, Troy Humphreys, CRC Press 2015).
- Colt Express rulebook: Christophe Raimbault, Jordi Valbuena. Ludonaute / Asmodee, 2014. <http://www.coltexpress.ludonaute.fr>

---
*Generated 2026-05-16*
