# Colt Express s5 — Partial-Plan Movement (method-split)

Pattern source: [trunk_thumper s10_partial_plans](../../trunk_thumper/s10_partial_plans/) (Game AI Pro Chapter 12.10, Troy Humphreys, CRC Press 2015).

## Overview

Demonstrates the **method-split for partial plans** pattern applied to Colt Express movement strategy. Two task names — `m_resolve_move_full_plan` (commits to a multi-action sequence upfront) and `m_resolve_move_partial_plan` (returns one state-conditioned action via a priority ladder) — invoked on the same state produce different plan lengths (2 vs 1), demonstrating partial planning's reactive character.

From Game AI Pro (p.166):

> There isn't much point to planning too far into the future since there is a good chance the world state could change, forcing our troll to make a different decision.

## Scenarios

| # | Scenario | Top-level task | Plan | Demonstrates |
|---|---|---|---|---|
| 1 | `scenario_1_full_plan_long_horizon` | `m_resolve_move_full_plan` | 2 | Pre-split: commits to `a_move` AND `a_robbery` upfront |
| 2 | `scenario_2_partial_plan_pursue_strongbox` | `m_resolve_move_partial_plan` | 1 | Post-split, SAME state as 1: `m_pursue_strongbox` returns just the move |
| 3 | `scenario_3_partial_plan_flee_marshal` | `m_resolve_move_partial_plan` | 1 | Post-split, marshal-adjacent state: `m_flee_marshal` moves Belle backward |

Scenarios 1 and 2 use the **same initial state** and differ only in which root task they invoke — that's the s10 idiom. Compare the plan lengths: that's the partial-plan story in a nutshell.

Verified via `python -m doctest -v problems.py` (24 tests passing).

## Domain structure

### Actions (5, all reused)

| Action | Source | Notes |
|---|---|---|
| `a_move(state, bandit, direction)` | Basic (s1-style) | The only action exercised by scenarios |
| `a_robbery(state, bandit, loot_token)` | Basic (s1-style) | Used by `m_resolve_move_full_plan` |
| `a_floor_change(state, bandit)` | Basic (s1-style) | Included for canonical completeness |
| `a_fire(state, shooter, target)` | From s3 | Included for canonical completeness |
| `a_punch(state, puncher, target)` | Simplified from s4 | Included for canonical completeness |

No new actions in s5 — the pattern is entirely about method structure.

### Methods (2 task names, 5 alternative methods)

```
Compound Task m_resolve_move_full_plan(bandit)
    Method m_resolve_move_full_plan            — pre-split, multi-action
        Subtasks [a_move forward, a_robbery <loot at destination>]

Compound Task m_resolve_move_partial_plan(bandit)
    Method m_flee_marshal                      — priority 1: marshal adjacent
        Subtasks [a_move(bandit, away)]
    Method m_pursue_strongbox                  — priority 2: strongbox in locomotive
        Subtasks [a_move(bandit, forward)]
    Method m_chase_richest_car                 — priority 3: any purse elsewhere
        Subtasks [a_move(bandit, toward richest)]
    Method m_move_default                      — fallback: just move forward
        Subtasks [a_move(bandit, forward)]
```

Each partial-plan method returns exactly **one** subtask — that's the method-split essence. If a future re-plan is run on the updated state, the planner will dispatch to the now-applicable method based on the new state.

### Helper functions

- `_h_pick_loot_to_rob(state, car)` — reused
- `_h_marshal_is_adjacent(state, bandit)` — new for s5
- `_h_flee_marshal_direction(state, bandit)` — new for s5
- `_h_richest_car_direction(state, bandit)` — new for s5
- `_h_make_state_with_strongbox_at_locomotive(name)` — local fixture for scenarios 1 and 2

## Why this matters

The chapter's argument (p.166): partial plans pay off most when subtasks are long-running (here: a `a_move` takes one game turn to execute), the world state is volatile (other bandits move, the Marshal moves, events fire), and a re-plan tick is cheap (HTN planning is fast). The full-plan version commits to "move forward and rob whatever's there" — but if another bandit grabbed the loot between turns, the second subtask would fail at execution.

In the partial-plan version, the planner only commits to one action. After it runs, the planner re-evaluates the state and picks the now-applicable priority method. The Marshal might have moved into your car between turns — flee-marshal fires instead of pursue-strongbox.

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.colt_express.s5_partial_plan_movement import the_domain, get_problems

problems = get_problems()
# Same state, different root tasks - compare the plans
s_full, _, _ = problems['scenario_1_full_plan_long_horizon']
s_partial, _, _ = problems['scenario_2_partial_plan_pursue_strongbox']

with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r_full = s.find_plan(copy.deepcopy(s_full),
                         [('m_resolve_move_full_plan', 'belle')])
    r_partial = s.find_plan(copy.deepcopy(s_partial),
                            [('m_resolve_move_partial_plan', 'belle')])
print(f'Full:    {len(r_full.plan)} actions')   # 2
print(f'Partial: {len(r_partial.plan)} actions')  # 1
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/colt_express/s5_partial_plan_movement/problems.py
```

## File structure

```
s5_partial_plan_movement/
├── __init__.py     # Package initialization
├── domain.py       # 5 actions (reused), 5 methods across 2 task names
├── problems.py     # 3 scenarios + doctests
└── README.md       # This file
```

## Reference

- Pattern source: trunk_thumper s10 (Game AI Pro 1, Troy Humphreys, CRC Press 2015, §12.10).

---
*Generated 2026-05-16*
