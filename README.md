# GTPyhop version 1.3.0

[![Python Version](https://img.shields.io/badge/python-3%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Clear%20BSD-green.svg)](https://github.com/PCfVW/GTPyhop/blob/pip/LICENSE.txt)

GTPyhop is a task-planning system based on [Pyhop](https://bitbucket.org/dananau/pyhop/src/master/), but generalized to plan for both goals and tasks.

[Dana Nau](https://www.cs.umd.edu/~nau/) is the original author of GTPyhop.

## The pip Branch

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) is forked from [Dana Nau's GTPyhop main branch](https://github.com/dananau/GTPyhop) and refactored for PyPI distribution.

The file tree structure of [this pip branch](https://github.com/PCfVW/GTPyhop/tree/pip), produced with the help of [_GithubTree](https://github.com/mgks/GitHubTree), is the following:

```
📄 LICENSE.txt
📄 pyproject.toml
📄 README.md
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

## Installation from PyPI (Recommended: Version 1.3.0)

**GTPyhop 1.3.0 is the latest version with thread-safe sessions and enhanced reliability.** For new projects, especially those requiring concurrent planning, use 1.3.0:

```bash
pip install gtpyhop>=1.3.0
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
Imported GTPyhop version 1.3.0
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

**🆕 New in 1.3.0:** You can also run regression tests from the command line:

```bash
# Legacy mode
python -m gtpyhop.examples.regression_tests

# Session mode (thread-safe)
python -m gtpyhop.examples.regression_tests --session
```

Happy Planning!

## 🆕 New in 1.3.0: Thread-Safe Sessions

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

📖 **For detailed examples, concurrent planning patterns, and complete API reference, see [GTPyhop-1.3.0-Thread-Safe-Sessions.md](https://github.com/PCfVW/GTPyhop/blob/pip/GTPyhop-1.3.0-Thread-Safe-Sessions.md)**

## Usage

You have successfully installed and tested gtpyhop; it's time to declare your own planning problems in gtpyhop.

### Very first HTN example

The key pattern is: create a Domain → define actions/methods → declare them → use gtpyhop.find_plan() to solve problems.

In the first three steps, we give simple illustrations on Domain creation, action and task method definition, and how to declare them; in step 4 below, you'll find the code for a complete example.

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

**4. Here is a complete example:**

```python
import gtpyhop

# Domain creation
gtpyhop.Domain('my_domain')

# Define state
state = gtpyhop.State('initial_state')
state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}

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

# Find plan
gtpyhop.set_verbose_level(1)
plan = gtpyhop.find_plan(state, [('transport', 'obj1', 'loc2')])
print(plan)
```

Put this code in a file, say `my_very_first_htn_example.py`, and run it from a terminal:

```bash
python my_very_first_htn_example.py
```

Does it run correctly? Increase the verbosity level to 2 or 3 and run it again to see more information about the planning process.

### 🆕 Session-Based Version (Recommended for 1.3.0+)

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
| **New projects** | **1.3.0** | Latest features, thread safety, better error handling |
| **Concurrent/parallel planning** | **1.3.0** | Thread-safe sessions prevent race conditions |
| **Production systems** | **1.3.0** | Timeout management, structured logging, persistence |
| **Web APIs/servers** | **1.3.0** | Isolated sessions per request, timeout handling |
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

### 🚀 Running Examples

**All examples support dual-mode execution:**

```bash
# Legacy mode (backward compatible)
python -m gtpyhop.examples.simple_htn

# Session mode (thread-safe, recommended for 1.3.0+)
python -m gtpyhop.examples.simple_htn --session

# Session mode with custom verbosity and no pauses
python -m gtpyhop.examples.simple_htn --session --verbose 2 --no-pauses
```

**Command-line arguments (available in all migrated examples):**
- `--session`: Enable thread-safe session mode
- `--verbose N`: Set verbosity level (0-3, default: 1 in session mode)
- `--no-pauses`: Skip interactive pauses for automated testing

### 📋 Available Examples

#### **Simple Examples** (Basic concepts and techniques)

| Example | Description | Key Features |
|---------|-------------|--------------|
| `simple_htn.py` | Basic hierarchical task networks | HTN planning, verbosity levels, execution |
| `simple_hgn.py` | Basic hierarchical goal networks | HGN planning, goal-oriented tasks |
| `backtracking_htn.py` | Backtracking demonstration | Method failure handling, alternative paths |
| `simple_htn_acting_error.py` | Error handling patterns | Execution failures, replanning |
| `logistics_hgn.py` | Logistics domain planning | Multi-goal planning, transportation |
| `pyhop_simple_travel_example.py` | Travel planning | Basic domain modeling |

#### **Complex Block World Examples** (Advanced planning scenarios)

| Example | Description | Key Features |
|---------|-------------|--------------|
| `blocks_htn/` | Hierarchical task networks | Complex HTN methods, block manipulation |
| `blocks_hgn/` | Hierarchical goal networks | Goal decomposition, multigoals |
| `blocks_gtn/` | Goal task networks | Mixed task/goal planning |
| `blocks_goal_splitting/` | Goal splitting methodology | Built-in goal decomposition methods |

### 🧪 Testing Examples

**Run all examples automatically:**

```bash
# Test all examples in both modes
python test_migration.py

# Test only session mode
python test_migration.py --mode session

# Test only legacy mode
python test_migration.py --mode legacy
```

**Run regression tests:**

```bash
# Legacy regression tests
python -m gtpyhop.examples.regression_tests

# Session-based regression tests
python -m gtpyhop.examples.regression_tests --session
```

### 💡 Example Usage Patterns

**Interactive exploration:**
```bash
# Run with pauses to examine output step by step
python -m gtpyhop.examples.blocks_htn.examples --session --verbose 3
```

**Automated testing:**
```bash
# Run without pauses for scripts/CI
python -m gtpyhop.examples.blocks_htn.examples --session --no-pauses
```

**Concurrent planning (session mode only):**
```python
import threading
import gtpyhop

# Load example Domain
from gtpyhop.examples.blocks_htn import actions, methods

def plan_worker(session_id, state, goals):
    with gtpyhop.PlannerSession(domain=the_domain, verbose=1) as session:
        with session.isolated_execution():
            result = session.find_plan(state, goals)
            print(f"Session {session_id}: {result.plan}")

# Run multiple planners concurrently
threads = []
for i in range(3):
    t = threading.Thread(target=plan_worker, args=(i, initial_state, goals))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Structured Logging System

GTPyhop 1.3.0 introduces a comprehensive structured logging system that replaces traditional print statements with configurable, thread-safe logging. This system provides programmatic access to planning logs, statistics, and debugging information.

### 🎯 Why Structured Logging?

**Traditional challenges:**
- Print statements mixed with actual output
- No programmatic access to planning information
- Difficult to filter or analyze planning traces
- Thread safety issues in concurrent scenarios

**Structured logging benefits:**
- **Programmatic access**: Query and analyze logs programmatically
- **Thread isolation**: Each session maintains separate logs
- **Configurable output**: Control verbosity and formatting
- **Performance monitoring**: Built-in statistics and performance metrics
- **Backward compatibility**: Existing print-based output still works

### 🔧 How It Works

The logging system operates in both legacy and session modes:

**Legacy Mode:** Uses global logging with backward-compatible print output
**Session Mode:** Each `PlannerSession` has isolated logging with structured data collection

### 📊 Log Levels and Components

**Available log levels:**
- `DEBUG` (0): Detailed debugging information
- `INFO` (1): General planning information
- `WARNING` (2): Warning messages
- `ERROR` (3): Error conditions

**Common components:**
- `FP`: Messages from `find_plan()`
- `RLL`: Messages from `run_lazy_lookahead()`
- `domain`: Domain-related operations
- `session`: Session management
- `stdout_capture`: Captured print statements

### 💻 Basic Usage Examples

**Import note:** All logging classes and functions are available directly from the main `gtpyhop` module:

```python
import gtpyhop

# Logging classes are available as gtpyhop.LogLevel, gtpyhop.StructuredLogger, etc.
# Or import specific components:
from gtpyhop import LogLevel, StructuredLogger, get_logging_stats
```

#### **Session Mode Logging (Recommended)**

```python
import gtpyhop

# Create session with logging
with gtpyhop.PlannerSession(domain=my_domain, verbose=2) as session:
    with session.isolated_execution():
        result = session.find_plan(state, goals)

        # Access structured logs
        logs = session.logger.get_logs()  # Get all INFO+ logs
        debug_logs = session.logger.get_logs(min_level=gtpyhop.LogLevel.DEBUG)

        # Print log summary
        print(f"Generated {len(logs)} log entries")
        for log in logs:
            print(f"[{log['level']}] {log['component']}: {log['message']}")
```

#### **Custom Log Handlers**

```python
import gtpyhop

# Create custom logger
logger = gtpyhop.StructuredLogger("my_session")

# Add custom stdout handler with formatting
custom_handler = gtpyhop.StdoutLogHandler("[{level}] {component}: {message}")
logger.add_handler(custom_handler)

# Log custom messages
logger.info("planning", "Starting plan search", state_size=len(state.pos))
logger.debug("search", "Exploring method", method_name="transport_by_truck")
```

#### **Programmatic Log Analysis**

```python
# Run planning with logging
with gtpyhop.PlannerSession(domain=logistics_domain, verbose=3) as session:
    with session.isolated_execution():
        result = session.find_plan(initial_state, goals)

        # Analyze logs
        logs = session.logger.get_logs()

        # Count log entries by component
        component_counts = {}
        for log in logs:
            component = log['component']
            component_counts[component] = component_counts.get(component, 0) + 1

        print("Log summary by component:")
        for component, count in component_counts.items():
            print(f"  {component}: {count} entries")

        # Find error logs
        error_logs = [log for log in logs if log['level'] == 'ERROR']
        if error_logs:
            print(f"Found {len(error_logs)} errors:")
            for error in error_logs:
                print(f"  {error['message']}")
```

### 🧵 Thread-Safe Concurrent Logging

Each session maintains isolated logs, making concurrent planning safe:

```python
import threading
import gtpyhop

def concurrent_planner(session_id, domain, state, goals):
    """Each thread gets isolated logging."""
    with gtpyhop.PlannerSession(domain=domain, verbose=2) as session:
        with session.isolated_execution():
            result = session.find_plan(state, goals)

            # Each session has separate logs
            logs = session.logger.get_logs()
            print(f"Session {session_id}: {len(logs)} log entries")

            return result, logs

# Run multiple planners concurrently
threads = []
results = {}

for i in range(3):
    def worker(session_id=i):
        result, logs = concurrent_planner(session_id, domain, state, goals)
        results[session_id] = {"result": result, "logs": logs}

    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Analyze results from each session
for session_id, data in results.items():
    print(f"Session {session_id}: {len(data['logs'])} logs, "
          f"plan length: {len(data['result'].plan) if data['result'].success else 'failed'}")
```

### 📈 Performance Monitoring

The logging system includes built-in performance monitoring:

```python
import gtpyhop

with gtpyhop.PlannerSession(domain=my_domain, verbose=2) as session:
    with session.isolated_execution():
        result = session.find_plan(state, goals)

        # Get logging statistics
        stats = gtpyhop.get_logging_stats(session.logger)

        print(f"Logging Performance:")
        print(f"  Total entries: {stats.total_entries}")
        print(f"  Memory usage: {stats.memory_usage_mb:.2f} MB")
        print(f"  Entries by level: {stats.entries_by_level}")
```

### 🔄 Legacy Mode Compatibility

The logging system maintains backward compatibility with existing code:

```python
# Legacy code continues to work
gtpyhop.verbose = 2
plan = gtpyhop.find_plan(state, goals)  # Prints to stdout as before

# But you can also access logs programmatically
logger = gtpyhop.get_logger("default")  # Get default session logger
logs = logger.get_logs()
print(f"Legacy planning generated {len(logs)} log entries")
```

### 🛠️ Advanced Features

#### **Stdout Capture**

Capture and log print statements from legacy code:

```python
logger = gtpyhop.StructuredLogger("capture_session")

with logger.capture_stdout() as captured:
    # Any print statements here are captured and logged
    print("This will be captured")
    gtpyhop.find_plan(state, goals)  # Legacy prints captured

# Captured output is now in structured logs
logs = logger.get_logs()
stdout_logs = [log for log in logs if log['component'] == 'stdout_capture']
```

#### **Custom Log Filtering**

```python
# Filter logs by component and level
def filter_planning_logs(logs, component_filter=None, min_level='INFO'):
    filtered = []
    for log in logs:
        if component_filter and log['component'] != component_filter:
            continue
        if log['level'] not in ['DEBUG', 'INFO', 'WARNING', 'ERROR'][
            ['DEBUG', 'INFO', 'WARNING', 'ERROR'].index(min_level):]:
            continue
        filtered.append(log)
    return filtered

# Usage
planning_logs = filter_planning_logs(logs, component_filter='FP', min_level='INFO')
```

### 🎓 Integration with Examples

All migrated examples support structured logging in session mode:

```bash
# Run with high verbosity to see detailed logs
python -m gtpyhop.examples.blocks_htn.examples --session --verbose 3

# The logs are available programmatically when using session mode
```

**Example integration in your code:**

```python
# Import any migrated example domain
from gtpyhop.examples.blocks_htn import the_domain, actions, methods

# Use with structured logging
with gtpyhop.PlannerSession(domain=the_domain, verbose=2) as session:
    with session.isolated_execution():
        result = session.find_plan(initial_state, goals)

        # Access detailed planning logs
        logs = session.logger.get_logs()
        method_calls = [log for log in logs if 'method' in log.get('context', {})]
        print(f"Called {len(method_calls)} methods during planning")
```

### 📚 Documentation Structure

- **README.md** (this file): Installation, basic usage, and overview of all features
- **[GTPyhop-1.3.0-Thread-Safe-Sessions.md](https://github.com/PCfVW/GTPyhop/tree/pipGTPyhop-1.3.0-Thread-Safe-Sessions.md)**: Comprehensive guide to 1.3.0 session-based architecture
  - Detailed concurrent planning examples
  - Complete API reference for session management
  - Migration guide from global API to sessions
  - Performance considerations and best practices
- **[Dana's additional information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md)**: Core GTPyhop concepts (states, actions, goals, methods)

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


## Version History

### 🚀 **1.3.0 — Thread-Safe Sessions** (Latest, Recommended)
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.3.0/**

**Major Features:**
- **🔒 Thread-safe session-based architecture** - Reliable concurrent planning
- **⏱️ Timeout management** - Built-in timeout enforcement and resource management
- **💾 Session persistence** - Save and restore planning sessions
- **📊 Structured logging** - Programmatic access to planning logs and statistics
- **🔧 Enhanced error handling** - Graceful degradation and comprehensive error reporting
- **📚 Complete example migration** - All 10 examples support both legacy and session modes

**Examples Migration Status:** ✅ **Complete** - All examples now support dual-mode execution:
- 6 simple examples: `simple_htn`, `simple_hgn`, `backtracking_htn`, `simple_htn_acting_error`, `logistics_hgn`, `pyhop_simple_travel_example`
- 4 complex block world examples: `blocks_htn`, `blocks_hgn`, `blocks_gtn`, `blocks_goal_splitting`
- Unified command-line interface: `--session`, `--verbose N`, `--no-pauses`
- Comprehensive test coverage: 9/9 examples pass in both legacy and session modes

**Compatibility:** 100% backward compatible with GTPyhop v1.2.1

**When to use:** New projects, concurrent planning, production systems, web APIs

📖 **[Complete 1.3.0  Thread‑Safe Sessions documentation →](https://github.com/PCfVW/GTPyhop/blob/pip/GTPyhop-1.3.0-Thread-Safe-Sessions.md)**

---

### 1.2.1 — Cosmetics & Documentation
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.2.1/**
- Documentation improvements and bug fixes
- Enhanced README with examples
- Iterative planning strategy refinements

### 1.2.0 — Initial PyPI Release
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/**
- First PyPI distribution
- Iterative planning strategy introduction
- Domain management utilities
