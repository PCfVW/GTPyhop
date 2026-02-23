# GTPyhop version 1.9.2

[![Python Version](https://img.shields.io/badge/python-3%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Clear%20BSD-green.svg)](https://github.com/PCfVW/GTPyhop/blob/pip/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/gtpyhop)](https://pypi.org/project/gtpyhop/)

GTPyhop is an HTN planning system based on [Pyhop](https://bitbucket.org/dananau/pyhop/src/master/), but generalized to plan for both goals and tasks.

[Dana Nau](https://www.cs.umd.edu/~nau/) is the original author of GTPyhop.

---

## Table of Contents

1. [Installation](#installation)
2. [Testing Your Installation](#testing-your-installation)
3. [Quick Start Tutorial](#lets-htn-start)
4. [Thread-Safe Sessions](#thread-safe-sessions-130)
5. [Examples](#examples)
6. [Documentation](#-documentation)
7. [New Features](#new-features)
8. [Project Structure](#project-structure)

---

## The pip Branch

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) is forked from [Dana Nau's GTPyhop main branch](https://github.com/dananau/GTPyhop) and refactored for PyPI distribution, thread-safe sessions, new domain and problems file structure to facilitate LibCST parsing, new example structure to facilitate benchmarking, and documentation.

## Installation

### From PyPI (Recommended)

**GTPyhop 1.9.2** is the latest version with iterative DFS backtracking, poetry generation examples, memory tracking, enhanced MCP orchestration examples, Opentrons Flex domains, and comprehensive style guides.

```bash
pip install gtpyhop>=1.9.2
```

For basic single-threaded planning, any version works:
```bash
pip install gtpyhop
```

[uv](https://docs.astral.sh/uv/) can of course be used if you prefer:

```bash
uv pip install gtpyhop
```

### From GitHub

Alternatively, you can directly install from GitHub:

```bash
git clone -b pip https://github.com/PCfVW/GTPyhop.git
cd GTPyhop
pip install .
```

## Testing Your Installation

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
Imported GTPyhop version 1.9.2
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

## Let's HTN Start!

You have successfully installed and tested gtpyhop; it's time to declare your own planning problems in gtpyhop.

### Very First HTN Example

The key pattern is: **create a Domain** -> **define actions/methods** -> **declare them** -> **define initial state** -> **use gtpyhop.find_plan() to solve problems**.

**1. Create a Domain**

```python
import gtpyhop

# Create a Domain
gtpyhop.Domain('my_domain')
```

**2. Define Actions**

Actions are atomic operations that directly modify a state. They are Python functions where the first argument is the current `state`, and the others are the action's arguments.

```python
def my_action(state, arg1, arg2):
    # Check preconditions
    if state.pos[arg1] == arg2:
        # Modify state
        state.pos[arg1] = 'new_location'
        state.status[arg2] = 'updated'
        return state  # Success
    return False  # Failure

# Declare actions
gtpyhop.declare_actions(my_action, another_action)
```

**3. Define Task Methods**

Task methods decompose compound tasks into subtasks and actions.

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

```python
initial_state = gtpyhop.State('initial_state')
initial_state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}
```

**5. Complete Example**

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

Put this code in a file, say `my_very_first_htn_example.py`, and run it:

```bash
python my_very_first_htn_example.py
```

Increase the verbosity level to 2 or 3 to see more information about the planning process.

### Session-Based Version (Recommended for 1.3.0+)

For better isolation and thread safety:

```python
import gtpyhop

# Domain creation
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

# Use session-based planning
with gtpyhop.PlannerSession(domain=my_domain, verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, [('transport', 'obj1', 'loc2')])
        if result.success:
            print("Plan found:", result.plan)
            print("Planning stats:", result.stats)
```

### Additional Resources

Please read [Dana's additional information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md) for detailed explanations of:
- [States](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#states)
- [Actions](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#actions)
- [Tasks and task methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#3-tasks-and-task-methods)
- [Goals and goal methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#4-goals-and-goal-methods)

## Thread-Safe Sessions (1.3.0+)

**GTPyhop 1.3.0 introduces session-based, thread-safe planning** that enables reliable concurrent execution and isolated planning contexts. This is a major architectural enhancement while maintaining 100% backward compatibility.

### Key Benefits
- **Thread-safe concurrent planning**: Multiple planners can run simultaneously
- **Isolated execution contexts**: Each session has its own configuration, logs, and statistics
- **Structured logging system**: Programmatic access to planning traces
- **Timeout management**: Built-in timeout enforcement and resource management
- **Session persistence**: Save and restore planning sessions

### Quick Start with Sessions
```python
import gtpyhop

my_domain = gtpyhop.Domain('my_domain')
# ... define actions and methods ...

with gtpyhop.PlannerSession(domain=my_domain, verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, [('transport', 'obj1', 'loc2')])
        if result.success:
            print(result.plan)
```

**For detailed documentation, see [Thread-Safe Sessions Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md)**

### Migration from Pre-1.3.0

**Existing code continues to work unchanged** - 100% backward compatible.

```python
# Before (still works)
plan = gtpyhop.find_plan(state, tasks)

# After (recommended)
with gtpyhop.PlannerSession(domain=my_domain) as session:
    with session.isolated_execution():
        result = session.find_plan(state, tasks)
        plan = result.plan if result.success else None
```

### Version Selection Guide

| Use Case | Recommended Version |
|----------|-------------------|
| **New projects** | **1.9.0+** |
| **Backtracking with iterative planner** | **1.9.0+** |
| **Memory tracking & benchmarking** | **1.8.0+** |
| **MCP integration** | **1.5.0+** |
| **Concurrent/parallel planning** | **1.3.0+** |
| **Educational/simple scripts** | Any version |

## Examples

GTPyhop includes comprehensive examples demonstrating various planning techniques. **All examples support both legacy and session modes.**

### Quick Example Run

```bash
# Legacy mode (backward compatible)
python -m gtpyhop.examples.simple_htn

# Session mode (thread-safe, recommended)
python -m gtpyhop.examples.simple_htn --session
```

**For comprehensive example documentation, see [All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)**

## Documentation

GTPyhop 1.9.2 includes comprehensive documentation organized in the `docs/` folder:

### Core Documentation
- **[All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)** - Pedagogical details about all HTN planning examples
- **[Running Examples](https://github.com/PCfVW/GTPyhop/blob/pip/docs/running_examples.md)** - Detailed instructions for executing examples
- **[Structured Logging](https://github.com/PCfVW/GTPyhop/blob/pip/docs/logging.md)** - Comprehensive logging system documentation
- **[Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md)** - Complete guide to session-based architecture
- **[Version History](https://github.com/PCfVW/GTPyhop/blob/pip/docs/changelog.md)** - Complete changelog

### Style Guides
- **[Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md)** - How to write GTPyhop examples (folder structure, required files)
- **[Domain Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_domain_style_guide.md)** - Conventions for writing domain files (actions and methods)
- **[Problems Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md)** - Conventions for writing problem files

### Example-Specific Documentation

#### Memory Tracking Examples (1.8.0+)
- **[Memory Tracking Overview](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/README.md)** - Memory tracking capabilities with psutil
- **[Scalable Data Processing](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_data_processing/README.md)** - Memory scaling via data size (10K-1M items)
- **[Scalable Recursive Decomposition](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md)** - Memory scaling via recursion depth (2^k tasks)
- **[Memory Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/benchmarking_quickstart.md)** - How to run memory benchmarks

#### Poetry Examples (1.9.0+)
- **[Poetry Overview](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/README.md)** - HTN-planned poetry generation with MCP delegation
- **[Structured Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/structured_poetry/README.md)** - Baseline: couplet, limerick, haiku, sonnet (6 scenarios)
- **[Backtracking Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/backtracking_poetry/README.md)** - Strict/relaxed rhyme methods with backtracking (3 scenarios)
- **[Candidate Planning Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/candidate_planning_poetry/README.md)** - Multi-candidate rhyme selection pipeline (3 scenarios)
- **[Bidirectional Planning Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/bidirectional_planning_poetry/README.md)** - Decomposed backward line construction (3 scenarios)
- **[Replanning Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/replanning_poetry/README.md)** - Post-generation evaluation and steering/revision (3 scenarios)
- **[Formal Mechanism Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/formal_mechanism_poetry/README.md)** - Three planning mechanisms from Anthropic's "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" paper (3 scenarios)
- **[Feature Space Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/feature_space_poetry/README.md)** - Feature-space interventions with measured data: Gemma 2 2B 426K (Version D) + Llama 3.2 1B 524K (Version L) + Gemma 2 2B 2.5M (Version D 2.5M) (12 scenarios)

#### IPC 2020 Total Order Domains
- **[Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/benchmarking_quickstart.md)** - Performance benchmarking guide
- **[Blocksworld-GTOHP](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/Blocksworld-GTOHP/ipc-2020-to-bw-gtohp-readme.md)** - IPC 2020 Blocksworld domain
- **[Childsnack](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/Childsnack/ipc-2020-to-cs-gtohp-readme.md)** - IPC 2020 Childsnack domain

#### MCP Orchestration Examples (1.5.0+)
- **[MCP Benchmarking](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/benchmarking_quickstart.md)** - MCP orchestration benchmarking guide
- **[Bio-Opentrons PCR Workflow](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/bio_opentrons/README.md)** - PCR workflow automation (6 scenarios)
- **[Cross-Server Orchestration](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/cross_server/README.md)** - Multi-server coordination (2 scenarios)
- **[Drug Target Discovery](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/drug_target_discovery/README.md)** - OpenTargets platform integration (3 scenarios)
- **[Omega HDQ DNA Extraction](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/omega_hdq_dna_bacteria_flex_96_channel/README.md)** - DNA extraction workflow (3 scenarios)
- **[TNF Cancer Modelling](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/tnf_cancer_modelling/README.md)** - Multiscale cancer modeling (1 scenario)

### External Resources
- **[Dana's Additional Information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md)** - Core GTPyhop concepts

## New Features

### Planning Strategies

GTPyhop supports three planning strategies, selectable via `set_recursive_planning` or the `PlannerSession(strategy=...)` parameter:

| Strategy | Backtracking? | Stack | Activation |
|----------|:------------:|-------|------------|
| **Iterative greedy** (default) | No | Explicit stack | `set_recursive_planning(False)` |
| **Recursive DFS** | Yes | Python call stack | `set_recursive_planning(True)` |
| **Iterative DFS BT** (1.9.0+) | Yes | Explicit stack | `set_recursive_planning("iterative_dfs_backtracking")` |

The **iterative greedy** strategy (default since 1.2.0) commits to the first applicable method and never reconsiders that choice. The **recursive DFS** strategy backtracks across methods via the Python call stack. The **iterative DFS backtracking** strategy (new in 1.9.0) combines the iterative planner's explicit stack with the recursive planner's ability to backtrack — it pushes all applicable method continuations onto the stack, so if one path fails, alternatives remain.

```python
# Global API
gtpyhop.set_recursive_planning(False)                        # iterative greedy (default)
gtpyhop.set_recursive_planning(True)                         # recursive DFS
gtpyhop.set_recursive_planning("iterative_dfs_backtracking") # iterative DFS with backtracking

# Session API (1.9.0+)
with gtpyhop.PlannerSession(domain=d, strategy="iterative_dfs_backtracking") as s:
    result = s.find_plan(state, tasks)
```

All existing `True`/`False` callers continue to work identically. See the [changelog](https://github.com/PCfVW/GTPyhop/blob/pip/docs/changelog.md) for full details.

### New Functions by Version

**1.9.0 (Iterative DFS Backtracking)**
- `seek_plan_iterative_backtracking` - Iterative DFS with full backtracking via explicit stack
- `_refine_task_and_continue_iterative_bt` - Multi-continuation task refinement
- `_refine_unigoal_and_continue_iterative_bt` - Multi-continuation unigoal refinement
- `_refine_multigoal_and_continue_iterative_bt` - Multi-continuation multigoal refinement
- `PlannerSession(strategy=...)` - Strategy selection parameter (`"recursive_dfs"`, `"iterative_greedy"`, `"iterative_dfs_backtracking"`)

**1.4.0 (Robustness & Benchmarking)**
- `validate_plan_from_goal` - Plan validation from initial to goal state
- `PlannerBenchmark` - Comprehensive benchmarking with resource tracking

**1.3.0 (Thread-Safe Sessions)**
- `PlannerSession` - Isolated, thread-safe planning context
- `create_session`, `get_session`, `destroy_session`, `list_sessions`
- `SessionSerializer`, `restore_session` - Session persistence

**1.2.1 (Iterative Planning)**
- `set_recursive_planning`, `get_recursive_planning`
- `seek_plan_iterative` and related iterative functions

## Project Structure

```
GTPyhop/
├── LICENSE.txt
├── pyproject.toml
├── README.md
├── docs/
│   ├── all_examples.md
│   ├── changelog.md
│   ├── gtpyhop_domain_style_guide.md
│   ├── gtpyhop_example_style_guide.md
│   ├── gtpyhop_problems_style_guide.md
│   ├── logging.md
│   ├── running_examples.md
│   └── thread_safe_sessions.md
└── src/gtpyhop/
    ├── __init__.py
    ├── main.py
    ├── logging_system.py
    ├── memory_tracking/
    │   ├── __init__.py
    │   ├── monitor.py
    │   └── tracker.py
    ├── examples/
    │   ├── __init__.py
    │   ├── regression_tests.py
    │   ├── simple_htn.py, simple_hgn.py, ...
    │   ├── blocks_htn/, blocks_hgn/, blocks_gtn/, blocks_goal_splitting/
    │   ├── ipc-2020-total-order/
    │   │   └── Blocksworld-GTOHP/, Childsnack/
    │   ├── mcp-orchestration/
    │   │   └── bio_opentrons/, cross_server/, drug_target_discovery/, omega_hdq_dna_bacteria_flex_96_channel/, tnf_cancer_modelling/
    │   ├── memory_tracking/
    │   │   └── scalable_data_processing/, scalable_recursive_decomposition/
    │   └── poetry/
    │       └── structured_poetry/, backtracking_poetry/, candidate_planning_poetry/, bidirectional_planning_poetry/, replanning_poetry/, formal_mechanism_poetry/, feature_space_poetry/
    └── test_harness/
```
