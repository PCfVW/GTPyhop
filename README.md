# GTPyhop

GTPyhop is a task-planning system based on Pyhop, but generalized to plan for both goals and tasks.

## pip Branch

This `pip` branch refactors Dana Nau's GTPyhop code to be able to pip install GTPyhop from the PyPI index.

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

This branch also introduces a new iterative planning strategy that enhances the planner's capabilities for complex planning scenarios. Iterative is the default strategy. When gtpyhop is imported, the recursive strategy can be set calling `set_recursive_strategy(True)`.

```python
set_recursive_strategy(True)
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

## Original GTPyhop

This is based on Dana Nau's original GTPyhop implementation, refactored for PyPI distribution. See [Dana Nau's GitHub repository](https://github.com/dananau/GTPyhop).

## Version History

Current refactored version: 1.2.0
