# ============================================================================
# Android: Netrunner Run Planning HTN Domain
# Based on the Fantasy Flight Games Android: Netrunner core set rules (2012)
# ============================================================================
#
# MOTIVATION:
# Models a single Runner-side run against a configured Corporation server stack,
# using the published mechanics of Android: Netrunner. The Runner is the
# planning agent; the Corp is configured environmental state (ice list,
# rez policy, ambush firing decisions, trace budget). The flagship scenario
# replicates the worked example on page 19 of the core rulebook.
#
# ARCHITECTURE:
# The top-level task m_steal_agenda decomposes into m_run_on_server, which in
# turn decomposes into initiation -> traversal of the ice stack -> access.
# The traversal recursively approaches each piece of ice, decides (per Corp
# policy) whether to encounter it, and resolves the encounter via icebreaker
# selection (with alternatives that drive HTN backtracking).
#
# CARD SUBSET (14 cards from the core set):
#   Corp ice (4): Ice Wall, Wall of Thorns, Enigma, Data Raven
#   Corp non-ice (4): AstroScript, Nisei MK II, Aggressive Secretary,
#                     Akitaro Watanabe (and Jinteki Personal Evolution id)
#   Runner icebreakers (4): Corroder, Gordian Blade, Wyrm, Crypsis
#   Runner hardware/resources (2): The Toolbox, Sacrificial Construct
#
# MODELING SIMPLIFICATIONS:
# - Random damage modeled as grip-count decrement (not specific card identity)
# - Corp policy (rez plan, ambush firing, trace budget) is per-scenario config
# - Scope A only: single run, no multi-turn play
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - State Property Map
#   - Card Data Tables
#   - Helper Functions
#   - Actions (24)
#   - Methods (17 task names; some with multiple alternative methods)
#   - Registration
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple, Dict, Set

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    # Graceful degradation: supports direct domain.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods

# ============================================================================
# DOMAIN
# ============================================================================

the_domain = Domain("android_netrunner")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (Android: Netrunner Run Planning)
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#  - [CONFIG]  Set at scenario creation, not modified by actions
#
# Persistent Runner state:
#  runner_credits: int                                  (E/P) [DATA]
#  runner_clicks: int                                   (E/P) [DATA]
#  grip_count: int                                      (E/P) [DATA]
#  heap_count: int                                      (E/P) [DATA]
#  mu_available: int                                    (E/P) [DATA]
#  tags: int                                            (E/P) [DATA]
#  brain_damage: int                                    (E/P) [DATA]
#  installed_programs: dict {name: True}                (E/P) [ENABLER]
#  installed_hardware: dict {name: True}                (E/P) [ENABLER]
#  installed_resources: dict {name: True}               (E/P) [ENABLER]
#  toolbox_recurring: int                               (E/P) [DATA]
#  virus_counters: dict {card_name: int}                (E/P) [DATA]
#  agenda_points_runner: int                            (E)   [DATA]
#  flatlined: bool                                      (E)   [ENABLER]
#
# Corp configuration:
#  corp_identity: str                                   (P)   [CONFIG]
#  corp_credits: int                                    (E/P) [DATA]
#  servers: dict {server_id: {'ice':list, 'contents':list, 'upgrades':list}}  (P) [CONFIG]
#  ice_rezzed: dict {(server, idx): bool}               (E/P) [ENABLER]
#  ice_advancement: dict {(server, idx): int}           (P)   [CONFIG]
#  upgrade_rezzed: dict {(server, idx): bool}           (E/P) [ENABLER]
#  agenda_advancement: dict {(server, idx): int}        (P)   [CONFIG]
#  corp_policy: dict                                    (P)   [CONFIG]
#    .rez_plan: dict {(server, idx, kind): bool}    "Will Corp rez this card on approach?"
#                                                   kind in {'ice', 'upgrade'}
#    .ambush_fire: dict {asset_name: bool}          "Will Corp pay to fire ambush?"
#    .trace_budget: dict {ice_name: int}            "Credits Corp will spend on trace"
#
# Run-scoped (cleared at end of run):
#  current_run: dict / None                             (E/P) [ENABLER]
#    .server: str
#    .approach_idx: int            # index of ice currently being approached
#    .gordian_pumps: int           # +1 str per pump, persists this run
#    .bad_pub_credits: int
#    .run_ended: bool              # set True by a_resolve_end_run
#
# Encounter-scoped (cleared at end of encounter):
#  current_encounter: dict / None                       (E/P) [ENABLER]
#    .ice_id: tuple (server, idx)
#    .breaker_pumps: dict {breaker_name: int}      # encounter-scoped pumps
#    .ice_strength_drain: int                      # Wyrm's -1 str applications
#    .subroutines_broken: set                      # indices of broken subs
#    .crypsis_used: bool                           # for end-of-encounter cleanup
#
# Scenario goal:
#  scenario_target_agenda: tuple (server, content_idx)  (P)   [CONFIG]
#  scenario_target_points: int                          (P)   [CONFIG]
# ============================================================================


# ============================================================================
# CARD DATA TABLES
# Static stats for each card in our 14-card subset, plus Jinteki PE identity.
# ============================================================================

# Ice cards: subtype, strength, rez cost, ordered list of subroutines, optional encounter ability
ICE_DATA: Dict[str, Dict] = {
    'ice_wall': {
        'subtype': 'barrier',
        'base_strength': 1,
        'rez_cost': 1,
        'subroutines': [{'kind': 'end_run'}],
        'advanceable': True,  # +1 strength per advancement token
    },
    'wall_of_thorns': {
        'subtype': 'barrier',  # also AP, but we just track 'barrier' for matching
        'base_strength': 5,
        'rez_cost': 8,
        'subroutines': [
            {'kind': 'net_damage', 'amount': 2},
            {'kind': 'end_run'},
        ],
        'advanceable': False,
    },
    'enigma': {
        'subtype': 'code_gate',
        'base_strength': 2,
        'rez_cost': 3,
        'subroutines': [
            {'kind': 'lose_click'},
            {'kind': 'end_run'},
        ],
        'advanceable': False,
    },
    'data_raven': {
        'subtype': 'sentry',
        'base_strength': 4,
        'rez_cost': 4,
        'subroutines': [
            {'kind': 'trace', 'base_strength': 3},
        ],
        'advanceable': False,
        'on_encounter': 'tag_or_end_run',  # Runner chooses to take a tag or end the run
    },
}

# Agenda cards: advancement requirement, agenda points
AGENDA_DATA: Dict[str, Dict] = {
    'astroscript': {'advancement_req': 3, 'points': 2},
    'nisei_mk_ii': {'advancement_req': 4, 'points': 2},
}

# Asset / upgrade cards: trash cost, plus card-specific effects
ASSET_DATA: Dict[str, Dict] = {
    'aggressive_secretary': {
        'trash_cost': 0,
        'rez_cost': 0,
        'ambush': True,  # If Corp pays 2c on access, trash N programs (N = advancement)
        'ambush_cost': 2,
    },
}

UPGRADE_DATA: Dict[str, Dict] = {
    'akitaro_watanabe': {
        'trash_cost': 3,
        'rez_cost': 1,
        'effect': 'reduce_ice_rez_on_server',  # -2 to rez cost of ice on this server
        'effect_amount': 2,
    },
}

# Icebreaker cards: subtype affinity, strength, install cost, costs
ICEBREAKER_DATA: Dict[str, Dict] = {
    'corroder': {
        'subtype_affinity': 'barrier',
        'base_strength': 2,
        'install_cost': 2,
        'mu_cost': 1,
        'break_cost': 1,         # cost per subroutine break
        'pump_cost': 1,          # cost per +1 strength (encounter scope)
        'pump_scope': 'encounter',
        'break_predicate': 'always',
    },
    'gordian_blade': {
        'subtype_affinity': 'code_gate',
        'base_strength': 2,
        'install_cost': 4,
        'mu_cost': 1,
        'break_cost': 1,
        'pump_cost': 1,
        'pump_scope': 'run',      # +1 strength for rest of run
        'break_predicate': 'always',
    },
    'wyrm': {
        'subtype_affinity': 'AI',  # AI breakers work on any subtype
        'base_strength': 1,
        'install_cost': 1,
        'mu_cost': 1,
        'break_cost': 3,
        'pump_cost': 1,
        'pump_scope': 'encounter',
        'break_predicate': 'ice_strength_le_zero',  # only breaks if ice strength <= 0
        'drain_cost': 1,           # cost per -1 ice strength (encounter scope)
    },
    'crypsis': {
        'subtype_affinity': 'AI',
        'base_strength': 0,
        'install_cost': 5,
        'mu_cost': 1,
        'break_cost': 1,
        'pump_cost': 1,
        'pump_scope': 'encounter',
        'break_predicate': 'always',
        'encounter_end_clause': 'spend_counter_or_trash',  # virus counter mechanic
    },
}

# Hardware cards
HARDWARE_DATA: Dict[str, Dict] = {
    'the_toolbox': {
        'install_cost': 9,
        'subtype': 'console',
        'mu_bonus': 2,
        'link_bonus': 1,
        'recurring_credits': 2,
        'recurring_scope': 'icebreakers_only',
    },
}

# Resource cards
RESOURCE_DATA: Dict[str, Dict] = {
    'sacrificial_construct': {
        'install_cost': 0,
        'subtype': 'remote',
        'effect': 'prevent_program_or_hardware_trash',
    },
}

# Corp identity cards
IDENTITY_DATA: Dict[str, Dict] = {
    'jinteki_personal_evolution': {
        'faction': 'jinteki',
        'on_agenda_scored_or_stolen': {'kind': 'net_damage', 'amount': 1},
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _h_get_ice_data(state: State, ice_id: Tuple[str, int]) -> Optional[Dict]:
    """Look up the static card data for the ice at the given (server, idx)."""
    server, idx = ice_id
    if server not in state.servers:
        return None
    ice_list = state.servers[server].get('ice', [])
    if idx < 0 or idx >= len(ice_list):
        return None
    ice_name = ice_list[idx]
    return ICE_DATA.get(ice_name)


def _h_get_ice_name(state: State, ice_id: Tuple[str, int]) -> Optional[str]:
    """Look up the name of the ice at the given (server, idx)."""
    server, idx = ice_id
    if server not in state.servers:
        return None
    ice_list = state.servers[server].get('ice', [])
    if idx < 0 or idx >= len(ice_list):
        return None
    return ice_list[idx]


def _h_current_ice_strength(state: State, ice_id: Tuple[str, int]) -> int:
    """Compute the current effective strength of an ice (base + advancement - drain)."""
    ice_data = _h_get_ice_data(state, ice_id)
    if ice_data is None:
        return 0
    base = ice_data['base_strength']
    advance = state.ice_advancement.get(ice_id, 0) if ice_data.get('advanceable') else 0
    drain = 0
    if state.current_encounter is not None and state.current_encounter.get('ice_id') == ice_id:
        drain = state.current_encounter.get('ice_strength_drain', 0)
    return base + advance - drain


def _h_current_breaker_strength(state: State, breaker_name: str) -> int:
    """Compute the current effective strength of an installed icebreaker."""
    breaker_data = ICEBREAKER_DATA.get(breaker_name)
    if breaker_data is None:
        return 0
    if breaker_name not in state.installed_programs:
        return 0
    base = breaker_data['base_strength']
    enc_pump = 0
    if state.current_encounter is not None:
        enc_pump = state.current_encounter.get('breaker_pumps', {}).get(breaker_name, 0)
    run_pump = 0
    if breaker_data.get('pump_scope') == 'run' and state.current_run is not None:
        if breaker_name == 'gordian_blade':
            run_pump = state.current_run.get('gordian_pumps', 0)
    return base + enc_pump + run_pump


def _h_subtype_matches(breaker_name: str, ice_name: str) -> bool:
    """Check whether the icebreaker's subtype affinity matches the ice subtype."""
    breaker = ICEBREAKER_DATA.get(breaker_name)
    ice = ICE_DATA.get(ice_name)
    if breaker is None or ice is None:
        return False
    affinity = breaker['subtype_affinity']
    if affinity == 'AI':
        return True
    return affinity == ice['subtype']


def _h_pay_icebreaker_cost(state: State, cost: int) -> bool:
    """
    Pay a cost related to icebreakers, draining Toolbox recurring credits first,
    then the general credit pool. Returns True on success, False if insufficient.
    """
    if cost < 0:
        return False
    available = state.toolbox_recurring + state.runner_credits
    if state.current_run is not None:
        available += state.current_run.get('bad_pub_credits', 0)
    if available < cost:
        return False
    remaining = cost
    # Drain Toolbox first
    if state.toolbox_recurring > 0:
        use = min(state.toolbox_recurring, remaining)
        state.toolbox_recurring -= use
        remaining -= use
    # Drain bad-pub credits next
    if remaining > 0 and state.current_run is not None:
        bp = state.current_run.get('bad_pub_credits', 0)
        if bp > 0:
            use = min(bp, remaining)
            state.current_run['bad_pub_credits'] = bp - use
            remaining -= use
    # Drain general pool
    if remaining > 0:
        state.runner_credits -= remaining
    return True


def _h_pay_generic_cost(state: State, cost: int) -> bool:
    """
    Pay a generic (non-icebreaker) cost. Drains bad-pub credits first, then
    general pool. Toolbox recurring CANNOT be used for non-icebreaker costs.
    """
    if cost < 0:
        return False
    available = state.runner_credits
    if state.current_run is not None:
        available += state.current_run.get('bad_pub_credits', 0)
    if available < cost:
        return False
    remaining = cost
    if state.current_run is not None:
        bp = state.current_run.get('bad_pub_credits', 0)
        if bp > 0:
            use = min(bp, remaining)
            state.current_run['bad_pub_credits'] = bp - use
            remaining -= use
    if remaining > 0:
        state.runner_credits -= remaining
    return True


def _h_breaker_can_interact(state: State, breaker_name: str, ice_id: Tuple[str, int]) -> bool:
    """Check the strength prerequisite: breaker strength >= ice strength."""
    return _h_current_breaker_strength(state, breaker_name) >= _h_current_ice_strength(state, ice_id)


def _h_breaker_can_break(state: State, breaker_name: str, ice_id: Tuple[str, int]) -> bool:
    """
    Check whether the breaker is allowed to break a subroutine on this ice,
    considering subtype affinity, strength prerequisite, and break predicate.
    """
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    breaker_data = ICEBREAKER_DATA.get(breaker_name)
    if breaker_data is None or breaker_name not in state.installed_programs:
        return False
    if not _h_subtype_matches(breaker_name, ice_name):
        return False
    if not _h_breaker_can_interact(state, breaker_name, ice_id):
        return False
    pred = breaker_data.get('break_predicate', 'always')
    if pred == 'always':
        return True
    if pred == 'ice_strength_le_zero':
        return _h_current_ice_strength(state, ice_id) <= 0
    return False


def _h_akitaro_discount(state: State, server: str) -> int:
    """Return the rez cost reduction for ice on a server, given Akitaro Watanabe."""
    upgrades = state.servers.get(server, {}).get('upgrades', [])
    for idx, upgrade in enumerate(upgrades):
        if upgrade == 'akitaro_watanabe' and state.upgrade_rezzed.get((server, idx), False):
            return UPGRADE_DATA['akitaro_watanabe']['effect_amount']
    return 0


def _h_rezzed_corp_ambush(state: State) -> Optional[str]:
    """If an ambush should fire on the just-accessed card, return its name."""
    # Stub used in access methods; full ambush handling is in m_handle_ambush
    return None


def _h_target_agenda_stolen(state: State) -> bool:
    """Check if the scenario's target agenda points threshold has been reached."""
    if not hasattr(state, 'scenario_target_points'):
        return False
    return state.agenda_points_runner >= state.scenario_target_points


# ============================================================================
# ACTIONS (24)
# ============================================================================

# ----------------------------------------------------------------------------
# Setup Actions (3)
# ----------------------------------------------------------------------------

def a_install_program(state: State, card_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_install_program(state, card_name)

    Action parameters:
        card_name: Internal name of the program card (e.g., 'corroder')

    Action purpose:
        Install a program from the grip into the rig, paying its install cost
        and consuming a click. Checks MU availability.

    Preconditions:
        - Card is a known program (ICEBREAKER_DATA)
        - Runner has at least 1 click (state.runner_clicks >= 1)
        - Runner has sufficient credits (state.runner_credits)
        - Sufficient MU available (state.mu_available)
        - Program not already installed (state.installed_programs)

    Effects:
        - Click consumed (state.runner_clicks) [DATA]
        - Credits paid (state.runner_credits) [DATA]
        - MU consumed (state.mu_available) [DATA]
        - Program installed (state.installed_programs) [ENABLER]
        - Virus counter init for virus programs (state.virus_counters) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(card_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if card_name not in ICEBREAKER_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.runner_clicks < 1:
        return False
    if state.current_run is not None:
        return False  # Can't install during a run
    breaker_data = ICEBREAKER_DATA[card_name]
    cost = breaker_data['install_cost']
    if state.runner_credits < cost:
        return False
    if state.mu_available < breaker_data['mu_cost']:
        return False
    if card_name in state.installed_programs:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Click consumed
    state.runner_clicks -= 1
    # [DATA] Credits paid
    state.runner_credits -= cost
    # [DATA] MU consumed
    state.mu_available -= breaker_data['mu_cost']
    # [ENABLER] Program installed
    state.installed_programs[card_name] = True
    # [DATA] Initialize virus counter for virus programs
    if breaker_data.get('encounter_end_clause') == 'spend_counter_or_trash':
        if card_name not in state.virus_counters:
            state.virus_counters[card_name] = 0
    # END: Effects

    return state


def a_install_hardware(state: State, card_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_install_hardware(state, card_name)

    Action parameters:
        card_name: Internal name of the hardware card (e.g., 'the_toolbox')

    Action purpose:
        Install a hardware card, paying its install cost and consuming a click.
        Applies any MU bonus, link bonus, and recurring-credit refill.

    Preconditions:
        - Card is a known hardware (HARDWARE_DATA)
        - Runner has at least 1 click (state.runner_clicks >= 1)
        - Runner has sufficient credits (state.runner_credits)
        - Card not already installed (state.installed_hardware)
        - For console subtype: no other console already installed

    Effects:
        - Click consumed (state.runner_clicks) [DATA]
        - Credits paid (state.runner_credits) [DATA]
        - Hardware installed (state.installed_hardware) [ENABLER]
        - MU available increased by mu_bonus (state.mu_available) [DATA]
        - Toolbox recurring initialized (state.toolbox_recurring) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(card_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if card_name not in HARDWARE_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.runner_clicks < 1:
        return False
    if state.current_run is not None:
        return False
    hw_data = HARDWARE_DATA[card_name]
    cost = hw_data['install_cost']
    if state.runner_credits < cost:
        return False
    if card_name in state.installed_hardware:
        return False
    # Console limit
    if hw_data.get('subtype') == 'console':
        for name in state.installed_hardware:
            if HARDWARE_DATA.get(name, {}).get('subtype') == 'console':
                return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Click consumed
    state.runner_clicks -= 1
    # [DATA] Credits paid
    state.runner_credits -= cost
    # [ENABLER] Hardware installed
    state.installed_hardware[card_name] = True
    # [DATA] MU bonus
    state.mu_available += hw_data.get('mu_bonus', 0)
    # [DATA] Recurring credits (Toolbox provides 2 to icebreakers)
    if card_name == 'the_toolbox':
        state.toolbox_recurring = hw_data.get('recurring_credits', 0)
    # END: Effects

    return state


def a_install_resource(state: State, card_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_install_resource(state, card_name)

    Action parameters:
        card_name: Internal name of the resource card (e.g., 'sacrificial_construct')

    Action purpose:
        Install a resource card, paying its install cost and consuming a click.

    Preconditions:
        - Card is a known resource (RESOURCE_DATA)
        - Runner has at least 1 click (state.runner_clicks >= 1)
        - Runner has sufficient credits (state.runner_credits)
        - Card not already installed (state.installed_resources)

    Effects:
        - Click consumed (state.runner_clicks) [DATA]
        - Credits paid (state.runner_credits) [DATA]
        - Resource installed (state.installed_resources) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(card_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if card_name not in RESOURCE_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.runner_clicks < 1:
        return False
    if state.current_run is not None:
        return False
    res_data = RESOURCE_DATA[card_name]
    cost = res_data['install_cost']
    if state.runner_credits < cost:
        return False
    if card_name in state.installed_resources:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Click consumed
    state.runner_clicks -= 1
    # [DATA] Credits paid
    state.runner_credits -= cost
    # [ENABLER] Resource installed
    state.installed_resources[card_name] = True
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# Run Flow Actions (4)
# ----------------------------------------------------------------------------

def a_initiate_run(state: State, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_initiate_run(state, server)

    Action parameters:
        server: Identifier of the server to run on (e.g., 'remote_1')

    Action purpose:
        Initiate a run against the named server, paying a click and creating
        the current_run state record.

    Preconditions:
        - Runner has at least 1 click (state.runner_clicks)
        - Not already running (state.current_run is None)
        - Target server exists (state.servers)

    Effects:
        - Click consumed (state.runner_clicks) [DATA]
        - Run state created with approach_idx = -1 (state.current_run) [ENABLER]
        - Bad publicity credits granted (state.current_run.bad_pub_credits) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.runner_clicks < 1:
        return False
    if state.current_run is not None:
        return False
    if server not in state.servers:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Click consumed
    state.runner_clicks -= 1
    # [ENABLER] Run state created
    state.current_run = {
        'server': server,
        'approach_idx': -1,            # incremented to 0 by first a_approach_ice
        'gordian_pumps': 0,
        'bad_pub_credits': 0,          # bad publicity not modeled in subset; left for hook
        'run_ended': False,
    }
    # END: Effects

    return state


def a_approach_ice(state: State, idx: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_approach_ice(state, idx)

    Action parameters:
        idx: Index of the ice being approached (0 = outermost)

    Action purpose:
        Approach the ice at position idx on the current run's server. If Corp
        policy directs to rez this ice (and Corp can afford it, with any
        Akitaro discount), pay the rez cost and mark it rezzed. Then begin
        the encounter if the ice is rezzed.

    Preconditions:
        - Run in progress (state.current_run)
        - approach_idx is consistent (current_run.approach_idx == idx - 1)
        - idx is a valid ice index for the server

    Effects:
        - approach_idx advanced (state.current_run.approach_idx) [DATA]
        - Corp may rez this ice and pay rez cost (state.ice_rezzed, state.corp_credits) [ENABLER]
        - May rez server upgrades (e.g., Akitaro) if Corp policy directs
        - If approached ice is rezzed at end, encounter begins (state.current_encounter) [ENABLER]
        - Upgrade rezzed (state.upgrade_rezzed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(idx, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if idx < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return False
    if state.current_encounter is not None:
        return False
    if state.current_run['approach_idx'] != idx - 1:
        return False
    server = state.current_run['server']
    if server not in state.servers:
        return False
    ice_list = state.servers[server].get('ice', [])
    if idx >= len(ice_list):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Advance approach pointer
    state.current_run['approach_idx'] = idx
    # [ENABLER] Corp rez window: per-approach upgrade rez decisions first (e.g., Akitaro
    #           before the discounted ice), then the approached ice itself.
    upgrades = state.servers[server].get('upgrades', [])
    for u_idx, upgrade in enumerate(upgrades):
        if state.upgrade_rezzed.get((server, u_idx), False):
            continue
        # Key includes approach context: (server, approach_idx, 'upgrade', upgrade_idx)
        if state.corp_policy.get('rez_plan', {}).get((server, idx, 'upgrade', u_idx), False):
            u_cost = UPGRADE_DATA.get(upgrade, {}).get('rez_cost', 0)
            if state.corp_credits >= u_cost:
                state.corp_credits -= u_cost
                state.upgrade_rezzed[(server, u_idx)] = True
    # [ENABLER] Then consider rezzing the approached ice
    if not state.ice_rezzed.get((server, idx), False):
        # Ice key: (server, ice_idx, 'ice'); approach_idx == ice_idx by definition
        if state.corp_policy.get('rez_plan', {}).get((server, idx, 'ice'), False):
            ice_name = ice_list[idx]
            rez_cost = ICE_DATA.get(ice_name, {}).get('rez_cost', 0)
            discount = _h_akitaro_discount(state, server)
            effective = max(0, rez_cost - discount)
            if state.corp_credits >= effective:
                state.corp_credits -= effective
                state.ice_rezzed[(server, idx)] = True
    # [ENABLER] If ice is rezzed, begin an encounter
    if state.ice_rezzed.get((server, idx), False):
        state.current_encounter = {
            'ice_id': (server, idx),
            'breaker_pumps': {},
            'ice_strength_drain': 0,
            'subroutines_broken': set(),
            'crypsis_used': False,
        }
    # END: Effects

    return state


def a_pass_ice(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_pass_ice(state)

    Action parameters:
        None

    Action purpose:
        Pass the currently-approached ice when it is not rezzed (the Corp
        declined to rez it). This concludes the approach without an encounter.

    Preconditions:
        - Run in progress (state.current_run)
        - Approached ice is not rezzed
        - No encounter in progress (state.current_encounter is None)

    Effects:
        - No state change; this is a marker action confirming the pass.

    Idempotency:
        This action returns state unchanged, so GTPyhop classifies it as
        idempotent and elides it from the returned plan even when the planner
        processes it. The 'approach pointer' was already advanced by the
        preceding a_approach_ice. To see this action in the trace, run with
        verbose=3.

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
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return False
    if state.current_encounter is not None:
        return False
    server = state.current_run['server']
    idx = state.current_run['approach_idx']
    if state.ice_rezzed.get((server, idx), False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # No state change needed; the approach pointer is already advanced.
    # END: Effects

    return state


def a_end_run(state: State, successful: bool) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_end_run(state, successful)

    Action parameters:
        successful: Whether the run reached and concluded the access phase

    Action purpose:
        End the current run. Clears the current_run state record. Bad
        publicity credits are returned to the bank.

    Preconditions:
        - Run in progress (state.current_run)
        - No encounter in progress (state.current_encounter)

    Effects:
        - Run state cleared (state.current_run) [DATA]
        - Bad-pub credits returned (implicit) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(successful, bool): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    if state.current_encounter is not None:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Clear run state
    state.current_run = None
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# Encounter Mechanics Actions (5)
# ----------------------------------------------------------------------------

def a_pump_breaker(state: State, breaker_name: str, amount: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_pump_breaker(state, breaker_name, amount)

    Action parameters:
        breaker_name: Name of the icebreaker to pump (e.g., 'corroder')
        amount: Number of +1 strength boosts to apply this encounter

    Action purpose:
        Pay credits to give an installed icebreaker a +amount strength boost
        that lasts only for the current encounter. For Corroder, Wyrm, Crypsis
        (encounter-scoped pump). Toolbox recurring credits used first.

    Preconditions:
        - Encounter in progress (state.current_encounter)
        - Breaker is installed and has 'encounter' pump scope
        - amount > 0
        - Runner can pay amount * pump_cost via icebreaker channel

    Effects:
        - breaker_pumps[breaker_name] increased by amount (state.current_encounter) [DATA]
        - Credits paid (toolbox first, then pool) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(breaker_name, str): return False
    if not isinstance(amount, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if amount <= 0: return False
    if breaker_name not in ICEBREAKER_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_encounter is None:
        return False
    if breaker_name not in state.installed_programs:
        return False
    breaker_data = ICEBREAKER_DATA[breaker_name]
    if breaker_data.get('pump_scope') != 'encounter':
        return False
    cost = amount * breaker_data['pump_cost']
    # Confirm payment is possible before mutating state
    if (state.toolbox_recurring + state.runner_credits
            + (state.current_run.get('bad_pub_credits', 0) if state.current_run else 0)) < cost:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Pay via icebreaker channel (Toolbox first)
    _h_pay_icebreaker_cost(state, cost)
    # [DATA] Apply encounter-scoped pump
    pumps = state.current_encounter.setdefault('breaker_pumps', {})
    pumps[breaker_name] = pumps.get(breaker_name, 0) + amount
    # END: Effects

    return state


def a_pump_gordian(state: State, amount: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_pump_gordian(state, amount)

    Action parameters:
        amount: Number of +1 strength boosts to apply (lasts rest of run)

    Action purpose:
        Pay credits to give Gordian Blade a +amount strength boost that lasts
        for the remainder of the current run (run-scoped pump).

    Preconditions:
        - Run in progress (state.current_run)
        - Gordian Blade is installed (state.installed_programs)
        - amount > 0
        - Runner can pay amount * 1 via icebreaker channel

    Effects:
        - current_run.gordian_pumps increased by amount (state.current_run) [DATA]
        - Credits paid (toolbox first, then pool) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(amount, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if amount <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    if 'gordian_blade' not in state.installed_programs:
        return False
    cost = amount * ICEBREAKER_DATA['gordian_blade']['pump_cost']
    if (state.toolbox_recurring + state.runner_credits
            + state.current_run.get('bad_pub_credits', 0)) < cost:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Pay via icebreaker channel
    _h_pay_icebreaker_cost(state, cost)
    # [DATA] Run-scoped pump
    state.current_run['gordian_pumps'] = state.current_run.get('gordian_pumps', 0) + amount
    # END: Effects

    return state


def a_drain_ice_strength(state: State, amount: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_drain_ice_strength(state, amount)

    Action parameters:
        amount: Number of -1 ice strength applications (encounter-scoped)

    Action purpose:
        Use Wyrm's 1-credit ability to reduce the strength of the currently-
        encountered ice by amount. Effect lasts only for this encounter.

    Preconditions:
        - Encounter in progress (state.current_encounter)
        - Wyrm is installed (state.installed_programs)
        - Wyrm's strength prerequisite met (current breaker strength >= ice strength)
        - Runner can pay amount * 1 via icebreaker channel

    Effects:
        - current_encounter.ice_strength_drain increased by amount (state.current_encounter) [DATA]
        - Credits paid (toolbox first, then pool) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(amount, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if amount <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_encounter is None:
        return False
    if 'wyrm' not in state.installed_programs:
        return False
    ice_id = state.current_encounter['ice_id']
    if not _h_breaker_can_interact(state, 'wyrm', ice_id):
        return False
    cost = amount * ICEBREAKER_DATA['wyrm']['drain_cost']
    if (state.toolbox_recurring + state.runner_credits
            + (state.current_run.get('bad_pub_credits', 0) if state.current_run else 0)) < cost:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Pay via icebreaker channel
    _h_pay_icebreaker_cost(state, cost)
    # [DATA] Reduce ice strength for this encounter
    state.current_encounter['ice_strength_drain'] = state.current_encounter.get('ice_strength_drain', 0) + amount
    # END: Effects

    return state


def a_break_subroutine(state: State, breaker_name: str, sub_idx: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_break_subroutine(state, breaker_name, sub_idx)

    Action parameters:
        breaker_name: Name of the icebreaker doing the breaking
        sub_idx: Index of the subroutine on the ice (0-based, listed order)

    Action purpose:
        Break the specified subroutine on the currently-encountered ice using
        the named breaker. Pays the breaker's break cost. Validates subtype
        affinity, strength prerequisite, and any break predicate (e.g., Wyrm
        requires ice strength <= 0). For Crypsis, marks crypsis_used so the
        end-of-encounter cleanup fires.

    Preconditions:
        - Encounter in progress (state.current_encounter)
        - Breaker can break this ice (subtype + strength + predicate)
        - sub_idx is a valid subroutine index on the ice
        - Subroutine not already broken
        - Runner can pay break_cost via icebreaker channel

    Effects:
        - Subroutine marked broken (state.current_encounter.subroutines_broken) [DATA]
        - Credits paid (toolbox first, then pool) [DATA]
        - crypsis_used flag set if breaker is crypsis [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(breaker_name, str): return False
    if not isinstance(sub_idx, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if sub_idx < 0: return False
    if breaker_name not in ICEBREAKER_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_encounter is None:
        return False
    ice_id = state.current_encounter['ice_id']
    ice_data = _h_get_ice_data(state, ice_id)
    if ice_data is None:
        return False
    if sub_idx >= len(ice_data['subroutines']):
        return False
    if sub_idx in state.current_encounter['subroutines_broken']:
        return False
    if not _h_breaker_can_break(state, breaker_name, ice_id):
        return False
    cost = ICEBREAKER_DATA[breaker_name]['break_cost']
    if (state.toolbox_recurring + state.runner_credits
            + (state.current_run.get('bad_pub_credits', 0) if state.current_run else 0)) < cost:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Pay via icebreaker channel
    _h_pay_icebreaker_cost(state, cost)
    # [DATA] Mark sub broken
    state.current_encounter['subroutines_broken'].add(sub_idx)
    # [DATA] Track Crypsis usage for end-of-encounter clause
    if breaker_name == 'crypsis':
        state.current_encounter['crypsis_used'] = True
    # END: Effects

    return state


def a_end_encounter(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_end_encounter(state)

    Action parameters:
        None

    Action purpose:
        Conclude the current encounter, clearing encounter-scoped state.
        Note: Crypsis end-of-encounter cleanup is handled by separate
        actions inside m_handle_encounter before this is called.

    Preconditions:
        - Encounter in progress (state.current_encounter)

    Effects:
        - Encounter state cleared (state.current_encounter) [DATA]

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
    if state.current_encounter is None:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Clear encounter state
    state.current_encounter = None
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# Subroutine Resolution Actions (5)
# ----------------------------------------------------------------------------

def a_resolve_end_run(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_resolve_end_run(state)

    Action parameters:
        None

    Action purpose:
        Resolve an unbroken 'end the run' subroutine: mark the current run as
        ended unsuccessfully.

    Preconditions:
        - Run in progress (state.current_run)
        - Run not already ended

    Effects:
        - Run flagged as ended (state.current_run.run_ended) [ENABLER]

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
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Mark run ended unsuccessfully
    state.current_run['run_ended'] = True
    # END: Effects

    return state


def a_resolve_net_damage(state: State, amount: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_resolve_net_damage(state, amount)

    Action parameters:
        amount: Net damage points to inflict on the Runner

    Action purpose:
        Resolve unbroken net damage: trash 'amount' random cards from the
        Runner's grip (modeled as grip_count decrement). If grip can't cover
        the damage, the Runner is flatlined.

    Preconditions:
        - amount > 0

    Effects:
        - grip_count decreased (or floored at 0) (state.grip_count) [DATA]
        - heap_count increased (state.heap_count) [DATA]
        - flatlined set if grip insufficient (state.flatlined) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(amount, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if amount <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No additional preconditions
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Trash cards from grip; flatline if grip empty before all damage applied
    actually_trashed = min(amount, state.grip_count)
    state.grip_count -= actually_trashed
    state.heap_count += actually_trashed
    if actually_trashed < amount:
        # [ENABLER] Flatlined
        state.flatlined = True
    # END: Effects

    return state


def a_resolve_lose_click(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_resolve_lose_click(state)

    Action parameters:
        None

    Action purpose:
        Resolve an unbroken 'Runner loses a click, if able' subroutine.
        If the Runner has no remaining clicks, the subroutine has no effect.

    Preconditions:
        None (always resolvable; "if able" is checked in effects)

    Effects:
        - runner_clicks decremented if >= 1, else no change (state.runner_clicks) [DATA]

    Idempotency:
        When runner_clicks is already 0, this action returns state unchanged,
        so GTPyhop classifies it as idempotent and elides it from the returned
        plan. This matches the rulebook ("if able"): when the Runner has no
        clicks, the subroutine has no effect. In scenario_3 (rulebook p.19)
        Bart's run is his last click, so this subroutine fires as a no-op and
        does not appear in result.plan. To see this action in the trace, run
        with verbose=3.

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
    # [DATA] Lose a click if available
    if state.runner_clicks >= 1:
        state.runner_clicks -= 1
    # END: Effects

    return state


def a_resolve_trace(state: State, ice_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_resolve_trace(state, ice_name)

    Action parameters:
        ice_name: Name of the ice card initiating the trace (e.g., 'data_raven')

    Action purpose:
        Resolve a trace subroutine. Corp spends a fixed budget configured
        in state.corp_policy.trace_budget[ice_name]; the Runner deterministically
        spends just enough to make the trace unsuccessful (if affordable),
        otherwise lets the trace succeed. For Data Raven, a successful trace
        places a power counter (cosmetic in our subset).

    Preconditions:
        - ice_name is a known tracer ice (ICE_DATA)

    Effects:
        - Corp credits decreased by trace_budget (state.corp_credits) [DATA]
        - Runner credits decreased by amount needed (state.runner_credits) [DATA]
        - If trace successful: cosmetic power counter (not tracked) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if ice_name not in ICE_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # ice must have a trace subroutine; we don't enforce strictly
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Corp spends configured trace budget
    trace_budget = state.corp_policy.get('trace_budget', {}).get(ice_name, 0)
    spend = min(trace_budget, state.corp_credits)
    state.corp_credits -= spend
    # [DATA] Compute base trace strength + Corp boost
    base = 0
    for sub in ICE_DATA[ice_name]['subroutines']:
        if sub.get('kind') == 'trace':
            base = sub.get('base_strength', 0)
            break
    trace_strength = base + spend
    # [DATA] Runner spends just enough to match (link strength = 0 in this subset)
    needed = trace_strength
    if state.runner_credits >= needed:
        state.runner_credits -= needed
    # else: trace succeeds; no further effect modeled for Data Raven (cosmetic counter)
    # END: Effects

    return state


def a_take_tag(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_take_tag(state)

    Action parameters:
        None

    Action purpose:
        Voluntarily take a tag (used for Data Raven's encounter ability
        "take 1 tag or end the run", when the Runner chooses to be tagged).

    Preconditions:
        None

    Effects:
        - tags incremented by 1 (state.tags) [DATA]

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
    # [DATA] Take a tag
    state.tags += 1
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# End-of-Encounter Cleanup Actions (3)
# ----------------------------------------------------------------------------

def a_spend_virus_counter(state: State, card_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_spend_virus_counter(state, card_name)

    Action parameters:
        card_name: Name of the card to spend a virus counter from (e.g., 'crypsis')

    Action purpose:
        Spend one hosted virus counter on the named card. Used at Crypsis's
        end-of-encounter cleanup to satisfy the "remove a counter or trash"
        clause.

    Preconditions:
        - Card has at least one virus counter (state.virus_counters)

    Effects:
        - virus_counters[card_name] decremented by 1 (state.virus_counters) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(card_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.virus_counters.get(card_name, 0) < 1:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Spend one virus counter
    state.virus_counters[card_name] -= 1
    # END: Effects

    return state


def a_trash_crypsis(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_trash_crypsis(state)

    Action parameters:
        None

    Action purpose:
        Trash Crypsis as the alternative to spending a virus counter at the
        end of an encounter in which Crypsis was used to break a subroutine.
        Frees up the MU Crypsis occupied.

    Preconditions:
        - Crypsis is installed (state.installed_programs)

    Effects:
        - Crypsis removed from installed_programs (state.installed_programs) [DATA]
        - MU freed (state.mu_available) [DATA]
        - heap_count incremented (state.heap_count) [DATA]

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
    if 'crypsis' not in state.installed_programs:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Remove Crypsis from rig
    del state.installed_programs['crypsis']
    # [DATA] Free MU
    state.mu_available += ICEBREAKER_DATA['crypsis']['mu_cost']
    # [DATA] Crypsis goes to heap
    state.heap_count += 1
    # END: Effects

    return state


def a_trash_sacrificial_construct(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_trash_sacrificial_construct(state)

    Action parameters:
        None

    Action purpose:
        Trash Sacrificial Construct to prevent a program or hardware trash
        that would otherwise resolve. Per the card text, this is a prevent
        effect that absorbs one such trash.

    Preconditions:
        - Sacrificial Construct is installed (state.installed_resources)

    Effects:
        - Sacrificial Construct removed from installed_resources (state.installed_resources) [DATA]
        - heap_count incremented (state.heap_count) [DATA]

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
    if 'sacrificial_construct' not in state.installed_resources:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Remove Sacrificial Construct from rig
    del state.installed_resources['sacrificial_construct']
    # [DATA] Sacrificial Construct goes to heap
    state.heap_count += 1
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# Access Phase Actions (4)
# ----------------------------------------------------------------------------

def a_steal_agenda(state: State, agenda_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_steal_agenda(state, agenda_name)

    Action parameters:
        agenda_name: Name of the agenda being accessed and stolen

    Action purpose:
        Steal an accessed agenda, adding its points to the Runner's score and
        triggering any "when scored or stolen" identity ability (e.g., Jinteki
        Personal Evolution does 1 net damage on every steal).

    Preconditions:
        - Run successful (current_run reached the access phase)
        - Agenda is in a server (state.servers)
        - Agenda data known (AGENDA_DATA)

    Effects:
        - agenda_points_runner increased by agenda's points (state.agenda_points_runner) [DATA]
        - Agenda removed from server contents (state.servers) [DATA]
        - Jinteki PE identity: 1 net damage applied if applicable (state.grip_count, state.heap_count) [DATA]
        - Flatlined (state.flatlined) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(agenda_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if agenda_name not in AGENDA_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    server = state.current_run['server']
    if server not in state.servers:
        return False
    contents = state.servers[server].get('contents', [])
    if agenda_name not in contents:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Add points to Runner's score
    state.agenda_points_runner += AGENDA_DATA[agenda_name]['points']
    # [DATA] Remove agenda from server
    contents.remove(agenda_name)
    # [DATA] Jinteki PE identity ability: 1 net damage on steal
    if state.corp_identity == 'jinteki_personal_evolution':
        if state.grip_count >= 1:
            state.grip_count -= 1
            state.heap_count += 1
        else:
            state.flatlined = True
    # END: Effects

    return state


def a_pay_trash_cost(state: State, card_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_pay_trash_cost(state, card_name)

    Action parameters:
        card_name: Name of the asset/upgrade being trashed

    Action purpose:
        Pay an accessed asset/upgrade's trash cost to remove it. Used in the
        access phase when the Runner can afford and wishes to trash.

    Preconditions:
        - Current run reached access phase
        - Card has a known trash cost (ASSET_DATA or UPGRADE_DATA)
        - Runner has sufficient credits (general pool only, not Toolbox)

    Effects:
        - Credits paid (state.runner_credits) [DATA]
        - Card removed from server (state.servers / state.upgrade_rezzed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(card_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    trash_cost = None
    if card_name in ASSET_DATA:
        trash_cost = ASSET_DATA[card_name]['trash_cost']
    elif card_name in UPGRADE_DATA:
        trash_cost = UPGRADE_DATA[card_name]['trash_cost']
    if trash_cost is None:
        return False
    if state.runner_credits < trash_cost:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Pay trash cost
    state.runner_credits -= trash_cost
    # [DATA] Remove from server
    server = state.current_run['server']
    server_data = state.servers.get(server, {})
    contents = server_data.get('contents', [])
    if card_name in contents:
        contents.remove(card_name)
    upgrades = server_data.get('upgrades', [])
    for u_idx, upgrade in enumerate(list(upgrades)):
        if upgrade == card_name:
            upgrades.pop(u_idx)
            # Also clear rez state for that slot; trailing upgrade slots shift
            state.upgrade_rezzed.pop((server, u_idx), None)
            break
    # END: Effects

    return state


def a_fire_ambush(state: State, asset_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_fire_ambush(state, asset_name)

    Action parameters:
        asset_name: Name of the ambush asset being triggered (e.g., 'aggressive_secretary')

    Action purpose:
        Trigger the on-access ambush effect of an asset like Aggressive
        Secretary: Corp pays the ambush cost; effect determined by card.
        For Aggressive Secretary: trash N programs where N = advancement
        tokens on the asset.

    Preconditions:
        - Asset is in the accessed server (state.servers)
        - Asset is a known ambush (ASSET_DATA)
        - Corp policy directs the ambush to fire (state.corp_policy.ambush_fire)
        - Corp can afford the ambush cost (state.corp_credits)

    Effects:
        - Corp credits decreased (state.corp_credits) [DATA]
        - Programs trashed up to N (separate a_trash_program actions) - handled in method
        - Ambush marker (no state change here beyond corp credits) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(asset_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if asset_name not in ASSET_DATA: return False
    if not ASSET_DATA[asset_name].get('ambush'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    if not state.corp_policy.get('ambush_fire', {}).get(asset_name, False):
        return False
    cost = ASSET_DATA[asset_name].get('ambush_cost', 0)
    if state.corp_credits < cost:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Corp pays the ambush cost
    state.corp_credits -= cost
    # END: Effects

    return state


def a_trash_program(state: State, program_name: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_trash_program(state, program_name)

    Action parameters:
        program_name: Name of the program being trashed

    Action purpose:
        Trash an installed program (typically from an ambush effect like
        Aggressive Secretary). Used when no prevent (Sacrificial Construct)
        is available or chosen.

    Preconditions:
        - Program is installed (state.installed_programs)

    Effects:
        - Program removed from installed_programs (state.installed_programs) [DATA]
        - MU freed (state.mu_available) [DATA]
        - heap_count incremented (state.heap_count) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(program_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if program_name not in ICEBREAKER_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if program_name not in state.installed_programs:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Remove program from rig
    del state.installed_programs[program_name]
    # [DATA] Free MU
    state.mu_available += ICEBREAKER_DATA[program_name]['mu_cost']
    # [DATA] Program goes to heap
    state.heap_count += 1
    # END: Effects

    return state


# ============================================================================
# METHODS
# ============================================================================

# ----------------------------------------------------------------------------
# Top-Level and Run Decomposition Methods (4 task names)
# ----------------------------------------------------------------------------

def m_steal_agenda(state: State, target_agenda: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_steal_agenda(state, target_agenda)

    Method parameters:
        target_agenda: Tuple (server, content_idx) identifying the agenda to steal

    Method purpose:
        Top-level decomposition: run on the server containing the target agenda
        and steal it.

    Preconditions:
        - target_agenda is a valid (server, idx) tuple
        - Server exists and the indexed content is a known agenda

    Task decomposition:
        - m_run_on_server: Execute a full run against the target server

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(target_agenda, tuple) or len(target_agenda) != 2: return False
    server, idx = target_agenda
    if not isinstance(server, str): return False
    if not isinstance(idx, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if server not in state.servers:
        return False
    contents = state.servers[server].get('contents', [])
    if idx < 0 or idx >= len(contents):
        return False
    if contents[idx] not in AGENDA_DATA:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("m_run_on_server", server)]
    # END: Task Decomposition


def m_run_on_server(state: State, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_run_on_server(state, server)

    Method parameters:
        server: Identifier of the server to run on

    Method purpose:
        Decompose a run on a server into: initiate -> traverse ice -> access
        -> end run.

    Preconditions:
        - Server exists (state.servers)
        - Runner has at least 1 click (state.runner_clicks)

    Task decomposition:
        - a_initiate_run: Begin the run
        - m_traverse_ice_stack: Approach each ice in turn
        - m_access_server: Access cards in the server
        - a_end_run: Conclude the run successfully

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if server not in state.servers:
        return False
    if state.runner_clicks < 1:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initiate_run", server),
        ("m_traverse_ice_stack", server),
        ("m_access_server", server),
        ("a_end_run", True),
    ]
    # END: Task Decomposition


def m_traverse_ice_stack(state: State, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_traverse_ice_stack(state, server)

    Method parameters:
        server: Identifier of the server being run on

    Method auxiliary parameters:
        next_idx: int (computed from current_run.approach_idx + 1)

    Method purpose:
        Recursively traverse the server's ice stack. If there are more pieces
        of ice to approach, decompose into [handle approach, recurse]; if not,
        return empty (control passes to the access phase).

    Preconditions:
        - Run in progress (state.current_run)
        - server matches current_run.server

    Task decomposition:
        - m_handle_approach: Approach the next ice
        - m_traverse_ice_stack: Recurse on the remaining stack

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if state.current_run is None:
        return False
    if state.current_run['server'] != server:
        return False
    next_idx = state.current_run['approach_idx'] + 1
    ice_count = len(state.servers.get(server, {}).get('ice', []))
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if state.current_run.get('run_ended'):
        # Run has ended; nothing more to traverse. Access phase will short-circuit too.
        return []
    if state.flatlined:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    if next_idx >= ice_count:
        return []
    return [
        ("m_handle_approach", server, next_idx),
        ("m_traverse_ice_stack", server),
    ]
    # END: Task Decomposition


def m_handle_approach(state: State, server: str, idx: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_handle_approach(state, server, idx)

    Method parameters:
        server: Identifier of the server being run on
        idx: Index of the ice being approached

    Method purpose:
        Approach the ice at index idx and dispatch to either an encounter
        (if Corp rezzes the ice) or a pass (if Corp declines).

    Preconditions:
        - Run in progress (state.current_run)

    Task decomposition:
        - a_approach_ice: Move to the ice (Corp may rez)
        - m_post_approach: Continue with encounter or pass based on rez state

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(idx, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if idx < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_approach_ice", idx),
        ("m_post_approach", server, idx),
    ]
    # END: Task Decomposition


def m_post_approach(state: State, server: str, idx: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_post_approach(state, server, idx)

    Method parameters:
        server: Identifier of the server being run on
        idx: Index of the ice approached

    Method purpose:
        After a_approach_ice has resolved the Corp rez window, dispatch to
        either an encounter (if ice is rezzed) or a pass (if ice is unrezzed).

    Preconditions:
        - Run in progress (state.current_run)

    Task decomposition:
        Either:
          - m_handle_encounter: if the ice ended up rezzed
        Or:
          - a_pass_ice: if the ice remained unrezzed

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(idx, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return []
    # END: Preconditions

    # BEGIN: Task Decomposition
    if state.ice_rezzed.get((server, idx), False):
        return [("m_handle_encounter", (server, idx))]
    return [("a_pass_ice",)]
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# Encounter Resolution Methods
# ----------------------------------------------------------------------------

# --- Method-side helpers (private to the methods section) -------------------

def _h_can_afford_icebreaker(state: State, cost: int) -> bool:
    """Check whether the Runner can pay an icebreaker cost via Toolbox + pool + bad-pub."""
    available = state.toolbox_recurring + state.runner_credits
    if state.current_run is not None:
        available += state.current_run.get('bad_pub_credits', 0)
    return available >= cost


def _h_end_run_sub_indices(ice_name: str) -> List[int]:
    """Return indices of 'end_run' subroutines on the named ice."""
    ice_data = ICE_DATA.get(ice_name)
    if ice_data is None:
        return []
    return [i for i, sub in enumerate(ice_data['subroutines']) if sub.get('kind') == 'end_run']


def _h_all_sub_indices(ice_name: str) -> List[int]:
    """Return indices of all subroutines on the named ice."""
    ice_data = ICE_DATA.get(ice_name)
    if ice_data is None:
        return []
    return list(range(len(ice_data['subroutines'])))


def _h_compute_break_plan(state: State, ice_id: Tuple[str, int],
                          breaker_name: str,
                          target_subs: List[int]) -> Optional[List[Tuple]]:
    """
    Compute a task list (pump + drain + breaks) for breaking the given target
    subroutines on the ice using the named breaker. Returns None if infeasible.
    Empty target_subs returns []  (trivial success).
    """
    if not target_subs:
        return []
    if breaker_name not in state.installed_programs:
        return None
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return None
    if not _h_subtype_matches(breaker_name, ice_name):
        return None
    breaker_data = ICEBREAKER_DATA[breaker_name]
    ice_str = _h_current_ice_strength(state, ice_id)
    breaker_str = _h_current_breaker_strength(state, breaker_name)
    pumps_needed = max(0, ice_str - breaker_str)
    n_breaks = len(target_subs)
    pump_cost = pumps_needed * breaker_data['pump_cost']
    break_cost = n_breaks * breaker_data['break_cost']
    drain_cost = 0
    drains_needed = 0
    if breaker_data.get('break_predicate') == 'ice_strength_le_zero':
        drains_needed = ice_str  # bring ice to 0
        drain_cost = drains_needed * breaker_data.get('drain_cost', 1)
    total = pump_cost + break_cost + drain_cost
    if not _h_can_afford_icebreaker(state, total):
        return None
    tasks: List[Tuple] = []
    if pumps_needed > 0:
        if breaker_data['pump_scope'] == 'run':
            tasks.append(('a_pump_gordian', pumps_needed))
        else:
            tasks.append(('a_pump_breaker', breaker_name, pumps_needed))
    if drains_needed > 0:
        tasks.append(('a_drain_ice_strength', drains_needed))
    for sub_idx in target_subs:
        tasks.append(('a_break_subroutine', breaker_name, sub_idx))
    return tasks


def m_handle_encounter(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_handle_encounter(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) identifying the encountered ice

    Method purpose:
        Sequence the encounter: optional on-encounter ability (Data Raven) ->
        break subroutines -> resolve unbroken subroutines -> Crypsis cleanup
        if applicable -> end encounter.

    Preconditions:
        - Encounter in progress for this ice (state.current_encounter)

    Task decomposition:
        - m_handle_on_encounter_ability: if the ice has an on-encounter ability (Data Raven)
        - m_break_ice: choose icebreaker and break subroutines
        - m_resolve_unbroken_subs: fire any unbroken subroutines
        - m_crypsis_cleanup: handle Crypsis end-of-encounter clause
        - a_end_encounter: clear encounter state

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple) or len(ice_id) != 2: return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if state.current_encounter is None:
        return False
    if state.current_encounter.get('ice_id') != ice_id:
        return False
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    ice_data = ICE_DATA[ice_name]
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if state.current_run is None or state.current_run.get('run_ended'):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks: List[Tuple] = []
    on_encounter = ice_data.get('on_encounter')
    if on_encounter == 'tag_or_end_run':
        tasks.append(("m_handle_data_raven_on_encounter",))
    tasks.append(("m_break_ice", ice_id))
    tasks.append(("m_resolve_unbroken_subs", ice_id))
    tasks.append(("m_crypsis_cleanup",))
    tasks.append(("a_end_encounter",))
    return tasks
    # END: Task Decomposition


# --- Data Raven on-encounter ability alternatives ---------------------------

def m_data_raven_take_tag(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_data_raven_take_tag(state)

    Method parameters:
        None

    Method purpose:
        Resolve Data Raven's on-encounter "take 1 tag or end the run" by
        choosing to take the tag. Preferred over ending the run (which would
        abort the steal attempt).

    Preconditions:
        - Encounter in progress on Data Raven (implicit by registration)

    Task decomposition:
        - a_take_tag: Accept the tag

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
    if state.current_encounter is None:
        return False
    ice_id = state.current_encounter.get('ice_id')
    if _h_get_ice_name(state, ice_id) != 'data_raven':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_take_tag",)]
    # END: Task Decomposition


def m_data_raven_voluntary_end_run(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_data_raven_voluntary_end_run(state)

    Method parameters:
        None

    Method purpose:
        Resolve Data Raven's on-encounter "take 1 tag or end the run" by
        choosing to end the run. This fails the steal attempt; only useful
        when no tag is acceptable (not in this subset).

    Preconditions:
        - Encounter in progress on Data Raven

    Task decomposition:
        - a_resolve_end_run: Voluntarily end the run

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
    if state.current_encounter is None:
        return False
    ice_id = state.current_encounter.get('ice_id')
    if _h_get_ice_name(state, ice_id) != 'data_raven':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_resolve_end_run",)]
    # END: Task Decomposition


# --- Break-ice alternatives: 8 methods (4 breakers x 2 completeness) --------

def m_break_with_corroder_full(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_break_with_corroder_full(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Break ALL subroutines on the ice using Corroder. Requires Corroder
        installed, subtype match, and credit budget for all pumps + breaks.

    Preconditions:
        - Corroder installed; subtype matches; sufficient credits

    Task decomposition:
        - a_pump_breaker (if pumps needed)
        - a_break_subroutine for each subroutine

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    target_subs = _h_all_sub_indices(ice_name)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    plan = _h_compute_break_plan(state, ice_id, 'corroder', target_subs)
    if plan is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return plan
    # END: Task Decomposition


def m_break_with_gordian_full(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_break_with_gordian_full(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Break ALL subroutines on the ice using Gordian Blade.

    Preconditions:
        - Gordian Blade installed; subtype matches; sufficient credits

    Task decomposition:
        - a_pump_gordian (if pumps needed; run-scope pump)
        - a_break_subroutine for each subroutine

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    target_subs = _h_all_sub_indices(ice_name)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    plan = _h_compute_break_plan(state, ice_id, 'gordian_blade', target_subs)
    if plan is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return plan
    # END: Task Decomposition


def m_break_with_wyrm_full(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_break_with_wyrm_full(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Break ALL subroutines on the ice using Wyrm (AI). Includes pump to
        meet strength prerequisite, then drain ice strength to zero, then
        break each subroutine.

    Preconditions:
        - Wyrm installed; sufficient credits

    Task decomposition:
        - a_pump_breaker (if pumps needed)
        - a_drain_ice_strength (to bring ice to 0)
        - a_break_subroutine for each subroutine

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    target_subs = _h_all_sub_indices(ice_name)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    plan = _h_compute_break_plan(state, ice_id, 'wyrm', target_subs)
    if plan is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return plan
    # END: Task Decomposition


def m_break_with_crypsis_full(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_break_with_crypsis_full(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Break ALL subroutines on the ice using Crypsis (AI). Marks Crypsis as
        used this encounter, triggering end-of-encounter cleanup.

    Preconditions:
        - Crypsis installed; sufficient credits

    Task decomposition:
        - a_pump_breaker (if pumps needed)
        - a_break_subroutine for each subroutine

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    target_subs = _h_all_sub_indices(ice_name)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    plan = _h_compute_break_plan(state, ice_id, 'crypsis', target_subs)
    if plan is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return plan
    # END: Task Decomposition


def m_break_with_corroder_partial(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_break_with_corroder_partial(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Break ONLY the 'end_run' subroutines on the ice using Corroder.
        Other subs are allowed to fire (e.g., net damage). Saves credits.

    Preconditions:
        - If end-run subs exist: Corroder installed, subtype matches, credits OK
        - If no end-run subs: trivially succeeds (no actions)

    Task decomposition:
        - a_pump_breaker (if pumps needed)
        - a_break_subroutine for each end-run subroutine

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    target_subs = _h_end_run_sub_indices(ice_name)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    plan = _h_compute_break_plan(state, ice_id, 'corroder', target_subs)
    if plan is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return plan
    # END: Task Decomposition


def m_break_with_gordian_partial(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_break_with_gordian_partial(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Break ONLY the 'end_run' subroutines using Gordian Blade. Saves credits.

    Preconditions:
        - If end-run subs exist: Gordian Blade installed, subtype matches, credits OK

    Task decomposition:
        - a_pump_gordian (if pumps needed; run-scope)
        - a_break_subroutine for each end-run subroutine

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    target_subs = _h_end_run_sub_indices(ice_name)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    plan = _h_compute_break_plan(state, ice_id, 'gordian_blade', target_subs)
    if plan is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return plan
    # END: Task Decomposition


def m_break_with_wyrm_partial(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_break_with_wyrm_partial(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Break ONLY the 'end_run' subroutines using Wyrm. Saves break costs.

    Preconditions:
        - If end-run subs exist: Wyrm installed, sufficient credits

    Task decomposition:
        - a_pump_breaker (if pumps needed)
        - a_drain_ice_strength (to bring ice to 0)
        - a_break_subroutine for each end-run subroutine

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    target_subs = _h_end_run_sub_indices(ice_name)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    plan = _h_compute_break_plan(state, ice_id, 'wyrm', target_subs)
    if plan is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return plan
    # END: Task Decomposition


def m_break_with_crypsis_partial(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_break_with_crypsis_partial(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Break ONLY the 'end_run' subroutines using Crypsis. Saves break costs.

    Preconditions:
        - If end-run subs exist: Crypsis installed, sufficient credits

    Task decomposition:
        - a_pump_breaker (if pumps needed)
        - a_break_subroutine for each end-run subroutine

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    target_subs = _h_end_run_sub_indices(ice_name)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    plan = _h_compute_break_plan(state, ice_id, 'crypsis', target_subs)
    if plan is None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return plan
    # END: Task Decomposition


# --- Unbroken-subroutine resolution -----------------------------------------

def m_resolve_unbroken_subs(state: State, ice_id: Tuple[str, int]) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_resolve_unbroken_subs(state, ice_id)

    Method parameters:
        ice_id: Tuple (server, idx) of the encountered ice

    Method purpose:
        Fire each unbroken subroutine on the ice in listed order. For our
        subset, every 'end_run' subroutine appears last on its ice; once it
        fires, the run ends and subsequent traversal short-circuits.

    Preconditions:
        - Encounter in progress on this ice

    Task decomposition:
        - For each unbroken subroutine, the matching a_resolve_<kind> action

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(ice_id, tuple): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if state.current_encounter is None:
        return False
    if state.current_encounter.get('ice_id') != ice_id:
        return False
    ice_name = _h_get_ice_name(state, ice_id)
    if ice_name is None:
        return False
    ice_data = ICE_DATA[ice_name]
    broken = state.current_encounter.get('subroutines_broken', set())
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No additional preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks: List[Tuple] = []
    for sub_idx, sub in enumerate(ice_data['subroutines']):
        if sub_idx in broken:
            continue
        kind = sub.get('kind')
        if kind == 'end_run':
            tasks.append(('a_resolve_end_run',))
        elif kind == 'net_damage':
            tasks.append(('a_resolve_net_damage', sub.get('amount', 1)))
        elif kind == 'lose_click':
            tasks.append(('a_resolve_lose_click',))
        elif kind == 'trace':
            tasks.append(('a_resolve_trace', ice_name))
    return tasks
    # END: Task Decomposition


# --- Crypsis end-of-encounter cleanup alternatives --------------------------

def m_crypsis_cleanup_spend_counter(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_crypsis_cleanup_spend_counter(state)

    Method parameters:
        None

    Method purpose:
        Resolve Crypsis end-of-encounter clause by spending one hosted virus
        counter on Crypsis. Preferred when counters are available.

    Preconditions:
        - Crypsis was used this encounter
        - Crypsis has at least one virus counter

    Task decomposition:
        - a_spend_virus_counter: Spend one counter from Crypsis

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
    if state.current_encounter is None:
        return False
    if not state.current_encounter.get('crypsis_used'):
        return False
    if 'crypsis' not in state.installed_programs:
        return False
    if state.virus_counters.get('crypsis', 0) < 1:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_spend_virus_counter', 'crypsis')]
    # END: Task Decomposition


def m_crypsis_cleanup_prevent_with_sc(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_crypsis_cleanup_prevent_with_sc(state)

    Method parameters:
        None

    Method purpose:
        Resolve Crypsis end-of-encounter clause by trashing Sacrificial
        Construct to prevent Crypsis from being trashed.

    Preconditions:
        - Crypsis was used this encounter
        - Sacrificial Construct is installed

    Task decomposition:
        - a_trash_sacrificial_construct: Trash SC to absorb the trash effect

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
    if state.current_encounter is None:
        return False
    if not state.current_encounter.get('crypsis_used'):
        return False
    if 'crypsis' not in state.installed_programs:
        return False
    if 'sacrificial_construct' not in state.installed_resources:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_trash_sacrificial_construct',)]
    # END: Task Decomposition


def m_crypsis_cleanup_let_trash(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_crypsis_cleanup_let_trash(state)

    Method parameters:
        None

    Method purpose:
        Resolve Crypsis end-of-encounter clause by letting Crypsis be trashed
        (no counter, no SC, or by choice).

    Preconditions:
        - Crypsis was used this encounter
        - Crypsis is installed

    Task decomposition:
        - a_trash_crypsis: Trash Crypsis to heap

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
    if state.current_encounter is None:
        return False
    if not state.current_encounter.get('crypsis_used'):
        return False
    if 'crypsis' not in state.installed_programs:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_trash_crypsis',)]
    # END: Task Decomposition


def m_crypsis_cleanup_skip(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_crypsis_cleanup_skip(state)

    Method parameters:
        None

    Method purpose:
        Skip Crypsis cleanup when Crypsis wasn't used this encounter (the
        clause only fires if Crypsis broke at least one subroutine).

    Preconditions:
        - Either no current encounter, or Crypsis wasn't used this encounter

    Task decomposition:
        - (empty) No actions needed

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
    if state.current_encounter is not None and state.current_encounter.get('crypsis_used'):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# Access Phase Methods
# ----------------------------------------------------------------------------

def m_access_server(state: State, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_access_server(state, server)

    Method parameters:
        server: Identifier of the server being accessed

    Method purpose:
        Access each card in the server: agendas first (steal them), then
        non-agenda contents (assets, possibly triggering ambush), then
        upgrades in the root. Short-circuits if the run ended or flatlined.

    Preconditions:
        - Run in progress (state.current_run)

    Task decomposition:
        - For each agenda in contents: m_access_one_agenda
        - For each non-agenda content (assets): m_access_one_asset
        - For each upgrade in root: m_access_one_upgrade

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return []
    if state.flatlined:
        return False
    if server not in state.servers:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks: List[Tuple] = []
    contents = state.servers[server].get('contents', [])
    upgrades = state.servers[server].get('upgrades', [])
    # Agendas first (by name, not index — index shifts as cards are stolen/trashed)
    for card in list(contents):
        if card in AGENDA_DATA:
            tasks.append(('m_access_one_agenda', server, card))
    # Then non-agenda contents (assets) by name
    for card in list(contents):
        if card in ASSET_DATA:
            tasks.append(('m_access_one_asset', server, card))
    # Then upgrades in the root by name
    for upgrade in list(upgrades):
        tasks.append(('m_access_one_upgrade', server, upgrade))
    return tasks
    # END: Task Decomposition


def m_access_one_agenda(state: State, server: str, agenda_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_access_one_agenda(state, server, agenda_name)

    Method parameters:
        server: Identifier of the server being accessed
        agenda_name: Name of the agenda to access

    Method purpose:
        Access a single agenda and steal it. Identity-driven side effects
        (e.g., Jinteki PE net damage) are applied inside a_steal_agenda.

    Preconditions:
        - Run in progress; not ended; not flatlined
        - Agenda is still in the server's contents

    Task decomposition:
        - a_steal_agenda: Take the agenda into the score area

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(agenda_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if agenda_name not in AGENDA_DATA: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return []
    if state.flatlined:
        return False
    contents = state.servers.get(server, {}).get('contents', [])
    if agenda_name not in contents:
        # Already stolen; nothing to do
        return []
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No additional preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_steal_agenda', agenda_name)]
    # END: Task Decomposition


# --- Asset access alternatives ---------------------------------------------

def m_access_one_asset(state: State, server: str, asset_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_access_one_asset(state, server, asset_name)

    Method parameters:
        server: Identifier of the server being accessed
        asset_name: Name of the asset card to access

    Method purpose:
        Access a single asset. First handle any on-access ambush effect
        (Aggressive Secretary), then optionally pay its trash cost.

    Preconditions:
        - Run in progress; not ended; not flatlined
        - Asset is still in the server's contents

    Task decomposition:
        - m_handle_ambush: Apply any ambush effect
        - m_decide_trash_asset: Optionally pay trash cost

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(asset_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if asset_name not in ASSET_DATA: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return []
    if state.flatlined:
        return False
    contents = state.servers.get(server, {}).get('contents', [])
    if asset_name not in contents:
        # Asset already trashed; skip
        return []
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No additional preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('m_handle_ambush', server, asset_name),
        ('m_decide_trash_asset', server, asset_name),
    ]
    # END: Task Decomposition


def m_handle_ambush_fire(state: State, server: str, asset_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_handle_ambush_fire(state, server, asset_name)

    Method parameters:
        server: Identifier of the server hosting the asset
        asset_name: Name of the asset whose ambush is firing

    Method purpose:
        Trigger an on-access ambush. Corp pays the ambush cost; the effect
        (currently only Aggressive Secretary's program-trash) is sequenced
        as a series of program trashes equal to the advancement count.

    Preconditions:
        - Asset is a known ambush
        - Corp policy directs the ambush to fire
        - Corp can afford the ambush cost

    Task decomposition:
        - a_fire_ambush: Pay the Corp ambush cost
        - a_trash_program: One per advancement token (capped at installed programs)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(asset_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if asset_name not in ASSET_DATA: return False
    if not ASSET_DATA[asset_name].get('ambush'): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if state.current_run is None:
        return False
    # Advancement is keyed by (server, card_name) — name-keyed survives index shifts
    advance = state.agenda_advancement.get((server, asset_name), 0)
    if advance < 1:
        return False
    # Which programs the Corp will trash: configured priority list, then any installed
    trash_targets = state.corp_policy.get('ambush_trash_targets', {}).get(asset_name, [])
    installed = list(state.installed_programs.keys())
    chosen: List[str] = []
    for name in trash_targets:
        if name in state.installed_programs and name not in chosen:
            chosen.append(name)
        if len(chosen) == advance:
            break
    if len(chosen) < advance:
        for name in installed:
            if name not in chosen:
                chosen.append(name)
            if len(chosen) == advance:
                break
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not state.corp_policy.get('ambush_fire', {}).get(asset_name, False):
        return False
    cost = ASSET_DATA[asset_name].get('ambush_cost', 0)
    if state.corp_credits < cost:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks: List[Tuple] = [('a_fire_ambush', asset_name)]
    for prog in chosen:
        tasks.append(('a_trash_program', prog))
    return tasks
    # END: Task Decomposition


def m_handle_ambush_skip(state: State, server: str, asset_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_handle_ambush_skip(state, server, asset_name)

    Method parameters:
        server: Identifier of the server hosting the asset
        asset_name: Name of the asset

    Method purpose:
        Skip the ambush effect when Corp policy declines to fire, when the
        asset has no ambush, or when Corp can't afford the cost.

    Preconditions:
        - Either: asset is not an ambush, or Corp policy declines, or Corp
          can't afford

    Task decomposition:
        - (empty) No actions

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(asset_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    # If the ambush *would* fire (Corp policy = True AND affordable AND has advancement),
    # this method does not apply.
    if asset_name in ASSET_DATA and ASSET_DATA[asset_name].get('ambush'):
        if state.corp_policy.get('ambush_fire', {}).get(asset_name, False):
            cost = ASSET_DATA[asset_name].get('ambush_cost', 0)
            if state.corp_credits >= cost:
                advance = state.agenda_advancement.get((server, asset_name), 0)
                if advance >= 1:
                    return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_decide_trash_asset_pay(state: State, server: str, asset_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_decide_trash_asset_pay(state, server, asset_name)

    Method parameters:
        server: Identifier of the server hosting the asset
        asset_name: Name of the asset

    Method purpose:
        Pay the asset's trash cost to remove it from the server. Used when
        the Runner can afford the cost and wants to remove the asset.

    Preconditions:
        - Asset has a known trash cost
        - Runner has sufficient credits

    Task decomposition:
        - a_pay_trash_cost: Pay and remove the asset

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(asset_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if asset_name not in ASSET_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    cost = ASSET_DATA[asset_name].get('trash_cost', 0)
    if state.runner_credits < cost:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_pay_trash_cost', asset_name)]
    # END: Task Decomposition


def m_decide_trash_asset_skip(state: State, server: str, asset_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_decide_trash_asset_skip(state, server, asset_name)

    Method parameters:
        server: Identifier of the server hosting the asset
        asset_name: Name of the asset

    Method purpose:
        Skip paying the trash cost; the asset stays installed. Used when
        the Runner can't or won't trash.

    Preconditions:
        None

    Task decomposition:
        - (empty) No actions

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(asset_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions; always available
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


# --- Upgrade access alternatives -------------------------------------------

def m_access_one_upgrade(state: State, server: str, upgrade_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_access_one_upgrade(state, server, upgrade_name)

    Method parameters:
        server: Identifier of the server being accessed
        upgrade_name: Name of the upgrade card to access

    Method purpose:
        Access a single upgrade in the server root. Optionally trash it by
        paying its trash cost.

    Preconditions:
        - Run in progress; not ended; not flatlined
        - Upgrade is still in the server's upgrades

    Task decomposition:
        - m_decide_trash_upgrade: Optionally pay trash cost

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(upgrade_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if upgrade_name not in UPGRADE_DATA: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if state.current_run is None:
        return False
    if state.current_run.get('run_ended'):
        return []
    if state.flatlined:
        return False
    upgrades = state.servers.get(server, {}).get('upgrades', [])
    if upgrade_name not in upgrades:
        # Already trashed
        return []
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No additional preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('m_decide_trash_upgrade', server, upgrade_name)]
    # END: Task Decomposition


def m_decide_trash_upgrade_pay(state: State, server: str, upgrade_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_decide_trash_upgrade_pay(state, server, upgrade_name)

    Method parameters:
        server: Identifier of the server hosting the upgrade
        upgrade_name: Name of the upgrade

    Method purpose:
        Pay the upgrade's trash cost.

    Preconditions:
        - Upgrade is known
        - Runner has sufficient credits

    Task decomposition:
        - a_pay_trash_cost: Pay and remove

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(upgrade_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if upgrade_name not in UPGRADE_DATA: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    cost = UPGRADE_DATA[upgrade_name].get('trash_cost', 0)
    if state.runner_credits < cost:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_pay_trash_cost', upgrade_name)]
    # END: Task Decomposition


def m_decide_trash_upgrade_skip(state: State, server: str, upgrade_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_decide_trash_upgrade_skip(state, server, upgrade_name)

    Method parameters:
        server: Identifier of the server hosting the upgrade
        upgrade_name: Name of the upgrade

    Method purpose:
        Skip paying the upgrade trash cost; the upgrade stays installed.

    Preconditions:
        None

    Task decomposition:
        - (empty) No actions

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(server, str): return False
    if not isinstance(upgrade_name, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions; always available
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    # Setup
    a_install_program, a_install_hardware, a_install_resource,
    # Run flow
    a_initiate_run, a_approach_ice, a_pass_ice, a_end_run,
    # Encounter mechanics
    a_pump_breaker, a_pump_gordian, a_drain_ice_strength,
    a_break_subroutine, a_end_encounter,
    # Subroutine resolution
    a_resolve_end_run, a_resolve_net_damage, a_resolve_lose_click,
    a_resolve_trace, a_take_tag,
    # End-of-encounter cleanup
    a_spend_virus_counter, a_trash_crypsis, a_trash_sacrificial_construct,
    # Access phase
    a_steal_agenda, a_pay_trash_cost, a_fire_ambush, a_trash_program,
)


# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Top-level and run decomposition (single method each)
declare_task_methods('m_steal_agenda', m_steal_agenda)
declare_task_methods('m_run_on_server', m_run_on_server)
declare_task_methods('m_traverse_ice_stack', m_traverse_ice_stack)
declare_task_methods('m_handle_approach', m_handle_approach)
declare_task_methods('m_post_approach', m_post_approach)
declare_task_methods('m_handle_encounter', m_handle_encounter)

# Data Raven on-encounter ability: 2 alternatives (take tag preferred)
declare_task_methods('m_handle_data_raven_on_encounter',
                     m_data_raven_take_tag,
                     m_data_raven_voluntary_end_run)

# Break ice: 8 alternatives in priority order
# Priority: matched breaker > AI breaker, full > partial
declare_task_methods('m_break_ice',
                     m_break_with_corroder_full,
                     m_break_with_gordian_full,
                     m_break_with_wyrm_full,
                     m_break_with_crypsis_full,
                     m_break_with_corroder_partial,
                     m_break_with_gordian_partial,
                     m_break_with_wyrm_partial,
                     m_break_with_crypsis_partial)

# Resolve unbroken subroutines (single method)
declare_task_methods('m_resolve_unbroken_subs', m_resolve_unbroken_subs)

# Crypsis cleanup: 4 alternatives (spend counter > prevent with SC > let trash; skip if not used)
declare_task_methods('m_crypsis_cleanup',
                     m_crypsis_cleanup_spend_counter,
                     m_crypsis_cleanup_prevent_with_sc,
                     m_crypsis_cleanup_let_trash,
                     m_crypsis_cleanup_skip)

# Access methods (single)
declare_task_methods('m_access_server', m_access_server)
declare_task_methods('m_access_one_agenda', m_access_one_agenda)
declare_task_methods('m_access_one_asset', m_access_one_asset)
declare_task_methods('m_access_one_upgrade', m_access_one_upgrade)

# Ambush handling: 2 alternatives (fire preferred when applicable, skip otherwise)
declare_task_methods('m_handle_ambush',
                     m_handle_ambush_fire,
                     m_handle_ambush_skip)

# Trash decisions: 2 alternatives each (pay preferred if affordable, skip otherwise)
declare_task_methods('m_decide_trash_asset',
                     m_decide_trash_asset_pay,
                     m_decide_trash_asset_skip)

declare_task_methods('m_decide_trash_upgrade',
                     m_decide_trash_upgrade_pay,
                     m_decide_trash_upgrade_skip)

# ============================================================================
# END OF FILE
# ============================================================================
