# Trunk Thumper §12.3 — Basic Attack or Patrol

Based on **Section 12.3** of Troy Humphreys' "Exploring HTN Planners through Example" in *Game AI Pro* (Steve Rabin, ed., CRC Press, 2015), pp. 154–155.

## Overview

The baseline Trunk Thumper. The chapter introduces a troll NPC that patrols numerous bridges and attacks passing enemies with a tree trunk. This sub-folder is the smallest possible version of his behavior: one root compound task with two methods — attack the visible enemy, else patrol bridges.

This is the starting point of the collection and establishes the action/method naming conventions used by every other sub-folder.

## Scenarios

| # | Scenario | Plan | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_enemy_visible_attack` | 2 | First (high-priority) method picked when `can_see_enemy = True` |
| 2 | `scenario_2_no_enemy_patrol` | 3 | Fallback method picked when no enemy visible |

## Domain structure

### Actions (5)

| Action | Effects | Chapter quote |
|---|---|---|
| `a_navigate_to_enemy` | `location = enemy_location` | `Operator [NavigateToOperator(EnemyLocRef)]` |
| `a_do_trunk_slam` | `slams_performed += 1` (see note below) | `Operator [AnimatedAttackOperator(TrunkSlamAnimName)]` |
| `a_choose_bridge_to_check` | `next_bridge_to_check = <picked>` | `Operator [ChooseBridgeToCheckOperator]` |
| `a_navigate_to_bridge` | `location = next_bridge_to_check` | `Operator [NavigateToOperator(NextBridgeLocRef)]` |
| `a_check_bridge` | `bridges_checked += [location]` | `Operator [CheckBridgeOperator(SearchAnimName)]` |

### Methods (1 task name, 2 alternatives)

```
Compound Task [BeTrunkThumper]                  → m_be_trunk_thumper
    Method [WsCanSeeEnemy == true]              → m_attack_visible_enemy
        Subtasks [NavigateToEnemy, DoTrunkSlam]
    Method [true]                               → m_patrol_bridges
        Subtasks [ChooseBridgeToCheck, NavigateToBridge, CheckBridge]
```

## Notes on faithfulness to the chapter

The chapter's literal text shows `Primitive Task [DoTrunkSlam]` with an `Operator` but no `Effects`. In GTPyhop, an action that returns the state unchanged is considered **idempotent** and is elided from `result.plan` (see the [example style guide](../../../../../docs/gtpyhop_example_style_guide.md), Section 8). To keep the action visible in the plan for pedagogical clarity — and to align with how §12.6 will extend the action with `WsTrunkHealth -= 1` — `a_do_trunk_slam` increments a `slams_performed` counter as a minimal state change. The action's docstring documents this divergence.

For the same reason, `a_check_bridge` records bridges into a `bridges_checked` list. The chapter's literal text doesn't specify this effect, but the chapter's narrative talks about the troll patrolling "numerous bridges" so the tracking is a natural fit.

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.trunk_thumper.s03_basic_attack_or_patrol import the_domain, get_problems

problems = get_problems()
state, tasks, desc = problems['scenario_1_enemy_visible_attack']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(copy.deepcopy(state), tasks)
print(f'Success: {result.success}, plan: {result.plan}')
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/trunk_thumper/s03_basic_attack_or_patrol/problems.py
```

## File Structure

```
s03_basic_attack_or_patrol/
├── __init__.py     # Package initialization
├── domain.py       # 5 actions, 2 methods, 1 task name
├── problems.py     # 2 scenarios
└── README.md       # This file
```

## Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, §12.3 pp. 154–155.

---
*Generated 2026-05-15*
