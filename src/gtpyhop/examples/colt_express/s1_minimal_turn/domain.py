# ============================================================================
# Colt Express - s1 Minimal Turn (priority-methods baseline)
# ============================================================================
#
# PATTERN SOURCE:
# trunk_thumper s03_basic_attack_or_patrol (Game AI Pro Chapter 12.3, Troy
# Humphreys, CRC Press 2015). Same shape: one compound task with two
# alternative methods, the first applicable wins.
#
# COLT EXPRESS FRAMING:
# Pure Stealin'-phase semantics. The bandit's turn decomposes into one of
# two actions: rob the loot here (priority, if loot is present and the
# bandit is on the interior) or move forward (fallback). This is the
# simplest priority/fallback pattern in the collection and establishes the
# canonical state schema that the other four sub-folders inherit.
#
# RULEBOOK QUOTE (Robbery action, p.4):
# "Take the Loot token of your choice from the Car where you are currently
#  located ... If your Bandit is on the roof of a Car, he cannot rob inside
#  it, and vice versa. If there is no Loot where your Bandit is, then the
#  Robbery action has no effect."
#
# Note: in this s1 baseline, the priority method ONLY fires when robbery
# would actually have an effect (loot present AND on interior). The "no
# effect" branch from the rulebook is handled by falling through to the
# move-forward fallback.
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# This file is organized into the following sections:
#   - Imports
#   - Domain (1)
#   - State Property Map
#   - Helper Functions
#   - Actions (3)
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

the_domain = Domain("colt_express_s1")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (canonical Colt Express schema)
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [DATA]    Informational/data container
#  - [CONFIG]  Set at scenario creation, not modified by actions
#
# Train geometry (CONFIG):
#  cars: list[str]                                      (P)   [CONFIG]
#  car_index: dict[str, int]                            (P)   [CONFIG]
#
# Bandits:
#  bandits: list[str]                                   (P)   [CONFIG]
#  bandit_car: dict[str, str]                           (E/P) [DATA]
#  bandit_level: dict[str, str]                         (E/P) [DATA]
#  bandit_purse: dict[str, int]                         (E)   [DATA]
#  bandit_bullets_taken: dict[str, int]                       [CONFIG] (unused in s1)
#  bandit_character: dict[str, str]                           [CONFIG] (unused in s1)
#
# Loot:
#  loot_at: dict[str, list[str]]                        (E/P) [DATA]
#
# Marshal:
#  marshal_car: Optional[str]                                 [CONFIG] (None in s1)
#
# Programmed deck (Stealin'):
#  deck: list[tuple[str, str]]                                [CONFIG] (unused in s1; s2 introduces)
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
# ACTIONS (3)
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
        Move the bandit one car in the given direction. This is the minimal
        baseline version: always exactly one car. The s5 partial-plan
        sub-folder elaborates direction and distance choice via priority
        methods, and s3 adds the Marshal forced-escape [EXPECTED_EFFECT]
        block when the destination car contains the Marshal.

    Preconditions:
        - The bandit exists in state.bandits (state.bandits)
        - direction is 'forward' or 'backward' (state-type check)
        - The destination car exists, i.e., the bandit is not at the train end
          (state.car_index)

    Effects:
        - Bandit's car updated to the adjacent car (state.bandit_car) [DATA]
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
        return False  # would walk off the end of the train
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Bandit moves one car in the requested direction
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
        loot_token: The specific loot token to pick up (e.g., 'purse_500',
                    'jewel_500', 'strongbox_1000')

    Action purpose:
        The bandit picks up a specific loot token from their current car.
        Per the rulebook, the bandit must be on the interior of the car;
        rooftop bandits cannot rob. The token's value (parsed from the
        token string after the underscore) is added to the bandit's purse.

    Preconditions:
        - The bandit exists in state.bandits (state.bandits)
        - The bandit is on 'interior' (state.bandit_level)
        - The loot_token is present in the bandit's current car (state.loot_at)

    Effects:
        - Loot token removed from car's loot list (state.loot_at) [DATA]
        - Token's value added to bandit's purse (state.bandit_purse) [DATA]
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
    if '_' not in loot_token: return False  # tokens are 'kind_value'
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
    # Token format: '<kind>_<value>' e.g. 'purse_300', 'jewel_500', 'strongbox_1000'
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
        Toggle the bandit between interior and roof of the car they're on.
        Per the rulebook: 'The interior to the roof of the Car on which
        he's standing; or from the roof of the Car he's in to its interior.'

    Preconditions:
        - The bandit exists in state.bandits (state.bandits)
        - The bandit has a valid current level: 'interior' or 'roof'
          (state.bandit_level)

    Effects:
        - Bandit's level toggled between 'interior' and 'roof'
          (state.bandit_level) [DATA]
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


# ============================================================================
# METHODS (1 task name, 2 alternative methods)
# ============================================================================

def m_rob_loot_here(state: State, bandit: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_rob_loot_here(state, bandit)

    Method parameters:
        bandit: ID of the bandit taking the turn

    Method auxiliary parameters:
        loot_token: str (inferred via _h_pick_loot_to_rob from
                    state.loot_at[state.bandit_car[bandit]])

    Method purpose:
        First (priority) method of m_take_turn. If the bandit is on the
        interior of a car containing loot, rob the first loot token. The
        chapter analog is trunk_thumper's m_attack_visible_enemy.

    Preconditions:
        - The bandit exists in state.bandits (state.bandits)
        - The bandit is on 'interior' (state.bandit_level)
        - There is at least one loot token at the bandit's car
          (state.loot_at)

    Task decomposition:
        - a_robbery: Pick up the first available loot token in the bandit's car

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
        Second (fallback) method of m_take_turn. When the priority method
        cannot fire (no loot at position, or bandit on roof), move one car
        forward toward the locomotive. s5 elaborates the direction choice
        via priority methods (flee Marshal, pursue Strongbox, etc.).

    Preconditions:
        - The bandit exists in state.bandits (state.bandits)
        - The bandit is not at the locomotive (forward move would walk off)
          (state.car_index)

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
        return False  # at locomotive, cannot move forward
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
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Root task: m_take_turn(bandit). Method ordering = priority (trunk_thumper s08).
# Rob loot at the bandit's current position first; fall back to moving
# forward if nothing to rob (or the bandit is on the roof).
declare_task_methods('m_take_turn',
                     m_rob_loot_here,
                     m_move_forward_fallback)

# ============================================================================
# END OF FILE
# ============================================================================
