# ============================================================================
# MCP Orchestration - Bio-Opentrons Flex HTN Domain V3
# Cross-Server Architecture for PCR Workflow Automation
# WITH DYNAMIC SAMPLE SCALING
# ============================================================================
#
# V3 CHANGES (from V2):
# - m_distribute_master_mix: Now dynamically generates dispense actions based
#   on num_samples parameter instead of hardcoded 4 wells
# - m_transfer_samples: Now dynamically generates sample transfer tasks based
#   on num_samples parameter instead of hardcoded 4 samples
#
# EXPECTED PLAN LENGTH FORMULA:
#   plan_length = 35 + (5 * num_samples) + num_samples
#   Where:
#     35 = fixed actions (init, labware, pipettes, master mix prep, thermocycling)
#     5 * num_samples = sample transfers (pick_up, aspirate, dispense, mix, drop)
#     num_samples = dispense actions for master mix distribution
#
#   Examples:
#     4 samples  -> 35 + 20 + 4 = 59 actions (was 55 due to fewer dispenses)
#     8 samples  -> 35 + 40 + 8 = 83 actions
#     16 samples -> 35 + 80 + 16 = 131 actions
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - State Property Map (Cross-Server PCR Workflow)
#   - Actions (18)
#   - Methods (14)
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple, Dict

def safe_add_to_path(relative_path: str) -> Optional[str]:
    """
    Safely add a relative path to sys.path with validation to prevent path traversal attacks.

    Args:
        relative_path: Relative path to add to sys.path

    Returns:
        The absolute path that was added, or None if validation failed

    Raises:
        ValueError: If path traversal is detected
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))

    # Validate the path is within expected boundaries to prevent path traversal
    if not target_path.startswith(os.path.dirname(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")

    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

# ----- Secure GTPyhop import strategy - tries PyPI first, falls back to local
try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    # Fallback to local development with secure path handling
    try:
        safe_add_to_path(os.path.join('..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
    except (ImportError, ValueError) as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("bio_opentrons")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (Cross-Server PCR Workflow Orchestration)
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Server 1: movement-server (Pipette Movement & Tip Operations)
# Server 2: liquid-server (Liquid Handling Operations)
# Server 3: module-server (Thermocycler, Temperature Module, Heater-Shaker)
#
# --- SERVER INITIALIZATION ---
# a_initialize_servers
#  (E) movement_server_ready: True [ENABLER]
#  (E) liquid_server_ready: True [ENABLER]
#  (E) module_server_ready: True [ENABLER]
#  (E) cross_server_initialized: True [ENABLER]
#
# --- MOVEMENT SERVER ACTIONS (Server 1) ---
# a_load_labware
#  (P) movement_server_ready == True [ENABLER]
#  (E) labware_loaded[slot]: labware_type [DATA]
#  (E) deck_slots_occupied[slot]: True [ENABLER]
#
# a_load_pipette
#  (P) movement_server_ready == True [ENABLER]
#  (E) pipette_loaded[mount]: pipette_type [DATA]
#  (E) pipette_ready[mount]: True [ENABLER]
#
# a_pick_up_tip
#  (P) pipette_ready[mount] == True [ENABLER]
#  (P) has_tip[mount] == False [ENABLER]
#  (E) has_tip[mount]: True [ENABLER]
#  (E) tips_used: int [DATA]
#
# a_drop_tip
#  (P) has_tip[mount] == True [ENABLER]
#  (E) has_tip[mount]: False [ENABLER]
#
# a_move_to_well
#  (P) pipette_ready[mount] == True [ENABLER]
#  (E) pipette_position[mount]: (labware, well) [DATA]
#
# --- LIQUID SERVER ACTIONS (Server 2) ---
# a_aspirate
#  (P) liquid_server_ready == True [ENABLER]
#  (P) has_tip[mount] == True [ENABLER]
#  (E) pipette_volume[mount]: volume [DATA]
#  (E) well_volume[labware][well]: decreased [DATA]
#
# a_dispense
#  (P) liquid_server_ready == True [ENABLER]
#  (P) has_tip[mount] == True [ENABLER]
#  (P) pipette_volume[mount] >= volume [ENABLER]
#  (E) pipette_volume[mount]: decreased [DATA]
#  (E) well_volume[labware][well]: increased [DATA]
#
# a_mix
#  (P) liquid_server_ready == True [ENABLER]
#  (P) has_tip[mount] == True [ENABLER]
#  (E) well_mixed[labware][well]: True [ENABLER]
#
# a_blow_out
#  (P) liquid_server_ready == True [ENABLER]
#  (P) has_tip[mount] == True [ENABLER]
#  (E) pipette_volume[mount]: 0 [DATA]
#
# a_transfer_liquid
#  (P) liquid_server_ready == True [ENABLER]
#  (P) has_tip[mount] == True [ENABLER]
#  (E) well_volume[src]: decreased [DATA]
#  (E) well_volume[dest]: increased [DATA]
#
# --- MODULE SERVER ACTIONS (Server 3) ---
# a_open_thermocycler_lid
#  (P) module_server_ready == True [ENABLER]
#  (E) thermocycler_lid_open: True [ENABLER]
#
# a_close_thermocycler_lid
#  (P) module_server_ready == True [ENABLER]
#  (P) thermocycler_lid_open == True [ENABLER]
#  (E) thermocycler_lid_open: False [ENABLER]
#
# a_set_thermocycler_temperature
#  (P) module_server_ready == True [ENABLER]
#  (P) thermocycler_lid_open == False [ENABLER]
#  (E) thermocycler_block_temp: temperature [DATA]
#  (E) thermocycler_at_temp: True [ENABLER]
#
# a_execute_thermocycler_profile
#  (P) module_server_ready == True [ENABLER]
#  (P) thermocycler_lid_open == False [ENABLER]
#  (E) thermocycler_profile_complete: True [ENABLER]
#  (E) pcr_cycles_completed: int [DATA]
#
# a_deactivate_thermocycler
#  (P) module_server_ready == True [ENABLER]
#  (E) thermocycler_active: False [ENABLER]
#
# a_set_temperature_module
#  (P) module_server_ready == True [ENABLER]
#  (E) temp_module_temp: temperature [DATA]
#  (E) temp_module_at_temp: True [ENABLER]
#
# a_set_heater_shaker
#  (P) module_server_ready == True [ENABLER]
#  (E) heater_shaker_temp: temperature [DATA]
#  (E) heater_shaker_speed: rpm [DATA]
#  (E) heater_shaker_active: True [ENABLER]
#
# a_deactivate_heater_shaker
#  (P) module_server_ready == True [ENABLER]
#  (E) heater_shaker_active: False [ENABLER]
# ============================================================================

# ============================================================================
# ACTIONS (18)
# ----------------------------------------------------------------------------

# ============================================================================
# SERVER INITIALIZATION ACTION
# ============================================================================

def a_initialize_servers(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: bio_opentrons:initialize_all

    Action signature:
        a_initialize_servers(state)

    Action parameters:
        None

    Action purpose:
        Initialize all three MCP servers for cross-server PCR workflow orchestration

    Preconditions:
        None (initialization action)

    Effects:
        - Movement server is ready (state.movement_server_ready) [ENABLER]
        - Liquid server is ready (state.liquid_server_ready) [ENABLER]
        - Module server is ready (state.module_server_ready) [ENABLER]
        - Cross-server orchestration is initialized (state.cross_server_initialized) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    # No preconditions for initialization action
    # END: Preconditions

    # BEGIN: Effects
    state.movement_server_ready = True
    state.liquid_server_ready = True
    state.module_server_ready = True
    state.cross_server_initialized = True

    # Initialize data structures
    if not hasattr(state, 'labware_loaded'):
        state.labware_loaded = {}
    if not hasattr(state, 'deck_slots_occupied'):
        state.deck_slots_occupied = {}
    if not hasattr(state, 'pipette_loaded'):
        state.pipette_loaded = {}
    if not hasattr(state, 'pipette_ready'):
        state.pipette_ready = {}
    if not hasattr(state, 'has_tip'):
        state.has_tip = {}
    if not hasattr(state, 'pipette_volume'):
        state.pipette_volume = {}
    if not hasattr(state, 'pipette_position'):
        state.pipette_position = {}
    if not hasattr(state, 'well_volume'):
        state.well_volume = {}
    if not hasattr(state, 'well_mixed'):
        state.well_mixed = {}
    if not hasattr(state, 'tips_used'):
        state.tips_used = 0
    # END: Effects

    return state


# ============================================================================
# MOVEMENT SERVER ACTIONS (Server 1: movement-server)
# ============================================================================

def a_load_labware(state: State, slot: str, labware_type: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: movement_server:load_labware

    Action signature:
        a_load_labware(state, slot, labware_type)

    Action parameters:
        slot: Deck slot position (e.g., 'D1', 'C2', 'B3')
        labware_type: Type of labware (e.g., 'nest_96_wellplate_200ul_flat', 'opentrons_flex_96_tiprack_1000ul')

    Action purpose:
        Load labware onto the Opentrons Flex deck at specified slot

    Preconditions:
        - Movement server is ready (state.movement_server_ready)
        - Slot is not already occupied (slot not in state.deck_slots_occupied)

    Effects:
        - Labware is loaded at slot (state.labware_loaded[slot]) [DATA]
        - Slot is marked as occupied (state.deck_slots_occupied[slot]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(slot, str): return False
    if not isinstance(labware_type, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not slot.strip(): return False
    if not labware_type.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'movement_server_ready') and state.movement_server_ready):
        return False
    if hasattr(state, 'deck_slots_occupied') and slot in state.deck_slots_occupied:
        return False
    # END: Preconditions

    # BEGIN: Effects
    if not hasattr(state, 'labware_loaded'):
        state.labware_loaded = {}
    state.labware_loaded[slot] = labware_type

    if not hasattr(state, 'deck_slots_occupied'):
        state.deck_slots_occupied = {}
    state.deck_slots_occupied[slot] = True

    # Initialize well volumes for this labware
    if not hasattr(state, 'well_volume'):
        state.well_volume = {}
    state.well_volume[slot] = {}
    # END: Effects

    return state


def a_load_pipette(state: State, mount: str, pipette_type: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: movement_server:load_pipette

    Action signature:
        a_load_pipette(state, mount, pipette_type)

    Action parameters:
        mount: Pipette mount ('left' or 'right')
        pipette_type: Pipette type (e.g., 'flex_1channel_1000', 'flex_8channel_1000')

    Action purpose:
        Load a pipette onto the specified mount of the Opentrons Flex

    Preconditions:
        - Movement server is ready (state.movement_server_ready)
        - Mount is not already occupied

    Effects:
        - Pipette is loaded at mount (state.pipette_loaded[mount]) [DATA]
        - Pipette is ready (state.pipette_ready[mount]) [ENABLER]
        - Tip state initialized (state.has_tip[mount] = False)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(mount, str): return False
    if not isinstance(pipette_type, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if mount not in ('left', 'right'): return False
    if not pipette_type.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'movement_server_ready') and state.movement_server_ready):
        return False
    if hasattr(state, 'pipette_loaded') and mount in state.pipette_loaded:
        return False
    # END: Preconditions

    # BEGIN: Effects
    if not hasattr(state, 'pipette_loaded'):
        state.pipette_loaded = {}
    state.pipette_loaded[mount] = pipette_type

    if not hasattr(state, 'pipette_ready'):
        state.pipette_ready = {}
    state.pipette_ready[mount] = True

    if not hasattr(state, 'has_tip'):
        state.has_tip = {}
    state.has_tip[mount] = False

    if not hasattr(state, 'pipette_volume'):
        state.pipette_volume = {}
    state.pipette_volume[mount] = 0.0
    # END: Effects

    return state




def a_pick_up_tip(state: State, mount: str, tiprack_slot: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: movement_server:pick_up_tip

    Action signature:
        a_pick_up_tip(state, mount, tiprack_slot)

    Action parameters:
        mount: Pipette mount ('left' or 'right')
        tiprack_slot: Slot containing the tiprack

    Action purpose:
        Pick up a tip from the specified tiprack

    Preconditions:
        - Movement server is ready
        - Pipette is ready at mount
        - Pipette does not already have a tip
        - Tiprack is loaded at slot

    Effects:
        - Pipette has tip (state.has_tip[mount] = True) [ENABLER]
        - Tips used counter incremented

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(mount, str): return False
    if not isinstance(tiprack_slot, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if mount not in ('left', 'right'): return False
    if not tiprack_slot.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'movement_server_ready') and state.movement_server_ready):
        return False
    if not (hasattr(state, 'pipette_ready') and state.pipette_ready.get(mount)):
        return False
    if hasattr(state, 'has_tip') and state.has_tip.get(mount):
        return False
    if not (hasattr(state, 'labware_loaded') and tiprack_slot in state.labware_loaded):
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.has_tip[mount] = True
    if not hasattr(state, 'tips_used'):
        state.tips_used = 0
    state.tips_used += 1
    # END: Effects

    return state


def a_drop_tip(state: State, mount: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: movement_server:drop_tip

    Action signature:
        a_drop_tip(state, mount)

    Action parameters:
        mount: Pipette mount ('left' or 'right')

    Action purpose:
        Drop the current tip into the trash

    Preconditions:
        - Movement server is ready
        - Pipette has a tip

    Effects:
        - Pipette no longer has tip (state.has_tip[mount] = False) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(mount, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if mount not in ('left', 'right'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'movement_server_ready') and state.movement_server_ready):
        return False
    if not (hasattr(state, 'has_tip') and state.has_tip.get(mount)):
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.has_tip[mount] = False
    state.pipette_volume[mount] = 0.0
    # END: Effects

    return state


def a_move_to_well(state: State, mount: str, labware_slot: str, well: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: movement_server:move_to_well

    Action signature:
        a_move_to_well(state, mount, labware_slot, well)

    Action parameters:
        mount: Pipette mount ('left' or 'right')
        labware_slot: Slot containing the labware
        well: Well identifier (e.g., 'A1', 'B2')

    Action purpose:
        Move pipette to a specific well in a labware

    Preconditions:
        - Movement server is ready
        - Pipette is ready at mount
        - Labware is loaded at slot

    Effects:
        - Pipette position updated (state.pipette_position[mount]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(mount, str): return False
    if not isinstance(labware_slot, str): return False
    if not isinstance(well, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if mount not in ('left', 'right'): return False
    if not labware_slot.strip(): return False
    if not well.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'movement_server_ready') and state.movement_server_ready):
        return False
    if not (hasattr(state, 'pipette_ready') and state.pipette_ready.get(mount)):
        return False
    if not (hasattr(state, 'labware_loaded') and labware_slot in state.labware_loaded):
        return False
    # END: Preconditions

    # BEGIN: Effects
    if not hasattr(state, 'pipette_position'):
        state.pipette_position = {}
    state.pipette_position[mount] = (labware_slot, well)
    # END: Effects

    return state


# ============================================================================
# LIQUID SERVER ACTIONS (Server 2: liquid-server)
# ============================================================================

def a_aspirate(state: State, mount: str, volume: float, labware_slot: str, well: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:aspirate

    Action signature:
        a_aspirate(state, mount, volume, labware_slot, well)

    Action parameters:
        mount: Pipette mount ('left' or 'right')
        volume: Volume to aspirate in µL
        labware_slot: Slot containing the source labware
        well: Well to aspirate from

    Action purpose:
        Aspirate liquid from a well into the pipette

    Preconditions:
        - Liquid server is ready
        - Pipette has a tip
        - Pipette has capacity for volume

    Effects:
        - Pipette volume increased (state.pipette_volume[mount]) [DATA]
        - Well volume decreased (state.well_volume[slot][well]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(mount, str): return False
    if not isinstance(volume, (int, float)): return False
    if not isinstance(labware_slot, str): return False
    if not isinstance(well, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if mount not in ('left', 'right'): return False
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    if not (hasattr(state, 'has_tip') and state.has_tip.get(mount)):
        return False
    # END: Preconditions

    # BEGIN: Effects
    if not hasattr(state, 'pipette_volume'):
        state.pipette_volume = {}
    current_vol = state.pipette_volume.get(mount, 0.0)
    state.pipette_volume[mount] = current_vol + volume

    # Update well volume tracking
    if not hasattr(state, 'well_volume'):
        state.well_volume = {}
    if labware_slot not in state.well_volume:
        state.well_volume[labware_slot] = {}
    current_well_vol = state.well_volume[labware_slot].get(well, 0.0)
    state.well_volume[labware_slot][well] = max(0, current_well_vol - volume)
    # END: Effects

    return state




def a_dispense(state: State, mount: str, volume: float, labware_slot: str, well: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:dispense

    Action signature:
        a_dispense(state, mount, volume, labware_slot, well)

    Action parameters:
        mount: Pipette mount ('left' or 'right')
        volume: Volume to dispense in µL
        labware_slot: Slot containing the destination labware
        well: Well to dispense into

    Action purpose:
        Dispense liquid from the pipette into a well

    Preconditions:
        - Liquid server is ready
        - Pipette has a tip
        - Pipette has sufficient volume

    Effects:
        - Pipette volume decreased (state.pipette_volume[mount]) [DATA]
        - Well volume increased (state.well_volume[slot][well]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(mount, str): return False
    if not isinstance(volume, (int, float)): return False
    if not isinstance(labware_slot, str): return False
    if not isinstance(well, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if mount not in ('left', 'right'): return False
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    if not (hasattr(state, 'has_tip') and state.has_tip.get(mount)):
        return False
    current_vol = state.pipette_volume.get(mount, 0.0) if hasattr(state, 'pipette_volume') else 0.0
    if current_vol < volume:
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.pipette_volume[mount] = current_vol - volume

    if not hasattr(state, 'well_volume'):
        state.well_volume = {}
    if labware_slot not in state.well_volume:
        state.well_volume[labware_slot] = {}
    current_well_vol = state.well_volume[labware_slot].get(well, 0.0)
    state.well_volume[labware_slot][well] = current_well_vol + volume
    # END: Effects

    return state


def a_mix(state: State, mount: str, repetitions: int, volume: float, labware_slot: str, well: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:mix

    Action signature:
        a_mix(state, mount, repetitions, volume, labware_slot, well)

    Action parameters:
        mount: Pipette mount ('left' or 'right')
        repetitions: Number of mix cycles
        volume: Volume to mix in µL
        labware_slot: Slot containing the labware
        well: Well to mix

    Action purpose:
        Mix contents of a well by repeated aspiration and dispensing

    Preconditions:
        - Liquid server is ready
        - Pipette has a tip

    Effects:
        - Well is marked as mixed (state.well_mixed[slot][well]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(mount, str): return False
    if not isinstance(repetitions, int): return False
    if not isinstance(volume, (int, float)): return False
    if not isinstance(labware_slot, str): return False
    if not isinstance(well, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if mount not in ('left', 'right'): return False
    if repetitions <= 0: return False
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    if not (hasattr(state, 'has_tip') and state.has_tip.get(mount)):
        return False
    # END: Preconditions

    # BEGIN: Effects
    if not hasattr(state, 'well_mixed'):
        state.well_mixed = {}
    if labware_slot not in state.well_mixed:
        state.well_mixed[labware_slot] = {}
    state.well_mixed[labware_slot][well] = True
    # END: Effects

    return state


def a_blow_out(state: State, mount: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:blow_out

    Action signature:
        a_blow_out(state, mount)

    Action parameters:
        mount: Pipette mount ('left' or 'right')

    Action purpose:
        Blow out any remaining liquid from the pipette tip

    Preconditions:
        - Liquid server is ready
        - Pipette has a tip

    Effects:
        - Pipette volume set to 0 (state.pipette_volume[mount]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(mount, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if mount not in ('left', 'right'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    if not (hasattr(state, 'has_tip') and state.has_tip.get(mount)):
        return False
    # END: Preconditions

    # BEGIN: Effects
    if not hasattr(state, 'pipette_volume'):
        state.pipette_volume = {}
    state.pipette_volume[mount] = 0.0
    # END: Effects

    return state



# ============================================================================
# MODULE SERVER ACTIONS (Server 3: module-server)
# ============================================================================

def a_open_thermocycler_lid(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:open_thermocycler_lid

    Action signature:
        a_open_thermocycler_lid(state)

    Action parameters:
        None

    Action purpose:
        Open the thermocycler lid to allow plate access

    Preconditions:
        - Module server is ready
        - Thermocycler lid is closed

    Effects:
        - Thermocycler lid is open (state.thermocycler_lid_open) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # Idempotent: if lid is already open, just succeed
    if hasattr(state, 'thermocycler_lid_open') and state.thermocycler_lid_open:
        return state
    state.thermocycler_lid_open = True
    # END: Effects

    return state


def a_close_thermocycler_lid(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:close_thermocycler_lid

    Action signature:
        a_close_thermocycler_lid(state)

    Action parameters:
        None

    Action purpose:
        Close the thermocycler lid for thermal cycling

    Preconditions:
        - Module server is ready
        - Thermocycler lid is open

    Effects:
        - Thermocycler lid is closed (state.thermocycler_lid_open = False) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    if not (hasattr(state, 'thermocycler_lid_open') and state.thermocycler_lid_open):
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.thermocycler_lid_open = False
    # END: Effects

    return state


def a_set_thermocycler_temperature(state: State, temperature: float, hold_time: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:set_block_temperature

    Action signature:
        a_set_thermocycler_temperature(state, temperature, hold_time)

    Action parameters:
        temperature: Target temperature in Celsius
        hold_time: Hold time in seconds

    Action purpose:
        Set thermocycler block to a specific temperature

    Preconditions:
        - Module server is ready
        - Thermocycler lid is closed

    Effects:
        - Thermocycler block temperature set (state.thermocycler_block_temp) [DATA]
        - Thermocycler at temperature (state.thermocycler_at_temp) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(temperature, (int, float)): return False
    if not isinstance(hold_time, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if temperature < 4 or temperature > 99: return False
    if hold_time < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    if hasattr(state, 'thermocycler_lid_open') and state.thermocycler_lid_open:
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.thermocycler_block_temp = temperature
    state.thermocycler_at_temp = True
    state.thermocycler_active = True
    # END: Effects

    return state



def a_execute_thermocycler_profile(state: State, profile_name: str, num_cycles: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:execute_profile

    Action signature:
        a_execute_thermocycler_profile(state, profile_name, num_cycles)

    Action parameters:
        profile_name: Name of the thermocycler profile (e.g., 'pcr_standard', 'denaturation')
        num_cycles: Number of cycles to execute

    Action purpose:
        Execute a thermocycler profile for PCR amplification

    Preconditions:
        - Module server is ready
        - Thermocycler lid is closed
        - Thermocycler is active

    Effects:
        - Thermocycler profile complete (state.thermocycler_profile_complete) [ENABLER]
        - PCR cycles completed (state.pcr_cycles_completed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(profile_name, str): return False
    if not isinstance(num_cycles, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not profile_name.strip(): return False
    if num_cycles <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    if hasattr(state, 'thermocycler_lid_open') and state.thermocycler_lid_open:
        return False
    if not (hasattr(state, 'thermocycler_active') and state.thermocycler_active):
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.thermocycler_profile_complete = True
    state.pcr_cycles_completed = num_cycles
    state.thermocycler_profile_name = profile_name
    # END: Effects

    return state


def a_deactivate_thermocycler(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:deactivate_thermocycler

    Action signature:
        a_deactivate_thermocycler(state)

    Action parameters:
        None

    Action purpose:
        Deactivate the thermocycler after completing thermal cycling

    Preconditions:
        - Module server is ready

    Effects:
        - Thermocycler is deactivated (state.thermocycler_active = False) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.thermocycler_active = False
    state.thermocycler_block_temp = None
    # END: Effects

    return state


def a_set_temperature_module(state: State, temperature: float) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:set_temperature

    Action signature:
        a_set_temperature_module(state, temperature)

    Action parameters:
        temperature: Target temperature in Celsius

    Action purpose:
        Set temperature module to hold reagents at specific temperature

    Preconditions:
        - Module server is ready

    Effects:
        - Temperature module temperature set (state.temp_module_temp) [DATA]
        - Temperature module at temperature (state.temp_module_at_temp) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(temperature, (int, float)): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if temperature < 4 or temperature > 95: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.temp_module_temp = temperature
    state.temp_module_at_temp = True
    # END: Effects

    return state


def a_set_heater_shaker(state: State, temperature: float, speed: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:set_heater_shaker

    Action signature:
        a_set_heater_shaker(state, temperature, speed)

    Action parameters:
        temperature: Target temperature in Celsius
        speed: Shaking speed in RPM

    Action purpose:
        Set heater-shaker module temperature and shaking speed

    Preconditions:
        - Module server is ready

    Effects:
        - Heater-shaker temperature set (state.heater_shaker_temp) [DATA]
        - Heater-shaker speed set (state.heater_shaker_speed) [DATA]
        - Heater-shaker active (state.heater_shaker_active) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(temperature, (int, float)): return False
    if not isinstance(speed, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if temperature < 4 or temperature > 95: return False
    if speed < 0 or speed > 3000: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.heater_shaker_temp = temperature
    state.heater_shaker_speed = speed
    state.heater_shaker_active = True
    # END: Effects

    return state


def a_deactivate_heater_shaker(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:deactivate_heater_shaker

    Action signature:
        a_deactivate_heater_shaker(state)

    Action parameters:
        None

    Action purpose:
        Deactivate the heater-shaker module

    Preconditions:
        - Module server is ready

    Effects:
        - Heater-shaker is deactivated (state.heater_shaker_active = False) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Effects
    state.heater_shaker_active = False
    state.heater_shaker_temp = None
    state.heater_shaker_speed = 0
    # END: Effects

    return state



# ============================================================================
# METHODS (15)
# ----------------------------------------------------------------------------

# ============================================================================
# TOP-LEVEL WORKFLOW METHOD
# ============================================================================

def m_complete_pcr_workflow(state: State, num_samples: int, num_cycles: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_complete_pcr_workflow(state, num_samples, num_cycles)

    Method parameters:
        num_samples: Number of samples to process
        num_cycles: Number of PCR cycles

    Method purpose:
        Top-level method for complete PCR workflow orchestration across three servers.
        Demonstrates multi-level hierarchical decomposition with 5 phases.

    Preconditions:
        - Cross-server system is initialized (state.cross_server_initialized)

    Returns:
        List of subtasks (phase methods) if successful, False otherwise

    Hierarchical Decomposition:
        m_complete_pcr_workflow
        ├── m_phase1_deck_initialization
        ├── m_phase2_reagent_preparation
        ├── m_phase3_sample_loading
        ├── m_phase4_thermocycling
        └── m_phase5_post_processing
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_samples, int): return False
    if not isinstance(num_cycles, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if num_samples <= 0 or num_samples > 96: return False
    if num_cycles <= 0 or num_cycles > 50: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'cross_server_initialized') and state.cross_server_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_phase1_deck_initialization",),
        ("m_phase2_reagent_preparation", num_samples),
        ("m_phase3_sample_loading", num_samples),
        ("m_phase4_thermocycling", num_cycles),
        ("m_phase5_post_processing",)
    ]
    # END: Task Decomposition


def m_initialize_and_run_pcr(state: State, num_samples: int, num_cycles: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_initialize_and_run_pcr(state, num_samples, num_cycles)

    Method parameters:
        num_samples: Number of samples to process
        num_cycles: Number of PCR cycles

    Method purpose:
        Entry-point method that initializes servers then runs complete PCR workflow

    Preconditions:
        None (entry-point method)

    Returns:
        List of subtasks if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_samples, int): return False
    if not isinstance(num_cycles, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if num_samples <= 0: return False
    if num_cycles <= 0: return False
    # END: State-Type Checks

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("m_complete_pcr_workflow", num_samples, num_cycles)
    ]
    # END: Task Decomposition


# ============================================================================
# PHASE 1: DECK INITIALIZATION
# ============================================================================

def m_phase1_deck_initialization(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_phase1_deck_initialization(state)

    Method parameters:
        None

    Method purpose:
        Phase 1: Initialize deck with all required labware and pipettes.
        Decomposes into sub-methods for labware and instrument setup.

    Preconditions:
        - Movement server is ready

    Returns:
        List of subtasks if successful, False otherwise

    Hierarchical Decomposition:
        m_phase1_deck_initialization
        ├── m_setup_labware
        └── m_setup_instruments
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'movement_server_ready') and state.movement_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_setup_labware",),
        ("m_setup_instruments",)
    ]
    # END: Task Decomposition


def m_setup_labware(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_setup_labware(state)

    Method parameters:
        None

    Method purpose:
        Load all required labware onto the Opentrons Flex deck for PCR workflow.

    Preconditions:
        - Movement server is ready

    Returns:
        List of actions if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'movement_server_ready') and state.movement_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Realistic Flex deck layout for PCR:
    # D1: Thermocycler (spans D1-D3)
    # C1: Tiprack 1000µL
    # C2: Reagent reservoir
    # B1: Sample plate (source)
    # A1: Temperature module with reagent plate
    return [
        ("a_load_labware", "D1", "opentrons_flex_96_wellplate_200ul_pcr"),  # PCR plate in thermocycler
        ("a_load_labware", "C1", "opentrons_flex_96_tiprack_1000ul"),
        ("a_load_labware", "C2", "nest_12_reservoir_15ml"),  # Master mix reservoir
        ("a_load_labware", "B1", "nest_96_wellplate_200ul_flat"),  # Sample plate
        ("a_load_labware", "A1", "opentrons_24_aluminumblock_nest_1.5ml_snapcap")  # Reagent tubes
    ]
    # END: Task Decomposition



def m_setup_instruments(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_setup_instruments(state)

    Method parameters:
        None

    Method purpose:
        Load pipettes and initialize temperature modules for PCR workflow.

    Preconditions:
        - Movement server is ready
        - Module server is ready

    Returns:
        List of actions if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'movement_server_ready') and state.movement_server_ready):
        return False
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_load_pipette", "left", "flex_1channel_1000"),
        ("a_load_pipette", "right", "flex_8channel_1000"),
        ("a_set_temperature_module", 4.0),  # Keep reagents cold
        ("a_open_thermocycler_lid",)  # Prepare thermocycler for loading
    ]
    # END: Task Decomposition


# ============================================================================
# PHASE 2: REAGENT PREPARATION
# ============================================================================

def m_phase2_reagent_preparation(state: State, num_samples: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_phase2_reagent_preparation(state, num_samples)

    Method parameters:
        num_samples: Number of samples to prepare reagents for

    Method purpose:
        Phase 2: Prepare master mix and distribute to PCR plate.
        Decomposes into sub-methods for master mix preparation and distribution.

    Preconditions:
        - Liquid server is ready
        - Deck is initialized

    Returns:
        List of subtasks if successful, False otherwise

    Hierarchical Decomposition:
        m_phase2_reagent_preparation
        ├── m_prepare_master_mix
        └── m_distribute_master_mix
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_samples, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if num_samples <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_prepare_master_mix", num_samples),
        ("m_distribute_master_mix", num_samples)
    ]
    # END: Task Decomposition


def m_prepare_master_mix(state: State, num_samples: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_prepare_master_mix(state, num_samples)

    Method parameters:
        num_samples: Number of samples (determines master mix volume)

    Method purpose:
        Prepare PCR master mix in the reservoir by combining reagents.

    Preconditions:
        - Liquid server is ready
        - Pipette is ready

    Returns:
        List of actions if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_samples, int): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    if not (hasattr(state, 'pipette_ready') and state.pipette_ready.get('left')):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # PCR Master Mix preparation: polymerase, buffer, dNTPs, primers
    return [
        ("a_pick_up_tip", "left", "C1"),
        ("a_aspirate", "left", 500.0, "A1", "A1"),  # Polymerase buffer
        ("a_dispense", "left", 500.0, "C2", "A1"),  # To reservoir
        ("a_aspirate", "left", 100.0, "A1", "B1"),  # dNTPs
        ("a_dispense", "left", 100.0, "C2", "A1"),
        ("a_aspirate", "left", 50.0, "A1", "C1"),   # Forward primer
        ("a_dispense", "left", 50.0, "C2", "A1"),
        ("a_aspirate", "left", 50.0, "A1", "D1"),   # Reverse primer
        ("a_dispense", "left", 50.0, "C2", "A1"),
        ("a_mix", "left", 5, 400.0, "C2", "A1"),    # Mix master mix
        ("a_drop_tip", "left")
    ]
    # END: Task Decomposition



def m_distribute_master_mix(state: State, num_samples: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_distribute_master_mix(state, num_samples)

    Method parameters:
        num_samples: Number of wells to distribute to

    Method purpose:
        Distribute master mix to PCR plate wells using 8-channel pipette.

    Preconditions:
        - Liquid server is ready
        - Pipette is ready

    Returns:
        List of actions if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_samples, int): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # V3: Dynamic sample count - generate dispense actions based on num_samples
    # Use 8-channel to distribute master mix efficiently
    # Handle large sample counts with multiple aspirate-dispense cycles

    actions = [("a_pick_up_tip", "right", "C1")]

    # Calculate samples per cycle (max ~38 samples per 1000 uL aspirate at 25 uL each)
    samples_per_cycle = 38
    sample_idx = 0

    while sample_idx < num_samples:
        # Calculate samples for this cycle
        remaining = num_samples - sample_idx
        cycle_samples = min(remaining, samples_per_cycle)

        # Aspirate volume for this batch (25 uL per sample + 50 uL dead volume)
        cycle_volume = min(25.0 * cycle_samples + 50.0, 1000.0)
        actions.append(("a_aspirate", "right", cycle_volume, "C2", "A1"))

        # Dispense to each well in this batch
        for j in range(cycle_samples):
            i = sample_idx + j
            row = chr(ord('A') + (i // 12))  # A-H for 96-well plate
            col = (i % 12) + 1               # 1-12
            well_id = f"{row}{col}"
            actions.append(("a_dispense", "right", 25.0, "D1", well_id))

        actions.append(("a_blow_out", "right"))
        sample_idx += cycle_samples

    actions.append(("a_drop_tip", "right"))

    return actions
    # END: Task Decomposition


# ============================================================================
# PHASE 3: SAMPLE LOADING
# ============================================================================

def m_phase3_sample_loading(state: State, num_samples: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_phase3_sample_loading(state, num_samples)

    Method parameters:
        num_samples: Number of samples to load

    Method purpose:
        Phase 3: Load samples into PCR plate wells containing master mix.
        Uses single-channel pipette for sample-specific transfers.

    Preconditions:
        - Liquid server is ready
        - Master mix distributed

    Returns:
        List of subtasks if successful, False otherwise

    Hierarchical Decomposition:
        m_phase3_sample_loading
        └── m_transfer_samples
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_samples, int): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_transfer_samples", num_samples)
    ]
    # END: Task Decomposition


def m_transfer_samples(state: State, num_samples: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_transfer_samples(state, num_samples)

    Method parameters:
        num_samples: Number of samples to transfer

    Method purpose:
        Transfer DNA samples from source plate to PCR plate with mixing.

    Preconditions:
        - Liquid server is ready
        - Pipette is ready

    Returns:
        List of actions if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_samples, int): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'liquid_server_ready') and state.liquid_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # V3: Dynamic sample count - generate transfer actions based on num_samples
    # Transfer samples with tip change between samples to prevent cross-contamination

    actions = []
    # 96-well plate: rows A-H (8), columns 1-12 (12) = 96 wells max
    for i in range(num_samples):
        row = chr(ord('A') + (i // 12))  # A, B, C, ... H
        col = (i % 12) + 1               # 1-12
        well_id = f"{row}{col}"
        # Each sample requires: pick_up_tip, aspirate, dispense, mix, drop_tip (5 actions)
        actions.extend([
            ("a_pick_up_tip", "left", "C1"),
            ("a_aspirate", "left", 5.0, "B1", well_id),   # Aspirate from source plate
            ("a_dispense", "left", 5.0, "D1", well_id),   # Dispense to PCR plate
            ("a_mix", "left", 3, 15.0, "D1", well_id),    # Mix sample with master mix
            ("a_drop_tip", "left")
        ])

    return actions
    # END: Task Decomposition



# ============================================================================
# PHASE 4: THERMOCYCLING
# ============================================================================

def m_phase4_thermocycling(state: State, num_cycles: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_phase4_thermocycling(state, num_cycles)

    Method parameters:
        num_cycles: Number of PCR cycles to run

    Method purpose:
        Phase 4: Execute thermocycling protocol for PCR amplification.
        Decomposes into sub-methods for thermocycler preparation and profile execution.

    Preconditions:
        - Module server is ready
        - Samples are loaded

    Returns:
        List of subtasks if successful, False otherwise

    Hierarchical Decomposition:
        m_phase4_thermocycling
        ├── m_prepare_thermocycler
        └── m_run_pcr_profile
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_cycles, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if num_cycles <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_prepare_thermocycler",),
        ("m_run_pcr_profile", num_cycles)
    ]
    # END: Task Decomposition


def m_prepare_thermocycler(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_prepare_thermocycler(state)

    Method parameters:
        None

    Method purpose:
        Prepare thermocycler for PCR: close lid and set initial temperature.

    Preconditions:
        - Module server is ready
        - Thermocycler lid is open (for plate loading)

    Returns:
        List of actions if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_close_thermocycler_lid",),
        ("a_set_thermocycler_temperature", 95.0, 120)  # Initial denaturation at 95°C for 2 min
    ]
    # END: Task Decomposition


def m_run_pcr_profile(state: State, num_cycles: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_run_pcr_profile(state, num_cycles)

    Method parameters:
        num_cycles: Number of PCR cycles

    Method purpose:
        Execute the PCR thermal profile (denaturation → annealing → extension cycles).

    Preconditions:
        - Module server is ready
        - Thermocycler lid is closed
        - Thermocycler is at temperature

    Returns:
        List of actions if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(num_cycles, int): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    if hasattr(state, 'thermocycler_lid_open') and state.thermocycler_lid_open:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Standard PCR profile
    return [
        ("a_execute_thermocycler_profile", "pcr_standard", num_cycles),
        ("a_set_thermocycler_temperature", 72.0, 300),  # Final extension at 72°C for 5 min
        ("a_set_thermocycler_temperature", 4.0, 0)      # Hold at 4°C
    ]
    # END: Task Decomposition


# ============================================================================
# PHASE 5: POST-PROCESSING
# ============================================================================

def m_phase5_post_processing(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_phase5_post_processing(state)

    Method parameters:
        None

    Method purpose:
        Phase 5: Post-processing after PCR completion.
        Open thermocycler for plate retrieval and deactivate modules.

    Preconditions:
        - Module server is ready
        - Thermocycler profile complete

    Returns:
        List of actions if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'module_server_ready') and state.module_server_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_deactivate_thermocycler",),
        ("a_open_thermocycler_lid",)
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

# Declare all 18 actions to the current domain
declare_actions(
    # Server initialization
    a_initialize_servers,
    # Movement server (Server 1)
    a_load_labware,
    a_load_pipette,
    a_pick_up_tip,
    a_drop_tip,
    a_move_to_well,
    # Liquid server (Server 2)
    a_aspirate,
    a_dispense,
    a_mix,
    a_blow_out,
    # Module server (Server 3)
    a_open_thermocycler_lid,
    a_close_thermocycler_lid,
    a_set_thermocycler_temperature,
    a_execute_thermocycler_profile,
    a_deactivate_thermocycler,
    a_set_temperature_module,
    a_set_heater_shaker,
    a_deactivate_heater_shaker
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Declare task methods to the current domain
# Top-level methods
declare_task_methods('m_initialize_and_run_pcr', m_initialize_and_run_pcr)
declare_task_methods('m_complete_pcr_workflow', m_complete_pcr_workflow)

# Phase 1 methods
declare_task_methods('m_phase1_deck_initialization', m_phase1_deck_initialization)
declare_task_methods('m_setup_labware', m_setup_labware)
declare_task_methods('m_setup_instruments', m_setup_instruments)

# Phase 2 methods
declare_task_methods('m_phase2_reagent_preparation', m_phase2_reagent_preparation)
declare_task_methods('m_prepare_master_mix', m_prepare_master_mix)
declare_task_methods('m_distribute_master_mix', m_distribute_master_mix)

# Phase 3 methods
declare_task_methods('m_phase3_sample_loading', m_phase3_sample_loading)
declare_task_methods('m_transfer_samples', m_transfer_samples)

# Phase 4 methods
declare_task_methods('m_phase4_thermocycling', m_phase4_thermocycling)
declare_task_methods('m_prepare_thermocycler', m_prepare_thermocycler)
declare_task_methods('m_run_pcr_profile', m_run_pcr_profile)

# Phase 5 methods
declare_task_methods('m_phase5_post_processing', m_phase5_post_processing)

# ============================================================================
# END OF FILE
# ============================================================================

