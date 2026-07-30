"""
Problem definitions for the Colt Express s3 marshal-expected-effects example.
-- Generated 2026-05-16

Three scenarios demonstrate the [EXPECTED_EFFECT] tag on the Marshal
forced-escape rule:
  - scenario_1_move_into_marshal_then_fire_from_roof: bandit moves into the
    Marshal's car, gets pushed to roof via [EXPECTED_EFFECT], then fires
    at a roof-bound target in another car. Plan = 2 actions.
  - scenario_2_marshal_action_pushes_bandit: the Marshal moves into a
    bandit's car, pushing the bandit to roof; then the bandit fires.
    Plan = 2 actions.
  - scenario_3_expected_effects_negative_control: same as scenario 1 but
    using the demo variant a_move_demo_no_marshal_trigger that omits the
    [EXPECTED_EFFECT] block. a_fire's "shooter on roof" precondition then
    cannot be satisfied -> plan fails (r.success == False).

Pattern source: trunk_thumper s07_expected_effects_chase (Game AI Pro
Chapter 12.7), scenario 3 of which has the same negative-control shape.
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

# BEGIN: Domain: colt_express_s3

# BEGIN: Scenario: scenario_1_move_into_marshal_then_fire_from_roof
# Configuration
# Setup: Belle in caboose interior; Doc on roof of locomotive; Marshal in c1.
# Belle moves forward into c1 (where the Marshal is) -> [EXPECTED_EFFECT]
# pushes her to roof. She then fires at Doc on roof of locomotive (different
# car, both on roof). Plan length = 2.
_shooter = 'belle'
_target = 'doc'

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_move_into_marshal_then_fire_from_roof')
_h_setup_train(initial_state_scenario_1, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_1.bandits = [_shooter, _target]
initial_state_scenario_1.bandit_car = {_shooter: 'caboose', _target: 'locomotive'}
initial_state_scenario_1.bandit_level = {_shooter: 'interior', _target: 'roof'}
initial_state_scenario_1.bandit_purse = {_shooter: 0, _target: 0}
initial_state_scenario_1.bandit_bullets_taken = {_shooter: 0, _target: 0}
initial_state_scenario_1.bandit_character = {_shooter: 'plain', _target: 'plain'}
initial_state_scenario_1.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}
initial_state_scenario_1.marshal_car = 'c1'

# Problem
problems['scenario_1_move_into_marshal_then_fire_from_roof'] = (
    initial_state_scenario_1,
    [('a_move', _shooter, 'forward'), ('a_fire', _shooter, _target)],
    f'{_shooter} moves forward into Marshal car (c1); [EXPECTED_EFFECT] '
    f'pushes her to roof; then fires at {_target} on roof of locomotive '
    f'-> 2 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_marshal_action_pushes_bandit
# Configuration
# Setup: Belle in c1 interior; Doc on roof of caboose; Marshal in locomotive.
# An a_marshal_move backward moves the Marshal into c1 (Belle's car) ->
# [EXPECTED_EFFECT] pushes Belle to roof. She then fires at Doc.
# Plan length = 2.
_shooter = 'belle'
_target = 'doc'

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_marshal_action_pushes_bandit')
_h_setup_train(initial_state_scenario_2, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_2.bandits = [_shooter, _target]
initial_state_scenario_2.bandit_car = {_shooter: 'c1', _target: 'caboose'}
initial_state_scenario_2.bandit_level = {_shooter: 'interior', _target: 'roof'}
initial_state_scenario_2.bandit_purse = {_shooter: 0, _target: 0}
initial_state_scenario_2.bandit_bullets_taken = {_shooter: 0, _target: 0}
initial_state_scenario_2.bandit_character = {_shooter: 'plain', _target: 'plain'}
initial_state_scenario_2.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}
initial_state_scenario_2.marshal_car = 'locomotive'

# Problem
problems['scenario_2_marshal_action_pushes_bandit'] = (
    initial_state_scenario_2,
    [('a_marshal_move', 'backward'), ('a_fire', _shooter, _target)],
    f'Marshal moves backward from locomotive into c1 ({_shooter}\'s car); '
    f'[EXPECTED_EFFECT] pushes {_shooter} to roof; then she fires at '
    f'{_target} on roof of caboose -> 2 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_expected_effects_negative_control
# Configuration
# Setup: identical to scenario 1.
# Task list uses the demo variant a_move_demo_no_marshal_trigger, which is
# byte-identical to a_move except the [EXPECTED_EFFECT] block is omitted.
# After the demo move, Belle is still on the interior of c1; a_fire's
# "shooter on roof" precondition then fails and planning is impossible.
# Expected: r.success == False, plan length = 0 / None.
_shooter = 'belle'
_target = 'doc'

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_expected_effects_negative_control')
_h_setup_train(initial_state_scenario_3, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_3.bandits = [_shooter, _target]
initial_state_scenario_3.bandit_car = {_shooter: 'caboose', _target: 'locomotive'}
initial_state_scenario_3.bandit_level = {_shooter: 'interior', _target: 'roof'}
initial_state_scenario_3.bandit_purse = {_shooter: 0, _target: 0}
initial_state_scenario_3.bandit_bullets_taken = {_shooter: 0, _target: 0}
initial_state_scenario_3.bandit_character = {_shooter: 'plain', _target: 'plain'}
initial_state_scenario_3.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}
initial_state_scenario_3.marshal_car = 'c1'

# Problem
problems['scenario_3_expected_effects_negative_control'] = (
    initial_state_scenario_3,
    [('a_move_demo_no_marshal_trigger', _shooter, 'forward'), ('a_fire', _shooter, _target)],
    f'NEGATIVE CONTROL: same as scenario 1 but using the demo variant '
    f'a_move_demo_no_marshal_trigger which omits the [EXPECTED_EFFECT]. '
    f'a_fire precondition fails -> plan impossible'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.colt_express.s3_marshal_expected_effects import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 - Bandit moves into Marshal car; [EXPECTED_EFFECT] pushes to
    roof; then fires. Plan = 2 actions.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_move_into_marshal_then_fire_from_roof'][0]),
    ...                      probs['scenario_1_move_into_marshal_then_fire_from_roof'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 2)
    >>> r1.plan[0][0]
    'a_move'
    >>> r1.plan[1][0]
    'a_fire'

    Scenario 2 - Marshal action pushes bandit to roof; bandit then fires.
    Plan = 2 actions.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_marshal_action_pushes_bandit'][0]),
    ...                      probs['scenario_2_marshal_action_pushes_bandit'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 2)
    >>> r2.plan[0][0]
    'a_marshal_move'
    >>> r2.plan[1][0]
    'a_fire'

    Scenario 3 - NEGATIVE CONTROL: demo variant omits [EXPECTED_EFFECT];
    a_fire precondition (shooter on roof) fails -> plan impossible.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_expected_effects_negative_control'][0]),
    ...                      probs['scenario_3_expected_effects_negative_control'][1])
    >>> sys.stdout = _o
    >>> r3.success
    False

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
