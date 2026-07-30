"""
Colt Express s5 partial-plan movement - GTPyhop

Demonstrates the **method-split for partial plans** pattern (introduced
in trunk_thumper s10, Game AI Pro Chapter 12.10) applied to Colt Express
movement strategy. Two task names — m_resolve_move_full_plan (commits to
multiple actions upfront) and m_resolve_move_partial_plan (returns one
state-conditioned action) — invoked on the same state produce different
plan lengths (2 vs 1), demonstrating partial planning's reactive
character.

Key features:
  - 5 actions reused from earlier sub-folders (a_move, a_robbery,
    a_floor_change, a_fire, a_punch); no new actions
  - 2 task names: m_resolve_move_full_plan (single method, multi-action),
    m_resolve_move_partial_plan (4 priority methods, each returns one action)
  - 3 scenarios: full-plan baseline (plan=2), same-state partial plan
    (plan=1), and a marshal-adjacent partial plan (plan=1)

Pattern source: trunk_thumper s10_partial_plans (Game AI Pro chapter
section 12.10). The "There isn't much point to planning too far into the
future since there is a good chance the world state could change" quote
from the chapter (p.166) is the motivation.

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
