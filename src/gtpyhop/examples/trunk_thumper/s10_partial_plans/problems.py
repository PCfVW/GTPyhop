"""
Problem definitions for the Trunk Thumper s10 partial-plans example.
-- Generated 2026-05-15

Three scenarios contrast the full-plan and partial-plan versions:
  - scenario_1_full_plan_long_horizon: pre-split version produces both actions (2 actions)
  - scenario_2_partial_plan_navigate_only_when_far: post-split with enemy far (1 action)
  - scenario_3_partial_plan_slam_only_when_close: post-split with enemy close (1 action)

Reference: Section 12.10 of [Humphreys 15].
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
    state.enemy_range = 'out_of_range'
    state.enemy_location = 'unknown'
    state.location = 'starting_position'
    state.slams_performed = 0
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: trunk_thumper_s10

# BEGIN: Scenario: scenario_1_full_plan_long_horizon
# Pre-split version: one method handles both navigate + slam.
# State
initial_state_scenario_1 = h_create_base_state('scenario_1_full_plan_long_horizon')
initial_state_scenario_1.can_see_enemy = True
initial_state_scenario_1.enemy_range = 'out_of_range'
initial_state_scenario_1.enemy_location = 'east_bridge'

# Problem
problems['scenario_1_full_plan_long_horizon'] = (
    initial_state_scenario_1,
    [('m_be_trunk_thumper_full_plan',)],
    'Full plan (pre-split): one method produces both navigate AND slam '
    '-> 2 actions. The chapter argues this commits too early.'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_partial_plan_navigate_only_when_far
# Post-split version, enemy out of range -> just navigate. The slam waits
# for the next plan invocation after arrival.
# State
initial_state_scenario_2 = h_create_base_state('scenario_2_partial_plan_navigate_only_when_far')
initial_state_scenario_2.can_see_enemy = True
initial_state_scenario_2.enemy_range = 'out_of_range'
initial_state_scenario_2.enemy_location = 'east_bridge'

# Problem
problems['scenario_2_partial_plan_navigate_only_when_far'] = (
    initial_state_scenario_2,
    [('m_be_trunk_thumper_partial_plan',)],
    'Partial plan (post-split), enemy far: m_partial_plan_navigate_only '
    '-> 1 action. Slam waits for next replan after arrival.'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_partial_plan_slam_only_when_close
# Post-split version, enemy in melee range -> just slam.
# State
initial_state_scenario_3 = h_create_base_state('scenario_3_partial_plan_slam_only_when_close')
initial_state_scenario_3.can_see_enemy = True
initial_state_scenario_3.enemy_range = 'melee'
initial_state_scenario_3.enemy_location = 'east_bridge'

# Problem
problems['scenario_3_partial_plan_slam_only_when_close'] = (
    initial_state_scenario_3,
    [('m_be_trunk_thumper_partial_plan',)],
    'Partial plan (post-split), enemy close: m_partial_plan_slam_only '
    '-> 1 action.'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.trunk_thumper.s10_partial_plans import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    3

    Scenario 1 - Full plan (2 actions: navigate AND slam committed upfront).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_full_plan_long_horizon'][0]),
    ...                      probs['scenario_1_full_plan_long_horizon'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 2)
    >>> [a[0] for a in r1.plan]
    ['a_navigate_to_enemy', 'a_do_trunk_slam']

    Scenario 2 - Partial plan, far (1 action: navigate only).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_partial_plan_navigate_only_when_far'][0]),
    ...                      probs['scenario_2_partial_plan_navigate_only_when_far'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 1)
    >>> r2.plan[0][0]
    'a_navigate_to_enemy'

    Scenario 3 - Partial plan, close (1 action: slam only).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_partial_plan_slam_only_when_close'][0]),
    ...                      probs['scenario_3_partial_plan_slam_only_when_close'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 1)
    >>> r3.plan[0][0]
    'a_do_trunk_slam'

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
