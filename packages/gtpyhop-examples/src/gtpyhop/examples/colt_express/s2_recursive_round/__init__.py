"""
Colt Express s2 recursive-round - GTPyhop

Demonstrates recursive task decomposition (introduced in trunk_thumper s06,
Game AI Pro Chapter 12.6) applied to Colt Express deck resolution during
the Stealin' phase. A pre-encoded `state.deck` of (bandit, card_kind)
tuples is resolved card-by-card via a recursive method that head-pops the
deck on each action, terminating when the deck is empty.

Key features:
  - 4 actions: a_move, a_robbery, a_floor_change (all deck-aware: each
    pops state.deck[0] as part of its effects), plus a_apply_event for
    end-of-round event resolution
  - 2 task names: m_resolve_programmed_deck (recursive, 2 methods) and
    m_play_round (2 methods: with/without event)
  - 3 scenarios: simple 3-card deck, longer 6-card deck, and a deck +
    end-of-round event chain

Pattern source: trunk_thumper s06_recursive_trunk_replacement (Game AI
Pro chapter section 12.6).

NOTE on action evolution: s2's a_move, a_robbery, a_floor_change are
DIFFERENT from s1's and s3's. They additionally check that state.deck[0]
matches and head-pop the deck. This is one of two parallel evolutions of
s1's actions (the other is s3's Marshal-aware version). Per the collection
copy-paste convention, each sub-folder declares its own action versions.

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

from . import domain
from . import problems

the_domain = domain.the_domain

def get_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """Return all problem definitions for benchmarking."""
    return problems.get_problems()

__all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']
