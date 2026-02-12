"""
Backtracking Poetry HTN Domain for GTPyhop

This package demonstrates HTN backtracking for poetry generation. The domain
provides two methods for rhymed line composition:
  - m_write_rhymed_line_strict  (tried first, fails when rhyme family exhausted)
  - m_write_rhymed_line_relaxed (fallback, always succeeds via near-rhyme)

Planning strategy behavior:
  - Recursive DFS:              backtracks -> finds plan
  - Iterative greedy:           no backtracking -> fails on limerick
  - Iterative DFS backtracking: backtracks -> finds plan

Supported forms:
  - Rhyming couplet (AA, 2 lines, 8 actions)
  - Limerick (AABBA, 5 lines, 17 actions) -- triggers backtracking at line 4
  - Haiku (5-7-5 syllables, 3 lines, 8 actions)
  - Shakespearean sonnet (ABAB CDCD EFEF GG, 14 lines, 44 actions)

-- Generated 2026-02-11
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

# Export the domain
the_domain = domain.the_domain

# ============================================================================
# PROBLEM DISCOVERY FUNCTION
# ============================================================================

def get_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, task, description) tuples
    """
    return problems.get_problems()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'domain',
    'problems',
    'the_domain',
    'get_problems',
    'GTPYHOP_SOURCE'
]
