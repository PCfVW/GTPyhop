# ============================================================================
# MCP Orchestration - Omega HDQ DNA Bacteria Extraction Domain
# Four-Server Architecture for DNA Extraction Workflow Automation
# ============================================================================
#
# Original protocol by Zach Galluzzo <zachary.galluzzo@opentrons.com>
#
# Four-Server Architecture:
#   - Server 1 (htn-planning-server): HTN planning with GTPyhop
#   - Server 2 (liquid-handling-server): Pipetting operations
#   - Server 3 (module-control-server): Heater-shaker, temperature module, magnetic block
#   - Server 4 (gripper-server): Labware transfers
#
# Protocol phases:
#   1. TL Lysis: Mix TL+PK buffers, transfer to samples, incubate 30 min
#   2. Sample Transfer: Move 200µL to new plate
#   3. AL Lysis: Add AL buffer, mix, incubate 4 min
#   4. Bead Binding: Add beads+binding buffer, incubate 10 min
#   5. Wash Cycles: 3 washes (VHB, VHB, SPM)
#   6. Dry Beads: Air dry 10 min
#   7. Elution: Add elution buffer, mix, collect DNA
#
# -- Generated 2025-11-29
# -- Refactored for style guide compliance 2025-11-30
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - State Property Map
#   - Actions (18)
#   - Methods (17)
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple

def safe_add_to_path(relative_path: str) -> Optional[str]:
    """
    Safely add a relative path to sys.path with validation to prevent path traversal attacks.

    Args:
        relative_path: Relative path to add to sys.path

    Returns:
        The absolute path that was added, or None if validation failed
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))
    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

# ----- Secure GTPyhop import strategy - tries PyPI first, falls back to local
try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
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
the_domain = Domain('omega_hdq_dna_bacteria')
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (Omega HDQ DNA Extraction Workflow)
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Server 2: liquid-handling-server (Pipetting Operations)
# Server 3: module-control-server (Heater-Shaker, Temperature Module, Magnetic Block)
# Server 4: gripper-server (Labware Transfers)
#
# --- LIQUID HANDLING ACTIONS (Server 2) ---
# a_pick_up_tip
#  (P) has_tip[pipette] == False [ENABLER]
#  (E) has_tip[pipette]: True [ENABLER]
#  (E) tips_used: int [DATA]
#  (E) pipette_volume[pipette]: 0.0 [DATA]
#
# a_return_tip
#  (P) has_tip[pipette] == True [ENABLER]
#  (E) has_tip[pipette]: False [ENABLER]
#  (E) pipette_volume[pipette]: 0.0 [DATA]
#
# a_aspirate
#  (P) has_tip[pipette] == True [ENABLER]
#  (P) pipette_volume[pipette] + volume <= 1000 [DATA]
#  (E) pipette_volume[pipette]: increased [DATA]
#  (E) well_volume[labware][well]: decreased [DATA]
#
# a_dispense
#  (P) has_tip[pipette] == True [ENABLER]
#  (E) pipette_volume[pipette]: decreased [DATA]
#  (E) well_volume[labware][well]: increased [DATA]
#
# a_blow_out
#  (P) has_tip[pipette] == True [ENABLER]
#  (E) pipette_volume[pipette]: 0.0 [DATA]
#
# a_air_gap
#  (P) has_tip[pipette] == True [ENABLER]
#  (E) pipette_volume[pipette]: increased [DATA]
#
# a_mix
#  (P) has_tip[pipette] == True [ENABLER]
#  (E) well_mixed[labware][well]: True [ENABLER]
#
# a_set_flow_rate
#  (E) flow_rate[pipette]: dict [DATA]
#
# a_home
#  (E) pipette_homed[pipette]: True [ENABLER]
#
# --- MODULE CONTROL ACTIONS (Server 3) ---
# a_hs_set_temperature
#  (P) heater_shaker_available == True [ENABLER]
#  (E) hs_target_temp: float [DATA]
#  (E) hs_at_temp: True [ENABLER]
#
# a_hs_set_shake_speed
#  (P) heater_shaker_available == True [ENABLER]
#  (E) hs_shake_speed: int [DATA]
#  (E) hs_shaking: True [ENABLER]
#
# a_hs_deactivate_shaker
#  (E) hs_shaking: False [ENABLER]
#  (E) hs_shake_speed: 0 [DATA]
#
# a_hs_open_latch
#  (P) hs_shaking == False [ENABLER]
#  (E) hs_latch_open: True [ENABLER]
#
# a_hs_close_latch
#  (E) hs_latch_open: False [ENABLER]
#
# a_temp_set_temperature
#  (P) temp_module_available == True [ENABLER]
#  (E) temp_module_temp: float [DATA]
#  (E) temp_at_temp: True [ENABLER]
#
# a_delay
#  (E) total_delay_minutes: increased [DATA]
#
# --- GRIPPER ACTIONS (Server 4) ---
# a_move_labware
#  (P) gripper_available == True if use_gripper [ENABLER]
#  (E) labware_position[labware]: destination [DATA]
#  (E) on_magnet[labware]: True/False [ENABLER]
# ============================================================================

# ============================================================================
# ACTIONS (18)
# ----------------------------------------------------------------------------

# ============================================================================
# LIQUID HANDLING ACTIONS (Server 2: liquid-handling-server)
# ============================================================================

def a_pick_up_tip(state: State, pipette: str, tip_rack: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:pick_up_tip

    Action signature:
        a_pick_up_tip(state, pipette, tip_rack)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')
        tip_rack: Tip rack identifier (e.g., 'tips', 'tips1')

    Action purpose:
        Pick up a tip from the specified rack for liquid handling operations

    Preconditions:
        - Pipette does not already have a tip (state.has_tip[pipette] == False)

    Effects:
        - Pipette has tip (state.has_tip[pipette]) [ENABLER]
        - Tips used counter incremented (state.tips_used) [DATA]
        - Pipette volume reset (state.pipette_volume[pipette]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    if not isinstance(tip_rack, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not pipette.strip(): return False
    if not tip_rack.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.has_tip.get(pipette, False):
        return False  # Already has tip
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Pipette now has a tip
    state.has_tip[pipette] = True
    # [DATA] Track tips used
    state.tips_used = state.tips_used + 1
    # [DATA] Reset pipette volume
    state.pipette_volume[pipette] = 0.0
    # END: Effects

    return state


def a_return_tip(state: State, pipette: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:return_tip

    Action signature:
        a_return_tip(state, pipette)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')

    Action purpose:
        Return the current tip to the rack or trash

    Preconditions:
        - Pipette has a tip (state.has_tip[pipette] == True)

    Effects:
        - Pipette no longer has tip (state.has_tip[pipette]) [ENABLER]
        - Pipette volume reset (state.pipette_volume[pipette]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not pipette.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.has_tip.get(pipette, False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Pipette no longer has tip
    state.has_tip[pipette] = False
    # [DATA] Reset pipette volume
    state.pipette_volume[pipette] = 0.0
    # END: Effects

    return state


def a_aspirate(state: State, pipette: str, volume: float, labware: str, well: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:aspirate

    Action signature:
        a_aspirate(state, pipette, volume, labware, well)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')
        volume: Volume to aspirate in µL
        labware: Labware identifier (e.g., 'TL_reservoir')
        well: Well identifier (e.g., 'A1')

    Action purpose:
        Aspirate liquid from a well into the pipette

    Preconditions:
        - Pipette has a tip (state.has_tip[pipette] == True)
        - Pipette has capacity for volume (pipette_volume + volume <= 1000)

    Effects:
        - Pipette volume increased (state.pipette_volume[pipette]) [DATA]
        - Well volume decreased (state.well_volume[labware][well]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    if not isinstance(volume, (int, float)): return False
    if not isinstance(labware, str): return False
    if not isinstance(well, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.has_tip.get(pipette, False):
        return False
    current_vol = state.pipette_volume.get(pipette, 0.0)
    if current_vol + volume > 1000:  # Max pipette volume
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Update pipette volume
    state.pipette_volume[pipette] = current_vol + volume
    # [DATA] Update well volume
    if labware not in state.well_volume:
        state.well_volume[labware] = {}
    current_well_vol = state.well_volume[labware].get(well, 0)
    state.well_volume[labware][well] = max(0, current_well_vol - volume)
    # END: Effects

    return state


def a_dispense(state: State, pipette: str, volume: float, labware: str, well: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:dispense

    Action signature:
        a_dispense(state, pipette, volume, labware, well)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')
        volume: Volume to dispense in µL
        labware: Labware identifier (e.g., 'sample_plate')
        well: Well identifier (e.g., 'A1')

    Action purpose:
        Dispense liquid from the pipette into a well

    Preconditions:
        - Pipette has a tip (state.has_tip[pipette] == True)

    Effects:
        - Pipette volume decreased (state.pipette_volume[pipette]) [DATA]
        - Well volume increased (state.well_volume[labware][well]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    if not isinstance(volume, (int, float)): return False
    if not isinstance(labware, str): return False
    if not isinstance(well, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.has_tip.get(pipette, False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    current_vol = state.pipette_volume.get(pipette, 0.0)
    if volume > current_vol:
        volume = current_vol  # Dispense what we have
    # [DATA] Update pipette volume
    state.pipette_volume[pipette] = current_vol - volume
    # [DATA] Update well volume
    if labware not in state.well_volume:
        state.well_volume[labware] = {}
    current_well_vol = state.well_volume[labware].get(well, 0)
    state.well_volume[labware][well] = current_well_vol + volume
    # END: Effects

    return state


def a_blow_out(state: State, pipette: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:blow_out

    Action signature:
        a_blow_out(state, pipette)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')

    Action purpose:
        Blow out any remaining liquid from the pipette tip

    Preconditions:
        - Pipette has a tip (state.has_tip[pipette] == True)

    Effects:
        - Pipette volume set to 0 (state.pipette_volume[pipette]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not pipette.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.has_tip.get(pipette, False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Reset pipette volume
    state.pipette_volume[pipette] = 0.0
    # END: Effects

    return state


def a_air_gap(state: State, pipette: str, volume: float) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:air_gap

    Action signature:
        a_air_gap(state, pipette, volume)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')
        volume: Air gap volume in µL

    Action purpose:
        Create an air gap in the tip to prevent dripping

    Preconditions:
        - Pipette has a tip (state.has_tip[pipette] == True)

    Effects:
        - Pipette volume increased by air gap (state.pipette_volume[pipette]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    if not isinstance(volume, (int, float)): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.has_tip.get(pipette, False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Add air gap to pipette volume
    current_vol = state.pipette_volume.get(pipette, 0.0)
    state.pipette_volume[pipette] = current_vol + volume
    # END: Effects

    return state


def a_mix(state: State, pipette: str, reps: int, volume: float, labware: str, well: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:mix

    Action signature:
        a_mix(state, pipette, reps, volume, labware, well)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')
        reps: Number of mix repetitions
        volume: Volume to mix in µL
        labware: Labware identifier (e.g., 'sample_plate')
        well: Well identifier (e.g., 'A1')

    Action purpose:
        Mix liquid in a well by repeated aspiration and dispensing

    Preconditions:
        - Pipette has a tip (state.has_tip[pipette] == True)

    Effects:
        - Well is marked as mixed (state.well_mixed[labware][well]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    if not isinstance(reps, int): return False
    if not isinstance(volume, (int, float)): return False
    if not isinstance(labware, str): return False
    if not isinstance(well, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if reps <= 0: return False
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.has_tip.get(pipette, False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Mark well as mixed
    if labware not in state.well_mixed:
        state.well_mixed[labware] = {}
    state.well_mixed[labware][well] = True
    # END: Effects

    return state


def a_set_flow_rate(state: State, pipette: str, aspirate_rate: float, dispense_rate: float) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:set_flow_rate

    Action signature:
        a_set_flow_rate(state, pipette, aspirate_rate, dispense_rate)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')
        aspirate_rate: Aspiration flow rate in µL/s
        dispense_rate: Dispense flow rate in µL/s

    Action purpose:
        Set pipette flow rates for liquid handling operations

    Preconditions:
        None

    Effects:
        - Flow rate configuration stored (state.flow_rate[pipette]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    if not isinstance(aspirate_rate, (int, float)): return False
    if not isinstance(dispense_rate, (int, float)): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if aspirate_rate <= 0: return False
    if dispense_rate <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for flow rate setting
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Store flow rate configuration
    state.flow_rate[pipette] = {'aspirate': aspirate_rate, 'dispense': dispense_rate}
    # END: Effects

    return state


def a_home(state: State, pipette: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: liquid_server:home

    Action signature:
        a_home(state, pipette)

    Action parameters:
        pipette: Pipette identifier (e.g., 'pip96')

    Action purpose:
        Home the pipette to its starting position

    Preconditions:
        None

    Effects:
        - Pipette is homed (state.pipette_homed[pipette]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(pipette, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not pipette.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for homing
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Pipette is homed
    state.pipette_homed[pipette] = True
    # END: Effects

    return state

# ============================================================================
# MODULE CONTROL ACTIONS (Server 3: module-control-server)
# ============================================================================

def a_hs_set_temperature(state: State, temperature: float) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:hs_set_temperature

    Action signature:
        a_hs_set_temperature(state, temperature)

    Action parameters:
        temperature: Target temperature in Celsius (e.g., 55.0)

    Action purpose:
        Set heater-shaker to target temperature for incubation

    Preconditions:
        - Heater-shaker is available (state.heater_shaker_available)

    Effects:
        - Target temperature set (state.hs_target_temp) [DATA]
        - Heater-shaker at temperature (state.hs_at_temp) [ENABLER]

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
    if not state.heater_shaker_available:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Set target temperature
    state.hs_target_temp = temperature
    # [ENABLER] At temperature
    state.hs_at_temp = True
    # END: Effects

    return state


def a_hs_set_shake_speed(state: State, rpm: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:hs_set_shake_speed

    Action signature:
        a_hs_set_shake_speed(state, rpm)

    Action parameters:
        rpm: Shake speed in RPM (e.g., 1800, 2000)

    Action purpose:
        Set heater-shaker shake speed and start shaking

    Preconditions:
        - Heater-shaker is available (state.heater_shaker_available)

    Effects:
        - Shake speed set (state.hs_shake_speed) [DATA]
        - Shaking started (state.hs_shaking) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(rpm, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if rpm < 0 or rpm > 3000: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not state.heater_shaker_available:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Set shake speed
    state.hs_shake_speed = rpm
    # [ENABLER] Shaking active
    state.hs_shaking = True
    # END: Effects

    return state


def a_hs_deactivate_shaker(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:hs_deactivate_shaker

    Action signature:
        a_hs_deactivate_shaker(state)

    Action parameters:
        None

    Action purpose:
        Stop the heater-shaker shaking

    Preconditions:
        None

    Effects:
        - Shaking stopped (state.hs_shaking) [ENABLER]
        - Shake speed reset (state.hs_shake_speed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for deactivation
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Shaking stopped
    state.hs_shaking = False
    # [DATA] Reset shake speed
    state.hs_shake_speed = 0
    # END: Effects

    return state


def a_hs_open_latch(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:hs_open_latch

    Action signature:
        a_hs_open_latch(state)

    Action parameters:
        None

    Action purpose:
        Open the heater-shaker latch for plate access

    Preconditions:
        - Heater-shaker is not shaking (state.hs_shaking == False)

    Effects:
        - Latch is open (state.hs_latch_open) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    if state.hs_shaking:
        return False  # Cannot open while shaking
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Latch is open
    state.hs_latch_open = True
    # END: Effects

    return state


def a_hs_close_latch(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:hs_close_latch

    Action signature:
        a_hs_close_latch(state)

    Action parameters:
        None

    Action purpose:
        Close the heater-shaker latch to secure plate

    Preconditions:
        None

    Effects:
        - Latch is closed (state.hs_latch_open) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for closing latch
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Latch is closed
    state.hs_latch_open = False
    # END: Effects

    return state


def a_temp_set_temperature(state: State, temperature: float) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:temp_set_temperature

    Action signature:
        a_temp_set_temperature(state, temperature)

    Action parameters:
        temperature: Target temperature in Celsius

    Action purpose:
        Set temperature module to target temperature for reagent storage

    Preconditions:
        - Temperature module is available (state.temp_module_available)

    Effects:
        - Temperature set (state.temp_module_temp) [DATA]
        - Module at temperature (state.temp_at_temp) [ENABLER]

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
    if not state.temp_module_available:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Set temperature
    state.temp_module_temp = temperature
    # [ENABLER] At temperature
    state.temp_at_temp = True
    # END: Effects

    return state


def a_delay(state: State, minutes: float, message: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: module_server:delay

    Action signature:
        a_delay(state, minutes, message)

    Action parameters:
        minutes: Delay duration in minutes
        message: Description of the delay purpose

    Action purpose:
        Wait for a specified time (simulated in planning)

    Preconditions:
        None

    Effects:
        - Total delay accumulated (state.total_delay_minutes) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(minutes, (int, float)): return False
    if not isinstance(message, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if minutes < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for delay
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Accumulate delay time
    state.total_delay_minutes = state.total_delay_minutes + minutes
    # END: Effects

    return state


# ============================================================================
# GRIPPER ACTIONS (Server 4: gripper-server)
# ============================================================================

def a_move_labware(state: State, labware: str, destination: str, use_gripper: bool) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: gripper_server:move_labware

    Action signature:
        a_move_labware(state, labware, destination, use_gripper)

    Action parameters:
        labware: Labware identifier (e.g., 'sample_plate', 'TL_plate')
        destination: Destination position (e.g., 'magblock', 'heater_shaker', 'deck_D1')
        use_gripper: Whether to use gripper for transfer

    Action purpose:
        Move labware from current position to destination

    Preconditions:
        - If use_gripper is True, gripper must be available (state.gripper_available)

    Effects:
        - Labware position updated (state.labware_position[labware]) [DATA]
        - Magnet status updated if moving to/from magblock (state.on_magnet[labware]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(labware, str): return False
    if not isinstance(destination, str): return False
    if not isinstance(use_gripper, bool): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not labware.strip(): return False
    if not destination.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if use_gripper and not state.gripper_available:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Update labware position
    state.labware_position[labware] = destination
    # [ENABLER] Update magnet status
    if destination == 'magblock':
        state.on_magnet[labware] = True
    else:
        state.on_magnet[labware] = False
    # END: Effects

    return state


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    # Liquid handling (Server 2)
    a_pick_up_tip, a_return_tip, a_aspirate, a_dispense,
    a_blow_out, a_air_gap, a_mix, a_set_flow_rate, a_home,
    # Module control (Server 3)
    a_hs_set_temperature, a_hs_set_shake_speed, a_hs_deactivate_shaker,
    a_hs_open_latch, a_hs_close_latch, a_temp_set_temperature, a_delay,
    # Gripper (Server 4)
    a_move_labware
)

# ============================================================================
# METHODS (17)
# ----------------------------------------------------------------------------

# ============================================================================
# TOP-LEVEL ORCHESTRATION METHODS
# ============================================================================

def m_hdq_dna_extraction(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_hdq_dna_extraction(state)

    Method parameters:
        None

    Method purpose:
        Top-level method for complete HDQ DNA extraction protocol.
        Orchestrates 10 sequential phases of the extraction workflow.

    Preconditions:
        None (entry-point method)

    Task decomposition:
        - m_initialize_protocol: Initialize protocol and prepare pipette
        - m_tl_lysis_phase: TL lysis with PK buffer
        - m_transfer_sample_to_new_plate: Transfer lysed sample
        - m_al_lysis_phase: AL lysis buffer addition
        - m_bead_binding_phase: Magnetic bead binding
        - m_magnetic_separation_initial: Initial magnetic separation
        - m_wash_all_cycles: Execute wash cycles
        - m_dry_beads: Air dry beads
        - m_elution_phase: Elute DNA
        - m_finalize_protocol: Home and finalize

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for entry-point method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('m_initialize_protocol',),
        ('m_tl_lysis_phase',),
        ('m_transfer_sample_to_new_plate',),
        ('m_al_lysis_phase',),
        ('m_bead_binding_phase',),
        ('m_magnetic_separation_initial',),
        ('m_wash_all_cycles',),
        ('m_dry_beads',),
        ('m_elution_phase',),
        ('m_finalize_protocol',)
    ]
    # END: Task Decomposition


# ============================================================================
# INITIALIZATION AND FINALIZATION METHODS
# ============================================================================

def m_initialize_protocol(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_initialize_protocol(state)

    Method parameters:
        None

    Method auxiliary parameters:
        heater_shaker_available: bool (inferred from state)

    Method purpose:
        Initialize the protocol by closing heater-shaker latch and picking up tip

    Preconditions:
        None

    Task decomposition:
        - a_hs_close_latch: Close heater-shaker latch (if available)
        - a_pick_up_tip: Pick up initial tip

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    hs_available = getattr(state, 'heater_shaker_available', False)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = []
    if hs_available:
        tasks.append(('a_hs_close_latch',))
    tasks.append(('a_pick_up_tip', 'pip96', 'tips'))
    return tasks
    # END: Task Decomposition


def m_finalize_protocol(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_finalize_protocol(state)

    Method parameters:
        None

    Method purpose:
        Finalize the protocol by homing the pipette

    Preconditions:
        None

    Task decomposition:
        - a_home: Home the pipette

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_home', 'pip96')]
    # END: Task Decomposition

# ============================================================================
# TL LYSIS PHASE METHODS
# ============================================================================

def m_tl_lysis_phase(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_tl_lysis_phase(state)

    Method parameters:
        None

    Method auxiliary parameters:
        tl_vol: float (inferred from state)
        pk_vol: float (inferred from state)
        dry_run: bool (inferred from state)
        heater_shaker_available: bool (inferred from state)

    Method purpose:
        TL Lysis phase: Mix TL+PK buffers, transfer to samples, incubate.
        Uses heater-shaker if available, otherwise manual mixing.

    Preconditions:
        None

    Task decomposition:
        - a_mix: Mix TL and PK buffers
        - a_aspirate: Aspirate mixed buffer
        - a_air_gap: Add air gap
        - a_dispense: Dispense to TL plate
        - m_resuspend_pellet: Mix with samples
        - a_return_tip: Return tip
        - a_hs_set_temperature: Set heater-shaker temp (if available)
        - a_hs_set_shake_speed: Start shaking (if available)
        - a_delay: Incubation delay
        - a_hs_deactivate_shaker: Stop shaking (if available)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    tl_vol = state.tl_vol
    pk_vol = state.pk_vol
    total_vol = tl_vol + pk_vol
    mix_reps = 1 if state.dry_run else 3
    incubation_time = 0.25 if state.dry_run else 30
    hs_available = getattr(state, 'heater_shaker_available', False)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = [
        # Mix TL and PK buffers
        ('a_mix', 'pip96', mix_reps, total_vol, 'TL_reservoir', 'A1'),
        # Transfer TL+PK to sample plate
        ('a_aspirate', 'pip96', total_vol, 'TL_reservoir', 'A1'),
        ('a_air_gap', 'pip96', 10),
        ('a_dispense', 'pip96', total_vol + 10, 'TL_plate', 'A1'),
        # Mix with samples
        ('m_resuspend_pellet', 'TL_plate', 'A1', total_vol),
    ]

    # Always return tip after resuspension
    tasks.append(('a_return_tip', 'pip96'))

    # Incubation with shaking (only if heater-shaker available)
    if hs_available:
        tasks.extend([
            ('a_hs_set_temperature', 55),
            ('a_hs_set_shake_speed', 2000),
            ('a_delay', incubation_time, 'TL lysis incubation'),
            ('a_hs_deactivate_shaker',),
        ])
    else:
        # Manual incubation delay
        tasks.append(('a_delay', incubation_time, 'TL lysis incubation (manual)'))

    return tasks
    # END: Task Decomposition


# ============================================================================
# SAMPLE TRANSFER METHODS
# ============================================================================

def m_transfer_sample_to_new_plate(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_transfer_sample_to_new_plate(state)

    Method parameters:
        None

    Method auxiliary parameters:
        sample_vol: float (inferred from state)
        heater_shaker_available: bool (inferred from state)

    Method purpose:
        Transfer 200µL of lysed sample to new deep well plate

    Preconditions:
        None

    Task decomposition:
        - a_pick_up_tip: Pick up tip
        - a_aspirate: Aspirate sample
        - a_air_gap: Add air gap
        - a_dispense: Dispense to sample plate
        - a_blow_out: Blow out residual
        - a_return_tip: Return tip
        - a_hs_open_latch: Open latch (if available)
        - a_move_labware: Move TL_plate to magblock
        - a_move_labware: Move sample_plate to destination
        - a_hs_close_latch: Close latch (if available)
        - a_move_labware: Move TL_plate off magblock

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    sample_vol = state.sample_vol
    hs_available = getattr(state, 'heater_shaker_available', False)
    sample_dest = 'heater_shaker' if hs_available else 'deck_D1'
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = [
        ('a_pick_up_tip', 'pip96', 'tips'),
        ('a_aspirate', 'pip96', sample_vol, 'TL_plate', 'A1'),
        ('a_air_gap', 'pip96', 20),
        ('a_dispense', 'pip96', sample_vol + 20, 'sample_plate', 'A1'),
        ('a_blow_out', 'pip96'),
        ('a_return_tip', 'pip96'),
    ]

    # Move plates: TL_plate to magblock, sample_plate to H-S or deck
    if hs_available:
        tasks.append(('a_hs_open_latch',))

    tasks.extend([
        ('a_move_labware', 'TL_plate', 'magblock', True),
        ('a_move_labware', 'sample_plate', sample_dest, True),
    ])

    if hs_available:
        tasks.append(('a_hs_close_latch',))

    # Move TL_plate off magblock to deck
    tasks.append(('a_move_labware', 'TL_plate', 'deck_slot_6', True))

    return tasks
    # END: Task Decomposition

# ============================================================================
# AL LYSIS PHASE METHODS
# ============================================================================

def m_al_lysis_phase(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_al_lysis_phase(state)

    Method parameters:
        None

    Method auxiliary parameters:
        al_vol: float (inferred from state)
        sample_vol: float (inferred from state)
        dry_run: bool (inferred from state)
        heater_shaker_available: bool (inferred from state)

    Method purpose:
        AL Lysis phase: Add AL buffer, mix, incubate 4 min

    Preconditions:
        None

    Task decomposition:
        - a_pick_up_tip: Pick up tip
        - a_aspirate: Aspirate AL buffer
        - a_air_gap: Add air gap
        - a_dispense: Dispense to sample plate
        - m_resuspend_pellet: Mix with sample
        - a_return_tip: Return tip
        - a_hs_set_shake_speed: Start shaking (if available)
        - a_delay: Incubation delay
        - a_hs_deactivate_shaker: Stop shaking (if available)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    al_vol = state.al_vol
    sample_vol = state.sample_vol
    incubation_time = 0.25 if state.dry_run else 4
    hs_available = getattr(state, 'heater_shaker_available', False)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = [
        ('a_pick_up_tip', 'pip96', 'tips'),
        ('a_aspirate', 'pip96', al_vol, 'AL_reservoir', 'A1'),
        ('a_air_gap', 'pip96', 10),
        ('a_dispense', 'pip96', al_vol + 10, 'sample_plate', 'A1'),
        ('m_resuspend_pellet', 'sample_plate', 'A1', al_vol + sample_vol),
    ]

    # Always return tip after resuspension
    tasks.append(('a_return_tip', 'pip96'))

    if hs_available:
        tasks.extend([
            ('a_hs_set_shake_speed', 2000),
            ('a_delay', incubation_time, 'AL lysis incubation'),
            ('a_hs_deactivate_shaker',),
        ])
    else:
        tasks.append(('a_delay', incubation_time, 'AL lysis incubation (manual)'))

    return tasks
    # END: Task Decomposition


# ============================================================================
# BEAD BINDING PHASE METHODS
# ============================================================================

def m_bead_binding_phase(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_bead_binding_phase(state)

    Method parameters:
        None

    Method auxiliary parameters:
        bind_vol: float (inferred from state)
        bead_vol: float (inferred from state)
        al_vol: float (inferred from state)
        sample_vol: float (inferred from state)
        dry_run: bool (inferred from state)
        heater_shaker_available: bool (inferred from state)

    Method purpose:
        Bead binding: Mix beads, transfer to samples, incubate 10 min

    Preconditions:
        None

    Task decomposition:
        - a_pick_up_tip: Pick up tip
        - a_mix: Mix beads in reservoir
        - a_aspirate: Aspirate beads
        - a_dispense: Dispense to sample plate
        - a_mix: Mix beads with sample
        - a_return_tip: Return tip
        - a_home: Home pipette
        - a_hs_set_shake_speed: Start shaking (if available)
        - a_delay: Incubation delay
        - a_hs_deactivate_shaker: Stop shaking (if available)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    bind_vol = state.bind_vol
    bead_vol = state.bead_vol
    al_vol = state.al_vol
    sample_vol = state.sample_vol
    total_bind_vol = bind_vol + bead_vol
    incubation_time = 0.25 if state.dry_run else 10
    mix_reps = 1 if state.dry_run else 3
    hs_available = getattr(state, 'heater_shaker_available', False)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = [
        ('a_pick_up_tip', 'pip96', 'tips'),
        # Mix beads in reservoir
        ('a_mix', 'pip96', mix_reps, total_bind_vol, 'bind_reservoir', 'A1'),
        # Transfer beads to sample plate
        ('a_aspirate', 'pip96', total_bind_vol, 'bind_reservoir', 'A1'),
        ('a_dispense', 'pip96', total_bind_vol, 'sample_plate', 'A1'),
        # Mix beads with sample
        ('a_mix', 'pip96', mix_reps, total_bind_vol + al_vol + sample_vol, 'sample_plate', 'A1'),
    ]

    # Always return tip after mixing
    tasks.extend([
        ('a_return_tip', 'pip96'),
        ('a_home', 'pip96'),
    ])

    if hs_available:
        tasks.extend([
            ('a_hs_set_shake_speed', 1800),
            ('a_delay', incubation_time, 'Bead binding incubation'),
            ('a_hs_deactivate_shaker',),
        ])
    else:
        tasks.append(('a_delay', incubation_time, 'Bead binding incubation (manual)'))

    return tasks
    # END: Task Decomposition

# ============================================================================
# MAGNETIC SEPARATION METHODS
# ============================================================================

def m_magnetic_separation_initial(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_magnetic_separation_initial(state)

    Method parameters:
        None

    Method auxiliary parameters:
        dry_run: bool (inferred from state)
        heater_shaker_available: bool (inferred from state)

    Method purpose:
        Initial magnetic separation: move to magblock, wait, remove supernatant

    Preconditions:
        None

    Task decomposition:
        - a_hs_open_latch: Open latch (if available)
        - a_move_labware: Move sample plate to magblock
        - a_hs_close_latch: Close latch (if available)
        - a_delay: Wait for bead settling
        - m_remove_supernatant: Remove supernatant
        - a_hs_open_latch: Open latch (if available)
        - a_move_labware: Move plate back
        - a_hs_close_latch: Close latch (if available)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    settling_time = 0.5 if state.dry_run else 2
    hs_available = getattr(state, 'heater_shaker_available', False)
    dest_after_mag = 'heater_shaker' if hs_available else 'deck_D1'
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = []
    if hs_available:
        tasks.append(('a_hs_open_latch',))

    tasks.extend([
        ('a_move_labware', 'sample_plate', 'magblock', True),
    ])

    if hs_available:
        tasks.append(('a_hs_close_latch',))

    tasks.extend([
        ('a_delay', settling_time, 'Bead settling'),
        ('m_remove_supernatant', 'sample_plate', 'bind_reservoir', 1000),
    ])

    # Move plate back to H-S or deck
    if hs_available:
        tasks.append(('a_hs_open_latch',))
    tasks.append(('a_move_labware', 'sample_plate', dest_after_mag, True))
    if hs_available:
        tasks.append(('a_hs_close_latch',))

    return tasks
    # END: Task Decomposition


def m_remove_supernatant(state: State, plate: str, waste: str, volume: float) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_remove_supernatant(state, plate, waste, volume)

    Method parameters:
        plate: Source plate identifier (e.g., 'sample_plate')
        waste: Waste destination identifier (e.g., 'bind_reservoir')
        volume: Volume to remove in µL

    Method purpose:
        Remove supernatant from plate and dispense to waste

    Preconditions:
        None

    Task decomposition:
        - a_pick_up_tip: Pick up tip
        - a_aspirate: Aspirate supernatant
        - a_dispense: Dispense to waste
        - a_return_tip: Return tip

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(plate, str): return False
    if not isinstance(waste, str): return False
    if not isinstance(volume, (int, float)): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_pick_up_tip', 'pip96', 'tips'),
        ('a_aspirate', 'pip96', volume, plate, 'A1'),
        ('a_dispense', 'pip96', volume, waste, 'A1'),
        ('a_return_tip', 'pip96'),
    ]
    # END: Task Decomposition

# ============================================================================
# WASH CYCLE METHODS
# ============================================================================

def m_wash_all_cycles(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_wash_all_cycles(state)

    Method parameters:
        None

    Method auxiliary parameters:
        num_washes: int (inferred from state)

    Method purpose:
        Execute all wash cycles based on configuration

    Preconditions:
        None

    Task decomposition:
        - m_single_wash_cycle: Execute each wash cycle (VHB x2, SPM x1)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    num_washes = state.num_washes
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = []
    for i in range(num_washes):
        # Determine wash buffer and waste based on wash number
        if i < 2:
            wash_source = 'wash1_reservoir'  # VHB
            waste_dest = 'TL_reservoir'
        else:
            wash_source = 'wash2_reservoir'  # SPM
            waste_dest = 'bind_reservoir'
        tasks.append(('m_single_wash_cycle', i + 1, wash_source, waste_dest))
    return tasks
    # END: Task Decomposition


def m_single_wash_cycle(state: State, wash_num: int, wash_source: str, waste_dest: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_single_wash_cycle(state, wash_num, wash_source, waste_dest)

    Method parameters:
        wash_num: Wash cycle number (1, 2, or 3)
        wash_source: Wash buffer source (e.g., 'wash1_reservoir')
        waste_dest: Waste destination (e.g., 'TL_reservoir')

    Method auxiliary parameters:
        wash_vol: float (inferred from state)
        dry_run: bool (inferred from state)
        tip_mixing: bool (inferred from state)
        heater_shaker_available: bool (inferred from state)

    Method purpose:
        Single wash cycle: add wash buffer, shake, magnetic separate, remove

    Preconditions:
        None

    Task decomposition:
        - a_pick_up_tip: Pick up tip
        - a_aspirate: Aspirate wash buffer
        - a_dispense: Dispense to sample plate
        - a_blow_out: Blow out residual
        - a_air_gap: Add air gap
        - a_return_tip/a_mix: Return tip or mix (based on tip_mixing)
        - a_hs_set_shake_speed: Start shaking (if available)
        - a_delay: Incubation delay
        - a_hs_deactivate_shaker: Stop shaking (if available)
        - a_move_labware: Move to magblock
        - a_delay: Bead settling
        - a_pick_up_tip: Pick up tip
        - a_aspirate: Aspirate supernatant
        - a_dispense: Dispense to waste
        - a_return_tip: Return tip
        - a_move_labware: Move back

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(wash_num, int): return False
    if not isinstance(wash_source, str): return False
    if not isinstance(waste_dest, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if wash_num < 1: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    wash_vol = state.wash_vol
    settling_time = 0.5 if state.dry_run else 2
    shake_time = 0.25 if state.dry_run else 5
    hs_available = getattr(state, 'heater_shaker_available', False)
    tip_mixing = getattr(state, 'tip_mixing', False)
    dest_after_mag = 'heater_shaker' if hs_available else 'deck_D1'
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = [
        ('a_pick_up_tip', 'pip96', 'tips'),
        ('a_aspirate', 'pip96', wash_vol, wash_source, 'A1'),
        ('a_dispense', 'pip96', wash_vol, 'sample_plate', 'A1'),
        ('a_blow_out', 'pip96'),
        ('a_air_gap', 'pip96', 10),
    ]

    if not tip_mixing:
        tasks.extend([
            ('a_return_tip', 'pip96'),
            ('a_home', 'pip96'),
        ])
    else:
        # Tip mixing: mix with tip still attached
        tasks.append(('a_mix', 'pip96', 12, wash_vol, 'sample_plate', 'A1'))
        tasks.append(('a_return_tip', 'pip96'))

    # Shake (only if heater-shaker available)
    if hs_available:
        tasks.extend([
            ('a_hs_set_shake_speed', 1800),
            ('a_delay', shake_time, f'Wash {wash_num} incubation'),
            ('a_hs_deactivate_shaker',),
        ])

    # Move to magblock
    if hs_available:
        tasks.append(('a_hs_open_latch',))
    tasks.append(('a_move_labware', 'sample_plate', 'magblock', True))
    if hs_available:
        tasks.append(('a_hs_close_latch',))

    tasks.append(('a_delay', settling_time, 'Bead settling'))

    # Remove supernatant
    tasks.extend([
        ('a_pick_up_tip', 'pip96', 'tips'),
        ('a_aspirate', 'pip96', 1000, 'sample_plate', 'A1'),
        ('a_dispense', 'pip96', 1000, waste_dest, 'A1'),
        ('a_return_tip', 'pip96'),
    ])

    # Move back to H-S or deck
    if hs_available:
        tasks.append(('a_hs_open_latch',))
    tasks.append(('a_move_labware', 'sample_plate', dest_after_mag, True))
    if hs_available:
        tasks.append(('a_hs_close_latch',))

    return tasks
    # END: Task Decomposition

# ============================================================================
# DRYING AND ELUTION METHODS
# ============================================================================

def m_dry_beads(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_dry_beads(state)

    Method parameters:
        None

    Method auxiliary parameters:
        dry_run: bool (inferred from state)

    Method purpose:
        Dry beads by air drying (simulated with delay)

    Preconditions:
        None

    Task decomposition:
        - a_delay: Wait for bead drying

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    dry_time = 0.5 if state.dry_run else 10
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [('a_delay', dry_time, 'Bead drying')]
    # END: Task Decomposition


def m_elution_phase(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_elution_phase(state)

    Method parameters:
        None

    Method auxiliary parameters:
        elution_vol: float (inferred from state)
        dry_run: bool (inferred from state)
        tip_mixing: bool (inferred from state)
        heater_shaker_available: bool (inferred from state)

    Method purpose:
        Elution: add elution buffer, mix, magnetic separate, collect DNA

    Preconditions:
        None

    Task decomposition:
        - a_pick_up_tip: Pick up tip
        - a_aspirate: Aspirate elution buffer
        - a_dispense: Dispense to sample plate
        - m_resuspend_pellet: Mix to resuspend beads
        - a_return_tip: Return tip
        - a_home: Home pipette (if not tip_mixing)
        - a_hs_set_shake_speed: Start shaking (if available)
        - a_delay: Elution incubation
        - a_hs_deactivate_shaker: Stop shaking (if available)
        - a_move_labware: Move to magblock
        - a_delay: Final bead settling
        - a_pick_up_tip: Pick up tip
        - a_aspirate: Aspirate eluate
        - a_dispense: Dispense to elution plate
        - a_return_tip: Return tip

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    elution_vol = state.elution_vol
    settling_time = 0.5 if state.dry_run else 2
    shake_time = 0.25 if state.dry_run else 5
    hs_available = getattr(state, 'heater_shaker_available', False)
    tip_mixing = getattr(state, 'tip_mixing', False)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = [
        ('a_pick_up_tip', 'pip96', 'tips1'),
        ('a_aspirate', 'pip96', elution_vol, 'elution_plate', 'A1'),
        ('a_dispense', 'pip96', elution_vol, 'sample_plate', 'A1'),
        ('m_resuspend_pellet', 'sample_plate', 'A1', elution_vol),
    ]

    # Always return tip after resuspension
    tasks.append(('a_return_tip', 'pip96'))
    if not tip_mixing:
        tasks.append(('a_home', 'pip96'))

    # Shake for elution (only if heater-shaker available)
    if hs_available:
        tasks.extend([
            ('a_hs_set_shake_speed', 2000),
            ('a_delay', shake_time, 'Elution incubation'),
            ('a_hs_deactivate_shaker',),
        ])

    # Move to magblock
    if hs_available:
        tasks.append(('a_hs_open_latch',))
    tasks.append(('a_move_labware', 'sample_plate', 'magblock', True))
    if hs_available:
        tasks.append(('a_hs_close_latch',))

    tasks.append(('a_delay', settling_time, 'Final bead settling'))

    # Transfer eluate to elution plate
    tasks.extend([
        ('a_pick_up_tip', 'pip96', 'tips1'),
        ('a_aspirate', 'pip96', elution_vol, 'sample_plate', 'A1'),
        ('a_dispense', 'pip96', elution_vol, 'elution_plate', 'A1'),
        ('a_return_tip', 'pip96'),
    ])

    return tasks
    # END: Task Decomposition


# ============================================================================
# HELPER METHODS
# ============================================================================

def m_resuspend_pellet(state: State, labware: str, well: str, volume: float) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_resuspend_pellet(state, labware, well, volume)

    Method parameters:
        labware: Labware identifier (e.g., 'sample_plate')
        well: Well identifier (e.g., 'A1')
        volume: Total volume in well in µL

    Method auxiliary parameters:
        dry_run: bool (inferred from state)

    Method purpose:
        Resuspend pellet by mixing at multiple positions.
        Simplified version of the complex 8-position mixing in original protocol.

    Preconditions:
        None

    Task decomposition:
        - a_set_flow_rate: Set high flow rate for mixing
        - a_mix: Mix at 8 positions × reps
        - a_set_flow_rate: Reset to normal flow rate

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(labware, str): return False
    if not isinstance(well, str): return False
    if not isinstance(volume, (int, float)): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if volume <= 0: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    mix_reps = 1 if state.dry_run else 3
    mix_vol = min(volume * 0.9, 900)  # 90% of volume, max 900µL
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ('a_set_flow_rate', 'pip96', 150, 200),
        ('a_mix', 'pip96', mix_reps * 8, mix_vol, labware, well),  # 8 positions × reps
        ('a_set_flow_rate', 'pip96', 50, 150),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

declare_task_methods('m_hdq_dna_extraction', m_hdq_dna_extraction)
declare_task_methods('m_initialize_protocol', m_initialize_protocol)
declare_task_methods('m_finalize_protocol', m_finalize_protocol)
declare_task_methods('m_tl_lysis_phase', m_tl_lysis_phase)
declare_task_methods('m_transfer_sample_to_new_plate', m_transfer_sample_to_new_plate)
declare_task_methods('m_al_lysis_phase', m_al_lysis_phase)
declare_task_methods('m_bead_binding_phase', m_bead_binding_phase)
declare_task_methods('m_magnetic_separation_initial', m_magnetic_separation_initial)
declare_task_methods('m_remove_supernatant', m_remove_supernatant)
declare_task_methods('m_wash_all_cycles', m_wash_all_cycles)
declare_task_methods('m_single_wash_cycle', m_single_wash_cycle)
declare_task_methods('m_dry_beads', m_dry_beads)
declare_task_methods('m_elution_phase', m_elution_phase)
declare_task_methods('m_resuspend_pellet', m_resuspend_pellet)

