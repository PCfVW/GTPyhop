# ============================================================================
# Colt Express - s2 Recursive Round (recursive deck resolution)
# ============================================================================
#
# PATTERN SOURCE:
# trunk_thumper s06_recursive_trunk_replacement (Game AI Pro Chapter 12.6,
# Troy Humphreys, CRC Press 2015). Recursive task decomposition: a
# compound task decomposes into a sequence ending in a recursive call to
# itself; termination is achieved via state mutation in the preceding
# subtasks.
#
# COLT EXPRESS FRAMING:
# Models the resolution of the pre-encoded programmed deck during the
# Stealin' phase. state.deck is a list of (bandit, card_kind) tuples;
# m_resolve_programmed_deck recursively pops the head and dispatches to
# the appropriate action, terminating when the deck is empty.
#
# Termination story (mirrors s06's WsTrunkHealth):
# - Base-case method matches when `not state.deck`
# - Recursive method matches when deck non-empty, returns
#   [(card_action, ...), (m_resolve_programmed_deck,)]
# - Each card_action head-pops the deck as part of its effects, so the
#   recursive call sees a strictly smaller deck.
# - Eventually deck is empty -> base case fires -> recursion terminates.
#
# RULEBOOK QUOTE (Phase 2: Stealin', p.3):
# "The First Player takes the deck of Action cards that had been created
#  during the Schemin'! phase and turns the deck over, without changing the
#  order of the cards. The Bandits' Actions are performed, one by one,
#  starting with the top card (i.e., in the order they have been played)."
#
# END-OF-ROUND EVENT SCOPE (per plan):
# Only the `hostage_taking` event is modeled in s2. a_apply_event reads
# state.event_card; per the rulebook (p.5) "Each Bandit who is either in
# the Locomotive or on its roof receives $250 ransom". The other 6 event
# types are documented as out-of-scope for s2.
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
#   - Imports
#   - Domain (1)
#   - State Property Map
#   - Helper Functions
#   - Actions (4): a_move, a_robbery, a_floor_change (all deck-aware),
#                 a_apply_event (hostage_taking only)
#   - Methods (2 task names with 4 total methods)
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

the_domain = Domain("colt_express_s2")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (canonical Colt Express schema; identical to s1, s3)
# Note: state.marshal_car and state.bandit_bullets_taken initialized but
# unused in s2 scenarios. state.deck is used heavily here for the first time.
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
# ACTIONS (4)
# ============================================================================

def a_move(state: State, bandit: str, direction: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_move(state, bandit, direction)

    Action parameters:
        bandit: ID of the bandit to move
        direction: 'forward' (toward locomotive) or 'backward' (toward caboose)

    Action purpose:
        Deck-aware Move. Verifies that state.deck[0] == (bandit, 'move')
        and head-pops the deck before applying the standard move effect.
        Evolution from s1: adds deck-head check and deck-pop. Distinct
        from s3's a_move which adds [EXPECTED_EFFECT] for Marshal forced-
        escape.

    Preconditions:
        - The bandit exists in state.bandits (state.bandits)
        - direction is 'forward' or 'backward' (state-type check)
        - The destination car exists (state.car_index)
        - state.deck is non-empty and state.deck[0] == (bandit, 'move')
          (state.deck)

    Effects:
        - state.deck head-popped (state.deck) [DATA]
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
    if not state.deck:
        return False
    if state.deck[0] != (bandit, 'move'):
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
    # [DATA] Head-pop the deck; this is the recursion termination mechanism
    state.deck = state.deck[1:]

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
        Deck-aware Robbery. Verifies state.deck[0] == (bandit, 'robbery')
        and head-pops the deck before applying the standard robbery effect.

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit is on 'interior'
        - The loot_token is present in state.loot_at[bandit_car]
        - state.deck[0] == (bandit, 'robbery')

    Effects:
        - state.deck head-popped (state.deck) [DATA]
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
    if not state.deck:
        return False
    if state.deck[0] != (bandit, 'robbery'):
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
    # [DATA] Head-pop the deck
    state.deck = state.deck[1:]

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
        Deck-aware Floor Change. Verifies state.deck[0] == (bandit,
        'floor_change') and head-pops the deck.

    Preconditions:
        - The bandit exists in state.bandits
        - The bandit has a valid current level
        - state.deck[0] == (bandit, 'floor_change')

    Effects:
        - state.deck head-popped (state.deck) [DATA]
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
    if not state.deck:
        return False
    if state.deck[0] != (bandit, 'floor_change'):
        return False
    current_level = state.bandit_level.get(bandit)
    if current_level not in ('interior', 'roof'):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Head-pop the deck
    state.deck = state.deck[1:]

    # [DATA] Toggle interior <-> roof
    state.bandit_level[bandit] = 'roof' if current_level == 'interior' else 'interior'

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


def a_apply_event(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_apply_event(state)

    Action parameters:
        None

    Action purpose:
        Apply the round's end-of-round event. For s2 we model only the
        `hostage_taking` event (per the rulebook, p.5: "Each Bandit who is
        either in the Locomotive or on its roof receives $250 ransom").
        The other 6 event types are out-of-scope for s2.

    Preconditions:
        - state.event_card == 'hostage_taking' (state.event_card)
        - The 'locomotive' car exists in the train (state.cars)

    Effects:
        - For every bandit at the locomotive, purse += 250 (state.bandit_purse) [DATA]
        - state.event_card cleared to None (state.event_card) [DATA]
        - Anti-idempotence counter incremented (state.actions_resolved) [DATA]

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
    if state.event_card != 'hostage_taking':
        return False
    if 'locomotive' not in state.cars:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Hostage-Taking: each bandit at the locomotive (interior or roof)
    # receives $250 ransom
    for b in state.bandits:
        if state.bandit_car.get(b) == 'locomotive':
            state.bandit_purse[b] = state.bandit_purse.get(b, 0) + 250

    # [DATA] Event consumed
    state.event_card = None

    # [DATA] Anti-idempotence counter
    state.actions_resolved = state.actions_resolved + 1
    # END: Effects

    return state


# ============================================================================
# METHODS (2 task names, 4 total methods)
# ============================================================================

def m_resolve_deck_empty(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_resolve_deck_empty(state)

    Method parameters:
        None

    Method purpose:
        Base-case method for m_resolve_programmed_deck. Fires when the
        deck is empty and terminates the recursion with an empty
        decomposition.

    Preconditions:
        - state.deck is empty (state.deck)

    Task decomposition:
        - (empty list) - terminates the recursion

    Returns:
        Empty list if successful (deck empty), False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.deck:
        return False  # not the base case; let the recursive method fire
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_resolve_deck_recursive(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_resolve_deck_recursive(state)

    Method parameters:
        None

    Method auxiliary parameters:
        bandit, card_kind: inferred from state.deck[0]
        loot_token: for 'robbery' cards, inferred via _h_pick_loot_to_rob

    Method purpose:
        Recursive method for m_resolve_programmed_deck. Reads
        state.deck[0] = (bandit, card_kind), dispatches to the appropriate
        action, and ends with a recursive call to m_resolve_programmed_deck.
        Terminates because each action head-pops the deck.

    Preconditions:
        - state.deck is non-empty (state.deck)
        - The head card's kind is supported ('move', 'robbery', 'floor_change')

    Task decomposition:
        - card_action: dispatched on state.deck[0][1]
        - m_resolve_programmed_deck: recursive continuation

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if not state.deck:
        return False
    head = state.deck[0]
    if not isinstance(head, tuple) or len(head) != 2:
        return False
    bandit, card_kind = head
    if not isinstance(bandit, str) or not isinstance(card_kind, str):
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if card_kind not in ('move', 'robbery', 'floor_change'):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    if card_kind == 'move':
        return [
            ('a_move', bandit, 'forward'),
            ('m_resolve_programmed_deck',),
        ]
    elif card_kind == 'robbery':
        current_car = state.bandit_car.get(bandit)
        if current_car is None:
            return False
        loot_token = _h_pick_loot_to_rob(state, current_car)
        if loot_token is None:
            return False
        return [
            ('a_robbery', bandit, loot_token),
            ('m_resolve_programmed_deck',),
        ]
    else:  # card_kind == 'floor_change'
        return [
            ('a_floor_change', bandit),
            ('m_resolve_programmed_deck',),
        ]
    # END: Task Decomposition


def m_play_round_with_event(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_play_round_with_event(state)

    Method parameters:
        None

    Method purpose:
        First (priority) method of m_play_round. When state.event_card is
        set, decompose into [m_resolve_programmed_deck, a_apply_event].

    Preconditions:
        - state.event_card is not None (state.event_card)

    Task decomposition:
        - m_resolve_programmed_deck: chomp through the deck
        - a_apply_event: fire the end-of-round event

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
    if state.event_card is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('m_resolve_programmed_deck',),
        ('a_apply_event',),
    ]
    # END: Task Decomposition


def m_play_round_no_event(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_play_round_no_event(state)

    Method parameters:
        None

    Method purpose:
        Fallback method of m_play_round. When state.event_card is None,
        just resolve the deck.

    Preconditions:
        None (fallback)

    Task decomposition:
        - m_resolve_programmed_deck

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
    # None - fallback
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('m_resolve_programmed_deck',),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_move,
    a_robbery,
    a_floor_change,
    a_apply_event,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# m_resolve_programmed_deck: base case first, recursive method second.
# Per s06's example, declaration order acts as priority.
declare_task_methods('m_resolve_programmed_deck',
                     m_resolve_deck_empty,
                     m_resolve_deck_recursive)

# m_play_round: with-event method first (higher priority), no-event fallback second.
declare_task_methods('m_play_round',
                     m_play_round_with_event,
                     m_play_round_no_event)

# ============================================================================
# END OF FILE
# ============================================================================
