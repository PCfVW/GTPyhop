"""
Problem definitions for the Trunk Thumper s06 recursive-trunk-replacement example.
-- Generated 2026-05-15

Three scenarios:
  - scenario_1_trunk_intact_direct_slam: trunk has health, attack directly (2 actions)
  - scenario_2_trunk_broken_must_replace_then_attack: trunk is broken, find new one and recurse (5 actions)
  - scenario_3_no_enemy_patrol_regression: no enemy visible, patrol (3 actions; regression check that s03 behavior still works)

Reference: Section 12.6 of [Humphreys 15].
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
    state.trunk_health = 3
    state.slams_performed = 0
    state.next_bridge_to_check = None
    state.bridges = []
    state.bridges_checked = []
    state.available_trunks = []
    state.found_trunk = None
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: trunk_thumper_s06

# BEGIN: Scenario: scenario_1_trunk_intact_direct_slam
# Configuration: trunk has health, enemy visible -> direct attack
_enemy_location = 'east_bridge'

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_trunk_intact_direct_slam')
initial_state_scenario_1.can_see_enemy = True
initial_state_scenario_1.enemy_location = _enemy_location
initial_state_scenario_1.trunk_health = 3
initial_state_scenario_1.bridges = ['north_bridge', 'east_bridge', 'south_bridge']

# Problem
problems['scenario_1_trunk_intact_direct_slam'] = (
    initial_state_scenario_1,
    [('m_be_trunk_thumper',)],
    'Trunk intact (health=3); m_attack_with_intact_trunk selected -> 2 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_trunk_broken_must_replace_then_attack
# Configuration: trunk broken (health=0), forces recursion through
# m_attack_after_finding_new_trunk to uproot a new trunk, then re-attempt
_enemy_location = 'east_bridge'

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_trunk_broken_must_replace_then_attack')
initial_state_scenario_2.can_see_enemy = True
initial_state_scenario_2.enemy_location = _enemy_location
initial_state_scenario_2.trunk_health = 0  # broken!
initial_state_scenario_2.available_trunks = ['oak_grove', 'pine_grove']
initial_state_scenario_2.bridges = ['north_bridge', 'east_bridge', 'south_bridge']

# Problem
problems['scenario_2_trunk_broken_must_replace_then_attack'] = (
    initial_state_scenario_2,
    [('m_be_trunk_thumper',)],
    'Trunk broken (health=0); m_attack_after_finding_new_trunk recurses '
    '-> 5 actions (find, nav_to_trunk, uproot, nav_to_enemy, slam)'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_no_enemy_patrol_regression
# Configuration: regression test - s03's patrol behavior must still work
# State
initial_state_scenario_3 = h_create_base_state('scenario_3_no_enemy_patrol_regression')
initial_state_scenario_3.can_see_enemy = False
initial_state_scenario_3.bridges = ['north_bridge', 'east_bridge', 'south_bridge']

# Problem
problems['scenario_3_no_enemy_patrol_regression'] = (
    initial_state_scenario_3,
    [('m_be_trunk_thumper',)],
    'No enemy visible; m_patrol_bridges selected (regression check) -> 3 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.trunk_thumper.s06_recursive_trunk_replacement import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 - Trunk intact, direct slam (2 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_trunk_intact_direct_slam'][0]),
    ...                      probs['scenario_1_trunk_intact_direct_slam'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 2)
    >>> r1.plan[0][0]
    'a_navigate_to_enemy'
    >>> r1.plan[1][0]
    'a_do_trunk_slam'

    Scenario 2 - Trunk broken, recursion through find-and-uproot (5 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_trunk_broken_must_replace_then_attack'][0]),
    ...                      probs['scenario_2_trunk_broken_must_replace_then_attack'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 5)
    >>> [a[0] for a in r2.plan]
    ['a_find_trunk', 'a_navigate_to_trunk', 'a_uproot_trunk', 'a_navigate_to_enemy', 'a_do_trunk_slam']

    Scenario 3 - No enemy, patrol (regression check, 3 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_no_enemy_patrol_regression'][0]),
    ...                      probs['scenario_3_no_enemy_patrol_regression'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 3)
    >>> r3.plan[0][0]
    'a_choose_bridge_to_check'

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
