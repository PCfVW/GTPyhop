# Trunk Thumper §12.7 — Expected Effects (chase + regain-LOS roar)

Based on **Section 12.7** of Troy Humphreys' "Exploring HTN Planners through Example" in *Game AI Pro* (Steve Rabin, ed., CRC Press, 2015), pp. 158–159.

## Overview

The chapter's designer asks for a chase behavior: when the troll can't currently see the enemy but saw them recently, navigate to the last known location and roar when line-of-sight is regained. The naive implementation hits a problem:

- `a_regain_los_roar` requires `can_see_enemy == True` to fire.
- Nothing in the plan *sets* `can_see_enemy` — it's a sensor-driven property.
- At planning time, the planner cannot satisfy the roar's precondition.

The chapter's solution is **expected effects**: effects applied to the working world state *during planning only* (no game-runtime equivalent), expressing sensor changes that *will* happen after the operator executes. The chapter writes:

```
Primitive Task [NavToLastEnemyLoc]
    Operator [NavigateToOperator(LastEnemyLocation)]
    Effects [WsLocation = LastEnemyLocation]
    ExpectedEffects [WsCanSeeEnemy = true]
```

## The `[EXPECTED_EFFECT]` tag

GTPyhop has no separate runtime, so the chapter's runtime-vs-planning distinction doesn't apply directly. Both kinds of effects are applied identically during planning. We preserve the chapter's distinction as a **comment-level tag** in the action's Effects block:

```python
# BEGIN: Effects
# [DATA] Troll's location updated to last known enemy location
state.location = state.last_enemy_location

# [EXPECTED_EFFECT] Vision sensor will set can_see_enemy True after arrival.
state.can_see_enemy = True
# END: Effects
```

The tag is documented in `docs/gtpyhop_domain_style_guide.md` (Section 8). Semantically `[EXPECTED_EFFECT]` is identical to `[DATA]`; the tag is purely informational, communicating *why* the effect is in the action.

## Scenarios

| # | Scenario | Plan length | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_enemy_visible_attack` | 2 (success) | Regression: first method still fires |
| 2 | `scenario_2_enemy_recently_seen_chase_and_roar` | 2 (success) | `[EXPECTED_EFFECT]` enables the roar precondition |
| 3 | `scenario_3_expected_effects_negative_control` | 0 (**failure**) | Without `[EXPECTED_EFFECT]`, the plan is impossible |

### Scenario 3: the negative control

Scenario 3 uses a teaching-variant action `a_nav_to_last_enemy_loc_demo_no_ee` — identical to the canonical action *except* it omits the `[EXPECTED_EFFECT]` on `can_see_enemy`. The scenario passes a literal task list `[('a_nav_to_last_enemy_loc_demo_no_ee',), ('a_regain_los_roar',)]` to bypass the method tree and invoke the broken sequence directly.

**The plan fails.** `a_nav_to_last_enemy_loc_demo_no_ee` executes and updates location, but `can_see_enemy` is never set; `a_regain_los_roar`'s precondition then fails, and the planner has no alternative to fall back on. This is the empirical demonstration of *why* `[EXPECTED_EFFECT]` is needed.

## What's new vs. s06

| New | Description |
|---|---|
| `has_seen_enemy_recently`, `last_enemy_location` state | Enable the chase method |
| `a_nav_to_last_enemy_loc` action | Canonical action with `[EXPECTED_EFFECT]` |
| `a_nav_to_last_enemy_loc_demo_no_ee` action | Teaching variant without the tag (for negative control) |
| `a_regain_los_roar` action | Roar; precondition motivates expected effects |
| Third method on `m_be_trunk_thumper` | `m_chase_recently_seen_enemy` between attack and patrol |
| `[EXPECTED_EFFECT]` tag | Documented in domain style guide |

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.trunk_thumper.s07_expected_effects_chase import the_domain, get_problems

problems = get_problems()
# Working chase scenario
state, tasks, _ = problems['scenario_2_enemy_recently_seen_chase_and_roar']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r = s.find_plan(copy.deepcopy(state), tasks)
print(f'Success: {r.success}, plan: {r.plan}')

# Negative control - SAME goal, but the plan fails without expected effects
state, tasks, _ = problems['scenario_3_expected_effects_negative_control']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r = s.find_plan(copy.deepcopy(state), tasks)
print(f'Negative control - success: {r.success}')  # False
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/trunk_thumper/s07_expected_effects_chase/problems.py
```

## File Structure

```
s07_expected_effects_chase/
├── __init__.py     # Package initialization
├── domain.py       # 10 actions (incl. negative-control variant), 5 methods across 2 task names
├── problems.py     # 3 scenarios (including the negative control)
└── README.md       # This file
```

## Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, §12.7 pp. 158–159.

---
*Generated 2026-05-15*
