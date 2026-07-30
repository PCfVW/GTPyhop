# ============================================================================
# Cybersecurity Attack Planning HTN Domain
# Based on the BAMS (Behavioral Adversary Modeling System)
# ============================================================================
#
# MOTIVATION:
# Models insider attacks against a network with a Document Management System
# (DMS), based on the BAMS domain from Boddy et al. (ICAPS 2005) and the
# hierarchy design by Pragst (2013/2014). A malicious insider (Bob) attempts
# to steal a secret document from a DMS server using combinations of physical,
# cyber, and malware attacks. This is a defensive tool: generated attack plans
# help network administrators identify vulnerabilities.
#
# ARCHITECTURE:
# The top-level task m_steal_secret_document decomposes into two alternative
# attack strategies (legitimate DMS access vs. covert malware relay), each
# with sub-phases that offer further alternatives. The planner backtracks
# across these alternatives when countermeasures block a path.
#
# SUPPORTED ATTACK PATHS:
# - Legitimate DMS access: credential theft + system access + ACL check + DMS
# - Covert malware relay: credential theft + system access + virus + inject
#
# MODULES:
# Physical (5 actions), Process (4), Network (2), DMS (6), Malware (4)
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - State Property Map
#   - Helper Functions
#   - Actions (21)
#   - Methods (16)
#   - Registration
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple, Set

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

the_domain = Domain("cybersecurity_attack_planning")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (BAMS Insider Attack Planning)
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#  - [CONFIG]  Set at scenario creation, not modified by actions
#
# Physical World:
#  location: dict {person: room}                     (E/P) [DATA]
#  at_host: dict {person: host or None}              (E/P) [ENABLER]
#  host_room: dict {host: room}                      (P)   [CONFIG]
#  door_between: dict {(room1,room2): door}          (P)   [CONFIG]
#  door_open: dict {door: bool}                      (E/P) [ENABLER]
#  door_locked: dict {door: bool}                    (P)   [CONFIG]
#
# People:
#  insider: set {person}                             (P)   [CONFIG]
#  tech_skill: dict {person: level}                  (P)   [CONFIG]
#
# Credentials:
#  knows_password: set {(person, uid, host)}         (E/P) [DATA]
#  has_certificate: set {(uid, host)}                (P)   [CONFIG]
#  dms_password_known: set {(person, uid, server)}   (E/P) [DATA]
#  admin_password_known: set {(person, server)}      (E/P) [DATA]
#
# Network:
#  is_hub: set {device}                              (P)   [CONFIG]
#  host_nd: dict {host: device}                      (P)   [CONFIG]
#  can_reach: set {(host1, host2)}                   (P)   [CONFIG]
#  firewall_blocks_sniff: set {(host1, host2)}       (P)   [CONFIG]
#
# Sniffer:
#  sniffer_running: set {host}                       (E/P) [ENABLER]
#  sniffable_passwords: set {(uid, server)}          (P)   [CONFIG]
#
# Process:
#  logged_in: set {(uid, host)}                      (E/P) [ENABLER]
#  has_shell: set {(uid, host)}                      (E/P) [ENABLER]
#
# DMS:
#  dms_session_active: set {(uid, server)}           (E/P) [ENABLER]
#  dms_client_found: set {(uid, server)}             (E/P) [ENABLER]
#  dms_session_connected: set {(uid, server)}        (E/P) [ENABLER]
#  dms_authenticated: set {(uid, server)}            (E/P) [ENABLER]
#  dms_read_acl: set {(doc, id)}                     (E/P) [DATA]
#  in_group: dict {uid: set of gids}                 (P)   [CONFIG]
#
# Admin:
#  nes_admin_on: set {(uid, server)}                 (E/P) [ENABLER]
#
# Malware:
#  scanned_host: set {host}                          (P)   [CONFIG]
#  virus_deployed: set {host}                        (E/P) [DATA]
#  code_injected: set {(client, server)}             (E/P) [DATA]
#
# Goal:
#  document_stolen: set {(person, doc)}              (E)   [DATA]
# ============================================================================


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _h_find_door(state: State, room1: str, room2: str) -> Optional[str]:
    """Find a door between two rooms, checking both orderings."""
    door = state.door_between.get((room1, room2))
    if door is None:
        door = state.door_between.get((room2, room1))
    return door


def _h_attacker_host(state: State, attacker: str) -> Optional[str]:
    """Find the attacker's own host (the host in their room)."""
    room = state.location.get(attacker)
    if room is None:
        return None
    for host, host_room in state.host_room.items():
        if host_room == room:
            return host
    return None


def _h_has_acl(state: State, document: str, uid: str) -> bool:
    """Check if uid (directly or via group) has read ACL on document."""
    if (document, uid) in state.dms_read_acl:
        return True
    for gid in state.in_group.get(uid, set()):
        if (document, gid) in state.dms_read_acl:
            return True
    return False


# ============================================================================
# ACTIONS (21)
# ============================================================================

# ----------------------------------------------------------------------------
# Physical Actions (5)
# ----------------------------------------------------------------------------

def a_move_to_room(state: State, person: str, from_room: str, to_room: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_move_to_room(state, person, from_room, to_room)

    Action parameters:
        person: The person moving between rooms
        from_room: The room the person is currently in
        to_room: The room the person is moving to

    Action purpose:
        Move a person from one room to an adjacent room through a door

    Preconditions:
        - Person is in from_room (state.location[person] == from_room)
        - A door exists between the rooms (state.door_between)
        - The door is open (state.door_open[door])
        - Person is not sitting at a host (state.at_host)

    Effects:
        - Person is now in to_room (state.location[person]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(from_room, str): return False
    if not isinstance(to_room, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.location.get(person) != from_room:
        return False
    door = _h_find_door(state, from_room, to_room)
    if door is None:
        return False
    if not state.door_open.get(door, False):
        return False
    if state.at_host.get(person) is not None:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Person moves to new room
    state.location[person] = to_room
    # END: Effects

    return state


def a_sit_at_host(state: State, person: str, host: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_sit_at_host(state, person, host)

    Action parameters:
        person: The person sitting down at the computer
        host: The computer to sit at

    Action purpose:
        Sit at a computer host in the current room

    Preconditions:
        - Person is in the same room as the host (state.location, state.host_room)
        - Person is not already at a host (state.at_host)

    Effects:
        - Person is now at the host (state.at_host[person]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.location.get(person) != state.host_room.get(host):
        return False
    if state.at_host.get(person) is not None:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Person is now at the computer
    state.at_host[person] = host
    # END: Effects

    return state


def a_leave_host(state: State, person: str, host: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_leave_host(state, person, host)

    Action parameters:
        person: The person leaving the computer
        host: The computer to leave

    Action purpose:
        Get up from a computer host

    Preconditions:
        - Person is at the specified host (state.at_host[person] == host)

    Effects:
        - Person is no longer at any host (state.at_host[person]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.at_host.get(person) != host:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Person is no longer at the computer
    state.at_host[person] = None
    # END: Effects

    return state


def a_open_door(state: State, person: str, door: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_open_door(state, person, door)

    Action parameters:
        person: The person opening the door
        door: The door to open

    Action purpose:
        Open a closed, unlocked door adjacent to the person's room

    Preconditions:
        - Person is in a room adjacent to the door (state.door_between)
        - Door is not locked (state.door_locked[door] == False)
        - Door is currently closed (state.door_open[door] == False)

    Effects:
        - Door is now open (state.door_open[door]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(door, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    person_room = state.location.get(person)
    adjacent = False
    for (r1, r2), d in state.door_between.items():
        if d == door and (r1 == person_room or r2 == person_room):
            adjacent = True
            break
    if not adjacent:
        return False
    if state.door_locked.get(door, False):
        return False
    if state.door_open.get(door, False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Door is now open
    state.door_open[door] = True
    # END: Effects

    return state


def a_shoulder_surf(state: State, observer: str, victim: str, host: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_shoulder_surf(state, observer, victim, host)

    Action parameters:
        observer: The attacker observing the password
        victim: The person whose password is being observed
        host: The host the victim is typing at

    Action purpose:
        Observe a victim typing their password at a computer

    Preconditions:
        - Observer and victim are in the same room (state.location)
        - Victim is at the specified host (state.at_host[victim] == host)
        - Observer is not the victim
        - Victim is logged in at the host (state.logged_in)

    Effects:
        - Observer learns all passwords the victim knows for this host
          (state.knows_password, state.dms_password_known) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(observer, str): return False
    if not isinstance(victim, str): return False
    if not isinstance(host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if observer == victim:
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.location.get(observer) != state.location.get(victim):
        return False
    if state.at_host.get(victim) != host:
        return False
    victim_logged_in = False
    for (uid, h) in state.logged_in:
        if h == host:
            victim_logged_in = True
            break
    if not victim_logged_in:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Observer learns victim's OS passwords for this host
    for (p, uid, h) in list(state.knows_password):
        if p == victim and h == host:
            state.knows_password.add((observer, uid, h))
    # [DATA] Observer learns victim's DMS passwords
    for (p, uid, srv) in list(state.dms_password_known):
        if p == victim:
            state.dms_password_known.add((observer, uid, srv))
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# Process Actions (4)
# ----------------------------------------------------------------------------

def a_login(state: State, person: str, uid: str, host: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_login(state, person, uid, host)

    Action parameters:
        person: The person logging in
        uid: The user ID to log in as
        host: The host to log in to

    Action purpose:
        Log in to a host with a known password (combines ENTER_UNAME + ENTER_PASSWORD)

    Preconditions:
        - Person is at the host (state.at_host[person] == host)
        - Person knows the password for uid@host (state.knows_password)

    Effects:
        - uid is logged in on host (state.logged_in) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.at_host.get(person) != host:
        return False
    if (person, uid, host) not in state.knows_password:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] User is now logged in
    state.logged_in.add((uid, host))
    # END: Effects

    return state


def a_launch_shell(state: State, person: str, uid: str, host: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_launch_shell(state, person, uid, host)

    Action parameters:
        person: The person launching the shell
        uid: The user ID for the shell session
        host: The host to launch the shell on

    Action purpose:
        Launch a shell session on a host where the user is logged in

    Preconditions:
        - uid is logged in on host (state.logged_in)
        - Person is at the host (state.at_host)

    Effects:
        - uid has a shell on host (state.has_shell) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, host) not in state.logged_in:
        return False
    if state.at_host.get(person) != host:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Shell session active
    state.has_shell.add((uid, host))
    # END: Effects

    return state


def a_nes_admin_login(state: State, person: str, uid: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_nes_admin_login(state, person, uid, server)

    Action parameters:
        person: The person logging in as NES admin
        uid: The user ID for the admin session
        server: The DMS server to administrate

    Action purpose:
        Log in to the NES admin interface on the DMS server

    Preconditions:
        - Person has a shell on some host (state.has_shell)
        - Person knows the admin password for the server (state.admin_password_known)

    Effects:
        - Admin session is active on server (state.nes_admin_on) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    has_any_shell = any(u == uid for (u, h) in state.has_shell)
    if not has_any_shell:
        return False
    if (person, server) not in state.admin_password_known:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Admin session active
    state.nes_admin_on.add((uid, server))
    # END: Effects

    return state


def a_dms_group_allow(state: State, person: str, uid: str, document: str, group_id: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_dms_group_allow(state, person, uid, document, group_id, server)

    Action parameters:
        person: The admin performing the ACL change
        uid: The admin user ID
        document: The document to modify ACL for
        group_id: The group to grant read access to
        server: The DMS server

    Action purpose:
        Modify a document's ACL to grant read access to a group

    Preconditions:
        - Admin session is active on server (state.nes_admin_on)

    Effects:
        - Group now has read access to document (state.dms_read_acl) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(document, str): return False
    if not isinstance(group_id, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, server) not in state.nes_admin_on:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Group now has read access
    state.dms_read_acl.add((document, group_id))
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# Network Actions (2)
# ----------------------------------------------------------------------------

def a_start_sniffer(state: State, person: str, uid: str, host: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_start_sniffer(state, person, uid, host)

    Action parameters:
        person: The person starting the sniffer
        uid: The user ID running the sniffer
        host: The host to run the sniffer on

    Action purpose:
        Start a packet sniffer on a host connected to a network hub

    Preconditions:
        - uid has a shell on host (state.has_shell)
        - Host is connected to a hub (state.host_nd, state.is_hub)

    Effects:
        - Sniffer is running on host (state.sniffer_running) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, host) not in state.has_shell:
        return False
    nd = state.host_nd.get(host)
    if nd is None or nd not in state.is_hub:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Sniffer is now running
    state.sniffer_running.add(host)
    # END: Effects

    return state


def a_read_sniffer(state: State, person: str, host: str, target_uid: str, target_server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_read_sniffer(state, person, host, target_uid, target_server)

    Action parameters:
        person: The person reading the sniffer output
        host: The host running the sniffer
        target_uid: The user ID whose password was sniffed
        target_server: The server the sniffed password is for

    Action purpose:
        Read captured password data from a running packet sniffer

    Preconditions:
        - Sniffer is running on host (state.sniffer_running)
        - Target credentials transit the hub (state.sniffable_passwords)
        - No firewall blocks sniffing between host and target (state.firewall_blocks_sniff)

    Effects:
        - Person learns the target's DMS password (state.dms_password_known) [DATA]
        - Person learns the target's admin password if applicable
          (state.admin_password_known) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(host, str): return False
    if not isinstance(target_uid, str): return False
    if not isinstance(target_server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if host not in state.sniffer_running:
        return False
    if (target_uid, target_server) not in state.sniffable_passwords:
        return False
    if (host, target_server) in state.firewall_blocks_sniff:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Person learns the DMS password
    state.dms_password_known.add((person, target_uid, target_server))
    # [DATA] If target has admin password, person learns it too
    for (p, srv) in list(state.admin_password_known):
        if p == target_uid and srv == target_server:
            state.admin_password_known.add((person, srv))
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# DMS Actions (6)
# ----------------------------------------------------------------------------

def a_start_dms_session(state: State, person: str, uid: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_start_dms_session(state, person, uid, server)

    Action parameters:
        person: The person starting the DMS session
        uid: The user ID for the session
        server: The DMS server

    Action purpose:
        Begin a DMS session

    Preconditions:
        - uid has a shell on some host (state.has_shell)

    Effects:
        - DMS session is active (state.dms_session_active) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Person must be at a host where they have an active shell (any uid)
    person_host = state.at_host.get(person)
    if person_host is None:
        return False
    if not any(h == person_host for (u, h) in state.has_shell):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] DMS session started
    state.dms_session_active.add((uid, server))
    # END: Effects

    return state


def a_dms_find_client(state: State, person: str, uid: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_dms_find_client(state, person, uid, server)

    Action parameters:
        person: The person finding the DMS client
        uid: The user ID for the session
        server: The DMS server

    Action purpose:
        Find the DMS client program on the host

    Preconditions:
        - DMS session is active (state.dms_session_active)

    Effects:
        - DMS client found (state.dms_client_found) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, server) not in state.dms_session_active:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Client program located
    state.dms_client_found.add((uid, server))
    # END: Effects

    return state


def a_dms_connect(state: State, person: str, uid: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_dms_connect(state, person, uid, server)

    Action parameters:
        person: The person connecting to the DMS server
        uid: The user ID for the session
        server: The DMS server

    Action purpose:
        Connect the DMS client to the DMS server

    Preconditions:
        - DMS client found (state.dms_client_found)
        - Server is reachable from person's host (state.can_reach)

    Effects:
        - DMS session connected to server (state.dms_session_connected) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, server) not in state.dms_client_found:
        return False
    person_host = state.at_host.get(person)
    if person_host is None:
        return False
    if (person_host, server) not in state.can_reach:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Connected to DMS server
    state.dms_session_connected.add((uid, server))
    # END: Effects

    return state


def a_dms_auth_password(state: State, person: str, uid: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_dms_auth_password(state, person, uid, server)

    Action parameters:
        person: The person authenticating
        uid: The user ID to authenticate as
        server: The DMS server

    Action purpose:
        Authenticate to the DMS using a password

    Preconditions:
        - DMS session is connected (state.dms_session_connected)
        - Person knows the DMS password for uid@server (state.dms_password_known)

    Effects:
        - DMS session is authenticated (state.dms_authenticated) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, server) not in state.dms_session_connected:
        return False
    if (person, uid, server) not in state.dms_password_known:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Authenticated to DMS
    state.dms_authenticated.add((uid, server))
    # END: Effects

    return state


def a_dms_auth_certificate(state: State, person: str, uid: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_dms_auth_certificate(state, person, uid, server)

    Action parameters:
        person: The person authenticating
        uid: The user ID to authenticate as
        server: The DMS server

    Action purpose:
        Authenticate to the DMS using an installed certificate

    Preconditions:
        - DMS session is connected (state.dms_session_connected)
        - Certificate is installed for uid on server (state.has_certificate)

    Effects:
        - DMS session is authenticated (state.dms_authenticated) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, server) not in state.dms_session_connected:
        return False
    if (uid, server) not in state.has_certificate:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Authenticated to DMS via certificate
    state.dms_authenticated.add((uid, server))
    # END: Effects

    return state


def a_dms_request_and_read(state: State, person: str, uid: str, document: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_dms_request_and_read(state, person, uid, document, server)

    Action parameters:
        person: The person requesting the document
        uid: The authenticated user ID
        document: The document to request and read
        server: The DMS server

    Action purpose:
        Request and read a document from the DMS after authentication

    Preconditions:
        - DMS session is authenticated (state.dms_authenticated)
        - uid or a group uid belongs to has read ACL on document (state.dms_read_acl, state.in_group)

    Effects:
        - Person has stolen the document (state.document_stolen) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(document, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, server) not in state.dms_authenticated:
        return False
    if not _h_has_acl(state, document, uid):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Document stolen
    state.document_stolen.add((person, document))
    # END: Effects

    return state


# ----------------------------------------------------------------------------
# Malware Actions (4)
# ----------------------------------------------------------------------------

def a_deploy_known_virus(state: State, person: str, uid: str, target_host: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_deploy_known_virus(state, person, uid, target_host)

    Action parameters:
        person: The attacker deploying the virus
        uid: The user ID on the target host
        target_host: The host to deploy the virus on

    Action purpose:
        Deploy a known virus on a target host (fails if antivirus scanner present)

    Preconditions:
        - uid has a shell on target_host (state.has_shell)
        - Target host has no virus scanner (state.scanned_host)

    Effects:
        - Virus deployed on target host (state.virus_deployed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(target_host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, target_host) not in state.has_shell:
        return False
    if target_host in state.scanned_host:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Virus deployed on target
    state.virus_deployed.add(target_host)
    # END: Effects

    return state


def a_write_custom_virus(state: State, person: str, uid: str, target_host: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_write_custom_virus(state, person, uid, target_host)

    Action parameters:
        person: The attacker writing the virus
        uid: The user ID on the target host
        target_host: The host to deploy the virus on

    Action purpose:
        Write and deploy a custom virus that bypasses antivirus scanners (requires high tech skill)

    Preconditions:
        - uid has a shell on target_host (state.has_shell)
        - Attacker has high tech skill (state.tech_skill[person] == 'high')

    Effects:
        - Virus deployed on target host (state.virus_deployed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(target_host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, target_host) not in state.has_shell:
        return False
    if state.tech_skill.get(person) != 'high':
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Custom virus deployed (bypasses scanners)
    state.virus_deployed.add(target_host)
    # END: Effects

    return state


def a_inject_code(state: State, person: str, uid: str, client_host: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_inject_code(state, person, uid, client_host, server)

    Action parameters:
        person: The attacker injecting the code
        uid: The user ID performing the injection
        client_host: The compromised client host
        server: The server to inject code into

    Action purpose:
        Inject trojan code into a server process via a compromised client

    Preconditions:
        - Virus is deployed on client_host (state.virus_deployed)
        - uid has a shell on client_host (state.has_shell)
        - Server is reachable from client_host (state.can_reach)

    Effects:
        - Code injected into server (state.code_injected) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(client_host, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if client_host not in state.virus_deployed:
        return False
    if (uid, client_host) not in state.has_shell:
        return False
    if (client_host, server) not in state.can_reach:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Trojan code injected
    state.code_injected.add((client_host, server))
    # END: Effects

    return state


def a_relay_document(state: State, person: str, document: str, client_host: str, server: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_relay_document(state, person, document, client_host, server)

    Action parameters:
        person: The attacker receiving the relayed document
        document: The document being relayed
        client_host: The compromised client relaying the document
        server: The server hosting the document

    Action purpose:
        Relay a document from the server through the compromised client (bypasses DMS ACL)

    Preconditions:
        - Code is injected into server via client (state.code_injected)

    Effects:
        - Person has stolen the document (state.document_stolen) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(person, str): return False
    if not isinstance(document, str): return False
    if not isinstance(client_host, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (client_host, server) not in state.code_injected:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Document stolen via covert relay
    state.document_stolen.add((person, document))
    # END: Effects

    return state


# ============================================================================
# METHODS (16)
# ============================================================================

# ----------------------------------------------------------------------------
# Top-Level Methods (2 alternatives for m_steal_secret_document)
# ----------------------------------------------------------------------------

def m_steal_via_legitimate_access(state: State, attacker: str, document: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_steal_via_legitimate_access(state, attacker, document, server)

    Method parameters:
        attacker: The insider attempting to steal the document
        document: The target document
        server: The DMS server hosting the document

    Method purpose:
        Steal a document via legitimate DMS access: acquire credentials,
        gain system access, ensure document permissions, then use DMS pipeline

    Preconditions:
        - Attacker is an insider (state.insider)

    Task decomposition:
        - m_gain_credentials: Acquire DMS credentials for the server
        - m_gain_system_access: Log in and get a shell
        - m_gain_document_access: Ensure read ACL on the document
        - m_dms_exfiltrate: Access DMS, authenticate, request and read

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(document, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if attacker not in state.insider:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_gain_credentials", attacker, server),
        ("m_gain_system_access", attacker),
        ("m_gain_document_access", attacker, document, server),
        ("m_dms_exfiltrate", attacker, document, server),
    ]
    # END: Task Decomposition


def m_steal_via_malware_relay(state: State, attacker: str, document: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_steal_via_malware_relay(state, attacker, document, server)

    Method parameters:
        attacker: The insider attempting to steal the document
        document: The target document
        server: The DMS server hosting the document

    Method purpose:
        Steal a document via covert malware relay: acquire credentials,
        gain system access, then deploy malware to relay the document
        (bypasses DMS access control)

    Preconditions:
        - Attacker is an insider (state.insider)

    Task decomposition:
        - m_gain_credentials: Acquire credentials for system access
        - m_gain_system_access: Log in and get a shell
        - m_deploy_and_relay: Deploy malware, inject code, relay document

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(document, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if attacker not in state.insider:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_gain_credentials", attacker, server),
        ("m_gain_system_access", attacker),
        ("m_deploy_and_relay", attacker, document, server),
    ]
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# Credential Acquisition Methods (3 alternatives for m_gain_credentials)
# ----------------------------------------------------------------------------

def m_credentials_already_known(state: State, attacker: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_credentials_already_known(state, attacker, server)

    Method parameters:
        attacker: The attacker
        server: The DMS server

    Method purpose:
        Check if the attacker already knows a DMS password for the server

    Preconditions:
        - Attacker knows a DMS password for some uid on server (state.dms_password_known)

    Task decomposition:
        - (empty) No actions needed

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    has_creds = any(p == attacker and srv == server
                    for (p, uid, srv) in state.dms_password_known)
    if not has_creds:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_credentials_via_shoulder_surf(state: State, attacker: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_credentials_via_shoulder_surf(state, attacker, server)

    Method parameters:
        attacker: The attacker
        server: The DMS server

    Method auxiliary parameters:
        victim: str (inferred from state — person who knows DMS password)
        victim_host: str (inferred from state — host the victim sits at)
        victim_room: str (inferred from state — room containing victim's host)

    Method purpose:
        Physically move to a victim's location and observe them typing
        their DMS password (shoulder surfing attack)

    Preconditions:
        - A victim exists who knows a DMS password for the server
        - A door exists between attacker's room and victim's room

    Task decomposition:
        - a_open_door: Open the door if closed (may fail if locked — triggers backtracking)
        - a_move_to_room: Move to victim's room
        - a_shoulder_surf: Observe the victim typing
        - a_move_to_room: Return to attacker's room

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    victim = None
    victim_host = None
    for (p, uid, srv) in state.dms_password_known:
        if p != attacker and srv == server:
            victim = p
            break
    if victim is None:
        return False
    for host, room in state.host_room.items():
        if state.at_host.get(victim) == host:
            victim_host = host
            break
    if victim_host is None:
        return False
    victim_room = state.host_room.get(victim_host)
    if victim_room is None:
        return False
    attacker_room = state.location.get(attacker)
    if attacker_room is None:
        return False
    if attacker_room == victim_room:
        return [("a_shoulder_surf", attacker, victim, victim_host)]
    door = _h_find_door(state, attacker_room, victim_room)
    if door is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Door existence checked above; lock/open status checked by actions at execution time
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = []
    if state.at_host.get(attacker) is not None:
        tasks.append(("a_leave_host", attacker, state.at_host[attacker]))
    if not state.door_open.get(door, False):
        tasks.append(("a_open_door", attacker, door))
    tasks.append(("a_move_to_room", attacker, attacker_room, victim_room))
    tasks.append(("a_shoulder_surf", attacker, victim, victim_host))
    tasks.append(("a_move_to_room", attacker, victim_room, attacker_room))
    return tasks
    # END: Task Decomposition


def m_credentials_via_sniff(state: State, attacker: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_credentials_via_sniff(state, attacker, server)

    Method parameters:
        attacker: The attacker
        server: The DMS server

    Method auxiliary parameters:
        attacker_host: str (inferred from state)
        attacker_uid: str (inferred from state)
        target_uid: str (inferred from sniffable_passwords)

    Method purpose:
        Sniff DMS credentials from network traffic on a hub-based network

    Preconditions:
        - Attacker has access to a host on a hub network
        - Target credentials are sniffable (state.sniffable_passwords)

    Task decomposition:
        - a_sit_at_host: Sit at attacker's computer (if not already)
        - a_login: Log in (if not already)
        - a_launch_shell: Get a shell (if not already)
        - a_start_sniffer: Start packet sniffer
        - a_read_sniffer: Read captured credentials

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    attacker_host = _h_attacker_host(state, attacker)
    if attacker_host is None:
        return False
    attacker_uid = None
    for (p, uid, h) in state.knows_password:
        if p == attacker and h == attacker_host:
            attacker_uid = uid
            break
    if attacker_uid is None:
        return False
    target_uid = None
    for (uid, srv) in state.sniffable_passwords:
        if srv == server:
            target_uid = uid
            break
    if target_uid is None:
        return False
    nd = state.host_nd.get(attacker_host)
    if nd is None or nd not in state.is_hub:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Hub and sniffable checks done above; firewall check deferred to a_read_sniffer
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = []
    if state.at_host.get(attacker) is not None and state.at_host[attacker] != attacker_host:
        tasks.append(("a_leave_host", attacker, state.at_host[attacker]))
    if state.at_host.get(attacker) != attacker_host:
        tasks.append(("a_sit_at_host", attacker, attacker_host))
    if (attacker_uid, attacker_host) not in state.logged_in:
        tasks.append(("a_login", attacker, attacker_uid, attacker_host))
    if (attacker_uid, attacker_host) not in state.has_shell:
        tasks.append(("a_launch_shell", attacker, attacker_uid, attacker_host))
    tasks.append(("a_start_sniffer", attacker, attacker_uid, attacker_host))
    tasks.append(("a_read_sniffer", attacker, attacker_host, target_uid, server))
    return tasks
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# System Access Method (1 method for m_gain_system_access)
# ----------------------------------------------------------------------------

def m_gain_system_access(state: State, attacker: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_gain_system_access(state, attacker)

    Method parameters:
        attacker: The attacker

    Method auxiliary parameters:
        attacker_host: str (inferred from state)
        attacker_uid: str (inferred from state)

    Method purpose:
        Log in and get a shell on the attacker's own host (skips steps already done)

    Preconditions:
        - Attacker has a host in their room

    Task decomposition:
        - a_sit_at_host: Sit at computer (if not already)
        - a_login: Log in (if not already)
        - a_launch_shell: Get shell (if not already)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    attacker_host = _h_attacker_host(state, attacker)
    if attacker_host is None:
        return False
    attacker_uid = None
    for (p, uid, h) in state.knows_password:
        if p == attacker and h == attacker_host:
            attacker_uid = uid
            break
    if attacker_uid is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No additional preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = []
    if state.at_host.get(attacker) is not None and state.at_host[attacker] != attacker_host:
        tasks.append(("a_leave_host", attacker, state.at_host[attacker]))
    if state.at_host.get(attacker) != attacker_host:
        tasks.append(("a_sit_at_host", attacker, attacker_host))
    if (attacker_uid, attacker_host) not in state.logged_in:
        tasks.append(("a_login", attacker, attacker_uid, attacker_host))
    if (attacker_uid, attacker_host) not in state.has_shell:
        tasks.append(("a_launch_shell", attacker, attacker_uid, attacker_host))
    return tasks
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# Document Access Methods (2 alternatives for m_gain_document_access)
# ----------------------------------------------------------------------------

def m_access_already_granted(state: State, attacker: str, document: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_access_already_granted(state, attacker, document, server)

    Method parameters:
        attacker: The attacker
        document: The target document
        server: The DMS server

    Method auxiliary parameters:
        auth_uid: str (inferred — the uid the attacker can authenticate as)

    Method purpose:
        Check if the attacker already has read ACL on the document
        (via direct uid or group membership)

    Preconditions:
        - A uid the attacker can authenticate as has read access (state.dms_read_acl, state.in_group)

    Task decomposition:
        - (empty) No actions needed

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(document, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    auth_uid = None
    for (p, uid, srv) in state.dms_password_known:
        if p == attacker and srv == server:
            auth_uid = uid
            break
    if auth_uid is None:
        for (uid, srv) in state.has_certificate:
            if srv == server:
                auth_uid = uid
                break
    if auth_uid is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not _h_has_acl(state, document, auth_uid):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_access_via_admin(state: State, attacker: str, document: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_access_via_admin(state, attacker, document, server)

    Method parameters:
        attacker: The attacker
        document: The target document
        server: The DMS server

    Method auxiliary parameters:
        attacker_uid: str (inferred from state)
        attacker_group: str (inferred from state.in_group)

    Method purpose:
        Gain admin credentials, log in as admin, and modify the document ACL
        to grant read access to the attacker's group

    Preconditions:
        - Attacker belongs to at least one group

    Task decomposition:
        - m_gain_admin_credentials: Get admin password (may sniff)
        - a_nes_admin_login: Log in as NES admin
        - a_dms_group_allow: Modify document ACL

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(document, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    attacker_uid = None
    for (p, uid, h) in state.knows_password:
        if p == attacker:
            attacker_uid = uid
            break
    if attacker_uid is None:
        return False
    groups = state.in_group.get(attacker_uid, set())
    if not groups:
        return False
    attacker_group = next(iter(groups))
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No additional preconditions — admin credential availability checked by sub-method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_gain_admin_credentials", attacker, server),
        ("a_nes_admin_login", attacker, attacker_uid, server),
        ("a_dms_group_allow", attacker, attacker_uid, document, attacker_group, server),
    ]
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# Admin Credential Methods (2 alternatives for m_gain_admin_credentials)
# ----------------------------------------------------------------------------

def m_admin_credentials_already_known(state: State, attacker: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_admin_credentials_already_known(state, attacker, server)

    Method parameters:
        attacker: The attacker
        server: The DMS server

    Method purpose:
        Check if the attacker already knows the admin password

    Preconditions:
        - Attacker knows admin password (state.admin_password_known)

    Task decomposition:
        - (empty) No actions needed

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (attacker, server) not in state.admin_password_known:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_admin_credentials_via_sniff(state: State, attacker: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_admin_credentials_via_sniff(state, attacker, server)

    Method parameters:
        attacker: The attacker
        server: The DMS server

    Method auxiliary parameters:
        attacker_host: str (inferred from state)
        attacker_uid: str (inferred from state)
        admin_uid: str (inferred from sniffable_passwords)

    Method purpose:
        Sniff admin credentials from network traffic

    Preconditions:
        - Admin credentials are sniffable on the network
        - Attacker's host is on a hub network

    Task decomposition:
        - a_start_sniffer / a_read_sniffer: Sniff admin credentials

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    attacker_host = _h_attacker_host(state, attacker)
    if attacker_host is None:
        return False
    attacker_uid = None
    for (p, uid, h) in state.knows_password:
        if p == attacker and h == attacker_host:
            attacker_uid = uid
            break
    if attacker_uid is None:
        return False
    admin_uid = None
    for (uid, srv) in state.sniffable_passwords:
        if srv == server:
            for (p, s) in state.admin_password_known:
                if p == uid and s == server:
                    admin_uid = uid
                    break
        if admin_uid is not None:
            break
    if admin_uid is None:
        return False
    nd = state.host_nd.get(attacker_host)
    if nd is None or nd not in state.is_hub:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Checks done in auxiliary inference
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = []
    if attacker_host not in state.sniffer_running:
        if (attacker_uid, attacker_host) not in state.has_shell:
            if state.at_host.get(attacker) != attacker_host:
                tasks.append(("a_sit_at_host", attacker, attacker_host))
            if (attacker_uid, attacker_host) not in state.logged_in:
                tasks.append(("a_login", attacker, attacker_uid, attacker_host))
            tasks.append(("a_launch_shell", attacker, attacker_uid, attacker_host))
        tasks.append(("a_start_sniffer", attacker, attacker_uid, attacker_host))
    tasks.append(("a_read_sniffer", attacker, attacker_host, admin_uid, server))
    return tasks
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# DMS Exfiltration Method (1 method for m_dms_exfiltrate)
# ----------------------------------------------------------------------------

def m_dms_exfiltrate(state: State, attacker: str, document: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_dms_exfiltrate(state, attacker, document, server)

    Method parameters:
        attacker: The attacker
        document: The target document
        server: The DMS server

    Method auxiliary parameters:
        auth_uid: str (inferred — the uid to authenticate as on the DMS)

    Method purpose:
        Access the DMS, authenticate, request and read the target document

    Preconditions:
        - Attacker has DMS credentials (password or certificate)

    Task decomposition:
        - a_start_dms_session: Begin DMS session
        - a_dms_find_client: Locate DMS client program
        - a_dms_connect: Connect to server
        - m_dms_authenticate: Authenticate (password or certificate)
        - a_dms_request_and_read: Request and read document

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(document, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    auth_uid = None
    for (p, uid, srv) in state.dms_password_known:
        if p == attacker and srv == server:
            auth_uid = uid
            break
    if auth_uid is None:
        for (uid, srv) in state.has_certificate:
            if srv == server:
                auth_uid = uid
                break
    if auth_uid is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Credential availability checked above
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_start_dms_session", attacker, auth_uid, server),
        ("a_dms_find_client", attacker, auth_uid, server),
        ("a_dms_connect", attacker, auth_uid, server),
        ("m_dms_authenticate", attacker, auth_uid, server),
        ("a_dms_request_and_read", attacker, auth_uid, document, server),
    ]
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# DMS Authentication Methods (2 alternatives for m_dms_authenticate)
# ----------------------------------------------------------------------------

def m_dms_auth_via_password(state: State, attacker: str, uid: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_dms_auth_via_password(state, attacker, uid, server)

    Method parameters:
        attacker: The attacker
        uid: The user ID to authenticate as
        server: The DMS server

    Method purpose:
        Authenticate to DMS using a password

    Preconditions:
        - Attacker knows the DMS password for uid@server (state.dms_password_known)

    Task decomposition:
        - a_dms_auth_password: Enter the password

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (attacker, uid, server) not in state.dms_password_known:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_dms_auth_password", attacker, uid, server)]
    # END: Task Decomposition


def m_dms_auth_via_certificate(state: State, attacker: str, uid: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_dms_auth_via_certificate(state, attacker, uid, server)

    Method parameters:
        attacker: The attacker
        uid: The user ID to authenticate as
        server: The DMS server

    Method purpose:
        Authenticate to DMS using an installed certificate

    Preconditions:
        - Certificate installed for uid on server (state.has_certificate)

    Task decomposition:
        - a_dms_auth_certificate: Present the certificate

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if (uid, server) not in state.has_certificate:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_dms_auth_certificate", attacker, uid, server)]
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# Malware Deploy and Relay Method (1 method for m_deploy_and_relay)
# ----------------------------------------------------------------------------

def m_deploy_and_relay(state: State, attacker: str, document: str, server: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_deploy_and_relay(state, attacker, document, server)

    Method parameters:
        attacker: The attacker
        document: The target document
        server: The DMS server

    Method auxiliary parameters:
        attacker_host: str (inferred from state)
        attacker_uid: str (inferred from state)

    Method purpose:
        Deploy malware on the attacker's host, inject code into the server,
        and relay the document back through the compromised channel

    Preconditions:
        - Attacker has system access (shell on their host)

    Task decomposition:
        - m_deploy_malware: Deploy virus on attacker's host
        - a_inject_code: Inject trojan into server process
        - a_relay_document: Relay document from server

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(document, str): return False
    if not isinstance(server, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    attacker_host = _h_attacker_host(state, attacker)
    if attacker_host is None:
        return False
    attacker_uid = None
    for (p, uid, h) in state.knows_password:
        if p == attacker and h == attacker_host:
            attacker_uid = uid
            break
    if attacker_uid is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # System access will be ensured by preceding m_gain_system_access
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_deploy_malware", attacker, attacker_uid, attacker_host),
        ("a_inject_code", attacker, attacker_uid, attacker_host, server),
        ("a_relay_document", attacker, document, attacker_host, server),
    ]
    # END: Task Decomposition


# ----------------------------------------------------------------------------
# Malware Deployment Methods (2 alternatives for m_deploy_malware)
# ----------------------------------------------------------------------------

def m_deploy_via_known_virus(state: State, attacker: str, uid: str, target_host: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_deploy_via_known_virus(state, attacker, uid, target_host)

    Method parameters:
        attacker: The attacker
        uid: The user ID on the target host
        target_host: The host to deploy the virus on

    Method purpose:
        Deploy a known virus on the target host (fails if scanner present —
        failure deferred to action execution to trigger backtracking)

    Preconditions:
        - None checked at method level (scanner check deferred to action)

    Task decomposition:
        - a_deploy_known_virus: Deploy the virus

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(target_host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Scanner check intentionally deferred to a_deploy_known_virus for backtracking
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_deploy_known_virus", attacker, uid, target_host)]
    # END: Task Decomposition


def m_deploy_via_custom_virus(state: State, attacker: str, uid: str, target_host: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_deploy_via_custom_virus(state, attacker, uid, target_host)

    Method parameters:
        attacker: The attacker
        uid: The user ID on the target host
        target_host: The host to deploy the virus on

    Method purpose:
        Write and deploy a custom virus that bypasses antivirus scanners

    Preconditions:
        - Attacker has high tech skill (state.tech_skill)

    Task decomposition:
        - a_write_custom_virus: Write and deploy custom virus

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(attacker, str): return False
    if not isinstance(uid, str): return False
    if not isinstance(target_host, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional value checks
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.tech_skill.get(attacker) != 'high':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_write_custom_virus", attacker, uid, target_host)]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    # Physical
    a_move_to_room, a_sit_at_host, a_leave_host, a_open_door, a_shoulder_surf,
    # Process
    a_login, a_launch_shell, a_nes_admin_login, a_dms_group_allow,
    # Network
    a_start_sniffer, a_read_sniffer,
    # DMS
    a_start_dms_session, a_dms_find_client, a_dms_connect,
    a_dms_auth_password, a_dms_auth_certificate, a_dms_request_and_read,
    # Malware
    a_deploy_known_virus, a_write_custom_virus, a_inject_code, a_relay_document,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Top-level: two attack strategies
declare_task_methods('m_steal_secret_document',
                     m_steal_via_legitimate_access,
                     m_steal_via_malware_relay)

# Credential acquisition: 3 alternatives (ordering enables backtracking in S4)
declare_task_methods('m_gain_credentials',
                     m_credentials_already_known,
                     m_credentials_via_shoulder_surf,
                     m_credentials_via_sniff)

# System access: single method
declare_task_methods('m_gain_system_access',
                     m_gain_system_access)

# Document access: 2 alternatives
declare_task_methods('m_gain_document_access',
                     m_access_already_granted,
                     m_access_via_admin)

# Admin credentials: 2 alternatives
declare_task_methods('m_gain_admin_credentials',
                     m_admin_credentials_already_known,
                     m_admin_credentials_via_sniff)

# DMS exfiltration pipeline: single method
declare_task_methods('m_dms_exfiltrate',
                     m_dms_exfiltrate)

# DMS authentication: 2 alternatives
declare_task_methods('m_dms_authenticate',
                     m_dms_auth_via_password,
                     m_dms_auth_via_certificate)

# Malware deploy + relay: single method
declare_task_methods('m_deploy_and_relay',
                     m_deploy_and_relay)

# Malware deployment: 2 alternatives (ordering enables backtracking in S8)
declare_task_methods('m_deploy_malware',
                     m_deploy_via_known_virus,
                     m_deploy_via_custom_virus)

# ============================================================================
# END OF FILE
# ============================================================================
