"""
Problem definitions for the TNF Cancer Modeling example.
-- Generated 2025-12-14

This file defines initial states for the multiscale TNF cancer modeling workflow.
The workflow integrates Boolean network modeling (MaBoSS) with agent-based
multicellular simulation (PhysiCell) to study TNF-induced cancer cell fate decisions.

Scenarios:
  - scenario_1_multiscale: Complete multiscale TNF cancer modeling workflow -> 12 actions
"""

import sys
import os
from typing import Dict, Tuple, List

# Secure GTPyhop import strategy
try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    # Fallback to local development
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import State
    except ImportError as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: tnf_cancer_modelling

# BEGIN: Scenario: scenario_1_multiscale
# Configuration
_gene_list = ["TNF", "TNFR1", "TNFR2", "NFKB1", "TP53", "MDM2", "CASP3", "CASP8", "MYC", "CCND1"]

# State
initial_state_scenario_1 = State('scenario_1_multiscale')
initial_state_scenario_1.tnf_gene_list = _gene_list
initial_state_scenario_1.omnipath_available = True

# Problem
problems['scenario_1_multiscale'] = (
    initial_state_scenario_1,
    [('m_multiscale_tnf_cancer_modeling',)],
    'Multiscale TNF cancer modeling workflow -> 12 actions'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems

