"""
Problem definitions for the Trunk Thumper s09 simultaneous-behaviors example.
-- Generated 2026-05-15

Three scenarios demonstrate the four-method priority structure:
  - scenario_1_melee_range_slam: enemy in melee -> slam (1 action)
  - scenario_2_out_of_range_navigate: enemy far -> non-blocking navigate (1 action)
  - scenario_3_navigating_and_hit_so_guard: navigating + hit by ranged -> guard
    (1 action; the simultaneous-behavior demonstration)

Each scenario is a single planner invocation. The chapter's point is that
GIVEN the right world state at the right moment, the planner picks the
right one-action behavior - the guard action interleaves with ongoing
path-following because nav is non-blocking.

Reference: Section 12.9 of [Humphreys 15].
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
    state.has_enemy = False
    state.enemy_range = 'out_of_range'  # 'melee' or 'out_of_range'
    state.hit_by_ranged_attack = False
    state.navigating = False
    state.slams_performed = 0
    state.guards_performed = 0
    state.navigations_started = 0
    state.idles_performed = 0
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: trunk_thumper_s09

# BEGIN: Scenario: scenario_1_melee_range_slam
# Enemy is in melee range -> first method fires, single slam action
# State
initial_state_scenario_1 = h_create_base_state('scenario_1_melee_range_slam')
initial_state_scenario_1.has_enemy = True
initial_state_scenario_1.enemy_range = 'melee'

# Problem
problems['scenario_1_melee_range_slam'] = (
    initial_state_scenario_1,
    [('m_be_trunk_thumper',)],
    'Enemy in melee range; m_melee_slam fires -> 1 action'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_out_of_range_navigate
# Enemy is out of melee range -> second method fires, non-blocking navigate
# State
initial_state_scenario_2 = h_create_base_state('scenario_2_out_of_range_navigate')
initial_state_scenario_2.has_enemy = True
initial_state_scenario_2.enemy_range = 'out_of_range'

# Problem
problems['scenario_2_out_of_range_navigate'] = (
    initial_state_scenario_2,
    [('m_be_trunk_thumper',)],
    'Enemy out of range; m_out_of_range_navigate fires; non-blocking nav '
    'sets state.navigating=True for next-tick re-plan -> 1 action'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_navigating_and_hit_so_guard
# THE SIMULTANEOUS-BEHAVIOR DEMONSTRATION: navigation is already in progress
# (state.navigating=True), and the troll just got hit by a ranged attack
# -> the guard method fires WHILE path-following continues in the background.
# State
initial_state_scenario_3 = h_create_base_state('scenario_3_navigating_and_hit_so_guard')
initial_state_scenario_3.has_enemy = False  # crucial: prevents methods 1 and 2 from firing
initial_state_scenario_3.navigating = True
initial_state_scenario_3.hit_by_ranged_attack = True

# Problem
problems['scenario_3_navigating_and_hit_so_guard'] = (
    initial_state_scenario_3,
    [('m_be_trunk_thumper',)],
    'Navigating in background, hit by ranged attack; m_guard_during_navigation '
    'fires; the guard action interleaves with ongoing path-following -> 1 action'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.trunk_thumper.s09_simultaneous_navigation_and_guard import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 - Melee range, slam (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_melee_range_slam'][0]),
    ...                      probs['scenario_1_melee_range_slam'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 1)
    >>> r1.plan[0][0]
    'a_do_trunk_slam'

    Scenario 2 - Out of range, non-blocking navigate (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_out_of_range_navigate'][0]),
    ...                      probs['scenario_2_out_of_range_navigate'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 1)
    >>> r2.plan[0][0]
    'a_navigate_to_enemy'

    Scenario 3 - Navigating + hit by ranged -> guard (1 action).
    Demonstrates the simultaneous-behavior pattern: navigation runs in the
    background while the planner interleaves a guard.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_navigating_and_hit_so_guard'][0]),
    ...                      probs['scenario_3_navigating_and_hit_so_guard'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 1)
    >>> r3.plan[0][0]
    'a_guard_face_with_arm'

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
