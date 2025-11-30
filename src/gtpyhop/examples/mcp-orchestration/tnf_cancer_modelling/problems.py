"""
Problem definitions for the TNF Cancer Modeling example.
-- Generated 2025-11-26

This file defines initial states for the multiscale TNF cancer modeling workflow.
The workflow integrates Boolean network modeling (MaBoSS) with agent-based 
multicellular simulation (PhysiCell) to study TNF-induced cancer cell fate decisions.
"""

import sys
import os

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
# PROBLEM
# ============================================================================

# BEGIN: Domain: tnf_cancer_modelling

# BEGIN: Initial State: multiscale_cancer_initial
# ===== [SCENARIO 1] Multiscale TNF Cancer Modeling --------------------------
initial_state_scenario_1 = State('multiscale_cancer_initial')

# Set required initial conditions
initial_state_scenario_1.tnf_gene_list = ["TNF", "TNFR1", "TNFR2", "NFKB1", "TP53", "MDM2", "CASP3", "CASP8", "MYC", "CCND1"]
initial_state_scenario_1.omnipath_available = True
# END: Initial State

# END: Domain

