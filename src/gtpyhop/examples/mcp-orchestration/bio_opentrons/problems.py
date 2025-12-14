"""
Problem definitions for the Bio-Opentrons Flex HTN Domain.
-- Generated 2025-12-09

This file defines initial states for cross-server PCR workflow orchestration.
The workflow demonstrates coordination between three MCP servers:
  - Server 1 (movement-server): Pipette movement and tip operations
  - Server 2 (liquid-server): Liquid handling operations
  - Server 3 (module-server): Temperature module control

Scenarios (with dynamic sample scaling):
  - scenario_1: 4 samples, 25 cycles -> 55 actions
  - scenario_2: 8 samples, 30 cycles -> 79 actions
  - scenario_3: 16 samples, 35 cycles -> 127 actions
  - scenario_4: 32 samples, 25 cycles -> 223 actions
  - scenario_5: 48 samples, 30 cycles -> 321 actions
  - scenario_6: 96 samples, 35 cycles -> 611 actions

Note: Maximum 96 samples due to 96-well plate hardware constraint.
Plan length formula: 31 + 6 × num_samples + 2 × (ceil(num_samples/40) - 1)
"""

import sys
import os
from typing import Dict, Tuple, List

# Secure GTPyhop import strategy
try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import State
    except ImportError as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def h_create_base_pcr_state(name: str) -> State:
    """Create a base state with common PCR workflow properties."""
    state = State(name)
    state.deck_slots = {}
    state.pipette_ready = {'left': False, 'right': False}
    state.pipette_has_tip = {'left': False, 'right': False}
    state.well_contents = {}
    state.thermocycler_lid_open = True
    state.thermocycler_temperature = 22.0
    state.thermocycler_profile_complete = False
    state.temperature_module_temp = 22.0
    state.heater_shaker_active = False
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: bio_opentrons

# BEGIN: Scenario: scenario_1
# Configuration
_samples, _cycles = 4, 25

# State
initial_state_scenario_1 = h_create_base_pcr_state('scenario_1')
initial_state_scenario_1.num_samples = _samples
initial_state_scenario_1.num_cycles = _cycles
initial_state_scenario_1.protocol_type = 'standard_pcr'

# Problem
problems['scenario_1'] = (
    initial_state_scenario_1,
    [('m_initialize_and_run_pcr', _samples, _cycles)],
    f'PCR: {_samples} samples, {_cycles} cycles -> 55 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2
# Configuration
_samples, _cycles = 8, 30

# State
initial_state_scenario_2 = h_create_base_pcr_state('scenario_2')
initial_state_scenario_2.num_samples = _samples
initial_state_scenario_2.num_cycles = _cycles
initial_state_scenario_2.protocol_type = 'standard_pcr'

# Problem
problems['scenario_2'] = (
    initial_state_scenario_2,
    [('m_initialize_and_run_pcr', _samples, _cycles)],
    f'PCR: {_samples} samples, {_cycles} cycles -> 79 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3
# Configuration
_samples, _cycles = 16, 35

# State
initial_state_scenario_3 = h_create_base_pcr_state('scenario_3')
initial_state_scenario_3.num_samples = _samples
initial_state_scenario_3.num_cycles = _cycles
initial_state_scenario_3.protocol_type = 'standard_pcr'

# Problem
problems['scenario_3'] = (
    initial_state_scenario_3,
    [('m_initialize_and_run_pcr', _samples, _cycles)],
    f'PCR: {_samples} samples, {_cycles} cycles -> 127 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_4
# Configuration
_samples, _cycles = 32, 25

# State
initial_state_scenario_4 = h_create_base_pcr_state('scenario_4')
initial_state_scenario_4.num_samples = _samples
initial_state_scenario_4.num_cycles = _cycles
initial_state_scenario_4.protocol_type = 'standard_pcr'

# Problem
problems['scenario_4'] = (
    initial_state_scenario_4,
    [('m_initialize_and_run_pcr', _samples, _cycles)],
    f'PCR: {_samples} samples, {_cycles} cycles -> 223 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_5
# Configuration
_samples, _cycles = 48, 30

# State
initial_state_scenario_5 = h_create_base_pcr_state('scenario_5')
initial_state_scenario_5.num_samples = _samples
initial_state_scenario_5.num_cycles = _cycles
initial_state_scenario_5.protocol_type = 'standard_pcr'

# Problem
problems['scenario_5'] = (
    initial_state_scenario_5,
    [('m_initialize_and_run_pcr', _samples, _cycles)],
    f'PCR: {_samples} samples, {_cycles} cycles -> 321 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_6
# Configuration
_samples, _cycles = 96, 35

# State
initial_state_scenario_6 = h_create_base_pcr_state('scenario_6')
initial_state_scenario_6.num_samples = _samples
initial_state_scenario_6.num_cycles = _cycles
initial_state_scenario_6.protocol_type = 'high_throughput_pcr'

# Problem
problems['scenario_6'] = (
    initial_state_scenario_6,
    [('m_initialize_and_run_pcr', _samples, _cycles)],
    f'PCR: {_samples} samples (full plate), {_cycles} cycles -> 611 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems