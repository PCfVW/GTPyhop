"""
Memory Tracking Examples for GTPyhop

This package contains examples demonstrating GTPyhop's memory tracking
capabilities using the battle-tested psutil library. These examples show
how memory usage scales with planning problem size and provide real
memory measurements during HTN planning operations.

Examples:
- scalable_data_processing: Memory-intensive HTN domain demonstrating
  memory tracking with scalable data processing (1K to 1M data points)
- scalable_recursive_decomposition: Memory tracking with recursive HTN
  task decomposition (2^k leaf tasks for depth k)

-- Generated 2026-01-09
"""

# Make subpackages available
__all__ = ['scalable_data_processing', 'scalable_recursive_decomposition']
