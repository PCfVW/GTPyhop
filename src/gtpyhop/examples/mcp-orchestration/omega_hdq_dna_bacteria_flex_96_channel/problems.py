"""
Problem definitions for Omega HDQ DNA Bacteria Extraction Domain.

This file defines initial states for multi-server DNA extraction workflow orchestration.
The workflow demonstrates coordination between four MCP servers:
  - Server 1 (htn-planning-server): HTN planning with GTPyhop
  - Server 2 (liquid-handling-server): Pipetting operations (96-channel)
  - Server 3 (module-control-server): Heater-shaker, temp module, magnetic block
  - Server 4 (gripper-server): Labware transfers

Problem Scenarios:
  - Scenario 1: Standard extraction (heater-shaker, 3 washes)  -> 129 actions
  - Scenario 2: Dry run mode (1 wash, reduced timings)         -> 91 actions
  - Scenario 3: Manual mixing mode (no heater-shaker)          -> 89 actions

Based on Opentrons Flex protocol by Zach Galluzzo.
-- Generated 2025-11-29
"""

import sys
import os

# Smart import
try:
    import gtpyhop
except ImportError:
    sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
    import gtpyhop


def create_base_state(name: str) -> gtpyhop.State:
    """Create a base state with common properties."""
    state = gtpyhop.State(name)
    
    # ========================================
    # Labware and Deck Layout
    # ========================================
    state.labware_position = {
        'TL_plate': 'heater_shaker',      # Sample Plate 1 on H-S
        'sample_plate': 'deck_C3',         # Sample Plate 2
        'TL_reservoir': 'deck_D2',         # TL buffer reservoir
        'AL_reservoir': 'deck_C2',         # AL buffer reservoir
        'wash1_reservoir': 'deck_B1',      # VHB wash buffer
        'wash2_reservoir': 'deck_B2',      # SPM wash buffer
        'bind_reservoir': 'deck_B3',       # Beads + binding buffer
        'elution_plate': 'temp_module',    # Elution plate on temp module
        'tips': 'deck_A1',                 # Tip rack 1
        'tips1': 'deck_A2',                # Tip rack 2
    }
    
    state.on_magnet = {
        'TL_plate': False,
        'sample_plate': False,
    }
    
    # ========================================
    # Pipette State
    # ========================================
    state.has_tip = {'pip96': False}
    state.pipette_volume = {'pip96': 0.0}
    state.pipette_homed = {'pip96': False}
    state.flow_rate = {'pip96': {'aspirate': 50, 'dispense': 150}}
    state.tips_used = 0
    
    # ========================================
    # Well Volumes (initial)
    # ========================================
    state.well_volume = {
        'TL_reservoir': {'A1': 270},       # TL_vol + PK_vol + extra
        'AL_reservoir': {'A1': 330},       # AL_vol + extra
        'wash1_reservoir': {'A1': 1300},   # 2 × wash_vol + extra
        'wash2_reservoir': {'A1': 700},    # wash_vol + extra
        'bind_reservoir': {'A1': 440},     # bind_vol + bead_vol + extra
        'elution_plate': {'A1': 105},      # elution_vol + extra
        'sample_plate': {'A1': 200},       # Initial sample volume
        'TL_plate': {'A1': 0},
    }
    state.well_mixed = {}
    
    # ========================================
    # Module States
    # ========================================
    state.heater_shaker_available = True
    state.hs_target_temp = 22.0
    state.hs_at_temp = False
    state.hs_shake_speed = 0
    state.hs_shaking = False
    state.hs_latch_open = False
    
    state.temp_module_available = True
    state.temp_module_temp = 22.0
    state.temp_at_temp = False
    
    state.gripper_available = True
    
    # ========================================
    # Protocol Configuration
    # ========================================
    state.dry_run = False
    state.tip_mixing = False
    state.num_washes = 3
    
    # Volumes (µL)
    state.tl_vol = 250
    state.pk_vol = 20
    state.al_vol = 230
    state.sample_vol = 200
    state.bind_vol = 320
    state.bead_vol = 20
    state.wash_vol = 600
    state.elution_vol = 100
    
    # Timing
    state.total_delay_minutes = 0.0
    
    return state


# ============================================================================
# PROBLEM
# ============================================================================

# BEGIN: Domain: omega_hdq_dna_bacteria_flex_96_channel

# BEGIN: Initial State: hdq_standard
# ===== [SCENARIO 1] Standard Extraction (heater-shaker, 3 washes) -> 129 actions
initial_state_scenario_1_standard = create_base_state('hdq_standard')
# Uses all defaults: heater_shaker=True, dry_run=False, num_washes=3
# END: Initial State

# BEGIN: Initial State: hdq_dry_run
# ===== [SCENARIO 2] Dry Run Mode (1 wash, reduced timings) -> 91 actions ====
initial_state_scenario_2_dry_run = create_base_state('hdq_dry_run')
initial_state_scenario_2_dry_run.dry_run = True
initial_state_scenario_2_dry_run.num_washes = 1
# END: Initial State

# BEGIN: Initial State: hdq_manual_mixing
# ===== [SCENARIO 3] Manual Mixing Mode (no heater-shaker) -> 89 actions =====
initial_state_scenario_3_manual_mixing = create_base_state('hdq_manual_mixing')
initial_state_scenario_3_manual_mixing.heater_shaker_available = False
initial_state_scenario_3_manual_mixing.tip_mixing = True
# Update labware position for non-heater-shaker mode
initial_state_scenario_3_manual_mixing.labware_position['TL_plate'] = 'deck_slot_6'
initial_state_scenario_3_manual_mixing.labware_position['sample_plate'] = 'deck_D1'
# END: Initial State

# END: Domain


# ============================================================================
# PROBLEM DEFINITIONS FOR BENCHMARKING
# ============================================================================

# Each problem is a tuple of (initial_state, task_list, description)
problems = {
    'scenario_1_standard': (
        initial_state_scenario_1_standard,
        [('m_hdq_dna_extraction',)],
        'HDQ DNA extraction: standard (heater-shaker, 3 washes) -> 129 actions'
    ),
    'scenario_2_dry_run': (
        initial_state_scenario_2_dry_run,
        [('m_hdq_dna_extraction',)],
        'HDQ DNA extraction: dry run (1 wash, reduced timings) -> 91 actions'
    ),
    'scenario_3_manual_mixing': (
        initial_state_scenario_3_manual_mixing,
        [('m_hdq_dna_extraction',)],
        'HDQ DNA extraction: manual mixing (no heater-shaker) -> 89 actions'
    )
}


def get_problems():
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
