# Memory Tracking Benchmarking - Quick Start Guide

## Prerequisites

- GTPyhop 1.8.0+ with memory tracking support
- psutil package
- Python 3.8+

### Installing Dependencies

```bash
pip install psutil
```

## Available Examples

| Example | Command Flag | Description |
|---------|--------------|-------------|
| `scalable_data_processing` | `--example data` | Memory scaling via data size (default) |
| `scalable_recursive_decomposition` | `--example recursive` | Memory scaling via recursion depth |

## Running the Demo

### Basic Usage

```bash
cd src/gtpyhop/examples/memory_tracking

# Run data processing scenarios (default)
python benchmarking.py

# Run recursive decomposition scenarios
python benchmarking.py --example recursive
```

### Run Specific Scenario

```bash
# Data processing examples
python benchmarking.py --example data --scenario scenario_01
python benchmarking.py --example data --scenario scenario_05

# Recursive decomposition examples
python benchmarking.py --example recursive --scenario scenario_03
python benchmarking.py --example recursive --scenario scenario_08
```

### List Available Scenarios

```bash
python benchmarking.py --list-scenarios --example data
python benchmarking.py --list-scenarios --example recursive
```

### Verbosity Levels

```bash
python benchmarking.py --verbose 0  # Silent (results only)
python benchmarking.py --verbose 1  # Normal (default)
python benchmarking.py --verbose 2  # Detailed
python benchmarking.py --verbose 3  # Debug
```

### Performance Test

```bash
# Test memory tracking overhead (default 50 iterations)
python benchmarking.py --performance-test

# For recursive decomposition
python benchmarking.py --performance-test --example recursive

# Custom iteration count
python benchmarking.py --performance-test --iterations 100
```

### Memory Measurement Options

```bash
# Disable garbage collection (reveals true memory allocation)
python benchmarking.py --example recursive --scenario scenario_10 --disable-gc

# Set memory sampling interval (default: 0.1s, use lower for fast scenarios)
python benchmarking.py --example recursive --scenario scenario_10 --sampling-interval 0.001

# Combined for accurate peak measurement
python benchmarking.py --example recursive --scenario scenario_10 \
    --disable-gc --sampling-interval 0.001
```

## Example 1: scalable_data_processing

Memory scaling via data size and transformations.

### Quick Reference

| Scenario | Data Type | Size | Transforms | Cleanup | Expected Memory |
|----------|-----------|------|------------|---------|-----------------|
| `scenario_01` | int | 10K | 2 | Yes | ~1.5 MB |
| `scenario_05` | dict | 10K | 4 | No | ~17 MB |
| `scenario_10` | dict | 100K | 16 | No | ~30 MB |
| `scenario_15` | dict | 300K | 16 | No | ~100+ MB |

### Configuration Options

- `config_data_type`: `'int'`, `'string'`, or `'dict'`
- `config_num_transforms`: 1-16 transformation copies
- `config_accumulate`: Keep intermediate results
- `config_cleanup`: Release memory at end

## Example 2: scalable_recursive_decomposition

Memory scaling via recursive method decomposition depth.
Based on Alford et al. (2015) Theorem 4.1.

**Note**: This measures **execution memory** (accumulated state from 2^k actions), not the planner's polynomial working memory. See the [detailed README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md#what-we-measure-vs-theoretical-complexity) for the distinction.

### Quick Reference

| Scenario | Depth | Leaf Tasks | Payload | Expected Peak Memory |
|----------|-------|------------|---------|---------------------|
| `scenario_01` | 4 | 16 | 1KB | ~16 KB |
| `scenario_03` | 8 | 256 | 1KB | ~256 KB |
| `scenario_05` | 12 | 4096 | 1KB | ~4 MB |
| `scenario_10` | 8 | 256 | 100KB | ~25.6 MB |
| `scenario_12` | 12 | 4096 | 10KB | ~40 MB |

Memory formula: `2^depth × payload_size`

### Configuration Options

- `config_depth`: Recursion depth k (yields 2^k leaf tasks)
- `config_payload_size`: Bytes appended per leaf task (accumulates in state.results)

### How It Works

Recursion depth k produces 2^k leaf tasks via binary decomposition:
```
m_recurse_level(k) -> [m_recurse_level(k-1), m_recurse_level(k-1)]
m_recurse_level(0) -> [a_execute_leaf_task]
```

## Understanding Results

- **Memory used**: Session memory usage relative to baseline (MB)
- **Peak memory**: Maximum observed memory during planning (MB)
- **Execution time**: Total planning time (seconds)
- **Leaf tasks executed**: (recursive only) Count of primitive tasks at recursion leaves

### Note on Memory Measurements

- **Memory used**: Final session memory relative to baseline
- **Peak memory**: Maximum observed during planning (sampled at configured interval)
- **Sampling interval**: Use `--sampling-interval 0.001` for fast scenarios (<100ms)
- **GC effects**: Use `--disable-gc` to prevent garbage collection during measurement

## Example Output

### Data Processing
```
=== Memory Tracking Demonstration: scalable_data_processing ===
GTPyhop version: 1.8.0
Memory tracking available: True

Running scenario_05: 10K dict, 4 transforms, accumulate, NO cleanup
  Success: 6 actions
  Memory used: 17.19 MB
  Peak memory: 17.19 MB
  Execution time: 0.761s
```

### Recursive Decomposition
```
=== Memory Tracking Demonstration: scalable_recursive_decomposition ===
GTPyhop version: 1.8.0
Memory tracking available: True
Memory sampling interval: 0.001s
Garbage collection: DISABLED

Running scenario_10: Depth 8: 256 leaf tasks, 258 actions, 100KB payload
  Success: 258 actions
  Memory used: 1.18 MB
  Peak memory: 25.54 MB
  Execution time: 0.020s
```

---
*Updated 2026-01-12*
