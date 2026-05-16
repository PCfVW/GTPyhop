# ============================================================================
# Colt Express - s3 Marshal Expected-Effects
# ============================================================================
#
# PATTERN SOURCE:
# trunk_thumper s07_expected_effects_chase (Game AI Pro Chapter 12.7, Troy
# Humphreys, CRC Press 2015). Introduces the [EXPECTED_EFFECT] tag: effects
# applied to the working world state during planning that represent
# sensor-driven changes (changes the operator does not directly cause but
# which a sensor or external system will produce after the operator runs).
#
# COLT EXPRESS FRAMING:
# The Marshal forced-escape rule is the canonical Colt Express example of an
# [EXPECTED_EFFECT]. Per the rulebook (p.4, "THE MARSHAL"):
# "When a Bandit enters a Car where the Marshal is, or when the Marshal
#  enters a Car where Bandits are, they must escape up to the roof of the
#  Car (even if they have just come down from there). A Bandit can never
#  stay inside the Car where the Marshal is located. Additionally, each one
#  of those Bandits immediately receives a Neutral Bullet card."
#
# The bandit's a_move directly updates state.bandit_car ([DATA]); the roof-
# escape and the neutral-bullet are SYSTEM REACTIONS to that move, not
# operator-driven effects. We model them as [EXPECTED_EFFECT] tagged
# assignments inside a_move so downstream actions whose preconditions
# require the bandit on the roof (e.g., a_fire) can succeed at planning time.
#
# A demo-variant action a_move_demo_no_marshal_trigger is provided as a
# negative control: byte-identical to a_move except the [EXPECTED_EFFECT]
# block is omitted. Scenario 3 invokes this variant to demonstrate plan
# failure when the tag is missing.
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
#   - Imports
#   - Domain (1)
#   - State Property Map
#   - Helper Functions
#   - Actions (6): a_move, a_robbery, a_floor_change, a_marshal_move, a_fire,
#                 plus a_move_demo_no_marshal_trigger (negative control)
#   - Methods (1 task name: m_take_turn with 2 alternative methods, reused
#              from s1)
#   - Registration
# ============================================================================

# ============================================================================
# IMPORTS
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

the_domain = Domain("colt_express_s3")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (canonical Colt Express schema; identical to s1)
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [DATA]            Informational/data container
#  - [EXPECTED_EFFECT] Sensor-driven state change applied at planning time
#  - [CONFIG]          Set at scenario creation, not modified by actions
#
# Train geometry:
#  cars: list[str]                                      (P)   [CONFIG]
#  car_index: dict[str, int]                            (P)   [CONFIG]
#
# Bandits:
#  bandits: list[str]                                   (P)   [CONFIG]
#  bandit_car: dict[str, str]                           (E/P) [DATA]
#  bandit_level: dict[str, str]                         (E/P) [DATA / EXPECTED_EFFECT]
#  bandit_purse: dict[str, int]                         (E)   [DATA]
#  bandit_bullets_taken: dict[str, int]                 (E)   [DATA / EXPECTED_EFFECT]
#  bandit_character: dict[str, str]                           [CONFIG] (unused in s3)
#
# Loot:
#  loot_at: dict[str, list[str]]                        (E/P) [DATA]
#
# Marshal:
#  marshal_car: Optional[str]                           (E/P) [DATA]
#
# Programmed deck (Stealin'):
#  deck: list[tuple[str, str]]                                [CONFIG] (unused in s3; s2 introduces)
#
# Round / event:
#  round_number: int                                          [CONFIG]
#  event_card: Optional[str]                                  [CONFIG]
#
# Anti-idempotence counter:
#  actions_resolved: int                                (E)   [DATA]
# ============================================================================


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _h_pick_loot_to_rob(state: State, car: str) -> Optional[str]:
    """Pick the first loot token in the given car (or None if empty)."""
    loot_here = state.loot_at.get(car, [])
    if not loot_here:
        return None
    return loot_here[0]


# ============================================================================
# ACTIONS (6)
# ============================================================================

def a_move(state: State, bandit: str, direction: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_move(state, bandit, direction)

    Action parameters:
        bandit: ID of the bandit to move (e.g., 'belle')
        direction: 'forward' (toward locomotive) or 'backward' (toward caboose)

    Action purpose:
        Move the bandit one car in the given direction. Evolution from s1:
        adds the [EXPECTED_EFFECT] block for the Marshal forced-escape rule.
        When the destination car contains the Marshal, the bandit is pushed
        to the roof and receives a Neutral Bullet (per the rulebook). This
        is a sensor-driven side effect, not a direct operator effect.
        See a_move_demo_no_marshal_trigger for the negative-control variant.

    Preconditions:
        - The bandit exists in state.bandits (state.bandits)
        - direction is 'forward' or 'backward' (state-type check)
        - The destination car exists (state.car_index)

    Effects:
        - Bandit's car updated to the adjacent car (state.bandit_car) [DATA]
        - If destination car contains the Marshal, bandit is pushed to the
          roof (state.bandit_level) [EXPECTED_EFFECT]
        - If destination car contains the Marshal, bandit receives a
          Neutral Bullet (state.bandit_bullets_taken) [EXPECTED_EFFECT]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(bandit, str): return False
    if not isinstance(direction, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not bandit.strip(): return False
    if direction not in ('forward', 'backward'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if bandit not in state.bandits:
        return False
    current_car = state.bandit_car.get(bandit)
    if current_car is None:
        return False
    current_index = state.car_index.get(current_car)
    if current_index is None:
        return False
    delta = -1 if direction == 'forward' else 1
    destination_index = current_index + delta
    if destination_index < 0 or destination_index >= len(state.cars):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Bandit moves one car in the requested direction
    destination_car = state.cars[destination_index]
    state.bandit_car[bandit] = destination_car

    # [EXPECTED_EFFECT] Marshal forced-escape: if the destination car contains
    # the Marshal, the rulebook forces the bandit onto the roof and gives them
    # a Neutral Bullet card. The sensor/system applies these changes after the
    # operator runs; at planning time we apply them here so downstream actions
    # whose preconditions read these fields can succeed. The demo variant
    # a_move_demo_no_marshal_trigger omits this block as the negative control.
    if state.marshal_car is not None and destination_car == state.marshal_car:
        state.bandit_level[bandit] = 'roof'
        state.bandit_bullets_taken[bandit] = state.bandit_bullets_taken.get(bandit, 0) + 1

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


def a_robbery(state: State, bandit: str, loot_token: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_robbery(state, bandit, loot_token)

    Action parameters:
        bandit: ID of the bandit performing the robbery
        loot_token: The specific loot token to pick up (e.g., 'purse_500')

    Action purpose:
        Identical to s1's a_robbery. The bandit picks up a specific loot
        token from their current car. Must be on the interior.

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit is on 'interior'
        - The loot_token is present in state.loot_at[bandit_car]

    Effects:
        - Loot token removed from car's loot list (state.loot_at) [DATA]
        - Token value added to bandit's purse (state.bandit_purse) [DATA]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(bandit, str): return False
    if not isinstance(loot_token, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not bandit.strip(): return False
    if not loot_token.strip(): return False
    if '_' not in loot_token: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if bandit not in state.bandits:
        return False
    if state.bandit_level.get(bandit) != 'interior':
        return False
    current_car = state.bandit_car.get(bandit)
    if current_car is None:
        return False
    if loot_token not in state.loot_at.get(current_car, []):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Remove the first matching loot token from the car
    new_loot_list = list(state.loot_at[current_car])
    new_loot_list.remove(loot_token)
    state.loot_at[current_car] = new_loot_list

    # [DATA] Add the token's value to the bandit's purse
    value = int(loot_token.rsplit('_', 1)[1])
    state.bandit_purse[bandit] = state.bandit_purse.get(bandit, 0) + value

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


def a_floor_change(state: State, bandit: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_floor_change(state, bandit)

    Action parameters:
        bandit: ID of the bandit changing floors

    Action purpose:
        Identical to s1's a_floor_change. Toggle the bandit between interior
        and roof of their current car.

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit has a valid current level (interior or roof)

    Effects:
        - Bandit's level toggled (state.bandit_level) [DATA]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(bandit, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not bandit.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if bandit not in state.bandits:
        return False
    current_level = state.bandit_level.get(bandit)
    if current_level not in ('interior', 'roof'):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Toggle interior <-> roof
    state.bandit_level[bandit] = 'roof' if current_level == 'interior' else 'interior'

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


def a_marshal_move(state: State, direction: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_marshal_move(state, direction)

    Action parameters:
        direction: 'forward' (toward locomotive) or 'backward' (toward caboose)

    Action purpose:
        Move the Marshal one car in the given direction. Symmetric counterpart
        of a_move's [EXPECTED_EFFECT]: when the Marshal enters a car
        containing any bandits, those bandits are pushed to the roof and
        receive a Neutral Bullet each. Per the rulebook, the Marshal action
        can be triggered by a Bandit's Marshal action card during Stealin'.

    Preconditions:
        - state.marshal_car is set (a Marshal is in play) (state.marshal_car)
        - direction is 'forward' or 'backward' (state-type check)
        - The destination car exists (state.car_index)

    Effects:
        - Marshal's car updated to the adjacent car (state.marshal_car) [DATA]
        - For every bandit in the Marshal's new car: pushed to roof
          (state.bandit_level) [EXPECTED_EFFECT]
        - For every bandit in the Marshal's new car: receives a Neutral
          Bullet (state.bandit_bullets_taken) [EXPECTED_EFFECT]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(direction, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if direction not in ('forward', 'backward'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.marshal_car is None:
        return False
    current_index = state.car_index.get(state.marshal_car)
    if current_index is None:
        return False
    delta = -1 if direction == 'forward' else 1
    destination_index = current_index + delta
    if destination_index < 0 or destination_index >= len(state.cars):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Marshal moves one car
    destination_car = state.cars[destination_index]
    state.marshal_car = destination_car

    # [EXPECTED_EFFECT] Marshal forced-escape: any bandits in the Marshal's
    # new car are pushed to the roof and receive a Neutral Bullet. Same
    # rulebook clause as a_move; this is the symmetric trigger (Marshal moves
    # INTO bandits' car, vs. bandit moves INTO Marshal's car).
    for b in state.bandits:
        if state.bandit_car.get(b) == destination_car:
            state.bandit_level[b] = 'roof'
            state.bandit_bullets_taken[b] = state.bandit_bullets_taken.get(b, 0) + 1

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


def a_fire(state: State, shooter: str, target: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_fire(state, shooter, target)

    Action parameters:
        shooter: ID of the bandit firing
        target: ID of the targeted bandit

    Action purpose:
        Roof-to-roof Fire action. The shooter on the roof of one car fires
        at a target on the roof of a different car. Per the rulebook (p.4):
        "When you are on the roof, however, you can shoot a Bandit who is
        in your Line of Sight and on the roof of any Car other than your
        own, regardless of the distance."
        For s3 we model the basic case (both on roof, different cars) and
        defer the Line-of-Sight nuance to a later folder if needed.

    Preconditions:
        - shooter and target both exist in state.bandits and differ (state.bandits)
        - shooter is on 'roof' (state.bandit_level)
        - target is on 'roof' (state.bandit_level)
        - shooter and target are in different cars (state.bandit_car)

    Effects:
        - target.bandit_bullets_taken += 1 (state.bandit_bullets_taken) [DATA]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(shooter, str): return False
    if not isinstance(target, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not shooter.strip(): return False
    if not target.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if shooter not in state.bandits:
        return False
    if target not in state.bandits:
        return False
    if shooter == target:
        return False
    if state.bandit_level.get(shooter) != 'roof':
        return False
    if state.bandit_level.get(target) != 'roof':
        return False
    if state.bandit_car.get(shooter) == state.bandit_car.get(target):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Target takes a bullet
    state.bandit_bullets_taken[target] = state.bandit_bullets_taken.get(target, 0) + 1

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


def a_move_demo_no_marshal_trigger(state: State, bandit: str, direction: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_move_demo_no_marshal_trigger(state, bandit, direction)

    Action parameters:
        bandit: ID of the bandit to move
        direction: 'forward' or 'backward'

    Action purpose:
        NEGATIVE-CONTROL DEMO ONLY. Byte-identical to a_move except the
        [EXPECTED_EFFECT] Marshal-trigger block is omitted. Used by
        scenario_3_expected_effects_negative_control to demonstrate that
        without the [EXPECTED_EFFECT] tag's effects, downstream actions
        whose preconditions depend on the bandit being pushed to the roof
        (e.g., a_fire) cannot succeed at planning time.

        Pattern source: trunk_thumper s07's a_nav_to_last_enemy_loc_demo_no_ee.

    Preconditions:
        Identical to a_move's preconditions.

    Effects:
        - Bandit's car updated (state.bandit_car) [DATA]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]
        - DELIBERATELY OMITS the [EXPECTED_EFFECT] block on
          state.bandit_level / state.bandit_bullets_taken

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(bandit, str): return False
    if not isinstance(direction, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not bandit.strip(): return False
    if direction not in ('forward', 'backward'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if bandit not in state.bandits:
        return False
    current_car = state.bandit_car.get(bandit)
    if current_car is None:
        return False
    current_index = state.car_index.get(current_car)
    if current_index is None:
        return False
    delta = -1 if direction == 'forward' else 1
    destination_index = current_index + delta
    if destination_index < 0 or destination_index >= len(state.cars):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Bandit moves one car. This variant DELIBERATELY OMITS the
    # [EXPECTED_EFFECT] block that the canonical a_move has — it's the
    # negative control for the [EXPECTED_EFFECT] teaching point.
    state.bandit_car[bandit] = state.cars[destination_index]

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


# ============================================================================
# METHODS (1 task name, 2 alternative methods — reused from s1)
# ============================================================================

def m_rob_loot_here(state: State, bandit: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_rob_loot_here(state, bandit)

    Method parameters:
        bandit: ID of the bandit taking the turn

    Method auxiliary parameters:
        loot_token: str (inferred via _h_pick_loot_to_rob)

    Method purpose:
        Identical to s1's m_rob_loot_here. First (priority) method of
        m_take_turn. Rob the first loot token if the bandit is on the
        interior of a car containing loot.

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit is on 'interior'
        - There is at least one loot token at the bandit's car

    Task decomposition:
        - a_robbery: Pick up the first available loot token

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(bandit, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not bandit.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if bandit not in state.bandits:
        return False
    current_car = state.bandit_car.get(bandit)
    if current_car is None:
        return False
    loot_token = _h_pick_loot_to_rob(state, current_car)
    if loot_token is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if state.bandit_level.get(bandit) != 'interior':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_robbery', bandit, loot_token),
    ]
    # END: Task Decomposition


def m_move_forward_fallback(state: State, bandit: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_move_forward_fallback(state, bandit)

    Method parameters:
        bandit: ID of the bandit taking the turn

    Method purpose:
        Identical to s1's m_move_forward_fallback. Second (fallback)
        method of m_take_turn. Move one car toward the locomotive.

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit is not at the locomotive

    Task decomposition:
        - a_move forward: Move one car toward the locomotive

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(bandit, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not bandit.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if bandit not in state.bandits:
        return False
    current_car = state.bandit_car.get(bandit)
    if current_car is None:
        return False
    if state.car_index.get(current_car, 0) == 0:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_move', bandit, 'forward'),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_move,
    a_robbery,
    a_floor_change,
    a_marshal_move,
    a_fire,
    a_move_demo_no_marshal_trigger,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Root task: m_take_turn(bandit). Same priority ordering as s1.
declare_task_methods('m_take_turn',
                     m_rob_loot_here,
                     m_move_forward_fallback)

# ============================================================================
# END OF FILE
# ============================================================================
