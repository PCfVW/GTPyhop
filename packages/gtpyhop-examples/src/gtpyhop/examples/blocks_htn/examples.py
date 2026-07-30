"""
Examples file for blocks_htn.
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
configuration "c on b, b on a, a on the table".
""")

    state1.display("Initial state is")

    goal1a = gtpyhop.Multigoal('goal1a')
    goal1a.pos={'c':'b', 'b':'a', 'a':'table'}

    goal1a.display()

    print("""
We don't have any methods for multigoals, but we have a task method for
('achieve' mg), the task of achieving multigoal mg. Here's ('achieve', goal1a):
    """)

    # Tell the test harness what answer to expect, so it can signal an error
    # if gtpyhop returns an incorrect answer. Checks like this have been very
    # very helpful for debugging both gtpyhop and the various example domains.

    expected = [('unstack', 'a', 'b'), ('putdown', 'a'), ('pickup', 'b'), ('stack', 'b', 'a'), ('pickup', 'c'), ('stack', 'c', 'b')]

    plan1 = gtpyhop.find_plan(state1,[('achieve', goal1a)])
    th.check_result(plan1,expected)
    th.pause(do_pauses)

    print("""
goal1b says we want c on b on a. It omits "a on table", but it still has the
same solution as goal1a, because "c on b on a" entails "a on table".
""")

    goal1b = gtpyhop.Multigoal('goal1b')
    goal1b.pos={'c':'b', 'b':'a'}

    goal1b.display()

    gtpyhop.verbose = 2
    plan2 = gtpyhop.find_plan(state1,[('achieve', goal1b)])
    th.check_result(plan2,expected)
    gtpyhop.verbose = 1

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

    sussman_plan = gtpyhop.find_plan(sus_s0,[('achieve', sus_sg)])
    th.check_result(sussman_plan,expected)

    th.pause(do_pauses)

    print("""
Another initial state and two multigoals, goal2a and goal2b, such that
('achieve', goal2a) and ('achieve', goal2b) have the same solutions.
""")

    state2 = gtpyhop.State('state2')
    state2.pos={'a':'c', 'b':'d', 'c':'table', 'd':'table'}
    state2.clear={'a':True, 'c':False,'b':True, 'd':False}
    state2.holding={'hand':False}

    state2.display('Initial state is')

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

#     th.pause(do_pauses)
#     print("When we run find_plan on the tasks ('achieve', goal2a) and")
#     print("('achieve', goal2b), it produces the same plan for both:")

    plan1 = gtpyhop.find_plan(state2,[('achieve', goal2a)])
    th.check_result(plan1,expected)

    plan2 = gtpyhop.find_plan(state2,[('achieve', goal2b)])
    th.check_result(plan2,expected)
    th.pause(do_pauses)

    print("\nRun find_plan on problem bw_large_d from the SHOP distribution:\n")

    state3 = gtpyhop.State('state3')
    state3.pos = {1:12, 12:13, 13:'table', 11:10, 10:5, 5:4, 4:14, 14:15, 15:'table', 9:8, 8:7, 7:6, 6:'table', 19:18, 18:17, 17:16, 16:3, 3:2, 2:'table'}
    state3.clear = {x:False for x in range(1,20)}
    state3.clear.update({1:True, 11:True, 9:True, 19:True})
    state3.holding={'hand':False}

    state3.display('Initial state is')

    goal3 = gtpyhop.Multigoal('goal3')
    goal3.pos = {15:13, 13:8, 8:9, 9:4, 4:'table', 12:2, 2:3, 3:16, 16:11, 11:7, 7:6, 6:'table'}
    goal3.clear = {17:True, 15:True, 12:True}

    goal3.display()

    expected = [('unstack', 1, 12), ('putdown', 1), ('unstack', 19, 18), ('putdown', 19), ('unstack', 18, 17), ('putdown', 18), ('unstack', 17, 16), ('putdown', 17), ('unstack', 9, 8), ('putdown', 9), ('unstack', 8, 7), ('putdown', 8), ('unstack', 11, 10), ('stack', 11, 7), ('unstack', 10, 5), ('putdown', 10), ('unstack', 5, 4), ('putdown', 5), ('unstack', 4, 14), ('putdown', 4), ('pickup', 9), ('stack', 9, 4), ('pickup', 8), ('stack', 8, 9), ('unstack', 14, 15), ('putdown', 14), ('unstack', 16, 3), ('stack', 16, 11), ('unstack', 3, 2), ('stack', 3, 16), ('pickup', 2), ('stack', 2, 3), ('unstack', 12, 13), ('stack', 12, 2), ('pickup', 13), ('stack', 13, 8), ('pickup', 15), ('stack', 15, 13)]

    plan = gtpyhop.find_plan(state3,[('achieve', goal3)])
    th.check_result(plan,expected)
    th.pause(do_pauses)

    # Skip the very large IPC2011BWrand50 problem for brevity in session mode
    print("\nSkipping large IPC2011BWrand50 problem for brevity...")

    print("""
Call run_lazy_lookahead on the following problem, with verbose=1:
""")

    state2.display(heading='Initial state is')
    goal2b.display(heading='Goal is')

    new_state = gtpyhop.run_lazy_lookahead(state2, [('achieve', goal2b)])

    th.pause(do_pauses)

    print("The goal should now be satisfied, so the planner should return an empty plan:\n")

    plan = gtpyhop.find_plan(new_state, [('achieve', goal2b)])
    th.check_result(plan,[])

    print("No more examples")


def main_session(do_pauses=True, verbose=1):
    """
    Thread-safe implementation using PlannerSession (GTPyhop 1.3.0+).
    This is a simplified version focusing on key examples.
    """
    print(f"\n=== Running blocks_htn examples with PlannerSession (verbose={verbose}) ===")

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

            result = session.find_plan(state1, [('pickup','b')])
            plan = result.plan if (result and result.success) else False
            th.check_result(plan, False)

            result = session.find_plan(state1, [('take','b')])
            plan = result.plan if (result and result.success) else False
            th.check_result(plan, False)

    th.pause(do_pauses)
    print("""
Next, some simple things that should succeed. As a reminder, in state1,
block a is on block b, block b is on the table, and block c is on the table.
""")

    # Test successes
    with gtpyhop.PlannerSession(domain=domain_to_use, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [('pickup','c')])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, [('pickup','c')])

            result = session.find_plan(state1, [('take','a')])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, [('unstack','a', 'b')])

            result = session.find_plan(state1, [('take','c')])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, [('pickup','c')])

            result = session.find_plan(state1, [('take','a'),('put','a','table')])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, [('unstack','a', 'b'), ('putdown','a')])

    th.pause(do_pauses)

    print("""
A Multigoal is a data structure that specifies desired values for some of
the state variables. Below, goal1a says we want the blocks in the
configuration "c on b, b on a, a on the table".
""")

    state1.display("Initial state is")

    goal1a = gtpyhop.Multigoal('goal1a')
    goal1a.pos={'c':'b', 'b':'a', 'a':'table'}
    goal1a.display()

    print("""
We don't have any methods for multigoals, but we have a task method for
('achieve' mg), the task of achieving multigoal mg. Here's ('achieve', goal1a):
    """)

    expected = [('unstack', 'a', 'b'), ('putdown', 'a'), ('pickup', 'b'), ('stack', 'b', 'a'), ('pickup', 'c'), ('stack', 'c', 'b')]

    with gtpyhop.PlannerSession(domain=domain_to_use, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [('achieve', goal1a)])
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
            result = session.find_plan(sus_s0, [('achieve', sus_sg)])
            plan = result.plan if (result and result.success) else None
            th.check_result(plan, expected)

    th.pause(do_pauses)

    print("No more examples (simplified session version)")


def main_with_args(argv=None):
    """
    Main function with command-line argument support for choosing execution mode.
    """
    parser = argparse.ArgumentParser(description="Run blocks_htn examples")
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
