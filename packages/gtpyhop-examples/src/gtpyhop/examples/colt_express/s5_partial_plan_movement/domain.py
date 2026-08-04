# ============================================================================
# Colt Express - s5 Partial-Plan Movement (method-split)
# ============================================================================
#
# PATTERN SOURCE:
# trunk_thumper s10_partial_plans (Game AI Pro Chapter 12.10, Troy
# Humphreys, CRC Press 2015). Partial planning lets the planner stop short
# of a fully-decomposed plan, leaving the rest to be filled in by a future
# re-plan. The chapter's recommended approach is the manual method-split:
# break one method's [task1, task2] subtask sequence into two separate
# methods (one per situation), each returning ONE subtask.
#
# COLT EXPRESS FRAMING:
# Models movement strategy. The "full plan" version (m_resolve_move_full_
# plan) commits to a multi-action sequence upfront (move + rob). The
# "partial plan" version (m_resolve_move_partial_plan) returns exactly
# one action via a priority-ordered ladder of state-conditioned methods.
# The same initial state, invoked with the two different task names,
# produces plans of length 2 and 1 respectively — exactly the s10
# pedagogical contrast.
#
# CHAPTER QUOTE (p.166):
# "There isn't much point to planning too far into the future since there
#  is a good chance the world state could change, forcing our troll to
#  make a different decision."
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
#   - Imports
#   - Domain (1)
#   - State Property Map
#   - Helper Functions
#   - Actions (5): all reused / basic versions (no new actions in s5)
#   - Methods (2 task names with 5 total methods)
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

the_domain = Domain("colt_express_s5")
set_current_domain(the_domain)


# ============================================================================
# STATE PROPERTY MAP (canonical schema; identical to s1, s3, s2, s4)
# Uses state.marshal_car heavily for the flee-marshal precondition.
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


def _h_marshal_is_adjacent(state: State, bandit: str) -> bool:
    """True if state.marshal_car is one car away from the bandit's car."""
    if state.marshal_car is None:
        return False
    bandit_car = state.bandit_car.get(bandit)
    if bandit_car is None:
        return False
    bandit_index = state.car_index.get(bandit_car)
    marshal_index = state.car_index.get(state.marshal_car)
    if bandit_index is None or marshal_index is None:
        return False
    return abs(bandit_index - marshal_index) == 1


def _h_flee_marshal_direction(state: State, bandit: str) -> Optional[str]:
    """Direction to move AWAY from the Marshal; None if not flee-applicable."""
    if state.marshal_car is None:
        return None
    bandit_car = state.bandit_car.get(bandit)
    if bandit_car is None:
        return None
    bandit_index = state.car_index.get(bandit_car)
    marshal_index = state.car_index.get(state.marshal_car)
    if bandit_index is None or marshal_index is None:
        return None
    if marshal_index < bandit_index:
        # Marshal is forward, flee backward
        new_index = bandit_index + 1
    else:
        # Marshal is backward, flee forward
        new_index = bandit_index - 1
    if 0 <= new_index < len(state.cars):
        return 'backward' if marshal_index < bandit_index else 'forward'
    return None  # would walk off the train


def _h_richest_car_direction(state: State, bandit: str) -> Optional[str]:
    """
    Direction to move toward the car with the highest total purse value
    (excluding the bandit's current car). Returns None if no other car
    has any loot.
    """
    bandit_car = state.bandit_car.get(bandit)
    if bandit_car is None:
        return None
    bandit_index = state.car_index.get(bandit_car)
    if bandit_index is None:
        return None
    richest_value = 0
    richest_index = None
    for car_name, idx in state.car_index.items():
        if idx == bandit_index:
            continue
        loot = state.loot_at.get(car_name, [])
        purse_total = sum(int(t.rsplit('_', 1)[1]) for t in loot if t.startswith('purse_'))
        if purse_total > richest_value:
            richest_value = purse_total
            richest_index = idx
    if richest_index is None:
        return None
    if richest_index < bandit_index:
        return 'forward'
    elif richest_index > bandit_index:
        return 'backward'
    return None


# ============================================================================
# ACTIONS (5)
# ============================================================================

def a_move(state: State, bandit: str, direction: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_move(state, bandit, direction)

    Action parameters:
        bandit: ID of the bandit to move
        direction: 'forward' or 'backward'

    Action purpose:
        Basic move (same as s1).

    Preconditions:
        - The bandit exists in state.bandits
        - direction is 'forward' or 'backward'
        - The destination car exists

    Effects:
        - Bandit's car updated (state.bandit_car) [DATA]
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
    # [DATA] Bandit moves one car
    state.bandit_car[bandit] = state.cars[destination_index]

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
        loot_token: The specific loot token to pick up

    Action purpose:
        Basic robbery (same as s1).

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit is on 'interior'
        - The loot_token is in state.loot_at[bandit_car]

    Effects:
        - Loot token removed from car (state.loot_at) [DATA]
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
        Basic floor change (same as s1).

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit has a valid current level

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
        Basic roof-to-roof Fire (same as s3). Included for canonical
        completeness; not exercised by s5 scenarios.

    Preconditions:
        - shooter and target distinct bandits
        - both on 'roof', different cars

    Effects:
        - target.bandit_bullets_taken += 1 [DATA]
        - Anti-idempotence counter incremented [DATA]
        - Anti-idempotence counter (state.actions_resolved) [DATA]

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


def a_punch(state: State, puncher: str, target: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_punch(state, puncher, target)

    Action parameters:
        puncher: ID of the punching bandit
        target: ID of the target bandit

    Action purpose:
        Basic punch (same simplification as s4). Included for canonical
        completeness; not exercised by s5 scenarios.

    Preconditions:
        - distinct bandits, same car, same level
        - target has at least $250 in purse

    Effects:
        - target.bandit_purse -= 250 [DATA]
        - Anti-idempotence counter incremented [DATA]
        - Anti-idempotence counter (state.actions_resolved) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(puncher, str): return False
    if not isinstance(target, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not puncher.strip(): return False
    if not target.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if puncher not in state.bandits:
        return False
    if target not in state.bandits:
        return False
    if puncher == target:
        return False
    if state.bandit_car.get(puncher) != state.bandit_car.get(target):
        return False
    if state.bandit_level.get(puncher) != state.bandit_level.get(target):
        return False
    if state.bandit_purse.get(target, 0) < 250:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Target loses $250 (falls on the floor)
    state.bandit_purse[target] = state.bandit_purse[target] - 250

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


# ============================================================================
# METHODS (2 task names, 5 total methods)
# ============================================================================

def m_resolve_move_full_plan(state: State, bandit: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_resolve_move_full_plan(state, bandit)

    Method parameters:
        bandit: ID of the bandit taking the turn

    Method auxiliary parameters:
        destination_car: inferred from state.cars[state.car_index[bandit_car] - 1]
        loot_token: inferred via _h_pick_loot_to_rob at destination

    Method purpose:
        Full-plan version: commits to move-forward then rob-at-destination
        in one decomposition. This represents the "pre-split" version of
        the method that s10 critiques as inefficient when state may
        change between subtasks.

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit can move forward (destination car exists)
        - The destination car has a loot token to rob

    Task decomposition:
        - a_move forward: move to next car
        - a_robbery: pick up the first loot token at the new car

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
    current_index = state.car_index.get(current_car)
    if current_index is None or current_index == 0:
        return False  # cannot move forward from locomotive
    destination_car = state.cars[current_index - 1]
    loot_token = _h_pick_loot_to_rob(state, destination_car)
    if loot_token is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No further checks
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_move', bandit, 'forward'),
        ('a_robbery', bandit, loot_token),
    ]
    # END: Task Decomposition


def m_flee_marshal(state: State, bandit: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_flee_marshal(state, bandit)

    Method parameters:
        bandit: ID of the bandit

    Method auxiliary parameters:
        flee_direction: inferred via _h_flee_marshal_direction

    Method purpose:
        First (priority) method of m_resolve_move_partial_plan. Fires
        when the Marshal is in an adjacent car. Moves the bandit AWAY
        from the Marshal in the available direction.

    Preconditions:
        - The bandit exists in state.bandits
        - state.marshal_car is set and adjacent (state.marshal_car)
        - There is a valid flee direction (not blocked by train end)

    Task decomposition:
        - a_move(bandit, flee_direction): one move away from Marshal

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
    if not _h_marshal_is_adjacent(state, bandit):
        return False
    flee_direction = _h_flee_marshal_direction(state, bandit)
    if flee_direction is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # All checks folded into auxiliary parameter inference
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_move', bandit, flee_direction),
    ]
    # END: Task Decomposition


def m_pursue_strongbox(state: State, bandit: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_pursue_strongbox(state, bandit)

    Method parameters:
        bandit: ID of the bandit

    Method purpose:
        Second-priority method. Fires when there is a strongbox in the
        Locomotive AND the Marshal is not adjacent. Moves the bandit
        forward toward the Locomotive.

    Preconditions:
        - The bandit exists in state.bandits
        - Any 'strongbox_' token exists in state.loot_at['locomotive']
        - The Marshal is NOT adjacent (else flee takes priority)
        - The bandit is not at the locomotive (can still move forward)

    Task decomposition:
        - a_move(bandit, 'forward'): one move toward the locomotive

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
    if _h_marshal_is_adjacent(state, bandit):
        return False  # flee takes priority
    loco_loot = state.loot_at.get('locomotive', [])
    if not any(t.startswith('strongbox_') for t in loco_loot):
        return False
    current_car = state.bandit_car.get(bandit)
    if current_car is None:
        return False
    if state.car_index.get(current_car, 0) == 0:
        return False  # already at locomotive
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_move', bandit, 'forward'),
    ]
    # END: Task Decomposition


def m_chase_richest_car(state: State, bandit: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_chase_richest_car(state, bandit)

    Method parameters:
        bandit: ID of the bandit

    Method auxiliary parameters:
        chase_direction: inferred via _h_richest_car_direction

    Method purpose:
        Third-priority method. Fires when there is at least one purse
        elsewhere in the train (not at the bandit's current car).
        Moves the bandit toward the richest car.

    Preconditions:
        - The bandit exists in state.bandits
        - The Marshal is NOT adjacent
        - There is no strongbox-pursuit applicable (no strongbox in
          locomotive, or bandit already there)
        - There is a richest other car (via _h_richest_car_direction)

    Task decomposition:
        - a_move(bandit, chase_direction): one move toward the richest car

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
    chase_direction = _h_richest_car_direction(state, bandit)
    if chase_direction is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if _h_marshal_is_adjacent(state, bandit):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_move', bandit, chase_direction),
    ]
    # END: Task Decomposition


def m_move_default(state: State, bandit: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_move_default(state, bandit)

    Method parameters:
        bandit: ID of the bandit

    Method purpose:
        Fallback method of m_resolve_move_partial_plan. Fires when none
        of the higher-priority methods apply. Moves the bandit one car
        forward (or returns False if at the locomotive).

    Preconditions:
        - The bandit exists in state.bandits
        - Forward movement is possible

    Task decomposition:
        - a_move(bandit, 'forward')

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
        return False  # already at locomotive
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
    a_fire,
    a_punch,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# m_resolve_move_full_plan: single method (the pre-split, committed version).
declare_task_methods('m_resolve_move_full_plan',
                     m_resolve_move_full_plan)

# m_resolve_move_partial_plan: priority order = flee marshal, pursue
# strongbox, chase richest car, default move. The s10 method-split pattern.
declare_task_methods('m_resolve_move_partial_plan',
                     m_flee_marshal,
                     m_pursue_strongbox,
                     m_chase_richest_car,
                     m_move_default)

# ============================================================================
# END OF FILE
# ============================================================================
