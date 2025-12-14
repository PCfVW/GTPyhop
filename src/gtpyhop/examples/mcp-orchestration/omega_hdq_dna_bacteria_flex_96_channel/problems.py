"""
Problem definitions for Omega HDQ DNA Bacteria Extraction Domain.
-- Generated 2025-12-09

This file defines initial states for multi-server DNA extraction workflow orchestration.
The workflow demonstrates coordination between four MCP servers:
  - Server 1 (htn-planning-server): HTN planning with GTPyhop
  - Server 2 (liquid-handling-server): Pipetting operations (96-channel)
  - Server 3 (module-control-server): Heater-shaker, temp module, magnetic block
  - Server 4 (gripper-server): Labware transfers

Scenarios:
  - scenario_1_standard: Standard extraction (heater-shaker, 3 washes) -> 129 actions
  - scenario_2_dry_run: Dry run mode (1 wash, reduced timings) -> 91 actions
  - scenario_3_manual_mixing: Manual mixing mode (no heater-shaker) -> 89 actions

Based on Opentrons Flex protocol by Zach Galluzzo.
"""

import sys
import os
from typing import Dict, Tuple, List

# Smart import
try:
    import gtpyhop
except ImportError:
    sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
    import gtpyhop


def h_create_base_state(name: str) -> gtpyhop.State:
    """Create a base state with common properties."""
    state = gtpyhop.State(name)

    # Labware and Deck Layout
    state.labware_position = {
        'TL_plate': 'heater_shaker',
        'sample_plate': 'deck_C3',
        'TL_reservoir': 'deck_D2',
        'AL_reservoir': 'deck_C2',
        'wash1_reservoir': 'deck_B1',
        'wash2_reservoir': 'deck_B2',
        'bind_reservoir': 'deck_B3',
        'elution_plate': 'temp_module',
        'tips': 'deck_A1',
        'tips1': 'deck_A2',
    }
    state.on_magnet = {'TL_plate': False, 'sample_plate': False}

    # Pipette State
    state.has_tip = {'pip96': False}
    state.pipette_volume = {'pip96': 0.0}
    state.pipette_homed = {'pip96': False}
    state.flow_rate = {'pip96': {'aspirate': 50, 'dispense': 150}}
    state.tips_used = 0

    # Well Volumes (initial)
    state.well_volume = {
        'TL_reservoir': {'A1': 270},
        'AL_reservoir': {'A1': 330},
        'wash1_reservoir': {'A1': 1300},
        'wash2_reservoir': {'A1': 700},
        'bind_reservoir': {'A1': 440},
        'elution_plate': {'A1': 105},
        'sample_plate': {'A1': 200},
        'TL_plate': {'A1': 0},
    }
    state.well_mixed = {}

    # Module States
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

    # Protocol Configuration
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
    state.total_delay_minutes = 0.0

    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: omega_hdq_dna_bacteria_flex_96_channel

# BEGIN: Scenario: scenario_1_standard
# Configuration
_dry_run, _num_washes = False, 3
_heater_shaker = True

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_standard')
# Uses all defaults

# Problem
problems['scenario_1_standard'] = (
    initial_state_scenario_1,
    [('m_hdq_dna_extraction',)],
    f'HDQ DNA extraction: standard (heater-shaker, {_num_washes} washes) -> 129 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_dry_run
# Configuration
_dry_run, _num_washes = True, 1

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_dry_run')
initial_state_scenario_2.dry_run = _dry_run
initial_state_scenario_2.num_washes = _num_washes

# Problem
problems['scenario_2_dry_run'] = (
    initial_state_scenario_2,
    [('m_hdq_dna_extraction',)],
    f'HDQ DNA extraction: dry run ({_num_washes} wash, reduced timings) -> 91 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_manual_mixing
# Configuration
_heater_shaker_available = False
_tip_mixing = True

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_manual_mixing')
initial_state_scenario_3.heater_shaker_available = _heater_shaker_available
initial_state_scenario_3.tip_mixing = _tip_mixing
initial_state_scenario_3.labware_position['TL_plate'] = 'deck_slot_6'
initial_state_scenario_3.labware_position['sample_plate'] = 'deck_D1'

# Problem
problems['scenario_3_manual_mixing'] = (
    initial_state_scenario_3,
    [('m_hdq_dna_extraction',)],
    'HDQ DNA extraction: manual mixing (no heater-shaker) -> 89 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems