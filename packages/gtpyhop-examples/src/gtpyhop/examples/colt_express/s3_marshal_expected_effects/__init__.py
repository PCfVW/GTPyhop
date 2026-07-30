"""
Colt Express s3 marshal expected-effects - GTPyhop

Demonstrates the [EXPECTED_EFFECT] tag (introduced in trunk_thumper s07,
Game AI Pro Chapter 12.7) applied to the Colt Express Marshal forced-escape
rule. When a bandit enters the Marshal's car (or vice versa), the rulebook
forces the bandit onto the roof and gives them a Neutral Bullet card. This
is a sensor-driven side effect of the move, not a direct operator effect.
Modeling it as [EXPECTED_EFFECT] inside a_move (and a_marshal_move) lets
downstream actions whose preconditions depend on the bandit's level
succeed at planning time.

Key features:
  - 6 actions: a_move (with EE), a_robbery, a_floor_change (all reused
    from s1), plus a_marshal_move, a_fire, and the demo variant
    a_move_demo_no_marshal_trigger
  - 2 methods reused from s1 (m_rob_loot_here, m_move_forward_fallback)
  - 3 scenarios: positive a_move-and-fire chain, a_marshal_move-and-fire
    chain, and a negative-control scenario whose plan fails because the
    demo variant omits the [EXPECTED_EFFECT]

Pattern source: trunk_thumper s07_expected_effects_chase (Game AI Pro
chapter section 12.7).

-- Generated 2026-05-16
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

# ============================================================================
# IMPORT DOMAIN AND PROBLEMS
# ============================================================================

from . import domain
from . import problems

the_domain = domain.the_domain

def get_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """Return all problem definitions for benchmarking."""
    return problems.get_problems()

__all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']
