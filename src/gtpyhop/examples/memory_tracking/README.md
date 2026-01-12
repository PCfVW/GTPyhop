# Memory Tracking Examples for GTPyhop

## Overview

This directory contains examples demonstrating **memory tracking capabilities** in GTPyhop using the `psutil` library. The examples show how memory usage scales with different aspects of planning problem complexity.

**Note**: These examples measure **plan execution memory** (accumulated state during action execution), not the planner's internal working memory. See the [scalable_recursive_decomposition README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md#what-we-measure-vs-theoretical-complexity) for a detailed explanation of this distinction.

## Available Examples

| Example | Directory | Description |
|---------|-----------|-------------|
| **Scalable Data Processing** | `scalable_data_processing/` | Memory scaling via data size and transformations |
| **Scalable Recursive Decomposition** | `scalable_recursive_decomposition/` | Memory scaling via method recursion depth |

### 1. Scalable Data Processing

Demonstrates memory behavior when scaling **data volume**:
- Varying data sizes (10K to 1M items)
- Different data types (int, string, dict)
- Multiple transformation passes

**Use case**: Understanding how state payload size affects memory consumption.

### 2. Scalable Recursive Decomposition

Demonstrates memory behavior when scaling **structural complexity**:
- Varying recursion depths (4 to 14 levels)
- Exponential task growth (2^k tasks for depth k)
- Based on Alford et al. (2015) Theorem 4.1
- Measures execution memory (exponential), not planning memory (polynomial)

**Use case**: Understanding how HTN decomposition structure affects memory consumption during plan execution.

## Directory Structure

```
memory_tracking/
├── __init__.py
├── benchmarking.py                      # Unified benchmarking script
├── benchmarking_quickstart.md           # Quick start guide
├── README.md                            # This file
├── scalable_data_processing/
│   ├── __init__.py
│   ├── domain.py
│   ├── problems.py
│   └── README.md
└── scalable_recursive_decomposition/
    ├── __init__.py
    ├── domain.py
    ├── problems.py
    └── README.md
```

## Quick Start

```bash
cd src/gtpyhop/examples/memory_tracking

# Run data processing scenarios (default)
python benchmarking.py

# Run recursive decomposition scenarios
python benchmarking.py --example recursive

# Run specific scenario
python benchmarking.py --example recursive --scenario scenario_03

# Run with accurate peak measurement (recommended for payload scaling)
python benchmarking.py --example recursive --scenario scenario_10 \
    --disable-gc --sampling-interval 0.001

# List available scenarios
python benchmarking.py --list-scenarios --example recursive
```

## Requirements

- GTPyhop 1.8.0+
- psutil (`pip install psutil`)
- Python 3.8+

## Memory Tracking Features

- **Real memory measurement** using psutil
- **Configurable sampling interval** (default 0.1s, use 0.001s for fast scenarios)
- **Session-based isolation** for concurrent planning
- **GC control** via `--disable-gc` for accurate transient allocation measurement
- **Graceful fallback** when psutil is unavailable

## See Also

- [benchmarking_quickstart.md](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/benchmarking_quickstart.md) - Detailed usage guide
- [scalable_data_processing/README.md](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_data_processing/README.md) - Data processing example details
- [scalable_recursive_decomposition/README.md](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md) - Recursive decomposition example details (includes theoretical background)

---
*Updated 2026-01-12*
