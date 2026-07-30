# Trunk Thumper §12.9 — Simultaneous Behaviors (single-planner non-blocking nav)

Based on **Section 12.9** of Troy Humphreys' "Exploring HTN Planners through Example" in *Game AI Pro* (Steve Rabin, ed., CRC Press, 2015), pp. 163–165.

## Overview

The chapter's designer needs the troll to do two things at once: navigate toward an enemy AND guard against incoming ranged attacks. §12.9 discusses two approaches:

1. **Two domains and two planners** (upper body / lower body). Works but costs synchronization, performance, and debuggability. The chapter explicitly cautions: *"you will not gain any friends when other programmers run into the debugging headache you just created with your multiple planners — trust me."*
2. **Single planner with non-blocking navigation** (the chapter's *recommended* approach). The navigate action starts path-following and completes immediately; the planner can then interleave a guard action while traversal continues in the background.

This sub-folder implements the recommended approach.

## Scenarios

| # | Scenario | Plan | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_melee_range_slam` | 1 | Enemy in melee → method 1 (slam) |
| 2 | `scenario_2_out_of_range_navigate` | 1 | Enemy far → method 2 (non-blocking navigate) |
| 3 | `scenario_3_navigating_and_hit_so_guard` | 1 | Already navigating + hit → method 3 (guard interleaves) |

Each scenario is a **single planner invocation** producing a single action. The chapter's point is that the planner's behavior depends on which world state is true *at the moment of replanning*, and that the non-blocking navigation pattern enables the simultaneous-behavior solution without two domains.

## The non-blocking navigation pattern

The key action is `a_navigate_to_enemy`:

```python
def a_navigate_to_enemy(state: State) -> Union[State, bool]:
    # ...
    # BEGIN: Effects
    # [ENABLER] Signal that path-following has begun
    state.navigating = True
    # ...
```

Setting `state.navigating = True` is the action's complete behavior. The actual path-following is presumed to happen in a real game's path-follower subsystem (out of scope for planning). On the next plan invocation, with `navigating = True`, method 3 (`m_guard_during_navigation`) can fire whenever a ranged attack is detected.

## Method priority structure

```
Compound Task [BeTrunkThumper]                              → m_be_trunk_thumper
    Method [has_enemy, enemy_range == melee]                → m_melee_slam
        Subtasks [DoTrunkSlam]
    Method [has_enemy, enemy_range != melee]                → m_out_of_range_navigate
        Subtasks [NavigateToEnemy]   (non-blocking)
    Method [navigating, hit_by_ranged_attack]               → m_guard_during_navigation
        Subtasks [GuardFaceWithArm]
    Method [true]                                           → m_idle
        Subtasks [Idle]
```

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.trunk_thumper.s09_simultaneous_navigation_and_guard import the_domain, get_problems

problems = get_problems()
state, tasks, _ = problems['scenario_3_navigating_and_hit_so_guard']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r = s.find_plan(copy.deepcopy(state), tasks)
print(r.plan)  # [('a_guard_face_with_arm',)]
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/trunk_thumper/s09_simultaneous_navigation_and_guard/problems.py
```

## File Structure

```
s09_simultaneous_navigation_and_guard/
├── __init__.py     # Package initialization
├── domain.py       # 4 actions, 4 methods, 1 task name
├── problems.py     # 3 scenarios
└── README.md       # This file
```

## Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, §12.9 pp. 163–165.

---
*Generated 2026-05-15*
