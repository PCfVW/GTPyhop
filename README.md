# GTPyhop - pip installable version
## A Goal-Task-Network planning system written in Python

> **Original work by Dana S. Nau**  
> University of Maryland  
> July 22, 2021

### About this branch

This is the **pip branch** of the GTPyhop repository. **No modifications have been made to Dana Nau's original code** - this branch solely focuses on restructuring the repository directories to create a proper Python package that can be installed via pip and imported directly into Python, allowing users to:

- Install GTPyhop using `pip install gtpyhop`
- Import the library directly with `import gtpyhop` in Python scripts
- Access all original functionality through standard Python package conventions

To reflect this pip branch adaptation, Dana's GTPyhop version number has been updated from 1.1.0 to 1.1.1b1, where the "b1" designation represents an observation period to assess the stability of this pip branch.


### Installation

```bash
pip install gtpyhop
```

### Quick Start

```python
import gtpyhop

# All original GTPyhop functionality is available
# Follow the examples from the original documentation
```

---

## Original GTPyhop Documentation

GTPyhop is an automated planning system written in Python, that uses hierarchical planning techniques to construct plans of action for tasks and goals. The way GTPyhop plans for tasks is very similar to the [Pyhop](https://bitbucket.org/dananau/pyhop/) planner, and GTPyhop is mostly backward-compatible with Pyhop. The way GTPyhop plans for goals is inspired by the [GDP](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf) algorithm. However, GTPyhop may use both tasks and goals throughout its planning process.

### Features

- GTPyhop creates a *plan* (a sequence of actions) to accomplish a *to-do* list *T* consisting of actions, tasks, and goals. The objective is to construct a *solution plan*, i.e., a sequence of actions that accomplishes all of the items in *T*, in the order that they occur in *T*. To do this, GTPyhop does a backtracking search in a *planning domain* that includes definitions of what the actions do, *task methods* telling how to accomplish tasks, and *goal methods* telling how to achieve goals.

- Unlike the task lists used in Pyhop and the goal lists used in GDP, GTPyhop's to-do list may contain both tasks and goals. The same is true for the to-do lists returned by GTPyhop's task methods and goal methods. Thus GTPyhop may switch back and forth between tasks and goals throughout its planning process.

- GTPyhop is mostly backward-compatible with Pyhop. However, GTPyhop includes more documentation, more debugging features, and the ability to load multiple planning domains into memory and switch among them without having to restart Python each time.

For further information, see this [overview of GTPyhop](http://www.cs.umd.edu/~nau/papers/nau2021gtpyhop.pdf) and this [additional information](additional_information.md).

### Package Structure

The pip-installable version maintains all original functionality while organizing files according to Python packaging standards:

- Core GTPyhop functionality is accessible through the main package import
- All example domains and test problems are included and accessible
- Original test harness and debugging features are preserved
- Documentation and additional information files are maintained

### Examples and Testing

After installation, you can access all the original examples:

```python
# All original examples are available, for instance:
# - simple_htn: simple task-planning examples
# - simple_hgn: simple goal-planning examples  
# - backtracking_htn: demonstration of backtracking
# - logistics_hgn: goal-planning version of the "logistics" domain
# - blocks_gtn: goal-task-planning version of the blocks world
# - blocks_htn: task-planning version of the blocks world
# - blocks_hgn: goal-planning version of the blocks world
# - blocks_goal_splitting: separating goals and solving them sequentially
# - pyhop_simple_travel_example: backward-compatibility with Pyhop
# - simple_htn_acting_error: problem demonstration at acting time
```

The package also includes the Run-Lazy-Lookahead algorithm described in [*Automated Planning and Acting*](http://www.laas.fr/planning), with demonstrations of integrated planning and acting using Run-Lazy-Lookahead and GTPyhop.

### Credits and References

**All credit for the GTPyhop algorithm and implementation goes to Dana S. Nau and collaborators.** This pip branch simply provides packaging convenience without altering the core system.

#### Related Work

- The [overview of GTPyhop](http://www.cs.umd.edu/~nau/papers/nau2021gtpyhop.pdf) from the 2021 HPlan workshop
- A paper about a [re-entrant version of GTPyhop](http://www.cs.umd.edu/~nau/papers/bansod2021integrating.pdf) from the 2021 HPlan workshop
- Slides from a [presentation about Pyhop](http://www.cs.umd.edu/~nau/papers/nau2013game.pdf) at the 2013 ICAPS Workshop on Planning in Games
- A paper that classifies [various kinds of hierarchical planning](https://www.ijcai.org/Abstract/16/429). In their terminology, GTPyhop's search strategy is a totally-ordered version of Goal-Task-Network (GTN) planning, without sharing and task insertion

### License

This packaging maintains the same open-source license as the original GTPyhop implementation.

---

**Note**: For the most up-to-date documentation and research papers, please refer to the original GTPyhop repository and Dana Nau's academic publications.