"""
Trunk Thumper Expected Effects - GTPyhop

Implements the chase-with-expected-effects domain from Section 12.7 of Troy
Humphreys' "Exploring HTN Planners through Example" (Game AI Pro, 2015).
Introduces a third method on BeTrunkThumper for chasing a recently-seen
enemy, and demonstrates the [EXPECTED_EFFECT] tag — effects applied during
planning to represent sensor-driven world-state changes that will happen
after the operator runs.

Key features:
  - 10 actions including a_nav_to_last_enemy_loc (with [EXPECTED_EFFECT])
    and a_regain_los_roar (which requires can_see_enemy at planning time)
  - A negative-control scenario shows what happens WITHOUT the expected
    effect: the roar action's precondition fails and the plan is impossible
  - 3 scenarios: visible attack, chase-with-roar, negative control

Reference: Section 12.7 of [Humphreys 15], pp. 158-159.

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
