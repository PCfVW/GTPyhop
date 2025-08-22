"""
Some examples that show GTPyhop backtracking through several methods and tasks.
-- Dana Nau <nau@umd.edu>, July 20, 2021

Updated for GTPyhop 1.3.0 thread-safe sessions - 2025-08-22
"""

import gtpyhop
import argparse

import gtpyhop.test_harness as th   # code for use in paging and debugging

# Import the function to check if recursive planning is enabled
try:
    from src.gtpyhop.main import get_recursive_planning
except ImportError:
    # Fallback for different import paths
    try:
        from gtpyhop.main import get_recursive_planning
    except ImportError:
        # If we can't import it, assume recursive planning is available
        def get_recursive_planning():
            return True

# Rather than hard-coding the domain name, use the name of the current file.
# This makes the code more portable.
domain_name = __name__
the_domain = gtpyhop.Domain(domain_name)

###############################################################################
# States:

state0 = gtpyhop.State('state0')
state0.flag = -1


###############################################################################
# Methods:


def m_err(state):
    return [('putv', 0), ('getv', 1)]

def m0(state):
    return [('putv', 0), ('getv', 0)]

def m1(state):
    return [('putv', 1), ('getv', 1)]

gtpyhop.declare_task_methods('put_it',m_err,m0,m1)


def m_need0(state):
    return [('getv', 0)]

def m_need1(state):
    return [('getv', 1)]

gtpyhop.declare_task_methods('need0',m_need0)

gtpyhop.declare_task_methods('need1',m_need1)

gtpyhop.declare_task_methods('need01',m_need0,m_need1)

gtpyhop.declare_task_methods('need10',m_need1,m_need0)

###############################################################################
# Actions:

def putv(state,flag_val):
    state.flag = flag_val
    return state

def getv(state,flag_val):
    if state.flag == flag_val:
        return state

gtpyhop.declare_actions(putv,getv)

###############################################################################
# Problem:


###############################################################################
# Running the examples

print('-----------------------------------------------------------------------')
print(f"Created the domain '{domain_name}'. To run the examples, type this:")
print(f"{domain_name}.main()")

def main(do_pauses=True):
    """
    Run various examples.
    main() will pause occasionally to let you examine the output.
    main(False) will run straight through to the end, without stopping.
    """
    # Legacy mode - preserved for backward compatibility
    main_legacy(do_pauses)


def main_legacy(do_pauses=True):
    """
    Legacy implementation using global state (preserved for backward compatibility).
    """
    # Check if recursive planning is enabled - backtracking only works with recursive planning
    if not get_recursive_planning():
        print("Backtracking examples require recursive planning, but iterative planning is currently enabled.")
        print("Skipping backtracking examples.")
        return

    # If we've changed to some other domain, this will change us back.
    gtpyhop.current_domain = the_domain
    gtpyhop.print_domain()

    state1 = state0.copy()

    state1.display(heading='\nInitial state is')

    # two possible expected answers for check_result
    expect0 = [('putv', 0), ('getv', 0), ('getv', 0)]
    expect1 = [('putv', 1), ('getv', 1), ('getv', 1)]

    print("Next are some example problems with verbose=3 in order to see the backtracking.\n")
    gtpyhop.verbose = 3
    th.pause(do_pauses)

    print("""Below, seek_plan backtracks once to use a different method for 'put_it'.
""")

    # The comma after each task name is to make Python parse it as a tuple, not an atom
    result = gtpyhop.find_plan(state0,[('put_it',),('need0',)])
    th.check_result(result,expect0)
    th.pause(do_pauses)

    print("""The backtracking in this example is the same as in the first one.
""")
    result = gtpyhop.find_plan(state0,[('put_it',),('need01',)])
    th.check_result(result,expect0)
    th.pause(do_pauses)

    print("""Below, seek_plan backtracks to use a different method for 'put_it',
and later it backtracks to use a different method for 'need10'.
""")
    result = gtpyhop.find_plan(state0,[('put_it',),('need10',)])
    th.check_result(result,expect0)
    th.pause(do_pauses)

    print("""First, seek_plan backtracks to use a different method for 'put_it'. But the
solution it finds for 'put_it' doesn't satisfy the preconditions of the
method for 'need1', making it backtrack to use a third method for 'put_it'.
""")
    result = gtpyhop.find_plan(state0,[('put_it',),('need1',)])
    th.check_result(result,expect1)

    print("No more examples")


def main_session(do_pauses=True, verbose=3):
    """
    Thread-safe implementation using PlannerSession (GTPyhop 1.3.0+).
    """
    print(f"\n=== Running backtracking_htn examples with PlannerSession (verbose={verbose}) ===")

    # Check if recursive planning is enabled - backtracking only works with recursive planning
    if not get_recursive_planning():
        print("Backtracking examples require recursive planning, but iterative planning is currently enabled.")
        print("Skipping backtracking examples.")
        return

    state1 = state0.copy()
    state1.display(heading='\nInitial state is')

    # two possible expected answers for check_result
    expect0 = [('putv', 0), ('getv', 0), ('getv', 0)]
    expect1 = [('putv', 1), ('getv', 1), ('getv', 1)]

    print("Next are some example problems with verbose=3 in order to see the backtracking.\n")
    th.pause(do_pauses)

    print("""Below, session.find_plan backtracks once to use a different method for 'put_it'.
""")

    # The comma after each task name is to make Python parse it as a tuple, not an atom
    with gtpyhop.PlannerSession(domain=the_domain, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state0, [('put_it',),('need0',)])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expect0)
    th.pause(do_pauses)

    print("""The backtracking in this example is the same as in the first one.
""")
    with gtpyhop.PlannerSession(domain=the_domain, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state0, [('put_it',),('need01',)])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expect0)
    th.pause(do_pauses)

    print("""Below, session.find_plan backtracks to use a different method for 'put_it',
and later it backtracks to use a different method for 'need10'.
""")
    with gtpyhop.PlannerSession(domain=the_domain, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state0, [('put_it',),('need10',)])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expect0)
    th.pause(do_pauses)

    print("""First, session.find_plan backtracks to use a different method for 'put_it'. But the
solution it finds for 'put_it' doesn't satisfy the preconditions of the
method for 'need1', making it backtrack to use a third method for 'put_it'.
""")
    with gtpyhop.PlannerSession(domain=the_domain, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state0, [('put_it',),('need1',)])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expect1)

    print("No more examples")


def main_with_args(argv=None):
    """
    Main function with command-line argument support for choosing execution mode.
    """
    parser = argparse.ArgumentParser(description="Run backtracking_htn examples")
    parser.add_argument("--session", action="store_true",
                       help="Run using PlannerSession (thread-safe)")
    parser.add_argument("--verbose", type=int, default=3,
                       help="Verbosity level for session runs (0-3)")
    parser.add_argument("--no-pauses", action="store_true",
                       help="Run without pauses")

    args = parser.parse_args(argv)
    do_pauses = not args.no_pauses

    if args.session:
        main_session(do_pauses, args.verbose)
    else:
        main_legacy(do_pauses)


if __name__ == "__main__":
    main_with_args()