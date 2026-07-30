# Trunk Thumper §12.10 — Partial Plans (method-split)

Based on **Section 12.10** of Troy Humphreys' "Exploring HTN Planners through Example" in *Game AI Pro* (Steve Rabin, ed., CRC Press, 2015), pp. 165–167.

## Overview

Partial planning lets the planner stop short of a fully-decomposed plan, leaving the rest to be filled in by a future re-plan. This is useful when (a) navigation takes a long time and the world state may change before arrival, and (b) you'd rather plan a few steps ahead than commit to a long sequence that could become invalid mid-execution.

The chapter discusses two approaches and **recommends the manual method-split**: break one method's `[task1, task2]` subtask sequence into two separate methods (one per situation, distinguished by world state). The planner picks whichever method matches the current state and produces a shorter plan; when the world state changes, it re-plans and picks the now-applicable next method.

The automatic alternative (assigning a "time" cost to primitive tasks and stopping when a threshold is crossed) is presented and then dismissed by the chapter itself ("what's the point of the automated partial planning?"). This sub-folder implements the recommended manual approach.

## Scenarios

| # | Scenario | Top-level task | Plan | Demonstrates |
|---|---|---|---|---|
| 1 | `scenario_1_full_plan_long_horizon` | `m_be_trunk_thumper_full_plan` | 2 | Pre-split: commits to navigate AND slam upfront |
| 2 | `scenario_2_partial_plan_navigate_only_when_far` | `m_be_trunk_thumper_partial_plan` | 1 | Post-split, enemy far: just navigate |
| 3 | `scenario_3_partial_plan_slam_only_when_close` | `m_be_trunk_thumper_partial_plan` | 1 | Post-split, enemy close: just slam |

Scenarios 1 and 2 use the **same initial state** (enemy visible, out of range) and differ only in which root task they invoke. Compare the plan lengths — that's the partial-plan story in a nutshell.

## The split

**Before (pre-split):**

```
Compound Task [BeTrunkThumper]
    Method [WsCanSeeEnemy == true]
        Subtasks [NavigateToEnemy(), DoTrunkSlam()]
```

**After (post-split):**

```
Compound Task [BeTrunkThumper]
    Method [WsCanSeeEnemy == true, WsEnemyRange > MeleeRange]
        Subtasks [NavigateToEnemy()]
    Method [WsCanSeeEnemy == true]
        Subtasks [DoTrunkSlam()]
```

The post-split version produces a one-action plan per call. After the troll navigates and the world state updates, the planner re-runs and finds itself in melee range, where the second method now applies. The plan stays reactive.

## Why this matters

> "There isn't much point to planning too far into the future since there is a good chance the world state could change, forcing our troll to make a different decision." — *Game AI Pro 1*, p. 166

Partial plans pay off most when:
- Subtasks are long-running (navigation, animations)
- The world state is volatile (combat, dynamic obstacles)
- A re-plan tick is cheap

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.trunk_thumper.s10_partial_plans import the_domain, get_problems

problems = get_problems()
# Same state, different root tasks - compare the plans
s_full, _, _ = problems['scenario_1_full_plan_long_horizon']
s_partial, _, _ = problems['scenario_2_partial_plan_navigate_only_when_far']

with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r_full = s.find_plan(copy.deepcopy(s_full),
                         [('m_be_trunk_thumper_full_plan',)])
    r_partial = s.find_plan(copy.deepcopy(s_partial),
                            [('m_be_trunk_thumper_partial_plan',)])
print(f'Full:    {len(r_full.plan)} actions')   # 2
print(f'Partial: {len(r_partial.plan)} actions')  # 1
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/trunk_thumper/s10_partial_plans/problems.py
```

## File Structure

```
s10_partial_plans/
├── __init__.py     # Package initialization
├── domain.py       # 2 actions, 3 methods, 2 task names (full vs. partial)
├── problems.py     # 3 scenarios
└── README.md       # This file
```

## Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, §12.10 pp. 165–167.

---
*Generated 2026-05-15*
