"""
Omega HDQ DNA Bacteria Extraction Domain for GTPyhop 1.6.0

This package demonstrates HTN planning for DNA extraction automation with:
  - Server 1 (htn-planning-server): HTN planning with GTPyhop
  - Server 2 (liquid-handling-server): Pipetting operations (96-channel)
  - Server 3 (module-control-server): Heater-shaker, temp module, magnetic block
  - Server 4 (gripper-server): Labware transfers

Based on Opentrons Flex protocol by Zach Galluzzo <zachary.galluzzo@opentrons.com>
Protocol: Omega_HDQ_DNA_Bacteria-Flex_96_channel.py (included for reference)

-- Generated 2025-11-29
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
    Return all state/task pairs for this domain.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
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

