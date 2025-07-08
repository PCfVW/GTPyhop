# GTPyhop

GTPyhop is a task-planning system based on [Pyhop](https://bitbucket.org/dananau/pyhop/src/master/), but generalized to plan for both goals and tasks.

## The pip Branch

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) is forked from [Dana Nau's GTPyhop main branch](https://github.com/dananau/GTPyhop), refactored for PyPI distribution.

## Installation

```bash
pip install gtpyhop
```

## Usage

```python
# Import the main GTPyhop planning system
import gtpyhop

# Import the regression test module
from gtpyhop.examples import regression_tests

# Run the regression tests to verify the installation
regression_tests.main()
```

## New Features

### Iterative Planning Strategy

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) introduces a new iterative planning strategy that enhances the planner's capabilities for large planning scenarios; it is the default strategy.

Once gtpyhop is imported, the recursive strategy can be set calling:

```python
set_recursive_strategy(True)  # Planning strategy now is recursive
```

### New Functions

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
- seek_plan &rarr; `seek_plan_recursive`
- _apply_action_and_continue &rarr; `apply_action_and_continue_recursive`
- _refine_multigoal_and_continue &rarr; `refine_multigoal_and_continue_recursive`
- _refine_unigoal_and_continue &rarr; `refine_unigoal_and_continue_recursive`
- _refine_task_and_continue &rarr; `refine_task_and_continue_recursive`


## Version History

Current refactored version: 1.2.0b2 -- This version will soon be ready to be indexed on PyPI.
