"""
Feature Space Poetry HTN Domain for GTPyhop

This package demonstrates using HTN planning to automate the suppress+inject
protocol from melometis Version D (Architecture 6). The HTN's state space IS
the CLT activation space -- actions are feature-level operations on the residual
stream, not text generation. The plan itself becomes a scientific artifact
recording the automated feature-level intervention.

Servers:
  - Local computation: Initialize, suppress, evaluate threshold, compile report
  - Server 1 (inference_server): Forward passes, probability measurement
  - Server 2 (clt_server): CLT encode/decode, feature injection

Scenarios (12 total):
  Gemma 2 2B, CLT 426K (scenarios 0-3): forward planning model
  Llama 3.2 1B, CLT 524K (scenarios 4-7): late selection model
  Gemma 2 2B, CLT 2.5M (scenarios 8-11): word-level planning model
  Each group: ground truth + 3 counterfactual what-ifs (9-34 actions)

-- Generated 2026-02-18, updated 2026-02-23
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
