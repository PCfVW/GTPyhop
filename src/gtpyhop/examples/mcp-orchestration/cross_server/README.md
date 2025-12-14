# Cross-Server HTN Plan Execution Orchestration

## Overview

This example demonstrates **cross-server HTN (Hierarchical Task Network) plan execution orchestration** using GTPyhop 1.7.0+. It showcases how a single HTN planner can coordinate actions across multiple MCP (Model Context Protocol) servers to accomplish complex robotic tasks.

## Benchmarking Scenarios

| Scenario | Configuration | Actions | Status |
|----------|---------------|---------|--------|
| `scenario_1_pick_and_place` | Move block_a from table to shelf | 9 | ✅ VALID |
| `scenario_2_multi_transfer` | Move block_a and block_b to shelf | 15 | ✅ VALID |

### Three-Server Architecture

1. **Server 1: mcp-python-ingestion** (HTN Planning)
   - Runs GTPyhop 1.7.0 HTN planner
   - Generates hierarchical task decomposition
   - Coordinates execution across servers 2 and 3

2. **Server 2: robot-server** (Gripper Actions - Mock)
   - Provides gripper control actions:
     - `open_gripper`: Open the robot gripper
     - `close_gripper`: Close the robot gripper
     - `grasp`: Grasp an object
     - `release`: Release an object
     - `verify_grasp`: Verify grasp is secure

3. **Server 3: motion-server** (Arm Motion Planning - Mock)
   - Provides arm motion actions:
     - `move_arm`: Move arm to a position
     - `plan_path`: Plan collision-free path
     - `execute_motion`: Execute planned motion

### Demonstration Scenario

**Task:** Pick-and-place operation to move `block_a` from `table_pos` to `shelf_pos`

**HTN Decomposition:**
```
m_initialize_and_orchestrate(block_a, shelf_pos)
├── a_initialize_servers()                    [Server 1]
└── m_cross_server_orchestration(block_a, shelf_pos)
    ├── m_pick_object(block_a)
    │   ├── a_move_arm_to_position(table_pos)  [Server 3]
    │   ├── a_open_gripper()                   [Server 2]
    │   ├── a_grasp_object(block_a)            [Server 2]
    │   ├── a_close_gripper()                  [Server 2]
    │   └── a_verify_grasp()                   [Server 2]
    └── m_place_object(block_a, shelf_pos)
        ├── a_move_arm_to_position(shelf_pos)  [Server 3]
        ├── a_release_object(shelf_pos)        [Server 2]
        └── a_open_gripper()                   [Server 2]
```

## File Structure

```
cross_server/
├── domain.py       # Domain definition with 9 actions and 6 methods
├── problems.py     # Initial state definitions (2 scenarios)
├── __init__.py     # Package initialization with get_problems()
└── README.md       # This file
```

## Domain Statistics

- **Primitive Actions**: 9
- **Methods**: 6
- **Servers**: 3 (mcp-python-ingestion, robot-server, motion-server)
- **Scenarios**: 2

## State Properties

### Server Status
- `server_1_ready`: HTN planning server ready (bool)
- `server_2_ready`: Robot gripper server ready (bool)
- `server_3_ready`: Motion planning server ready (bool)
- `cross_server_initialized`: All servers initialized (bool)

### Robot State
- `arm_position`: Current arm position (str)
- `arm_trajectory`: List of visited positions (List[str])
- `gripper_state`: "open" or "closed" (str)
- `holding`: Object ID currently held, or None (Optional[str])

### Object State
- `object_location`: Dictionary mapping object IDs to locations (Dict[str, str])
- `grasped_objects`: List of objects that have been grasped (List[str])

### Motion Planning
- `planned_path`: Planned motion path (List[str])
- `path_planning_complete`: Path planning completed (bool)
- `motion_execution_complete`: Motion execution completed (bool)

### Grasp Verification
- `grasp_verified`: Grasp has been verified (bool)
- `grasp_force`: Measured grasp force in Newtons (float)

## Actions Summary

### Server Initialization (1 action)
1. **a_initialize_servers**: Initialize all three MCP servers

### Gripper Actions - Server 2 (4 actions)
2. **a_open_gripper**: Open the robot gripper
3. **a_close_gripper**: Close the robot gripper
4. **a_grasp_object**: Grasp an object with the gripper
5. **a_release_object**: Release the held object at a location

### Motion Actions - Server 3 (3 actions)
6. **a_move_arm_to_position**: Move arm to a target position
7. **a_plan_motion_path**: Plan a collision-free motion path
8. **a_execute_planned_motion**: Execute the planned motion

### Verification Actions - Server 2 (1 action)
9. **a_verify_grasp**: Verify that the grasp is secure

## Methods Summary

1. **m_initialize_and_orchestrate**: Top-level method (initialize → orchestrate)
2. **m_cross_server_orchestration**: Coordinate pick-and-place across servers
3. **m_pick_object**: Decompose pick task (move → open → grasp → close → verify)
4. **m_place_object**: Decompose place task (move → release → open)
5. **m_move_with_planning**: Move with motion planning (plan → execute)
6. **m_move_arm_to_position_task**: Wrapper for arm movement action

## Usage Examples

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.mcp_orchestration.cross_server import the_domain, problems

# Create planner session
session = gtpyhop.PlannerSession(the_domain, verbose=1)

# Get problem instance
state, tasks, desc = problems.get_problems()['scenario_1_pick_and_place']

# Find plan
result = session.find_plan(state, tasks)

if result.success:
    print(f"Plan found with {len(result.plan)} actions:")
    for i, action in enumerate(result.plan, 1):
        print(f"  {i}. {action[0]}")
```

### Using the benchmarking script

```bash
cd src/gtpyhop/examples/mcp-orchestration
python benchmarking.py cross_server
```

## Expected Plan Output

For **scenario_1** (move block_a from table_pos to shelf_pos):

```
Action 1: a_initialize_servers()
Action 2: a_move_arm_to_position(table_pos)
Action 3: a_open_gripper()
Action 4: a_grasp_object(block_a)
Action 5: a_close_gripper()
Action 6: a_verify_grasp()
Action 7: a_move_arm_to_position(shelf_pos)
Action 8: a_release_object(shelf_pos)
Action 9: a_open_gripper()
```

**Total: 9 actions** coordinated across 3 servers

## Cross-Server Coordination Details

### Action-to-Server Mapping

| Action | Server | Purpose |
|--------|--------|---------|
| `a_initialize_servers` | Server 1 | Initialize all servers |
| `a_open_gripper` | Server 2 | Open gripper |
| `a_close_gripper` | Server 2 | Close gripper |
| `a_grasp_object` | Server 2 | Grasp object |
| `a_release_object` | Server 2 | Release object |
| `a_verify_grasp` | Server 2 | Verify grasp |
| `a_move_arm_to_position` | Server 3 | Move arm |
| `a_plan_motion_path` | Server 3 | Plan path |
| `a_execute_planned_motion` | Server 3 | Execute motion |

### Workflow Enablers

The domain uses **workflow enabler** properties to ensure correct sequencing:

1. **Server Initialization**: `cross_server_initialized` must be True before orchestration
2. **Gripper State**: Must be "open" to grasp, "closed" to release
3. **Holding State**: Must be None to grasp, not None to release
4. **Motion Planning**: `path_planning_complete` must be True before execution

## Testing and Verification

### Test Domain Loads

```bash
cd C:\Users\Eric JACOPIN\Documents\Code\Source\GTPyhop\src\gtpyhop\examples\mcp-orchestration

python -c "import sys; sys.path.insert(0, '.'); from cross_server import the_domain; print(f'Domain loaded: {the_domain}')"
```

### Test Planning

```bash
python -c "import sys; sys.path.insert(0, '.'); from cross_server import domain, problems; import gtpyhop; session = gtpyhop.PlannerSession(domain.the_domain, verbose=1); result = session.find_plan(problems.initial_state_scenario_1, [('m_initialize_and_orchestrate', 'block_a', 'shelf_pos')]); print(f'\nPlan found: {result.success if result else False}'); print(f'Plan length: {len(result.plan) if result and result.success else 0}')"
```

## Key Features

### 1. **GTPyhop 1.7.0+ Structure**
- Single `domain.py` file with all actions and methods
- `problems.py` with Unified Scenario Block format (Configuration → State → Problem)
- `__init__.py` with `get_problems()` function for automatic discovery

### 2. **Complete Docstrings**
All actions and methods include complete documentation following the style guide

### 3. **Code Markers**
Actions use structured markers:
- `# BEGIN/END: Type Checking`
- `# BEGIN/END: State-Type Checks`
- `# BEGIN/END: Preconditions`
- `# BEGIN/END: Effects`

Methods use:
- `# BEGIN/END: Task Decomposition`

### 4. **State Property Map**
Comprehensive documentation of all state properties with:
- (E) for Effects, (P) for Preconditions
- [ENABLER] for workflow gates
- [DATA] for informational properties

## Troubleshooting

### Domain Not Found

```bash
# Make sure you're in the correct directory
cd C:\Users\Eric JACOPIN\Documents\Code\Source\GTPyhop\src\gtpyhop\examples\mcp-orchestration

# Verify the cross_server directory exists
dir cross_server
```

### Import Errors

```bash
# Install gtpyhop if needed
pip install gtpyhop

# Or use local development version
# The domain.py includes fallback to local gtpyhop
```

### Planning Fails

Check that the initial state includes:
- `object_location` dictionary with object positions
- `arm_position` set to a valid position
- `gripper_state` set to "closed" or "open"
- `holding` set to None (for pick tasks)

## Next Steps

1. **Extend the domain**: Add more objects, locations, or constraints
2. **Add new methods**: Create methods for multi-object transfer
3. **Integrate with real servers**: Replace mock servers with actual MCP server implementations
4. **Add error handling**: Implement recovery methods for failed actions
5. **Performance optimization**: Use motion planning for all arm movements

## References

- **GTPyhop Documentation**: https://github.com/dananau/GTPyhop
- **MCP Protocol**: https://modelcontextprotocol.io/
- **HTN Planning**: Hierarchical Task Network planning methodology

---
*Generated 2025-12-14*


