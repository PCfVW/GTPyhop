"""
Problem definitions for the Trunk Thumper s03 baseline example.
-- Generated 2026-05-15

Two scenarios exercise the two methods of the BeTrunkThumper root task:
  - scenario_1_enemy_visible_attack: an enemy is visible -> attack (2 actions)
  - scenario_2_no_enemy_patrol: no enemy visible -> patrol a bridge (3 actions)

Reference: Section 12.3 of [Humphreys 15].
"""

import sys
import os
from typing import Dict, Tuple, List

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def h_create_base_state(name: str) -> State:
    """Create a base state with all properties initialized to sensible defaults."""
    state = State(name)
    state.can_see_enemy = False
    state.enemy_location = 'unknown'
    state.location = 'starting_position'
    state.next_bridge_to_check = None
    state.bridges = []
    state.bridges_checked = []
    state.slams_performed = 0
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: trunk_thumper_s03

# BEGIN: Scenario: scenario_1_enemy_visible_attack
# Configuration
_enemy_location = 'east_bridge'

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_enemy_visible_attack')
initial_state_scenario_1.can_see_enemy = True
initial_state_scenario_1.enemy_location = _enemy_location
initial_state_scenario_1.bridges = ['north_bridge', 'east_bridge', 'south_bridge']

# Problem
problems['scenario_1_enemy_visible_attack'] = (
    initial_state_scenario_1,
    [('m_be_trunk_thumper',)],
    f'Enemy visible at {_enemy_location}; first method (attack) selected '
    f'-> 2 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_no_enemy_patrol
# Configuration

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_no_enemy_patrol')
initial_state_scenario_2.can_see_enemy = False
initial_state_scenario_2.bridges = ['north_bridge', 'east_bridge', 'south_bridge']

# Problem
problems['scenario_2_no_enemy_patrol'] = (
    initial_state_scenario_2,
    [('m_be_trunk_thumper',)],
    'No enemy visible; fallback method (patrol) selected -> 3 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.trunk_thumper.s03_basic_attack_or_patrol import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    2

    Scenario 1 - Enemy visible, attack via first method (2 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_enemy_visible_attack'][0]),
    ...                      probs['scenario_1_enemy_visible_attack'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 2)
    >>> r1.plan[0][0]
    'a_navigate_to_enemy'
    >>> r1.plan[1][0]
    'a_do_trunk_slam'

    Scenario 2 - No enemy, patrol via second method (3 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_no_enemy_patrol'][0]),
    ...                      probs['scenario_2_no_enemy_patrol'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 3)
    >>> r2.plan[0][0]
    'a_choose_bridge_to_check'
    >>> r2.plan[1][0]
    'a_navigate_to_bridge'
    >>> r2.plan[2][0]
    'a_check_bridge'

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
