"""
Problem definitions for the Android: Netrunner Run Planning example.
-- Generated 2026-05-15

This file defines 8 scenarios for Runner-side single-run planning. The Runner
attempts to steal a target agenda from a Corporation server with a configured
ice stack and per-scenario Corp policy. The flagship scenario faithfully
replicates the worked run example on page 19 of the core rulebook.

Scenarios:
  - scenario_1_empty_server_walk_in: No ice, trivial run (3 actions)
  - scenario_2_single_barrier_corroder: One Ice Wall, Corroder break (6 actions)
  - scenario_3_rulebook_run_example: p.19 replication, greedy fails (13 actions)
  - scenario_4_sentry_needs_ai_fallback: Sentry needs Crypsis fallback (9 actions)
  - scenario_5_wyrm_drain_path: Only Wyrm available, drain mechanic (9 actions)
  - scenario_6_accept_net_damage_to_save_credits: 2-ice run, greedy fails (11 actions)
  - scenario_7_crypsis_no_sc_must_trash: Crypsis cleanup falls to trash (8 actions)
  - scenario_8_ambush_secretary_showcase: Aggressive Secretary ambush (9 actions)

Note on plan lengths: GTPyhop elides idempotent (no-state-change) actions from
the returned plan. In scenario 3, a_pass_ice (Ice Wall not rezzed) and
a_resolve_lose_click (Runner has 0 clicks) are no-ops and do not appear in
result.plan, so the action count is 13 rather than the 15 a literal reading
of the rulebook narrative would suggest.
"""

import sys
import os
from typing import Dict, Tuple, List

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def h_create_base_state(name: str) -> State:
    """Create a base state with all properties initialized to empty defaults."""
    state = State(name)

    # Persistent Runner state
    state.runner_credits = 0
    state.runner_clicks = 0
    state.grip_count = 5
    state.heap_count = 0
    state.mu_available = 4
    state.tags = 0
    state.brain_damage = 0
    state.installed_programs = {}
    state.installed_hardware = {}
    state.installed_resources = {}
    state.toolbox_recurring = 0
    state.virus_counters = {}
    state.agenda_points_runner = 0
    state.flatlined = False

    # Corp configuration
    state.corp_identity = 'none'
    state.corp_credits = 0
    state.servers = {}
    state.ice_rezzed = {}
    state.ice_advancement = {}
    state.upgrade_rezzed = {}
    state.agenda_advancement = {}
    state.corp_policy = {
        'rez_plan': {},
        'ambush_fire': {},
        'trace_budget': {},
        'ambush_trash_targets': {},
    }

    # Run-scoped and encounter-scoped state
    state.current_run = None
    state.current_encounter = None

    # Scenario target
    state.scenario_target_agenda = ('remote_1', 0)
    state.scenario_target_points = 2

    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: android_netrunner

# BEGIN: Scenario: scenario_1_empty_server_walk_in
# Configuration
_server = 'remote_1'
_target = ('remote_1', 0)

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_empty_server_walk_in')
initial_state_scenario_1.runner_credits = 5
initial_state_scenario_1.runner_clicks = 1
initial_state_scenario_1.servers = {
    'remote_1': {
        'ice': [],
        'contents': ['astroscript'],
        'upgrades': [],
    }
}
initial_state_scenario_1.scenario_target_agenda = _target

# Problem
problems['scenario_1_empty_server_walk_in'] = (
    initial_state_scenario_1,
    [('m_steal_agenda', _target)],
    'Empty server walk-in: no ice, immediate access -> 3 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_single_barrier_corroder
# Configuration
_server = 'remote_1'
_target = ('remote_1', 0)

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_single_barrier_corroder')
initial_state_scenario_2.runner_credits = 5
initial_state_scenario_2.runner_clicks = 1
initial_state_scenario_2.installed_programs = {'corroder': True}
initial_state_scenario_2.mu_available = 3  # 4 - 1 (Corroder)
initial_state_scenario_2.corp_credits = 5
initial_state_scenario_2.servers = {
    'remote_1': {
        'ice': ['ice_wall'],
        'contents': ['astroscript'],
        'upgrades': [],
    }
}
initial_state_scenario_2.ice_rezzed = {('remote_1', 0): False}
initial_state_scenario_2.corp_policy['rez_plan'] = {
    ('remote_1', 0, 'ice'): True,
}
initial_state_scenario_2.scenario_target_agenda = _target

# Problem
problems['scenario_2_single_barrier_corroder'] = (
    initial_state_scenario_2,
    [('m_steal_agenda', _target)],
    'Single barrier Ice Wall, broken by Corroder -> 6 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_rulebook_run_example
# Configuration: replicates the worked example on page 19 of the core rulebook.
# Runner (Bart): Gordian Blade, Crypsis, Sacrificial Construct, The Toolbox installed.
# Pool: 5 credits + 2 recurring on Toolbox. Last click of turn (clicks=1, decremented by run).
# Corp (Olivia, Jinteki Personal Evolution): 7 credits.
# Server: Enigma (rezzed) -> Ice Wall (unrezzed, Corp will not rez) -> Wall of Thorns
#         (unrezzed, Corp will rez when approached, with Akitaro discount).
# Server root: Akitaro Watanabe (unrezzed, Corp will rez before Wall of Thorns).
# Server contents: Nisei MK II agenda (1 advancement counter).
_server = 'remote_1'
_target = ('remote_1', 0)

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_rulebook_run_example')
initial_state_scenario_3.runner_credits = 5
initial_state_scenario_3.runner_clicks = 1
initial_state_scenario_3.grip_count = 5
initial_state_scenario_3.installed_programs = {'gordian_blade': True, 'crypsis': True}
initial_state_scenario_3.installed_hardware = {'the_toolbox': True}
initial_state_scenario_3.installed_resources = {'sacrificial_construct': True}
initial_state_scenario_3.toolbox_recurring = 2
# MU: base 4 + Toolbox bonus 2 = 6, minus Gordian 1, Crypsis 1 = 4 available
initial_state_scenario_3.mu_available = 4
initial_state_scenario_3.virus_counters = {'crypsis': 0}
initial_state_scenario_3.corp_identity = 'jinteki_personal_evolution'
initial_state_scenario_3.corp_credits = 7
initial_state_scenario_3.servers = {
    'remote_1': {
        'ice': ['enigma', 'ice_wall', 'wall_of_thorns'],
        'contents': ['nisei_mk_ii'],
        'upgrades': ['akitaro_watanabe'],
    }
}
# Enigma initially rezzed (per rulebook narrative); other ice initially unrezzed.
initial_state_scenario_3.ice_rezzed = {
    ('remote_1', 0): True,
    ('remote_1', 1): False,
    ('remote_1', 2): False,
}
# Nisei MK II has 1 advancement counter on it at start (per rulebook image).
initial_state_scenario_3.agenda_advancement = {('remote_1', 'nisei_mk_ii'): 1}
initial_state_scenario_3.upgrade_rezzed = {('remote_1', 0): False}
# Corp policy: rez Akitaro AND Wall of Thorns at approach to ice #2.
initial_state_scenario_3.corp_policy['rez_plan'] = {
    ('remote_1', 2, 'upgrade', 0): True,
    ('remote_1', 2, 'ice'): True,
}
initial_state_scenario_3.scenario_target_agenda = _target

# Problem
problems['scenario_3_rulebook_run_example'] = (
    initial_state_scenario_3,
    [('m_steal_agenda', _target)],
    'Rulebook p.19 replication: Enigma + Ice Wall + Wall of Thorns; Jinteki PE; '
    'partial breaks via Gordian and Crypsis; Sacrificial Construct saves Crypsis '
    '-> 13 actions (greedy FAILS, requires backtracking; idempotent no-ops elided)'
)
# END: Scenario

# BEGIN: Scenario: scenario_4_sentry_needs_ai_fallback
# Configuration: A sentry-subtype ice (Data Raven) is approached. Corroder and
# Gordian don't match sentry subtype, so the planner falls back to Crypsis (AI).
# Data Raven's on-encounter ability fires (take 1 tag); its trace subroutine is
# then broken by Crypsis. No Sacrificial Construct, so Crypsis is trashed at the
# end of the encounter.
_server = 'remote_1'
_target = ('remote_1', 0)

# State
initial_state_scenario_4 = h_create_base_state('scenario_4_sentry_needs_ai_fallback')
initial_state_scenario_4.runner_credits = 10
initial_state_scenario_4.runner_clicks = 1
initial_state_scenario_4.installed_programs = {'corroder': True, 'crypsis': True}
initial_state_scenario_4.mu_available = 2  # 4 - 1 Corroder - 1 Crypsis
initial_state_scenario_4.virus_counters = {'crypsis': 0}
initial_state_scenario_4.corp_credits = 5
initial_state_scenario_4.servers = {
    'remote_1': {
        'ice': ['data_raven'],
        'contents': ['astroscript'],
        'upgrades': [],
    }
}
initial_state_scenario_4.ice_rezzed = {('remote_1', 0): False}
initial_state_scenario_4.corp_policy['rez_plan'] = {
    ('remote_1', 0, 'ice'): True,
}
initial_state_scenario_4.scenario_target_agenda = _target

# Problem
problems['scenario_4_sentry_needs_ai_fallback'] = (
    initial_state_scenario_4,
    [('m_steal_agenda', _target)],
    'Sentry needs AI fallback: Data Raven; Crypsis breaks the trace -> 9 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_5_wyrm_drain_path
# Configuration: Only Wyrm installed against Wall of Thorns. Wyrm requires its
# break-predicate (ice strength <= 0), so it must pump up to ice strength to
# interact, then drain ice strength to zero, then break each subroutine.
# Showcases the Wyrm-specific drain mechanic.
_server = 'remote_1'
_target = ('remote_1', 0)

# State
initial_state_scenario_5 = h_create_base_state('scenario_5_wyrm_drain_path')
initial_state_scenario_5.runner_credits = 15  # pump 4 + drain 5 + 2 breaks (6) = 15
initial_state_scenario_5.runner_clicks = 1
initial_state_scenario_5.installed_programs = {'wyrm': True}
initial_state_scenario_5.mu_available = 3  # 4 - 1 Wyrm
initial_state_scenario_5.corp_credits = 10
initial_state_scenario_5.servers = {
    'remote_1': {
        'ice': ['wall_of_thorns'],
        'contents': ['astroscript'],
        'upgrades': [],
    }
}
initial_state_scenario_5.ice_rezzed = {('remote_1', 0): False}
initial_state_scenario_5.corp_policy['rez_plan'] = {
    ('remote_1', 0, 'ice'): True,
}
initial_state_scenario_5.scenario_target_agenda = _target

# Problem
problems['scenario_5_wyrm_drain_path'] = (
    initial_state_scenario_5,
    [('m_steal_agenda', _target)],
    'Wyrm drain path: pump + drain + break both subs on Wall of Thorns -> 9 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_6_accept_net_damage_to_save_credits
# Configuration: 2-ice run (Wall of Thorns then Enigma). Runner has 5 credits,
# Corroder, and Gordian Blade. Greedy breaks both subs on Wall of Thorns
# (4+1 = 5 credits) and runs out for Enigma; backtracking does partial at
# Wall of Thorns (4 credits, take 2 net damage), leaving 1 credit to partial
# Enigma.
_server = 'remote_1'
_target = ('remote_1', 0)

# State
initial_state_scenario_6 = h_create_base_state('scenario_6_accept_net_damage_to_save_credits')
initial_state_scenario_6.runner_credits = 5
initial_state_scenario_6.runner_clicks = 1
initial_state_scenario_6.grip_count = 5
initial_state_scenario_6.installed_programs = {'corroder': True, 'gordian_blade': True}
initial_state_scenario_6.mu_available = 2  # 4 - 1 - 1
initial_state_scenario_6.corp_credits = 15
initial_state_scenario_6.servers = {
    'remote_1': {
        'ice': ['wall_of_thorns', 'enigma'],
        'contents': ['astroscript'],
        'upgrades': [],
    }
}
initial_state_scenario_6.ice_rezzed = {
    ('remote_1', 0): False,
    ('remote_1', 1): False,
}
initial_state_scenario_6.corp_policy['rez_plan'] = {
    ('remote_1', 0, 'ice'): True,
    ('remote_1', 1, 'ice'): True,
}
initial_state_scenario_6.scenario_target_agenda = _target

# Problem
problems['scenario_6_accept_net_damage_to_save_credits'] = (
    initial_state_scenario_6,
    [('m_steal_agenda', _target)],
    'Accept net damage: partial Wall of Thorns + partial Enigma '
    '-> 11 actions (greedy FAILS)'
)
# END: Scenario

# BEGIN: Scenario: scenario_7_crypsis_no_sc_must_trash
# Configuration: Crypsis is the only icebreaker; no Sacrificial Construct, no
# virus counters. After Crypsis breaks the ice, end-of-encounter cleanup
# exhausts both counter-spend and SC alternatives and falls through to
# trashing Crypsis. Crypsis is lost but the ice was already broken.
_server = 'remote_1'
_target = ('remote_1', 0)

# State
initial_state_scenario_7 = h_create_base_state('scenario_7_crypsis_no_sc_must_trash')
initial_state_scenario_7.runner_credits = 5
initial_state_scenario_7.runner_clicks = 1
initial_state_scenario_7.installed_programs = {'crypsis': True}
initial_state_scenario_7.mu_available = 3  # 4 - 1 Crypsis
initial_state_scenario_7.virus_counters = {'crypsis': 0}
initial_state_scenario_7.corp_credits = 5
initial_state_scenario_7.servers = {
    'remote_1': {
        'ice': ['ice_wall'],
        'contents': ['astroscript'],
        'upgrades': [],
    }
}
initial_state_scenario_7.ice_rezzed = {('remote_1', 0): False}
initial_state_scenario_7.corp_policy['rez_plan'] = {
    ('remote_1', 0, 'ice'): True,
}
initial_state_scenario_7.scenario_target_agenda = _target

# Problem
problems['scenario_7_crypsis_no_sc_must_trash'] = (
    initial_state_scenario_7,
    [('m_steal_agenda', _target)],
    'Crypsis no SC must trash: cleanup chain falls to a_trash_crypsis -> 8 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_8_ambush_secretary_showcase
# Configuration: Showcases the Aggressive Secretary ambush card. The Runner
# steals the target agenda, then accesses Aggressive Secretary (1 advancement
# counter); the Corp fires the ambush (paying 2 credits), trashing the
# Runner's Corroder (per ambush priority). The Runner then pays the (zero)
# trash cost and removes the asset.
_server = 'remote_1'
_target = ('remote_1', 0)

# State
initial_state_scenario_8 = h_create_base_state('scenario_8_ambush_secretary_showcase')
initial_state_scenario_8.runner_credits = 8
initial_state_scenario_8.runner_clicks = 1
initial_state_scenario_8.installed_programs = {'corroder': True, 'crypsis': True}
initial_state_scenario_8.mu_available = 2
initial_state_scenario_8.virus_counters = {'crypsis': 0}
initial_state_scenario_8.corp_credits = 5
initial_state_scenario_8.servers = {
    'remote_1': {
        'ice': ['ice_wall'],
        'contents': ['astroscript', 'aggressive_secretary'],
        'upgrades': [],
    }
}
# 1 advancement token on Aggressive Secretary
initial_state_scenario_8.agenda_advancement = {('remote_1', 'aggressive_secretary'): 1}
initial_state_scenario_8.ice_rezzed = {('remote_1', 0): False}
initial_state_scenario_8.corp_policy['rez_plan'] = {
    ('remote_1', 0, 'ice'): True,
}
initial_state_scenario_8.corp_policy['ambush_fire'] = {
    'aggressive_secretary': True,
}
initial_state_scenario_8.corp_policy['ambush_trash_targets'] = {
    'aggressive_secretary': ['corroder'],
}
initial_state_scenario_8.scenario_target_agenda = _target

# Problem
problems['scenario_8_ambush_secretary_showcase'] = (
    initial_state_scenario_8,
    [('m_steal_agenda', _target)],
    'Aggressive Secretary ambush: steal agenda, ambush trashes Corroder -> 9 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.android_netrunner import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    8

    Scenario 1 - Empty server walk-in (3 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_empty_server_walk_in'][0]),
    ...                      probs['scenario_1_empty_server_walk_in'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 3)
    >>> r1.plan[0][0]
    'a_initiate_run'
    >>> r1.plan[1][0]
    'a_steal_agenda'

    Scenario 2 - Single barrier Ice Wall broken by Corroder (6 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_single_barrier_corroder'][0]),
    ...                      probs['scenario_2_single_barrier_corroder'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 6)
    >>> r2.plan[2]
    ('a_break_subroutine', 'corroder', 0)

    Scenario 3 - Rulebook p.19 replication (13 actions; greedy FAILS).
    Bart's run: partial-break Enigma with Gordian, pass Ice Wall, pump-and-partial
    Wall of Thorns with Crypsis, save Crypsis with Sacrificial Construct, steal
    Nisei MK II (Jinteki PE does 1 net damage on steal).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_rulebook_run_example'][0]),
    ...                      probs['scenario_3_rulebook_run_example'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 13)
    >>> ('a_break_subroutine', 'gordian_blade', 1) in r3.plan
    True
    >>> ('a_pump_breaker', 'crypsis', 5) in r3.plan
    True
    >>> ('a_trash_sacrificial_construct',) in r3.plan
    True
    >>> ('a_steal_agenda', 'nisei_mk_ii') in r3.plan
    True

    Greedy fails on scenario 3 (commits to full break of Enigma, runs out of
    credits at Wall of Thorns).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g3 = s.find_plan(copy.deepcopy(probs['scenario_3_rulebook_run_example'][0]),
    ...                      probs['scenario_3_rulebook_run_example'][1])
    >>> sys.stdout = _o
    >>> g3.success
    False

    Scenario 4 - Sentry needs AI fallback: Data Raven; Crypsis breaks the trace
    (9 actions). Corroder fails subtype match; Crypsis is picked as AI fallback.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r4 = s.find_plan(copy.deepcopy(probs['scenario_4_sentry_needs_ai_fallback'][0]),
    ...                      probs['scenario_4_sentry_needs_ai_fallback'][1])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 9)
    >>> ('a_take_tag',) in r4.plan
    True
    >>> ('a_pump_breaker', 'crypsis', 4) in r4.plan
    True
    >>> ('a_break_subroutine', 'crypsis', 0) in r4.plan
    True

    Scenario 5 - Wyrm drain path: only Wyrm installed against Wall of Thorns
    (9 actions). Pump Wyrm to ice strength, drain ice to zero, then break.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r5 = s.find_plan(copy.deepcopy(probs['scenario_5_wyrm_drain_path'][0]),
    ...                      probs['scenario_5_wyrm_drain_path'][1])
    >>> sys.stdout = _o
    >>> r5.success, len(r5.plan)
    (True, 9)
    >>> ('a_pump_breaker', 'wyrm', 4) in r5.plan
    True
    >>> ('a_drain_ice_strength', 5) in r5.plan
    True

    Scenario 6 - Accept net damage to save credits (11 actions; greedy FAILS).
    Greedy fully breaks Wall of Thorns, runs out for Enigma; backtracking does
    partial Wall of Thorns (takes 2 net damage) + partial Enigma.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r6 = s.find_plan(copy.deepcopy(probs['scenario_6_accept_net_damage_to_save_credits'][0]),
    ...                      probs['scenario_6_accept_net_damage_to_save_credits'][1])
    >>> sys.stdout = _o
    >>> r6.success, len(r6.plan)
    (True, 11)
    >>> ('a_resolve_net_damage', 2) in r6.plan
    True
    >>> ('a_break_subroutine', 'corroder', 1) in r6.plan
    True
    >>> ('a_break_subroutine', 'gordian_blade', 1) in r6.plan
    True

    Greedy fails on scenario 6.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g6 = s.find_plan(copy.deepcopy(probs['scenario_6_accept_net_damage_to_save_credits'][0]),
    ...                      probs['scenario_6_accept_net_damage_to_save_credits'][1])
    >>> sys.stdout = _o
    >>> g6.success
    False

    Scenario 7 - Crypsis used, no Sacrificial Construct, no virus counters:
    cleanup chain falls through to trash Crypsis (8 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r7 = s.find_plan(copy.deepcopy(probs['scenario_7_crypsis_no_sc_must_trash'][0]),
    ...                      probs['scenario_7_crypsis_no_sc_must_trash'][1])
    >>> sys.stdout = _o
    >>> r7.success, len(r7.plan)
    (True, 8)
    >>> ('a_trash_crypsis',) in r7.plan
    True

    Scenario 8 - Aggressive Secretary ambush showcase (9 actions). Agenda is
    accessed first and stolen; then the ambush fires on access of the asset,
    trashing Corroder per Corp policy.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r8 = s.find_plan(copy.deepcopy(probs['scenario_8_ambush_secretary_showcase'][0]),
    ...                      probs['scenario_8_ambush_secretary_showcase'][1])
    >>> sys.stdout = _o
    >>> r8.success, len(r8.plan)
    (True, 9)
    >>> ('a_fire_ambush', 'aggressive_secretary') in r8.plan
    True
    >>> ('a_trash_program', 'corroder') in r8.plan
    True

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
