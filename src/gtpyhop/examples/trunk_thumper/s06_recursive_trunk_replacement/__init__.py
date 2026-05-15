"""
Trunk Thumper Recursion - GTPyhop

Implements the recursive trunk-replacement domain from Section 12.6 of Troy
Humphreys' "Exploring HTN Planners through Example" (Game AI Pro, 2015).
When the troll's tree trunk breaks (WsTrunkHealth reaches 0), the AttackEnemy
compound task recurses through a sub-method that finds a new trunk, uproots
it, then re-invokes AttackEnemy.

Key features:
  - 8 actions, 2 task names (m_be_trunk_thumper, m_attack_enemy)
  - Recursion in m_attack_enemy: the find-new-trunk method ends with a
    recursive call to m_attack_enemy
  - 3 scenarios covering intact trunk, broken trunk (forces recursion),
    and patrol regression check

Reference: Section 12.6 of [Humphreys 15], pp. 157-158.

-- Generated 2026-05-15
"""

import sys
import os
from typing import Dict, Tuple, List, Optional

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
