"""
Problem definitions for the Trunk Thumper s07 expected-effects example.
-- Generated 2026-05-15

Three scenarios:
  - scenario_1_enemy_visible_attack: regression check, first method (2 actions)
  - scenario_2_enemy_recently_seen_chase_and_roar: demonstrates [EXPECTED_EFFECT]
    via the chase-and-roar sequence (2 actions)
  - scenario_3_expected_effects_negative_control: invokes the no-EE variant of
    the navigation action; the plan FAILS because a_regain_los_roar's
    precondition is no longer met at planning time

Reference: Section 12.7 of [Humphreys 15].
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
    state.has_seen_enemy_recently = False
    state.enemy_location = 'unknown'
    state.last_enemy_location = ''
    state.location = 'starting_position'
    state.trunk_health = 3
    state.slams_performed = 0
    state.roars_performed = 0
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

# BEGIN: Domain: trunk_thumper_s07

# BEGIN: Scenario: scenario_1_enemy_visible_attack
# Configuration: regression check that the first method still fires
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
    'Enemy visible; m_attack_visible_enemy -> m_attack_enemy -> intact-trunk -> 2 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_enemy_recently_seen_chase_and_roar
# Configuration: enemy NOT currently visible but seen recently; chase and roar.
# This scenario relies on the [EXPECTED_EFFECT] in a_nav_to_last_enemy_loc to
# satisfy a_regain_los_roar's can_see_enemy precondition during planning.
_last_enemy_location = 'east_bridge'

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_enemy_recently_seen_chase_and_roar')
initial_state_scenario_2.can_see_enemy = False
initial_state_scenario_2.has_seen_enemy_recently = True
initial_state_scenario_2.last_enemy_location = _last_enemy_location
initial_state_scenario_2.bridges = ['north_bridge', 'east_bridge', 'south_bridge']

# Problem
problems['scenario_2_enemy_recently_seen_chase_and_roar'] = (
    initial_state_scenario_2,
    [('m_be_trunk_thumper',)],
    'Enemy recently seen; m_chase_recently_seen_enemy fires; '
    '[EXPECTED_EFFECT] satisfies a_regain_los_roar precondition -> 2 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_expected_effects_negative_control
# Configuration: identical to scenario 2 BUT we invoke the no-EE variant
# directly as the task list. The first action runs (nav happens, location
# updates), but the second action's precondition fails because the missing
# [EXPECTED_EFFECT] means can_see_enemy was never set to True. The plan
# fails, demonstrating WHY expected effects are needed.
_last_enemy_location = 'east_bridge'

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_expected_effects_negative_control')
initial_state_scenario_3.can_see_enemy = False
initial_state_scenario_3.has_seen_enemy_recently = True
initial_state_scenario_3.last_enemy_location = _last_enemy_location
initial_state_scenario_3.bridges = ['north_bridge', 'east_bridge', 'south_bridge']

# Problem
problems['scenario_3_expected_effects_negative_control'] = (
    initial_state_scenario_3,
    [('a_nav_to_last_enemy_loc_demo_no_ee',), ('a_regain_los_roar',)],
    'Negative control: directly invoke the no-[EXPECTED_EFFECT] variant '
    '+ roar. Plan FAILS at the roar precondition -> demonstrates why '
    '[EXPECTED_EFFECT] is needed'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.trunk_thumper.s07_expected_effects_chase import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 - Enemy visible, attack (regression, 2 actions).

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

    Scenario 2 - Recently seen, chase and roar (2 actions).
    Demonstrates that [EXPECTED_EFFECT] satisfies a_regain_los_roar's precondition.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_enemy_recently_seen_chase_and_roar'][0]),
    ...                      probs['scenario_2_enemy_recently_seen_chase_and_roar'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 2)
    >>> r2.plan[0]
    ('a_nav_to_last_enemy_loc',)
    >>> r2.plan[1]
    ('a_regain_los_roar',)

    Scenario 3 - Negative control: no [EXPECTED_EFFECT], plan fails.

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
