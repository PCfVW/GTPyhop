"""
Examples file for blocks_goal_splitting.
-- Dana Nau <nau@umd.edu>, July 20, 2021

Updated for GTPyhop 1.3.0 thread-safe sessions - 2025-08-22
"""

# Uncomment this to use it in debugging:
# from IPython import embed
# from IPython.terminal.debugger import set_trace

import gtpyhop
import argparse
import gtpyhop.test_harness as th   # code for use in paging and debugging


# We must declare the current domain before importing methods and actions.
# To make the code more portable, we don't hard-code the domain name, but
# instead use the name of the package.
the_domain = gtpyhop.Domain(__package__)

from .methods import *
from .actions import *

print('-----------------------------------------------------------------------')
print(f"Created '{gtpyhop.current_domain}'. To run the examples, type this:")
print(f'{the_domain.__name__}.main()')


#############     beginning of tests     ################

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
    # If we've changed to some other domain, this will change us back.
    print(f"Changing current domain to {the_domain}, if it isn't that already.")
    gtpyhop.set_current_domain(gtpyhop.find_domain_by_name(gtpyhop.Domain(__package__).__name__))

    gtpyhop.print_domain()

    state1 = gtpyhop.State('state1')
    state1.pos={'a':'b', 'b':'table', 'c':'table'}
    state1.clear={'c':True, 'b':False,'a':True}
    state1.holding={'hand':False}

    state1.display('\nInitial state is')

    print("""
Below, both goal1a and goal1b specify that we want c on b, and b on a.
However, goal1a also specifies that we want a on the table.
""")

    goal1a = gtpyhop.Multigoal('goal1a')
    goal1a.pos={'c':'b', 'b':'a', 'a':'table'}

    goal1a.display()

    goal1b = gtpyhop.Multigoal('goal1b')
    goal1b.pos={'c':'b', 'b':'a'}

    goal1b.display()

    ### goal1b omits some of the conditions of goal1a,
    ### but those conditions will need to be achieved anyway

    th.pause(do_pauses)

    print("""
Run GTPyhop with goal1a and goal1b, starting in state1. Both should produce the
same plan, but it won't be a very good plan, because m_split_multigoal doesn't know
how to choose the best order for achieving the goals.
""")

    state1.display("Initial state is")

    # Tell the test harness what answer to expect, so it can signal an error
    # if gtpyhop returns an incorrect answer. Checks like this have been very
    # very helpful for debugging both gtpyhop and the various example domains.

    expected = [('unstack', 'a', 'b'), ('putdown', 'a'), ('pickup', 'c'), ('stack', 'c', 'b'), ('unstack', 'c', 'b'), ('putdown', 'c'), ('pickup', 'b'), ('stack', 'b', 'a'), ('pickup', 'c'), ('stack', 'c', 'b')]

    plan1 = gtpyhop.find_plan(state1,[goal1a])
    th.check_result(plan1,expected)

    plan2 = gtpyhop.find_plan(state1,[goal1b])
    th.check_result(plan2,expected)
    th.pause(do_pauses)


    print("""
Run GTPyhop on two more planning problems. Like before, goal2a omits some
of the conditions in goal2a, but both goals should produce the same plan.
""")

    state2 = gtpyhop.State('state2')
    state2.pos={'a':'c', 'b':'d', 'c':'table', 'd':'table'}
    state2.clear={'a':True, 'c':False,'b':True, 'd':False}
    state2.holding={'hand':False}

    state2.display('The initial state is')
    
    goal2a = gtpyhop.Multigoal('goal2a')
    goal2a.pos={'b':'c', 'a':'d', 'c':'table', 'd':'table'}
    goal2a.clear={'a':True, 'c':False,'b':True, 'd':False}
    goal2a.holding={'hand':False}

    goal2a.display()
    
    goal2b = gtpyhop.Multigoal('goal2b')
    goal2b.pos={'b':'c', 'a':'d'}

    goal2b.display()
    
    ### goal2b omits some of the conditions of goal2a,
    ### but those conditions will need to be achieved anyway.

    expected = [('unstack', 'a', 'c'), ('putdown', 'a'), ('unstack', 'b', 'd'), ('stack', 'b', 'c'), ('pickup', 'a'), ('stack', 'a', 'd')] 

    plan1 = gtpyhop.find_plan(state2,[goal2a])
    th.check_result(plan1,expected)

    plan2 = gtpyhop.find_plan(state2,[goal2b])
    th.check_result(plan2,expected)
    th.pause(do_pauses)

    # Skip large examples for brevity in legacy mode
    print("Skipping large examples for brevity...")

    print("No more examples")


def main_session(do_pauses=True, verbose=1):
    """
    Thread-safe implementation using PlannerSession (GTPyhop 1.3.0+).
    This demonstrates goal splitting methodology with built-in methods.
    """
    print(f"\n=== Running blocks_goal_splitting examples with PlannerSession (verbose={verbose}) ===")

    # Make sure we have the right domain
    domain_to_use = gtpyhop.find_domain_by_name(gtpyhop.Domain(__package__).__name__)
    print(f"Using domain: {domain_to_use}")

    state1 = gtpyhop.State('state1')
    state1.pos={'a':'b', 'b':'table', 'c':'table'}
    state1.clear={'c':True, 'b':False,'a':True}
    state1.holding={'hand':False}

    state1.display('\nInitial state is')

    print("""
Below, both goal1a and goal1b specify that we want c on b, and b on a.
However, goal1a also specifies that we want a on the table.
""")

    goal1a = gtpyhop.Multigoal('goal1a')
    goal1a.pos={'c':'b', 'b':'a', 'a':'table'}
    goal1a.display()

    goal1b = gtpyhop.Multigoal('goal1b')
    goal1b.pos={'c':'b', 'b':'a'}
    goal1b.display()

    th.pause(do_pauses)

    print("""
Run session.find_plan with goal1a and goal1b, starting in state1. Both should produce the
same plan, but it won't be a very good plan, because m_split_multigoal doesn't know
how to choose the best order for achieving the goals.
""")

    state1.display("Initial state is")

    expected = [('unstack', 'a', 'b'), ('putdown', 'a'), ('pickup', 'c'), ('stack', 'c', 'b'), ('unstack', 'c', 'b'), ('putdown', 'c'), ('pickup', 'b'), ('stack', 'b', 'a'), ('pickup', 'c'), ('stack', 'c', 'b')]

    with gtpyhop.PlannerSession(domain=domain_to_use, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [goal1a])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expected)

            result = session.find_plan(state1, [goal1b])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expected)

    th.pause(do_pauses)

    print("""
Run session.find_plan on two more planning problems. Like before, goal2b omits some
of the conditions in goal2a, but both goals should produce the same plan.
""")

    state2 = gtpyhop.State('state2')
    state2.pos={'a':'c', 'b':'d', 'c':'table', 'd':'table'}
    state2.clear={'a':True, 'c':False,'b':True, 'd':False}
    state2.holding={'hand':False}

    state2.display('The initial state is')

    goal2a = gtpyhop.Multigoal('goal2a')
    goal2a.pos={'b':'c', 'a':'d', 'c':'table', 'd':'table'}
    goal2a.clear={'a':True, 'c':False,'b':True, 'd':False}
    goal2a.holding={'hand':False}
    goal2a.display()

    goal2b = gtpyhop.Multigoal('goal2b')
    goal2b.pos={'b':'c', 'a':'d'}
    goal2b.display()

    expected = [('unstack', 'a', 'c'), ('putdown', 'a'), ('unstack', 'b', 'd'), ('stack', 'b', 'c'), ('pickup', 'a'), ('stack', 'a', 'd')]

    with gtpyhop.PlannerSession(domain=domain_to_use, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state2, [goal2a])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expected)

            result = session.find_plan(state2, [goal2b])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expected)

    th.pause(do_pauses)

    print("No more examples (simplified session version)")


def main_with_args(argv=None):
    """
    Main function with command-line argument support for choosing execution mode.
    """
    parser = argparse.ArgumentParser(description="Run blocks_goal_splitting examples")
    parser.add_argument("--session", action="store_true",
                       help="Run using PlannerSession (thread-safe)")
    parser.add_argument("--verbose", type=int, default=1,
                       help="Verbosity level for session runs (0-3)")
    parser.add_argument("--no-pauses", action="store_true",
                       help="Run without pauses")

    args = parser.parse_args(argv)
    do_pauses = not args.no_pauses

    if args.session:
        main_session(do_pauses, args.verbose)
    else:
        main_legacy(do_pauses)


# It's tempting to make the following call to main() unconditional, to run the
# examples without making the user type an extra command. But if we do this
# and an error occurs while main() is executing, we get a situation in which
# the actions, methods, and examples files have been imported but the module
# hasn't been - which causes problems if we try to import the module again.

if __name__=="__main__":
    main_with_args()
