# Trunk Thumper §12.8 — Priority Methods (whirlwind combo + boulder fallback + WsIsTired)

Based on **Section 12.8** of Troy Humphreys' "Exploring HTN Planners through Example" in *Game AI Pro* (Steve Rabin, ed., CRC Press, 2015), pp. 160–163.

## Overview

§12.8 combines two designer requests:

1. **Recovery + boulder fallback**: a recovery animation after each slam (so the player can react), and a low-priority boulder throw when the troll cannot navigate to the enemy.
2. **Whirlwind combo**: after three trunk slams (`WsPowerUp` accumulates), the troll can perform a powerful whirlwind attack. This introduced a "subtle bug" — the third slam's effects cause a re-plan, which immediately fires the whirlwind, chaining attack-into-combo with no breather. The chapter fixes this with `WsIsTired`: the slam sets the troll tired; the whirlwind precondition requires *not* tired; the recovery clears the flag.

This sub-folder implements **both stories** together. The `m_attack_enemy` task has **four methods in priority order**:

| # | Method | Preconditions |
|---|---|---|
| 1 | `m_whirlwind_combo` | `power_up >= 3` AND NOT `is_tired` |
| 2 | `m_attack_with_intact_trunk` | `trunk_health > 0`, `can_see_enemy`, `can_navigate_to_enemy` |
| 3 | `m_attack_after_finding_new_trunk` | `available_trunks`, `can_see_enemy` (recursive) |
| 4 | `m_boulder_fallback` | none (fallback) |

The planner picks the first applicable method. Method ordering encodes priority.

## Scenarios

| # | Scenario | Plan | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_slam_and_recovery` | 3 | Default attack path (method 2) |
| 2 | `scenario_2_whirlwind_after_three_slams` | 2 | Whirlwind combo fires (method 1) |
| 3 | `scenario_3_cannot_navigate_so_boulder_fallback` | 2 | Path-blocked falls to boulder (method 4) |
| 4 | `scenario_4_tired_blocks_whirlwind_combo` | 3 | `is_tired` guard prevents premature whirlwind combo (method 2 instead of 1) |

### Scenario 4 — the chapter's key example for §12.8

This is the scenario the chapter introduces specifically to demonstrate the WsIsTired fix. The initial state has `power_up = 3` (whirlwind threshold met) AND `is_tired = True` (troll just slammed).

- **Without** the `is_tired` precondition on `m_whirlwind_combo`: the planner would pick method 1 and produce `[whirlwind, recovery]` (2 actions), chaining the whirlwind directly off a slam — the "subtle bug" the chapter warns against.
- **With** the `is_tired` precondition: method 1 fails its precondition, the planner falls through to method 2, and produces `[navigate, slam, recovery]` (3 actions) — a sensible attack rhythm.

To experiment, comment out `if state.is_tired: return False` in `m_whirlwind_combo` and re-run scenario 4 — you'll see the bug.

## What's new vs. s07

| New | Description |
|---|---|
| `power_up` state | Accumulates with each slam, reset by whirlwind |
| `is_tired` state | Set by slam, cleared by recovery; guards whirlwind |
| `can_navigate_to_enemy` state | When False, blocks the standard slam path |
| `has_boulder` state | Set by `a_pickup_boulder`, cleared by `a_throw_boulder` |
| `a_do_recovery_roar` action | Clears `is_tired` |
| `a_do_whirlwind_trunk_attack` action | Big combo; precondition `NOT is_tired AND power_up >= 3` |
| `a_pickup_boulder`, `a_throw_boulder` actions | Boulder-throw fallback |
| `m_whirlwind_combo`, `m_boulder_fallback` methods | New methods on `m_attack_enemy` |

## Scope note — MTR is out of scope

The chapter's §12.8 spends much of its space on the **Method Traversal Record (MTR)**, a *runtime* mechanism for deciding whether a currently-running plan should be aborted in favor of a higher-priority new plan when sensors change the world state. GTPyhop produces one plan per `find_plan` call and does not expose the decomposition trail — MTR is out of scope for this collection. The *underlying claim* of priority via method ordering, however, *is* exactly how GTPyhop selects between alternative methods, which is what scenarios 1–4 demonstrate. See the collection README for the full scope discussion.

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.trunk_thumper.s08_priority_methods import the_domain, get_problems

problems = get_problems()
state, tasks, _ = problems['scenario_4_tired_blocks_whirlwind_combo']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r = s.find_plan(copy.deepcopy(state), tasks)
for action in r.plan: print(action)
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/trunk_thumper/s08_priority_methods/problems.py
```

## File Structure

```
s08_priority_methods/
├── __init__.py     # Package initialization
├── domain.py       # 9 actions, 5 methods across 2 task names
├── problems.py     # 4 scenarios
└── README.md       # This file
```

## Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, §12.8 pp. 160–163.

---
*Generated 2026-05-15*
