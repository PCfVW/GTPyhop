"""
Scalable Recursive Decomposition Domain for GTPyhop Memory Tracking

This domain demonstrates memory tracking capabilities with recursive method
decomposition following Alford et al.'s (2015) Theorem 4.1 structure.

Theoretical Foundation:
    Alford, R., Bercher, P., & Aha, D.W. (2015). "Tight Bounds for HTN Planning."
    ICAPS 2015, pp. 7-15.

    Theorem 4.1: Plan-existence for totally-ordered mostly-acyclic propositional
    HTN problems is PSPACE-complete.

    Section 4 (p.4-5) shows how to encode 2^k repetitions of a task using k
    method levels: method o_k decomposes into two ordered copies of o_{k-1},
    which each decompose into two copies of o_{k-2}, and so on until reaching
    the primitive task o_0. This yields 2^k leaf tasks.

Implementation:
    We implement this binary recursive decomposition structure:
    - m_recurse_level(k) -> [m_recurse_level(k-1), m_recurse_level(k-1)]
    - m_recurse_level(0) -> [a_execute_leaf_task]

    This is an ACYCLIC structure (no task decomposes back to itself or higher),
    which is a strict subset of tail-recursive problems.

Configuration Properties (set in initial state):
    - config_depth: int - Recursion depth k (yields 2^k leaf tasks)
    - config_payload_size: int - Bytes of payload per state (amplifies memory)

Memory Tracking:
    - Each leaf task appends config_payload_size bytes to state.results
    - Memory accumulates: 2^k leaf tasks × payload_size bytes
    - Demonstrates both depth scaling (task count) and payload scaling (per-task data)
"""

import sys
import os
from typing import Optional, Union, List, Tuple, Dict

# Secure GTPyhop import strategy
try:
    import gtpyhop
    from gtpyhop import Domain, State, declare_actions, declare_task_methods, set_current_domain
except ImportError:
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import Domain, State, declare_actions, declare_task_methods, set_current_domain
    except ImportError as e:
        print(f"Error: Could not import gtpyhop: {e}")
        sys.exit(1)

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("scalable_recursive_decomposition")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#  - [CONFIG]  Configuration parameter read from initial state
#
# Configuration Properties (set in problems.py):
#  config_depth: int [CONFIG] - Recursion depth k
#  config_payload_size: int [CONFIG] - Bytes of payload per state
#
# Step 1: a_initialize_recursion
#  (P) config_payload_size [CONFIG]
#  (E) results: [] [DATA] - accumulator for leaf task outputs
#  (E) task_count: 0 [DATA]
#  (E) initialized: True [ENABLER]
#
# Step 2: a_execute_leaf_task (called 2^k times)
#  (P) initialized [ENABLER]
#  (P) config_payload_size [CONFIG]
#  (E) results: appended with payload_size bytes [DATA]
#  (E) task_count: incremented [DATA]
#
# Step 3: a_finalize_recursion
#  (P) initialized [ENABLER]
#  (E) execution_complete: True [ENABLER]
# ============================================================================

# ============================================================================
# ACTIONS
# ============================================================================

def a_initialize_recursion(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:initialize

    Action signature:
        a_initialize_recursion(state)

    Action parameters:
        None

    Action purpose:
        Initialize state with memory payload for recursive decomposition demo

    Preconditions:
        None (initialization action)

    Effects:
        - Results accumulator initialized (state.results) [DATA]
        - Task counter initialized (state.task_count) [DATA]
        - Initialization flag (state.initialized) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for initialization action
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Results accumulator - each leaf task will append payload_size bytes
    state.results = []

    # [DATA] Counter for executed leaf tasks
    state.task_count = 0

    # [ENABLER] Initialization completed - gates leaf task execution
    state.initialized = True
    # END: Effects

    return state


def a_execute_leaf_task(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:execute

    Action signature:
        a_execute_leaf_task(state)

    Action parameters:
        None

    Action purpose:
        Execute a single leaf task (primitive task at recursion base case).
        Appends payload_size bytes to state.results, accumulating memory.

    Preconditions:
        - State is initialized (state.initialized)

    Effects:
        - Payload appended to results (state.results) [DATA]
        - Task counter incremented (state.task_count) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'initialized') and state.initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Append payload_size bytes to results - this accumulates memory
    payload_size = getattr(state, 'config_payload_size', 1024)
    state.results.append(b'X' * payload_size)

    # [DATA] Increment task counter
    state.task_count = getattr(state, 'task_count', 0) + 1

    # [MEMORY TRACKING] Sample memory after each allocation for accurate peak detection
    # This is important for fast scenarios where background thread may not sample in time
    try:
        from gtpyhop import ResourceManager
        ResourceManager.sample_memory()
    except (ImportError, AttributeError):
        pass  # Memory tracking not available or not configured
    # END: Effects

    return state


def a_finalize_recursion(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:finalize

    Action signature:
        a_finalize_recursion(state)

    Action parameters:
        None

    Action purpose:
        Finalize recursive decomposition execution

    Preconditions:
        - State is initialized (state.initialized)

    Effects:
        - Execution complete flag (state.execution_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'initialized') and state.initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Execution completed
    state.execution_complete = True
    # END: Effects

    return state

# ============================================================================
# METHODS
# ============================================================================

def m_recursive_decomposition(state: State, depth: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_recursive_decomposition(state, depth)

    Method parameters:
        depth: Recursion depth k (yields 2^k leaf tasks)

    Method purpose:
        Top-level method orchestrating recursive decomposition workflow

    Preconditions:
        - Depth is non-negative

    Task decomposition:
        - a_initialize_recursion: Initialize state with payload
        - m_recurse_level: Recursively decompose to 2^depth leaf tasks
        - a_finalize_recursion: Mark execution complete

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(depth, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if depth < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No state preconditions for top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_recursion",),
        ("m_recurse_level", depth),
        ("a_finalize_recursion",)
    ]
    # END: Task Decomposition


def m_recurse_level(state: State, level: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_recurse_level(state, level)

    Method parameters:
        level: Current recursion level (0 = base case)

    Method purpose:
        Binary recursive decomposition: level k -> two copies of level k-1

        This implements Alford et al. (2015) Section 4's counting structure:
        - m_recurse_level(0) -> [a_execute_leaf_task]
        - m_recurse_level(k) -> [m_recurse_level(k-1), m_recurse_level(k-1)]

        Result: m_recurse_level(k) produces 2^k leaf task executions.

    Preconditions:
        - Level is non-negative
        - State is initialized (for level 0 base case)

    Task decomposition:
        - If level == 0: Single leaf task execution
        - If level > 0: Two recursive calls to level-1

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(level, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if level < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # For base case, state must be initialized
    if level == 0:
        if not (hasattr(state, 'initialized') and state.initialized):
            return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    if level == 0:
        # Base case: execute single leaf task
        return [
            ("a_execute_leaf_task",)
        ]
    else:
        # Recursive case: binary decomposition
        # Two totally-ordered copies of the next lower level
        return [
            ("m_recurse_level", level - 1),
            ("m_recurse_level", level - 1)
        ]
    # END: Task Decomposition

# ============================================================================
# DOMAIN REGISTRATION
# ============================================================================

declare_actions(
    a_initialize_recursion,
    a_execute_leaf_task,
    a_finalize_recursion
)

declare_task_methods('m_recursive_decomposition', m_recursive_decomposition)
declare_task_methods('m_recurse_level', m_recurse_level)
