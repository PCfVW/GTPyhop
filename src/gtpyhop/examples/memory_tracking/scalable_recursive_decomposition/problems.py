"""
Problem definitions for the Scalable Recursive Decomposition example.

This file defines initial states for memory tracking demonstration via
recursive method decomposition following Alford et al. (2015) Theorem 4.1.

Theoretical Foundation:
    For recursion depth k, the method structure produces exactly 2^k leaf tasks.
    Total plan length = 2^k + 2 actions (initialize + 2^k leaves + finalize).

Memory Accumulation Model:
    Each leaf task appends config_payload_size bytes to state.results.
    Expected peak memory = 2^k × config_payload_size bytes (plus overhead).
    Example: depth 8 with 100KB payload → 256 × 100KB = 25.6 MB

Configuration Options (via state properties):
    - config_depth: int - Recursion depth k (yields 2^k leaf tasks)
    - config_payload_size: int - Bytes appended per leaf task execution

Scenarios (12 total):
    Group A (scenario_01-06): Depth scaling with fixed 1KB payload
    Group B (scenario_07-10): Payload scaling with fixed depth 8
    Group C (scenario_11-12): Combined scaling for stress testing

Note on Measurement:
    Use --sampling-interval 0.001 for fast scenarios (<100ms) to capture peaks.
    Use --disable-gc to prevent garbage collection during measurement.
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
    """Create a base state for recursive decomposition demonstration."""
    state = State(name)
    state.initialized = False
    state.execution_complete = False
    state.task_count = 0
    # Default configuration (can be overridden per scenario)
    state.config_depth = 4
    state.config_payload_size = 1024  # 1KB default
    return state


def h_create_configured_state(
    name: str,
    depth: int = 4,
    payload_size: int = 1024
) -> State:
    """Create a state with specific configuration for recursive decomposition."""
    state = h_create_base_state(name)
    state.config_depth = depth
    state.config_payload_size = payload_size
    return state


def h_calculate_plan_length(depth: int) -> int:
    """Calculate expected plan length for given depth: 2^depth + 2."""
    return (2 ** depth) + 2


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: scalable_recursive_decomposition

# ============================================================================
# GROUP A: DEPTH SCALING (scenario_01 to scenario_06)
# Fixed payload (1KB), varying recursion depth
# Demonstrates exponential task growth: 2^k leaf tasks for depth k
# ============================================================================

# BEGIN: Scenario: scenario_01
# Configuration: Depth 4, baseline
_depth = 4
_payload_size = 1024  # 1KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_01 = h_create_configured_state(
    'scenario_01',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_01'] = (
    initial_state_scenario_01,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 1KB payload'
)
# END: Scenario

# BEGIN: Scenario: scenario_02
# Configuration: Depth 6, light scaling
_depth = 6
_payload_size = 1024  # 1KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_02 = h_create_configured_state(
    'scenario_02',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_02'] = (
    initial_state_scenario_02,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 1KB payload'
)
# END: Scenario

# BEGIN: Scenario: scenario_03
# Configuration: Depth 8, medium scaling
_depth = 8
_payload_size = 1024  # 1KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_03 = h_create_configured_state(
    'scenario_03',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_03'] = (
    initial_state_scenario_03,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 1KB payload'
)
# END: Scenario

# BEGIN: Scenario: scenario_04
# Configuration: Depth 10, heavy scaling
_depth = 10
_payload_size = 1024  # 1KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_04 = h_create_configured_state(
    'scenario_04',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_04'] = (
    initial_state_scenario_04,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 1KB payload'
)
# END: Scenario

# BEGIN: Scenario: scenario_05
# Configuration: Depth 12, stress test
_depth = 12
_payload_size = 1024  # 1KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_05 = h_create_configured_state(
    'scenario_05',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_05'] = (
    initial_state_scenario_05,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 1KB payload'
)
# END: Scenario

# BEGIN: Scenario: scenario_06
# Configuration: Depth 14, extreme (USE WITH CAUTION)
_depth = 14
_payload_size = 1024  # 1KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_06 = h_create_configured_state(
    'scenario_06',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_06'] = (
    initial_state_scenario_06,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 1KB payload (EXTREME)'
)
# END: Scenario

# ============================================================================
# GROUP B: PAYLOAD SCALING (scenario_07 to scenario_10)
# Fixed depth (8 = 256 tasks), varying payload size
# Each leaf task appends payload_size bytes to state.results, so memory
# accumulates as: 256 tasks × payload_size.
# Expected: scenario_10 (100KB) should show ~25.6 MB peak memory.
# Note: Use --sampling-interval 0.001 --disable-gc to capture peaks accurately.
# ============================================================================

# BEGIN: Scenario: scenario_07
# Configuration: Depth 8, minimal payload
_depth = 8
_payload_size = 100  # 100 bytes
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_07 = h_create_configured_state(
    'scenario_07',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_07'] = (
    initial_state_scenario_07,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 100B payload'
)
# END: Scenario

# BEGIN: Scenario: scenario_08
# Configuration: Depth 8, standard payload (same as scenario_03)
_depth = 8
_payload_size = 1024  # 1KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_08 = h_create_configured_state(
    'scenario_08',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_08'] = (
    initial_state_scenario_08,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 1KB payload'
)
# END: Scenario

# BEGIN: Scenario: scenario_09
# Configuration: Depth 8, large payload
_depth = 8
_payload_size = 10240  # 10KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_09 = h_create_configured_state(
    'scenario_09',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_09'] = (
    initial_state_scenario_09,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 10KB payload'
)
# END: Scenario

# BEGIN: Scenario: scenario_10
# Configuration: Depth 8, heavy payload
_depth = 8
_payload_size = 102400  # 100KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_10 = h_create_configured_state(
    'scenario_10',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_10'] = (
    initial_state_scenario_10,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 100KB payload'
)
# END: Scenario

# ============================================================================
# GROUP C: COMBINED SCALING (scenario_11 to scenario_12)
# Higher depth with larger payload for stress testing
# ============================================================================

# BEGIN: Scenario: scenario_11
# Configuration: Depth 10, large payload
_depth = 10
_payload_size = 10240  # 10KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_11 = h_create_configured_state(
    'scenario_11',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_11'] = (
    initial_state_scenario_11,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 10KB payload (STRESS)'
)
# END: Scenario

# BEGIN: Scenario: scenario_12
# Configuration: Depth 12, large payload (maximum practical)
_depth = 12
_payload_size = 10240  # 10KB
_expected_tasks = 2 ** _depth
_expected_plan = h_calculate_plan_length(_depth)
initial_state_scenario_12 = h_create_configured_state(
    'scenario_12',
    depth=_depth,
    payload_size=_payload_size
)
problems['scenario_12'] = (
    initial_state_scenario_12,
    [('m_recursive_decomposition', _depth)],
    f'Depth {_depth}: {_expected_tasks} leaf tasks, {_expected_plan} actions, 10KB payload (MAX)'
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
