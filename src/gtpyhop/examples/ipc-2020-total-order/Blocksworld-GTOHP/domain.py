# ============================================================================
# IPC 2020 Total Order - Blocksworld Domain
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - Actions (5)
#   - Helpers - State Parameter Inference (2)
#   - Methods (8)
#   - Goal Methods
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

# -------------------- Smart GTPyhop import strategy with secure path handling
import sys
import os
from typing import Optional, Union, List, Tuple

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
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods, declare_unigoal_methods, declare_multigoal_methods
except ImportError:
    # Fallback to local development with secure path handling
    try:
        safe_add_to_path(os.path.join('..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods, declare_unigoal_methods, declare_multigoal_methods
    except (ImportError, ValueError) as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("Blocksworld-GTOHP")
set_current_domain(the_domain)

# ============================================================================
# ACTIONS (5)
# ----------------------------------------------------------------------------
#   - pick_up
#   - put_down
#   - stack
#   - unstack
#   - nop
# ============================================================================

# (:action pick-up
#   :parameters (?x - block)
#   :precondition (and (clear ?x) (ontable ?x) (handempty))
#   :effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x)))
def pick_up(state: State, x: str) -> Union[State, bool]:
    """
    Class: Action

    Action signature:
        pick_up(state, x)

    Action parameters:
        x: block

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Pick up block x from the table

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    if not (isinstance(x, str)):
        return False
    # State type checking: parameter x must be a block
    if not (x in state.blocks): 
        return False

    # (and (clear ?x) (ontable ?x) (handempty))
    # -----> Check preconditions
    if not ((x in state.clear) and (x in state.ontable) and (state.handempty)):
        return False

    # (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x)))
    # <----- Apply effects()
    state.ontable.discard(x)    # HDDL: (not (ontable ?x))
    state.clear.discard(x)      # HDDL: (not (clear ?x))
    state.handempty = False     # HDDL: (not (handempty))
    state.holding = x           # HDDL: (holding ?x)

    return state


# (:action put-down
#   :parameters (?x - block)
#   :precondition (holding ?x)
#   :effect (and (not (holding ?x)) (clear ?x) (handempty) (ontable ?x)))
def put_down(state: State, x: str) -> Union[State, bool]:
    """
    Class: Action

    Action signature:
        put_down(state, x)

    Action parameters:
        x: block

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Release block x from hand on the table

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    if not (isinstance(x, str)):
        return False
    # State type checking: parameter x must be a block
    if not (x in state.blocks): 
        return False

    # (holding ?x)
    # -----> Check preconditions
    if not (state.holding == x):
        return False

    # (and (not (holding ?x)) (clear ?x) (handempty) (ontable ?x)))
    # <----- Apply effects()
    state.holding = None        # HDDL: (not (holding ?x))
    state.clear.add(x)          # HDDL: (clear ?x)
    state.handempty = True      # HDDL: (handempty)
    state.ontable.add(x)        # HDDL: (ontable ?x)

    return state


# (:action stack
#   :parameters (?x - block ?y - block)
#   :precondition (and (holding ?x) (clear ?y))
#   :effect (and (not (holding ?x)) (not (clear ?y)) (clear ?x) (handempty) (on ?x ?y)))
def stack(state: State, x: str, y: str) -> Union[State, bool]:
    """
    Class: Action

    Action signature:
        stack(state, x, y)

    Action parameters:
        x: block
        y: block

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Place block x on top of block y

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    # Python type checking: parameter y must be a string
    if not (isinstance(x, str) and isinstance(y, str)):
        return False
    # State type checking: parameter x must be a block
    # State type checking: parameter y must be a block
    if not (x in state.blocks and y in state.blocks): 
        return False
    
    # (and (holding ?x) (clear ?y))
    # -----> Check preconditions
    if not ((state.holding == x) and (y in state.clear)):
        return False

    # (and (not (holding ?x)) (not (clear ?y)) (clear ?x) (handempty) (on ?x ?y)))
    # <----- Apply effects()
    state.holding = None        # HDDL: (not (holding ?x))
    state.clear.discard(y)      # HDDL: (not (clear ?y))
    state.clear.add(x)          # HDDL: (clear ?x)
    state.handempty = True      # HDDL: (handempty)
    state.on[x] = y             # HDDL: (on ?x ?y)

    return state


# (:action unstack
#   :parameters (?x - block ?y - block)
#   :precondition (and (on ?x ?y) (clear ?x) (handempty))
#   :effect (and (holding ?x) (clear ?y) (not (clear ?x)) (not (handempty)) (not (on ?x ?y))))
def unstack(state: State, x: str, y: str) -> Union[State, bool]:
    """
    Class: Action

    Action signature:
        unstack(state, x, y)

    Action parameters:
        x: block
        y: block

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Remove block x from top of block y

    Returns:
        Updated state if successful, False otherwise
    """

    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    # Python type checking: parameter y must be a string
    if not (isinstance(x, str) and isinstance(y, str)):
        return False
    # State type checking: parameter x must be a block
    # State type checking: parameter y must be a block
    if not (x in state.blocks and y in state.blocks): 
        return False

    # (and (on ?x ?y) (clear ?x) (handempty))
    # -----> Check preconditions
    if not ((x in state.on and state.on[x] == y) and (x in state.clear) and (state.handempty)):
        return False

    # (and (holding ?x) (clear ?y) (not (clear ?x)) (not (handempty)) (not (on ?x ?y))))
    # <----- Apply effects()
    state.holding = x           # HDDL: (holding ?x)
    state.clear.add(y)          # HDDL: (clear ?y)
    state.clear.discard(x)      # HDDL: (not (clear ?x))
    state.handempty = False     # HDDL: (not (handempty))
    state.on.pop(x, None)       # HDDL: (not (on ?x ?y))

    return state


# (:action nop
#   :parameters ()
#   :precondition ()
#   :effect ())
# )
def nop(state: State) -> Union[State, bool]:
    """
    Class: Action

    Action signature:
        nop(state)

    Action parameters:
        None

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Do nothing

    Returns:
        Same state if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False

    # ()
    # -----> Check preconditions
    # Action nop has no preconditions

    # ()
    # <----- Apply effects()
    # Action nop has no effects

    return state


# Declare actions to the domain
declare_actions(pick_up)
declare_actions(put_down)
declare_actions(stack)
declare_actions(unstack)
declare_actions(nop)

# ============================================================================
# HELPERS - STATE PARAMETER INFERENCE (2)
# ----------------------------------------------------------------------------
#   - infer_top_block
#   - infer_bottom_block
# ============================================================================
def infer_top_block(state: State, x: str) -> Optional[str]:
    """
    Class: Helper-State-Parameter-Inference

    Helper signature:
        infer_top_block(state,x)

    Helper parameters:
        state: current state
        x: block

    Helper auxiliary parameters:
        None (inferred from None)

    Helper purpose:
        Infer the block on top of block x from the state

    Helper returns:
        The block on top of x if it exists, None otherwise.
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return None
    # Python type checking: x must be a string
    if not (isinstance(x, str)):
        return None
    # State type checking: parameter x must be a block
    if not (x in state.blocks):
        return None
    # does y:x exist in state.on?
    for top_block, bottom_block in state.on.items():
        if bottom_block == x:
            return top_block
    return None


def infer_bottom_block(state: State, x: str) -> Optional[str]:
    """
    Class: Helper-State-Parameter-Inference

    Helper signature:
        infer_bottom_block(state,x)

    Helper parameters:
        state: current state
        x: block

    Helper auxiliary parameters:
        None (inferred from None)

    Helper purpose:
        Infer the block below block x from the state

    Helper returns:
        The block below x if it exists, None otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return None
    # Python type checking: x must be a string
    if not (isinstance(x, str)):
        return None
    # State type checking: parameter x must be a block
    if not (x in state.blocks):
        return None
    # does x:z exist in state.on?
    for top_block, bottom_block in state.on.items():
        if top_block == x:
            return bottom_block
    return None

# ============================================================================
# METHODS (8)
# ----------------------------------------------------------------------------
#   - m0_do_put_on
#   - m1_do_put_on
#   - m2_do_on_table
#   - m3_do_on_table
#   - m4_do_move
#   - m5_do_move
#   - m6_do_clear
#   - m7_do_clear
# ============================================================================

# (:method m0_do_put_on
#   :parameters ( ?x - block  ?y - block )
#   :task (do_put_on ?x ?y)
#   :precondition (and (on ?x ?y))
#   :ordered-subtasks(and (t1 (nop))) ) 
def m0_do_put_on(state: State, x: str, y: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m0_do_put_on(state, x, y)

    Method parameters:
        x: block
        y: block

    Method auxiliary parameters:
        None (inferred from None)

    Method purpose:
        Do nothing if x is already on y

    Returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: both x and y must be strings
    if not (isinstance(x, str) and isinstance(y, str)):
        return False
    # State type checking: parameter x must be a block
    # State type checking: parameter y must be a block
    if not (x in state.blocks and y in state.blocks): 
        return False

    # (and (on ?x ?y))
    # -----> Check preconditions
    if not ((x in state.on and y == state.on[x])):
        return False

    # Return subtask decomposition
    return [
        ("nop",)
    ]

# (:method m0_do_put_on
#   :parameters ( ?x - block  ?y - block )
#   :task (do_put_on ?x ?y)
#   :precondition (and (on ?x ?y))
#   :ordered-subtasks(and (t1 (nop))) ) 
def m1_do_put_on(state: State, x: str, y: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m1_do_put_on(state, x, y)

    Method parameters:
        x: block
        y: block

    Method auxiliary parameters:
        None (inferred from None)

    Method purpose:
        Put block x on top of block y

    Returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    # Python type checking: parameter y must be a string
    if not (isinstance(x, str) and isinstance(y, str)):
        return False
    # State type checking: parameter x must be a block
    # State type checking: parameter y must be a block
    if not (x in state.blocks and y in state.blocks): 
        return False

    # -----> Check preconditions
    if not ((state.handempty)):
        return False

    # Return subtask decomposition
    return [
        ("do_clear", x),
        ("do_clear", y),
        ("do_on_table", y),
        ("do_move", x, y)
    ]

# (:method m2_do_on_table
#     :parameters ( ?x - block ?y - block )
#     :task (do_on_table ?x)
#     :precondition (and (clear ?x) (handempty) (not (ontable ?x)))
#     :ordered-subtasks(and (t1 (unstack ?x ?y)) (t2 (put-down ?x))) ) 
def m2_do_on_table(state: State, x: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m2_do_on_table(state, x)

    Method parameters:
        x: block
    
    Method auxiliary parameters:
        y: block (inferred from on(?y, ?x) in state.on)
    
    Method purpose:
        Put block x from top of block y onto the table
    
    Returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: x must be a string
    if not (isinstance(x, str)):
        return False
    # State type checking: parameter x must be a block
    if not (x in state.blocks): 
        return False

    # Inferred auxiliary parameters
    y = infer_top_block(state, x)

    if y is None:
        return False  # Cannot infer y - no block on top of x

    # -----> Check preconditions
    if not ((x in state.clear) and (state.handempty) and (not (x in state.ontable))):
        return False

    # Return subtask decomposition using inferred parameters
    return [
        ("unstack", x, y),
        ("put_down", x)
    ]

# (:method m3_do_on_table
#   :parameters ( ?x - block )
#   :task (do_on_table ?x)
#   :precondition (and (clear ?x))
#   :ordered-subtasks(and (t1 (nop))) ) 
def m3_do_on_table(state: State, x: str) -> Union[List[Tuple], bool]:
    """
    Method signature:
        m3_do_on_table(state, x)

    Method parameters:
        x: block

    Method auxiliary parameters:
        None (inferred from None)

    Purpose:
        Do nothing if block x is already clear

    Returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    if not (isinstance(x, str)):
        return False
    # State type checking: parameter x must be a block
    if not (x in state.blocks): 
        return False

    # -----> Check preconditions
    if not ((x in state.clear)):
        return False

    # Return subtask decomposition
    return [
        ("nop",)
    ]


# (:method m4_do_move
#   :parameters ( ?x - block  ?y - block )
#   :task (do_move ?x ?y)
#   :precondition (and (clear ?x) (clear ?y) (handempty) (ontable ?x))
#   :ordered-subtasks(and (t1 (pick-up ?x)) (t2 (stack ?x ?y))) ) 
def m4_do_move(state: State, x: str, y: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m4_do_move(state, x, y)

    Method parameters:
        x: block
        y: block

    Method auxiliary parameters:
        None (inferred from None)

    Method purpose:
        Move block x from table to block y

    Method returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    # Python type checking: parameter y must be a string
    if not (isinstance(x, str) and isinstance(y, str)):
        return False
    # State type checking: parameter x must be a block
    # State type checking: parameter y must be a block
    if not (x in state.blocks and y in state.blocks): 
        return False

    # -----> Check preconditions
    if not ((x in state.clear) and (y in state.clear) and (state.handempty) and (x in state.ontable)):
        return False

    # Return subtask decomposition
    return [
        ("pick_up", x),
        ("stack", x, y)
    ]

# (:method m5_do_move
#     :parameters ( ?x - block  ?y - block ?z - block )
#     :task (do_move ?x ?y)
#     :precondition (and (clear ?x) (clear ?y) (handempty) (not (ontable ?x)))
#     :ordered-subtasks(and (t1 (unstack ?x ?z)) (t2 (stack ?x ?y))) ) 
def m5_do_move(state: State, x: str, y: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m5_do_move(state, x, y)
    
    Method parameters:
        x: block
        y: block
    
    Method auxiliary parameters (inferred from state.on):
        z: block  (inferred from on(?z, ?x) in state.on)

    Method purpose:
        Move block x from top of block z to block y
    
    Method returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    # Python type checking: parameter y must be a string
    if not (isinstance(x, str) and isinstance(y, str)):
        return False
    # State type checking: parameter x must be a block
    # State type checking: parameter y must be a block
    if not (x in state.blocks and y in state.blocks): 
        return False

    # Inferred auxiliary parameters
    z = infer_bottom_block(state, x)

    if z is None:
        return False  # Cannot infer z

    # -----> Check preconditions
    if not ((x in state.clear) and (y in state.clear) and (state.handempty) and (not (x in state.ontable))):
        return False

    # Return subtask decomposition using inferred parameters
    return [("unstack", x, z), ("stack", x, y)]


# (:method m6_do_clear
#   :parameters ( ?x - block )
#   :task (do_clear ?x)
#   :precondition (and (clear ?x))
#   :ordered-subtasks(and (t1 (nop))) ) 
def m6_do_clear(state: State, x: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m6_do_clear(state, x)

    Method parameters:
        x: block

    Method auxiliary parameters:
        None (inferred from None)

    Method purpose:
        Clear block x

    Method returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    if not (isinstance(x, str)):
        return False
    # State type checking: parameter x must be a block
    if not (x in state.blocks): 
        return False

    # -----> Check preconditions
    if not ((x in state.clear)):
        return False

    # Return subtask decomposition
    return [
        ("nop",)
    ]

# (:method m7_do_clear
#     :parameters ( ?x - block ?y - block )
#     :task (do_clear ?x)
#     :precondition (and (not (clear ?x)) (on ?y ?x) (handempty))
#     :ordered-subtasks(and (t1 (do_clear ?y)) (t2 (unstack ?y ?x)) (t3 (put-down ?y))) ) 
def m7_do_clear(state: State, x: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m7_do_clear(state, x)
    
    Method parameters:
        x: block
    
    Method auxiliary parameters:
        y: block (inferred from on(?y, ?x) in state.on)

    Method purpose:
        Clear block x by clearing block y on top of x

    Method returns:
        When x is already clear, returns an empty list of actions (no-op).
        List of subtasks if successful, False otherwise
    """    
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter x must be a string
    if not (isinstance(x, str)):
        return False
    # State type checking: parameter x must be a block
    if not (x in state.blocks): 
        return False

    # #########################################################################
    # Fixing: Trying to clear an already clear block should be a no-op
    # This change tells the planner that if a block is already clear, 
    # it doesn't need to do anything (returns an empty list of actions) 
    # rather than trying to clear it again.
    if x in state.clear:
        # DO NOT return False here, as that would indicate failure to the planner
        return []
    # #########################################################################

    # Infer auxiliary parameter y (block) from the on dictionary of the state:
    # does y:x exist in state.on?
    y = infer_top_block(state, x)

    if y is None:
        return False  # Cannot infer y - no block on top of x

    # (and (not (clear ?x)) (on ?y ?x) (handempty))
    # -----> Check preconditions
    if not ((not (x in state.clear)) and (y in state.on and state.on[y] == x) and (state.handempty)):
        return False

    # Return subtask decomposition using inferred parameters
    return [
        ("do_clear", y),
        ("unstack", y, x),
        ("put_down", y)
    ]

# Declare methods to the domain
declare_task_methods('do_put_on', m0_do_put_on, m1_do_put_on)
declare_task_methods('do_on_table', m2_do_on_table, m3_do_on_table)
declare_task_methods('do_move', m4_do_move, m5_do_move)
declare_task_methods('do_clear', m6_do_clear, m7_do_clear)

# ============================================================================
# GOAL METHODS
# ============================================================================
declare_unigoal_methods("on",m0_do_put_on, m1_do_put_on)
declare_multigoal_methods(gtpyhop.m_split_multigoal)

# ============================================================================
# END OF FILE
# ============================================================================