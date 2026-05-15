# ============================================================================
# Trunk Thumper - Section 12.7 Expected Effects
# (Planning for World State Changes not Controlled by Tasks)
# ============================================================================
#
# REFERENCE:
# Troy Humphreys, "Exploring HTN Planners through Example," in Game AI Pro
# (Steve Rabin, ed.), CRC Press, 2015, pp. 158-159 (Section 12.7).
#
# MOTIVATION:
# The chapter's designer asks for a chase behavior: when the troll can't see
# the enemy but saw them recently, navigate to the last known location and
# roar once line-of-sight is regained. The naive implementation hits a snag:
# a_regain_los_roar requires WsCanSeeEnemy == True, but nothing in the plan
# *sets* WsCanSeeEnemy — it's a sensor-driven world state property. The
# chapter introduces "expected effects": effects applied during planning to
# model sensor changes that will happen after the operator executes.
#
# CHAPTER QUOTE:
# "Primitive Task [NavToLastEnemyLoc]
#      Operator [NavigateToOperator(LastEnemyLocation)]
#      Effects [WsLocation = LastEnemyLocation]
#      ExpectedEffects [WsCanSeeEnemy = true]"
#
# THE [EXPECTED_EFFECT] TAG:
# GTPyhop does not distinguish runtime effects from expected effects — both
# are applied during planning. The chapter's distinction is preserved as a
# COMMENT-LEVEL TAG in the action's Effects block, alongside [DATA] and
# [ENABLER]. The semantics are identical to [DATA]; the tag is informational.
# See docs/gtpyhop_domain_style_guide.md.
#
# NEGATIVE CONTROL:
# A second action a_nav_to_last_enemy_loc_demo_no_ee is defined identically
# to the canonical action *except* it omits the [EXPECTED_EFFECT]. The
# negative-control scenario uses this action to demonstrate that without
# the expected effect, the plan cannot be completed: a_regain_los_roar's
# precondition fails.
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

the_domain = Domain("trunk_thumper_s07")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (Trunk Thumper s07 - adds chase behavior + expected effects)
# Legend:
#  - (E)/(P) Effects / Preconditions
#  - [ENABLER] Workflow gate
#  - [DATA]    Informational
#  - [CONFIG]  Set at scenario creation
#  - [EXPECTED_EFFECT] (NEW in §12.7) Applied during planning to model
#                     sensor-driven world state changes that happen after
#                     the operator runs
#
# World perception:
#  can_see_enemy: bool                                  (E/P) [CONFIG, EE]
#  has_seen_enemy_recently: bool                        (P)   [CONFIG]
#  enemy_location: str                                  (P)   [CONFIG]
#  last_enemy_location: str                             (P)   [CONFIG]
#
# Troll state:
#  location: str                                        (E/P) [DATA]
#  trunk_health: int                                    (E/P) [ENABLER]
#  slams_performed: int                                 (E)   [DATA]
#  roars_performed: int                                 (E)   [DATA]
#
# Patrol configuration:
#  next_bridge_to_check: Optional[str]                  (E/P) [DATA]
#  bridges: list[str]                                   (P)   [CONFIG]
#  bridges_checked: list[str]                           (E/P) [DATA]
#
# Trunk discovery:
#  available_trunks: list[str]                          (P)   [CONFIG]
#  found_trunk: Optional[str]                           (E/P) [ENABLER]
# ============================================================================


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _h_pick_next_bridge(state: State) -> Optional[str]:
    for bridge in state.bridges:
        if bridge not in state.bridges_checked:
            return bridge
    if state.bridges:
        return state.bridges[0]
    return None


def _h_pick_available_trunk(state: State) -> Optional[str]:
    if state.available_trunks:
        return state.available_trunks[0]
    return None


# ============================================================================
# ACTIONS (10)
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
        Navigate to the enemy's location.

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
        Execute the trunk slam attack.

    Preconditions:
        - The trunk still has health (state.trunk_health > 0)

    Effects:
        - trunk_health decreased by 1 (state.trunk_health) [DATA]
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
    if state.trunk_health <= 0:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Trunk takes wear from the slam
    state.trunk_health = state.trunk_health - 1
    # [DATA] Track that a slam occurred
    state.slams_performed = state.slams_performed + 1
    # END: Effects

    return state


def a_nav_to_last_enemy_loc(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_nav_to_last_enemy_loc(state)

    Action parameters:
        None

    Action purpose:
        Navigate to the last known enemy location. NEW in §12.7. This action
        is the chapter's canonical example of [EXPECTED_EFFECT]: in addition
        to the ordinary location effect, the planner is told to expect that
        the vision sensor will set can_see_enemy = True after arrival.

    Preconditions:
        - The troll has seen the enemy recently (state.has_seen_enemy_recently)
        - The last enemy location is known (state.last_enemy_location)

    Effects:
        - Troll's location is now the last known enemy location (state.location) [DATA]
        - can_see_enemy is set to True (state.can_see_enemy) [EXPECTED_EFFECT]
          Vision sensor will set this once we arrive; without this annotation,
          downstream a_regain_los_roar's precondition would fail at planning
          time. See domain header for the chapter quote.

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
    if not state.has_seen_enemy_recently:
        return False
    if not state.last_enemy_location:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Troll's location updated to last known enemy location
    state.location = state.last_enemy_location

    # [EXPECTED_EFFECT] Vision sensor will set can_see_enemy True after arrival.
    # Per the chapter: "Expected effects are effects that get applied to the
    # world state only during planning and plan validation. The idea here is
    # that you can express changes in the world state that should happen
    # based on tasks being executed." In GTPyhop both kinds of effects are
    # applied identically during planning; the tag is purely informational.
    state.can_see_enemy = True
    # END: Effects

    return state


def a_nav_to_last_enemy_loc_demo_no_ee(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_nav_to_last_enemy_loc_demo_no_ee(state)

    Action parameters:
        None

    Action purpose:
        TEACHING VARIANT (negative control). Identical to
        a_nav_to_last_enemy_loc EXCEPT it omits the [EXPECTED_EFFECT] on
        can_see_enemy. Used by scenario 3 to demonstrate what happens when
        an expected effect is missing: the downstream a_regain_los_roar's
        precondition fails at planning time and the plan is impossible.

    Preconditions:
        - The troll has seen the enemy recently (state.has_seen_enemy_recently)
        - The last enemy location is known (state.last_enemy_location)

    Effects:
        - Troll's location is now the last known enemy location (state.location) [DATA]
        - (deliberately MISSING: the [EXPECTED_EFFECT] on can_see_enemy)

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
    if not state.has_seen_enemy_recently:
        return False
    if not state.last_enemy_location:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Troll's location updated; this variant deliberately OMITS the
    # [EXPECTED_EFFECT] on can_see_enemy that the canonical action has.
    state.location = state.last_enemy_location
    # END: Effects

    return state


def a_regain_los_roar(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_regain_los_roar(state)

    Action parameters:
        None

    Action purpose:
        Play a big roar animation when the troll regains line-of-sight on
        the enemy. NEW in §12.7. The precondition is the key bit: this
        action requires can_see_enemy == True at planning time, which is
        only achievable if the preceding navigation action's
        [EXPECTED_EFFECT] is applied.

    Preconditions:
        - The troll can see the enemy (state.can_see_enemy)
        - This is what motivates the [EXPECTED_EFFECT] tag in the chapter

    Effects:
        - roars_performed incremented by 1 (state.roars_performed) [DATA]

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
    # [DATA] Track that the roar happened
    state.roars_performed = state.roars_performed + 1
    # END: Effects

    return state


def a_find_trunk(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_find_trunk(state)

    Action parameters:
        None

    Action purpose:
        Locate a usable tree trunk nearby.

    Preconditions:
        - At least one trunk is available (state.available_trunks)

    Effects:
        - found_trunk set to the chosen tree (state.found_trunk) [ENABLER]

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
    if not state.available_trunks:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Picked trunk gates the subsequent navigate + uproot actions
    state.found_trunk = _h_pick_available_trunk(state)
    # END: Effects

    return state


def a_navigate_to_trunk(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_navigate_to_trunk(state)

    Action parameters:
        None

    Action purpose:
        Walk to the found tree trunk's location.

    Preconditions:
        - A trunk has been found (state.found_trunk is not None)

    Effects:
        - Troll's location is now the trunk's location (state.location) [DATA]

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
    if state.found_trunk is None:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Troll's location updated to trunk's location
    state.location = state.found_trunk
    # END: Effects

    return state


def a_uproot_trunk(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_uproot_trunk(state)

    Action parameters:
        None

    Action purpose:
        Yank the tree out of the ground, restoring trunk_health to 3.

    Preconditions:
        - The troll is at the found trunk's location

    Effects:
        - trunk_health reset to 3 (state.trunk_health) [ENABLER]
        - found_trunk consumed from available list (state.available_trunks, state.found_trunk) [DATA]

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
    if state.found_trunk is None:
        return False
    if state.location != state.found_trunk:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Trunk health restored to 3
    state.trunk_health = 3
    # [DATA] Consume the picked trunk
    state.available_trunks = [t for t in state.available_trunks if t != state.found_trunk]
    state.found_trunk = None
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
        Select the next bridge for the troll to patrol.

    Preconditions:
        - At least one bridge exists (state.bridges)

    Effects:
        - next_bridge_to_check set (state.next_bridge_to_check) [ENABLER]

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
        Navigate to the chosen bridge.

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
        Inspect the current bridge for enemies.

    Preconditions:
        - The troll has navigated to a chosen bridge

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
# METHODS
# ============================================================================

# --- BeTrunkThumper (NEW: third method for chase) -------------------------

def m_attack_visible_enemy(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_visible_enemy(state)

    Method parameters:
        None

    Method purpose:
        First method of BeTrunkThumper: enemy is visible -> attack.

    Preconditions:
        - state.can_see_enemy

    Task decomposition:
        - m_attack_enemy

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
    return [('m_attack_enemy',)]
    # END: Task Decomposition


def m_chase_recently_seen_enemy(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_chase_recently_seen_enemy(state)

    Method parameters:
        None

    Method purpose:
        Second method of BeTrunkThumper (NEW in §12.7): the troll can't see
        the enemy but has seen them recently -> navigate to last known
        location and roar when line-of-sight is regained. Demonstrates the
        [EXPECTED_EFFECT] tag.

    Preconditions:
        - state.can_see_enemy is False (otherwise m_attack_visible_enemy would have fired)
        - state.has_seen_enemy_recently

    Task decomposition:
        - a_nav_to_last_enemy_loc (sets can_see_enemy via [EXPECTED_EFFECT])
        - a_regain_los_roar (precondition needs can_see_enemy True)

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
    if state.can_see_enemy:
        return False
    if not state.has_seen_enemy_recently:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_nav_to_last_enemy_loc',),
        ('a_regain_los_roar',),
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
        Third method of BeTrunkThumper (was second in §12.6): fallback to
        patrol when neither attack nor chase apply.

    Preconditions:
        None (fallback method)

    Task decomposition:
        - a_choose_bridge_to_check
        - a_navigate_to_bridge
        - a_check_bridge

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
    # No preconditions - fallback method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_choose_bridge_to_check',),
        ('a_navigate_to_bridge',),
        ('a_check_bridge',),
    ]
    # END: Task Decomposition


# --- AttackEnemy (carried forward from §12.6) -----------------------------

def m_attack_with_intact_trunk(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_with_intact_trunk(state)

    Method parameters:
        None

    Method purpose:
        First method of AttackEnemy: trunk has health, navigate and slam.

    Preconditions:
        - state.trunk_health > 0
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
    if state.trunk_health <= 0:
        return False
    if not state.can_see_enemy:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_navigate_to_enemy',),
        ('a_do_trunk_slam',),
    ]
    # END: Task Decomposition


def m_attack_after_finding_new_trunk(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_after_finding_new_trunk(state)

    Method parameters:
        None

    Method purpose:
        Second method of AttackEnemy: find a new trunk, walk there, uproot,
        then recurse into AttackEnemy.

    Preconditions:
        - state.available_trunks (at least one trunk)
        - state.can_see_enemy

    Task decomposition:
        - a_find_trunk
        - a_navigate_to_trunk
        - a_uproot_trunk
        - m_attack_enemy  (recursion)

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
    if not state.available_trunks:
        return False
    if not state.can_see_enemy:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_find_trunk',),
        ('a_navigate_to_trunk',),
        ('a_uproot_trunk',),
        ('m_attack_enemy',),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_navigate_to_enemy,
    a_do_trunk_slam,
    a_nav_to_last_enemy_loc,
    a_nav_to_last_enemy_loc_demo_no_ee,
    a_regain_los_roar,
    a_find_trunk,
    a_navigate_to_trunk,
    a_uproot_trunk,
    a_choose_bridge_to_check,
    a_navigate_to_bridge,
    a_check_bridge,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# BeTrunkThumper: 3 methods (attack | chase | patrol) in priority order
declare_task_methods('m_be_trunk_thumper',
                     m_attack_visible_enemy,
                     m_chase_recently_seen_enemy,
                     m_patrol_bridges)

# AttackEnemy: 2 methods (intact-trunk | find-new-trunk-recurse)
declare_task_methods('m_attack_enemy',
                     m_attack_with_intact_trunk,
                     m_attack_after_finding_new_trunk)

# ============================================================================
# END OF FILE
# ============================================================================
