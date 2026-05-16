# Colt Express s3 — Marshal Expected Effects

Pattern source: [trunk_thumper s07_expected_effects_chase](../../trunk_thumper/s07_expected_effects_chase/) (Game AI Pro Chapter 12.7, Troy Humphreys, CRC Press 2015).

## Overview

The headline sub-folder of the colt_express collection. Demonstrates the `[EXPECTED_EFFECT]` tag (documented in `docs/gtpyhop_domain_style_guide.md` §8.4) on the Colt Express **Marshal forced-escape** rule.

Per the rulebook (p.4):

> When a Bandit enters a Car where the Marshal is, or when the Marshal enters a Car where Bandits are, they must escape up to the roof of the Car (even if they have just come down from there). A Bandit can never stay inside the Car where the Marshal is located. Additionally, each one of those Bandits immediately receives a Neutral Bullet card.

The bandit's `a_move` directly updates `state.bandit_car` (`[DATA]`); the roof-escape and the neutral-bullet are **system reactions** to the move, not operator-driven effects. We tag these reactions as `[EXPECTED_EFFECT]` so downstream actions whose preconditions depend on them (e.g., `a_fire` requires shooter on roof) succeed at planning time.

The sub-folder also ships a **negative-control scenario** demonstrating what happens when the `[EXPECTED_EFFECT]` block is omitted — the plan fails because the chained-on action's precondition cannot be satisfied. This is the structural twin of trunk_thumper s07's scenario 3.

## Scenarios

| # | Scenario | Plan | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_move_into_marshal_then_fire_from_roof` | 2 | Bandit `a_move` triggers `[EXPECTED_EFFECT]` push to roof; downstream `a_fire` precondition satisfied |
| 2 | `scenario_2_marshal_action_pushes_bandit` | 2 | `a_marshal_move` triggers symmetric `[EXPECTED_EFFECT]` for bandits in destination car |
| 3 | `scenario_3_expected_effects_negative_control` | **0 / fail** | Demo variant `a_move_demo_no_marshal_trigger` omits `[EXPECTED_EFFECT]` → `a_fire` precondition fails → plan impossible |

Verified via `python -m doctest -v problems.py` (22 tests passing).

## Domain structure

### Actions (6)

| Action | Source | Notes |
|---|---|---|
| `a_move(state, bandit, direction)` | Evolved from s1 | **Adds `[EXPECTED_EFFECT]` block**: when destination car contains Marshal, push bandit to roof + neutral bullet |
| `a_robbery(state, bandit, loot_token)` | Reused from s1 | Unchanged |
| `a_floor_change(state, bandit)` | Reused from s1 | Unchanged |
| `a_marshal_move(state, direction)` | **New** | Moves Marshal one car; `[EXPECTED_EFFECT]` pushes any bandits in destination car to roof + neutral bullet |
| `a_fire(state, shooter, target)` | **New** | Roof-to-roof fire; requires both shooter and target on roof, different cars |
| `a_move_demo_no_marshal_trigger(...)` | **New (negative control)** | Byte-identical to `a_move` except `[EXPECTED_EFFECT]` block omitted. Used only in scenario 3 |

### Methods (1 task name, 2 alternatives — reused from s1)

```
Compound Task m_take_turn(bandit)
    Method m_rob_loot_here       — priority: interior + loot present
    Method m_move_forward_fallback — fallback: not at locomotive
```

s3 doesn't add new methods; the methods are reused from s1 unchanged. All three scenarios use **manual task lists** (not `m_take_turn`) to directly invoke the action sequences being demonstrated — matching the trunk_thumper s07 scenario 3 pattern.

## The `[EXPECTED_EFFECT]` block in detail

The canonical `a_move` body:

```python
# BEGIN: Effects
# [DATA] Bandit moves one car in the requested direction
destination_car = state.cars[destination_index]
state.bandit_car[bandit] = destination_car

# [EXPECTED_EFFECT] Marshal forced-escape: if the destination car contains
# the Marshal, the rulebook forces the bandit onto the roof and gives them
# a Neutral Bullet card. The sensor/system applies these changes after the
# operator runs; at planning time we apply them here so downstream actions
# whose preconditions read these fields can succeed.
if state.marshal_car is not None and destination_car == state.marshal_car:
    state.bandit_level[bandit] = 'roof'
    state.bandit_bullets_taken[bandit] = state.bandit_bullets_taken.get(bandit, 0) + 1

# [DATA] Anti-idempotence counter
state.actions_resolved = state.actions_resolved + 1
# END: Effects
```

The demo variant `a_move_demo_no_marshal_trigger` is byte-identical except the `[EXPECTED_EFFECT]` `if` block is omitted. Its Effects block contains only the `[DATA]` `state.bandit_car` update and the `actions_resolved` increment.

## Scenario 3 — the negative control

Scenario 3 uses the same initial state as scenario 1 but invokes the demo variant in its task list:

```python
[('a_move_demo_no_marshal_trigger', 'belle', 'forward'),
 ('a_fire', 'belle', 'doc')]
```

- After `a_move_demo_no_marshal_trigger`: Belle is in c1 (Marshal's car) but **still on interior** — the demo variant didn't apply the forced-escape.
- `a_fire` precondition requires `state.bandit_level['belle'] == 'roof'`. False → precondition fails → planning is impossible → `r.success == False`.

This is the empirical demonstration of *why* the `[EXPECTED_EFFECT]` tag is needed. To experiment, swap the demo action for the canonical `a_move` in scenario 3's task list — the plan will then succeed with length 2 (the same as scenario 1).

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.colt_express.s3_marshal_expected_effects import the_domain, get_problems

problems = get_problems()
# Working scenario
state, tasks, _ = problems['scenario_1_move_into_marshal_then_fire_from_roof']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r = s.find_plan(copy.deepcopy(state), tasks)
print(f'Success: {r.success}, plan: {r.plan}')

# Negative control - SAME goal shape, plan fails without the [EXPECTED_EFFECT]
state, tasks, _ = problems['scenario_3_expected_effects_negative_control']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r = s.find_plan(copy.deepcopy(state), tasks)
print(f'Negative control - success: {r.success}')  # False
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/colt_express/s3_marshal_expected_effects/problems.py
```

## File structure

```
s3_marshal_expected_effects/
├── __init__.py     # Package initialization
├── domain.py       # 6 actions (incl. demo variant), 2 methods reused from s1
├── problems.py     # 3 scenarios incl. negative control + doctests
└── README.md       # This file
```

## Reference

- Pattern source: trunk_thumper s07 (Game AI Pro 1, Troy Humphreys, CRC Press 2015, §12.7).
- `[EXPECTED_EFFECT]` tag definition: `docs/gtpyhop_domain_style_guide.md` §8.4.
- Colt Express rulebook (Marshal rules, p.4): Christophe Raimbault, Jordi Valbuena, Ludonaute 2014.

---
*Generated 2026-05-16*
