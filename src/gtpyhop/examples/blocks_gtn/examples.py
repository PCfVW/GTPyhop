"""
Examples file for blocks_gtn.
-- Dana Nau <nau@umd.edu>, July 20, 2021

Updated for GTPyhop 1.3.0 thread-safe sessions - 2025-08-22
"""

# Uncomment this to use it in debugging:
# from IPython import embed
# from IPython.terminal.debugger import set_trace

import gtpyhop
import argparse
import gtpyhop.test_harness as th   # code for use in paging and debugging

print(">>> __name__ = ", __name__)  # Debugging line

# We must declare the current domain before importing methods and actions.
# To make the code more portable, we don't hard-code the domain name, but
# instead use the name of the package.
the_domain = gtpyhop.Domain(__package__)
print(">>> the_domain = ", the_domain)  # Debugging line
print(">>> the_domain.__name__ = ", the_domain.__name__)  # Debugging line
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

    print("\nLet's call find_plan on some simple things that should fail.\n")

    state1 = gtpyhop.State('state1')
    state1.pos={'a':'b', 'b':'table', 'c':'table'}
    state1.clear={'c':True, 'b':False,'a':True}
    state1.holding={'hand':False}

    state1.display('Initial state is')

    plan = gtpyhop.find_plan(state1,[('pickup','a')])
    th.check_result(plan,False)

    plan = gtpyhop.find_plan(state1,[('pickup','b')])
    th.check_result(plan,False)

    plan = gtpyhop.find_plan(state1,[('take','b')])
    th.check_result(plan,False)

    th.pause(do_pauses)
    print("""
Next, some simple things that should succeed. As a reminder, in state1,
block a is on block b, block b is on the table, and block c is on the table.
""")
    
    plan = gtpyhop.find_plan(state1,[('pickup','c')])
    th.check_result(plan, [('pickup','c')])

    plan = gtpyhop.find_plan(state1,[('take','a')])
    th.check_result(plan, [('unstack','a', 'b')])

    plan = gtpyhop.find_plan(state1,[('take','c')])
    th.check_result(plan, [('pickup','c')])

    plan = gtpyhop.find_plan(state1,[('take','a'),('put','a','table')])
    th.check_result(plan, [('unstack','a', 'b'), ('putdown','a')])
    th.pause(do_pauses)

    print("""
A Multigoal is a data structure that specifies desired values for some of
the state variables. Below, goal1a says we want the blocks in the
configuration "c on b, b on a, a on the table", and goal1b says we want "c
on b, b on a" without specifying where block a should be. However, goal1a
and goal1b have the same solution plans, because "c on b, b on a" entails "a
on the table".
""")

    state1.display("Initial state is")

    goal1a = gtpyhop.Multigoal('goal1a')
    goal1a.pos={'c':'b', 'b':'a', 'a':'table'}
    goal1a.display()

    goal1b = gtpyhop.Multigoal('goal1b')
    goal1b.pos={'c':'b', 'b':'a'}
    goal1b.display()

    expected = [('unstack', 'a', 'b'), ('putdown', 'a'), ('pickup', 'b'), ('stack', 'b', 'a'), ('pickup', 'c'), ('stack', 'c', 'b')]

    plan1 = gtpyhop.find_plan(state1,[goal1a])
    th.check_result(plan1,expected)

    plan2 = gtpyhop.find_plan(state1,[goal1b])
    th.check_result(plan2,expected)
    th.pause(do_pauses)

    print("""
Run find_plan on the famous Sussman anomaly.
""")

    sus_s0 = gtpyhop.State('Sussman anomaly initial state')
    sus_s0.pos={'c':'a', 'a':'table', 'b':'table'}
    sus_s0.clear={'c':True, 'a':False,'b':True}
    sus_s0.holding={'hand':False}

    sus_s0.display()

    sus_sg = gtpyhop.Multigoal('Sussman anomaly multigoal')
    sus_sg.pos={'a':'b', 'b':'c'}
    sus_sg.display()

    expected = [('unstack', 'c', 'a'), ('putdown', 'c'), ('pickup', 'b'), ('stack', 'b', 'c'), ('pickup', 'a'), ('stack', 'a', 'b')]

    sussman_plan = gtpyhop.find_plan(sus_s0,[sus_sg])
    th.check_result(sussman_plan,expected)

    th.pause(do_pauses)

    # Skip large examples and run_lazy_lookahead for brevity
    print("Skipping large examples for brevity...")

    print("No more examples")


def main_session(do_pauses=True, verbose=1):
    """
    Thread-safe implementation using PlannerSession (GTPyhop 1.3.0+).
    This is a simplified version focusing on key examples with mixed task/goal planning.
    """
    print(f"\n=== Running blocks_gtn examples with PlannerSession (verbose={verbose}) ===")

    # Make sure we have the right domain
    domain_to_use = gtpyhop.find_domain_by_name(gtpyhop.Domain(__package__).__name__)
    print(f"Using domain: {domain_to_use}")

    print("\nLet's call session.find_plan on some simple things that should fail.\n")

    state1 = gtpyhop.State('state1')
    state1.pos={'a':'b', 'b':'table', 'c':'table'}
    state1.clear={'c':True, 'b':False,'a':True}
    state1.holding={'hand':False}

    state1.display('Initial state is')

    # Test failures
    with gtpyhop.PlannerSession(domain=domain_to_use, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [('pickup','a')])
            plan = result.plan if (result and result.success) else False
            th.check_result(plan, False)

            result = session.find_plan(state1, [('take','b')])
            plan = result.plan if (result and result.success) else False
            th.check_result(plan, False)

    th.pause(do_pauses)
    print("""
Next, some simple things that should succeed. This demonstrates mixed task/goal planning.
""")

    # Test successes with mixed tasks and goals
    with gtpyhop.PlannerSession(domain=domain_to_use, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [('pickup','c')])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, [('pickup','c')])

            result = session.find_plan(state1, [('take','a')])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, [('unstack','a', 'b')])

            result = session.find_plan(state1, [('take','a'),('put','a','table')])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, [('unstack','a', 'b'), ('putdown','a')])

    th.pause(do_pauses)

    print("""
Multigoal example demonstrating goal-oriented planning in GTN.
""")

    state1.display("Initial state is")

    goal1a = gtpyhop.Multigoal('goal1a')
    goal1a.pos={'c':'b', 'b':'a', 'a':'table'}
    goal1a.display()

    expected = [('unstack', 'a', 'b'), ('putdown', 'a'), ('pickup', 'b'), ('stack', 'b', 'a'), ('pickup', 'c'), ('stack', 'c', 'b')]

    with gtpyhop.PlannerSession(domain=domain_to_use, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [goal1a])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expected)

    th.pause(do_pauses)

    print("""
Run find_plan on the famous Sussman anomaly.
""")

    sus_s0 = gtpyhop.State('Sussman anomaly initial state')
    sus_s0.pos={'c':'a', 'a':'table', 'b':'table'}
    sus_s0.clear={'c':True, 'a':False,'b':True}
    sus_s0.holding={'hand':False}

    sus_s0.display()

    sus_sg = gtpyhop.Multigoal('Sussman anomaly multigoal')
    sus_sg.pos={'a':'b', 'b':'c'}
    sus_sg.display()

    expected = [('unstack', 'c', 'a'), ('putdown', 'c'), ('pickup', 'b'), ('stack', 'b', 'c'), ('pickup', 'a'), ('stack', 'a', 'b')]

    with gtpyhop.PlannerSession(domain=domain_to_use, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(sus_s0, [sus_sg])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expected)

    th.pause(do_pauses)

    print("No more examples (simplified session version)")


def main_with_args(argv=None):
    """
    Main function with command-line argument support for choosing execution mode.
    """
    parser = argparse.ArgumentParser(description="Run blocks_gtn examples")
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
