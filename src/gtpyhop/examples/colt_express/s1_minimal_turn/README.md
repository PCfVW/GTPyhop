# Colt Express s1 — Minimal Turn (priority-methods baseline)

Pattern source: [trunk_thumper s03_basic_attack_or_patrol](../../trunk_thumper/s03_basic_attack_or_patrol/) (Game AI Pro Chapter 12.3, Troy Humphreys, CRC Press 2015).

## Overview

The smallest possible Colt Express turn model: one compound task (`m_take_turn`) with two alternative methods, the first applicable wins. Pure Stealin'-phase semantics: if there is loot at the bandit's position (and the bandit is on the interior), rob it; else move forward toward the locomotive.

This is the starting point of the collection. It establishes:
- The **canonical state schema** that all other sub-folders inherit
- The **`h_sample_car_loot` helper** and `COLT_EXPRESS_LOOT_DISTRIBUTION` constant
- The action signature convention: explicit `bandit: str` parameter
- The anti-idempotence pattern via `state.actions_resolved`

## Scenarios

| # | Scenario | Plan | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_rob_loot_at_position` | 1 | Priority method picked: bandit on interior with loot → rob |
| 2 | `scenario_2_move_forward_no_loot` | 1 | Fallback method picked: bandit on car without loot → move forward |
| 3 | `scenario_3_descend_and_rob` | 2 | Manual task list `[a_floor_change, m_take_turn]` — floor_change brings the bandit down from the roof so the priority method can fire |

Verified plan lengths (from `python -m doctest -v problems.py`, all 26 tests pass):

| Scenario | Plan length |
|---|---|
| `scenario_1_rob_loot_at_position` | 1 |
| `scenario_2_move_forward_no_loot` | 1 |
| `scenario_3_descend_and_rob` | 2 |

## Domain structure

### Actions (3)

| Action | Effects | Notes |
|---|---|---|
| `a_move(state, bandit, direction)` | Bandit moves one car forward/backward | `direction in ('forward', 'backward')`. s5 elaborates direction choice. |
| `a_robbery(state, bandit, loot_token)` | Loot token removed from car; value added to bandit's purse | Requires bandit on interior. |
| `a_floor_change(state, bandit)` | Toggle bandit between interior and roof | Always applicable when bandit has a valid level. |

All three actions increment `state.actions_resolved` as an anti-idempotence safety net.

### Methods (1 task name, 2 alternatives)

```
Compound Task m_take_turn(bandit)
    Method m_rob_loot_here       — priority: interior + loot present
        Subtasks [a_robbery(bandit, <first loot token>)]
    Method m_move_forward_fallback — fallback: not at locomotive
        Subtasks [a_move(bandit, 'forward')]
```

### Helper functions

- `_h_pick_loot_to_rob(state, car)` — first loot token in car, or None
- `h_sample_car_loot(seed, num_jewels, num_purses)` — deterministic loot sampler (introduced here, copy-pasted to later sub-folders)
- `h_create_base_state(name)` — initializes the FULL canonical state schema (introduced here, copy-pasted to later sub-folders)
- `_h_setup_train(state, car_names)` — populates `state.cars` and `state.car_index`

## Pure Stealin' framing

The original Trunk Thumper s03 baseline used "attack visible enemy" vs. "patrol bridges" — both Stealin'-phase-equivalent in that they're behaviors triggered by current world state. For Colt Express we kept the *pattern* (priority + fallback) but chose actions consistent with the collection's locked Stealin'-only scope. The pair "rob if loot here, else move" is a deterministic-resolution decision the planner makes mid-Stealin', not a Schemin' card-selection decision.

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.colt_express.s1_minimal_turn import the_domain, get_problems

problems = get_problems()
state, tasks, desc = problems['scenario_1_rob_loot_at_position']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(copy.deepcopy(state), tasks)
print(f'Success: {result.success}, plan: {result.plan}')
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/colt_express/s1_minimal_turn/problems.py
```

## File structure

```
s1_minimal_turn/
├── __init__.py     # Package initialization
├── domain.py       # 3 actions, 2 methods, 1 task name
├── problems.py     # 3 scenarios + canonical helpers + doctests
└── README.md       # This file
```

## Reference

- Pattern source: trunk_thumper s03 (Game AI Pro 1, Troy Humphreys, CRC Press 2015, §12.3).
- Colt Express rulebook: Christophe Raimbault, Jordi Valbuena, Ludonaute 2014. <http://www.coltexpress.ludonaute.fr>

---
*Generated 2026-05-16*
