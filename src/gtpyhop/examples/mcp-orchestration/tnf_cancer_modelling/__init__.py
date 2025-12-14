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
        """Return all problem definitions for benchmarking."""
        return problems.get_problems()

    __all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']

except ImportError as e:
    print(f"Warning: Could not import tnf_cancer_modelling components: {e}")
    __all__ = ['GTPYHOP_SOURCE']

