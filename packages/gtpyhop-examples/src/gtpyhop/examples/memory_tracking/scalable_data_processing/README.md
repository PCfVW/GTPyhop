# Scalable Data Processing - Memory Tracking Example

## Overview

This example demonstrates memory tracking capabilities in GTPyhop with configurable memory-intensive planning operations. Memory behavior is controlled via state configuration properties, allowing systematic exploration of how data size and transformations affect memory consumption.

## Configuration Options

Each scenario can be configured with:
- **data_type**: `'int'` (~28 bytes), `'string'` (~500 bytes), `'dict'` (~1KB+)
- **num_transforms**: 1-16 (copies created during structure creation)
- **accumulate**: Keep intermediate results or overwrite
- **cleanup**: Release memory at end or retain

## Scenarios (20 total)

### Scenario Groups

| Group | Scenarios | Description | Typical Memory |
|-------|-----------|-------------|----------------|
| Small | 01-05 | 10K data points, testing data types | 1-20 MB |
| Medium | 06-10 | 50-100K points, testing transforms | 15-50 MB |
| Large | 11-15 | 200-300K points, accumulation tests | 50-150 MB |
| Stress | 16-20 | 500K-1M points, max memory usage | 200+ MB |

### Sample Scenarios

| Scenario | Configuration | Expected Behavior |
|----------|--------------|-------------------|
| `scenario_01` | 10K int, 2 transforms, cleanup | ~1.5 MB, fast baseline |
| `scenario_05` | 10K dict, 4 transforms, no cleanup | ~17 MB, data retained |
| `scenario_10` | 100K dict, 16 transforms, no cleanup | Heavy memory, ~30+ sec |
| `scenario_15` | 300K dict, 16 transforms, no cleanup | Stress test (~300MB+) |

## Domain Structure

### Actions (6 total)

1. **a_initialize_memory_demo** - Initialize demo with data size configuration
2. **a_allocate_large_dataset** - Allocate dataset based on config_data_type
3. **a_process_dataset_chunk** - Process dataset in chunks
4. **a_create_memory_intensive_structure** - Create N transform copies
5. **a_perform_memory_operations** - Perform calculations on structures
6. **a_cleanup_memory** - Optionally clean up based on config_cleanup

### Methods (3 total)

1. **m_memory_tracking_demo** - Top-level workflow orchestration
2. **m_allocate_and_process** - Dataset allocation and chunk processing
3. **m_create_and_operate** - Structure creation and operations

### HTN Planning Workflow

```
m_memory_tracking_demo(data_size)
├── a_initialize_memory_demo(data_size)
├── m_allocate_and_process(data_size)
│   ├── a_allocate_large_dataset(data_size)
│   └── a_process_dataset_chunk(chunk_size)
├── m_create_and_operate()
│   ├── a_create_memory_intensive_structure()
│   └── a_perform_memory_operations()
└── a_cleanup_memory()
```

## Quick Start

```bash
cd src/gtpyhop/examples/memory_tracking

# Run all data processing scenarios
python benchmarking.py --example data

# Run specific scenario
python benchmarking.py --example data --scenario scenario_05

# For accurate peak measurement
python benchmarking.py --example data --scenario scenario_05 \
    --disable-gc --sampling-interval 0.001
```

### Memory Measurement Options

- **--disable-gc**: Disable garbage collection during planning (reveals true memory allocation)
- **--sampling-interval FLOAT**: Memory sampling interval in seconds (default: 0.1, use 0.001 for fast scenarios)

## Usage Example

```python
from gtpyhop import PlannerSession
from gtpyhop.examples.memory_tracking.scalable_data_processing import (
    the_domain, get_problems
)

problems = get_problems()
state, tasks, description = problems['scenario_05']

with PlannerSession(domain=the_domain, memory_tracking=True) as session:
    result = session.find_plan(state, tasks)

    if result.success:
        print(f"Plan: {len(result.plan)} actions")
        print(f"Memory used: {result.stats['memory_mb']:.2f} MB")
        print(f"Peak memory: {result.stats['peak_memory_mb']:.2f} MB")
```

## Memory Behavior

### Understanding Memory vs Peak Memory

- **Memory used**: Final state's memory footprint at end of planning
- **Peak memory**: Maximum memory observed during planning (captured by background monitoring)

The difference can be significant because GTPyhop creates deep copies of states during backtracking, which temporarily consume memory before being garbage collected.

### High Peak Memory

Peak memory includes temporary copies created during GTPyhop's backtracking. For scenario_10 (100K dict, 16 transforms), expect peaks of ~3GB due to:
- Original dataset: ~100MB
- 16 transform copies: ~1.6GB
- State deep copies during backtracking: additional ~1.5GB

## Customization

Edit `problems.py` to add custom scenarios:

```python
# BEGIN: Scenario: scenario_custom
_data_size = 50000

initial_state_custom = h_create_configured_state(
    'scenario_custom',
    data_type='dict',
    num_transforms=8,
    accumulate=True,
    cleanup=False
)

problems['scenario_custom'] = (
    initial_state_custom,
    [('m_memory_tracking_demo', _data_size)],
    f'Custom: 50K dict, 8 transforms, no cleanup'
)
# END: Scenario
```

---
*Updated 2026-01-10*
