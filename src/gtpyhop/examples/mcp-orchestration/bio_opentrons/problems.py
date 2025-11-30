"""
Problem definitions for the Bio-Opentrons Flex HTN Domain.
-- Generated 2025-11-30

This file defines initial states for cross-server PCR workflow orchestration.
The workflow demonstrates coordination between three MCP servers:
  - Server 1 (movement-server): Pipette movement and tip operations
  - Server 2 (liquid-server): Liquid handling operations
  - Server 3 (module-server): Temperature module control

Problem Scenarios (with dynamic sample scaling):
  - Scenario 1: 4 samples, 25 cycles   -> 55 actions
  - Scenario 2: 8 samples, 30 cycles   -> 79 actions
  - Scenario 3: 16 samples, 35 cycles  -> 127 actions
  - Scenario 4: 32 samples, 25 cycles  -> 223 actions
  - Scenario 5: 48 samples, 30 cycles  -> 321 actions (+2 for extra aspirate)
  - Scenario 6: 96 samples, 35 cycles  -> 611 actions (+4 for extra aspirates)

Note: Maximum 96 samples due to 96-well plate hardware constraint (8 rows × 12 columns).

Plan length formula: 31 + 6 × num_samples + 2 × (ceil(num_samples/40) - 1)
  - Base: 31 + 6 × num_samples
  - Extra aspirate cycles: For >40 samples, pipette max (1000 µL) at 25 µL/sample
    requires additional aspirate cycles, each adding 2 actions.
"""

import sys
import os

# Secure GTPyhop import strategy
try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    # Fallback to local development
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import State
    except ImportError as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)


# ============================================================================
# HELPER FUNCTION: Create base PCR state
# ============================================================================

def create_base_pcr_state(name: str) -> State:
    """Create a base state with common PCR workflow properties."""
    state = State(name)
    
    # Server readiness (will be set by a_initialize_servers)
    # These are not set initially - the plan will initialize them
    
    # Deck layout (empty initially - will be populated by labware loading)
    state.deck_slots = {}
    
    # Pipette state (empty initially - will be set by pipette loading)
    state.pipette_ready = {'left': False, 'right': False}
    state.pipette_has_tip = {'left': False, 'right': False}
    
    # Well contents tracking (simplified)
    state.well_contents = {}
    
    # Module states
    state.thermocycler_lid_open = True  # Start with lid open
    state.thermocycler_temperature = 22.0  # Room temperature
    state.thermocycler_profile_complete = False
    state.temperature_module_temp = 22.0
    state.heater_shaker_active = False
    
    return state


# ============================================================================
# PROBLEM
# ============================================================================

# BEGIN: Domain: bio_opentrons

# BEGIN: Initial State: pcr_4samples_25cycles
# ===== [SCENARIO 1] PCR: 4 samples, 25 cycles -> 55 actions =================
initial_state_scenario_1 = create_base_pcr_state('pcr_4samples_25cycles')
initial_state_scenario_1.num_samples = 4
initial_state_scenario_1.num_cycles = 25
initial_state_scenario_1.protocol_type = 'standard_pcr'
# END: Initial State

# BEGIN: Initial State: pcr_8samples_30cycles
# ===== [SCENARIO 2] PCR: 8 samples, 30 cycles -> 79 actions =================
initial_state_scenario_2 = create_base_pcr_state('pcr_8samples_30cycles')
initial_state_scenario_2.num_samples = 8
initial_state_scenario_2.num_cycles = 30
initial_state_scenario_2.protocol_type = 'standard_pcr'
# END: Initial State

# BEGIN: Initial State: pcr_16samples_35cycles
# ===== [SCENARIO 3] PCR: 16 samples, 35 cycles -> 127 actions ===============
initial_state_scenario_3 = create_base_pcr_state('pcr_16samples_35cycles')
initial_state_scenario_3.num_samples = 16
initial_state_scenario_3.num_cycles = 35
initial_state_scenario_3.protocol_type = 'standard_pcr'
# END: Initial State

# BEGIN: Initial State: pcr_32samples_25cycles
# ===== [SCENARIO 4] PCR: 32 samples, 25 cycles -> 223 actions ===============
initial_state_scenario_4 = create_base_pcr_state('pcr_32samples_25cycles')
initial_state_scenario_4.num_samples = 32
initial_state_scenario_4.num_cycles = 25
initial_state_scenario_4.protocol_type = 'standard_pcr'
# END: Initial State

# BEGIN: Initial State: pcr_48samples_30cycles
# ===== [SCENARIO 5] PCR: 48 samples, 30 cycles -> 321 actions ===============
initial_state_scenario_5 = create_base_pcr_state('pcr_48samples_30cycles')
initial_state_scenario_5.num_samples = 48
initial_state_scenario_5.num_cycles = 30
initial_state_scenario_5.protocol_type = 'standard_pcr'
# END: Initial State

# BEGIN: Initial State: pcr_96samples_35cycles
# ===== [SCENARIO 6] PCR: 96 samples, 35 cycles -> 611 actions ===============
initial_state_scenario_6 = create_base_pcr_state('pcr_96samples_35cycles')
initial_state_scenario_6.num_samples = 96
initial_state_scenario_6.num_cycles = 35
initial_state_scenario_6.protocol_type = 'high_throughput_pcr'
# END: Initial State

# END: Domain


# ============================================================================
# PROBLEM DEFINITIONS FOR BENCHMARKING
# ============================================================================

# Each problem is a tuple of (initial_state, task_list, description)
problems = {
    'scenario_1_4samples': (
        initial_state_scenario_1,
        [('m_initialize_and_run_pcr', 4, 25)],
        'PCR: 4 samples, 25 cycles -> 55 actions'
    ),
    'scenario_2_8samples': (
        initial_state_scenario_2,
        [('m_initialize_and_run_pcr', 8, 30)],
        'PCR: 8 samples, 30 cycles -> 79 actions'
    ),
    'scenario_3_16samples': (
        initial_state_scenario_3,
        [('m_initialize_and_run_pcr', 16, 35)],
        'PCR: 16 samples, 35 cycles -> 127 actions'
    ),
    'scenario_4_32samples': (
        initial_state_scenario_4,
        [('m_initialize_and_run_pcr', 32, 25)],
        'PCR: 32 samples, 25 cycles -> 223 actions'
    ),
    'scenario_5_48samples': (
        initial_state_scenario_5,
        [('m_initialize_and_run_pcr', 48, 30)],
        'PCR: 48 samples, 30 cycles -> 321 actions'
    ),
    'scenario_6_96samples': (
        initial_state_scenario_6,
        [('m_initialize_and_run_pcr', 96, 35)],
        'PCR: 96 samples (full plate), 35 cycles -> 611 actions'
    )
}


def get_problems():
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems

