"""
Problem definitions for the Cross-Server Robot Orchestration example.
-- Generated 2025-11-27

This file defines initial states for cross-server HTN plan execution orchestration.
The workflow demonstrates coordination between three MCP servers:
  - Server 1 (mcp-python-ingestion): HTN planning with GTPyhop
  - Server 2 (robot-server): Robot gripper actions (mock)
  - Server 3 (motion-server): Arm motion planning (mock)
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
# PROBLEM
# ============================================================================

# ===== [SCENARIO 1] Pick-and-Place Task: Move block_a from table to shelf ===
initial_state_scenario_1 = State('cross_server_pick_and_place')

# Object locations
initial_state_scenario_1.object_location = {
    'block_a': 'table_pos',
    'block_b': 'shelf_pos',
    'block_c': 'table_pos'
}

# Robot state
initial_state_scenario_1.arm_position = 'home'
initial_state_scenario_1.gripper_state = 'closed'
initial_state_scenario_1.holding = None

# Server readiness (will be set by a_initialize_servers)
# These are not set initially - the plan will initialize them

# ===== [SCENARIO 2] Multi-Object Transfer: Move multiple blocks ============
initial_state_scenario_2 = State('cross_server_multi_transfer')

# Object locations
initial_state_scenario_2.object_location = {
    'block_a': 'table_pos',
    'block_b': 'table_pos',
    'block_c': 'shelf_pos'
}

# Robot state
initial_state_scenario_2.arm_position = 'home'
initial_state_scenario_2.gripper_state = 'closed'
initial_state_scenario_2.holding = None

# Server readiness (will be set by a_initialize_servers)
# These are not set initially - the plan will initialize them

