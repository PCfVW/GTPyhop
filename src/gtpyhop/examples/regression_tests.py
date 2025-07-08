"""
The following code runs GTPyhop on all but one of the example domains, to
see whether they run without error and return correct answers. The
2nd-to-last line imports simple_htn_acting_error but doesn't run it,
because running it is *supposed* to cause an error.

-- Dana Nau <nau@umd.edu>, July 20, 2021
"""

def main():
    """
    Run all the regression tests.
    """
    # The argument False tells the test harness not to stop for user input
    from gtpyhop.examples import simple_htn; simple_htn.main(False)
    from gtpyhop.examples import simple_hgn; simple_hgn.main(False)
    
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
