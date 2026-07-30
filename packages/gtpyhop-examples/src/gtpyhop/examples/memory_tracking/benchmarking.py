#!/usr/bin/env python3
"""
Memory Tracking Benchmarking Script for GTPyhop

This script demonstrates memory tracking capabilities by running
scalable memory-intensive planning problems and measuring actual
memory usage using psutil. It supports two example types:

1. scalable_data_processing: Memory scaling via data size
2. scalable_recursive_decomposition: Memory scaling via recursion depth
   (based on Alford et al. 2015, Theorem 4.1)

Usage:
    python benchmarking.py [options]

Examples:
    python benchmarking.py                              # Run data processing scenarios
    python benchmarking.py --example recursive          # Run recursive decomposition
    python benchmarking.py --example data --scenario scenario_01
    python benchmarking.py --example recursive --scenario scenario_03
    python benchmarking.py --performance-test           # Run performance overhead test

    # Accurate peak measurement for payload scaling (recommended)
    python benchmarking.py --example recursive --scenario scenario_10 \\
        --disable-gc --sampling-interval 0.001

Options:
    --example {data,recursive}   Example type (default: data)
    --scenario NAME              Run specific scenario
    --verbose {0,1,2,3}          Verbosity level (default: 1)
    --disable-gc                 Disable garbage collection during planning
    --sampling-interval FLOAT    Memory sampling interval in seconds (default: 0.1)
    --list-scenarios             List available scenarios
    --performance-test           Compare overhead with/without memory tracking

-- Generated 2026-01-10
"""

import sys
import os
import gc
import time
import argparse
import statistics
from typing import Dict, Any, Optional, List, Tuple

# Add parent directories to path for imports (BEFORE any gtpyhop imports)
# This ensures we use the local source, not the installed package
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate to src/ directory (memory_tracking -> examples -> gtpyhop -> src)
src_dir = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, src_dir)

# Import GTPyhop with memory tracking
try:
    import gtpyhop
    from gtpyhop import PlannerSession, ResourceManager
except ImportError as e:
    print(f"Error: Could not import gtpyhop: {e}")
    print("Please install gtpyhop using: pip install gtpyhop")
    sys.exit(1)

# Import memory tracking components
try:
    from gtpyhop.memory_tracking import MEMORY_TRACKING_AVAILABLE
    if not MEMORY_TRACKING_AVAILABLE:
        print("Warning: Memory tracking dependencies not available")
        print("Install with: pip install psutil")
except ImportError:
    print("Warning: Memory tracking module not available")
    MEMORY_TRACKING_AVAILABLE = False


# Example type constants
EXAMPLE_DATA = 'data'
EXAMPLE_RECURSIVE = 'recursive'

# Map example names to import paths
EXAMPLE_MODULES = {
    EXAMPLE_DATA: 'scalable_data_processing',
    EXAMPLE_RECURSIVE: 'scalable_recursive_decomposition',
}


def get_example_components(example_type: str) -> Tuple[Any, Dict]:
    """
    Import and return domain and problems for the specified example type.

    Args:
        example_type: 'data' or 'recursive'

    Returns:
        Tuple of (domain, problems_dict)
    """
    if example_type == EXAMPLE_DATA:
        from scalable_data_processing import the_domain, get_problems
        return the_domain, get_problems()
    elif example_type == EXAMPLE_RECURSIVE:
        from scalable_recursive_decomposition import the_domain, get_problems
        return the_domain, get_problems()
    else:
        raise ValueError(f"Unknown example type: {example_type}")


def run_memory_tracking_demo(
    example_type: str = EXAMPLE_DATA,
    scenario_name: Optional[str] = None,
    verbose: int = 1,
    disable_gc: bool = False,
    sampling_interval: Optional[float] = None
) -> bool:
    """Run memory tracking demonstration."""
    the_domain, problems = get_example_components(example_type)

    if scenario_name:
        if scenario_name not in problems:
            print(f"Error: Scenario '{scenario_name}' not found")
            print(f"Available scenarios: {list(problems.keys())}")
            return False
        scenarios_to_run = {scenario_name: problems[scenario_name]}
    else:
        scenarios_to_run = problems

    # Use default if not specified
    effective_interval = sampling_interval if sampling_interval is not None else 0.1

    example_name = EXAMPLE_MODULES[example_type]
    print(f"=== Memory Tracking Demonstration: {example_name} ===")
    print(f"GTPyhop version: {gtpyhop.__version__}")
    print(f"Memory tracking available: {MEMORY_TRACKING_AVAILABLE}")
    print(f"Memory sampling interval: {effective_interval:.3f}s")
    print(f"Garbage collection: {'DISABLED' if disable_gc else 'enabled'}")
    print()

    results = []

    for name, (state, tasks, description) in scenarios_to_run.items():
        print(f"Running {name}: {description}")

        # Reset ResourceManager state for fresh measurements
        ResourceManager.reset()

        # Create a fresh copy of the state for each run
        state_copy = state.copy()

        # Disable GC if requested (to prevent reclamation of transient allocations)
        gc_was_enabled = gc.isenabled()
        if disable_gc:
            gc.collect()  # Clean up before measurement
            gc.disable()

        # Run with memory tracking enabled
        start_time = time.time()

        try:
            with PlannerSession(
                domain=the_domain,
                memory_tracking=MEMORY_TRACKING_AVAILABLE,
                memory_sampling_interval=effective_interval,
                verbose=verbose
            ) as session:
                result = session.find_plan(state_copy, tasks)

                execution_time = time.time() - start_time

                if result.success:
                    memory_mb = result.stats.get('memory_mb', 0)
                    peak_memory_mb = result.stats.get('peak_memory_mb', 0)

                    print(f"  Success: {len(result.plan)} actions")
                    print(f"  Memory used: {memory_mb:.2f} MB")
                    print(f"  Peak memory: {peak_memory_mb:.2f} MB")
                    print(f"  Execution time: {execution_time:.3f}s")

                    # For recursive decomposition, also show task count from the modified state
                    if hasattr(state_copy, 'task_count') and state_copy.task_count > 0:
                        print(f"  Leaf tasks executed: {state_copy.task_count}")

                    results.append({
                        'scenario': name,
                        'success': True,
                        'actions': len(result.plan),
                        'memory_mb': memory_mb,
                        'peak_memory_mb': peak_memory_mb,
                        'execution_time': execution_time
                    })
                else:
                    print(f"  Failed: {result.error}")
                    results.append({
                        'scenario': name,
                        'success': False,
                        'error': result.error,
                        'execution_time': execution_time
                    })

        except Exception as e:
            print(f"  Exception: {e}")
            results.append({
                'scenario': name,
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            })

        finally:
            # Re-enable GC if it was enabled before
            if disable_gc and gc_was_enabled:
                gc.enable()
                gc.collect()  # Clean up accumulated allocations

        print()

    # Print summary
    print("=== Summary ===")
    print(f"{'Scenario':<20} {'Status':<10} {'Actions':<8} {'Memory (MB)':<12} {'Peak (MB)':<12} {'Time (s)':<10}")
    print("-" * 82)

    for result in results:
        status = "OK" if result['success'] else "FAILED"
        actions = str(result.get('actions', '-'))
        memory = f"{result.get('memory_mb', 0):.2f}" if result['success'] else '-'
        peak = f"{result.get('peak_memory_mb', 0):.2f}" if result['success'] else '-'
        time_str = f"{result['execution_time']:.3f}"

        print(f"{result['scenario']:<20} {status:<10} {actions:<8} {memory:<12} {peak:<12} {time_str:<10}")

    # Return success if all scenarios passed
    return all(r['success'] for r in results)


def run_performance_overhead_test(
    example_type: str = EXAMPLE_DATA,
    iterations: int = 50
) -> bool:
    """
    Benchmark memory tracking overhead by comparing execution times
    with and without memory tracking enabled.

    Args:
        example_type: 'data' or 'recursive'
        iterations: Number of iterations to run for each configuration

    Returns:
        True if overhead is acceptable (< 5%), False otherwise
    """
    the_domain, problems = get_example_components(example_type)
    state, tasks, _ = problems['scenario_01']  # Use smallest scenario for consistent timing

    example_name = EXAMPLE_MODULES[example_type]
    print(f"=== Memory Tracking Performance Overhead Test: {example_name} ===")
    print(f"Running {iterations} iterations of scenario_01")
    print()

    # Benchmark without memory tracking
    print("Testing without memory tracking...")
    ResourceManager.reset()  # Fresh state before benchmark phase
    no_tracking_times: List[float] = []
    for i in range(iterations):
        state_copy = state.copy()
        start_time = time.time()
        with PlannerSession(
            domain=the_domain,
            memory_tracking=False,
            verbose=0
        ) as session:
            result = session.find_plan(state_copy, tasks)
            if not result.success:
                print(f"  Planning failed on iteration {i}")
                return False
        no_tracking_times.append(time.time() - start_time)

    # Benchmark with memory tracking
    print("Testing with memory tracking...")
    ResourceManager.reset()  # Fresh state before benchmark phase
    with_tracking_times: List[float] = []
    for i in range(iterations):
        state_copy = state.copy()
        start_time = time.time()
        with PlannerSession(
            domain=the_domain,
            memory_tracking=True,
            verbose=0
        ) as session:
            result = session.find_plan(state_copy, tasks)
            if not result.success:
                print(f"  Planning failed on iteration {i}")
                return False
        with_tracking_times.append(time.time() - start_time)

    # Calculate statistics
    no_tracking_avg = statistics.mean(no_tracking_times)
    with_tracking_avg = statistics.mean(with_tracking_times)

    no_tracking_std = statistics.stdev(no_tracking_times) if len(no_tracking_times) > 1 else 0
    with_tracking_std = statistics.stdev(with_tracking_times) if len(with_tracking_times) > 1 else 0

    # Calculate overhead (handle edge case where no_tracking_avg is very small)
    if no_tracking_avg > 0.0001:
        overhead_percent = ((with_tracking_avg - no_tracking_avg) / no_tracking_avg) * 100
    else:
        overhead_percent = 0.0

    print()
    print("=== Performance Results ===")
    print(f"Without tracking: {no_tracking_avg:.4f}s +/- {no_tracking_std:.4f}s")
    print(f"With tracking:    {with_tracking_avg:.4f}s +/- {with_tracking_std:.4f}s")
    print(f"Overhead:         {overhead_percent:.1f}%")
    print()

    # Validate overhead is acceptable (< 5% threshold)
    acceptable_threshold = 5.0
    if overhead_percent < acceptable_threshold:
        print(f"OK: Performance overhead acceptable: {overhead_percent:.1f}% < {acceptable_threshold}%")
        return True
    else:
        print(f"WARNING: Performance overhead high: {overhead_percent:.1f}% >= {acceptable_threshold}%")
        return False


def list_scenarios(example_type: str) -> None:
    """List available scenarios for the specified example type."""
    the_domain, problems = get_example_components(example_type)
    example_name = EXAMPLE_MODULES[example_type]
    print(f"Available scenarios for {example_name}:")
    for name, (_, _, description) in problems.items():
        print(f"  - {name}: {description}")


def create_argument_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Memory Tracking Benchmarking for GTPyhop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmarking.py                                    # Run data processing scenarios
  python benchmarking.py --example recursive                # Run recursive decomposition
  python benchmarking.py --example data --scenario scenario_01
  python benchmarking.py --example recursive --scenario scenario_03
  python benchmarking.py --performance-test --example recursive
  python benchmarking.py --list-scenarios --example recursive

Example Types:
  data      - scalable_data_processing: Memory scaling via data size
  recursive - scalable_recursive_decomposition: Memory scaling via recursion depth
              (based on Alford et al. 2015, Theorem 4.1)
        """
    )

    parser.add_argument(
        '--example', '-e',
        type=str,
        default=EXAMPLE_DATA,
        choices=[EXAMPLE_DATA, EXAMPLE_RECURSIVE],
        help=f"Example type to run (default: {EXAMPLE_DATA})"
    )

    parser.add_argument(
        '--scenario',
        type=str,
        help='Run specific scenario (e.g., scenario_01, scenario_03)'
    )

    parser.add_argument(
        '--verbose', '-v',
        type=int,
        default=1,
        choices=[0, 1, 2, 3],
        help='Verbosity level (0=silent, 1=normal, 2=detailed, 3=debug)'
    )

    parser.add_argument(
        '--list-scenarios',
        action='store_true',
        help='List available scenarios and exit'
    )

    parser.add_argument(
        '--performance-test',
        action='store_true',
        help='Run performance overhead test (compares with/without memory tracking)'
    )

    parser.add_argument(
        '--iterations',
        type=int,
        default=50,
        help='Number of iterations for performance test (default: 50)'
    )

    parser.add_argument(
        '--disable-gc',
        action='store_true',
        help='Disable garbage collection during planning (reveals true memory allocation)'
    )

    parser.add_argument(
        '--sampling-interval',
        type=float,
        default=None,
        help='Memory sampling interval in seconds (default: 0.1). Lower values capture faster peaks.'
    )

    return parser


def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.list_scenarios:
        list_scenarios(args.example)
        return 0

    if args.performance_test:
        success = run_performance_overhead_test(
            example_type=args.example,
            iterations=args.iterations
        )
        return 0 if success else 1

    success = run_memory_tracking_demo(
        example_type=args.example,
        scenario_name=args.scenario,
        verbose=args.verbose,
        disable_gc=args.disable_gc,
        sampling_interval=args.sampling_interval
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
