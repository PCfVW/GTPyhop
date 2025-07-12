# GTPyhop

GTPyhop is a task-planning system based on [Pyhop](https://bitbucket.org/dananau/pyhop/src/master/), but generalized to plan for both goals and tasks.

[Dana Nau](https://www.cs.umd.edu/~nau/) is the original developper of GTPyhop.

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
            ├── 📁backtracking_htn.py
            ├── 📁blocks_goal_splitting/
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

## Installation from PyPI (soon available)

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

We suggest you give gtpyhop a try straight away; start an interactive python session:
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
Imported GTPyhop version 1.2.0
Messages from find_plan will be prefaced with 'FP>'.
Messages from run_lazy_lookahead will be prefaced with 'RLL>'.
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

Please read [Dana's additional information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md) of how to implement:
- [States](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#states)
- [Actions](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#actions)
- [Tasks and task methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#3-tasks-and-task-methods)
- [Goals and goal methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#4-goals-and-goal-methods)
- ...and much more about GTPyhop!

## New Features

### Iterative Planning Strategy

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) introduces a new iterative planning strategy that enhances the planner's capabilities for large planning scenarios; it is the default strategy.

Once gtpyhop is imported, Dana Nau's original recursive strategy can be set calling:

```python
set_recursive_strategy(True)  # Planning strategy now is recursive
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

> **1.2.0** -- Uploaded to PyPI: https://pypi.org/project/gtpyhop/

> 1.2.0rc1 -- Uploaded to Test PyPI: https://test.pypi.org/project/gtpyhop/1.2.0rc1/

> 1.2.0b2 -- This tested refactored version will soon be ready to be indexed on TestPyPI as 1.2.0rc1
