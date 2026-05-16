# Colt Express s2 — Recursive Round (deck resolution)

Pattern source: [trunk_thumper s06_recursive_trunk_replacement](../../trunk_thumper/s06_recursive_trunk_replacement/) (Game AI Pro Chapter 12.6, Troy Humphreys, CRC Press 2015).

## Overview

Demonstrates **recursive task decomposition** applied to Colt Express deck resolution during the Stealin' phase. The pre-encoded `state.deck` (a list of `(bandit, card_kind)` tuples) is resolved card-by-card via a recursive method that head-pops the deck on each action, terminating when the deck is empty.

The termination story mirrors trunk_thumper s06's `WsTrunkHealth` reset:

- **Base-case method** (`m_resolve_deck_empty`) matches when `not state.deck` → returns `[]`
- **Recursive method** (`m_resolve_deck_recursive`) matches when deck non-empty → returns `[(card_action, ...), ('m_resolve_programmed_deck',)]`
- Each card action **head-pops the deck** as part of its effects (the analog of `a_uproot_trunk` setting `trunk_health = 3`), so the recursive call sees a strictly smaller deck.
- Eventually deck is empty → base case fires → recursion terminates.

s2 also introduces `m_play_round` with two methods (with/without an end-of-round event) and the `a_apply_event` action. Per the locked-in v1.9.7 scope, only the `hostage_taking` event is modeled; the other 6 event types are documented as out-of-scope.

## Scenarios

| # | Scenario | Plan | Demonstrates |
|---|---|---|---|
| 1 | `scenario_1_one_round_three_turns` | 3 | 3-card deck, no event — recursion through 3 dispatches plus base case |
| 2 | `scenario_2_longer_deck_resolution` | 6 | 6-card deck, no event — recursion handles arbitrary deck lengths |
| 3 | `scenario_3_round_with_hostage_taking_event` | 4 | 3-card deck + event — `m_play_round_with_event` chains deck resolution then `a_apply_event` |

Verified via `python -m doctest -v problems.py` (25 tests passing) and a verbose=3 spot check on scenario 1 confirming no actions are silently treated as idempotent.

**Note on scenario 2's naming:** the implementation plan originally called this scenario `scenario_2_two_rounds_back_to_back` with the framing of two consecutive `m_play_round` calls. The per-round granularity (each round resolves exactly N cards) is **not modeled in s2** — the recursive deck resolver simply chomps through whatever deck it sees. The 6-card scenario therefore resolves as a single long deck rather than two distinct rounds. The teaching point — recursion handles arbitrary lengths — is the same.

## Domain structure

### Actions (4)

| Action | Source | Notes |
|---|---|---|
| `a_move(state, bandit, direction)` | **Evolved from s1** | Adds `state.deck[0] == (bandit, 'move')` precondition and `state.deck = state.deck[1:]` effect (head-pop) |
| `a_robbery(state, bandit, loot_token)` | **Evolved from s1** | Adds deck-head check and head-pop |
| `a_floor_change(state, bandit)` | **Evolved from s1** | Adds deck-head check and head-pop |
| `a_apply_event(state)` | **New** | Models `hostage_taking` only: $250 to each bandit at locomotive |

**Action divergence note**: s2's deck-aware actions are a different evolution from s3's Marshal-aware actions. Both descend from s1's minimal versions. Per the collection's copy-paste convention, each sub-folder declares its own action variants.

### Methods (2 task names, 4 alternative methods total)

```
Compound Task m_resolve_programmed_deck
    Method m_resolve_deck_empty       — base case: deck empty -> return []
    Method m_resolve_deck_recursive   — recursive: pop head, dispatch, recurse

Compound Task m_play_round
    Method m_play_round_with_event    — priority: event_card present
        Subtasks [m_resolve_programmed_deck, a_apply_event]
    Method m_play_round_no_event      — fallback: no event
        Subtasks [m_resolve_programmed_deck]
```

### Helper functions

- `_h_pick_loot_to_rob(state, car)` — reused from s1
- `h_sample_car_loot`, `h_create_base_state`, `_h_setup_train` — copy-pasted from s1 (canonical helpers)

## The recursion mechanism

```python
def m_resolve_deck_recursive(state):
    # ... preconditions check state.deck non-empty ...
    bandit, card_kind = state.deck[0]
    if card_kind == 'move':
        return [('a_move', bandit, 'forward'), ('m_resolve_programmed_deck',)]
    elif card_kind == 'robbery':
        loot_token = _h_pick_loot_to_rob(state, state.bandit_car[bandit])
        return [('a_robbery', bandit, loot_token), ('m_resolve_programmed_deck',)]
    else:  # 'floor_change'
        return [('a_floor_change', bandit), ('m_resolve_programmed_deck',)]
```

Each branch returns a 2-element decomposition: the dispatched action plus a recursive call. The action head-pops the deck (`state.deck = state.deck[1:]`) so the recursive call sees one fewer card. After N iterations the deck is empty and `m_resolve_deck_empty` matches with `return []`, terminating the recursion.

This is structurally identical to s06's `m_attack_after_finding_new_trunk` ending with a recursive call to `m_attack_enemy` after the prior `a_uproot_trunk` set `trunk_health = 3` to satisfy the base-case method's precondition.

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.colt_express.s2_recursive_round import the_domain, get_problems

problems = get_problems()
state, tasks, _ = problems['scenario_2_longer_deck_resolution']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    r = s.find_plan(copy.deepcopy(state), tasks)
for action in r.plan: print(action)
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/colt_express/s2_recursive_round/problems.py
```

## File structure

```
s2_recursive_round/
├── __init__.py     # Package initialization
├── domain.py       # 4 actions, 4 methods across 2 task names
├── problems.py     # 3 scenarios + doctests
└── README.md       # This file
```

## Reference

- Pattern source: trunk_thumper s06 (Game AI Pro 1, Troy Humphreys, CRC Press 2015, §12.6).
- Colt Express rulebook (Phase 2 Stealin', p.3; Events Hostage-Taking, p.5).

---
*Generated 2026-05-16*
