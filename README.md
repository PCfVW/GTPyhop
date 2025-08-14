# GTPyhop version 1.2.1

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
        ├── 📄 main.py
        └── 📁 test_harness/
            ├── 📄 __init__.py
            └── 📄 test_harness.py
```

## Installation from PyPI is available since version 1.2.0

Open a terminal and type the following:

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
Imported GTPyhop version 1.2.1
Messages from find_plan will be prefixed with 'FP>'.
Messages from run_lazy_lookahead will be prefixed with 'RLL>'.
Using iterative seek_plan.
```

Now import the regression tests module:

```python
from gtpyhop.examples import regression_tests
```

Be prepared to see a lot of information on the screen about the examples and how to solve them, with different levels of verbosity; with this in mind, run the regression tests:

```python
regression_tests.main()
```

The last lines printed in your terminal should be:

```code
-----------------------------------------------------------------------
Created the domain 'gtpyhop.examples.simple_htn_acting_error'. To run the examples, type this:
gtpyhop.examples.simple_htn_acting_error.main()

Finished without error.
```

Happy Planning!

## Usage

You have successfully installed and tested gtpyhop; it's time to declare your own planning problems in gtpyhop.

### Very first HTN example

The key pattern is: create domain → define actions/methods → declare them → use gtpyhop.find_plan() to solve problems.

In the first three steps, we give simple illustrations on domain creation, action and task method definition, and how to declare them; in step 4 below, you'll find the code for a complete example.

**1. First, create a Domain to hold your definitions**

```python
import gtpyhop

# Create domain
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

# Create domain
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

### Additional Information

Please read [Dana's additional information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md) of how to implement:
- [States](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#states)
- [Actions](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#actions)
- [Tasks and task methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#3-tasks-and-task-methods)
- [Goals and goal methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#4-goals-and-goal-methods)
- ...and much more about GTPyhop!

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

The following functions have been added to Dana's original code:

- `print_domain_names`
- `find_domain_by_name`, `is_domain_created`
- `set_current_domain`, `get_current_domain`
- `set_recursive_planning`, `get_recursive_planning`, `reset_planning_strategy`
- `set_verbose_level`, `get_verbose_level`
- `seek_plan_iterative`,
  - `refine_multigoal_and_continue_iterative`
  - `refine_unigoal_and_continue_iterative`
  - `refine_task_and_continue_iterative`
  - `apply_action_and_continue_iterative`

### Renaming

`_recursive` has been added at the end of the identifiers of the original functions involved in seeking for a plan: 

- seek_plan &rarr; `seek_plan_recursive`
- _apply_action_and_continue &rarr; `apply_action_and_continue_recursive`
- _refine_multigoal_and_continue &rarr; `refine_multigoal_and_continue_recursive`
- _refine_unigoal_and_continue &rarr; `refine_unigoal_and_continue_recursive`
- _refine_task_and_continue &rarr; `refine_task_and_continue_recursive`


## Version History

> **1.2.1** -- **Cosmetics** Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.2.1/
> 
> - Fix: set_recursive_strategy() replaced by set_recursive_planning() in README.md
> - Added Python and License badges to this README.md
> - Added summary of trivial differences between recursive and iterative planning strategies
> - Added very first HTN example
> - Added "open a terminal and" in the first paragraph of Testing your installation
> - Removed (soon available) after Installation from PyPI
> - Added how to get back to iterative planning strategy
> - Removed unnecessary imports in `main.py`
> - Fix: various typos and inconsistencies in README.md

> **1.2.0** -- Uploaded to PyPI: https://pypi.org/project/gtpyhop/

> 1.2.0rc1 -- Uploaded to Test PyPI: https://test.pypi.org/project/gtpyhop/1.2.0rc1/

> 1.2.0b2 -- This tested refactored version will soon be ready to be indexed on TestPyPI as 1.2.0rc1
