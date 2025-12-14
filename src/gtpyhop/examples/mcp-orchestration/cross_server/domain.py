# ============================================================================
# MCP Orchestration - Cross-Server HTN Plan Execution Domain
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - State Property Map
#   - Actions (9)
#   - Methods (6)
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

# -------------------- Smart GTPyhop import strategy with secure path handling
import sys
import os
from typing import Optional, Union, List, Tuple, Dict

def safe_add_to_path(relative_path: str) -> Optional[str]:
    """
    Safely add a relative path to sys.path with validation to prevent path traversal attacks.

    Args:
        relative_path: Relative path to add to sys.path

    Returns:
        The absolute path that was added, or None if validation failed

    Raises:
        ValueError: If path traversal is detected
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))

    # Validate the path is within expected boundaries to prevent path traversal
    if not target_path.startswith(os.path.dirname(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")

    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

# ----- Secure GTPyhop import strategy - tries PyPI first, falls back to local
try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    # Fallback to local development with secure path handling
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
the_domain = Domain("cross_server")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (Cross-Server Robot Orchestration)
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Server 1: mcp-python-ingestion (HTN Planning with GTPyhop)
# Server 2: robot-server (Gripper actions - mock)
# Server 3: motion-server (Arm motion planning - mock)
#
# Step 1: a_open_gripper
#  (P) gripper_state != "open" [ENABLER]
#  (E) gripper_state: "open" [ENABLER]
#
# Step 2: a_close_gripper
#  (P) gripper_state == "open" [ENABLER]
#  (P) holding is not None [ENABLER]
#  (E) gripper_state: "closed" [ENABLER]
#
# Step 3: a_grasp_object
#  (P) gripper_state == "open" [ENABLER]
#  (P) arm_position == object_location [ENABLER]
#  (P) holding is None [ENABLER]
#  (E) holding: str (object_id) [DATA]
#  (E) grasped_objects: List[str] [DATA]
#
# Step 4: a_release_object
#  (P) gripper_state == "closed" [ENABLER]
#  (P) holding is not None [ENABLER]
#  (E) holding: None [ENABLER]
#  (E) object_location[object]: str [DATA]
#
# Step 5: a_move_arm_to_position
#  (P) arm_position != target_position [ENABLER]
#  (E) arm_position: str [DATA]
#  (E) arm_trajectory: List[str] [DATA]
#
# Step 6: a_plan_motion_path
#  (P) arm_position is defined [ENABLER]
#  (E) planned_path: List[str] [DATA]
#  (E) path_planning_complete: True [ENABLER]
#
# Step 7: a_execute_planned_motion
#  (P) path_planning_complete is True [ENABLER]
#  (P) planned_path is not empty [ENABLER]
#  (E) arm_position: str (final position) [DATA]
#  (E) motion_execution_complete: True [ENABLER]
#
# Step 8: a_verify_grasp
#  (P) holding is not None [ENABLER]
#  (E) grasp_verified: True [ENABLER]
#  (E) grasp_force: float [DATA]
#
# Step 9: a_initialize_servers
#  (E) server_1_ready: True [ENABLER]
#  (E) server_2_ready: True [ENABLER]
#  (E) server_3_ready: True [ENABLER]
#  (E) cross_server_initialized: True [ENABLER]
#
# ============================================================================

# ============================================================================
# ACTIONS (9)
# ----------------------------------------------------------------------------

# ============================================================================
# CROSS-SERVER ROBOT ORCHESTRATION ACTIONS
# ============================================================================

# ============================================================================
# SERVER INITIALIZATION ACTION
# ============================================================================

def a_initialize_servers(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: cross_server:initialize

    Action signature:
        a_initialize_servers(state)

    Action parameters:
        None

    Action purpose:
        Initialize all three MCP servers for cross-server orchestration

    Preconditions:
        None (initialization action)

    Effects:
        - Server 1 (mcp-python-ingestion) is ready (state.server_1_ready) [ENABLER]
        - Server 2 (robot-server) is ready (state.server_2_ready) [ENABLER]
        - Server 3 (motion-server) is ready (state.server_3_ready) [ENABLER]
        - Cross-server orchestration is initialized (state.cross_server_initialized) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed for initialization
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for initialization action
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Server 1 ready - HTN planning server
    state.server_1_ready = True

    # [ENABLER] Server 2 ready - Robot gripper server
    state.server_2_ready = True

    # [ENABLER] Server 3 ready - Motion planning server
    state.server_3_ready = True

    # [ENABLER] Cross-server orchestration initialized
    state.cross_server_initialized = True
    # END: Effects

    return state


# ============================================================================
# GRIPPER ACTIONS (Server 2: robot-server)
# ============================================================================

def a_open_gripper(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: robot_server:open_gripper

    Action signature:
        a_open_gripper(state)

    Action parameters:
        None

    Action purpose:
        Open the robot gripper to prepare for grasping

    Preconditions:
        - Gripper is not already open (state.gripper_state != "open")
        - Server 2 is ready (state.server_2_ready)

    Effects:
        - Gripper state is set to open (state.gripper_state) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Gripper must not already be open
    if hasattr(state, 'gripper_state') and state.gripper_state == "open":
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Gripper is now open
    state.gripper_state = "open"
    # END: Effects

    return state


def a_close_gripper(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: robot_server:close_gripper

    Action signature:
        a_close_gripper(state)

    Action parameters:
        None

    Action purpose:
        Close the robot gripper to secure a grasped object

    Preconditions:
        - Gripper is open (state.gripper_state == "open")
        - An object is being held (state.holding is not None)
        - Server 2 is ready (state.server_2_ready)

    Effects:
        - Gripper state is set to closed (state.gripper_state) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Gripper must be open
    if not (hasattr(state, 'gripper_state') and state.gripper_state == "open"):
        return False
    # Must be holding an object
    if not (hasattr(state, 'holding') and state.holding is not None):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Gripper is now closed
    state.gripper_state = "closed"
    # END: Effects

    return state


def a_grasp_object(state: State, object_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: robot_server:grasp

    Action signature:
        a_grasp_object(state, object_id)

    Action parameters:
        object_id: ID of the object to grasp (e.g., 'block_a')

    Action purpose:
        Grasp an object with the robot gripper

    Preconditions:
        - Gripper is open (state.gripper_state == "open")
        - Arm is at object location (state.arm_position == state.object_location[object_id])
        - Not currently holding anything (state.holding is None)
        - Server 2 is ready (state.server_2_ready)

    Effects:
        - Object is now being held (state.holding) [DATA]
        - Object added to grasped objects list (state.grasped_objects) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(object_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not object_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Gripper must be open
    if not (hasattr(state, 'gripper_state') and state.gripper_state == "open"):
        return False
    # Must not be holding anything
    if hasattr(state, 'holding') and state.holding is not None:
        return False
    # Object must exist
    if not (hasattr(state, 'object_location') and object_id in state.object_location):
        return False
    # Arm must be at object location
    if not (hasattr(state, 'arm_position') and
            state.arm_position == state.object_location[object_id]):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Now holding the object
    state.holding = object_id

    # [DATA] Add to grasped objects list
    if not hasattr(state, 'grasped_objects'):
        state.grasped_objects = []
    if object_id not in state.grasped_objects:
        state.grasped_objects.append(object_id)
    # END: Effects

    return state


def a_release_object(state: State, location: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: robot_server:release

    Action signature:
        a_release_object(state, location)

    Action parameters:
        location: Target location to place the object (e.g., 'shelf', 'table')

    Action purpose:
        Release the currently held object at a target location

    Preconditions:
        - Gripper is closed (state.gripper_state == "closed")
        - Currently holding an object (state.holding is not None)
        - Arm is at target location (state.arm_position == location)
        - Server 2 is ready (state.server_2_ready)

    Effects:
        - No longer holding object (state.holding) [ENABLER]
        - Object location is updated (state.object_location[object]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(location, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not location.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Gripper must be closed
    if not (hasattr(state, 'gripper_state') and state.gripper_state == "closed"):
        return False
    # Must be holding an object
    if not (hasattr(state, 'holding') and state.holding is not None):
        return False
    # Arm must be at target location
    if not (hasattr(state, 'arm_position') and state.arm_position == location):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Update object location
    object_id = state.holding
    if not hasattr(state, 'object_location'):
        state.object_location = {}
    state.object_location[object_id] = location

    # [ENABLER] No longer holding object
    state.holding = None
    # END: Effects

    return state


# ============================================================================
# MOTION PLANNING ACTIONS (Server 3: motion-server)
# ============================================================================

def a_move_arm_to_position(state: State, target_position: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: motion_server:move_arm

    Action signature:
        a_move_arm_to_position(state, target_position)

    Action parameters:
        target_position: Target position for the arm (e.g., 'home', 'shelf_pos', 'table_pos')

    Action purpose:
        Move robot arm to a target position

    Preconditions:
        - Arm is not already at target position (state.arm_position != target_position)
        - Server 3 is ready (state.server_3_ready)

    Effects:
        - Arm position is updated (state.arm_position) [DATA]
        - Arm trajectory is recorded (state.arm_trajectory) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(target_position, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not target_position.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 3 must be ready
    if not (hasattr(state, 'server_3_ready') and state.server_3_ready):
        return False
    # Arm must not already be at target position
    if hasattr(state, 'arm_position') and state.arm_position == target_position:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Update arm position
    state.arm_position = target_position

    # [DATA] Record trajectory
    if not hasattr(state, 'arm_trajectory'):
        state.arm_trajectory = []
    state.arm_trajectory.append(target_position)
    # END: Effects

    return state


def a_plan_motion_path(state: State, start_position: str, end_position: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: motion_server:plan_path

    Action signature:
        a_plan_motion_path(state, start_position, end_position)

    Action parameters:
        start_position: Starting position for path planning
        end_position: Target position for path planning

    Action purpose:
        Plan a collision-free motion path for the robot arm

    Preconditions:
        - Arm position is defined (state.arm_position)
        - Server 3 is ready (state.server_3_ready)

    Effects:
        - Planned path is generated (state.planned_path) [DATA]
        - Path planning is complete (state.path_planning_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(start_position, str): return False
    if not isinstance(end_position, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not start_position.strip(): return False
    if not end_position.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 3 must be ready
    if not (hasattr(state, 'server_3_ready') and state.server_3_ready):
        return False
    # Arm position must be defined
    if not hasattr(state, 'arm_position'):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Generate planned path (simplified for demo)
    state.planned_path = [start_position, f"{start_position}_mid", f"{end_position}_mid", end_position]

    # [ENABLER] Path planning complete
    state.path_planning_complete = True
    # END: Effects

    return state


def a_execute_planned_motion(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: motion_server:execute_motion

    Action signature:
        a_execute_planned_motion(state)

    Action parameters:
        None

    Action purpose:
        Execute the previously planned motion path

    Preconditions:
        - Path planning is complete (state.path_planning_complete)
        - Planned path exists and is not empty (state.planned_path)
        - Server 3 is ready (state.server_3_ready)

    Effects:
        - Arm position is updated to final position (state.arm_position) [DATA]
        - Motion execution is complete (state.motion_execution_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 3 must be ready
    if not (hasattr(state, 'server_3_ready') and state.server_3_ready):
        return False
    # Path planning must be complete
    if not (hasattr(state, 'path_planning_complete') and state.path_planning_complete):
        return False
    # Planned path must exist and not be empty
    if not (hasattr(state, 'planned_path') and state.planned_path):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Update arm position to final position in path
    state.arm_position = state.planned_path[-1]

    # [ENABLER] Motion execution complete
    state.motion_execution_complete = True
    # END: Effects

    return state


def a_verify_grasp(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: robot_server:verify_grasp

    Action signature:
        a_verify_grasp(state)

    Action parameters:
        None

    Action purpose:
        Verify that the object is securely grasped

    Preconditions:
        - Currently holding an object (state.holding is not None)
        - Server 2 is ready (state.server_2_ready)

    Effects:
        - Grasp is verified (state.grasp_verified) [ENABLER]
        - Grasp force is measured (state.grasp_force) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Must be holding an object
    if not (hasattr(state, 'holding') and state.holding is not None):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Grasp verified
    state.grasp_verified = True

    # [DATA] Grasp force (simulated value)
    state.grasp_force = 5.0  # Newtons
    # END: Effects

    return state


# ============================================================================
# METHODS (6)
# ----------------------------------------------------------------------------

# ============================================================================
# CROSS-SERVER ORCHESTRATION METHODS
# ============================================================================

def m_cross_server_orchestration(state: State, object_id: str, target_location: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_cross_server_orchestration(state, object_id, target_location)

    Method parameters:
        object_id: ID of the object to move
        target_location: Target location for the object

    Method purpose:
        Top-level method for cross-server pick-and-place orchestration

    Preconditions:
        - Cross-server system is initialized (state.cross_server_initialized)

    Returns:
        List of subtasks if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(object_id, str): return False
    if not isinstance(target_location, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not object_id.strip(): return False
    if not target_location.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Cross-server system must be initialized
    if not (hasattr(state, 'cross_server_initialized') and state.cross_server_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_pick_object", object_id),
        ("m_place_object", object_id, target_location)
    ]
    # END: Task Decomposition


def m_pick_object(state: State, object_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_pick_object(state, object_id)

    Method parameters:
        object_id: ID of the object to pick up

    Method purpose:
        Decompose pick task into: move to object → open gripper (if needed) → grasp → close gripper → verify

    Preconditions:
        - Object exists in object_location (state.object_location[object_id])
        - Not currently holding anything (state.holding is None)
        - Gripper is closed

    Returns:
        List of subtasks if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(object_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not object_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Object must exist
    if not (hasattr(state, 'object_location') and object_id in state.object_location):
        return False
    # Must not be holding anything
    if hasattr(state, 'holding') and state.holding is not None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    object_location = state.object_location[object_id]
    tasks = [("a_move_arm_to_position", object_location)]

    # Only open gripper if it's not already open
    if not (hasattr(state, 'gripper_state') and state.gripper_state == "open"):
        tasks.append(("a_open_gripper",))

    tasks.extend([
        ("a_grasp_object", object_id),
        ("a_close_gripper",),
        ("a_verify_grasp",)
    ])

    return tasks
    # END: Task Decomposition


def m_pick_object_gripper_open(state: State, object_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_pick_object_gripper_open(state, object_id)

    Method parameters:
        object_id: ID of the object to pick up

    Method purpose:
        Decompose pick task when gripper is already open: move to object → grasp → close gripper → verify

    Preconditions:
        - Object exists in object_location (state.object_location[object_id])
        - Not currently holding anything (state.holding is None)
        - Gripper is already open

    Returns:
        List of subtasks if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(object_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not object_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Object must exist
    if not (hasattr(state, 'object_location') and object_id in state.object_location):
        return False
    # Must not be holding anything
    if hasattr(state, 'holding') and state.holding is not None:
        return False
    # Gripper must be open (this method handles open gripper case)
    if not (hasattr(state, 'gripper_state') and state.gripper_state == "open"):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    object_location = state.object_location[object_id]
    return [
        ("a_move_arm_to_position", object_location),
        ("a_grasp_object", object_id),
        ("a_close_gripper",),
        ("a_verify_grasp",)
    ]
    # END: Task Decomposition


def m_place_object(state: State, object_id: str, target_location: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_place_object(state, object_id, target_location)

    Method parameters:
        object_id: ID of the object to place
        target_location: Target location for placement

    Method purpose:
        Decompose place task into: move to location → release object

    Preconditions:
        - Currently holding the specified object (state.holding == object_id)
        - Gripper is closed (state.gripper_state == "closed")

    Returns:
        List of subtasks if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(object_id, str): return False
    if not isinstance(target_location, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not object_id.strip(): return False
    if not target_location.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Must be holding the specified object
    if not (hasattr(state, 'holding') and state.holding == object_id):
        return False
    # Gripper must be closed
    if not (hasattr(state, 'gripper_state') and state.gripper_state == "closed"):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_move_arm_to_position", target_location),
        ("a_release_object", target_location),
        ("a_open_gripper",)
    ]
    # END: Task Decomposition


def m_initialize_and_orchestrate(state: State, object_id: str, target_location: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_initialize_and_orchestrate(state, object_id, target_location)

    Method parameters:
        object_id: ID of the object to move
        target_location: Target location for the object

    Method purpose:
        Initialize servers and then perform cross-server orchestration

    Preconditions:
        None (top-level method)

    Returns:
        List of subtasks if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(object_id, str): return False
    if not isinstance(target_location, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not object_id.strip(): return False
    if not target_location.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("m_cross_server_orchestration", object_id, target_location)
    ]
    # END: Task Decomposition


def m_move_with_planning(state: State, start_pos: str, end_pos: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_move_with_planning(state, start_pos, end_pos)

    Method parameters:
        start_pos: Starting position
        end_pos: Ending position

    Method purpose:
        Move arm using motion planning (plan path → execute motion)

    Preconditions:
        - Server 3 is ready (state.server_3_ready)

    Returns:
        List of subtasks if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(start_pos, str): return False
    if not isinstance(end_pos, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not start_pos.strip(): return False
    if not end_pos.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 3 must be ready
    if not (hasattr(state, 'server_3_ready') and state.server_3_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_plan_motion_path", start_pos, end_pos),
        ("a_execute_planned_motion",)
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

# Declare all 9 actions to the current domain
declare_actions(
    a_initialize_servers,
    a_open_gripper,
    a_close_gripper,
    a_grasp_object,
    a_release_object,
    a_move_arm_to_position,
    a_plan_motion_path,
    a_execute_planned_motion,
    a_verify_grasp
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Declare task methods to the current domain
declare_task_methods('m_initialize_and_orchestrate', m_initialize_and_orchestrate)
declare_task_methods('m_cross_server_orchestration', m_cross_server_orchestration)
declare_task_methods('m_pick_object', m_pick_object)
declare_task_methods('m_place_object', m_place_object)
declare_task_methods('m_move_with_planning', m_move_with_planning)

# ============================================================================
# END OF FILE
# ============================================================================



