"""
Problem definitions for the Trunk Thumper s08 priority-methods example.
-- Generated 2026-05-15

Four scenarios exercise the four priority-ordered methods of m_attack_enemy:
  - scenario_1_slam_and_recovery: default path (navigate + slam + recover, 3 actions)
  - scenario_2_whirlwind_after_three_slams: power_up=3, not tired -> whirlwind combo (2 actions)
  - scenario_3_cannot_navigate_so_boulder_fallback: can't reach enemy -> boulder (2 actions)
  - scenario_4_tired_blocks_whirlwind_combo: power_up=3 BUT tired -> falls back to slam (3 actions)

Reference: Section 12.8 of [Humphreys 15].
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
    state.can_navigate_to_enemy = True
    state.enemy_location = 'unknown'
    state.location = 'starting_position'
    state.trunk_health = 3
    state.power_up = 0
    state.is_tired = False
    state.has_boulder = False
    state.slams_performed = 0
    state.whirlwinds_performed = 0
    state.boulders_thrown = 0
    state.recoveries_performed = 0
    state.available_trunks = []
    state.found_trunk = None
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: trunk_thumper_s08

# BEGIN: Scenario: scenario_1_slam_and_recovery
# Default attack path: enemy visible, can navigate, trunk healthy, not tired
_enemy_location = 'east_bridge'

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_slam_and_recovery')
initial_state_scenario_1.can_see_enemy = True
initial_state_scenario_1.can_navigate_to_enemy = True
initial_state_scenario_1.enemy_location = _enemy_location
initial_state_scenario_1.trunk_health = 3
initial_state_scenario_1.power_up = 0
initial_state_scenario_1.is_tired = False

# Problem
problems['scenario_1_slam_and_recovery'] = (
    initial_state_scenario_1,
    [('m_be_trunk_thumper',)],
    'Default attack: navigate + slam + recover -> 3 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_whirlwind_after_three_slams
# Power_up has accumulated to 3 and the troll is not tired -> whirlwind fires
_enemy_location = 'east_bridge'

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_whirlwind_after_three_slams')
initial_state_scenario_2.can_see_enemy = True
initial_state_scenario_2.can_navigate_to_enemy = True
initial_state_scenario_2.enemy_location = _enemy_location
initial_state_scenario_2.trunk_health = 1
initial_state_scenario_2.power_up = 3
initial_state_scenario_2.is_tired = False

# Problem
problems['scenario_2_whirlwind_after_three_slams'] = (
    initial_state_scenario_2,
    [('m_be_trunk_thumper',)],
    'power_up=3, not tired; m_whirlwind_combo fires -> 2 actions (whirlwind + recover)'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_cannot_navigate_so_boulder_fallback
# Trunk healthy, enemy visible, BUT can_navigate_to_enemy is False
# (e.g., obstacle blocks path) -> falls through to boulder fallback
_enemy_location = 'east_bridge'

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_cannot_navigate_so_boulder_fallback')
initial_state_scenario_3.can_see_enemy = True
initial_state_scenario_3.can_navigate_to_enemy = False  # blocked!
initial_state_scenario_3.enemy_location = _enemy_location
initial_state_scenario_3.trunk_health = 3
initial_state_scenario_3.power_up = 0
initial_state_scenario_3.is_tired = False

# Problem
problems['scenario_3_cannot_navigate_so_boulder_fallback'] = (
    initial_state_scenario_3,
    [('m_be_trunk_thumper',)],
    'can_navigate_to_enemy=False; m_attack_with_intact_trunk fails; '
    'falls through (find-trunk fails, no trunks) -> m_boulder_fallback -> 2 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_4_tired_blocks_whirlwind_combo
# THE CHAPTER'S KEY EXAMPLE FOR §12.8: power_up=3 (whirlwind threshold)
# AND is_tired=True (just slammed). Without the is_tired check, the
# whirlwind would chain directly off the slam (the chapter's "subtle bug").
# WITH the is_tired check, m_whirlwind_combo fails and the planner falls
# through to the default slam+recovery path.
_enemy_location = 'east_bridge'

# State
initial_state_scenario_4 = h_create_base_state('scenario_4_tired_blocks_whirlwind_combo')
initial_state_scenario_4.can_see_enemy = True
initial_state_scenario_4.can_navigate_to_enemy = True
initial_state_scenario_4.enemy_location = _enemy_location
initial_state_scenario_4.trunk_health = 3
initial_state_scenario_4.power_up = 3       # at threshold
initial_state_scenario_4.is_tired = True    # but tired!

# Problem
problems['scenario_4_tired_blocks_whirlwind_combo'] = (
    initial_state_scenario_4,
    [('m_be_trunk_thumper',)],
    'power_up=3 BUT is_tired=True; is_tired guard prevents whirlwind chain; '
    'falls back to slam+recovery -> 3 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.trunk_thumper.s08_priority_methods import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    4

    Scenario 1 - Default slam-and-recovery (3 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_slam_and_recovery'][0]),
    ...                      probs['scenario_1_slam_and_recovery'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 3)
    >>> [a[0] for a in r1.plan]
    ['a_navigate_to_enemy', 'a_do_trunk_slam', 'a_do_recovery_roar']

    Scenario 2 - Whirlwind combo (2 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_whirlwind_after_three_slams'][0]),
    ...                      probs['scenario_2_whirlwind_after_three_slams'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 2)
    >>> [a[0] for a in r2.plan]
    ['a_do_whirlwind_trunk_attack', 'a_do_recovery_roar']

    Scenario 3 - Boulder fallback when cannot navigate (2 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_cannot_navigate_so_boulder_fallback'][0]),
    ...                      probs['scenario_3_cannot_navigate_so_boulder_fallback'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 2)
    >>> [a[0] for a in r3.plan]
    ['a_pickup_boulder', 'a_throw_boulder']

    Scenario 4 - is_tired guards against premature whirlwind (3 actions).
    Without the is_tired precondition, the whirlwind would chain off a slam.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r4 = s.find_plan(copy.deepcopy(probs['scenario_4_tired_blocks_whirlwind_combo'][0]),
    ...                      probs['scenario_4_tired_blocks_whirlwind_combo'][1])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 3)
    >>> [a[0] for a in r4.plan]
    ['a_navigate_to_enemy', 'a_do_trunk_slam', 'a_do_recovery_roar']

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
