# Colt Express Examples for GTPyhop

A collection of progressive HTN planning examples based on the **Colt Express**
board game (Christophe Raimbault / Jordi Valbuena, Ludonaute 2014). The
collection's structural template is the [trunk_thumper](../trunk_thumper/)
collection — each sub-folder demonstrates one HTN concept applied to the
game's mechanics, with a direct lineage to a trunk_thumper sub-folder.

## Why this collection exists

The trunk_thumper collection covers the canonical HTN patterns through one
toy game-AI scenario (a troll patrolling bridges). Colt Express applies the
same pattern catalog to a richer, real-world game with multi-bandit
interactions, a sensor-driven Marshal mechanic, character-specific abilities,
and end-of-round events. Together they form a two-tier teaching arc:
trunk_thumper introduces each pattern; colt_express shows the pattern
operating in a more complex domain.

## Scope: Stealin'-only

Colt Express has two phases per round: **Schemin'** (players program a deck
of Action cards under imperfect information) and **Stealin'** (the deck
resolves deterministically). Only the Stealin' phase is modeled here. The
programmed deck is pre-encoded in `state.deck` and the planner resolves it
action-by-action, filling in the parameter choices the rules leave open
(Move direction, Fire target, Robbery pick). The Schemin' phase requires
imperfect-information modeling that is out of scope for classical HTN.

## Sub-folders

| Folder | Pattern source | Topic | Actions | Methods | Scenarios |
|---|---|---|---|---|---|
| `s1_minimal_turn/` | trunk_thumper [s03](../trunk_thumper/s03_basic_attack_or_patrol/) | Priority methods: rob-if-loot vs. move-forward baseline | 3 | 2 | 3 |
| `s3_marshal_expected_effects/` | trunk_thumper [s07](../trunk_thumper/s07_expected_effects_chase/) | `[EXPECTED_EFFECT]` tag for Marshal forced-escape, with negative-control scenario | 6 | 2 | 3 |
| `s2_recursive_round/` | trunk_thumper [s06](../trunk_thumper/s06_recursive_trunk_replacement/) | Recursive deck resolution (head-pop termination) | 4 | 4 | 3 |
| `s4_character_priorities/` | trunk_thumper [s08](../trunk_thumper/s08_priority_methods/) | Priority-method ladder for Belle / Tuco / Django / Cheyenne abilities | 8 | 6 | 4 |
| `s5_partial_plan_movement/` | trunk_thumper [s10](../trunk_thumper/s10_partial_plans/) | Method-split partial plans for movement strategy | 5 | 5 | 3 |

**Totals**: 16 scenarios across 5 sub-folders; 15 pass with expected plan lengths, 1 intentional fail (s3 scenario 3, the [EXPECTED_EFFECT] negative control).

**Build order** (matches the order of effort but not the numeric folder names):
`s1 -> s3 -> s2 -> s4 -> s5`. s3 locks the Marshal-push and `bandit_level`
state shape (the trickiest part of Colt Express) before later sub-folders
are built on top of it.

trunk_thumper's `s09` (simultaneous behaviors via non-blocking navigation)
has no Colt Express analog — bandits play exactly one card per turn — so the
pattern is not represented in this collection.

## Canonical state schema

Every sub-folder's `h_create_base_state` MUST initialize all canonical
fields below (use empty dict / list / `None` when unused in a given
scenario). Fields may be added at the end; never renamed or reshaped.

```python
# === Train geometry ===
state.cars: List[str]                     # ['locomotive', 'c1', 'c2', ...]
state.car_index: Dict[str, int]           # name -> 0..N-1

# === Bandits ===
state.bandits: List[str]                  # ['belle', 'tuco', ...]
state.bandit_car: Dict[str, str]
state.bandit_level: Dict[str, str]        # 'interior' | 'roof'
state.bandit_purse: Dict[str, int]
state.bandit_bullets_taken: Dict[str, int]
state.bandit_character: Dict[str, str]    # 'belle','tuco','django','cheyenne','plain'

# === Loot ===
state.loot_at: Dict[str, List[str]]       # car -> ['purse_300','jewel_500','strongbox_1000',...]

# === Marshal ===
state.marshal_car: Optional[str]          # None if no marshal in scenario

# === Programmed deck (Stealin') ===
state.deck: List[Tuple[str, str]]         # [(bandit, card_kind), ...] head = next to resolve

# === Round / event ===
state.round_number: int
state.event_card: Optional[str]

# === Anti-idempotence counter ===
state.actions_resolved: int
```

Anti-idempotence: GTPyhop elides actions that return state unchanged from
`result.plan`. Every action in this collection increments
`state.actions_resolved` as a safety net so action invocations remain
visible in plans even when their primary effects happen to be no-ops.

## Loot distribution and sampling helper

The collection ships a documented loot-token distribution (counts from the
maintainer's physical Colt Express box) plus a deterministic helper function
that mimics the physical loot-token draw.

```python
COLT_EXPRESS_LOOT_DISTRIBUTION = {
    'purses':      [250]*5 + [300]*2 + [350]*1 + [400]*2 + [450]*1 + [500]*1,  # 12 purses
    'jewels':      [500]*4,                                                     # 4 jewels
    'strongboxes': [1000]*2,                                                    # 2 strongboxes
}

def h_sample_car_loot(seed: int, num_jewels: int = 1, num_purses: int = 4,
                     distribution=None) -> List[str]:
    """Deterministically sample loot tokens for one car. Same seed -> same output."""
```

Note: the rulebook lists 18 purses and 6 jewels; the maintainer's actual
physical set has 12 purses and 4 jewels ("maybe I lost some"). The
collection uses the physical counts as canonical. Scenarios needing more
tokens than the distribution provides may pass an enlarged distribution
into the sampler.

The helper is **copy-pasted** into every sub-folder's `problems.py`, per
the trunk_thumper convention that each sub-folder is a self-contained
teaching artifact.

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.colt_express.s1_minimal_turn import the_domain, get_problems

problems = get_problems()
state, tasks, desc = problems['scenario_1_play_move_card']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(copy.deepcopy(state), tasks)
print(f'Success: {result.success}, plan: {result.plan}')
```

Run all doctests:

```bash
python -m doctest -v src/gtpyhop/examples/colt_express/s1_minimal_turn/problems.py
python -m doctest -v src/gtpyhop/examples/colt_express/s3_marshal_expected_effects/problems.py
python -m doctest -v src/gtpyhop/examples/colt_express/s2_recursive_round/problems.py
python -m doctest -v src/gtpyhop/examples/colt_express/s4_character_priorities/problems.py
python -m doctest -v src/gtpyhop/examples/colt_express/s5_partial_plan_movement/problems.py
```

Run a benchmark:

```bash
cd src/gtpyhop/examples/colt_express
python benchmarking.py --list-domains
python benchmarking.py s1_minimal_turn
python benchmarking.py s3_marshal_expected_effects --strategy iterative_dfs_backtracking
```

## File structure

```
colt_express/
├── __init__.py
├── README.md                       # this file
├── benchmarking.py                 # adapted from trunk_thumper/benchmarking.py
├── benchmarking_quickstart.md      # how to run benchmarks + expected plan lengths
├── s1_minimal_turn/
├── s3_marshal_expected_effects/
├── s2_recursive_round/
├── s4_character_priorities/
└── s5_partial_plan_movement/
```

## Out of scope

- **Schemin' phase**: strategic card selection under imperfect information.
- **Ghost character**: face-down-first-card mechanic complicates the deck-
  resolution recursion.
- **6 of 7 Event cards**: only `hostage_taking` is modeled in s2.
- **Loot maximization** ("richest bandit wins"): HTN goals are discrete;
  cost-aware planning is a v3.0 concern.
- **Hidden Purse values**: all loot values exposed in `state.loot_at`.
  Realism is preserved via the deterministic `h_sample_car_loot` helper that
  mimics the physical token draw.

## References

- **Colt Express rulebook** — Christophe Raimbault, Jordi Valbuena.
  Ludonaute / Asmodee, 2014. <http://www.coltexpress.ludonaute.fr>
- **Pattern source**: trunk_thumper collection (Game AI Pro Chapter 12,
  Troy Humphreys, CRC Press 2015).

---
*Generated 2026-05-16*
