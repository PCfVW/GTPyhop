"""
Problem definitions for the Colt Express s2 recursive-round example.
-- Generated 2026-05-16

Three scenarios demonstrate recursive deck resolution via
m_resolve_programmed_deck (base case + recursive method) and the
m_play_round orchestrator (with and without an end-of-round event):
  - scenario_1_one_round_three_turns: 3-card deck, no event -> 3 actions
  - scenario_2_longer_deck_resolution: 6-card deck, no event -> 6 actions
    (note: framed in the plan as "two rounds back to back" but
    implemented as one resolution of a longer deck; per-round
    granularity is not modeled in s2)
  - scenario_3_round_with_hostage_taking_event: 3-card deck + event ->
    4 actions (3 deck actions plus a_apply_event)

Pattern source: trunk_thumper s06_recursive_trunk_replacement (Game AI
Pro Chapter 12.6). Termination story mirrors s06's WsTrunkHealth reset:
each card action head-pops state.deck, eventually emptying it, at which
point the base-case method m_resolve_deck_empty fires with return [].
"""

import sys
import os
from typing import Dict, Tuple, List, Optional

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State


# ============================================================================
# LOOT DISTRIBUTION (canonical; copy-pasted from s1)
# ============================================================================

COLT_EXPRESS_LOOT_DISTRIBUTION: Dict[str, List[int]] = {
    'purses':      [250]*5 + [300]*2 + [350]*1 + [400]*2 + [450]*1 + [500]*1,
    'jewels':      [500]*4,
    'strongboxes': [1000]*2,
}


# ============================================================================
# HELPER FUNCTIONS (canonical; copy-pasted from s1)
# ============================================================================

def h_sample_car_loot(seed: int,
                      num_jewels: int = 1,
                      num_purses: int = 4,
                      distribution: Optional[Dict[str, List[int]]] = None
                      ) -> List[str]:
    """
    Deterministically sample loot tokens for one car from the distribution.

    Returns a list of string tokens like
        ['jewel_500', 'purse_250', 'purse_300', 'purse_500', 'purse_250']

    Sampling is WITHOUT replacement from a copy of the distribution. The
    same seed yields the same output, so scenarios are reproducible.

    Args:
        seed: Integer seed for the deterministic PRNG.
        num_jewels: How many jewel tokens to include (default 1).
        num_purses: How many purse tokens to include (default 4).
        distribution: Optional override of COLT_EXPRESS_LOOT_DISTRIBUTION.

    Returns:
        List of loot-token strings, jewels first, then purses.
    """
    import random
    if distribution is None:
        distribution = COLT_EXPRESS_LOOT_DISTRIBUTION
    rng = random.Random(seed)
    jewels = list(distribution.get('jewels', []))
    purses = list(distribution.get('purses', []))
    rng.shuffle(jewels)
    rng.shuffle(purses)
    tokens  = [f'jewel_{v}' for v in jewels[:num_jewels]]
    tokens += [f'purse_{v}' for v in purses[:num_purses]]
    return tokens


def h_create_base_state(name: str) -> State:
    """
    Create a base state with the FULL canonical schema initialized.

    Sub-folders may add fields to this state after construction, but must
    not rename or reshape canonical fields. Unused fields are initialized
    to empty containers / None / 0 so cross-folder scenario copy-paste
    works without surprises.
    """
    state = State(name)

    # === Train geometry ===
    state.cars = []
    state.car_index = {}

    # === Bandits ===
    state.bandits = []
    state.bandit_car = {}
    state.bandit_level = {}
    state.bandit_purse = {}
    state.bandit_bullets_taken = {}
    state.bandit_character = {}

    # === Loot ===
    state.loot_at = {}

    # === Marshal ===
    state.marshal_car = None

    # === Programmed deck (Stealin') ===
    state.deck = []

    # === Round / event ===
    state.round_number = 1
    state.event_card = None

    # === Anti-idempotence counter ===
    state.actions_resolved = 0

    return state


def _h_setup_train(state: State, car_names: List[str]) -> None:
    """Convenience helper: populate state.cars and state.car_index."""
    state.cars = list(car_names)
    state.car_index = {name: i for i, name in enumerate(car_names)}


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: colt_express_s2

# BEGIN: Scenario: scenario_1_one_round_three_turns
# Configuration
# Setup: Belle in caboose interior; c1 has a purse_500.
# Deck = [(belle, move), (belle, robbery), (belle, move)].
# Expected plan: a_move (caboose -> c1), a_robbery (purse_500), a_move
# (c1 -> locomotive). Plan length = 3.
_bandit = 'belle'

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_one_round_three_turns')
_h_setup_train(initial_state_scenario_1, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_1.bandits = [_bandit]
initial_state_scenario_1.bandit_car = {_bandit: 'caboose'}
initial_state_scenario_1.bandit_level = {_bandit: 'interior'}
initial_state_scenario_1.bandit_purse = {_bandit: 0}
initial_state_scenario_1.bandit_bullets_taken = {_bandit: 0}
initial_state_scenario_1.bandit_character = {_bandit: 'plain'}
initial_state_scenario_1.loot_at = {'locomotive': [], 'c1': ['purse_500'], 'caboose': []}
initial_state_scenario_1.deck = [
    (_bandit, 'move'),
    (_bandit, 'robbery'),
    (_bandit, 'move'),
]

# Problem
problems['scenario_1_one_round_three_turns'] = (
    initial_state_scenario_1,
    [('m_play_round',)],
    f'Three-card deck for {_bandit}: move + robbery + move; no event -> '
    f'3 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_longer_deck_resolution
# Configuration
# Setup: Belle in caboose interior; c1 has a purse_500.
# Deck = 6 cards: move, robbery, move, floor_change x3.
# Expected plan length: 6. (Plan-language framing: this was called "two
# rounds back to back" in the design plan; the per-round granularity is
# not modeled in s2, so it resolves as one longer deck.)
_bandit = 'belle'

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_longer_deck_resolution')
_h_setup_train(initial_state_scenario_2, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_2.bandits = [_bandit]
initial_state_scenario_2.bandit_car = {_bandit: 'caboose'}
initial_state_scenario_2.bandit_level = {_bandit: 'interior'}
initial_state_scenario_2.bandit_purse = {_bandit: 0}
initial_state_scenario_2.bandit_bullets_taken = {_bandit: 0}
initial_state_scenario_2.bandit_character = {_bandit: 'plain'}
initial_state_scenario_2.loot_at = {'locomotive': [], 'c1': ['purse_500'], 'caboose': []}
initial_state_scenario_2.deck = [
    (_bandit, 'move'),
    (_bandit, 'robbery'),
    (_bandit, 'move'),
    (_bandit, 'floor_change'),
    (_bandit, 'floor_change'),
    (_bandit, 'floor_change'),
]

# Problem
problems['scenario_2_longer_deck_resolution'] = (
    initial_state_scenario_2,
    [('m_play_round',)],
    f'Six-card deck for {_bandit}: move + robbery + move + 3 floor_changes; '
    f'no event -> 6 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_round_with_hostage_taking_event
# Configuration
# Setup: same as scenario 1 PLUS state.event_card = 'hostage_taking'.
# After resolving the 3-card deck Belle ends up at the locomotive. The
# hostage_taking event then gives every bandit at the locomotive $250
# ransom (per rulebook p.5). Expected plan length: 4 (3 deck + 1 event).
_bandit = 'belle'

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_round_with_hostage_taking_event')
_h_setup_train(initial_state_scenario_3, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_3.bandits = [_bandit]
initial_state_scenario_3.bandit_car = {_bandit: 'caboose'}
initial_state_scenario_3.bandit_level = {_bandit: 'interior'}
initial_state_scenario_3.bandit_purse = {_bandit: 0}
initial_state_scenario_3.bandit_bullets_taken = {_bandit: 0}
initial_state_scenario_3.bandit_character = {_bandit: 'plain'}
initial_state_scenario_3.loot_at = {'locomotive': [], 'c1': ['purse_500'], 'caboose': []}
initial_state_scenario_3.deck = [
    (_bandit, 'move'),
    (_bandit, 'robbery'),
    (_bandit, 'move'),
]
initial_state_scenario_3.event_card = 'hostage_taking'

# Problem
problems['scenario_3_round_with_hostage_taking_event'] = (
    initial_state_scenario_3,
    [('m_play_round',)],
    f'Three-card deck for {_bandit} ending at locomotive, plus '
    f'hostage_taking event -> 4 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.colt_express.s2_recursive_round import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 - 3-card deck, no event (3 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_one_round_three_turns'][0]),
    ...                      probs['scenario_1_one_round_three_turns'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 3)
    >>> r1.plan[0][0]
    'a_move'
    >>> r1.plan[1][0]
    'a_robbery'
    >>> r1.plan[2][0]
    'a_move'

    Scenario 2 - 6-card deck, no event (6 actions). Demonstrates that
    recursion handles arbitrary deck lengths.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_longer_deck_resolution'][0]),
    ...                      probs['scenario_2_longer_deck_resolution'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 6)
    >>> r2.plan[0][0]
    'a_move'
    >>> r2.plan[3][0]
    'a_floor_change'
    >>> r2.plan[5][0]
    'a_floor_change'

    Scenario 3 - 3-card deck + hostage_taking event (4 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_round_with_hostage_taking_event'][0]),
    ...                      probs['scenario_3_round_with_hostage_taking_event'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 4)
    >>> r3.plan[3][0]
    'a_apply_event'

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
