"""
Blocksworld-GTOHP Domain Package

This package contains the Blocksworld domain definition and problem instances
for the GTPyhop planning system.

Supports both PyPI installation and local development setups.
"""

# Smart GTPyhop import strategy
try:
    # Try PyPI installation first (recommended)
    from gtpyhop import Domain, State, Multigoal
    GTPYHOP_SOURCE = "PyPI"
except ImportError:
    # Fallback to local development setup
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    try:
        from gtpyhop import Domain, State, Multigoal
        GTPYHOP_SOURCE = "Local"
    except ImportError as e:
        print(f"Warning: Could not import gtpyhop in Blocksworld-GTOHP package: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        raise

# Import domain components
try:
    from . import domain
    from . import problems
    
    # Make key components available at package level
    the_domain = domain.the_domain
    
    # Export problem discovery function
    def get_problems():
        """Return all state/goal pairs for this domain."""
        problem_dict = {}
        for attr_name in dir(problems):
            if attr_name.startswith('state_BW_rand_'):
                problem_id = attr_name.replace('state_', '')
                state = getattr(problems, attr_name)
                goal_attr = f'goal_{problem_id}'
                if hasattr(problems, goal_attr):
                    goal = getattr(problems, goal_attr)  # Direct dictionary
                    problem_dict[problem_id] = (state, goal)
        return problem_dict
    
    __all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']
    
except ImportError as e:
    print(f"Warning: Could not import Blocksworld-GTOHP components: {e}")
    __all__ = ['GTPYHOP_SOURCE']
