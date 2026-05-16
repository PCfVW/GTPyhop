# ============================================================================
# Colt Express - s4 Character Priorities (priority-method ladder)
# ============================================================================
#
# PATTERN SOURCE:
# trunk_thumper s08_priority_methods (Game AI Pro Chapter 12.8, Troy
# Humphreys, CRC Press 2015). Method ordering = priority: the planner tries
# methods in declaration order; the first applicable method wins. Methods
# that don't apply return False, causing the planner to fall through to the
# next-priority alternative.
#
# COLT EXPRESS FRAMING:
# Models 4 character abilities (Belle / Tuco / Django / Cheyenne) as
# higher-priority methods on m_resolve_fire and m_resolve_punch. The
# Belle-immunity method structurally mirrors s08's WsIsTired fix: a
# higher-priority precondition guard that prevents the generic action from
# firing in a game-rule-defined special situation.
#
# RULEBOOK QUOTES (Bandits' special abilities, p.5):
# - Belle:    "You cannot be the target of a Fire action or a Punch action
#             if there is another Bandit who can be targeted, too."
# - Tuco:     "Tuco's shots are not stopped by the roof. You can shoot a
#             Bandit who is on the same Car as you are, on the other level."
# - Django:   "Django's shots are so powerful that they knock the other
#             bandits back. When shooting a Bandit, make him move one Car
#             in the direction of fire."
# - Cheyenne: "When punching a Bandit, you can take the Purse he has just
#             lost."
#
# SIMPLIFICATION NOTE:
# Punches in the rulebook make the target lose a specific loot TOKEN (chosen
# by the puncher or the target depending on context); the lost purse falls
# on the car floor at the puncher's position. The canonical state schema
# tracks state.bandit_purse as Dict[str, int] (totals), not Dict[str,
# List[str]] (token lists), so we model punches as a flat $250 transfer.
# Cheyenne's special keeps the $250 instead of "dropping it on the floor".
# This is enough to demonstrate the priority-method pattern.
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
#   - Imports
#   - Domain (1)
#   - State Property Map
#   - Helper Functions
#   - Actions (8): a_move, a_robbery, a_floor_change (basic from s1),
#                 a_fire (from s3), a_fire_through_floor (Tuco),
#                 a_fire_with_knockback (Django), a_punch,
#                 a_punch_and_keep_purse (Cheyenne)
#   - Methods (2 task names with 6 total methods)
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

the_domain = Domain("colt_express_s4")
set_current_domain(the_domain)

# Standard punch transfer amount (simplification: real game transfers a
# specific loot token; we use $250 as a flat amount). Documented above.
_PUNCH_TRANSFER = 250


# ============================================================================
# STATE PROPERTY MAP (canonical schema; identical to s1, s3, s2)
# Uses state.bandit_character for the first time to dispatch in
# priority methods.
# ============================================================================


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _h_find_alternate_target(state: State, shooter: str, blocked_target: str) -> Optional[str]:
    """
    Find an alternative bandit who could be hit by a standard a_fire from
    the shooter, when the originally-named target (Belle) is immune.

    "Valid" means: bandit on roof of a car different from the shooter's.
    The shooter must themselves be on a roof for any alternative to apply.
    """
    if state.bandit_level.get(shooter) != 'roof':
        return None
    shooter_car = state.bandit_car.get(shooter)
    for b in state.bandits:
        if b == shooter or b == blocked_target:
            continue
        if state.bandit_level.get(b) != 'roof':
            continue
        if state.bandit_car.get(b) == shooter_car:
            continue
        return b
    return None


# ============================================================================
# ACTIONS (8)
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
        Basic move (same as s1; no Marshal awareness or deck handling).

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
        Basic roof-to-roof Fire (same as s3). Used as the default fire
        action and also as the redirected fire when Belle immunity fires
        the alternative-target redirect.

    Preconditions:
        - shooter and target are distinct bandits
        - both on 'roof' (state.bandit_level)
        - in different cars (state.bandit_car)

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


def a_fire_through_floor(state: State, shooter: str, target: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_fire_through_floor(state, shooter, target)

    Action parameters:
        shooter: ID of the bandit firing (must be 'tuco')
        target: ID of the targeted bandit

    Action purpose:
        Tuco's special Fire: shoots through the floor at a bandit on the
        same Car but the opposite level. Per the rulebook (p.5):
        "Tuco's shots are not stopped by the roof. You can shoot a Bandit
        who is on the same Car as you are, on the other level, through
        the roof of your Car."

    Preconditions:
        - shooter is 'tuco' (state.bandit_character)
        - shooter and target are distinct bandits
        - shooter and target in the SAME car (state.bandit_car)
        - shooter and target on OPPOSITE levels (state.bandit_level)

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
    if state.bandit_character.get(shooter) != 'tuco':
        return False
    if state.bandit_car.get(shooter) != state.bandit_car.get(target):
        return False
    if state.bandit_level.get(shooter) == state.bandit_level.get(target):
        return False  # same level: standard fire, not through-floor
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Target takes a bullet
    state.bandit_bullets_taken[target] = state.bandit_bullets_taken.get(target, 0) + 1

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


def a_fire_with_knockback(state: State, shooter: str, target: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_fire_with_knockback(state, shooter, target)

    Action parameters:
        shooter: ID of the bandit firing (must be 'django')
        target: ID of the targeted bandit

    Action purpose:
        Django's special Fire: roof-to-roof shot that knocks the target
        one car in the direction of fire. Per the rulebook (p.5):
        "Django's shots are so powerful that they knock the other bandits
        back. When shooting a Bandit, make him move one Car in the
        direction of fire, bearing in mind that Bandits can never leave
        the train."

    Preconditions:
        - shooter is 'django' (state.bandit_character)
        - both on 'roof', different cars (same as a_fire)

    Effects:
        - target.bandit_bullets_taken += 1 (state.bandit_bullets_taken) [DATA]
        - Target knocked one car in the direction of fire (state.bandit_car)
          [DATA]; if would move beyond the train end, target stays put
          (rulebook clause).
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
    if state.bandit_character.get(shooter) != 'django':
        return False
    if state.bandit_level.get(shooter) != 'roof':
        return False
    if state.bandit_level.get(target) != 'roof':
        return False
    shooter_car = state.bandit_car.get(shooter)
    target_car = state.bandit_car.get(target)
    if shooter_car == target_car:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Target takes a bullet
    state.bandit_bullets_taken[target] = state.bandit_bullets_taken.get(target, 0) + 1

    # [DATA] Knockback: target moves one car AWAY from shooter; rulebook
    # specifies "Bandits can never leave the train" so if the new index
    # would be out of range, target stays put.
    shooter_index = state.car_index.get(shooter_car, 0)
    target_index = state.car_index.get(target_car, 0)
    knockback_delta = 1 if target_index > shooter_index else -1
    new_index = target_index + knockback_delta
    if 0 <= new_index < len(state.cars):
        state.bandit_car[target] = state.cars[new_index]

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
        Standard Punch. Per the rulebook (p.4): "Choose a target among the
        Bandits who are on the same Car and same floor as you are. The
        targeted Bandit loses a Loot token..." For s4 we simplify to a
        flat $250 transfer that "falls on the floor" (i.e., disappears
        from the bandit's purse with no recipient).

    Preconditions:
        - puncher and target are distinct bandits
        - same car, same level (state.bandit_car, state.bandit_level)
        - target has at least $250 in purse (state.bandit_purse)

    Effects:
        - target.bandit_purse -= 250 (state.bandit_purse) [DATA]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]

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
    if state.bandit_purse.get(target, 0) < _PUNCH_TRANSFER:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Target loses the punch-transfer amount (falls "on the floor")
    state.bandit_purse[target] = state.bandit_purse[target] - _PUNCH_TRANSFER

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


def a_punch_and_keep_purse(state: State, puncher: str, target: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_punch_and_keep_purse(state, puncher, target)

    Action parameters:
        puncher: ID of the punching bandit (must be 'cheyenne')
        target: ID of the target bandit

    Action purpose:
        Cheyenne's special Punch. Per the rulebook (p.5): "When punching
        a Bandit, you can take the Purse he has just lost." We model this
        as a $250 transfer FROM target TO puncher (rather than the standard
        $250 vanishing).

    Preconditions:
        - puncher is 'cheyenne' (state.bandit_character)
        - puncher and target are distinct bandits, same car, same level
        - target has at least $250 in purse

    Effects:
        - target.bandit_purse -= 250 (state.bandit_purse) [DATA]
        - puncher.bandit_purse += 250 (state.bandit_purse) [DATA]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]

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
    if state.bandit_character.get(puncher) != 'cheyenne':
        return False
    if state.bandit_car.get(puncher) != state.bandit_car.get(target):
        return False
    if state.bandit_level.get(puncher) != state.bandit_level.get(target):
        return False
    if state.bandit_purse.get(target, 0) < _PUNCH_TRANSFER:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Target loses the punch-transfer amount
    state.bandit_purse[target] = state.bandit_purse[target] - _PUNCH_TRANSFER

    # [DATA] Cheyenne KEEPS it (the rulebook special; otherwise it falls on the floor)
    state.bandit_purse[puncher] = state.bandit_purse.get(puncher, 0) + _PUNCH_TRANSFER

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


# ============================================================================
# METHODS (2 task names, 6 alternative methods total)
# ============================================================================

def m_fire_blocked_by_belle_immunity(state: State, shooter: str, target: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_fire_blocked_by_belle_immunity(state, shooter, target)

    Method parameters:
        shooter: ID of the firing bandit
        target: ID of the originally-named target

    Method auxiliary parameters:
        alt_target: str (inferred via _h_find_alternate_target when
                    target is Belle and an alternative exists)

    Method purpose:
        First (priority) method of m_resolve_fire. Implements Belle's
        immunity: "You cannot be the target of a Fire action ... if there
        is another Bandit who can be targeted, too." If the target is
        Belle and an alternative is available, redirect the fire to the
        alternative. Otherwise return False (fall through to the next
        priority method).

        This is the structural twin of trunk_thumper s08's
        m_whirlwind_combo with the WsIsTired guard: a higher-priority
        method whose precondition prevents the generic action from
        firing in a specific game-rule-defined situation. Differences:
        Belle redirects rather than aborts; s08's m_whirlwind_combo just
        falls through.

    Preconditions:
        - target's bandit_character is 'belle' (state.bandit_character)
        - An alternative valid target exists (_h_find_alternate_target)

    Task decomposition:
        - a_fire(shooter, alt_target): redirected fire at the alternative

    Returns:
        Task decomposition if successful, False otherwise
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

    # BEGIN: Auxiliary Parameter Inference
    if state.bandit_character.get(target) != 'belle':
        return False
    alt_target = _h_find_alternate_target(state, shooter, target)
    if alt_target is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # All checks were folded into auxiliary parameter inference above
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_fire', shooter, alt_target),
    ]
    # END: Task Decomposition


def m_fire_tuco_through_floor(state: State, shooter: str, target: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_fire_tuco_through_floor(state, shooter, target)

    Method parameters:
        shooter: ID of the firing bandit
        target: ID of the target bandit

    Method purpose:
        Second-priority method. Tuco's through-floor special. Fires when
        the shooter is Tuco and the target is on the same car but the
        opposite level. Otherwise returns False to fall through.

    Preconditions:
        - shooter's bandit_character is 'tuco' (state.bandit_character)
        - shooter and target are in the same car (state.bandit_car)
        - shooter and target are on different levels (state.bandit_level)

    Task decomposition:
        - a_fire_through_floor(shooter, target)

    Returns:
        Task decomposition if successful, False otherwise
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
    if state.bandit_character.get(shooter) != 'tuco':
        return False
    if state.bandit_car.get(shooter) != state.bandit_car.get(target):
        return False
    if state.bandit_level.get(shooter) == state.bandit_level.get(target):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_fire_through_floor', shooter, target),
    ]
    # END: Task Decomposition


def m_fire_django_knockback(state: State, shooter: str, target: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_fire_django_knockback(state, shooter, target)

    Method parameters:
        shooter: ID of the firing bandit
        target: ID of the target bandit

    Method purpose:
        Third-priority method. Django's knockback special. Fires when the
        shooter is Django and the standard roof-to-roof geometry holds.

    Preconditions:
        - shooter's bandit_character is 'django' (state.bandit_character)
        - both on roof, different cars (standard fire geometry)

    Task decomposition:
        - a_fire_with_knockback(shooter, target)

    Returns:
        Task decomposition if successful, False otherwise
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
    if state.bandit_character.get(shooter) != 'django':
        return False
    if state.bandit_level.get(shooter) != 'roof':
        return False
    if state.bandit_level.get(target) != 'roof':
        return False
    if state.bandit_car.get(shooter) == state.bandit_car.get(target):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_fire_with_knockback', shooter, target),
    ]
    # END: Task Decomposition


def m_fire_standard(state: State, shooter: str, target: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_fire_standard(state, shooter, target)

    Method parameters:
        shooter: ID of the firing bandit
        target: ID of the target bandit

    Method purpose:
        Fallback method of m_resolve_fire. Standard roof-to-roof fire when
        no character special applies.

    Preconditions:
        None (fallback)

    Task decomposition:
        - a_fire(shooter, target)

    Returns:
        Task decomposition if successful, False otherwise
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
    # None - fallback
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_fire', shooter, target),
    ]
    # END: Task Decomposition


def m_punch_cheyenne_keep_purse(state: State, puncher: str, target: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_punch_cheyenne_keep_purse(state, puncher, target)

    Method parameters:
        puncher: ID of the punching bandit
        target: ID of the target bandit

    Method purpose:
        First (priority) method of m_resolve_punch. Cheyenne's special:
        keep the punched purse. Fires when the puncher is Cheyenne and
        the target has a purse to take.

    Preconditions:
        - puncher's bandit_character is 'cheyenne' (state.bandit_character)

    Task decomposition:
        - a_punch_and_keep_purse(puncher, target)

    Returns:
        Task decomposition if successful, False otherwise
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
    if state.bandit_character.get(puncher) != 'cheyenne':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_punch_and_keep_purse', puncher, target),
    ]
    # END: Task Decomposition


def m_punch_standard(state: State, puncher: str, target: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_punch_standard(state, puncher, target)

    Method parameters:
        puncher: ID of the punching bandit
        target: ID of the target bandit

    Method purpose:
        Fallback method of m_resolve_punch. Standard punch when no
        character special applies.

    Preconditions:
        None (fallback)

    Task decomposition:
        - a_punch(puncher, target)

    Returns:
        Task decomposition if successful, False otherwise
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
    # None - fallback
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_punch', puncher, target),
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
    a_fire_through_floor,
    a_fire_with_knockback,
    a_punch,
    a_punch_and_keep_purse,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# m_resolve_fire: priority order = Belle immunity, Tuco through floor,
# Django knockback, standard fallback (per the rulebook ability hierarchy).
declare_task_methods('m_resolve_fire',
                     m_fire_blocked_by_belle_immunity,
                     m_fire_tuco_through_floor,
                     m_fire_django_knockback,
                     m_fire_standard)

# m_resolve_punch: priority order = Cheyenne keep purse, standard fallback.
declare_task_methods('m_resolve_punch',
                     m_punch_cheyenne_keep_purse,
                     m_punch_standard)

# ============================================================================
# END OF FILE
# ============================================================================
