"""
Problem definitions for the Cybersecurity Attack Planning example.
-- Generated 2026-04-14

This file defines 9 scenarios for insider attack planning against a
Document Management System (DMS), based on the BAMS domain. Each scenario
varies network topology, door locks, attacker knowledge, and malware
configuration to exercise different attack paths and backtracking points.

Scenarios:
  - scenario_1_direct_access: Known DMS credentials, ACL granted (8 actions)
  - scenario_2_shoulder_surfing: Physical password observation (11 actions)
  - scenario_3_network_sniffing: Sniff DMS password from hub traffic (10 actions)
  - scenario_4_locked_room_fallback: Locked door blocks surf -> sniff (10 actions)
  - scenario_5_firewall_sniff_blocked: Firewall present, surf succeeds first (11 actions)
  - scenario_6_admin_acl_change: Sniff admin password, modify ACL (12 actions)
  - scenario_7_direct_client_hack: No ACL -> malware relay (6 actions)
  - scenario_8_custom_virus_bypass: Scanner blocks known virus -> custom (6 actions)
  - scenario_9_covert_exfiltration: No ACL, sniff creds, then malware (8 actions)
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
    # Graceful degradation: supports direct problems.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def h_create_base_state(name: str) -> State:
    """Create a base state with all properties initialized to empty defaults."""
    state = State(name)

    # Physical
    state.location = {}
    state.at_host = {}
    state.host_room = {}
    state.door_between = {}
    state.door_open = {}
    state.door_locked = {}

    # People
    state.insider = set()
    state.tech_skill = {}

    # Credentials
    state.knows_password = set()
    state.has_certificate = set()
    state.dms_password_known = set()
    state.admin_password_known = set()

    # Network
    state.is_hub = set()
    state.host_nd = {}
    state.can_reach = set()
    state.firewall_blocks_sniff = set()

    # Sniffer
    state.sniffer_running = set()
    state.sniffable_passwords = set()

    # Process
    state.logged_in = set()
    state.has_shell = set()

    # DMS
    state.dms_session_active = set()
    state.dms_client_found = set()
    state.dms_session_connected = set()
    state.dms_authenticated = set()
    state.dms_read_acl = set()
    state.in_group = {}

    # Admin
    state.nes_admin_on = set()

    # Malware
    state.scanned_host = set()
    state.virus_deployed = set()
    state.code_injected = set()

    # Goal
    state.document_stolen = set()

    return state


def _h_setup_office_layout_1(state: State) -> State:
    """
    Configure the standard BAMS office layout with hub-based network.

    People: Bob (attacker, insider), Adam (admin), Greg (user)
    Hosts: yeti (Bob's), bigfoot (Adam's), sherpa (Greg's), everest (server)
    Rooms: bob_office, greg_office, adam_office, server_room
    Doors: d0 (bob<->greg), d1 (greg<->adam) — both open, unlocked
    Network: hub1 connects all front-office hosts; all can reach everest
    """
    # People
    state.location = {'bob': 'bob_office', 'adam': 'adam_office', 'greg': 'greg_office'}
    state.insider = {'bob'}
    state.tech_skill = {'bob': 'high', 'adam': 'medium', 'greg': 'low'}

    # Hosts
    state.host_room = {
        'yeti': 'bob_office',
        'bigfoot': 'adam_office',
        'sherpa': 'greg_office',
        'everest': 'server_room',
    }

    # Doors (Office Layout 1: bob -- d0 -- greg -- d1 -- adam)
    state.door_between = {
        ('bob_office', 'greg_office'): 'd0',
        ('greg_office', 'adam_office'): 'd1',
    }
    state.door_open = {'d0': True, 'd1': True}
    state.door_locked = {'d0': False, 'd1': False}

    # Network (hub-based — all front-office hosts on hub1)
    state.is_hub = {'hub1'}
    state.host_nd = {
        'yeti': 'hub1',
        'bigfoot': 'hub1',
        'sherpa': 'hub1',
        'everest': 'hub1',
    }
    state.can_reach = {
        ('yeti', 'everest'), ('bigfoot', 'everest'),
        ('sherpa', 'everest'), ('everest', 'yeti'),
        ('everest', 'bigfoot'), ('everest', 'sherpa'),
    }

    # Bob knows his own OS password for yeti
    state.knows_password = {('bob', 'bob', 'yeti')}

    # Group membership
    state.in_group = {
        'bob': {'staff'},
        'adam': {'staff', 'admin'},
        'greg': {'staff'},
    }

    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: cybersecurity_attack_planning

# BEGIN: Scenario: scenario_1_direct_access
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_direct_access')
_h_setup_office_layout_1(initial_state_scenario_1)
# Bob already knows his DMS password
initial_state_scenario_1.dms_password_known = {('bob', 'bob', 'everest')}
# Staff group has read access to the document
initial_state_scenario_1.dms_read_acl = {('secret_doc', 'staff')}

# Problem
problems['scenario_1_direct_access'] = (
    initial_state_scenario_1,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Direct access: known DMS credentials, ACL granted -> 8 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_shoulder_surfing
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_shoulder_surfing')
_h_setup_office_layout_1(initial_state_scenario_2)
# Bob does NOT know DMS password; Greg does
initial_state_scenario_2.dms_password_known = {('greg', 'greg', 'everest')}
# Greg is sitting at his host and logged in
initial_state_scenario_2.at_host = {'greg': 'sherpa'}
initial_state_scenario_2.logged_in = {('greg', 'sherpa')}
initial_state_scenario_2.knows_password.add(('greg', 'greg', 'sherpa'))
# Staff group has read access
initial_state_scenario_2.dms_read_acl = {('secret_doc', 'staff')}

# Problem
problems['scenario_2_shoulder_surfing'] = (
    initial_state_scenario_2,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Shoulder surfing: observe Greg typing password -> 11 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_network_sniffing
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_network_sniffing')
_h_setup_office_layout_1(initial_state_scenario_3)
# No DMS password for Bob; Adam's password transits the hub
initial_state_scenario_3.sniffable_passwords = {('adam', 'everest')}
initial_state_scenario_3.dms_password_known = {('adam', 'adam', 'everest')}
# Staff group has read access
initial_state_scenario_3.dms_read_acl = {('secret_doc', 'staff')}

# Problem
problems['scenario_3_network_sniffing'] = (
    initial_state_scenario_3,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Network sniffing: sniff Adam DMS password from hub -> 10 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_4_locked_room_fallback
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_4 = h_create_base_state('scenario_4_locked_room_fallback')
_h_setup_office_layout_1(initial_state_scenario_4)
# Greg knows DMS password and is at his host
initial_state_scenario_4.dms_password_known = {('greg', 'greg', 'everest')}
initial_state_scenario_4.at_host = {'greg': 'sherpa'}
initial_state_scenario_4.logged_in = {('greg', 'sherpa')}
initial_state_scenario_4.knows_password.add(('greg', 'greg', 'sherpa'))
# LOCKED DOOR: d0 between bob_office and greg_office is locked AND closed
initial_state_scenario_4.door_locked = {'d0': True, 'd1': False}
initial_state_scenario_4.door_open = {'d0': False, 'd1': True}
# Greg's DMS password also transits the hub (sniffing fallback)
initial_state_scenario_4.sniffable_passwords = {('greg', 'everest')}
# Staff group has read access
initial_state_scenario_4.dms_read_acl = {('secret_doc', 'staff')}

# Problem
problems['scenario_4_locked_room_fallback'] = (
    initial_state_scenario_4,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Locked room fallback: door locked -> surf fails -> sniff succeeds'
)
# END: Scenario

# BEGIN: Scenario: scenario_5_firewall_sniff_blocked
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_5 = h_create_base_state('scenario_5_firewall_sniff_blocked')
_h_setup_office_layout_1(initial_state_scenario_5)
# Greg knows DMS password and is at his host (same as S2)
initial_state_scenario_5.dms_password_known = {('greg', 'greg', 'everest')}
initial_state_scenario_5.at_host = {'greg': 'sherpa'}
initial_state_scenario_5.logged_in = {('greg', 'sherpa')}
initial_state_scenario_5.knows_password.add(('greg', 'greg', 'sherpa'))
# Firewall would block sniffing (but surf succeeds first in method ordering)
initial_state_scenario_5.firewall_blocks_sniff = {('yeti', 'everest')}
# Staff group has read access
initial_state_scenario_5.dms_read_acl = {('secret_doc', 'staff')}

# Problem
problems['scenario_5_firewall_sniff_blocked'] = (
    initial_state_scenario_5,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Firewall blocks sniffing: surf succeeds first -> 11 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_6_admin_acl_change
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_6 = h_create_base_state('scenario_6_admin_acl_change')
_h_setup_office_layout_1(initial_state_scenario_6)
# Bob knows his own DMS password (credentials OK)
initial_state_scenario_6.dms_password_known = {('bob', 'bob', 'everest')}
# NO ACL access (empty dms_read_acl)
initial_state_scenario_6.dms_read_acl = set()
# Admin (Adam) password is sniffable; Adam knows the admin password
initial_state_scenario_6.sniffable_passwords = {('adam', 'everest')}
initial_state_scenario_6.admin_password_known = {('adam', 'everest')}

# Problem
problems['scenario_6_admin_acl_change'] = (
    initial_state_scenario_6,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Admin ACL change: sniff admin password, modify ACL -> 12 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_7_direct_client_hack
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_7 = h_create_base_state('scenario_7_direct_client_hack')
_h_setup_office_layout_1(initial_state_scenario_7)
# Bob knows his own DMS password
initial_state_scenario_7.dms_password_known = {('bob', 'bob', 'everest')}
# NO ACL access — document is restricted; no admin credentials available
initial_state_scenario_7.dms_read_acl = set()
# No admin password sniffable (admin path blocked)
# -> Legitimate access fails at document access phase
# -> Backtrack to malware relay (no virus scanner)

# Problem
problems['scenario_7_direct_client_hack'] = (
    initial_state_scenario_7,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Direct client hack: no ACL, no admin -> malware relay'
)
# END: Scenario

# BEGIN: Scenario: scenario_8_custom_virus_bypass
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_8 = h_create_base_state('scenario_8_custom_virus_bypass')
_h_setup_office_layout_1(initial_state_scenario_8)
# Bob knows his own DMS password
initial_state_scenario_8.dms_password_known = {('bob', 'bob', 'everest')}
# NO ACL access, no admin path -> legitimate fails -> malware
initial_state_scenario_8.dms_read_acl = set()
# Virus scanner on Bob's host -> known virus fails -> custom virus
initial_state_scenario_8.scanned_host = {'yeti'}

# Problem
problems['scenario_8_custom_virus_bypass'] = (
    initial_state_scenario_8,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Custom virus bypass: scanner blocks known virus -> custom virus'
)
# END: Scenario

# BEGIN: Scenario: scenario_9_covert_exfiltration
# Configuration
_attacker = 'bob'
_document = 'secret_doc'
_server = 'everest'

# State
initial_state_scenario_9 = h_create_base_state('scenario_9_covert_exfiltration')
_h_setup_office_layout_1(initial_state_scenario_9)
# Bob does NOT know DMS password; Adam's password is sniffable
initial_state_scenario_9.sniffable_passwords = {('adam', 'everest')}
initial_state_scenario_9.dms_password_known = {('adam', 'adam', 'everest')}
# NO ACL access, no admin path -> legitimate fails -> malware
initial_state_scenario_9.dms_read_acl = set()

# Problem
problems['scenario_9_covert_exfiltration'] = (
    initial_state_scenario_9,
    [('m_steal_secret_document', _attacker, _document, _server)],
    'Covert exfiltration: sniff creds, no ACL -> malware relay'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.cybersecurity_attack_planning import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    9

    Scenario 1 — Direct access: known credentials, ACL granted (8 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(*probs['scenario_1_direct_access'][:2])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 8)
    >>> r1.plan[0][0]
    'a_sit_at_host'
    >>> r1.plan[-1][0]
    'a_dms_request_and_read'

    Scenario 2 — Shoulder surfing: observe Greg typing password (11 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(*probs['scenario_2_shoulder_surfing'][:2])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 11)
    >>> r2.plan[1][0]
    'a_shoulder_surf'

    Scenario 3 — Network sniffing: sniff Adam's DMS password from hub (10 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(*probs['scenario_3_network_sniffing'][:2])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 10)
    >>> r3.plan[4][0]
    'a_read_sniffer'

    Scenario 4 — Locked room fallback: door locked, surf fails, sniff succeeds
    (10 actions). Greedy fails because a_open_door fails on the locked door.

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r4 = s.find_plan(*probs['scenario_4_locked_room_fallback'][:2])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 10)
    >>> 'a_read_sniffer' in [a[0] for a in r4.plan]
    True
    >>> 'a_shoulder_surf' in [a[0] for a in r4.plan]
    False

    Greedy fails on scenario 4 (commits to shoulder surf, door is locked).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g4 = s.find_plan(*probs['scenario_4_locked_room_fallback'][:2])
    >>> sys.stdout = _o
    >>> g4.success
    False

    Scenario 5 — Firewall blocks sniffing but surf succeeds first (11 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r5 = s.find_plan(*probs['scenario_5_firewall_sniff_blocked'][:2])
    >>> sys.stdout = _o
    >>> r5.success, len(r5.plan)
    (True, 11)
    >>> r5.plan[1][0]
    'a_shoulder_surf'

    Scenario 6 — Admin ACL change: sniff admin password, modify ACL (12 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r6 = s.find_plan(*probs['scenario_6_admin_acl_change'][:2])
    >>> sys.stdout = _o
    >>> r6.success, len(r6.plan)
    (True, 12)
    >>> 'a_nes_admin_login' in [a[0] for a in r6.plan]
    True
    >>> 'a_dms_group_allow' in [a[0] for a in r6.plan]
    True

    Scenario 7 — Direct client hack: no ACL -> malware relay (6 actions).
    Greedy fails (commits to legitimate DMS path which has no ACL).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r7 = s.find_plan(*probs['scenario_7_direct_client_hack'][:2])
    >>> sys.stdout = _o
    >>> r7.success, len(r7.plan)
    (True, 6)
    >>> r7.plan[-1][0]
    'a_relay_document'

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g7 = s.find_plan(*probs['scenario_7_direct_client_hack'][:2])
    >>> sys.stdout = _o
    >>> g7.success
    False

    Scenario 8 — Custom virus bypass: scanner blocks known virus -> custom
    (6 actions). Greedy fails (double backtracking: legit->malware, then
    known_virus->custom_virus).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r8 = s.find_plan(*probs['scenario_8_custom_virus_bypass'][:2])
    >>> sys.stdout = _o
    >>> r8.success, len(r8.plan)
    (True, 6)
    >>> r8.plan[3][0]
    'a_write_custom_virus'

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g8 = s.find_plan(*probs['scenario_8_custom_virus_bypass'][:2])
    >>> sys.stdout = _o
    >>> g8.success
    False

    Scenario 9 — Covert exfiltration: sniff creds, no ACL -> malware (8 actions).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0, strategy='iterative_dfs_backtracking') as s:
    ...     r9 = s.find_plan(*probs['scenario_9_covert_exfiltration'][:2])
    >>> sys.stdout = _o
    >>> r9.success, len(r9.plan)
    (True, 8)
    >>> 'a_read_sniffer' in [a[0] for a in r9.plan]
    True
    >>> r9.plan[-1][0]
    'a_relay_document'

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as s:
    ...     g9 = s.find_plan(*probs['scenario_9_covert_exfiltration'][:2])
    >>> sys.stdout = _o
    >>> g9.success
    False

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
