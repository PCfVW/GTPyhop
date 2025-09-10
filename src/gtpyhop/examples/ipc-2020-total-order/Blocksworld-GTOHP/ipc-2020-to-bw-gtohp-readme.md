# Blocksworld-GTOHP Domain

## Overview

The Blocksworld-GTOHP domain is a classic planning domain that involves manipulating blocks in a world where blocks can be stacked on top of each other or placed on a table. This implementation is part of the IPC 2020 Total Order track and provides a comprehensive set of problems ranging from simple to complex configurations.

## Domain Description

In the Blocksworld domain, an agent must rearrange blocks to achieve a desired configuration. The domain involves:

- **Blocks**: Individual objects that can be moved and stacked
- **Table**: A surface where blocks can be placed
- **Stacking**: Blocks can be placed on top of other blocks
- **Clear**: Only blocks with no other blocks on top can be moved

### Actions Available

The domain provides 4 primitive actions for manipulating blocks:

- **pickup**: Pick up a clear block from the table
- **putdown**: Place a held block on the table  
- **stack**: Place a held block on top of another clear block
- **unstack**: Remove the top block from a stack

### Methods Available

The domain includes 7 methods for achieving goals:

- **m0_do_put_on**: Do nothing if one block is already on another block
- **m1_do_put_on**: Put block one block on top of another block
- **m2_do_on_table**: Put one block from top of tower (another block) onto the table
- **m3_do_on_table**: Do nothing if one block is already clear
- **m4_do_move**: Move one block from table to top of tower (another block)
- **m5_do_move**: Move one block from top of one block to another
- **m6_do_clear**: Clear one block
- **m7_do_clear**: Clear one block by clearing the block on its top

### Goal Representation

Goals in this domain specify desired block arrangements using "on" relationships:
```python
goal = {"block1": "block2", "block3": "table", "block4": "block1"}
```
This represents: block1 on block2, block3 on table, block4 on block1.

## Problem Set

This domain contains **20 problem instances** with increasing complexity:

| Problem Range | Block Count | Complexity Level |
|---------------|-------------|------------------|
| BW_rand_5 to BW_rand_11 | 5-11 blocks | Simple |
| BW_rand_13 to BW_rand_25 | 13-25 blocks | Medium |
| BW_rand_27 to BW_rand_43 | 27-43 blocks | Complex |

### Problem Naming Convention

Problems are named `BW_rand_X` where X indicates the number of blocks:
- `BW_rand_5`: 5 blocks
- `BW_rand_7`: 7 blocks
- ...
- `BW_rand_43`: 43 blocks

## Encoding Details

### State Representation

States are encoded using several predicates:
- `on(block, target)`: Block is on target (another block or table)
- `clear(block)`: Block has nothing on top of it
- `holding(block)`: Agent is currently holding the block
- `handempty()`: Agent's hand is empty

### Problem Structure

Each problem consists of:
1. **Initial State**: Starting configuration of blocks
2. **Goal State**: Desired final configuration
3. **Multigoal Method**: Method for achieving "on" relationships between blocks

### Planning Approach

The domain uses:
- **Hierarchical Task Networks (HTN)**: For structured problem decomposition
- **Goal Methods**: For achieving "on" relationships between blocks
- **Action Methods**: For primitive block manipulation actions

## Performance Characteristics

Based on benchmark results:

- **Success Rate**: 95% (19/20 problems solved)
- **Execution Time**: 0.001s to 0.066s per problem
- **Plan Length**: 18 to 1,089 actions
- **Memory Usage**: ~26-27MB peak memory

### Difficulty Analysis

- **Easiest Problems**: BW_rand_5 to BW_rand_15 (consistently fast)
- **Medium Problems**: BW_rand_17 to BW_rand_35 (moderate complexity)
- **Hardest Problem**: BW_rand_43 (currently unsolved by the planner)

## Usage Examples

### Running Benchmarks

```bash
# Run all Blocksworld problems
python benchmarking.py Blocksworld-GTOHP

# Run with verbose output
python benchmarking.py Blocksworld-GTOHP --verbose 2

# Sort by memory usage
python benchmarking.py Blocksworld-GTOHP --sort-by memory
```

### Accessing Problems Programmatically

```python
import importlib
bw = importlib.import_module('Blocksworld-GTOHP')

# Get all problems
problems = bw.get_problems()
print(f"Found {len(problems)} problems")

# Access specific problem
state, goal = problems['BW_rand_5']
print(f"Goal: {goal}")
```

## File Structure

- `domain.py`: Domain definition with actions and methods
- `problems.py`: All 20 problem instances
- `__init__.py`: Package initialization and problem discovery
- `ipc-2020-to-bw-gtohp-readme.md`: This documentation file

## Implementation Notes

### Key Features

1. **Smart Import Strategy**: Supports both PyPI and local GTPyhop installations
2. **Multigoal Support**: Uses GTPyhop's built-in multigoal splitting
3. **Action and method template**: Systematic approach for defining actions and methods

### Technical Details

- **Domain Type**: HTN (Hierarchical Task Network)
- **Goal Type**: 1 Multigoal with "on" relationships
- **Action Count**: 4 primitive actions (pickup, putdown, stack, unstack)
- **Method Count**: 8 task and 1 goal methods for problem decomposition

### References

- [**IPC 2020 Total Order**](https://github.com/panda-planner-dev/ipc2020-domains/tree/master/total-order)
- **Original Domain Authors**
    - Humbert Fiorino humbert.fiorino@univ-grenoble-alpes.fr
    - Abdeldjalil Ramoul abdeldjalil.ramoul@univ-grenoble-alpes.fr
    - Damien Pellier damien.pellier@univ-grenoble-alpes.fr
- [**Paper**](https://ojs.aaai.org/index.php/ICAPS/article/view/3502)
    - Dominik Schreiber, Damien Pellier, Humbert Fiorino, & Tom&aacute;&#353; Balyo, _Tree-REX: SAT-Based Tree Exploration for Efficient and High-Quality HTN Planning_, Proceedings of the 29th International Conference on Automated Planning and Scheduling (2020) pp. 382-390.

## See Also

- `../benchmarking_quickstart_latest.md`: Quick start guide for running benchmarks
- `../Childsnack/ipc-2020-to-cs-gtohp-readme.md`: Documentation for the IPC 2020 Total Order Childsnack domain
- `problems.py`: Detailed problem definitions and initial states
- `domain.py`: Complete domain implementation with all actions and methods
