# Scalable Recursive Decomposition - Memory Tracking Example

## Overview

This example demonstrates memory scaling behavior when planning complexity arises from **recursive method decomposition depth** rather than data size. It complements the `scalable_data_processing` example by showing how hierarchical task structure itself drives memory consumption.

**Important Clarification**: This example measures **plan execution memory** (accumulated state during action execution), not the planner's internal working memory. See [What We Measure vs. Theoretical Complexity](#what-we-measure-vs-theoretical-complexity) for details.

## Theoretical Foundation

### The Paper

Ron Alford, Pascal Bercher, & David Aha (2015). ["Tight Bounds for HTN Planning."](https://ojs.aaai.org/index.php/ICAPS/article/view/13721) 25th ICAPS, pp. 7-15. [Video Recording](https://www.icaps-conference.org/recording/tight-bounds-for-htn-planning/)

### Theorem 4.1 (p.5)

> Plan-existence for totally-ordered mostly-acyclic propositional HTN problems is PSPACE-complete.

**What this means**: Even when HTN methods are:
- **Totally-ordered** (subtasks execute in a fixed sequence)
- **Mostly-acyclic** (recursion is bounded, no infinite loops)
- **Propositional** (no variables, ground terms only)

...the problem of deciding whether a plan exists is as hard as the hardest problems solvable in polynomial space (PSPACE).

### Why Theorem 4.1 Instead of Theorem 3.7?

The paper presents two relevant results:

| Theorem | Problem Class | Complexity |
|---------|--------------|------------|
| 3.7 | Totally-ordered **tail-recursive** | PSPACE-complete |
| 4.1 | Totally-ordered **mostly-acyclic** | PSPACE-complete |

We implement the **acyclic** structure from Theorem 4.1 because:

1. **Acyclic is stricter than tail-recursive**: Acyclic problems are a proper subset of tail-recursive problems. Our implementation has no cycles at all — each method decomposes to strictly lower levels, never back to itself.

2. **Same complexity class**: Both are PSPACE-complete, so we demonstrate the same theoretical result.

3. **Cleaner structure**: The acyclic binary decomposition from Section 4 is easier to understand and implement correctly.

4. **Guaranteed termination**: Acyclic structures cannot loop indefinitely, making them safer for demonstration purposes.

### The Counting Structure (Section 4, p.4-5)

The paper shows how to encode **2^k repetitions** of a task using k method levels:

```
Let o_0 be a primitive task (action).
Define methods M = {(o_1, tn_1), ..., (o_k, tn_k)} where each tn_i
contains two totally-ordered copies of o_{i-1}.

Then o_k decomposes into 2^k copies of o_0.
```

**Visually**:
```
m_recurse_level(3)
├── m_recurse_level(2)
│   ├── m_recurse_level(1)
│   │   ├── m_recurse_level(0) → a_execute_leaf_task
│   │   └── m_recurse_level(0) → a_execute_leaf_task
│   └── m_recurse_level(1)
│       ├── m_recurse_level(0) → a_execute_leaf_task
│       └── m_recurse_level(0) → a_execute_leaf_task
└── m_recurse_level(2)
    ├── m_recurse_level(1)
    │   ├── m_recurse_level(0) → a_execute_leaf_task
    │   └── m_recurse_level(0) → a_execute_leaf_task
    └── m_recurse_level(1)
        ├── m_recurse_level(0) → a_execute_leaf_task
        └── m_recurse_level(0) → a_execute_leaf_task

Result: 8 = 2^3 leaf tasks
```

## What We Measure vs. Theoretical Complexity

### Understanding PSPACE-Completeness

Theorem 4.1 states that plan-existence is **PSPACE-complete**, meaning the planner's **working memory** during search is bounded by a polynomial in the input size. However, this does not mean that:
- The **plan length** is polynomial (it can be exponential: 2^k actions)
- The **accumulated execution state** is polynomial (it can be exponential)

The theorem guarantees that a planner needs only polynomial space to *decide* whether a plan exists—not that executing the plan uses polynomial memory.

### What This Example Actually Measures

This example measures **plan execution memory**: the memory consumed by accumulated results in `state.results` as actions execute. This grows as **2^k × payload_size** (exponential in depth).

| What | Growth | Measured Here? |
|------|--------|----------------|
| Plan length | O(2^k) exponential | Yes (action count) |
| Accumulated state (`state.results`) | O(2^k × payload) exponential | **Yes** (peak memory) |
| Planner's task network | O(r × h) polynomial | No |
| Planner's call stack | O(depth) polynomial | No |

### Why Not Measure Planning Memory Directly?

Measuring the planner's internal working memory separately from execution memory is impractical in GTPyhop for several reasons:

**1. State copies are transient and immediately released**

GTPyhop creates state copies only when applying actions, and releases them immediately after. There is no backtracking that would retain multiple states:

```python
# From main.py _apply_action_and_continue_recursive():
state_copy = state.copy()           # Created
newstate = action(state_copy, ...)  # Used
return seek_plan_recursive(newstate, ...)  # state_copy eligible for GC
```

**2. Python's garbage collector masks transient allocations**

The background memory monitor samples at configurable intervals (default 0.1s, minimum 0.001s). State copies created and destroyed within milliseconds may never be captured:

```
Timeline:    |--sample--|--sample--|--sample--|
State copy:     ^create    ^destroy
                  (never sampled!)
```

**3. Plan output and accumulated state dominate measurements**

The plan list and `state.results` persist and grow throughout planning. These execution artifacts dwarf the planner's transient working memory, making it impossible to isolate planning-specific memory usage.

**4. GTPyhop's architecture interleaves planning and execution**

Unlike planners that first generate a complete plan then execute it, GTPyhop applies actions during the search process. The state modifications (including our `state.results` accumulation) happen *during* planning, not after.

### What This Example Demonstrates

Despite not measuring theoretical planning complexity directly, this example effectively demonstrates:

1. **Memory tracking accuracy**: The psutil-based measurement correctly captures the predictable 2^k × payload_size memory growth
2. **Exponential scaling from HTN structure**: Shows how recursive decomposition depth drives resource consumption
3. **Measurement methodology**: Validates sampling intervals, GC effects, and peak detection
4. **Practical planning costs**: Real-world HTN planning incurs these execution costs

### The Planner's Actual Working Memory (For Reference)

For completeness, GTPyhop's internal working memory during planning is indeed polynomial:

- **Task network (todo_list)**: At most O(r × h) tasks, where r = max subtasks per method, h = decomposition height
- **Call stack / explicit stack**: Bounded by decomposition depth O(h)
- **Current state**: Single state object (no parallel branches)

This matches the PSPACE bound from Theorem 4.1. However, measuring this separately would require instrumenting the planner internals, which is outside the scope of this memory tracking demonstration.

## Implementation

### Domain Structure

**Actions (3 total)**:
- `a_initialize_recursion` - Initialize results accumulator
- `a_execute_leaf_task` - Append payload_size bytes to state.results
- `a_finalize_recursion` - Mark execution complete

**Methods (2 total)**:
- `m_recursive_decomposition(depth)` - Top-level entry point
- `m_recurse_level(level)` - Binary recursive decomposition

### The Core Implementation

```python
def m_recurse_level(state, level):
    if level == 0:
        # Base case: execute single leaf task
        return [("a_execute_leaf_task",)]
    else:
        # Recursive case: two copies of next lower level
        return [
            ("m_recurse_level", level - 1),
            ("m_recurse_level", level - 1)
        ]
```

This directly implements Alford et al.'s counting structure.

### Expected Plan Length

For depth k: **2^k + 2 actions**
- 1 initialization action
- 2^k leaf task executions
- 1 finalization action

| Depth | Leaf Tasks | Total Actions |
|-------|------------|---------------|
| 4 | 16 | 18 |
| 6 | 64 | 66 |
| 8 | 256 | 258 |
| 10 | 1024 | 1026 |
| 12 | 4096 | 4098 |
| 14 | 16384 | 16386 |

## Scenarios

### Configuration Parameters

- **config_depth**: Recursion depth k (controls task count as 2^k)
- **config_payload_size**: Bytes appended per leaf task (memory = 2^k × payload_size)

#### What is a "Payload"?

In this memory tracking context, **payload** refers to the amount of data (in bytes) that each leaf task appends to `state.results` when it executes. It simulates the memory footprint of real-world action effects—such as storing sensor readings, computation results, or intermediate data structures.

By varying the payload size, we can control memory consumption independently of the number of tasks, allowing us to distinguish between:
- **Structural scaling**: More tasks (controlled by depth)
- **Data scaling**: Larger data per task (controlled by payload)

### Group A: Depth Scaling (Fixed 1KB Payload)

| Scenario | Depth | Leaf Tasks | Purpose |
|----------|-------|------------|---------|
| scenario_01 | 4 | 16 | Baseline |
| scenario_02 | 6 | 64 | Light |
| scenario_03 | 8 | 256 | Medium |
| scenario_04 | 10 | 1024 | Heavy |
| scenario_05 | 12 | 4096 | Stress |
| scenario_06 | 14 | 16384 | Extreme |

### Group B: Payload Scaling (Fixed Depth 8)

| Scenario | Depth | Payload | Expected Data | Measured Peak* |
|----------|-------|---------|---------------|----------------|
| scenario_07 | 8 | 100B | ~25 KB | ~1.1 MB |
| scenario_08 | 8 | 1KB | ~256 KB | ~1.2 MB |
| scenario_09 | 8 | 10KB | ~2.5 MB | ~3.5 MB |
| scenario_10 | 8 | 100KB | ~25.6 MB | ~26 MB |

*Measured on Windows 11, Python 3.14, GTPyhop 1.8.0. Values vary by machine and OS.

**Data formula**: 256 tasks × payload_size

#### Understanding the Difference Between Expected and Measured

The "Expected Data" column shows the **pure payload data** (2^k × payload_size). The "Measured Peak" column shows **actual memory measurements**, which include additional overhead:

1. **Baseline overhead (~1 MB)**: Python runtime, GTPyhop module, psutil, and other loaded libraries contribute a fixed baseline that dominates small payload scenarios.

2. **Python object overhead**: Each byte array in `state.results` carries Python object headers and list structure overhead beyond the raw payload bytes.

3. **Plan list**: The 258 action tuples in the plan list consume memory (minor contribution).

4. **Runtime allocations**: Temporary objects created during planning that haven't been garbage collected.

**Key insight**: For small payloads (100B, 1KB), the ~1 MB baseline overhead dominates, making the "Expected Data" values misleading. For large payloads (100KB), the payload data dominates and measurements closely match expectations. This demonstrates that the memory tracking accurately captures the **scaling behavior** even though absolute values include unavoidable overhead.

### Group C: Combined Scaling

| Scenario | Depth | Payload | Purpose |
|----------|-------|---------|---------|
| scenario_11 | 10 | 10KB | Combined stress |
| scenario_12 | 12 | 10KB | Maximum practical |

## Quick Start

```bash
cd src/gtpyhop/examples/memory_tracking

# Basic run
python benchmarking.py --example recursive --scenario scenario_03

# For accurate peak memory measurement (recommended for payload scaling)
python benchmarking.py --example recursive --scenario scenario_10 --disable-gc --sampling-interval 0.001
```

## Usage Example

```python
from gtpyhop import PlannerSession
from gtpyhop.examples.memory_tracking.scalable_recursive_decomposition import (
    the_domain, get_problems
)

problems = get_problems()
state, tasks, description = problems['scenario_10']  # 100KB payload

with PlannerSession(
    domain=the_domain,
    memory_tracking=True,
    memory_sampling_interval=0.001  # 1ms for accurate peak capture
) as session:
    result = session.find_plan(state, tasks)

    if result.success:
        print(f"Plan: {len(result.plan)} actions")  # 258 actions
        print(f"Memory used: {result.stats['memory_mb']:.2f} MB")
        print(f"Peak memory: {result.stats['peak_memory_mb']:.2f} MB")  # ~25 MB
```

## Memory Behavior

### What Drives Memory Usage (Execution Memory)

The memory we measure is **execution memory**, primarily driven by:

1. **Data accumulation** (dominant): Each leaf task appends `config_payload_size` bytes to `state.results`. This is the main contributor to measured memory.
2. **Plan accumulation**: The growing plan list stores 2^k + 2 action tuples (minor contribution).
3. **Task network**: Transient task lists during decomposition (polynomial, not captured).

### Expected Patterns

- **Depth scaling**: Memory grows exponentially with depth (2^k leaf tasks × payload)
- **Payload scaling**: Memory grows linearly with payload size
- **Combined**: Total memory = O(2^depth × payload_size)

This exponential growth reflects **plan execution costs**, not the planner's polynomial working memory.

### Memory Formula

```
Expected peak memory ≈ 2^depth × payload_size + overhead
```

Examples (depth 8 = 256 tasks):
- 100B payload → ~25 KB data
- 1KB payload → ~256 KB data
- 100KB payload → ~25.6 MB data

**Note**: This exponential scaling is expected and correct—it measures the accumulated results from executing 2^k actions, not the planner's internal memory usage.

### Measurement Tips

For accurate peak memory capture:

```bash
# Use fast sampling (1ms) and disable GC
python benchmarking.py --example recursive --scenario scenario_10 \
    --disable-gc --sampling-interval 0.001
```

- **--disable-gc**: Prevents garbage collection from reclaiming data during measurement
- **--sampling-interval 0.001**: Samples memory every 1ms (captures fast peaks)

Default sampling (0.1s) may miss peaks in scenarios completing in <100ms.

### Explicit Memory Sampling

For fast-executing domains, the background monitoring thread may not sample frequently
enough to capture peak memory. This domain calls `ResourceManager.sample_memory()` after
each leaf task execution to ensure accurate peak detection:

```python
# In a_execute_leaf_task action:
from gtpyhop import ResourceManager
ResourceManager.sample_memory()  # Capture memory at this point
```

This ensures reliable peak memory measurements regardless of execution speed.

## Comparison with scalable_data_processing

| Aspect | scalable_data_processing | scalable_recursive_decomposition |
|--------|-------------------------|----------------------------------|
| **Scaling dimension** | Data size (N items) | Structure depth (k levels) |
| **Growth pattern** | O(N) tasks | O(2^k) tasks |
| **Memory driver** | Large data structures | Accumulated results per task |
| **Theoretical basis** | Empirical | Alford et al. (2015) Theorem 4.1 |
| **What's measured** | Execution memory | Execution memory |
| **Memory growth** | Linear in data size | Exponential in depth |

## References

1. Ron Alford, Pascal Bercher, & David Aha (2015). ["Tight Bounds for HTN Planning."](https://ojs.aaai.org/index.php/ICAPS/article/view/13721) 25th ICAPS, pp. 7-15. [Video Recording](https://www.icaps-conference.org/recording/tight-bounds-for-htn-planning/)

2. Kutluhan  Erol, Jim Hendler, & Dana Nau (1996). [Complexity Results for HTN Planning](https://www.cs.umd.edu/~nau/papers/erol1996complexity.pdf). *Annals of Mathematics and Artificial Intelligence*, 18(1), 69-93.

---
*Updated 2026-01-12*
