# ============================================================================
# Trunk Thumper - Section 12.10 Partial Plans
# (Speeding up Planning with Partial Plans)
# ============================================================================
#
# REFERENCE:
# Troy Humphreys, "Exploring HTN Planners through Example," in Game AI Pro
# (Steve Rabin, ed.), CRC Press, 2015, pp. 165-167 (Section 12.10).
#
# MOTIVATION:
# Partial planning lets the planner stop short of a fully-decomposed plan,
# leaving the rest to be filled in by a future re-plan. This is useful when
# (a) navigation takes a long time and the world state may change before
# arrival, and (b) we'd rather plan a few steps ahead than commit to a long
# sequence that may become invalid mid-execution.
#
# The chapter's RECOMMENDED approach is manual partial-plan splits: break
# one method's [task1, task2] subtask sequence into two separate methods
# (one per situation, distinguished by world state). The planner picks
# whichever method matches the current state and produces a shorter plan;
# when the world state changes, it re-plans and picks the now-applicable
# next method.
#
# CHAPTER QUOTES:
# Pre-split version:
# "Compound Task [BeTrunkThumper]
#      Method [WsCanSeeEnemy == true]
#          Subtasks [NavigateToEnemy(), DoTrunkSlam()]"
#
# Post-split (partial plan) version:
# "Compound Task [BeTrunkThumper]
#      Method [WsCanSeeEnemy == true, WsEnemyRange > MeleeRange]
#          Subtasks [NavigateToEnemy()]
#      Method [WsCanSeeEnemy == true]
#          Subtasks [DoTrunkSlam()]"
#
# This sub-folder declares BOTH versions as separate top-level task names so
# the three scenarios can contrast the full-plan and partial-plan behaviors
# side-by-side.
#
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple

try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods

# ============================================================================
# DOMAIN
# ============================================================================

the_domain = Domain("trunk_thumper_s10")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (s10)
# Legend:
#  - (E)/(P) Effects / Preconditions
#  - [DATA]/[ENABLER]/[CONFIG]
#
# World perception:
#  can_see_enemy: bool                                  (P)   [CONFIG]
#  enemy_range: str ('melee' or 'out_of_range')         (P)   [CONFIG]
#  enemy_location: str                                  (P)   [CONFIG]
#
# Troll state:
#  location: str                                        (E/P) [DATA]
#  slams_performed: int                                 (E)   [DATA]
# ============================================================================


# ============================================================================
# ACTIONS (2)
# ============================================================================

def a_navigate_to_enemy(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_navigate_to_enemy(state)

    Action parameters:
        None

    Action purpose:
        Navigate to the enemy. In the chapter's discussion of partial plans,
        this is the canonical "long-running" task that motivates splitting
        the plan: we don't want to commit to a long [navigate, slam, ...]
        sequence when the world state could change mid-navigation.

    Preconditions:
        - state.can_see_enemy

    Effects:
        - location updated (state.location) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.can_see_enemy:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Troll's location updated
    state.location = state.enemy_location
    # END: Effects

    return state


def a_do_trunk_slam(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_do_trunk_slam(state)

    Action parameters:
        None

    Action purpose:
        Execute the trunk slam attack.

    Preconditions:
        None

    Effects:
        - slams_performed incremented (state.slams_performed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    # None
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Track slam count
    state.slams_performed = state.slams_performed + 1
    # END: Effects

    return state


# ============================================================================
# METHODS
# ============================================================================

# --- Full-plan version (pre-split, the chapter's "before" --------------)

def m_full_plan_navigate_then_slam(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_full_plan_navigate_then_slam(state)

    Method parameters:
        None

    Method purpose:
        Pre-split version: one method, both subtasks. Whenever the troll
        can see the enemy, plan the entire navigate + slam sequence.
        This is what we want to AVOID for long-running navigation - the
        plan commits to slam-after-arrival before we even start moving,
        and the slam can't react if the world changes during transit.

    Preconditions:
        - state.can_see_enemy

    Task decomposition:
        - a_navigate_to_enemy
        - a_do_trunk_slam

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.can_see_enemy:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_navigate_to_enemy',),
        ('a_do_trunk_slam',),
    ]
    # END: Task Decomposition


# --- Partial-plan version (post-split, the chapter's "after" -----------)

def m_partial_plan_navigate_only(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_partial_plan_navigate_only(state)

    Method parameters:
        None

    Method purpose:
        First method of the partial-plan version: enemy visible AND out of
        melee range -> JUST navigate. After the troll arrives, the planner
        replans against the now-updated world state and picks the slam
        method below. This is the chapter's "partial plan" pattern.

    Preconditions:
        - state.can_see_enemy
        - state.enemy_range != 'melee'

    Task decomposition:
        - a_navigate_to_enemy

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.can_see_enemy:
        return False
    if state.enemy_range == 'melee':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_navigate_to_enemy',)]
    # END: Task Decomposition


def m_partial_plan_slam_only(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_partial_plan_slam_only(state)

    Method parameters:
        None

    Method purpose:
        Second method of the partial-plan version: enemy in melee range
        -> JUST slam.

    Preconditions:
        - state.can_see_enemy
        - state.enemy_range == 'melee'

    Task decomposition:
        - a_do_trunk_slam

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.can_see_enemy:
        return False
    if state.enemy_range != 'melee':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_do_trunk_slam',)]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_navigate_to_enemy,
    a_do_trunk_slam,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Two top-level task names so scenarios can compare:
#  m_be_trunk_thumper_full_plan: chapter's pre-split version (1 method, both subtasks)
declare_task_methods('m_be_trunk_thumper_full_plan',
                     m_full_plan_navigate_then_slam)

#  m_be_trunk_thumper_partial_plan: chapter's post-split version (2 methods)
declare_task_methods('m_be_trunk_thumper_partial_plan',
                     m_partial_plan_navigate_only,
                     m_partial_plan_slam_only)

# ============================================================================
# END OF FILE
# ============================================================================
