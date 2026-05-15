# ============================================================================
# Trunk Thumper - Section 12.6 Recursion (Using Recursion for Greater Expressiveness)
# ============================================================================
#
# REFERENCE:
# Troy Humphreys, "Exploring HTN Planners through Example," in Game AI Pro
# (Steve Rabin, ed.), CRC Press, 2015, pp. 157-158 (Section 12.6).
#
# MOTIVATION:
# The chapter's designer requests that the troll's tree trunk break after
# three attacks, forcing him to find another one. This is implemented via
# RECURSION: AttackEnemy is wrapped in a new compound task with two methods,
# and the find-trunk method ends by re-invoking AttackEnemy. Because the
# UprootTrunk action resets WsTrunkHealth to 3, the planner does not infinite
# loop: the second decomposition of AttackEnemy picks the (now-feasible)
# first method.
#
# CHAPTER QUOTE:
# "Compound Task [AttackEnemy]
#      Method [WsTrunkHealth > 0]
#          Subtasks [NavigateToEnemy(), DoTrunkSlam()]
#      Method [true]
#          Subtasks [FindTrunk(), NavigateToTrunk(), UprootTrunk(), AttackEnemy()]"
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

the_domain = Domain("trunk_thumper_s06")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (Trunk Thumper s06 - adds WsTrunkHealth)
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
#  trunk_health: int                                    (E/P) [ENABLER] (NEW in §12.6)
#  slams_performed: int                                 (E)   [DATA]
#
# Patrol configuration:
#  next_bridge_to_check: Optional[str]                  (E/P) [DATA]
#  bridges: list[str]                                   (P)   [CONFIG]
#  bridges_checked: list[str]                           (E/P) [DATA]
#
# Trunk discovery (NEW in §12.6):
#  available_trunks: list[str]                          (P)   [CONFIG]
#  found_trunk: Optional[str]                           (E/P) [ENABLER]
# ============================================================================


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _h_pick_next_bridge(state: State) -> Optional[str]:
    """Pick the next bridge to check: the first one not in bridges_checked."""
    for bridge in state.bridges:
        if bridge not in state.bridges_checked:
            return bridge
    if state.bridges:
        return state.bridges[0]
    return None


def _h_pick_available_trunk(state: State) -> Optional[str]:
    """Pick the first available tree trunk, or None if none remain."""
    if state.available_trunks:
        return state.available_trunks[0]
    return None


# ============================================================================
# ACTIONS (8)
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
        Execute the trunk slam attack. NEW in §12.6: decrements trunk_health,
        per the chapter's design that the trunk breaks after three attacks.

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


def a_find_trunk(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_find_trunk(state)

    Action parameters:
        None

    Action purpose:
        Locate a usable tree trunk nearby. The chapter's
        Primitive Task [FindTrunk] / Operator [...]. Models this by picking
        the first entry from state.available_trunks and recording it in
        state.found_trunk.

    Preconditions:
        - At least one trunk is available (state.available_trunks)

    Effects:
        - found_trunk is set to the chosen tree (state.found_trunk) [ENABLER]

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
        Walk to the found tree trunk's location. The chapter's
        Primitive Task [NavigateToTrunk] / Operator [NavigateToOperator(FoundTrunk)]
        with Effects [WsLocation = FoundTrunk].

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
        Yank the tree out of the ground, restoring trunk_health to 3. The
        chapter's Primitive Task [UprootTrunk] / Operator [UprootTrunkOperator]
        with Effects [WsTrunkHealth = 3]. This is what enables the recursive
        re-decomposition of AttackEnemy to terminate (because the trunk-health
        precondition of the first method is now satisfied).

    Preconditions:
        - The troll is at the found trunk's location (state.location == state.found_trunk)

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
    # [ENABLER] Trunk health restored to 3 (per chapter's UprootTrunk effect)
    state.trunk_health = 3
    # [DATA] Consume the picked trunk from the available list
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
# METHODS
# ============================================================================

# --- BeTrunkThumper -------------------------------------------------------

def m_attack_visible_enemy(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_visible_enemy(state)

    Method parameters:
        None

    Method purpose:
        First method of BeTrunkThumper: when an enemy is visible, invoke
        the AttackEnemy compound task (NEW in §12.6 — previously the subtasks
        were inline).

    Preconditions:
        - The troll can see the enemy (state.can_see_enemy)

    Task decomposition:
        - m_attack_enemy: New compound task that handles trunk health

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


def m_patrol_bridges(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_patrol_bridges(state)

    Method parameters:
        None

    Method purpose:
        Second method of BeTrunkThumper: when no enemy is visible, patrol
        the bridges.

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


# --- AttackEnemy (NEW in §12.6, with recursion) ---------------------------

def m_attack_with_intact_trunk(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_with_intact_trunk(state)

    Method parameters:
        None

    Method purpose:
        First method of AttackEnemy: when the trunk has health, navigate
        to the enemy and slam.

    Preconditions:
        - The trunk still has health (state.trunk_health > 0)
        - The troll can see the enemy (state.can_see_enemy)

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
        Second method of AttackEnemy: find a new trunk, walk there, uproot
        it, then RECURSE into m_attack_enemy. The recursion terminates because
        a_uproot_trunk sets trunk_health = 3, which makes the first method
        (m_attack_with_intact_trunk) applicable on the recursive call.

    Preconditions:
        - At least one usable trunk is available (state.available_trunks)
        - The troll can see the enemy (state.can_see_enemy, needed by the
          recursive call's first-method precondition)

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

declare_task_methods('m_be_trunk_thumper',
                     m_attack_visible_enemy,
                     m_patrol_bridges)

declare_task_methods('m_attack_enemy',
                     m_attack_with_intact_trunk,
                     m_attack_after_finding_new_trunk)

# ============================================================================
# END OF FILE
# ============================================================================
