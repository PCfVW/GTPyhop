# Childsnack Domain

## Overview

The Childsnack domain is a planning domain that models the task of preparing and serving sandwiches to children in a childcare setting. This domain is part of the IPC 2020 Total Order track and presents interesting challenges involving resource management, dietary restrictions, and efficient service logistics.

## Domain Description

In the Childsnack domain, an agent must prepare sandwiches according to children's dietary needs and serve them at appropriate tables. The domain involves:

- **Children**: Individuals with specific dietary requirements (gluten-free or regular)
- **Sandwiches**: Food items made from bread and contents
- **Ingredients**: Bread and contents with different properties (gluten-free or regular)
- **Tables**: Locations where children sit and are served
- **Trays**: Containers for transporting sandwiches from kitchen to tables

### Key Constraints

- **Dietary Restrictions**: Some children require gluten-free sandwiches
- **Ingredient Compatibility**: Gluten-free sandwiches need gluten-free bread
- **Service Logistics**: Sandwiches must be transported on trays to correct tables
- **Resource Management**: Limited trays and ingredients must be used efficiently

### Actions Available

The domain provides 6 primitive actions for sandwich preparation and service:

- **make_sandwich**: Create a regular sandwich from bread and contents
- **make_sandwich_no_gluten**: Create a gluten-free sandwich
- **put_on_tray**: Place a sandwich on a tray
- **move_tray**: Transport a tray between kitchen and tables
- **serve_sandwich**: Serve a regular sandwich to a child
- **serve_sandwich_no_gluten**: Serve a gluten-free sandwich to a child

### Methods Available

The domain includes 2 methods for achieving goals:
- **m0_serve**: Use a tray to serve a single child at the table with a gluten-free sandwich, ensuring both the bread and filling are gluten-free.
- **m1_serve**: Use a tray to serve a single child at the table with a sandwich made from regular bread and filling (containing gluten).

### Goal Representation

Goals specify which children should be served (satisfied):
```python
goal = {"child1": "table2", "child2": "table1", "child3": "table3"}
```
This represents: child1 served at table2, child2 at table1, child3 at table3.

## Problem Set

This domain contains **30 problem instances** with increasing complexity:

| Problem Range | Children Count | Complexity Level |
|---------------|----------------|------------------|
| childsnack_p01 to p10 | 10-15 children | Simple |
| childsnack_p11 to p20 | 16-20 children | Medium |
| childsnack_p21 to p30 | 50-500 children | Complex |

### Problem Naming Convention

Problems are named `childsnack_pXX` where XX is the problem number:
- `childsnack_p01`: 10 children
- ...
- `childsnack_p10`: 15 children
- ...
- `childsnack_p20`: 20 children
- ...
- `childsnack_p30`: 500 children (largest instance)

## Encoding Details

### State Representation

States are encoded using several predicates:
- `waiting(child, table)`: Child is waiting to be served at a table
- `served(child)`: Child has been served and is satisfied
- `at_kitchen_bread(bread)`: Bread is available in the kitchen
- `at_kitchen_content(content)`: Sandwich content is available in the kitchen
- `no_gluten_bread(bread)`: Bread is gluten-free
- `no_gluten_content(content)`: Content is gluten-free
- `allergic_gluten(child)`: Child requires gluten-free food
- `tray_at(tray, location)`: Tray is at a specific location
- `sandwich_at(sandwich, location)`: Sandwich is at a specific location

### Problem Structure

Each problem consists of:
1. **Initial State**: Children waiting, available ingredients, tray locations
2. **Goal State**: All children served (satisfied)
3. **Multigoal method**: Method for achieving "served" relationships

### Planning Approach

The domain uses:
- **Hierarchical Task Networks (HTN)**: For structured meal preparation
- **Goal Methods**: For achieving "served" relationships
- **Resource Management**: Direct management of trays and ingredients (cf. Helpers)

## Performance Characteristics

Based on benchmark results:

- **Success Rate**: 100% (30/30 problems solved)
- **Execution Time**: 0.006s to 3.496s per problem
- **Plan Length**: 50 to 2,500 actions
- **Memory Usage**: ~26-39MB peak memory

### Difficulty Analysis

- **Simple Problems**: p01-p10 (10-15 children, <0.02s)
- **Medium Problems**: p11-p20 (16-20 children, 0.02-0.05s)
- **Complex Problems**: p21-p30 (50-500 children, 0.1-3.5s)

### Scaling Characteristics

The domain shows excellent scalability:
- **Linear Time Growth**: Execution time scales roughly linearly with problem size
- **Efficient Memory Usage**: Memory usage remains reasonable even for large instances
- **Robust Planning**: 100% success rate across all problem sizes

## Usage Examples

### Running Benchmarks

```bash
# Run all Childsnack problems
python benchmarking.py Childsnack

# Run with verbose output
python benchmarking.py Childsnack --verbose 1

# Sort by execution time
python benchmarking.py Childsnack --sort-by time
```

### Accessing Problems Programmatically

```python
import importlib
cs = importlib.import_module('Childsnack')

# Get all problems
problems = cs.get_problems()
print(f"Found {len(problems)} problems")

# Access specific problem
state, goal = problems['childsnack_p01']
print(f"Goal: {goal}")
```

## File Structure

- `domain.py`: Domain definition with actions and methods
- `problems.py`: All 30 problem instances
- `__init__.py`: Package initialization and problem discovery
- `ipc-2020-to-cs-gtohp-readme.md`: This documentation file

## Implementation Notes

### Key Features

1. **Smart Import Strategy**: Supports both PyPI and local GTPyhop installations
2. **Multigoal Support**: Uses GTPyhop's built-in multigoal splitting
3. **Action and method template**: Systematic approach for defining actions and methods
4. **Comprehensive Problem Set**: 30 problem instances

### Technical Details

- **Domain Type**: HTN (Hierarchical Task Network)
- **Goal Type**: Multigoal with "served" relationships
- **Action Count**: 6 primitive actions for sandwich preparation and service
- **Method Count**: 2 task and 1 goal methods for meal planning

### References

- [**IPC 2020 Total Order**](https://github.com/panda-planner-dev/ipc2020-domains/tree/master/total-order)
- **Original Domain Authors**
    - Abdeldjalil Ramoul abdeldjalil.ramoul@cloud-temple.com
    - Damien Pellier damien.pellier@univ-grenoble-alpes.fr
    - Humbert Fiorino humbert.fiorino@univ-grenoble-alpes.fr
    - Sylvie Pesty sylvie.pesty@univ-grenoble-alpes.fr
- [**Paper**](https://doi.org/10.1142/S0218213017600211): Abdeldjalil Ramoul, Damien Pellier, Humbert Fiorino, and Sylvie Pesty, _Grounding of HTN Planning Domain_, International Journal on Artificial Intelligence Tools, 26(5) (2017).

## See Also

- `../benchmarking_quickstart_latest.md`: Quick start guide for running benchmarks
- `../Blocksworld-GTOHP/ipc-2020-to-bw-gtohp-readme.md`: Documentation for the IPC 2020 Total Order Blocksworld-GTOHP domain
- `problems.py`: Detailed problem definitions and initial states
- `domain.py`: Complete domain implementation with all actions and methods
