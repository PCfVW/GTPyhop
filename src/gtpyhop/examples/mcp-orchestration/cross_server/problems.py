"""
Problem definitions for the Cross-Server Robot Orchestration example.
-- Generated 2025-12-14

This file defines initial states for cross-server HTN plan execution orchestration.
The workflow demonstrates coordination between three MCP servers:
  - Server 1 (mcp-python-ingestion): HTN planning with GTPyhop
  - Server 2 (robot-server): Robot gripper actions (mock)
  - Server 3 (motion-server): Arm motion planning (mock)

Scenarios:
  - scenario_1_pick_and_place: Move block_a from table to shelf -> 9 actions
  - scenario_2_multi_transfer: Move block_a and block_b to shelf -> 15 actions
"""

import sys
import os
from typing import Dict, Tuple, List

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
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: cross_server

# BEGIN: Scenario: scenario_1_pick_and_place
# Configuration
_object_id = 'block_a'
_target_location = 'shelf_pos'

# State
initial_state_scenario_1 = State('scenario_1_pick_and_place')
initial_state_scenario_1.object_location = {
    'block_a': 'table_pos',
    'block_b': 'shelf_pos',
    'block_c': 'table_pos'
}
initial_state_scenario_1.arm_position = 'home'
initial_state_scenario_1.gripper_state = 'closed'
initial_state_scenario_1.holding = None

# Problem
problems['scenario_1_pick_and_place'] = (
    initial_state_scenario_1,
    [('m_initialize_and_orchestrate', _object_id, _target_location)],
    f'Pick-and-place: Move {_object_id} from table to {_target_location} -> 9 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_multi_transfer
# Configuration
_objects_to_move = ['block_a', 'block_b']
_target_location = 'shelf_pos'

# State
initial_state_scenario_2 = State('scenario_2_multi_transfer')
initial_state_scenario_2.object_location = {
    'block_a': 'table_pos',
    'block_b': 'table_pos',
    'block_c': 'shelf_pos'
}
initial_state_scenario_2.arm_position = 'home'
initial_state_scenario_2.gripper_state = 'closed'
initial_state_scenario_2.holding = None

# Problem
# Note: This requires two sequential pick-and-place operations
problems['scenario_2_multi_transfer'] = (
    initial_state_scenario_2,
    [
        ('m_initialize_and_orchestrate', _objects_to_move[0], _target_location),
        ('m_cross_server_orchestration', _objects_to_move[1], _target_location)
    ],
    f'Multi-transfer: Move {_objects_to_move} to {_target_location} -> 15 actions'
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

