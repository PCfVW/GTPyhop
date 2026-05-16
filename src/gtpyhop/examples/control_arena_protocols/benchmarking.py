#!/usr/bin/env python3
"""
Control Arena Protocol Benchmarking Script for GTPyhop

This script runs the control arena protocol examples and demonstrates
HTN planning with backtracking for AI safety micro-protocols.

Usage:
    python benchmarking.py [options]

Examples:
    python benchmarking.py                                  # Run defer_to_trusted
    python benchmarking.py --example resample               # Run resample protocol
    python benchmarking.py --example adversarial             # Run adversarial protocol
    python benchmarking.py --example defer --scenario scenario_2_high_suspicion
    python benchmarking.py --list-scenarios --example adversarial

Options:
    --example {defer,resample,adversarial}  Example type (default: defer)
    --scenario NAME                         Run specific scenario
    --strategy STRATEGY                     Planning strategy (default: iterative_dfs_backtracking)
    --verbose {0,1,2,3}                     Verbosity level (default: 1)
    --list-scenarios                        List available scenarios

-- Generated 2026-03-31
"""

import sys
import os
import time
import argparse
from typing import Dict, Any, Optional, List, Tuple

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, src_dir)

# Import GTPyhop
try:
    import gtpyhop
    from gtpyhop import PlannerSession
except ImportError as e:
    print(f"Error: Could not import gtpyhop: {e}")
    print("Please install gtpyhop using: pip install gtpyhop")
    sys.exit(1)

# Example type constants
EXAMPLE_DEFER = 'defer'
EXAMPLE_RESAMPLE = 'resample'
EXAMPLE_ADVERSARIAL = 'adversarial'

# Map example names to import paths
EXAMPLE_MODULES = {
    EXAMPLE_DEFER: 'defer_to_trusted_protocol',
    EXAMPLE_RESAMPLE: 'defer_to_resample_protocol',
    EXAMPLE_ADVERSARIAL: 'adversarial_protocol',
}


def get_example_components(example_type: str) -> Tuple[Any, Dict]:
    """
    Import and return domain and problems for the specified example type.

    Args:
        example_type: 'defer', 'resample', or 'adversarial'

    Returns:
        Tuple of (domain, problems_dict)
    """
    if example_type == EXAMPLE_DEFER:
        from defer_to_trusted_protocol import the_domain, get_problems
        return the_domain, get_problems()
    elif example_type == EXAMPLE_RESAMPLE:
        from defer_to_resample_protocol import the_domain, get_problems
        return the_domain, get_problems()
    elif example_type == EXAMPLE_ADVERSARIAL:
        from adversarial_protocol import the_domain, get_problems
        return the_domain, get_problems()
    else:
        raise ValueError(f"Unknown example type: {example_type}")


def run_protocol_demo(
    example_type: str = EXAMPLE_DEFER,
    scenario_name: Optional[str] = None,
    verbose: int = 1,
    strategy: str = 'iterative_dfs_backtracking'
) -> bool:
    """Run control arena protocol demonstration."""
    the_domain, problems = get_example_components(example_type)

    if scenario_name:
        if scenario_name not in problems:
            print(f"Error: Scenario '{scenario_name}' not found")
            print(f"Available scenarios: {list(problems.keys())}")
            return False
        scenarios_to_run = {scenario_name: problems[scenario_name]}
    else:
        scenarios_to_run = problems

    example_name = EXAMPLE_MODULES[example_type]
    print(f"=== Control Arena Protocol: {example_name} ===")
    print(f"GTPyhop version: {gtpyhop.__version__}")
    print(f"Strategy: {strategy}")
    print()

    results = []

    for name, (state, tasks, description) in scenarios_to_run.items():
        print(f"Running {name}: {description}")

        state_copy = state.copy()
        start_time = time.time()

        try:
            with PlannerSession(
                domain=the_domain,
                verbose=verbose,
                strategy=strategy
            ) as session:
                result = session.find_plan(state_copy, tasks)
                execution_time = time.time() - start_time

                if result.success:
                    # Determine routing outcome
                    has_accept = any(a[0] == 'a_accept_output' for a in result.plan)
                    has_defer = any(a[0] == 'a_defer_to_trusted' for a in result.plan)
                    # accept_no_ee: scenario uses a_accept_output_demo_no_expected_effect
                    # (the negative-control teaching variant from adversarial_protocol,
                    # added 2026-05-16). Plan is an accept-trajectory but the
                    # [EXPECTED_EFFECT] block is omitted, so safety-critical state
                    # like side_task_observed is never set.
                    has_accept_demo = any(
                        a[0] == 'a_accept_output_demo_no_expected_effect' for a in result.plan
                    )
                    outcome = ('accept' if has_accept
                               else 'accept_no_ee' if has_accept_demo
                               else 'defer' if has_defer
                               else 'unknown')

                    print(f"  Success: {len(result.plan)} actions, outcome: {outcome}")
                    print(f"  Time: {execution_time:.3f}s")

                    results.append({
                        'scenario': name,
                        'success': True,
                        'actions': len(result.plan),
                        'outcome': outcome,
                        'execution_time': execution_time
                    })
                else:
                    print(f"  Failed")
                    results.append({
                        'scenario': name,
                        'success': False,
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

        print()

    # Print summary
    print("=== Summary ===")
    print(f"{'Scenario':<35} {'Status':<8} {'Actions':<8} {'Outcome':<8} {'Time (s)':<10}")
    print("-" * 79)

    for result in results:
        status = "OK" if result['success'] else "FAILED"
        actions = str(result.get('actions', '-'))
        outcome = result.get('outcome', '-')
        time_str = f"{result['execution_time']:.3f}"

        print(f"{result['scenario']:<35} {status:<8} {actions:<8} {outcome:<8} {time_str:<10}")

    return all(r['success'] for r in results)


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
        description="Control Arena Protocol Benchmarking for GTPyhop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmarking.py                                    # Run defer_to_trusted
  python benchmarking.py --example resample                 # Run resample protocol
  python benchmarking.py --example adversarial              # Run adversarial protocol
  python benchmarking.py --example defer --scenario scenario_2_high_suspicion
  python benchmarking.py --list-scenarios --example adversarial

Example Types:
  defer       - Defer to Trusted: accept or defer based on suspicion threshold
  resample    - Defer to Resample: recursive multi-sample protocol
  adversarial - Adversarial: honest vs. attack with vulnerability detection
        """
    )

    parser.add_argument(
        '--example', '-e',
        type=str,
        default=EXAMPLE_DEFER,
        choices=[EXAMPLE_DEFER, EXAMPLE_RESAMPLE, EXAMPLE_ADVERSARIAL],
        help=f"Example type to run (default: {EXAMPLE_DEFER})"
    )

    parser.add_argument(
        '--scenario',
        type=str,
        help='Run specific scenario (e.g., scenario_2_high_suspicion)'
    )

    parser.add_argument(
        '--strategy',
        type=str,
        default='iterative_dfs_backtracking',
        help='Planning strategy (default: iterative_dfs_backtracking)'
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

    return parser


def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.list_scenarios:
        list_scenarios(args.example)
        return 0

    success = run_protocol_demo(
        example_type=args.example,
        scenario_name=args.scenario,
        verbose=args.verbose,
        strategy=args.strategy
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
