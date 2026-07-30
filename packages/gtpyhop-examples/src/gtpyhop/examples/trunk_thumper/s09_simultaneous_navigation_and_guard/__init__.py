"""
Trunk Thumper Simultaneous Behaviors - GTPyhop

Implements the single-planner approach from Section 12.9 of Troy Humphreys'
"Exploring HTN Planners through Example" (Game AI Pro, 2015) for handling
simultaneous behaviors. Navigation is modeled as non-blocking: a_navigate_to_enemy
completes immediately, setting Navigating=True; the path-following happens
"in the background". This frees the planner to interleave a guard action
while traversal is in progress.

Key features:
  - 4 actions (slam, guard, non-blocking navigate, idle)
  - Single m_be_trunk_thumper task with 4 priority-ordered methods
  - 3 scenarios: melee slam, out-of-range navigate, navigating-and-hit guard

Reference: Section 12.9 of [Humphreys 15], pp. 163-165 (the chapter's
*recommended* approach; the multi-planner alternative is presented and
ultimately discouraged - "you will not gain any friends... trust me").

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
