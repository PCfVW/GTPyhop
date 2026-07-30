# Colt Express s4 — Character Priorities (priority-method ladder)

Pattern source: [trunk_thumper s08_priority_methods](../../trunk_thumper/s08_priority_methods/) (Game AI Pro Chapter 12.8, Troy Humphreys, CRC Press 2015).

## Overview

Demonstrates the **priority-method ladder** pattern applied to Colt Express character abilities. Each character's special ability is implemented as a separate, higher-priority method that returns False on miss so the planner falls through to the next method in declaration order.

4 of the 6 characters are modeled (per locked-in scope):

| Character | Ability | Implemented as |
|---|---|---|
| Belle | Cannot be targeted by Fire/Punch if alternative exists | `m_fire_blocked_by_belle_immunity` (top priority on `m_resolve_fire`) |
| Tuco | Fire through the floor | `m_fire_tuco_through_floor` + action `a_fire_through_floor` |
| Django | Knockback on Fire | `m_fire_django_knockback` + action `a_fire_with_knockback` |
| Cheyenne | Keep the punched purse | `m_punch_cheyenne_keep_purse` + action `a_punch_and_keep_purse` |

Skipped: **Ghost** (face-down first card complicates the s2 deck recursion), **Doc** (trivial initial-state +1 card, not method-shaping).

The Belle-immunity method structurally mirrors trunk_thumper s08's `WsIsTired` fix: a higher-priority guard whose precondition prevents the generic action from firing in a specific game-rule-defined situation.

## Scenarios

| # | Scenario | Plan | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_belle_immunity_redirects_fire` | 1 | Belle-immunity redirects Tuco's fire at Belle to Doc (the alternative target) |
| 2 | `scenario_2_tuco_fires_through_floor` | 1 | Tuco-through-floor fires (Tuco on roof, Doc on interior of same car) |
| 3 | `scenario_3_django_knockback_fire` | 1 | Django-knockback fires (roof-to-roof, target at train edge, knockback nulled) |
| 4 | `scenario_4_cheyenne_keeps_punched_purse` | 1 | Cheyenne-keep-purse fires (same car, same level, target has $500) |

Verified via `python -m doctest -v problems.py` (27 tests passing).

**Note on scenario count:** The implementation plan originally specified 3 scenarios with a combined "Tuco-or-Django" third scenario. Extended to **4 scenarios** (one per character) for clearer pedagogy. Plan length per scenario remains 1.

## Domain structure

### Actions (8)

| Action | Source | Notes |
|---|---|---|
| `a_move(state, bandit, direction)` | Basic (s1-style) | No Marshal/deck awareness |
| `a_robbery(state, bandit, loot_token)` | Basic (s1-style) | |
| `a_floor_change(state, bandit)` | Basic (s1-style) | |
| `a_fire(state, shooter, target)` | From s3 | Roof-to-roof; used as fallback and as Belle-redirect target |
| `a_fire_through_floor(state, shooter, target)` | **New** | Tuco's special; same car, different levels |
| `a_fire_with_knockback(state, shooter, target)` | **New** | Django's special; roof-to-roof + target knocked back one car (or stays if at train edge) |
| `a_punch(state, puncher, target)` | **New** | Standard punch; target loses $250 to "the floor" (simplification) |
| `a_punch_and_keep_purse(state, puncher, target)` | **New** | Cheyenne's special; $250 transfers from target to puncher |

### Methods (2 task names, 6 alternative methods total)

```
Compound Task m_resolve_fire(shooter, target)
    Method m_fire_blocked_by_belle_immunity   — target is belle, alt exists
        Subtasks [a_fire(shooter, alt_target)]  (redirects)
    Method m_fire_tuco_through_floor          — shooter is tuco, same car, opposite levels
        Subtasks [a_fire_through_floor(shooter, target)]
    Method m_fire_django_knockback            — shooter is django, standard roof-to-roof
        Subtasks [a_fire_with_knockback(shooter, target)]
    Method m_fire_standard                    — fallback
        Subtasks [a_fire(shooter, target)]

Compound Task m_resolve_punch(puncher, target)
    Method m_punch_cheyenne_keep_purse        — puncher is cheyenne
        Subtasks [a_punch_and_keep_purse(puncher, target)]
    Method m_punch_standard                   — fallback
        Subtasks [a_punch(puncher, target)]
```

The s08 lesson — that priority is encoded by **method declaration order** — applies directly: `declare_task_methods('m_resolve_fire', m_fire_blocked_by_belle_immunity, m_fire_tuco_through_floor, m_fire_django_knockback, m_fire_standard)` lists them highest-priority first. Each one returns False when it doesn't apply, letting the planner try the next.

### Helper functions

- `_h_find_alternate_target(state, shooter, blocked_target)` — finds a valid alternative target for Belle-immunity redirect
- `h_sample_car_loot`, `h_create_base_state`, `_h_setup_train` — copy-pasted canonical helpers from s1

## The Belle-immunity guard

This is the structural twin of s08's "subtle bug" fix:

```python
def m_fire_blocked_by_belle_immunity(state, shooter, target):
    # ... type / value checks ...

    # BEGIN: Auxiliary Parameter Inference
    if state.bandit_character.get(target) != 'belle':
        return False  # not Belle: this method doesn't apply
    alt_target = _h_find_alternate_target(state, shooter, target)
    if alt_target is None:
        return False  # no alternative: Belle isn't immune here; fall through
    # END: Auxiliary Parameter Inference

    # BEGIN: Task Decomposition
    return [('a_fire', shooter, alt_target)]
    # END: Task Decomposition
```

**Why a separate method (not a guard inside `m_fire_standard`)**: s08's WsIsTired pattern shows that a generic action method with a `if state.is_tired: return False` guard works for *blocking* but not for *redirecting*. Belle-immunity requires redirection, so it lives as a dedicated method that returns an alternative decomposition.

To experiment: comment out `if alt_target is None: return False` and re-run scenario 1 — you'll see the planner try to fire at Belle anyway (which would violate the rule). The negative-control variant is left as an exercise here rather than shipped as a separate scenario (per the locked-in "neg controls in s3 only" scope).

## Simplifications

| Real rule | Modeled as |
|---|---|
| Punch removes a specific loot token of any value | Flat $250 transfer (sufficient to demonstrate the priority pattern) |
| Cheyenne keeps the *purse* if punched; other loot falls | $250 transfer to Cheyenne regardless of token type |
| Tuco's through-floor fire respects line-of-sight | We don't model LoS (same car + opposite levels is sufficient) |
| Django's knockback distance varies by Fire context | One car always |

These simplifications are documented in each action's docstring.

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.colt_express.s4_character_priorities import the_domain, get_problems

problems = get_problems()
state, tasks, _ = problems['scenario_1_belle_immunity_redirects_fire']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r = s.find_plan(copy.deepcopy(state), tasks)
print(r.plan)  # [('a_fire', 'tuco', 'doc')]
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/colt_express/s4_character_priorities/problems.py
```

## File structure

```
s4_character_priorities/
├── __init__.py     # Package initialization
├── domain.py       # 8 actions, 6 methods across 2 task names
├── problems.py     # 4 scenarios + doctests
└── README.md       # This file
```

## Reference

- Pattern source: trunk_thumper s08 (Game AI Pro 1, Troy Humphreys, CRC Press 2015, §12.8).
- Colt Express rulebook character abilities, p.5.

---
*Generated 2026-05-16*
