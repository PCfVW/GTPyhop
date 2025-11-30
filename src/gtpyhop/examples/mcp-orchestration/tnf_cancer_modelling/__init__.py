"""
TNF Cancer Modelling Domain Package

This package contains the TNF cancer modelling domain definition and problem instances
for the GTPyhop planning system.

Supports both PyPI installation and local development setups.
"""

# Smart GTPyhop import strategy
try:
    # Try PyPI installation first (recommended)
    from gtpyhop import Domain, State
    GTPYHOP_SOURCE = "PyPI"
except ImportError:
    # Fallback to local development setup
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    try:
        from gtpyhop import Domain, State
        GTPYHOP_SOURCE = "Local"
    except ImportError as e:
        print(f"Warning: Could not import gtpyhop in tnf_cancer_modelling package: {e}")
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
        """Return all state/task pairs for this domain."""
        # Problem descriptions
        descriptions = {
            'scenario_1': 'Multiscale TNF Cancer Modeling: Boolean network + agent-based simulation'
        }

        problem_dict = {}
        for attr_name in dir(problems):
            if attr_name.startswith('initial_state_'):
                problem_id = attr_name.replace('initial_state_', '')
                state = getattr(problems, attr_name)
                # For TNF cancer modelling, we use task-based planning, not goal-based
                # The task is always the same: multiscale TNF cancer modeling
                task = [('m_multiscale_tnf_cancer_modeling',)]
                # Get description or generate a default one
                description = descriptions.get(problem_id, f'TNF cancer modeling: {problem_id}')
                problem_dict[problem_id] = (state, task, description)
        return problem_dict

    __all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']

except ImportError as e:
    print(f"Warning: Could not import tnf_cancer_modelling components: {e}")
    __all__ = ['GTPYHOP_SOURCE']

