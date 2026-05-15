# ============================================================================
# Trunk Thumper - Section 12.3 Baseline (Putting Together an HTN Domain)
# ============================================================================
#
# REFERENCE:
# Troy Humphreys, "Exploring HTN Planners through Example," in Game AI Pro
# (Steve Rabin, ed.), CRC Press, 2015, pp. 154-155 (Section 12.3).
#
# MOTIVATION:
# The baseline Trunk Thumper. The chapter introduces a "Trunk Thumper" troll
# NPC that patrols bridges and attacks passing enemies with a tree trunk.
# This sub-folder implements the simplest version of the troll's behavior:
# one root compound task (BeTrunkThumper) with two methods (attack or patrol).
# No recursion, no expected effects, no priority subtleties.
#
# CHAPTER QUOTE:
# "Compound Task [BeTrunkThumper]
#      Method [WsCanSeeEnemy == true]
#          Subtasks [NavigateToEnemy(), DoTrunkSlam()]
#      Method [true]
#          Subtasks [ChooseBridgeToCheck(), NavigateToBridge(), CheckBridge()]"
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# This file is organized into the following sections:
#   - Imports
#   - Domain (1)
#   - State Property Map
#   - Helper Functions
#   - Actions (5)
#   - Methods (1 task name with 2 alternative methods)
#   - Registration
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

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

the_domain = Domain("trunk_thumper_s03")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (Trunk Thumper s03 baseline)
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#  - [CONFIG]  Set at scenario creation, not modified by actions
#
# World perception:
#  can_see_enemy: bool                                  (P)   [CONFIG]
#  enemy_location: str                                  (P)   [CONFIG]
#
# Troll state:
#  location: str                                        (E/P) [DATA]
#  next_bridge_to_check: Optional[str]                  (E/P) [DATA]
#
# Patrol configuration:
#  bridges: list[str]                                   (P)   [CONFIG]
#  bridges_checked: list[str]                           (E/P) [DATA]
# ============================================================================


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _h_pick_next_bridge(state: State) -> Optional[str]:
    """Pick the next bridge to check: the first one not in bridges_checked."""
    for bridge in state.bridges:
        if bridge not in state.bridges_checked:
            return bridge
    # All checked; cycle back to the first
    if state.bridges:
        return state.bridges[0]
    return None


# ============================================================================
# ACTIONS (5)
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
        Navigate to the enemy's location. The chapter's
        Primitive Task [NavigateToEnemy] / Operator [NavigateToOperator(EnemyLocRef)]
        with Effects [WsLocation = EnemyLocRef].

    Preconditions:
        - The troll can see the enemy (state.can_see_enemy)

    Effects:
        - Troll's location is now the enemy's location (state.location) [DATA]

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
    # [DATA] Troll's location updated to enemy's location
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
        Execute the trunk slam attack. The chapter's
        Primitive Task [DoTrunkSlam] / Operator [AnimatedAttackOperator(TrunkSlamAnimName)].
        In the chapter's literal §12.3 this task has no preconditions or effects;
        later sections add WsTrunkHealth decrement (§12.6), AttackedRecently
        (§12.8), WsPowerUp accumulation (§12.8), and WsIsTired (§12.8). We add
        a minimal slams_performed counter here so the action is not idempotent
        (GTPyhop elides actions that return state unchanged from result.plan).

    Preconditions:
        None (per the chapter)

    Effects:
        - slams_performed incremented by 1 (state.slams_performed) [DATA]

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
    # No preconditions in the baseline
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Track that a slam occurred; ensures the action is not idempotent
    state.slams_performed = state.slams_performed + 1
    # END: Effects

    return state


def a_choose_bridge_to_check(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_choose_bridge_to_check(state)

    Action parameters:
        None

    Action purpose:
        Select the next bridge for the troll to patrol. The chapter's
        Primitive Task [ChooseBridgeToCheck] / Operator [ChooseBridgeToCheckOperator].
        We model the selection deterministically as "first bridge not yet checked;
        cycle back to the start if all have been checked."

    Preconditions:
        - At least one bridge exists (state.bridges)

    Effects:
        - next_bridge_to_check is set to the selected bridge (state.next_bridge_to_check) [ENABLER]

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
    if not state.bridges:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Selected bridge gates the subsequent navigate + check actions
    state.next_bridge_to_check = _h_pick_next_bridge(state)
    # END: Effects

    return state


def a_navigate_to_bridge(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_navigate_to_bridge(state)

    Action parameters:
        None

    Action purpose:
        Navigate to the chosen bridge. The chapter's
        Primitive Task [NavigateToBridge] / Operator [NavigateToOperator(NextBridgeLocRef)]
        with Effects [WsLocation = NextBridgeLocRef].

    Preconditions:
        - A bridge has been chosen (state.next_bridge_to_check is not None)

    Effects:
        - Troll's location is now the chosen bridge (state.location) [DATA]

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
    if state.next_bridge_to_check is None:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Troll's location updated to chosen bridge
    state.location = state.next_bridge_to_check
    # END: Effects

    return state


def a_check_bridge(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_check_bridge(state)

    Action parameters:
        None

    Action purpose:
        Inspect the current bridge for enemies. The chapter's
        Primitive Task [CheckBridge] / Operator [CheckBridgeOperator(SearchAnimName)].
        We record the bridge as having been checked, which makes
        a_choose_bridge_to_check pick a different one next time (until all
        bridges have been checked, after which it cycles).

    Preconditions:
        - The troll has navigated to a chosen bridge
          (state.location == state.next_bridge_to_check)

    Effects:
        - Current bridge added to bridges_checked (state.bridges_checked) [DATA]

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
    if state.next_bridge_to_check is None:
        return False
    if state.location != state.next_bridge_to_check:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Record this bridge as checked
    if state.location not in state.bridges_checked:
        state.bridges_checked = list(state.bridges_checked) + [state.location]
    # END: Effects

    return state


# ============================================================================
# METHODS (1 task name, 2 alternative methods)
# ============================================================================

def m_attack_visible_enemy(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_visible_enemy(state)

    Method parameters:
        None

    Method purpose:
        First method of BeTrunkThumper: when the troll can see an enemy,
        navigate to them and execute the trunk slam.

    Preconditions:
        - The troll can see the enemy (state.can_see_enemy)

    Task decomposition:
        - a_navigate_to_enemy: Close the distance to the enemy
        - a_do_trunk_slam: Hit the enemy with the trunk

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


def m_patrol_bridges(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_patrol_bridges(state)

    Method parameters:
        None

    Method purpose:
        Second method of BeTrunkThumper: when no enemy is visible, patrol
        the bridges. Select a bridge, navigate to it, and check it.

    Preconditions:
        None (fallback method; chapter writes Method [true])

    Task decomposition:
        - a_choose_bridge_to_check: Pick the next bridge
        - a_navigate_to_bridge: Walk there
        - a_check_bridge: Inspect it

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
    # No preconditions - this is the fallback when no enemy is visible
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_choose_bridge_to_check',),
        ('a_navigate_to_bridge',),
        ('a_check_bridge',),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_navigate_to_enemy,
    a_do_trunk_slam,
    a_choose_bridge_to_check,
    a_navigate_to_bridge,
    a_check_bridge,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Root task: BeTrunkThumper. Method ordering = priority (chapter §12.8).
# Attack visible enemy first, fall back to patrol if no enemy seen.
declare_task_methods('m_be_trunk_thumper',
                     m_attack_visible_enemy,
                     m_patrol_bridges)

# ============================================================================
# END OF FILE
# ============================================================================
