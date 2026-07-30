"""
The simple_travel_example.py file from the Pyhop distribution, with some
minor changes to make it compatible with GTPyhop:
  - declare a domain to hold the action and method definitions
  - replace all references to pyhop with gtpyhop
  - change 'verbose' to a global variable instead of a keyword argument

To keep this file as close as possible to the Pyhop version, it doesn't use
the test harness that's used with the other example files.
-- Dana Nau <nau@umd.edu>, July 20, 2021

Updated for GTPyhop 1.3.0 thread-safe sessions - 2025-08-22
"""

import gtpyhop
import argparse


# declare a domain to hold the action and method definitions
#
the_domain = gtpyhop.Domain('pyhop_simple_travel_example')

def taxi_rate(dist):
    return (1.5 + 0.5 * dist)

def walk(state,a,x,y):
    if state.loc[a] == x:
        state.loc[a] = y
        return state
    else: return False

def call_taxi(state,a,x):
    state.loc['taxi'] = x
    return state
    
def ride_taxi(state,a,x,y):
    if state.loc['taxi']==x and state.loc[a]==x:
        state.loc['taxi'] = y
        state.loc[a] = y
        state.owe[a] = taxi_rate(state.dist[x][y])
        return state
    else: return False

def pay_driver(state,a):
    if state.cash[a] >= state.owe[a]:
        state.cash[a] = state.cash[a] - state.owe[a]
        state.owe[a] = 0
        return state
    else: return False

gtpyhop.declare_operators(walk, call_taxi, ride_taxi, pay_driver)
print('')
gtpyhop.print_operators()



def travel_by_foot(state,a,x,y):
    if state.dist[x][y] <= 2:
        return [('walk',a,x,y)]
    return False

def travel_by_taxi(state,a,x,y):
    if state.cash[a] >= taxi_rate(state.dist[x][y]):
        return [('call_taxi',a,x), ('ride_taxi',a,x,y), ('pay_driver',a)]
    return False

gtpyhop.declare_methods('travel',travel_by_foot,travel_by_taxi)
print('')
gtpyhop.print_methods()

state1 = gtpyhop.State('state1')
state1.loc = {'me':'home'}
state1.cash = {'me':20}
state1.owe = {'me':0}
state1.dist = {'home':{'park':8}, 'park':{'home':8}}

def main_legacy():
    """
    Legacy implementation using global state (preserved for backward compatibility).
    """
    print("""
********************************************************************************
Call gtpyhop.pyhop(state1,[('travel','me','home','park')]) with different verbosity levels
********************************************************************************
""")

    print("- If verbose=0, GTPyhop returns the solution but prints nothing.\n")
    gtpyhop.verbose = 0
    gtpyhop.pyhop(state1,[('travel','me','home','park')])

    print('- If verbose=1, GTPyhop prints the problem and solution, and returns the solution:')
    gtpyhop.verbose = 1
    gtpyhop.pyhop(state1,[('travel','me','home','park')])

    print('- If verbose=2, GTPyhop also prints a note at each recursive call:')
    gtpyhop.verbose = 2
    gtpyhop.pyhop(state1,[('travel','me','home','park')])

    print('- If verbose=3, GTPyhop also prints the intermediate states:')
    gtpyhop.verbose = 3
    gtpyhop.pyhop(state1,[('travel','me','home','park')])


def main_session(verbose=1):
    """
    Thread-safe implementation using PlannerSession (GTPyhop 1.3.0+).
    """
    print(f"""
********************************************************************************
Running pyhop_simple_travel_example with PlannerSession (verbose={verbose})
********************************************************************************
""")

    print("- Session with verbose=0: GTPyhop returns the solution but prints nothing.\n")
    with gtpyhop.PlannerSession(domain=the_domain, verbose=0) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [('travel','me','home','park')])
            plan = result.plan if (result and result.success) else None
            print(f"Plan: {plan}")

    print('- Session with verbose=1: GTPyhop prints the problem and solution:')
    with gtpyhop.PlannerSession(domain=the_domain, verbose=1) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [('travel','me','home','park')])
            plan = result.plan if (result and result.success) else None
            print(f"Plan: {plan}")

    print('- Session with verbose=2: GTPyhop also prints a note at each recursive call:')
    with gtpyhop.PlannerSession(domain=the_domain, verbose=2) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [('travel','me','home','park')])
            plan = result.plan if (result and result.success) else None
            print(f"Plan: {plan}")

    print('- Session with verbose=3: GTPyhop also prints the intermediate states:')
    with gtpyhop.PlannerSession(domain=the_domain, verbose=3) as session:
        with session.isolated_execution():
            result = session.find_plan(state1, [('travel','me','home','park')])
            plan = result.plan if (result and result.success) else None
            print(f"Plan: {plan}")


def main_with_args(argv=None):
    """
    Main function with command-line argument support for choosing execution mode.
    """
    parser = argparse.ArgumentParser(description="Run pyhop_simple_travel_example")
    parser.add_argument("--session", action="store_true",
                       help="Run using PlannerSession (thread-safe)")
    parser.add_argument("--verbose", type=int, default=1,
                       help="Verbosity level for session runs (0-3)")

    args = parser.parse_args(argv)

    if args.session:
        main_session(args.verbose)
    else:
        main_legacy()


if __name__ == "__main__":
    main_with_args()

