"""
Colt Express s4 character-priorities - GTPyhop

Demonstrates priority-method ladders (introduced in trunk_thumper s08,
Game AI Pro Chapter 12.8) applied to Colt Express character abilities.
Each ability is implemented as a separate, higher-priority method that
returns False on miss so the planner falls through to the next method.

Characters modeled (4 of 6, per locked-in scope):
  - Belle:    "You cannot be the target of a Fire action or a Punch
              action if there is another Bandit who can be targeted, too."
              Implemented as m_fire_blocked_by_belle_immunity (top
              priority on m_resolve_fire).
  - Tuco:     "Tuco's shots are not stopped by the roof. You can shoot
              a Bandit who is on the same Car as you are, on the other
              level." Implemented as m_fire_tuco_through_floor with the
              special action a_fire_through_floor.
  - Django:   "Django's shots are so powerful that they knock the other
              bandits back. When shooting a Bandit, make him move one
              Car in the direction of fire." Implemented as
              m_fire_django_knockback with action a_fire_with_knockback.
  - Cheyenne: "When punching a Bandit, you can take the Purse he has
              just lost." Implemented as m_punch_cheyenne_keep_purse
              with action a_punch_and_keep_purse.

(Ghost and Doc skipped per scope decision: Ghost complicates s2's deck
recursion; Doc is trivial initial-state config.)

Key features:
  - 8 actions: 3 basic from s1, plus a_fire (from s3), a_fire_through_floor,
    a_fire_with_knockback, a_punch, a_punch_and_keep_purse
  - 2 task names: m_resolve_fire (4 methods), m_resolve_punch (2 methods)
  - 4 scenarios — one per character ability (extended from the plan's 3)

Pattern source: trunk_thumper s08_priority_methods (Game AI Pro chapter
section 12.8). Belle's immunity guard mirrors s08's WsIsTired fix
structurally: a higher-priority method whose precondition prevents the
generic action from firing in a specific game-rule-defined situation.

-- Generated 2026-05-16
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
