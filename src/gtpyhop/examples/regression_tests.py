"""
The following code runs GTPyhop on all but one of the example domains, to
see whether they run without error and return correct answers. The
2nd-to-last line imports simple_htn_acting_error but doesn't run it,
because running it is *supposed* to cause an error.

-- Dana Nau <nau@umd.edu>, July 20, 2021

Updated for GTPyhop 1.3.0 thread-safe sessions - 2025-08-22
"""

import argparse


def main():
    """
    Run all the regression tests (legacy mode).
    """
    # Legacy mode - preserved for backward compatibility
    main_legacy()


def main_legacy():
    """
    Legacy implementation using global state (preserved for backward compatibility).
    """
    print("=== Running regression tests in LEGACY mode ===")

    # The argument False tells the test harness not to stop for user input
    from gtpyhop.examples import simple_htn; simple_htn.main_legacy(False)
    from gtpyhop.examples import simple_hgn; simple_hgn.main_legacy(False)

    # skip testing the recursive backtracking when planning is iterative
    from src.gtpyhop.main import get_recursive_planning
    if get_recursive_planning():
         from gtpyhop.examples import backtracking_htn; backtracking_htn.main(False)

    from gtpyhop.examples import logistics_hgn; logistics_hgn.main(False)

    # Python recursion limit is set to 1000 by default which is:
    #  - not enough for both blocks_gtn and blocks_hgn examples,
    #  - enough for blocks_goal_splitting, and blocks_htn examples.
    if get_recursive_planning():
        import sys
        current_recursion_limit = sys.getrecursionlimit()
        blocks_gtn_recursion_limit = 2000
        # Increase recursion limit for blocks_gtn test if needed
        if current_recursion_limit < blocks_gtn_recursion_limit:
            sys.setrecursionlimit(blocks_gtn_recursion_limit)  # Increase recursion limit for the next test
            print(f"Recursion limit set to {blocks_gtn_recursion_limit} for blocks_gtn test.")

    # With an appropriate recursion limit, next 2 tests should run without error
    # Of course, if we're running with iterative planning, we don't need to increase the recursion limit.
    from gtpyhop.examples import blocks_gtn; blocks_gtn.main(False)
    from gtpyhop.examples import blocks_hgn; blocks_hgn.main(False)

    # Restore the original recursion limit after the test if needed
    if get_recursive_planning():
        if current_recursion_limit < blocks_gtn_recursion_limit:
            sys.setrecursionlimit(current_recursion_limit)
            print(f"Recursion limit restored to {current_recursion_limit} after blocks_gtn test.")

    from gtpyhop.examples import blocks_goal_splitting; blocks_goal_splitting.main(False)
    from gtpyhop.examples import blocks_htn; blocks_htn.main(False)
    from gtpyhop.examples import pyhop_simple_travel_example
    from gtpyhop.examples import simple_htn_acting_error
    print('\nFinished without error.')


def main_session():
    """
    Thread-safe implementation using PlannerSession (GTPyhop 1.3.0+).
    """
    import subprocess
    import sys

    print("=== Running regression tests in SESSION mode ===")

    # List of examples to test in session mode with their specific arguments
    examples_to_test = [
        # Simple examples (now migrated)
        ('gtpyhop.examples.simple_htn', ['--session', '--no-pauses']),
        ('gtpyhop.examples.simple_hgn', ['--session', '--no-pauses']),
        ('gtpyhop.examples.backtracking_htn', ['--session', '--no-pauses']),
        ('gtpyhop.examples.logistics_hgn', ['--session', '--no-pauses']),
        ('gtpyhop.examples.blocks_gtn.examples', ['--session', '--no-pauses']),
        ('gtpyhop.examples.blocks_hgn.examples', ['--session', '--no-pauses']),
        ('gtpyhop.examples.blocks_goal_splitting.examples', ['--session', '--no-pauses']),
        ('gtpyhop.examples.blocks_htn.examples', ['--session', '--no-pauses']),
        ('gtpyhop.examples.pyhop_simple_travel_example', ['--session']),  # No --no-pauses for this one
        ('gtpyhop.examples.simple_htn_acting_error', ['--session', '--no-pauses'])
    ]

    # Skip backtracking if not using recursive planning
    from src.gtpyhop.main import get_recursive_planning
    if not get_recursive_planning():
        examples_to_test = [ex for ex in examples_to_test if ex[0] != 'gtpyhop.examples.backtracking_htn']

    for example, args in examples_to_test:
        print(f"\n--- Testing {example} ---")
        try:
            result = subprocess.run([
                sys.executable, '-m', example
            ] + args, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print(f"ERROR: {example} failed with return code {result.returncode}")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                raise RuntimeError(f"Test failed for {example}")
            else:
                print(f"SUCCESS: {example} completed successfully")
        except subprocess.TimeoutExpired:
            print(f"ERROR: {example} timed out")
            raise RuntimeError(f"Test timed out for {example}")
        except Exception as e:
            print(f"ERROR: {example} failed with exception: {e}")
            raise

    print('\nFinished without error.')


def main_with_args(argv=None):
    """
    Main function with command-line argument support for choosing execution mode.
    """
    parser = argparse.ArgumentParser(description="Run regression tests")
    parser.add_argument("--session", action="store_true",
                       help="Run using PlannerSession (thread-safe)")

    args = parser.parse_args(argv)

    if args.session:
        main_session()
    else:
        main_legacy()


if __name__ == "__main__":
    main_with_args()
