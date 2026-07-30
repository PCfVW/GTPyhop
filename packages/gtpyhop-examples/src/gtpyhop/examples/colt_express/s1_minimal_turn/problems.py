"""
Problem definitions for the Colt Express s1 minimal-turn example.
-- Generated 2026-05-16

Three scenarios exercise the two methods of the m_take_turn root task,
plus a manual task list demonstrating a_floor_change:
  - scenario_1_rob_loot_at_position: bandit on car with loot -> rob (1 action)
  - scenario_2_move_forward_no_loot: bandit on empty car -> move (1 action)
  - scenario_3_descend_and_rob: bandit on roof above loot, manual task list
    [a_floor_change, m_take_turn] -> 2 actions

This file also establishes the canonical state schema and the
COLT_EXPRESS_LOOT_DISTRIBUTION / h_sample_car_loot helpers that the other
four sub-folders inherit by copy-paste.

Pattern source: trunk_thumper s03 (Game AI Pro Chapter 12.3).
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
# LOOT DISTRIBUTION (canonical; copy-pasted to every colt_express sub-folder)
# ============================================================================
# Counts from the maintainer's physical Colt Express box. The rulebook lists
# 18 purses and 6 jewels; the actual physical set has 12 purses and 4 jewels
# ("maybe I lost some"). Scenarios needing more tokens may pass an enlarged
# distribution into h_sample_car_loot.

COLT_EXPRESS_LOOT_DISTRIBUTION: Dict[str, List[int]] = {
    'purses':      [250]*5 + [300]*2 + [350]*1 + [400]*2 + [450]*1 + [500]*1,
    'jewels':      [500]*4,
    'strongboxes': [1000]*2,
}


# ============================================================================
# HELPER FUNCTIONS (canonical; copy-pasted to every colt_express sub-folder)
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

# BEGIN: Domain: colt_express_s1

# BEGIN: Scenario: scenario_1_rob_loot_at_position
# Configuration
_bandit = 'belle'
_starting_car = 'c1'
_loot_token = 'purse_500'

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_rob_loot_at_position')
_h_setup_train(initial_state_scenario_1, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_1.bandits = [_bandit]
initial_state_scenario_1.bandit_car = {_bandit: _starting_car}
initial_state_scenario_1.bandit_level = {_bandit: 'interior'}
initial_state_scenario_1.bandit_purse = {_bandit: 0}
initial_state_scenario_1.bandit_bullets_taken = {_bandit: 0}
initial_state_scenario_1.bandit_character = {_bandit: 'plain'}
initial_state_scenario_1.loot_at = {'locomotive': [], 'c1': [_loot_token], 'caboose': []}

# Problem
problems['scenario_1_rob_loot_at_position'] = (
    initial_state_scenario_1,
    [('m_take_turn', _bandit)],
    f'{_bandit} on interior of {_starting_car} with {_loot_token}; '
    f'priority method (rob) selected -> 1 action'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_move_forward_no_loot
# Configuration
_bandit = 'belle'
_starting_car = 'caboose'

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_move_forward_no_loot')
_h_setup_train(initial_state_scenario_2, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_2.bandits = [_bandit]
initial_state_scenario_2.bandit_car = {_bandit: _starting_car}
initial_state_scenario_2.bandit_level = {_bandit: 'interior'}
initial_state_scenario_2.bandit_purse = {_bandit: 0}
initial_state_scenario_2.bandit_bullets_taken = {_bandit: 0}
initial_state_scenario_2.bandit_character = {_bandit: 'plain'}
initial_state_scenario_2.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}

# Problem
problems['scenario_2_move_forward_no_loot'] = (
    initial_state_scenario_2,
    [('m_take_turn', _bandit)],
    f'{_bandit} on {_starting_car} with no loot anywhere; '
    f'fallback method (move forward) selected -> 1 action'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_descend_and_rob
# Configuration
_bandit = 'belle'
_starting_car = 'c1'
_loot_token = 'jewel_500'

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_descend_and_rob')
_h_setup_train(initial_state_scenario_3, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_3.bandits = [_bandit]
initial_state_scenario_3.bandit_car = {_bandit: _starting_car}
initial_state_scenario_3.bandit_level = {_bandit: 'roof'}  # starts on roof
initial_state_scenario_3.bandit_purse = {_bandit: 0}
initial_state_scenario_3.bandit_bullets_taken = {_bandit: 0}
initial_state_scenario_3.bandit_character = {_bandit: 'plain'}
initial_state_scenario_3.loot_at = {'locomotive': [], 'c1': [_loot_token], 'caboose': []}

# Problem
problems['scenario_3_descend_and_rob'] = (
    initial_state_scenario_3,
    [('a_floor_change', _bandit), ('m_take_turn', _bandit)],
    f'{_bandit} on roof of {_starting_car} above {_loot_token}; '
    f'manual task list (floor_change + m_take_turn) -> 2 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.colt_express.s1_minimal_turn import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 - Loot at position, priority method selected (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_rob_loot_at_position'][0]),
    ...                      probs['scenario_1_rob_loot_at_position'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 1)
    >>> r1.plan[0][0]
    'a_robbery'
    >>> r1.plan[0][1]
    'belle'
    >>> r1.plan[0][2]
    'purse_500'

    Scenario 2 - No loot, fallback method selected (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_move_forward_no_loot'][0]),
    ...                      probs['scenario_2_move_forward_no_loot'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 1)
    >>> r2.plan[0][0]
    'a_move'
    >>> r2.plan[0][2]
    'forward'

    Scenario 3 - Bandit on roof above loot, manual sequence (2 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_descend_and_rob'][0]),
    ...                      probs['scenario_3_descend_and_rob'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 2)
    >>> r3.plan[0][0]
    'a_floor_change'
    >>> r3.plan[1][0]
    'a_robbery'
    >>> r3.plan[1][2]
    'jewel_500'

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
