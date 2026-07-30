"""
Trunk Thumper Priority Methods - GTPyhop

Implements the multi-method AttackEnemy from Section 12.8 of Troy Humphreys'
"Exploring HTN Planners through Example" (Game AI Pro, 2015). Combines two
sub-stories from the chapter:
  (a) AttackEnemy gains a third "boulder fallback" method for when the troll
      cannot navigate to the enemy.
  (b) The WsPowerUp/whirlwind combo: three trunk slams accumulate WsPowerUp,
      enabling DoWhirlwindTrunkAttack as a higher-priority method. WsIsTired
      correctly gates the whirlwind from triggering off a single slam (the
      chapter's "subtle bug" example, fixed by the WsIsTired world state).

Key features:
  - 13 actions including DoWhirlwindTrunkAttack and boulder attack
  - 4 alternative methods on m_attack_enemy in priority order
  - 4 scenarios covering default slam+recovery, whirlwind combo, boulder
    fallback, and the WsIsTired guard against premature whirlwind

Reference: Section 12.8 of [Humphreys 15], pp. 160-163.

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
