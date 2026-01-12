"""
Problem definitions for the Scalable Data Processing example.
-- Generated 2026-01-09

This file defines initial states for memory tracking demonstration workflow.
The workflow demonstrates memory usage scaling with different data sizes
and configurable memory-greedy behavior.

Configuration Options (via state properties):
  - config_data_type: 'int' (~28 bytes), 'string' (~500 bytes), 'dict' (~1KB+)
  - config_num_transforms: 1-16 (number of transformation copies)
  - config_accumulate: True/False (keep intermediate results)
  - config_cleanup: True/False (release memory at end)

Scenarios (20 total):
  - scenario_01-05: Small scenarios with increasing data types
  - scenario_06-10: Medium scenarios with transformations
  - scenario_11-15: Large scenarios with accumulation
  - scenario_16-20: Memory-intensive scenarios (no cleanup, dict, accumulate)
"""

import sys
import os

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
# HELPER FUNCTIONS
# ============================================================================

def h_create_base_state(name: str) -> State:
    """Create a base state for memory tracking demonstration."""
    state = State(name)
    state.demo_initialized = False
    state.dataset_allocated = False
    state.structure_created = False
    state.operations_complete = False
    state.memory_cleaned = False
    # Default configuration (can be overridden per scenario)
    state.config_data_type = 'int'
    state.config_num_transforms = 4
    state.config_accumulate = False
    state.config_cleanup = True
    return state


def h_create_configured_state(
    name: str,
    data_type: str = 'int',
    num_transforms: int = 4,
    accumulate: bool = False,
    cleanup: bool = True
) -> State:
    """Create a state with specific configuration for memory behavior."""
    state = h_create_base_state(name)
    state.config_data_type = data_type
    state.config_num_transforms = num_transforms
    state.config_accumulate = accumulate
    state.config_cleanup = cleanup
    return state

# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: scalable_data_processing

# ============================================================================
# SMALL SCENARIOS (scenario_01 to scenario_05)
# Testing different data types with small data sizes
# ============================================================================

# BEGIN: Scenario: scenario_01
# Configuration: Small int baseline
_data_size = 10000  # 10K data points
initial_state_scenario_01 = h_create_configured_state(
    'scenario_01',
    data_type='int',
    num_transforms=2,
    accumulate=False,
    cleanup=True
)
problems['scenario_01'] = (
    initial_state_scenario_01,
    [('m_memory_tracking_demo', _data_size)],
    '10K int, 2 transforms, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_02
# Configuration: Small string (memory increase)
_data_size = 10000  # 10K data points
initial_state_scenario_02 = h_create_configured_state(
    'scenario_02',
    data_type='string',
    num_transforms=2,
    accumulate=False,
    cleanup=True
)
problems['scenario_02'] = (
    initial_state_scenario_02,
    [('m_memory_tracking_demo', _data_size)],
    '10K string (~5MB), 2 transforms, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_03
# Configuration: Small dict (highest memory per item)
_data_size = 10000  # 10K data points
initial_state_scenario_03 = h_create_configured_state(
    'scenario_03',
    data_type='dict',
    num_transforms=2,
    accumulate=False,
    cleanup=True
)
problems['scenario_03'] = (
    initial_state_scenario_03,
    [('m_memory_tracking_demo', _data_size)],
    '10K dict (~10MB), 2 transforms, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_04
# Configuration: Small dict with accumulation
_data_size = 10000  # 10K data points
initial_state_scenario_04 = h_create_configured_state(
    'scenario_04',
    data_type='dict',
    num_transforms=4,
    accumulate=True,
    cleanup=True
)
problems['scenario_04'] = (
    initial_state_scenario_04,
    [('m_memory_tracking_demo', _data_size)],
    '10K dict, 4 transforms, accumulate, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_05
# Configuration: Small dict, no cleanup
_data_size = 10000  # 10K data points
initial_state_scenario_05 = h_create_configured_state(
    'scenario_05',
    data_type='dict',
    num_transforms=4,
    accumulate=True,
    cleanup=False
)
problems['scenario_05'] = (
    initial_state_scenario_05,
    [('m_memory_tracking_demo', _data_size)],
    '10K dict, 4 transforms, accumulate, NO cleanup'
)
# END: Scenario

# ============================================================================
# MEDIUM SCENARIOS (scenario_06 to scenario_10)
# Testing scaling with medium data sizes
# ============================================================================

# BEGIN: Scenario: scenario_06
# Configuration: Medium string baseline
_data_size = 50000  # 50K data points
initial_state_scenario_06 = h_create_configured_state(
    'scenario_06',
    data_type='string',
    num_transforms=4,
    accumulate=False,
    cleanup=True
)
problems['scenario_06'] = (
    initial_state_scenario_06,
    [('m_memory_tracking_demo', _data_size)],
    '50K string (~25MB), 4 transforms, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_07
# Configuration: Medium dict
_data_size = 50000  # 50K data points
initial_state_scenario_07 = h_create_configured_state(
    'scenario_07',
    data_type='dict',
    num_transforms=4,
    accumulate=False,
    cleanup=True
)
problems['scenario_07'] = (
    initial_state_scenario_07,
    [('m_memory_tracking_demo', _data_size)],
    '50K dict (~50MB), 4 transforms, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_08
# Configuration: Medium dict with accumulation
_data_size = 50000  # 50K data points
initial_state_scenario_08 = h_create_configured_state(
    'scenario_08',
    data_type='dict',
    num_transforms=8,
    accumulate=True,
    cleanup=True
)
problems['scenario_08'] = (
    initial_state_scenario_08,
    [('m_memory_tracking_demo', _data_size)],
    '50K dict, 8 transforms, accumulate, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_09
# Configuration: Medium dict, no cleanup
_data_size = 50000  # 50K data points
initial_state_scenario_09 = h_create_configured_state(
    'scenario_09',
    data_type='dict',
    num_transforms=8,
    accumulate=True,
    cleanup=False
)
problems['scenario_09'] = (
    initial_state_scenario_09,
    [('m_memory_tracking_demo', _data_size)],
    '50K dict, 8 transforms, accumulate, NO cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_10
# Configuration: Medium dict, max transforms, no cleanup (MEMORY EATER)
_data_size = 100000  # 100K data points
initial_state_scenario_10 = h_create_configured_state(
    'scenario_10',
    data_type='dict',
    num_transforms=16,
    accumulate=True,
    cleanup=False
)
problems['scenario_10'] = (
    initial_state_scenario_10,
    [('m_memory_tracking_demo', _data_size)],
    '100K dict, 16 transforms, accumulate, NO cleanup (~100MB+)'
)
# END: Scenario

# ============================================================================
# LARGE SCENARIOS (scenario_11 to scenario_15)
# Testing larger data sizes with various configurations
# ============================================================================

# BEGIN: Scenario: scenario_11
# Configuration: Large string
_data_size = 200000  # 200K data points
initial_state_scenario_11 = h_create_configured_state(
    'scenario_11',
    data_type='string',
    num_transforms=4,
    accumulate=True,
    cleanup=True
)
problems['scenario_11'] = (
    initial_state_scenario_11,
    [('m_memory_tracking_demo', _data_size)],
    '200K string (~100MB), 4 transforms, accumulate, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_12
# Configuration: Large dict baseline
_data_size = 200000  # 200K data points
initial_state_scenario_12 = h_create_configured_state(
    'scenario_12',
    data_type='dict',
    num_transforms=4,
    accumulate=False,
    cleanup=True
)
problems['scenario_12'] = (
    initial_state_scenario_12,
    [('m_memory_tracking_demo', _data_size)],
    '200K dict (~200MB), 4 transforms, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_13
# Configuration: Large dict with accumulation
_data_size = 200000  # 200K data points
initial_state_scenario_13 = h_create_configured_state(
    'scenario_13',
    data_type='dict',
    num_transforms=8,
    accumulate=True,
    cleanup=True
)
problems['scenario_13'] = (
    initial_state_scenario_13,
    [('m_memory_tracking_demo', _data_size)],
    '200K dict, 8 transforms, accumulate, cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_14
# Configuration: Large dict, no cleanup
_data_size = 200000  # 200K data points
initial_state_scenario_14 = h_create_configured_state(
    'scenario_14',
    data_type='dict',
    num_transforms=8,
    accumulate=True,
    cleanup=False
)
problems['scenario_14'] = (
    initial_state_scenario_14,
    [('m_memory_tracking_demo', _data_size)],
    '200K dict, 8 transforms, accumulate, NO cleanup'
)
# END: Scenario

# BEGIN: Scenario: scenario_15
# Configuration: Large dict, max settings (HEAVY MEMORY)
_data_size = 300000  # 300K data points
initial_state_scenario_15 = h_create_configured_state(
    'scenario_15',
    data_type='dict',
    num_transforms=16,
    accumulate=True,
    cleanup=False
)
problems['scenario_15'] = (
    initial_state_scenario_15,
    [('m_memory_tracking_demo', _data_size)],
    '300K dict, 16 transforms, accumulate, NO cleanup (~300MB+)'
)
# END: Scenario

# ============================================================================
# MEMORY-INTENSIVE SCENARIOS (scenario_16 to scenario_20)
# Maximum memory consumption for stress testing
# ============================================================================

# BEGIN: Scenario: scenario_16
# Configuration: Very large dict
_data_size = 500000  # 500K data points
initial_state_scenario_16 = h_create_configured_state(
    'scenario_16',
    data_type='dict',
    num_transforms=8,
    accumulate=True,
    cleanup=False
)
problems['scenario_16'] = (
    initial_state_scenario_16,
    [('m_memory_tracking_demo', _data_size)],
    '500K dict, 8 transforms, accumulate, NO cleanup (~500MB+)'
)
# END: Scenario

# BEGIN: Scenario: scenario_17
# Configuration: Very large with max transforms
_data_size = 500000  # 500K data points
initial_state_scenario_17 = h_create_configured_state(
    'scenario_17',
    data_type='dict',
    num_transforms=16,
    accumulate=True,
    cleanup=False
)
problems['scenario_17'] = (
    initial_state_scenario_17,
    [('m_memory_tracking_demo', _data_size)],
    '500K dict, 16 transforms, accumulate, NO cleanup (~800MB+)'
)
# END: Scenario

# BEGIN: Scenario: scenario_18
# Configuration: Large scale stress test
_data_size = 750000  # 750K data points
initial_state_scenario_18 = h_create_configured_state(
    'scenario_18',
    data_type='dict',
    num_transforms=12,
    accumulate=True,
    cleanup=False
)
problems['scenario_18'] = (
    initial_state_scenario_18,
    [('m_memory_tracking_demo', _data_size)],
    '750K dict, 12 transforms, accumulate, NO cleanup (~1GB)'
)
# END: Scenario

# BEGIN: Scenario: scenario_19
# Configuration: Maximum practical load
_data_size = 1000000  # 1M data points
initial_state_scenario_19 = h_create_configured_state(
    'scenario_19',
    data_type='dict',
    num_transforms=8,
    accumulate=True,
    cleanup=False
)
problems['scenario_19'] = (
    initial_state_scenario_19,
    [('m_memory_tracking_demo', _data_size)],
    '1M dict, 8 transforms, accumulate, NO cleanup (~1GB+)'
)
# END: Scenario

# BEGIN: Scenario: scenario_20
# Configuration: Extreme stress test (USE WITH CAUTION)
_data_size = 1000000  # 1M data points
initial_state_scenario_20 = h_create_configured_state(
    'scenario_20',
    data_type='dict',
    num_transforms=16,
    accumulate=True,
    cleanup=False
)
problems['scenario_20'] = (
    initial_state_scenario_20,
    [('m_memory_tracking_demo', _data_size)],
    '1M dict, 16 transforms, accumulate, NO cleanup (~2GB+)'
)
# END: Scenario

# END: Domain

def get_problems():
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
