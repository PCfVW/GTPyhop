"""
Cybersecurity Attack Planning for GTPyhop

Models insider attacks against a network with a Document Management System
(DMS), based on the BAMS (Behavioral Adversary Modeling System) domain from
Boddy et al. (ICAPS 2005) and the hierarchy design by Pragst (2013/2014).

Key features:
  - 5 BAMS modules: Physical, Process, Network, DMS, Malware
  - 21 actions, 16 methods, 5 backtracking points
  - 9 scenarios exercising different attack paths and countermeasures
  - Demonstrates both greedy success and backtracking recovery

-- Generated 2026-04-14
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

the_domain = domain.the_domain

# ============================================================================
# PROBLEM DISCOVERY FUNCTION
# ============================================================================

def get_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """Return all problem definitions for benchmarking."""
    return problems.get_problems()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']
