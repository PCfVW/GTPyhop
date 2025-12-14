"""
Problem definitions for the Drug Target Discovery Pipeline example.
-- Generated 2025-12-09

This file defines initial states for drug target discovery workflows.
The workflow demonstrates coordination between 8 MCP servers:
  - OpenTargets: Disease-target associations
  - UniProt: Protein information
  - Reactome: Pathway biology
  - PDB: Protein structures
  - AlphaFold: Structure predictions
  - ChEMBL: Drug/compound data
  - PubMed: Literature search
  - KEGG: Pathway/gene data

Scenarios:
  - scenario_1_breast_cancer: Breast cancer drug target discovery -> ~15 actions
  - scenario_2_alzheimers: Alzheimer's disease investigation -> ~15 actions
  - scenario_3_diabetes: Type 2 diabetes metabolic targets -> ~15 actions
"""

import sys
import os
from typing import Dict, Tuple, List, Any

# Secure GTPyhop import strategy
try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import State
    except ImportError as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def h_create_initial_state(name: str, disease: str = "") -> State:
    """
    Helper function to create initial state for drug target discovery.

    Args:
        name: State name identifier
        disease: Target disease name (optional)

    Returns:
        Configured gtpyhop.State object with all required properties
    """
    state = State(name)

    # Disease information
    state.target_disease = disease
    state.disease_id = ""
    state.disease_info = {}

    # Target tracking
    state.disease_targets = []
    state.validated_proteins = []

    # Pathway information
    state.pathways = []
    state.pathway_details = {}

    # Structure information
    state.pdb_structures = []
    state.alphafold_structures = []

    # Compound information
    state.compounds = []
    state.compound_activities = []

    # Literature
    state.literature = []

    # Workflow flags (ENABLERS)
    state.disease_search_completed = False
    state.targets_retrieved = False
    state.proteins_validated = False
    state.pathways_analyzed = False
    state.structures_retrieved = False
    state.compounds_found = False
    state.literature_gathered = False

    # Execution tracking
    state.servers_called = []
    state.api_calls = 0

    return state


# =============================================================================
# SCENARIOS
# =============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: drug_target_discovery

# BEGIN: Scenario: scenario_1_breast_cancer
# Configuration
_disease = "breast cancer"

# State
initial_state_scenario_1 = h_create_initial_state('scenario_1_breast_cancer', _disease)

# Problem
problems['scenario_1_breast_cancer'] = (
    initial_state_scenario_1,
    [('m_drug_target_discovery', _disease)],
    f"""Breast Cancer Drug Target Discovery Pipeline

This problem demonstrates a complete drug target discovery workflow for
{_disease}, orchestrating 8 MCP servers to:
1. Search OpenTargets for {_disease} disease information
2. Retrieve associated therapeutic targets
3. Validate targets with UniProt protein data
4. Analyze pathway context via Reactome
5. Get structural data from PDB and AlphaFold
6. Find existing compounds in ChEMBL
7. Gather supporting literature from PubMed"""
)
# END: Scenario

# BEGIN: Scenario: scenario_2_alzheimers
# Configuration
_disease = "Alzheimer's disease"

# State
initial_state_scenario_2 = h_create_initial_state('scenario_2_alzheimers', _disease)

# Problem
problems['scenario_2_alzheimers'] = (
    initial_state_scenario_2,
    [('m_drug_target_discovery', _disease)],
    f"""{_disease} Drug Target Discovery Pipeline

Investigates {_disease} for potential therapeutic targets,
focusing on neurodegeneration pathways and amyloid-related proteins.
Orchestrates 8 MCP servers to identify and validate drug targets."""
)
# END: Scenario

# BEGIN: Scenario: scenario_3_diabetes
# Configuration
_disease = "type 2 diabetes"

# State
initial_state_scenario_3 = h_create_initial_state('scenario_3_diabetes', _disease)

# Problem
problems['scenario_3_diabetes'] = (
    initial_state_scenario_3,
    [('m_drug_target_discovery', _disease)],
    f"""Type 2 Diabetes Drug Target Discovery Pipeline

Investigates {_disease} for metabolic pathway targets,
focusing on insulin signaling and glucose metabolism.
Orchestrates 8 MCP servers to discover therapeutic targets."""
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

