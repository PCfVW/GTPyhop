# ============================================================================
# Trunk Thumper - Section 12.8 Priority Methods
# (How to Handle Higher Priority Plans)
# ============================================================================
#
# REFERENCE:
# Troy Humphreys, "Exploring HTN Planners through Example," in Game AI Pro
# (Steve Rabin, ed.), CRC Press, 2015, pp. 160-163 (Section 12.8).
#
# MOTIVATION:
# The chapter's designer plays the game and asks for two changes:
#   (a) Recovery animation after a trunk slam so the player can react, plus
#       a boulder-attack fallback when the troll cannot navigate to the enemy.
#   (b) A "whirlwind" combo attack that fires after three slams (via WsPowerUp).
#       This introduces a subtle bug: the third slam's effects cause a replan,
#       which immediately fires the whirlwind, chaining attack-into-combo with
#       no breather. The chapter fixes this via WsIsTired: the slam sets the
#       troll tired; the whirlwind precondition requires NOT tired; the
#       recovery clears the tired flag.
#
# CHAPTER QUOTES:
# Sub-story (a): "Compound Task [AttackEnemy]
#      Method [WsTrunkHealth > 0, AttackedRecently == false, CanNavigateToEnemy == true]
#          Subtasks [NavigateToEnemy(), DoTrunkSlam(), RecoveryRoar()]
#      Method [WsTrunkHealth == 0]
#          Subtasks [FindTrunk(), NavigateToTrunk(), UprootTrunk(), AttackEnemy()]
#      Method [true]
#          Subtasks [PickupBoulder(), ThrowBoulder()]"
#
# Sub-story (b): "Primitive Task [DoTrunkSlam]
#      Operator [AnimatedAttackOperator(TrunkSlamAnimName)]
#      Effects [WsPowerUp += 1, WsIsTired = true]
#  Primitive Task [DoWhirlwindTrunkAttack]
#      Preconditions [WsIsTired == false]
#      Operator [DoWhirlwindTrunkAttack()]
#      Effects [WsPowerUp = 0]
#  Primitive Task [DoRecover]
#      Operator [PlayAnimation(TrunkSlamRecoveryAnim)]
#      Effects [WsIsTired = false]"
#
# This s08 sub-folder COMBINES both sub-stories: m_attack_enemy has 4
# methods (whirlwind | slam+recovery | find-new-trunk | boulder-fallback),
# the WsPowerUp/WsIsTired machinery is in place, and four scenarios cover
# the default, the whirlwind, the boulder fallback, and the WsIsTired guard.
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

the_domain = Domain("trunk_thumper_s08")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (s08 - adds power_up, is_tired, can_navigate)
# Legend:
#  - (E)/(P) Effects / Preconditions
#  - [ENABLER] Workflow gate
#  - [DATA]    Informational
#  - [CONFIG]  Set at scenario creation
#
# World perception:
#  can_see_enemy: bool                                  (P)   [CONFIG]
#  can_navigate_to_enemy: bool                          (P)   [CONFIG]  (NEW)
#  enemy_location: str                                  (P)   [CONFIG]
#
# Troll state:
#  location: str                                        (E/P) [DATA]
#  trunk_health: int                                    (E/P) [ENABLER]
#  power_up: int                                        (E/P) [ENABLER]  (NEW)
#  is_tired: bool                                       (E/P) [ENABLER]  (NEW)
#  slams_performed: int                                 (E)   [DATA]
#  whirlwinds_performed: int                            (E)   [DATA]
#  boulders_thrown: int                                 (E)   [DATA]
#
# Trunk discovery:
#  available_trunks: list[str]                          (P)   [CONFIG]
#  found_trunk: Optional[str]                           (E/P) [ENABLER]
# ============================================================================


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _h_pick_available_trunk(state: State) -> Optional[str]:
    if state.available_trunks:
        return state.available_trunks[0]
    return None


# ============================================================================
# ACTIONS (9)
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
        - The troll can reach the enemy (state.can_navigate_to_enemy)

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
    if not state.can_navigate_to_enemy:
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
        Execute the trunk slam attack. Per §12.8 the slam now accumulates
        power_up toward the whirlwind combo AND sets is_tired so the
        whirlwind cannot chain off the same slam.

    Preconditions:
        - The trunk still has health (state.trunk_health > 0)

    Effects:
        - trunk_health decreased by 1 (state.trunk_health) [DATA]
        - power_up incremented by 1 (state.power_up) [ENABLER]
        - is_tired set True (state.is_tired) [ENABLER]
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
    if state.trunk_health <= 0:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Trunk takes wear
    state.trunk_health = state.trunk_health - 1
    # [ENABLER] Accumulate power_up toward whirlwind threshold
    state.power_up = state.power_up + 1
    # [ENABLER] Troll is now tired - gates whirlwind precondition
    state.is_tired = True
    # [DATA] Count
    state.slams_performed = state.slams_performed + 1
    # END: Effects

    return state


def a_do_recovery_roar(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_do_recovery_roar(state)

    Action parameters:
        None

    Action purpose:
        Recovery animation after an attack. Clears is_tired so the troll
        can fire the whirlwind combo next time the power_up threshold is met.

    Preconditions:
        None (always safe to recover)

    Effects:
        - is_tired set False (state.is_tired) [ENABLER]
        - recoveries_performed incremented (state.recoveries_performed) [DATA]

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
    # [ENABLER] Recovery clears the tired flag
    state.is_tired = False
    # [DATA] Track recoveries (also keeps action non-idempotent when troll
    # was already not tired - GTPyhop would otherwise elide the action)
    state.recoveries_performed = state.recoveries_performed + 1
    # END: Effects

    return state


def a_do_whirlwind_trunk_attack(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_do_whirlwind_trunk_attack(state)

    Action parameters:
        None

    Action purpose:
        The "whirlwind" combo attack from §12.8. Fires after three slams
        have charged the troll's power_up. The WsIsTired precondition
        prevents this from chaining directly off a slam.

    Preconditions:
        - power_up has accumulated to 3 (state.power_up >= 3)
        - Troll is not tired (NOT state.is_tired) - the chapter's key fix

    Effects:
        - power_up reset to 0 (state.power_up) [ENABLER]
        - whirlwinds_performed incremented (state.whirlwinds_performed) [DATA]

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
    if state.power_up < 3:
        return False
    if state.is_tired:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Whirlwind consumes the accumulated power_up
    state.power_up = 0
    # [DATA] Track the whirlwind
    state.whirlwinds_performed = state.whirlwinds_performed + 1
    # END: Effects

    return state


def a_pickup_boulder(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_pickup_boulder(state)

    Action parameters:
        None

    Action purpose:
        Pick up a boulder, preparing to throw it. The chapter's
        Primitive Task [PickupBoulder] / Operator [PickupBoulder()].

    Preconditions:
        None

    Effects:
        - Marks that the troll is holding a boulder (state.has_boulder) [ENABLER]

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
    # [ENABLER] Now holding a boulder, enables a_throw_boulder
    state.has_boulder = True
    # END: Effects

    return state


def a_throw_boulder(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_throw_boulder(state)

    Action parameters:
        None

    Action purpose:
        Throw the held boulder at the enemy. The chapter's
        Primitive Task [ThrowBoulder] / Operator [ThrowBoulder()].

    Preconditions:
        - The troll is holding a boulder (state.has_boulder)

    Effects:
        - Boulder released (state.has_boulder = False) [ENABLER]
        - boulders_thrown incremented (state.boulders_thrown) [DATA]

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
    if not state.has_boulder:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Released the boulder
    state.has_boulder = False
    # [DATA] Count the boulder throws
    state.boulders_thrown = state.boulders_thrown + 1
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
        - found_trunk set (state.found_trunk) [ENABLER]

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
        - location is now the trunk's location (state.location) [DATA]

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
        - At the found trunk's location

    Effects:
        - trunk_health reset to 3 (state.trunk_health) [ENABLER]
        - found_trunk consumed (state.available_trunks, state.found_trunk) [DATA]

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


# ============================================================================
# METHODS
# ============================================================================

# --- BeTrunkThumper (top-level) -------------------------------------------

def m_attack_visible_enemy(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_visible_enemy(state)

    Method parameters:
        None

    Method purpose:
        First method of BeTrunkThumper: enemy visible -> AttackEnemy.

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


# --- AttackEnemy (4 methods in priority order) ----------------------------

def m_whirlwind_combo(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_whirlwind_combo(state)

    Method parameters:
        None

    Method purpose:
        Highest-priority method of AttackEnemy (NEW in §12.8): when the
        troll is fully powered up and not tired, do the whirlwind combo
        and recover. The is_tired check prevents this from chaining
        directly off a slam (the chapter's "subtle bug" fix).

    Preconditions:
        - power_up >= 3
        - NOT is_tired

    Task decomposition:
        - a_do_whirlwind_trunk_attack
        - a_do_recovery_roar

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
    if state.power_up < 3:
        return False
    if state.is_tired:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_do_whirlwind_trunk_attack',),
        ('a_do_recovery_roar',),
    ]
    # END: Task Decomposition


def m_attack_with_intact_trunk(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_with_intact_trunk(state)

    Method parameters:
        None

    Method purpose:
        Default attack: navigate, slam, recover.

    Preconditions:
        - state.trunk_health > 0
        - state.can_see_enemy
        - state.can_navigate_to_enemy

    Task decomposition:
        - a_navigate_to_enemy
        - a_do_trunk_slam
        - a_do_recovery_roar

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
    if not state.can_navigate_to_enemy:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_navigate_to_enemy',),
        ('a_do_trunk_slam',),
        ('a_do_recovery_roar',),
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
        Find a new trunk and recurse.

    Preconditions:
        - state.available_trunks
        - state.can_see_enemy

    Task decomposition:
        - a_find_trunk
        - a_navigate_to_trunk
        - a_uproot_trunk
        - m_attack_enemy (recursion)

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


def m_boulder_fallback(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_boulder_fallback(state)

    Method parameters:
        None

    Method purpose:
        Final fallback (NEW in §12.8): pick up and throw a boulder. The
        chapter introduces this for when the troll cannot navigate to the
        enemy.

    Preconditions:
        None (fallback)

    Task decomposition:
        - a_pickup_boulder
        - a_throw_boulder

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
    # No preconditions - fallback
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_pickup_boulder',),
        ('a_throw_boulder',),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_navigate_to_enemy,
    a_do_trunk_slam,
    a_do_recovery_roar,
    a_do_whirlwind_trunk_attack,
    a_pickup_boulder,
    a_throw_boulder,
    a_find_trunk,
    a_navigate_to_trunk,
    a_uproot_trunk,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

declare_task_methods('m_be_trunk_thumper',
                     m_attack_visible_enemy)

# Four methods on AttackEnemy in priority order:
#  1. m_whirlwind_combo (power_up >= 3 AND NOT is_tired)
#  2. m_attack_with_intact_trunk (trunk healthy, can navigate)
#  3. m_attack_after_finding_new_trunk (trunk broken, recurse)
#  4. m_boulder_fallback (always applicable)
declare_task_methods('m_attack_enemy',
                     m_whirlwind_combo,
                     m_attack_with_intact_trunk,
                     m_attack_after_finding_new_trunk,
                     m_boulder_fallback)

# ============================================================================
# END OF FILE
# ============================================================================
