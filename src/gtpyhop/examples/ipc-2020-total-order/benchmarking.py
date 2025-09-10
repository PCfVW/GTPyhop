"""
GTPyhop 1.4.0 Benchmarking System

A comprehensive benchmarking tool for evaluating GTPyhop planning performance
across different domains with resource tracking and detailed reporting.

Author: Eric Jacopin
Version: 4.0 (Production Ready)
"""

import time
import os
import sys
import gc
import argparse
import importlib
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple, Union
from contextlib import contextmanager

# === Configuration Constants ===
MIN_COLUMN_WIDTH = 6  # Minimum width for table columns
CPU_COUNT_DIVISOR = 1  # CPU percentage calculation divisor
GTPYHOP_LOCAL_PATH = os.path.join('..', '..', '..')  # Relative path to local GTPyhop

# === Import Management ===

def safe_add_to_path(relative_path: str) -> Optional[str]:
    """
    Safely add a relative path to sys.path with validation to prevent path traversal attacks.

    Args:
        relative_path: Relative path to add to sys.path

    Returns:
        The absolute path that was added, or None if validation failed

    Raises:
        ValueError: If path traversal is detected
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))

    # Validate the path is within expected boundaries to prevent path traversal
    if not target_path.startswith(os.path.dirname(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")

    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

def setup_gtpyhop_imports(verbose: bool = True) -> Tuple[bool, Optional[str], Optional[Tuple]]:
    """
    Single function to handle all GTPyhop imports and verification with security validation.

    Args:
        verbose: Whether to print status messages

    Returns:
        Tuple of (success, source, imports) where:
        - success: Boolean indicating if imports were successful
        - source: String indicating import source ("PyPI" or "Local")
        - imports: Tuple of imported modules or None if failed
    """
    try:
        # Try PyPI installation first (recommended approach)
        from gtpyhop import State, Multigoal, find_plan, set_verbose_level, get_verbose_level, PlannerSession
        if verbose:
            print("Using GTPyhop from PyPI installation")
        return True, "PyPI", (State, Multigoal, find_plan, set_verbose_level, get_verbose_level, PlannerSession)
    except ImportError:
        try:
            # Fallback to local development setup with secure path handling
            safe_add_to_path(GTPYHOP_LOCAL_PATH)
            from gtpyhop import State, Multigoal, find_plan, set_verbose_level, get_verbose_level, PlannerSession
            if verbose:
                print("Using GTPyhop from local development setup")
            return True, "Local", (State, Multigoal, find_plan, set_verbose_level, get_verbose_level, PlannerSession)
        except (ImportError, ValueError) as e:
            if verbose:
                print(f"Error: Could not import gtpyhop: {e}")
                print("Please install gtpyhop using: pip install gtpyhop")
                print("Or ensure the local gtpyhop source is available")
            return False, None, None

# Verify required modules are available
try:
    import psutil
except ImportError:
    print("Error: psutil module is required. Install with: pip install psutil")
    sys.exit(1)

# Setup GTPyhop imports with consolidated logic
gtpyhop_available, gtpyhop_source, gtpyhop_imports = setup_gtpyhop_imports()
if not gtpyhop_available:
    print("Error: GTPyhop is not available")
    print()
    print("Installation options:")
    print("1. PyPI installation (recommended):")
    print("   pip install gtpyhop")
    print()
    print("2. Local development setup:")
    print("   Ensure gtpyhop source code is available in the parent directory")
    print("   and properly structured")
    print()
    print("For most users, option 1 (pip install gtpyhop) is recommended")
    sys.exit(1)
else:
    print(f"GTPyhop loaded successfully from: {gtpyhop_source}")

# Extract imports from the tuple for global use
State, Multigoal, find_plan, set_verbose_level, get_verbose_level, PlannerSession = gtpyhop_imports

# === Domain Loading ===

def load_domain_package(domain_name: str) -> Tuple[Dict[str, Tuple[Any, Any]], Any]:
    """
    Load a domain package and return its problems and module using secure package-based imports.

    This function safely loads domain packages by validating paths and handling
    import errors gracefully. It supports both local and installed domain packages.

    Args:
        domain_name: Name of the domain folder (e.g., 'Blocksworld-GTOHP', 'Childsnack')

    Returns:
        Tuple of (problems_dict, domain_module) where:
        - problems_dict: Dictionary of {problem_name: (state, goal)} pairs
        - domain_module: The imported domain module
        Returns ({}, None) if loading fails

    Raises:
        No exceptions - all errors are caught and logged
    """
    try:
        # Safely add current directory to Python path for domain imports
        current_dir = os.path.dirname(__file__)
        safe_add_to_path('.')  # Add current directory securely

        # Import the domain package (preserving original name with hyphens)
        domain_package = importlib.import_module(domain_name)

        # Report which GTPyhop source the domain is using
        if hasattr(domain_package, 'GTPYHOP_SOURCE'):
            print(f"Domain {domain_name} using GTPyhop from: {domain_package.GTPYHOP_SOURCE}")

        # Get problems using the package's get_problems function
        if hasattr(domain_package, 'get_problems'):
            problems = domain_package.get_problems()
            print(f"Loaded {len(problems)} problems from {domain_name}")
            return problems, domain_package
        else:
            print(f"Warning: Domain package {domain_name} has no get_problems function")
            return {}, domain_package

    except ImportError as e:
        print(f"Error loading domain package {domain_name}: {e}")
        print("This might be due to missing GTPyhop installation or import issues")
        print("Try: pip install gtpyhop")
        return {}, None
    except Exception as e:
        print(f"Unexpected error loading domain {domain_name}: {e}")
        return {}, None

def validate_domain_package(domain_name: str) -> bool:
    """
    Validate that the specified domain exists as a package with required files.

    This function performs comprehensive validation of domain package structure
    to ensure all required files are present before attempting to load.

    Args:
        domain_name: Name of the domain to validate

    Returns:
        True if domain package is valid and complete, False otherwise
    """
    if not domain_name:
        return False

    # Construct domain path relative to current file location
    domain_path = os.path.join(os.path.dirname(__file__), domain_name)

    # Check if domain directory exists
    if not os.path.isdir(domain_path):
        return False

    # Verify all required files are present
    required_files = ['__init__.py', 'domain.py', 'problems.py']
    for file_name in required_files:
        if not os.path.exists(os.path.join(domain_path, file_name)):
            return False

    return True

# === Data Structures ===

@dataclass
class ResourceUsage:
    """
    Track comprehensive resource usage metrics during planning execution.

    Attributes:
        cpu_percent: CPU usage percentage during execution
        memory_kb: Memory delta in kilobytes (change from start to end)
        peak_memory_kb: Peak memory usage in kilobytes during execution
    """
    cpu_percent: float = 0.0
    memory_kb: float = 0.0
    peak_memory_kb: float = 0.0

@dataclass
class BenchmarkResult:
    """
    Comprehensive result data for a single benchmark execution.

    Attributes:
        problem_name: Unique identifier for the problem instance
        plan_length: Number of actions in the solution plan (None if failed)
        execution_time: Total execution time in seconds
        success: Boolean indicating whether planning succeeded
        resources: Resource usage metrics during execution
        error: Error message if planning failed (None if successful)
    """
    problem_name: str
    plan_length: Optional[int]
    execution_time: float
    success: bool
    resources: ResourceUsage = field(default_factory=ResourceUsage)
    error: Optional[str] = None

# === Domain Abstraction ===

class DomainHandler:
    """
    Abstract handler for domain-specific planning logic.

    This class encapsulates domain-specific knowledge to remove hard-coded
    logic from the generic benchmark class.
    """

    @staticmethod
    def create_multigoal(problem_name: str, goal: Dict[str, Any]) -> Any:
        """
        Create appropriate multigoal object based on domain type.

        Args:
            problem_name: Name of the problem to determine domain type
            goal: Goal dictionary to be converted to multigoal

        Returns:
            Configured Multigoal object appropriate for the domain
        """
        multigoal = Multigoal(f"goal_{problem_name}")

        # Domain-specific attribute assignment based on problem name
        if "childsnack" in problem_name.lower():
            multigoal.served = goal  # Childsnack uses 'served' attribute
        else:
            multigoal.on = goal      # Blocksworld uses 'on' attribute

        return multigoal

# === Benchmarking Engine ===

class PlannerBenchmark:
    """
    Comprehensive benchmarking system for GTPyhop planning performance evaluation.

    This class provides sophisticated resource tracking, execution monitoring,
    and result analysis capabilities for planning domain benchmarks using
    GTPyhop 1.3.0's thread-safe session-based architecture.
    """

    def __init__(self, domain: Any, verbose: bool = False, use_sessions: bool = True):
        """
        Initialize the benchmark system with thread-safe session support.

        Args:
            domain: The planning domain to use for benchmarking
            verbose: Whether to print detailed execution information
            use_sessions: Whether to use thread-safe PlannerSession (recommended)
        """
        self.domain = domain
        self.verbose = verbose
        self.use_sessions = use_sessions
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process(os.getpid())
        self.domain_handler = DomainHandler()

        # Legacy support: keep planner function for backward compatibility
        self.planner = find_plan if not use_sessions else None

    def _get_memory_usage(self) -> Tuple[float, float]:
        """
        Get current and peak memory usage in KB with forced garbage collection.

        This method ensures accurate memory measurements by forcing garbage
        collection before measurement and handling platform-specific differences.

        Returns:
            Tuple of (current_memory_kb, peak_memory_kb)
        """
        # Force garbage collection before measuring memory for accuracy
        gc.collect()

        process = self.process
        mem_info = process.memory_full_info()

        # Convert to KB for better precision (1 KB = 1024 bytes)
        current_kb = mem_info.rss / 1024.0  # Resident Set Size in KB

        # Platform-specific peak memory handling
        if sys.platform == 'win32':
            peak_kb = mem_info.peak_wset / 1024.0  # Windows: use peak working set
        else:
            peak_kb = mem_info.rss / 1024.0  # Unix: use RSS as fallback

        return current_kb, max(peak_kb, current_kb)  # Ensure peak >= current

    def _calculate_resource_metrics(self, start_time: float, start_mem: float) -> Tuple[float, ResourceUsage]:
        """
        Calculate execution time and resource usage metrics.

        This helper method eliminates code duplication in resource tracking
        by centralizing the calculation logic.

        Args:
            start_time: Starting timestamp from perf_counter()
            start_mem: Starting memory usage in KB

        Returns:
            Tuple of (execution_time, ResourceUsage object)
        """
        exec_time = time.perf_counter() - start_time
        current_mem, peak_mem = self._get_memory_usage()
        cpu_percent = self.process.cpu_percent(interval=None) / psutil.cpu_count()

        resources = ResourceUsage(
            cpu_percent=round(cpu_percent, 2),
            memory_kb=round(current_mem - start_mem, 1),  # Memory delta in KB
            peak_memory_kb=round(peak_mem, 1)  # Peak memory in KB
        )

        return exec_time, resources

    @contextmanager
    def track_resources(self):
        """
        Context manager to track CPU and memory usage during planning execution.

        This context manager provides comprehensive resource monitoring with
        accurate measurements and proper cleanup handling.

        Yields:
            ResourceTracker object with execution metrics
        """
        class ResourceTracker:
            """Internal tracker class to hold execution metrics."""
            def __init__(self):
                self.exec_time = 0
                self.resources = ResourceUsage()

        # Force garbage collection before starting measurements for accuracy
        gc.collect()

        tracker = ResourceTracker()

        # Capture initial state for delta calculations
        start_mem, _ = self._get_memory_usage()
        start_time = time.perf_counter()

        # Initialize CPU monitoring (first call returns 0.0)
        self.process.cpu_percent(interval=None)

        try:
            # Yield control to the benchmarked code
            yield tracker

            # Calculate metrics after successful execution
            tracker.exec_time, tracker.resources = self._calculate_resource_metrics(start_time, start_mem)

        except Exception as e:
            # Ensure metrics are captured even if execution fails
            tracker.exec_time, tracker.resources = self._calculate_resource_metrics(start_time, start_mem)
            raise  # Re-raise the exception after capturing metrics

    def run_single(self, problem_name: str, state: Any, goal: Any,
                   benchmarking_verbose: int = 0, multiple_problems: bool = False) -> BenchmarkResult:
        """
        Execute a single planning problem and collect comprehensive metrics.

        This method handles the complete lifecycle of a single benchmark execution,
        including resource tracking, error handling, and result compilation.

        Args:
            problem_name: Unique identifier for the problem instance
            state: Initial state for the planning problem
            goal: Goal specification for the planning problem
            benchmarking_verbose: Verbosity level for planning output
            multiple_problems: Whether this is part of a batch execution

        Returns:
            BenchmarkResult object with complete execution metrics
        """
        if self.verbose:
            print(f"Solving {problem_name}...")

        # Manage verbosity level for single problem execution
        if not multiple_problems:
            current_verbose_level = get_verbose_level()
            set_verbose_level(benchmarking_verbose)

        # Initialize result variables with safe defaults
        plan = None
        resources = ResourceUsage()
        error = None
        exec_time = 0.0

        try:
            # Execute planning with comprehensive resource tracking
            with self.track_resources() as tracker:
                if self.use_sessions:
                    # Use thread-safe session-based planning (GTPyhop 1.3.0+)
                    session_verbose = benchmarking_verbose if not multiple_problems else 0
                    with PlannerSession(domain=self.domain, verbose=session_verbose) as session:
                        with session.isolated_execution():
                            # Use domain handler for goal conversion
                            if isinstance(goal, dict):
                                multigoal = self.domain_handler.create_multigoal(problem_name, goal)
                                result = session.find_plan(state, [multigoal])
                            else:
                                # Fallback for non-dictionary goals (future extensibility)
                                result = session.find_plan(state, [goal])

                            # Extract plan from session result
                            plan = result.plan if (result and result.success) else None
                else:
                    # Legacy mode: use global find_plan function
                    if isinstance(goal, dict):
                        multigoal = self.domain_handler.create_multigoal(problem_name, goal)
                        plan = self.planner(state, [multigoal])
                    else:
                        # Fallback for non-dictionary goals (future extensibility)
                        plan = self.planner(state, [goal])

            # Extract metrics from tracker (guaranteed to exist after context exit)
            exec_time = tracker.exec_time
            resources = tracker.resources

            # Determine success and plan length with robust checking
            success = plan is not False and plan is not None
            plan_length = len(plan) if success else None

        except Exception as e:
            # Simplified exception handling with clear error reporting
            print(f"[ERROR] Planning failed for {problem_name}: {str(e)}")
            error = str(e)
            success = False
            plan_length = None
            # Note: exec_time and resources retain values from tracker if available

        # Create comprehensive result object
        result = BenchmarkResult(
            problem_name=problem_name,
            plan_length=plan_length,
            execution_time=exec_time,
            success=success,
            error=error,
            resources=resources
        )

        # Store result for batch analysis
        self.results.append(result)

        # Restore verbosity level for single problem execution
        if not multiple_problems:
            set_verbose_level(current_verbose_level)

        return result

    def run_multiple(self, problems: Dict[str, Tuple[Any, Any]], benchmarking_verbose: int = 0) -> List[BenchmarkResult]:
        """
        Execute multiple planning problems in batch mode with consistent verbosity.

        This method efficiently processes multiple problems while maintaining
        consistent verbosity settings and providing batch execution optimizations.

        Args:
            problems: Dictionary mapping problem names to (state, goal) tuples
            benchmarking_verbose: Verbosity level for all planning executions

        Returns:
            List of BenchmarkResult objects for all executed problems
        """
        # Set consistent verbosity for batch execution
        current_verbose_level = get_verbose_level()
        set_verbose_level(benchmarking_verbose)

        # Execute all problems with batch optimization flag
        for name, (state, goal) in problems.items():
            self.run_single(name, state, goal, benchmarking_verbose, multiple_problems=True)

        # Restore original verbosity level
        set_verbose_level(current_verbose_level)
        return self.results

    def print_summary(self, sort_by: str = 'time') -> None:
        """
        Print comprehensive benchmark summary with dynamic formatting and sorting.

        This method generates a professional table display with automatic column
        width adjustment and multiple sorting options for result analysis.

        Args:
            sort_by: Sorting criteria ('time', 'memory', or 'name')
        """
        # Apply requested sorting to results
        if sort_by == 'time':
            sorted_results = sorted(self.results, key=lambda x: x.execution_time)
        elif sort_by == 'memory':
            sorted_results = sorted(self.results, key=lambda x: x.resources.peak_memory_kb)
        elif sort_by == 'name':
            sorted_results = sorted(self.results, key=lambda x: x.problem_name)
        else:
            sorted_results = self.results

        # Calculate optimal column widths based on actual content
        widths = self._calculate_column_widths(sorted_results)

        print("\n=== Benchmark Summary ===")

        # Generate header with dynamic column widths
        header = (
            f"{'Problem':<{widths['problem']}} | "
            f"{'Status':<{widths['status']}} | "
            f"{'Plan Len':>{widths['plan_len']}} | "
            f"{'Time (s)':>{widths['time']}} | "
            f"{'CPU %':>{widths['cpu']}} | "
            f"{'Mem Δ (KB)':>{widths['mem_delta']}} | "
            f"{'Peak Mem (KB)':>{widths['peak_mem']}}"
        )
        print(header)

        # Generate separator line that exactly matches header width
        separator_width = len(header)
        print("-" * separator_width)

        # Generate data rows with consistent formatting
        for result in sorted_results:
            # Format status with appropriate emoji and error information
            status = "✅" if result.success else f"❌ ({result.error})"
            length = str(result.plan_length) if result.plan_length is not None else "N/A"

            # Build row with precise column alignment
            row = (
                f"{result.problem_name:<{widths['problem']}} | "
                f"{status:<{widths['status']}} | "
                f"{length:>{widths['plan_len']}} | "
                f"{result.execution_time:>{widths['time']}.3f}s | "
                f"{result.resources.cpu_percent:>{widths['cpu']}.1f}% | "
                f"{result.resources.memory_kb:>{widths['mem_delta']}.1f} | "
                f"{result.resources.peak_memory_kb:>{widths['peak_mem']}.1f}"
            )
            print(row)

    def _calculate_column_widths(self, results: List[BenchmarkResult]) -> Dict[str, int]:
        """
        Calculate optimal column widths based on actual content for perfect table alignment.

        This method analyzes all data that will be displayed to determine the minimum
        width required for each column, ensuring proper alignment regardless of content.

        Args:
            results: List of benchmark results to analyze

        Returns:
            Dictionary mapping column names to their optimal widths
        """
        # Initialize with header widths as baseline minimum
        widths = {
            'problem': len('Problem'),
            'status': len('Status'),
            'plan_len': len('Plan Len'),
            'time': len('Time (s)'),
            'cpu': len('CPU %'),
            'mem_delta': len('Mem Δ (KB)'),
            'peak_mem': len('Peak Mem (KB)')
        }

        # Analyze each result to find maximum width requirements
        for result in results:
            # Problem name width (varies significantly between domains)
            widths['problem'] = max(widths['problem'], len(result.problem_name))

            # Status width (account for both success ✅ and failure ❌ (error) formats)
            status = "✅" if result.success else f"❌ ({result.error})"
            widths['status'] = max(widths['status'], len(status))

            # Plan length width (handles both numeric values and "N/A")
            length_str = str(result.plan_length) if result.plan_length is not None else "N/A"
            widths['plan_len'] = max(widths['plan_len'], len(length_str))

            # Execution time width (format: X.XXXs with 3 decimal places)
            time_str = f"{result.execution_time:.3f}s"
            widths['time'] = max(widths['time'], len(time_str))

            # CPU percentage width (format: XX.X% with 1 decimal place)
            cpu_str = f"{result.resources.cpu_percent:.1f}%"
            widths['cpu'] = max(widths['cpu'], len(cpu_str))

            # Memory delta width (format: XXXX.X with 1 decimal place)
            mem_delta_str = f"{result.resources.memory_kb:.1f}"
            widths['mem_delta'] = max(widths['mem_delta'], len(mem_delta_str))

            # Peak memory width (format: XXXXX.X with 1 decimal place)
            peak_mem_str = f"{result.resources.peak_memory_kb:.1f}"
            widths['peak_mem'] = max(widths['peak_mem'], len(peak_mem_str))

        # Apply minimum width constraint for readability
        for key in widths:
            widths[key] = max(widths[key], MIN_COLUMN_WIDTH)

        return widths

# === Command Line Interface ===

def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the comprehensive command-line argument parser.

    This function sets up all command-line options with detailed help text
    and usage examples for optimal user experience.

    Returns:
        Configured ArgumentParser object ready for parsing
    """
    parser = argparse.ArgumentParser(
        description='Run GTPyhop benchmarks on different planning domains',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmarking.py Blocksworld-GTOHP    # Run Blocksworld benchmarks
  python benchmarking.py Childsnack           # Run Childsnack benchmarks
  python benchmarking.py --list-domains       # List available domains

Installation:
  pip install gtpyhop psutil                  # Install required dependencies
        """
    )

    # Primary domain argument
    parser.add_argument(
        'domain',
        nargs='?',
        help='Domain to benchmark (Blocksworld-GTOHP, Childsnack)'
    )

    # Domain discovery option
    parser.add_argument(
        '--list-domains',
        action='store_true',
        help='List available domains and exit'
    )

    # Planning verbosity control
    parser.add_argument(
        '--verbose',
        type=int,
        default=0,
        choices=[0, 1, 2, 3],
        help='Verbosity level for planning (0-3, default: 0)'
    )

    # Result sorting options
    parser.add_argument(
        '--sort-by',
        choices=['time', 'memory', 'name'],
        default='time',
        help='Sort results by time, memory usage, or problem name (default: time)'
    )

    # Import debugging option
    parser.add_argument(
        '--show-imports',
        action='store_true',
        help='Show which GTPyhop import method is being used'
    )

    parser.add_argument(
        '--legacy-mode',
        action='store_true',
        help='Use legacy global find_plan instead of thread-safe sessions (not recommended)'
    )

    return parser

def list_available_domains() -> List[str]:
    """
    Discover and list all available domain packages in the current directory.

    This function scans the current directory for valid domain packages by
    checking for the presence of required files (__init__.py, domain.py, problems.py).

    Returns:
        Sorted list of available domain names
    """
    base_dir = os.path.dirname(__file__)
    domains = []

    # Scan directory for valid domain packages
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)

        # Check if item is a directory with required domain files
        if (os.path.isdir(item_path) and
            os.path.exists(os.path.join(item_path, '__init__.py')) and
            os.path.exists(os.path.join(item_path, 'domain.py')) and
            os.path.exists(os.path.join(item_path, 'problems.py'))):
            domains.append(item)

    return sorted(domains)

# === Main Execution ===

def main() -> int:
    """
    Main function to handle command-line execution and orchestrate benchmarking.

    This function provides the primary entry point for the benchmarking system,
    handling argument parsing, domain validation, and benchmark execution.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    # Handle import information request
    if args.show_imports:
        # Use the already established import source information
        print(f"GTPyhop import source: {gtpyhop_source}")
        return 0

    # Handle domain listing request
    if args.list_domains:
        domains = list_available_domains()
        print("Available domains:")
        for domain in domains:
            print(f"  - {domain}")
        return 0

    # Validate required domain argument
    if not args.domain:
        print("Error: Domain argument is required")
        parser.print_help()
        return 1

    # Handle legacy domain name inconsistency for backward compatibility
    domain_name = args.domain
    if domain_name == "Blocksworld-GTHOP":
        print("Note: Correcting domain name from 'Blocksworld-GTHOP' to 'Blocksworld-GTOHP'")
        domain_name = "Blocksworld-GTOHP"

    # Validate domain package exists and is complete
    if not validate_domain_package(domain_name):
        available_domains = list_available_domains()
        print(f"Error: Domain '{domain_name}' not found or invalid")
        print("Available domains:")
        for domain in available_domains:
            print(f"  - {domain}")
        return 1

    # Load domain problems with comprehensive error handling
    print(f"Loading domain: {domain_name}")
    problems, domain_module = load_domain_package(domain_name)

    if not problems or domain_module is None:
        print(f"Error: No problems found in domain '{domain_name}'")
        print("This might be due to missing GTPyhop installation")
        print("Try: pip install gtpyhop")
        return 1

    print(f"Found {len(problems)} problems in {domain_name}")

    # Configure planning verbosity if requested (for legacy mode only)
    if args.verbose > 0:
        set_verbose_level(args.verbose)

    # Initialize benchmark system with session support (default: thread-safe sessions)
    use_sessions = not args.legacy_mode
    if args.legacy_mode:
        print("⚠️  WARNING: Using legacy mode. Thread-safe sessions are recommended for production use.")

    # Extract the domain object from the module for session-based planning
    domain_obj = getattr(domain_module, 'the_domain', None)
    if use_sessions and domain_obj is None:
        print("⚠️  WARNING: Domain object 'the_domain' not found. Falling back to legacy mode.")
        use_sessions = False

    benchmark = PlannerBenchmark(domain=domain_obj if use_sessions else domain_module,
                                verbose=True, use_sessions=use_sessions)

    # Execute benchmark suite
    planning_mode = "Thread-Safe Sessions" if use_sessions else "Legacy Global"
    print(f"\nRunning benchmarks for {domain_name} using {planning_mode} planning...")
    benchmark.run_multiple(problems, benchmarking_verbose=args.verbose)

    # Display primary results with requested sorting
    print(f"\n=== {domain_name} Benchmark Results ===")
    benchmark.print_summary(sort_by=args.sort_by)

    # Provide additional memory-sorted view if not already shown
    if args.sort_by != 'memory':
        print(f"\n=== {domain_name} Results Sorted by Peak Memory Usage ===")
        benchmark.print_summary(sort_by='memory')

    return 0

if __name__ == "__main__":
    sys.exit(main())