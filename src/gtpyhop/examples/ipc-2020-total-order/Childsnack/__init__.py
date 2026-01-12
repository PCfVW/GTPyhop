"""
Childsnack Domain for GTPyhop

IPC 2020 Total Order track - Childsnack domain for serving sandwiches
to children with allergies. This package contains the domain definition
and problem instances.

-- Generated 2026-01-12
"""

import sys
import os
from typing import Dict, Tuple, List, Optional

# ============================================================================
# SMART GTPYHOP IMPORT STRATEGY
# ============================================================================

def safe_add_to_path(relative_path: str) -> Optional[str]:
    """Safely add a relative path to sys.path with validation."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))

    if not target_path.startswith(os.path.dirname(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")

    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

# Try PyPI installation first, fallback to local
try:
    import gtpyhop
    GTPYHOP_SOURCE = "pypi"
except ImportError:
    try:
        safe_add_to_path(os.path.join('..', '..', '..', '..'))
        import gtpyhop
        GTPYHOP_SOURCE = "local"
    except (ImportError, ValueError) as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)

# ============================================================================
# IMPORT DOMAIN AND PROBLEMS
# ============================================================================

from . import domain
from . import problems

the_domain = domain.the_domain

# ============================================================================
# PROBLEM DISCOVERY FUNCTION
# ============================================================================

def get_problems() -> Dict[str, Tuple[gtpyhop.State, dict, str]]:
    """
    Return all state/goal pairs for this domain.

    Returns:
        Dictionary mapping problem IDs to (state, goal, description) tuples.
    """
    problem_dict = {}
    for attr_name in dir(problems):
        if attr_name.startswith('state_childsnack_'):
            problem_id = attr_name.replace('state_childsnack_', '')
            state = getattr(problems, attr_name)
            goal_attr = f'goal_childsnack_{problem_id}'
            if hasattr(problems, goal_attr):
                goal = getattr(problems, goal_attr)
                problem_dict[f"childsnack_{problem_id}"] = (state, goal, f"Childsnack {problem_id}")
    return problem_dict

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']
