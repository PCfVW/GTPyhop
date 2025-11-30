#!/usr/bin/env python3
"""
Benchmarking Script for MCP Orchestration Examples

This script benchmarks MCP orchestration domains in the current directory.
It imports shared infrastructure from ipc-2020-total-order but runs in the
mcp-orchestration context.

Usage:
    python benchmarking.py <domain_package_name> [options]

Examples:
    python benchmarking.py bio_opentrons
    python benchmarking.py bio_opentrons --verbose 0
    python benchmarking.py --list-domains
"""

import sys
import os

# Add current directory to path first (for mcp-orchestration domains)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the benchmarking infrastructure from ipc-2020-total-order
ipc_dir = os.path.join(current_dir, '..', 'ipc-2020-total-order')
sys.path.insert(0, ipc_dir)

# Import all benchmarking components except list_available_domains
from benchmarking import (
    PlannerBenchmark, load_domain_package, create_argument_parser,
    set_verbose_level, gtpyhop_source, get_verbose_level,
    BenchmarkResult, ResourceUsage
)
from gtpyhop import PlannerSession


class MCPBenchmark(PlannerBenchmark):
    """
    Extended benchmark for MCP orchestration domains that use task lists
    instead of goal dictionaries.
    """

    def run_single(self, problem_name, state, tasks, benchmarking_verbose=0, multiple_problems=False):
        """
        Execute a single MCP planning problem with task-based goals.

        Args:
            problem_name: Unique identifier for the problem
            state: Initial state
            tasks: List of tasks (not goal dict)
            benchmarking_verbose: Verbosity level
            multiple_problems: Whether part of batch

        Returns:
            BenchmarkResult
        """
        if self.verbose:
            print(f"Solving {problem_name}...")

        if not multiple_problems:
            current_verbose_level = get_verbose_level()
            set_verbose_level(benchmarking_verbose)

        plan = None
        resources = ResourceUsage()
        error = None
        exec_time = 0.0

        try:
            with self.track_resources() as tracker:
                if self.use_sessions:
                    session_verbose = benchmarking_verbose if not multiple_problems else 0
                    with PlannerSession(domain=self.domain, verbose=session_verbose) as session:
                        with session.isolated_execution():
                            # Tasks are already a list, pass directly
                            result = session.find_plan(state, tasks)
                            plan = result.plan if (result and result.success) else None
                else:
                    plan = self.planner(state, tasks)

            exec_time = tracker.exec_time
            resources = tracker.resources
            success = plan is not False and plan is not None
            plan_length = len(plan) if success else None

        except Exception as e:
            error = str(e)
            success = False
            plan_length = None

        if not multiple_problems:
            set_verbose_level(current_verbose_level)

        result = BenchmarkResult(
            problem_name=problem_name,
            success=success,
            plan_length=plan_length,
            execution_time=exec_time,
            resources=resources,
            error=error
        )
        self.results.append(result)

        if not multiple_problems:
            set_verbose_level(current_verbose_level)

        return result

def list_available_domains():
    """List available domains in the mcp-orchestration directory."""
    domains = []
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if (os.path.isdir(item_path) and
            os.path.exists(os.path.join(item_path, '__init__.py')) and
            os.path.exists(os.path.join(item_path, 'domain.py')) and
            os.path.exists(os.path.join(item_path, 'problems.py'))):
            domains.append(item)
    return sorted(domains)

def validate_domain_package(domain_name):
    """Validate that the specified domain exists in mcp-orchestration."""
    if not domain_name:
        return False
    domain_path = os.path.join(current_dir, domain_name)
    if not os.path.isdir(domain_path):
        return False
    required_files = ['__init__.py', 'domain.py', 'problems.py']
    for file_name in required_files:
        if not os.path.exists(os.path.join(domain_path, file_name)):
            return False
    return True

def main():
    """Main entry point for mcp-orchestration benchmarking."""
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.show_imports:
        print(f"GTPyhop import source: {gtpyhop_source}")
        return 0

    if args.list_domains:
        domains = list_available_domains()
        print("Available MCP orchestration domains:")
        for domain in domains:
            print(f"  - {domain}")
        return 0

    if not args.domain:
        print("Error: Domain argument is required")
        print("\nAvailable domains:")
        for domain in list_available_domains():
            print(f"  - {domain}")
        return 1

    domain_name = args.domain

    if not validate_domain_package(domain_name):
        print(f"Error: Domain '{domain_name}' not found or invalid")
        print("\nAvailable domains:")
        for domain in list_available_domains():
            print(f"  - {domain}")
        return 1

    print(f"Loading domain: {domain_name}")
    problems, domain_module = load_domain_package(domain_name)

    if not problems or domain_module is None:
        print(f"Error: No problems found in domain '{domain_name}'")
        return 1

    print(f"Found {len(problems)} problems in {domain_name}")

    if args.verbose > 0:
        set_verbose_level(args.verbose)

    use_sessions = not args.legacy_mode
    domain_obj = getattr(domain_module, 'the_domain', None)
    if use_sessions and domain_obj is None:
        print("WARNING: 'the_domain' not found. Falling back to legacy mode.")
        use_sessions = False

    benchmark = MCPBenchmark(
        domain=domain_obj if use_sessions else domain_module,
        verbose=True, use_sessions=use_sessions
    )

    # Normalize problems to (state, tasks) format, supporting optional description
    normalized_problems = {}
    for name, value in problems.items():
        if len(value) == 3:
            state, tasks, description = value
            normalized_problems[name] = (state, tasks)
        else:
            normalized_problems[name] = value

    planning_mode = "Thread-Safe Sessions" if use_sessions else "Legacy Global"
    print(f"\nRunning benchmarks for {domain_name} using {planning_mode} planning...")
    benchmark.run_multiple(normalized_problems, benchmarking_verbose=args.verbose)

    print(f"\n=== {domain_name} Benchmark Results ===")
    benchmark.print_summary(sort_by=args.sort_by)

    return 0

if __name__ == "__main__":
    sys.exit(main())

