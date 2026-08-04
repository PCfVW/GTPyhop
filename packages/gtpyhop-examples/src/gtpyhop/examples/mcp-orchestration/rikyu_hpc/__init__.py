"""
Rikyu HPC / vast.ai Containerized Training Example for GTPyhop

This package demonstrates HTN planning over four MCP endpoints:
  - Server 1 (mcp-python-ingestion): HTN planning with GTPyhop
  - Server 2 (rikyu-hpc):  Slurm, filesystem and login node (hpc_server.py)
  - Server 3 (rikyu-docs): documentation search (docs_server.py)
  - Server 4 (vastai):     rented GPU instances (vast.ai CLI / SDK / REST)

Servers 2 and 3 mirror the tool surface of the RIKEN-RCCS Rikyu-Agent
repository. Server 4 is the vast.ai public API, modelled as a fourth server: it
is not part of Rikyu-Agent, and it is present so that an image Rikyu cannot
execute still has somewhere to run.

Rikyu does run containers - Apptainer 1.4.5, unprivileged, behind a
'singularity' symlink - but advertises this nowhere, so a plan has to probe the
login node to find out. Once it knows, the image architecture decides where the
run happens: an x86_64 image converts to SIF cleanly and then fails at exec on
the aarch64 Grace nodes. See README.md for the full provenance table.

-- Generated 2026-08-04
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
# PROBLEM DISCOVERY FUNCTIONS
# ============================================================================

def get_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """
    Return all solvable problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples
    """
    return problems.get_problems()


def get_trap_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """
    Return the trap problems, every one of which must fail to produce a plan.

    Kept separate from get_problems() so that benchmarking reports the solvable
    scenarios only. Each trap violates exactly one documented Rikyu or vast.ai
    rule, so a plan found for any of them is an attributable defect.

    Returns:
        Dictionary mapping trap IDs to (state, tasks, description) tuples
    """
    return problems.get_trap_problems()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'domain',
    'problems',
    'the_domain',
    'get_problems',
    'get_trap_problems',
    'GTPYHOP_SOURCE'
]
