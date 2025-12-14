# GTPyhop version 1.7.0

[![Python Version](https://img.shields.io/badge/python-3%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Clear%20BSD-green.svg)](https://github.com/PCfVW/GTPyhop/blob/pip/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/gtpyhop)](https://pypi.org/project/gtpyhop/)

GTPyhop is an HTN planning system based on [Pyhop](https://bitbucket.org/dananau/pyhop/src/master/), but generalized to plan for both goals and tasks.

[Dana Nau](https://www.cs.umd.edu/~nau/) is the original author of GTPyhop.

## The pip Branch

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) is forked from [Dana Nau's GTPyhop main branch](https://github.com/dananau/GTPyhop) and refactored for PyPI distribution.

The file tree structure of [this pip branch](https://github.com/PCfVW/GTPyhop/tree/pip), produced with the help of [_GithubTree](https://github.com/mgks/GitHubTree), is the following:

```
📄 LICENSE.txt
📄 pyproject.toml
📄 README.md
📁 docs/
    ├── 📄 all_examples.md
    ├── 📄 changelog.md
    ├── 📄 gtpyhop_domain_style_guide.md
    ├── 📄 gtpyhop_problems_style_guide.md
    ├── 📄 logging.md
    ├── 📄 running_examples.md
    └── 📄 thread_safe_sessions.md
📁 src/
    └── 📁 gtpyhop/
        ├── 📄 __init__.py
        ├── 📁 examples/
            ├── 📄 __init__.py
            ├── 📄 backtracking_htn.py
            ├── 📁 blocks_goal_splitting/
                ├── 📄 __init__.py
                ├── 📄 actions.py
                ├── 📄 examples.py
                ├── 📄 methods.py
                └── 📄 README.txt
            ├── 📁 blocks_gtn/
                ├── 📄 __init__.py
                ├── 📄 actions.py
                ├── 📄 examples.py
                ├── 📄 methods.py
                └── 📄 README.txt
            ├── 📁 blocks_hgn/
                ├── 📄 __init__.py
                ├── 📄 actions.py
                ├── 📄 examples.py
                └── 📄 methods.py
            ├── 📁 blocks_htn/
                ├── 📄 __init__.py
                ├── 📄 actions.py
                ├── 📄 examples.py
                └── 📄 methods.py
            ├── 📁 ipc-2020-total-order/
                ├── 📄 benchmarking.py
                ├── 📄 benchmarking_quickstart.md
                ├── 📁 Blocksworld-GTOHP/
                    ├── 📄 __init__.py
                    ├── 📄 domain.py/
                    ├── 📄 ipc-2020-to-bw-gtohp-readme.md
                    └── 📄 problems.py/
                └── 📁 Childsnack/
                    ├── 📄 __init__.py
                    ├── 📄 domain.py/
                    ├── 📄 ipc-2020-to-childsnack-readme.md
                    └── 📄 problems.py/
            ├── 📁 mcp-orchestration/
                ├── 📄 __init__.py
                ├── 📄 benchmarking.py
                ├── 📄 benchmarking_quickstart.md
                ├── 📁 bio_opentrons/
                    ├── 📄 __init__.py
                    ├── 📄 domain.py
                    ├── 📄 problems.py
                    └── 📄 README.md
                ├── 📁 cross_server/
                    ├── 📄 __init__.py
                    ├── 📄 domain.py
                    ├── 📄 problems.py
                    └── 📄 README.md
                ├── 📁 drug_target_discovery/
                    ├── 📄 __init__.py
                    ├── 📄 domain.py
                    ├── 📄 problems.py
                    └── 📄 README.md
                ├── 📁 omega_hdq_dna_bacteria_flex_96_channel/
                    ├── 📄 __init__.py
                    ├── 📄 domain.py
                    ├── 📄 problems.py
                    └── 📄 README.md
                └── 📁 tnf_cancer_modelling/
                    ├── 📄 __init__.py
                    ├── 📄 domain.py
                    ├── 📄 problems.py
                    └── 📄 README.md
            ├── 📄 logistics_hgn.py
            ├── 📄 pyhop_simple_travel_example.py
            ├── 📄 regression_tests.py
            ├── 📄 simple_hgn.py
            ├── 📄 simple_htn_acting_error.py
            └── 📄 simple_htn.py
        ├── 📄 logging_system.py
        ├── 📄 main.py
        └── 📁 test_harness/
            ├── 📄 __init__.py
            └── 📄 test_harness.py
```

## Installation from PyPI (Recommended: Version 1.7.0)

**GTPyhop 1.7.0 is the latest version with enhanced MCP orchestration examples, Opentrons Flex domains, and comprehensive style guides.** For new projects, especially those requiring reliable planning and benchmarking, use 1.7.0:

```bash
pip install gtpyhop>=1.7.0
```

For basic single-threaded planning, any version works:
```bash
pip install gtpyhop
```

[uv](https://docs.astral.sh/uv/) can of course be used if you prefer:

```bash
uv pip install gtpyhop
```

## Installation from github

Alternatively, you can directly install from github:

```bash
git clone -b pip https://github.com/PCfVW/GTPyhop.git
cd GTPyhop
pip install .
```

## Testing your installation

We suggest you give gtpyhop a try straight away; open a terminal and start an interactive python session:
```bash
python
```

.. and import gtpyhop to run the regression tests:

```python
# Import the main GTPyhop planning system
import gtpyhop
```

The following should be printed in your terminal:

```code
Imported GTPyhop version 1.7.0
Messages from find_plan will be prefixed with 'FP>'.
Messages from run_lazy_lookahead will be prefixed with 'RLL>'.
Using session-based architecture with structured logging.
```

Now import the regression tests module:

```python
from gtpyhop.examples import regression_tests
```

Be prepared to see a lot of information on the screen about the examples and how to solve them, with different levels of verbosity; with this in mind, run the regression tests:

```python
# Run legacy regression tests (backward compatible)
regression_tests.main()

# Or run session-based regression tests (recommended for 1.3.0+)
regression_tests.main_session()
```

The last line printed in your terminal should be:

```code
Finished without error.
```

**For GTPyhop 1.3.0+:** You can also run regression tests from the command line:

```bash
# Legacy mode
python -m gtpyhop.examples.regression_tests

# Session mode (thread-safe)
python -m gtpyhop.examples.regression_tests --session
```

Happy Planning!

## Thread-Safe Sessions (1.3.0+)

**GTPyhop 1.3.0 introduces session-based, thread-safe planning** that enables reliable concurrent execution and isolated planning contexts. This is a major architectural enhancement while maintaining 100% backward compatibility.

### Key Benefits
- **Thread-safe concurrent planning**: Multiple planners can run simultaneously without interference
- **Isolated execution contexts**: Each session has its own configuration, logs, and statistics
- **Structured logging system**: Programmatic access to planning traces, statistics, and debugging information
- **Timeout management**: Built-in timeout enforcement and resource management
- **Session persistence**: Save and restore planning sessions across runs

### Quick Start with Sessions
```python
import gtpyhop

# Create a Domain and define actions/methods (same as before)
my_domain = gtpyhop.Domain('my_domain')
# ... define actions and methods ...

# NEW: Use session-based planning for thread safety
with gtpyhop.PlannerSession(domain=my_domain, verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, [('transport', 'obj1', 'loc2')])
        if result.success:
            print(result.plan)
```

**For detailed examples, concurrent planning patterns, and complete API reference, see [Thread-Safe Sessions Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md)**

## Let's HTN Start!

You have successfully installed and tested gtpyhop; it's time to declare your own planning problems in gtpyhop.

### Very first HTN example

The key pattern is: create a Domain → define actions/methods → declare them → define initial state → use gtpyhop.find_plan() to solve problems.

In the first three steps, we give simple illustrations on Domain creation, action and task method definition, and how to declare them; make sure you declared an initial state before calling for planning; in step 5 below, you'll find the code for a complete example.

**1. First, create a Domain to hold your definitions**

```python
import gtpyhop

# Create a Domain
gtpyhop.Domain('my_domain')
```

**2. Define Actions**

Actions are atomic operations that directly modify a state: actions are Python functions where the first argument is the current `state`, and the others are the action's arguments telling what changes the action shall bring to the state.

For example, the function my_action(state, arg1, arg2) below implements the action ('my_action', arg1, arg2). In the following code, `arg1` is used as an object key to check and modify its position, while `arg2` is used both as a condition to check against and as a key to update the status:

```python
def my_action(state, arg1, arg2):
    # Check preconditions using arg1 and arg2
    if state.pos[arg1] == arg2:
        # Modify state using arg1 and arg2
        state.pos[arg1] = 'new_location'
        state.status[arg2] = 'updated'
        return state  # Success
    return False  # Failure

# Declare actions
gtpyhop.declare_actions(my_action, another_action)
```

**3. Define Task Methods**

During planning, Task methods decompose compound tasks into subtasks (which shall be further decomposed) and actions (whose Python functions will be executed).

Task methods are also Python functions where the first argument is the current `state`, and the others can be passed to the subtasks and actions.

In the following code, `arg1` is used as an argument to the subtasks (perhaps specifying what object to work with), while `arg2` is used as an argument to the action (perhaps specifying a target location or condition):

```python
def method_for_task(state, arg1, arg2):
    # Check if this method is applicable
    if some_condition:
        # Return list of subtasks/actions
        return [('subtask1', arg1), ('action1', arg2)]
    return False  # Method not applicable

# Declare task methods
gtpyhop.declare_task_methods('task_name', method_for_task, alternative_method)
```

**4. Define Initial State**
Give a description of the initial state, including the values of all relevant state variables; in the following code, `pos` is a dictionary that maps objects to their locations:

```python
# Define initial state
initial_state = gtpyhop.State('initial_state')
initial_state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}
```

**5. Here is the complete example:**

```python
import gtpyhop

# Domain creation
gtpyhop.Domain('my_domain')

# Actions
def move(state, obj, target):
    if obj in state.pos:
        state.pos[obj] = target
        return state
    return False

gtpyhop.declare_actions(move)

# Task methods
def transport(state, obj, destination):
    current = state.pos[obj]
    if current != destination:
        return [('move', obj, destination)]
    return []

gtpyhop.declare_task_methods('transport', transport)

# Define initial state
initial_state = gtpyhop.State('initial_state')
initial_state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}

# Find plan
gtpyhop.set_verbose_level(1)
plan = gtpyhop.find_plan(initial_state, [('transport', 'obj1', 'loc2')])
print(plan)
```

Put this code in a file, say `my_very_first_htn_example.py`, and run it from a terminal:

```bash
python my_very_first_htn_example.py
```

Does it run correctly? Increase the verbosity level to 2 or 3 and run it again to see more information about the planning process.

### Session-Based Version (Recommended for 1.3.0+)

For better isolation and thread safety, use the session-based approach:

```python
import gtpyhop

# Domain creation (same as above)
my_domain = gtpyhop.Domain('my_domain')
state = gtpyhop.State('initial_state')
state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}

# Define actions and methods (same as above)
def move(state, obj, target):
    if obj in state.pos:
        state.pos[obj] = target
        return state
    return False

gtpyhop.declare_actions(move)

def transport(state, obj, destination):
    current = state.pos[obj]
    if current != destination:
        return [('move', obj, destination)]
    return []

gtpyhop.declare_task_methods('transport', transport)

# NEW: Use session-based planning
with gtpyhop.PlannerSession(domain=my_domain, verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, [('transport', 'obj1', 'loc2')])
        if result.success:
            print("Plan found:", result.plan)
            print("Planning stats:", result.stats)

            # NEW: Access structured logs
            logs = session.logger.get_logs()
            print(f"Generated {len(logs)} log entries during planning")
        else:
            print("Planning failed:", result.error)
```

**Benefits of the session approach:**
- Thread-safe for concurrent use
- Isolated configuration per session
- Built-in timeout and resource management
- Structured result objects with statistics
- **Comprehensive logging system** with programmatic access to planning traces
- Session persistence capabilities

### 🔄 Migration from Pre-1.3.0 Versions

**Existing code continues to work unchanged** - GTPyhop 1.3.0 maintains 100% backward compatibility.

**To leverage 1.3.0 features:**
1. **For single-threaded code**: No changes required, but consider sessions for better structure
2. **For concurrent code**: Migrate to `PlannerSession` to avoid race conditions
3. **For production systems**: Use sessions for timeout management and structured logging

**Simple migration pattern:**
```python
# Before (still works)
plan = gtpyhop.find_plan(state, tasks)

# After (recommended)
with gtpyhop.PlannerSession(domain=my_domain) as session:
    with session.isolated_execution():
        result = session.find_plan(state, tasks)
        plan = result.plan if result.success else None
```

### 📋 Version Selection Guide

| Use Case | Recommended Version | Why |
|----------|-------------------|-----|
| **New projects** | **1.7.0+** | Latest features, enhanced MCP orchestration, comprehensive style guides |
| **MCP integration** | **1.7.0+** | Cross-server orchestration, Opentrons Flex domains, drug discovery workflows |
| **Concurrent/parallel planning** | **1.7.0+** | Thread-safe sessions by default, prevent race conditions |
| **Production systems** | **1.7.0+** | Robustness improvements, timeout management, structured logging |
| **Benchmarking/evaluation** | **1.7.0+** | Resource monitoring, IPC domains, 5 validated MCP examples |
| **Web APIs/servers** | **1.7.0+** | Isolated sessions per request, timeout handling |
| **Educational/simple scripts** | Any version | All versions support basic planning |
| **Legacy code maintenance** | Keep current | All versions are backward compatible |

### Additional Information

Please read [Dana's additional information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md) of how to implement:
- [States](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#states)
- [Actions](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#actions)
- [Tasks and task methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#3-tasks-and-task-methods)
- [Goals and goal methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#4-goals-and-goal-methods)
- ...and much more about GTPyhop!

## Examples

GTPyhop includes comprehensive examples demonstrating various planning techniques. **All examples support both legacy and session modes** for maximum flexibility and thread safety.

### 🚀 Quick Example Run

**Try GTPyhop immediately:**

```bash
# Legacy mode (backward compatible)
python -m gtpyhop.examples.simple_htn

# Session mode (thread-safe, recommended for 1.3.0+)
python -m gtpyhop.examples.simple_htn --session
```

📖 **For comprehensive example documentation, see [All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)**

## 📚 Documentation

GTPyhop 1.7.0+ includes comprehensive documentation organized in the `docs/` folder:

### Core Documentation
- **[All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)** - Pedagogical details about all HTN Planning examples
- **[Running Examples](https://github.com/PCfVW/GTPyhop/blob/pip/docs/running_examples.md)** - Detailed instructions for executing examples
- **[Structured Logging](https://github.com/PCfVW/GTPyhop/blob/pip/docs/logging.md)** - Comprehensive logging system documentation
- **[Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md)** - Complete guide to 1.3.0 session-based architecture
- **[Version History](https://github.com/PCfVW/GTPyhop/blob/pip/docs/changelog.md)** - Complete changelog and version information

### Style Guides (1.6.0+, Enhanced in 1.7.0)
- **[Domain Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_domain_style_guide.md)** - LibCST-compatible conventions for writing domain files (actions and methods) with proper type hints, docstrings, and comment markers (Version 1.1.0)
- **[Problems Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md)** - Conventions for writing problem files with initial states and goal tasks (Version 2.1.0)

### Specialized Documentation

#### IPC 2020 Total Order Domains
- **[Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/benchmarking_quickstart.md)** - Performance benchmarking guide
- **[Blocksworld-GTOHP Domain](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/Blocksworld-GTOHP/ipc-2020-to-bw-gtohp-readme.md)** - IPC 2020 Blocksworld domain
- **[Childsnack Domain](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/Childsnack/ipc-2020-to-cs-gtohp-readme.md)** - IPC 2020 Childsnack domain

#### MCP Orchestration Examples (1.5.0+, Enhanced in 1.7.0)
- **[MCP Orchestration Benchmarking](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/benchmarking_quickstart.md)** - MCP orchestration benchmarking guide (updated for thread-safe sessions)
- **[Bio-Opentrons PCR Workflow](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/bio_opentrons/README.md)** - PCR workflow automation with Opentrons Flex (dynamic 4-96 sample scaling, three-server architecture, 6 scenarios)
- **[Cross-Server Orchestration](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/cross_server/README.md)** - Cross-server HTN plan execution (2 scenarios, fixed gripper logic in 1.7.0)
- **[Drug Target Discovery](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/drug_target_discovery/README.md)** - Drug target discovery pipeline using OpenTargets platform (3 scenarios, 8 actions each, new in 1.7.0)
- **[Omega HDQ DNA Extraction](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/omega_hdq_dna_bacteria_flex_96_channel/README.md)** - DNA extraction workflow with Opentrons Flex 96-channel (magnetic bead purification, four-server architecture, 3 scenarios)
- **[TNF Cancer Modelling](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/tnf_cancer_modelling/README.md)** - Multiscale cancer modeling workflow (1 scenario, 12 actions)

### External Resources
- **[Dana's Additional Information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md)** - Core GTPyhop concepts (states, actions, goals, methods)


## New Features

### Iterative Planning Strategy

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) introduces a new iterative planning strategy that enhances the planner's capabilities for large planning scenarios; it is the default strategy.

- How it works: Uses an explicit stack data structure
- Memory usage: More memory-efficient, no call stack buildup
- Limitations: No recursion limit constraints
- Backtracking: Explicit stack management for exploring alternatives
- Use cases:
    - Large planning problems that might exceed recursion limits
    - Memory-constrained environments
    - Production systems requiring reliability

Once gtpyhop is imported, Dana Nau's original recursive strategy can be set by calling:

```python
set_recursive_planning(True)  # Planning strategy now is recursive
```

Recursive Planning Strategy:
- How it works: Uses Python's call stack with recursive function calls
- Memory usage: Each recursive call adds a frame to the call stack
- Limitations: Limited by Python's recursion limit (default 1000)
- Backtracking: Natural backtracking through function returns
- Use cases:
    - Small to medium planning problems
    - When you need to see traditional backtracking behavior
    - Educational purposes or debugging

Of course you can get back to the iterative planning strategy by calling:

```python
set_recursive_planning(False)  # Planning strategy now is iterative
```

### New Functions

#### Functions Added in 1.4.0 (Robustness, Validation & Benchmarking)

main.py

- `validate_plan_from_goal` - Preconditions of each action are successively satisfied from the initial state to eventually produce the goal state.

**Benchmarking** (benchmarking.py)
- `safe_add_to_path`, `setup_gtpyhop_imports`,
- `load_domain_package`,`validate_domain_package`,`load_domain_package`,`load_domain_package`,
- `create_argument_parser`, `list_available_domains`, `main`,
- `ResourceUsage` (data class),`BenchmarkResult` (data classe),
- `DomainHandler` (abstract class),
    - `create_multigoal` (staticmethod),
- `PlannerBenchmark` (class)
    - `_get_memory_usage`, `_calculate_resource_metrics`, `track_resources` (methods)
    - `run_single`, `run_multiple`, `_calculate_column_widths`, `print_summary` (methods)

#### Functions Added in 1.3.0 (Thread-Safe Sessions)
**Session Management:**
- `PlannerSession` (class) - Isolated, thread-safe planning context
- `create_session`, `get_session`, `destroy_session`, `list_sessions` - Session lifecycle management
- `PlanningTimeoutError` (exception) - Timeout handling for session-scoped operations

**Session Persistence:**
- `SessionSerializer` (class), `restore_session`, `restore_all_sessions` - Session persistence and recovery
- `set_persistence_directory`, `get_persistence_directory` - Configure auto-save/recovery

**Enhanced Planning:**
- `session.find_plan()` - Per-session planning with timeout and expansion limits
- `session.isolated_execution()` - Context manager for safe global state management

#### Functions Added in 1.2.1 (Iterative Planning & Utilities)
**Domain Management:**
- `print_domain_names`, `find_domain_by_name`, `is_domain_created`
- `set_current_domain`, `get_current_domain`

**Planning Strategy Control:**
- `set_recursive_planning`, `get_recursive_planning`, `reset_planning_strategy`
- `set_verbose_level`, `get_verbose_level`

**Iterative Planning Implementation:**
- `seek_plan_iterative` and related iterative planning functions
- `refine_multigoal_and_continue_iterative`, `refine_unigoal_and_continue_iterative`
- `refine_task_and_continue_iterative`, `apply_action_and_continue_iterative`

### Renaming

`_recursive` has been added at the end of the identifiers of the original functions involved in seeking for a plan: 

- seek_plan &rarr; `seek_plan_recursive`
- _apply_action_and_continue &rarr; `apply_action_and_continue_recursive`
- _refine_multigoal_and_continue &rarr; `refine_multigoal_and_continue_recursive`
- _refine_unigoal_and_continue &rarr; `refine_unigoal_and_continue_recursive`
- _refine_task_and_continue &rarr; `refine_task_and_continue_recursive`



