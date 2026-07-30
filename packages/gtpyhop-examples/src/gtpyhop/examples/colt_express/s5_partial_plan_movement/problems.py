"""
Problem definitions for the Colt Express s5 partial-plan movement example.
-- Generated 2026-05-16

Three scenarios demonstrate the method-split partial-plan pattern:
  - scenario_1_full_plan_long_horizon: SAME state as scenario 2, but
    invokes m_resolve_move_full_plan. Plan = 2 actions (commits to
    move + rob upfront).
  - scenario_2_partial_plan_pursue_strongbox: SAME state as scenario 1,
    but invokes m_resolve_move_partial_plan. Plan = 1 action
    (m_pursue_strongbox fires; the robbery is deferred to a future
    re-plan after the bandit's situation is reassessed).
  - scenario_3_partial_plan_flee_marshal: Marshal-adjacent state,
    invokes m_resolve_move_partial_plan. Plan = 1 action
    (m_flee_marshal fires; bandit moves AWAY from Marshal).

Pattern source: trunk_thumper s10_partial_plans (Game AI Pro Chapter
12.10). Scenarios 1 and 2 use the SAME state and differ only in which
root task they invoke — exactly the s10 idiom for demonstrating the
plan-length contrast.

m_chase_richest_car and m_move_default are defined for completeness but
not specifically exercised by these three scenarios; they fire when
state conditions exclude flee and pursue (e.g., no marshal, no strongbox).
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


def _h_make_state_with_strongbox_at_locomotive(name: str) -> State:
    """Shared state for scenarios 1 and 2: Belle at caboose, c1 has
    purse_300, locomotive has strongbox_1000, no marshal."""
    state = h_create_base_state(name)
    _h_setup_train(state, ['locomotive', 'c1', 'caboose'])
    state.bandits = ['belle']
    state.bandit_car = {'belle': 'caboose'}
    state.bandit_level = {'belle': 'interior'}
    state.bandit_purse = {'belle': 0}
    state.bandit_bullets_taken = {'belle': 0}
    state.bandit_character = {'belle': 'plain'}
    state.loot_at = {
        'locomotive': ['strongbox_1000'],
        'c1':         ['purse_300'],
        'caboose':    [],
    }
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: colt_express_s5

# BEGIN: Scenario: scenario_1_full_plan_long_horizon
# Configuration
# Setup: Belle at caboose interior; c1 has purse_300; locomotive has
# strongbox_1000; no marshal. Invokes m_resolve_move_full_plan, which
# commits to a 2-action decomposition: move forward + rob at destination.
# Plan length = 2.
# SAME state as scenario 2; contrast in plan length comes from the
# different task name invoked.

# State
initial_state_scenario_1 = _h_make_state_with_strongbox_at_locomotive(
    'scenario_1_full_plan_long_horizon')

# Problem
problems['scenario_1_full_plan_long_horizon'] = (
    initial_state_scenario_1,
    [('m_resolve_move_full_plan', 'belle')],
    'Full plan: commits to a_move forward + a_robbery upfront -> 2 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_partial_plan_pursue_strongbox
# Configuration
# Setup: IDENTICAL to scenario 1. Invokes m_resolve_move_partial_plan.
# Priority ladder: m_flee_marshal falls through (no marshal),
# m_pursue_strongbox fires (strongbox at locomotive, marshal not adjacent,
# Belle not at locomotive). Plan length = 1.

# State
initial_state_scenario_2 = _h_make_state_with_strongbox_at_locomotive(
    'scenario_2_partial_plan_pursue_strongbox')

# Problem
problems['scenario_2_partial_plan_pursue_strongbox'] = (
    initial_state_scenario_2,
    [('m_resolve_move_partial_plan', 'belle')],
    'Partial plan, same state as scenario 1: m_pursue_strongbox fires -> '
    '1 action'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_partial_plan_flee_marshal
# Configuration
# Setup: Belle at c1 interior; marshal at locomotive (adjacent). No loot
# anywhere relevant. m_resolve_move_partial_plan ladder: m_flee_marshal
# fires (marshal adjacent forward of Belle, flee = backward). Plan = 1.

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_partial_plan_flee_marshal')
_h_setup_train(initial_state_scenario_3, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_3.bandits = ['belle']
initial_state_scenario_3.bandit_car = {'belle': 'c1'}
initial_state_scenario_3.bandit_level = {'belle': 'interior'}
initial_state_scenario_3.bandit_purse = {'belle': 0}
initial_state_scenario_3.bandit_bullets_taken = {'belle': 0}
initial_state_scenario_3.bandit_character = {'belle': 'plain'}
initial_state_scenario_3.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}
initial_state_scenario_3.marshal_car = 'locomotive'

# Problem
problems['scenario_3_partial_plan_flee_marshal'] = (
    initial_state_scenario_3,
    [('m_resolve_move_partial_plan', 'belle')],
    'Partial plan, marshal adjacent forward of Belle: m_flee_marshal '
    'fires, Belle moves backward -> 1 action'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.colt_express.s5_partial_plan_movement import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 - Full plan commits to move + rob upfront (2 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_full_plan_long_horizon'][0]),
    ...                      probs['scenario_1_full_plan_long_horizon'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 2)
    >>> r1.plan[0][0]
    'a_move'
    >>> r1.plan[1][0]
    'a_robbery'

    Scenario 2 - SAME state as 1, partial plan returns one action (pursue
    strongbox).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_partial_plan_pursue_strongbox'][0]),
    ...                      probs['scenario_2_partial_plan_pursue_strongbox'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 1)
    >>> r2.plan[0][0]
    'a_move'
    >>> r2.plan[0][2]
    'forward'

    Scenario 3 - Marshal adjacent, partial plan flees backward (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_partial_plan_flee_marshal'][0]),
    ...                      probs['scenario_3_partial_plan_flee_marshal'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 1)
    >>> r3.plan[0][0]
    'a_move'
    >>> r3.plan[0][2]
    'backward'

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
