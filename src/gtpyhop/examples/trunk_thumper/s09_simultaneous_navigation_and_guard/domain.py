# ============================================================================
# Trunk Thumper - Section 12.9 Simultaneous Behaviors
# (Managing Simultaneous Behaviors)
# ============================================================================
#
# REFERENCE:
# Troy Humphreys, "Exploring HTN Planners through Example," in Game AI Pro
# (Steve Rabin, ed.), CRC Press, 2015, pp. 163-165 (Section 12.9).
#
# MOTIVATION:
# Behavior selection algorithms are typically good at doing one thing at a
# time, but games sometimes need two things at once - e.g., navigate AND
# guard against incoming ranged attacks. The chapter discusses two approaches:
#   (1) Two domains and two planners (upper body / lower body). Works but
#       costs synchronization, performance, and debuggability. The chapter
#       warns: "you will not gain any friends... trust me."
#   (2) Single planner with non-blocking navigation: a_navigate_to_enemy
#       starts the path-follower and completes immediately (with a
#       Navigating=True side effect). This frees the planner to interleave
#       a guard action while path-following continues in the background.
#
# This sub-folder implements the chapter's RECOMMENDED approach (#2).
#
# CHAPTER QUOTE (the recommended domain):
# "Compound Task [BeTrunkThumper]
#      Method [WsHasEnemy == true, WsEnemyRange <= MeleeRange]
#          Subtasks [DoTrunkSlam()]
#      Method [WsHasEnemy == true, WsEnemyRange > MeleeRange]
#          Subtasks [NavigateToEnemy()]
#      Method [Navigating == true, HitByRangedAttack == true]
#          Subtasks [GuardFaceWithArm()]
#      Method [true]
#          Subtasks [Idle()]"
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

the_domain = Domain("trunk_thumper_s09")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (s09)
# Legend:
#  - (E)/(P) Effects / Preconditions
#  - [ENABLER] Workflow gate
#  - [DATA]    Informational
#  - [CONFIG]  Set at scenario creation
#
# World perception:
#  has_enemy: bool                                      (P)   [CONFIG]
#  enemy_range: str ('melee' or 'out_of_range')         (P)   [CONFIG]
#  hit_by_ranged_attack: bool                           (P)   [CONFIG]
#
# Troll state:
#  navigating: bool                                     (E/P) [ENABLER]
#  slams_performed: int                                 (E)   [DATA]
#  guards_performed: int                                (E)   [DATA]
#  navigations_started: int                             (E)   [DATA]
#  idles_performed: int                                 (E)   [DATA]
# ============================================================================


# ============================================================================
# ACTIONS (4)
# ============================================================================

def a_do_trunk_slam(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_do_trunk_slam(state)

    Action parameters:
        None

    Action purpose:
        Execute the trunk slam attack. In s09 we focus on the simultaneous
        behaviors story, so the action is simplified (no power_up etc.).

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
    # [DATA] Track
    state.slams_performed = state.slams_performed + 1
    # END: Effects

    return state


def a_navigate_to_enemy(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_navigate_to_enemy(state)

    Action parameters:
        None

    Action purpose:
        Start navigation to the enemy. THIS IS A NON-BLOCKING ACTION per
        §12.9's recommended approach. The path-follower runs in the
        background; this action completes immediately, signaling that
        path-following has started via the Navigating flag. The planner
        can then interleave a guard action while traversal is in progress.

    Preconditions:
        - There is an enemy (state.has_enemy)

    Effects:
        - Navigating set True (state.navigating) [ENABLER]
        - navigations_started incremented (state.navigations_started) [DATA]

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
    if not state.has_enemy:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Signal that path-following has begun (chapter's key insight)
    state.navigating = True
    # [DATA] Track navigation count
    state.navigations_started = state.navigations_started + 1
    # END: Effects

    return state


def a_guard_face_with_arm(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_guard_face_with_arm(state)

    Action parameters:
        None

    Action purpose:
        Raise an arm to shield the troll's face from incoming ranged attacks.
        Used while navigation is in progress (the chapter's simultaneous-
        behavior demonstration).

    Preconditions:
        None (the priority comes from method ordering)

    Effects:
        - guards_performed incremented (state.guards_performed) [DATA]

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
    # [DATA] Track guard count
    state.guards_performed = state.guards_performed + 1
    # END: Effects

    return state


def a_idle(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_idle(state)

    Action parameters:
        None

    Action purpose:
        Do nothing useful - the chapter's fallback when no other method applies.

    Preconditions:
        None

    Effects:
        - idles_performed incremented (state.idles_performed) [DATA]

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
    # [DATA] Track idle count
    state.idles_performed = state.idles_performed + 1
    # END: Effects

    return state


# ============================================================================
# METHODS
# ============================================================================

def m_melee_slam(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_melee_slam(state)

    Method parameters:
        None

    Method purpose:
        First method of BeTrunkThumper: enemy in melee range -> slam.

    Preconditions:
        - state.has_enemy
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
    if not state.has_enemy:
        return False
    if state.enemy_range != 'melee':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_do_trunk_slam',)]
    # END: Task Decomposition


def m_out_of_range_navigate(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_out_of_range_navigate(state)

    Method parameters:
        None

    Method purpose:
        Second method of BeTrunkThumper: enemy out of melee range -> start
        non-blocking navigation. The action completes immediately, leaving
        path-following to run in the background.

    Preconditions:
        - state.has_enemy
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
    if not state.has_enemy:
        return False
    if state.enemy_range == 'melee':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_navigate_to_enemy',)]
    # END: Task Decomposition


def m_guard_during_navigation(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_guard_during_navigation(state)

    Method parameters:
        None

    Method purpose:
        Third method of BeTrunkThumper: while navigating, if a ranged attack
        landed, raise an arm to guard. This is the chapter's key
        SIMULTANEOUS BEHAVIOR: the guard happens while path-following is
        in progress in the background (state.navigating is True).

    Preconditions:
        - state.navigating (path-following in progress)
        - state.hit_by_ranged_attack

    Task decomposition:
        - a_guard_face_with_arm

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
    if not state.navigating:
        return False
    if not state.hit_by_ranged_attack:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_guard_face_with_arm',)]
    # END: Task Decomposition


def m_idle(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_idle(state)

    Method parameters:
        None

    Method purpose:
        Fourth (fallback) method of BeTrunkThumper.

    Preconditions:
        None

    Task decomposition:
        - a_idle

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
    # None
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_idle',)]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_do_trunk_slam,
    a_navigate_to_enemy,
    a_guard_face_with_arm,
    a_idle,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Method ordering encodes priority (chapter's recommended approach):
#  1. m_melee_slam (enemy in melee range)
#  2. m_out_of_range_navigate (enemy out of range, start non-blocking nav)
#  3. m_guard_during_navigation (already navigating + hit by ranged)
#  4. m_idle (fallback)
declare_task_methods('m_be_trunk_thumper',
                     m_melee_slam,
                     m_out_of_range_navigate,
                     m_guard_during_navigation,
                     m_idle)

# ============================================================================
# END OF FILE
# ============================================================================
