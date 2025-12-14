"""
Drug Target Discovery Domain Package

This package provides a GTPyhop domain for drug target discovery workflows
using the OpenTargets platform.
"""

from . import domain
from . import problems

# Export the domain for benchmarking
the_domain = domain.the_domain

def get_problems():
    """Return all problem definitions for benchmarking."""
    return problems.get_problems()

