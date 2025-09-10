# GTPyhop 1.4.0 HTN Planning Examples

This document provides pedagogical details about all HTN Planning examples included with GTPyhop 1.4.0. Each example demonstrates different aspects of hierarchical task network planning, from basic concepts to advanced techniques.

## 🎓 Learning Path

**Recommended order for learning:**
1. **simple_htn.py** - Start here for basic HTN concepts
2. **simple_hgn.py** - Learn goal-oriented planning
3. **backtracking_htn.py** - Understand method failure and backtracking
4. **simple_htn_acting_error.py** - Error handling and replanning
5. **logistics_hgn.py** - Multi-goal planning scenarios
6. **pyhop_simple_travel_example.py** - Classic Pyhop compatibility
7. **blocks_htn/** - Advanced HTN methods
8. **blocks_hgn/** - Advanced goal decomposition
9. **blocks_gtn/** - Mixed task/goal planning
10. **blocks_goal_splitting/** - Built-in goal splitting methods

## 📚 Simple Examples (Basic Concepts)

### simple_htn.py - Basic Hierarchical Task Networks
**Purpose:** Introduction to HTN planning fundamentals
**Domain:** Travel planning (home to park via taxi/walking)
**Key Learning Points:**
- Domain creation and state representation
- Action definitions with preconditions and effects
- Task method decomposition
- Hierarchical planning from high-level tasks to primitive actions
- Verbosity levels and debugging output

**Core Concepts Demonstrated:**
- **Actions:** `walk`, `call_taxi`, `ride_taxi`, `pay_driver`
- **Tasks:** `travel`, `travel_by_foot`, `travel_by_taxi`
- **State Variables:** locations, cash, debts
- **Planning Strategy:** Decompose travel task into appropriate subtasks

**Educational Value:** Perfect starting point for understanding how HTN planning breaks down complex tasks into manageable subtasks.

### simple_hgn.py - Basic Hierarchical Goal Networks
**Purpose:** Introduction to goal-oriented planning
**Domain:** Same travel domain as simple_htn but using goals
**Key Learning Points:**
- Goal vs. task distinction
- Goal method definitions
- State-based goal achievement
- Goal decomposition strategies

**Core Concepts Demonstrated:**
- **Goals:** `loc` (location goals)
- **Goal Methods:** Methods that achieve specific state conditions
- **Comparison:** Shows how the same domain can be modeled with goals vs. tasks

**Educational Value:** Demonstrates the difference between task-oriented and goal-oriented planning approaches.

### backtracking_htn.py - Backtracking Demonstration
**Purpose:** Understanding method failure and alternative exploration
**Domain:** Simple abstract domain with multiple method choices
**Key Learning Points:**
- Method failure handling
- Backtracking through alternative methods
- Search space exploration
- Planning strategy comparison (recursive vs. iterative)

**Core Concepts Demonstrated:**
- **Multiple Methods:** Several methods for the same task
- **Failure Conditions:** Methods that can fail under certain conditions
- **Backtracking:** How the planner explores alternatives

**Educational Value:** Critical for understanding how HTN planners handle uncertainty and multiple solution paths.

### simple_htn_acting_error.py - Error Handling Patterns
**Purpose:** Execution failures and replanning strategies
**Domain:** Travel domain with potential execution failures
**Key Learning Points:**
- Action execution failures
- Replanning after failures
- Robust planning strategies
- Error recovery mechanisms

**Educational Value:** Shows how real-world planning systems must handle execution uncertainties.

### logistics_hgn.py - Multi-Goal Planning
**Purpose:** Complex logistics domain with multiple objectives
**Domain:** Package delivery with trucks and airplanes
**Key Learning Points:**
- Multi-goal planning scenarios
- Resource management (trucks, planes, packages)
- Spatial reasoning (cities, airports)
- Goal interaction and dependencies

**Core Concepts Demonstrated:**
- **Actions:** `drive_truck`, `fly_airplane`, `load_truck`, `load_airplane`, `unload_truck`, `unload_airplane`
- **Goals:** Package location goals
- **Resources:** Trucks, airplanes, packages, locations

**Educational Value:** Demonstrates how HTN planning scales to realistic logistics problems.

### pyhop_simple_travel_example.py - Classic Pyhop Compatibility
**Purpose:** Compatibility with original Pyhop examples
**Domain:** Simple travel domain from original Pyhop
**Key Learning Points:**
- Migration from Pyhop to GTPyhop
- Backward compatibility
- Classic HTN planning patterns

**Educational Value:** Helps users familiar with Pyhop understand GTPyhop's enhanced capabilities.

## 🏗️ Complex Block World Examples (Advanced Scenarios)

### blocks_htn/ - Advanced Hierarchical Task Networks
**Purpose:** Complex HTN methods for blocks world manipulation
**Domain:** Classic blocks world with stacking operations
**Key Learning Points:**
- Complex task decomposition strategies
- Block manipulation primitives
- Stack management
- Advanced HTN method design

**Core Concepts Demonstrated:**
- **Actions:** `pickup`, `putdown`, `stack`, `unstack`
- **Tasks:** `move_blocks`, `get_block`, `put_block`
- **Complex Methods:** Multi-step block manipulation strategies
- **State Management:** Block positions, clear blocks, table space

**Educational Value:** Shows how HTN planning handles complex manipulation domains with intricate preconditions.

### blocks_hgn/ - Advanced Hierarchical Goal Networks
**Purpose:** Goal-oriented approach to blocks world planning
**Domain:** Blocks world using goal decomposition
**Key Learning Points:**
- Goal decomposition in complex domains
- Multi-goal achievement strategies
- Goal interaction management
- State-based planning

**Core Concepts Demonstrated:**
- **Goals:** Block position goals, stacking goals
- **Goal Methods:** Methods to achieve specific block configurations
- **Goal Dependencies:** How achieving one goal affects others

**Educational Value:** Demonstrates sophisticated goal-oriented planning in a well-understood domain.

### blocks_gtn/ - Goal Task Networks (Mixed Planning)
**Purpose:** Near-optimal blocks world planning algorithm
**Domain:** Blocks world with mixed task/goal approach
**Key Learning Points:**
- Hybrid task/goal planning
- Optimal planning strategies
- Algorithm implementation from research literature
- Performance optimization

**Reference:** Based on Gupta & Nau (1992) "On the complexity of blocks-world planning"

**Educational Value:** Shows how research algorithms can be implemented in GTPyhop for optimal performance.

### blocks_goal_splitting/ - Built-in Goal Decomposition
**Purpose:** Using GTPyhop's built-in goal splitting methods
**Domain:** Blocks world with automatic goal decomposition
**Key Learning Points:**
- Built-in `m_split_multigoal` method
- Automatic goal ordering
- Deleted-condition interactions
- Limitations of naive goal splitting

**Core Concepts Demonstrated:**
- **Multigoal Splitting:** Automatic decomposition of complex goals
- **Sequential Achievement:** Achieving goals one by one
- **Interaction Problems:** How goals can interfere with each other

**Educational Value:** Illustrates both the power and limitations of automatic goal decomposition methods.

## 🏆 IPC 2020 Total Order Examples

### Blocksworld-GTOHP and Childsnack Domains
**Purpose:** Competition-grade planning domains
**Location:** `src/gtpyhop/examples/ipc-2020-total-order/`
**Key Learning Points:**
- Competition-standard domain modeling
- Performance benchmarking
- Scalable planning problems
- Real-world domain complexity

**Domains Available:**
- **Blocksworld-GTOHP:** Advanced blocks world with competition problems
- **Childsnack:** Resource management in childcare setting

**Educational Value:** Shows how GTPyhop handles competition-grade planning problems.

## 🏎️ Running the Examples

### Command-Line Interface
All examples support both legacy and session modes:

```bash
# Legacy mode (backward compatible)
python -m gtpyhop.examples.simple_htn

# Session mode (thread-safe, recommended)
python -m gtpyhop.examples.simple_htn --session

# With custom verbosity and no pauses
python -m gtpyhop.examples.simple_htn --session --verbose 2 --no-pauses
```

### Available Arguments
- `--session`: Enable thread-safe session mode
- `--verbose N`: Set verbosity level (0-3)
- `--no-pauses`: Skip interactive pauses for automated testing

### Regression Testing
```bash
# Test all examples
python -m gtpyhop.examples.regression_tests

# Session-based testing
python -m gtpyhop.examples.regression_tests --session
```

## 📖 Pedagogical Recommendations

### For Beginners
1. Start with `simple_htn.py` to understand basic concepts
2. Compare with `simple_hgn.py` to see goal vs. task approaches
3. Use high verbosity (`--verbose 3`) to see detailed planning traces
4. Experiment with different initial states and goals

### For Advanced Users
1. Study the blocks world examples to understand complex domains
2. Examine the IPC domains for competition-grade problems
3. Use session mode for concurrent planning experiments
4. Analyze planning logs programmatically using the structured logging system

### For Researchers
1. Use the examples as templates for new domains
2. Study the method design patterns in complex examples
3. Benchmark performance using the IPC domains
4. Extend examples with new planning techniques

## 🔗 Related Documentation
- [Running Examples Guide](running_examples.md) - Detailed execution instructions
- [Structured Logging](logging.md) - Analyzing planning traces
- [Thread-Safe Sessions](thread_safe_sessions.md) - Concurrent planning patterns
