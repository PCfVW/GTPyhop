# Trunk Thumper §12.6 — Recursive Trunk Replacement

Based on **Section 12.6** of Troy Humphreys' "Exploring HTN Planners through Example" in *Game AI Pro* (Steve Rabin, ed., CRC Press, 2015), pp. 157–158.

## Overview

The chapter's designer notices that the troll's trunk attack is overpowered. They suggest the trunk breaks after three attacks, forcing the troll to search for another one. This is implemented via **recursion**:

```
Compound Task [AttackEnemy]
    Method [WsTrunkHealth > 0]
        Subtasks [NavigateToEnemy(), DoTrunkSlam()]
    Method [true]
        Subtasks [FindTrunk(), NavigateToTrunk(), UprootTrunk(), AttackEnemy()]
```

The second method ends with a recursive call to `AttackEnemy`. The recursion **terminates** because `UprootTrunk`'s effect sets `WsTrunkHealth = 3`, which satisfies the first method's precondition on the recursive call.

## Scenarios

| # | Scenario | Plan | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_trunk_intact_direct_slam` | 2 | Trunk has health → first method picks → direct attack |
| 2 | `scenario_2_trunk_broken_must_replace_then_attack` | 5 | Trunk broken → recursive method: find, nav, uproot, then recurse into attack |
| 3 | `scenario_3_no_enemy_patrol_regression` | 3 | s03's patrol behavior still works (regression check) |

## What's new vs. s03

| New | Description |
|---|---|
| `WsTrunkHealth` state | Decremented by `a_do_trunk_slam`, reset to 3 by `a_uproot_trunk` |
| `m_attack_enemy` compound task | Two methods, second one recurses |
| `a_find_trunk`, `a_navigate_to_trunk`, `a_uproot_trunk` actions | New trunk-acquisition pipeline |
| `available_trunks`, `found_trunk` state | Modeling the trunk discovery |
| `a_do_trunk_slam` precondition | Now requires `trunk_health > 0` (it didn't in s03) |

## Termination of the recursion

The chapter is explicit about why this doesn't infinite-loop:

> "If the tree trunk's health was still zero, this would cause the planner to infinite loop. But the new task UprootTrunk's effect sets WsTrunkHealth back to three, allowing us to have the plan FindTrunk → NavigateToTrunk → UprootTrunk → NavigateToEnemy → DoTrunkSlam."

In our model:
1. Outer call to `m_attack_enemy`: `trunk_health = 0`, so first method `m_attack_with_intact_trunk` fails its precondition → planner falls through to `m_attack_after_finding_new_trunk`
2. That method's task list runs `a_find_trunk` → `a_navigate_to_trunk` → `a_uproot_trunk` (this sets `trunk_health = 3`) → recursive `m_attack_enemy`
3. Inner call to `m_attack_enemy`: `trunk_health = 3` now, so first method succeeds → plan ends with `a_navigate_to_enemy` → `a_do_trunk_slam`

The MTR-style "method indices chosen" trail for the plan is `[1, 0]` at `m_attack_enemy`: outer recursion picked method 1 (find new trunk), inner recursion picked method 0 (intact attack).

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.trunk_thumper.s06_recursive_trunk_replacement import the_domain, get_problems

problems = get_problems()
state, tasks, desc = problems['scenario_2_trunk_broken_must_replace_then_attack']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(copy.deepcopy(state), tasks)
for action in result.plan: print(action)
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/trunk_thumper/s06_recursive_trunk_replacement/problems.py
```

## File Structure

```
s06_recursive_trunk_replacement/
├── __init__.py     # Package initialization
├── domain.py       # 8 actions, 4 methods across 2 task names
├── problems.py     # 3 scenarios
└── README.md       # This file
```

## Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, §12.6 pp. 157–158.

---
*Generated 2026-05-15*
