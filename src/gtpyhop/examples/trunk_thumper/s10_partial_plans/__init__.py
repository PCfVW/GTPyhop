"""
Trunk Thumper Partial Plans - GTPyhop

Implements the manual partial-plan splits from Section 12.10 of Troy
Humphreys' "Exploring HTN Planners through Example" (Game AI Pro, 2015).
Demonstrates that splitting one method's [Navigate, Slam] subtask sequence
into two separate methods (one per situation) produces shorter, more
reactive plans.

Key features:
  - 2 actions (a_navigate_to_enemy, a_do_trunk_slam)
  - TWO top-level task names for comparison:
      m_be_trunk_thumper_full_plan: chapter's pre-split version
      m_be_trunk_thumper_partial_plan: chapter's post-split version
  - 3 scenarios contrasting full and partial plans

Reference: Section 12.10 of [Humphreys 15], pp. 165-167.

-- Generated 2026-05-15
"""

import sys
import os
from typing import Dict, Tuple, List, Optional

def safe_add_to_path(relative_path: str) -> Optional[str]:
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))
    if not target_path.startswith(os.path.dirname(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")
    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

try:
    import gtpyhop
    GTPYHOP_SOURCE = "pypi"
except ImportError:
    try:
        safe_add_to_path(os.path.join('..', '..', '..', '..', '..'))
        import gtpyhop
        GTPYHOP_SOURCE = "local"
    except (ImportError, ValueError) as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)

from . import domain
from . import problems

the_domain = domain.the_domain


def get_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """Return all problem definitions for benchmarking."""
    return problems.get_problems()


__all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']
