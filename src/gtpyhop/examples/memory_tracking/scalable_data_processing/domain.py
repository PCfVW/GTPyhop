"""
Scalable Data Processing Domain for GTPyhop Memory Tracking

This domain demonstrates memory tracking capabilities with configurable
memory-intensive planning operations. Memory behavior is controlled via
state configuration properties set in problems.py.

Configuration Properties (set in initial state):
  - config_data_size: int - Number of data items to create
  - config_data_type: str - 'int', 'string', or 'dict'
  - config_num_transforms: int - Number of transformation copies (1-16)
  - config_accumulate: bool - Keep all intermediate results
  - config_cleanup: bool - Release memory at end

-- Generated 2026-01-09
"""

import sys
import os
from typing import Optional, Union, List, Tuple, Dict

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import Domain, State, declare_actions, declare_task_methods, set_current_domain
except ImportError:
    # Graceful degradation: supports direct domain.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import Domain, State, declare_actions, declare_task_methods, set_current_domain

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("scalable_data_processing")
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
#  config_data_size: int [CONFIG] - Number of data items
#  config_data_type: str [CONFIG] - 'int', 'string', or 'dict'
#  config_num_transforms: int [CONFIG] - Number of transforms (1-16)
#  config_accumulate: bool [CONFIG] - Keep intermediate results
#  config_cleanup: bool [CONFIG] - Release memory at end
#
# Step 1: a_initialize_memory_demo
#  (P) config_data_size [CONFIG]
#  (E) demo_initialized: True [ENABLER]
#
# Step 2: a_allocate_large_dataset
#  (P) demo_initialized [ENABLER]
#  (P) config_data_type [CONFIG]
#  (E) large_dataset: List [DATA]
#  (E) dataset_allocated: True [ENABLER]
#
# Step 3: a_process_dataset_chunk
#  (P) dataset_allocated [ENABLER]
#  (P) config_accumulate [CONFIG]
#  (E) processed_chunks: List [DATA]
#  (E) chunk_count: int [DATA]
#
# Step 4: a_create_memory_intensive_structure
#  (P) dataset_allocated [ENABLER]
#  (P) config_num_transforms [CONFIG]
#  (E) memory_structure: Dict [DATA]
#  (E) structure_created: True [ENABLER]
#
# Step 5: a_perform_memory_operations
#  (P) structure_created [ENABLER]
#  (P) config_accumulate [CONFIG]
#  (E) operation_results: List [DATA]
#  (E) operations_complete: True [ENABLER]
#
# Step 6: a_cleanup_memory
#  (P) operations_complete [ENABLER]
#  (P) config_cleanup [CONFIG]
#  (E) memory_cleaned: True [ENABLER]
# ============================================================================

# ============================================================================
# HELPER FUNCTIONS FOR MEMORY-INTENSIVE DATA GENERATION
# ============================================================================

def _generate_int_item(index: int) -> int:
    """Generate an integer item (~28 bytes in Python)."""
    return index * 12345 + 67890

def _generate_string_item(index: int) -> str:
    """Generate a string item (~500 bytes each)."""
    return f"data_item_{index:010d}_" + "X" * 480

def _generate_dict_item(index: int) -> Dict:
    """Generate a dictionary item (~1KB+ each)."""
    return {
        'id': index,
        'name': f"item_{index:010d}",
        'description': f"This is a detailed description for item number {index} " * 5,
        'values': [index * i for i in range(10)],
        'metadata': {'created': index, 'modified': index * 2, 'version': index % 100}
    }

def _generate_data_item(index: int, data_type: str):
    """Generate a data item based on configured type."""
    if data_type == 'string':
        return _generate_string_item(index)
    elif data_type == 'dict':
        return _generate_dict_item(index)
    else:  # default to int
        return _generate_int_item(index)

def _transform_item(item, transform_index: int):
    """Apply a transformation to an item."""
    if isinstance(item, int):
        # Different mathematical transformations for integers
        transforms = [
            lambda x: x * 2,
            lambda x: x * x,
            lambda x: x * x * x,
            lambda x: x + 1000000,
            lambda x: x * 3 + 500,
            lambda x: x * 5 - 100,
            lambda x: x * 7,
            lambda x: x * 11,
            lambda x: x * 13,
            lambda x: x * 17,
            lambda x: x * 19,
            lambda x: x * 23,
            lambda x: x * 29,
            lambda x: x * 31,
            lambda x: x * 37,
            lambda x: x * 41,
        ]
        return transforms[transform_index % len(transforms)](item)
    elif isinstance(item, str):
        # String transformations - create modified copies
        transforms = [
            lambda s: s.upper(),
            lambda s: s.lower(),
            lambda s: s[::-1],
            lambda s: s + "_copy",
            lambda s: "prefix_" + s,
            lambda s: s.replace("X", "Y"),
            lambda s: s.replace("_", "-"),
            lambda s: s + s[-100:],
            lambda s: s[:200] + "_mid_" + s[200:],
            lambda s: "BEGIN_" + s + "_END",
            lambda s: s.replace("data", "DATA"),
            lambda s: s.replace("item", "ITEM"),
            lambda s: s + "_v2",
            lambda s: s + "_v3",
            lambda s: s + "_v4",
            lambda s: s + "_v5",
        ]
        return transforms[transform_index % len(transforms)](item)
    elif isinstance(item, dict):
        # Dictionary transformations - create modified copies
        new_dict = item.copy()
        new_dict[f'transform_{transform_index}'] = True
        new_dict['description'] = item.get('description', '') + f" [Transform {transform_index}]"
        new_dict['values'] = [v * (transform_index + 1) for v in item.get('values', [])]
        return new_dict
    return item

# ============================================================================
# ACTIONS
# ============================================================================

def a_initialize_memory_demo(state: State, data_size: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:initialize

    Action signature:
        a_initialize_memory_demo(state, data_size)

    Action parameters:
        data_size: Size of dataset to create (number of elements)

    Action purpose:
        Initialize memory tracking demonstration with specified data size

    Preconditions:
        None (initialization action)

    Effects:
        - Demo initialized flag (state.demo_initialized) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(data_size, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if data_size <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for initialization action
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Demo initialization completed - gates dataset allocation
    state.demo_initialized = True
    # END: Effects

    return state

def a_allocate_large_dataset(state: State, data_size: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:allocate

    Action signature:
        a_allocate_large_dataset(state, data_size)

    Action parameters:
        data_size: Number of elements to allocate

    Action purpose:
        Allocate large dataset based on configured data type

    Preconditions:
        - Demo is initialized (state.demo_initialized)

    Effects:
        - Large dataset allocated (state.large_dataset) [DATA]
        - Dataset allocation completed (state.dataset_allocated) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(data_size, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if data_size <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'demo_initialized') and state.demo_initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # Read configuration from state
    data_type = getattr(state, 'config_data_type', 'int')

    # [DATA] Large dataset for memory demonstration - type based on config
    state.large_dataset = [_generate_data_item(i, data_type) for i in range(data_size)]

    # [ENABLER] Dataset allocation completed - gates processing operations
    state.dataset_allocated = True
    # END: Effects

    return state

def a_process_dataset_chunk(state: State, chunk_size: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:process

    Action signature:
        a_process_dataset_chunk(state, chunk_size)

    Action parameters:
        chunk_size: Size of chunks to process

    Action purpose:
        Process dataset in chunks, optionally accumulating results

    Preconditions:
        - Dataset is allocated (state.dataset_allocated)
        - Large dataset exists (state.large_dataset)

    Effects:
        - Processed chunks list (state.processed_chunks) [DATA]
        - Chunk count (state.chunk_count) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(chunk_size, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if chunk_size <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'dataset_allocated') and state.dataset_allocated):
        return False
    if not (hasattr(state, 'large_dataset') and state.large_dataset):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # Read configuration
    accumulate = getattr(state, 'config_accumulate', False)

    # [DATA] Process dataset in chunks
    if not hasattr(state, 'processed_chunks') or not accumulate:
        state.processed_chunks = []

    dataset = state.large_dataset
    for i in range(0, len(dataset), chunk_size):
        chunk = dataset[i:i + chunk_size]
        # Create processed copies of each chunk item
        processed_chunk = [_transform_item(item, 0) for item in chunk]
        state.processed_chunks.append(processed_chunk)

    # [DATA] Track number of chunks processed
    state.chunk_count = len(state.processed_chunks)
    # END: Effects

    return state

def a_create_memory_intensive_structure(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:create_structure

    Action signature:
        a_create_memory_intensive_structure(state)

    Action parameters:
        None

    Action purpose:
        Create memory-intensive data structure with configurable transforms

    Preconditions:
        - Dataset is allocated (state.dataset_allocated)
        - Large dataset exists (state.large_dataset)

    Effects:
        - Memory-intensive structure (state.memory_structure) [DATA]
        - Structure creation completed (state.structure_created) [ENABLER]

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
    if not (hasattr(state, 'dataset_allocated') and state.dataset_allocated):
        return False
    if not (hasattr(state, 'large_dataset') and state.large_dataset):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # Read configuration - number of transformations to create
    num_transforms = getattr(state, 'config_num_transforms', 4)
    num_transforms = max(1, min(16, num_transforms))  # Clamp to 1-16

    # [DATA] Create memory-intensive dictionary structure with N transformations
    state.memory_structure = {}

    # Always keep original
    state.memory_structure['original'] = state.large_dataset.copy()

    # Create configured number of transformations
    for t in range(num_transforms):
        transform_name = f'transform_{t:02d}'
        state.memory_structure[transform_name] = [
            _transform_item(item, t) for item in state.large_dataset
        ]

    # [ENABLER] Structure creation completed - gates memory operations
    state.structure_created = True
    # END: Effects

    return state

def a_perform_memory_operations(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:operations

    Action signature:
        a_perform_memory_operations(state)

    Action parameters:
        None

    Action purpose:
        Perform memory-intensive operations on created structures

    Preconditions:
        - Memory structure is created (state.structure_created)
        - Memory structure exists (state.memory_structure)

    Effects:
        - Operation results (state.operation_results) [DATA]
        - Operations completed (state.operations_complete) [ENABLER]

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
    if not (hasattr(state, 'structure_created') and state.structure_created):
        return False
    if not (hasattr(state, 'memory_structure') and state.memory_structure):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # Read configuration
    accumulate = getattr(state, 'config_accumulate', False)

    # [DATA] Perform operations and store results
    structure = state.memory_structure

    if not hasattr(state, 'operation_results') or not accumulate:
        state.operation_results = []

    # Calculate statistics for each structure component
    for key, data_list in structure.items():
        if data_list:
            # Store metadata about each transformation
            result = {
                'transform': key,
                'count': len(data_list),
                'sample': str(data_list[0])[:100] if data_list else None
            }
            state.operation_results.append(result)

    # [ENABLER] Operations completed - gates cleanup
    state.operations_complete = True
    # END: Effects

    return state

def a_cleanup_memory(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: memory_server:cleanup

    Action signature:
        a_cleanup_memory(state)

    Action parameters:
        None

    Action purpose:
        Optionally clean up allocated memory structures based on config

    Preconditions:
        - Operations are complete (state.operations_complete)

    Effects:
        - Memory cleaned flag (state.memory_cleaned) [ENABLER]

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
    if not (hasattr(state, 'operations_complete') and state.operations_complete):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # Read configuration - whether to actually clean up
    do_cleanup = getattr(state, 'config_cleanup', True)

    # [ENABLER] Memory cleanup completed
    state.memory_cleaned = True

    # Only release memory if configured to do so
    if do_cleanup:
        if hasattr(state, 'large_dataset'):
            state.large_dataset = None
        if hasattr(state, 'memory_structure'):
            state.memory_structure = None
        if hasattr(state, 'processed_chunks'):
            state.processed_chunks = None
    # END: Effects

    return state

# ============================================================================
# METHODS
# ============================================================================

def m_memory_tracking_demo(state: State, data_size: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_memory_tracking_demo(state, data_size)

    Method parameters:
        data_size: Size of dataset for memory demonstration

    Method purpose:
        Demonstrate memory tracking through complete workflow

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_memory_demo: Initialize demo with data size
        - m_allocate_and_process: Allocate and process dataset
        - m_create_and_operate: Create structures and perform operations
        - a_cleanup_memory: Clean up allocated memory

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(data_size, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if data_size <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_memory_demo", data_size),
        ("m_allocate_and_process", data_size),
        ("m_create_and_operate",),
        ("a_cleanup_memory",)
    ]
    # END: Task Decomposition

def m_allocate_and_process(state: State, data_size: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_allocate_and_process(state, data_size)

    Method parameters:
        data_size: Size of dataset to allocate and process

    Method auxiliary parameters:
        chunk_size: int (computed as data_size // 10)

    Method purpose:
        Allocate dataset and process it in chunks

    Preconditions:
        - Demo is initialized (state.demo_initialized)

    Task decomposition:
        - a_allocate_large_dataset: Allocate the dataset
        - a_process_dataset_chunk: Process dataset in chunks

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(data_size, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if data_size <= 0: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    chunk_size = max(1, data_size // 10)  # Process in 10 chunks
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'demo_initialized') and state.demo_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_allocate_large_dataset", data_size),
        ("a_process_dataset_chunk", chunk_size)
    ]
    # END: Task Decomposition

def m_create_and_operate(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_create_and_operate(state)

    Method parameters:
        None

    Method purpose:
        Create memory structures and perform operations

    Preconditions:
        - Dataset is allocated (state.dataset_allocated)

    Task decomposition:
        - a_create_memory_intensive_structure: Create memory structures
        - a_perform_memory_operations: Perform operations on structures

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'dataset_allocated') and state.dataset_allocated):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_create_memory_intensive_structure",),
        ("a_perform_memory_operations",)
    ]
    # END: Task Decomposition

# ============================================================================
# DOMAIN REGISTRATION
# ============================================================================

declare_actions(
    a_initialize_memory_demo,
    a_allocate_large_dataset,
    a_process_dataset_chunk,
    a_create_memory_intensive_structure,
    a_perform_memory_operations,
    a_cleanup_memory
)

declare_task_methods('m_memory_tracking_demo', m_memory_tracking_demo)
declare_task_methods('m_allocate_and_process', m_allocate_and_process)
declare_task_methods('m_create_and_operate', m_create_and_operate)
