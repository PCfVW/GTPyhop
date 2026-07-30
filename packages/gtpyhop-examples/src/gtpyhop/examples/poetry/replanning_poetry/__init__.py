"""
Replanning Poetry HTN Domain for GTPyhop

This package demonstrates post-generation evaluation and steering/revision for
neuro-symbolic poetry generation. After initial generation, an evaluation step
may determine that a line needs a better target word, triggering replanning:
the planner backtracks and tries a revision path that steers to a new target
and completely regenerates the line. This models Anthropic's "Planning in Poems"
(March 2025) finding that injecting an alternative planned word causes the model
to restructure the entire line in 70% of test poems.

Architecture:
  - Server 1 (phonetics-server): Rhyme target selection, steering, verification
  - Server 2 (llm-server): Text generation, line evaluation

Supported forms:
  - Rhyming couplet (AA, 2 lines, 12 actions)
  - Limerick (AABBA, 5 lines, 28 actions)
  - Haiku (5-7-5 syllables, 3 lines, 8 actions)
  - Shakespearean sonnet (ABAB CDCD EFEF GG, 14 lines, 72 actions)

-- Generated 2026-02-12
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
