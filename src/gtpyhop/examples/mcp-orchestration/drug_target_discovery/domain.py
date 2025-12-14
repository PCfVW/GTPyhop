"""
Drug Target Discovery Pipeline - GTPyhop Domain.

Domain: drug_target_discovery
Version: 1.0.0
MCP Servers: opentargets, uniprot, reactome, pdb, alphafold, chembl, pubmed, kegg

This domain implements HTN planning for drug target discovery workflows,
orchestrating 8 real MCP servers from the Augmented Nature ecosystem.

This represents pioneering work - the first real-world orchestration of
multiple MCP servers using HTN (Hierarchical Task Network) Planning.

Actions (10):
    - a_search_disease: Search for disease by name (OpenTargets)
    - a_get_disease_targets: Get targets associated with disease (OpenTargets)
    - a_get_protein_by_gene: Find protein by gene symbol (UniProt)
    - a_get_protein_info: Get detailed protein information (UniProt)
    - a_find_pathways_by_gene: Find pathways containing gene (Reactome)
    - a_get_kegg_pathway: Get KEGG pathway information (KEGG)
    - a_get_pdb_structures: Search PDB by UniProt accession (PDB)
    - a_get_alphafold_structure: Get AlphaFold structure prediction (AlphaFold)
    - a_get_compounds_for_target: Find compounds for target (ChEMBL)
    - a_search_literature: Search PubMed articles (PubMed)

Methods (6):
    - m_drug_target_discovery: Top-level orchestration method
    - m_validate_targets: Validate targets with protein information
    - m_analyze_pathways: Analyze pathway context
    - m_get_structures: Retrieve structural information
    - m_find_compounds: Find drug compounds for targets
    - m_gather_literature: Gather supporting literature
"""

import sys
import os
from typing import Optional, Union, List, Tuple, Dict, Any

# Secure GTPyhop import strategy
try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
    except ImportError as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)


# =============================================================================
# DOMAIN
# =============================================================================
the_domain = Domain("drug_target_discovery")
set_current_domain(the_domain)
DOMAIN_NAME = "drug_target_discovery"  # For reference in other parts of the code


# =============================================================================
# STATE PROPERTY MAP
# =============================================================================
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Step 1: a_search_disease
#  (P) target_disease: str [DATA] - disease name to search
#  (E) disease_id: str [DATA] - found disease identifier
#  (E) disease_info: Dict [DATA] - disease metadata
#  (E) disease_search_completed: bool [ENABLER] - gates get_disease_targets
#
# Step 2: a_get_disease_targets
#  (P) disease_search_completed: bool [ENABLER]
#  (P) disease_id: str [DATA]
#  (E) disease_targets: List[Dict] [DATA] - list of target info
#  (E) targets_retrieved: bool [ENABLER] - gates validate_targets
#
# Step 3: a_get_protein_by_gene
#  (P) targets_retrieved: bool [ENABLER]
#  (E) validated_proteins: List[Dict] [DATA] - protein info with accessions
#  (E) proteins_validated: bool [ENABLER] - gates analyze_pathways
#
# Step 4: a_find_pathways_by_gene / a_get_kegg_pathway
#  (P) proteins_validated: bool [ENABLER]
#  (E) pathways: List[Dict] [DATA] - pathway information
#  (E) pathways_analyzed: bool [ENABLER] - gates get_structures
#
# Step 5: a_get_pdb_structures / a_get_alphafold_structure
#  (P) proteins_validated: bool [ENABLER]
#  (E) pdb_structures: List[Dict] [DATA]
#  (E) alphafold_structures: List[Dict] [DATA]
#  (E) structures_retrieved: bool [ENABLER] - gates find_compounds
#
# Step 6: a_get_compounds_for_target
#  (P) proteins_validated: bool [ENABLER]
#  (E) compounds: List[Dict] [DATA]
#  (E) compounds_found: bool [ENABLER] - gates gather_literature
#
# Step 7: a_search_literature
#  (E) literature: List[Dict] [DATA]
#  (E) literature_gathered: bool [ENABLER] - workflow complete
# =============================================================================


# =============================================================================
# BEGIN: Actions
# =============================================================================

# --- Action: a_search_disease ---

def a_search_disease(state: State, query: str, size: int = 25) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: opentargets-server:search_diseases

    Action signature:
        a_search_disease(state, query, size)

    Action parameters:
        query: Disease name or term to search for (e.g., 'breast cancer')
        size: Maximum number of results to return (default: 25)

    Action purpose:
        Search OpenTargets database for diseases matching the query

    Preconditions:
        - Query must be a non-empty string

    Effects:
        - Disease search results stored (state.disease_info) [DATA]
        - Disease ID extracted (state.disease_id) [DATA]
        - Disease search completed flag (state.disease_search_completed) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(query, str):
        return False
    if not isinstance(size, int):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not query.strip():
        return False
    if size < 1:
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No state preconditions - this is the first action in the pipeline
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Store the search query
    state.target_disease = query

    # [DATA] Disease search results (populated by MCP server at runtime)
    # Placeholder structure for planning - actual data comes from server
    state.disease_info = {
        "query": query,
        "size": size,
        "results": [],  # Populated by MCP server
        "source": "opentargets"
    }

    # [DATA] Disease ID will be extracted from results
    # For planning, we set a placeholder that indicates search was performed
    state.disease_id = f"disease_id_for_{query.replace(' ', '_')}"

    # [ENABLER] Gates a_get_disease_targets
    state.disease_search_completed = True
    # END: Effects

    return state


# --- Action: a_get_disease_targets ---

def a_get_disease_targets(state: State, disease_id: str, size: int = 50) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: opentargets-server:get_disease_targets_summary

    Action signature:
        a_get_disease_targets(state, disease_id, size)

    Action parameters:
        disease_id: OpenTargets disease ID (e.g., 'EFO_0000305' for breast cancer)
        size: Maximum number of targets to return (default: 50)

    Action purpose:
        Retrieve prioritized therapeutic targets associated with the disease

    Preconditions:
        - Disease search must be completed (state.disease_search_completed)
        - Disease ID must be available (state.disease_id)

    Effects:
        - Target list stored (state.disease_targets) [DATA]
        - Targets retrieved flag (state.targets_retrieved) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(disease_id, str):
        return False
    if not isinstance(size, int):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not disease_id.strip():
        return False
    if size < 1:
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Disease search must be completed first
    if not (hasattr(state, 'disease_search_completed') and state.disease_search_completed):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Store disease targets (populated by MCP server at runtime)
    # Placeholder structure for planning
    state.disease_targets = []  # Will contain target dicts with gene_symbol, id, score, etc.

    # [DATA] Track the query parameters
    state.targets_query = {
        "disease_id": disease_id,
        "size": size
    }

    # [ENABLER] Gates m_validate_targets
    state.targets_retrieved = True
    # END: Effects

    return state


# --- Action: a_get_protein_by_gene ---

def a_get_protein_by_gene(state: State, gene: str, organism: str = "human") -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: uniprot-server:search_by_gene

    Action signature:
        a_get_protein_by_gene(state, gene, organism)

    Action parameters:
        gene: Gene symbol to search for (e.g., 'BRCA1', 'TP53')
        organism: Organism filter (default: 'human')

    Action purpose:
        Find UniProt protein entries for a given gene symbol

    Preconditions:
        - Targets must be retrieved first (state.targets_retrieved)

    Effects:
        - Protein information added to validated list (state.validated_proteins) [DATA]
        - Proteins validated flag set (state.proteins_validated) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(gene, str):
        return False
    if not isinstance(organism, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not gene.strip():
        return False
    if not organism.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Targets must be retrieved first
    if not (hasattr(state, 'targets_retrieved') and state.targets_retrieved):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Initialize validated_proteins if not exists
    if not hasattr(state, 'validated_proteins') or state.validated_proteins is None:
        state.validated_proteins = []

    # [DATA] Add protein info to validated list (populated by MCP server at runtime)
    protein_info = {
        "gene": gene,
        "organism": organism,
        "accession": "",  # Populated by MCP server
        "protein_name": "",  # Populated by MCP server
        "source": "uniprot"
    }
    state.validated_proteins.append(protein_info)

    # [ENABLER] Gates m_analyze_pathways
    state.proteins_validated = True
    # END: Effects

    return state


# --- Action: a_get_protein_info ---

def a_get_protein_info(state: State, accession: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: uniprot-server:get_protein_info

    Action signature:
        a_get_protein_info(state, accession)

    Action parameters:
        accession: UniProt accession number (e.g., 'P04637' for TP53)

    Action purpose:
        Get detailed protein information from UniProt

    Preconditions:
        - Targets must be retrieved first (state.targets_retrieved)

    Effects:
        - Protein details added to validated list (state.validated_proteins) [DATA]
        - Proteins validated flag set (state.proteins_validated) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(accession, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not accession.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Targets must be retrieved first
    if not (hasattr(state, 'targets_retrieved') and state.targets_retrieved):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Initialize validated_proteins if not exists
    if not hasattr(state, 'validated_proteins') or state.validated_proteins is None:
        state.validated_proteins = []

    # [DATA] Add detailed protein info (populated by MCP server at runtime)
    protein_details = {
        "accession": accession,
        "gene": "",  # Populated by MCP server
        "protein_name": "",  # Populated by MCP server
        "function": "",  # Populated by MCP server
        "sequence_length": 0,  # Populated by MCP server
        "source": "uniprot"
    }
    state.validated_proteins.append(protein_details)

    # [ENABLER] Gates m_analyze_pathways
    state.proteins_validated = True
    # END: Effects

    return state


# --- Action: a_find_pathways_by_gene ---

def a_find_pathways_by_gene(state: State, gene: str, species: str = "Homo sapiens") -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: reactome-server:find_pathways_by_gene

    Action signature:
        a_find_pathways_by_gene(state, gene, species)

    Action parameters:
        gene: Gene symbol to search for (e.g., 'BRCA1')
        species: Species name (default: 'Homo sapiens')

    Action purpose:
        Find biological pathways containing the specified gene

    Preconditions:
        - Proteins must be validated first (state.proteins_validated)

    Effects:
        - Pathway information added (state.pathways) [DATA]
        - Pathways analyzed flag set (state.pathways_analyzed) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(gene, str):
        return False
    if not isinstance(species, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not gene.strip():
        return False
    if not species.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Proteins must be validated first
    if not (hasattr(state, 'proteins_validated') and state.proteins_validated):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Initialize pathways list if not exists
    if not hasattr(state, 'pathways') or state.pathways is None:
        state.pathways = []

    # [DATA] Add pathway info (populated by MCP server at runtime)
    pathway_info = {
        "gene": gene,
        "species": species,
        "pathway_id": "",  # Populated by MCP server
        "pathway_name": "",  # Populated by MCP server
        "source": "reactome"
    }
    state.pathways.append(pathway_info)

    # [ENABLER] Gates m_get_structures
    state.pathways_analyzed = True
    # END: Effects

    return state


# --- Action: a_get_kegg_pathway ---

def a_get_kegg_pathway(state: State, pathway_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: kegg-server:get_pathway_info

    Action signature:
        a_get_kegg_pathway(state, pathway_id)

    Action parameters:
        pathway_id: KEGG pathway identifier (e.g., 'hsa04110' for cell cycle)

    Action purpose:
        Get detailed pathway information from KEGG

    Preconditions:
        - Proteins must be validated first (state.proteins_validated)

    Effects:
        - Pathway details stored (state.pathway_details) [DATA]
        - Pathways analyzed flag set (state.pathways_analyzed) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(pathway_id, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not pathway_id.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Proteins must be validated first
    if not (hasattr(state, 'proteins_validated') and state.proteins_validated):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Initialize pathway_details dict if not exists
    if not hasattr(state, 'pathway_details') or state.pathway_details is None:
        state.pathway_details = {}

    # [DATA] Store pathway details (populated by MCP server at runtime)
    state.pathway_details[pathway_id] = {
        "pathway_id": pathway_id,
        "name": "",  # Populated by MCP server
        "description": "",  # Populated by MCP server
        "genes": [],  # Populated by MCP server
        "source": "kegg"
    }

    # [ENABLER] Gates m_get_structures
    state.pathways_analyzed = True
    # END: Effects

    return state


# --- Action: a_get_pdb_structures ---

def a_get_pdb_structures(state: State, uniprot_accession: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: pdb-server:search_by_uniprot

    Action signature:
        a_get_pdb_structures(state, uniprot_accession)

    Action parameters:
        uniprot_accession: UniProt accession number to search PDB for

    Action purpose:
        Find experimentally determined protein structures from PDB

    Preconditions:
        - Proteins must be validated first (state.proteins_validated)

    Effects:
        - PDB structure information stored (state.pdb_structures) [DATA]
        - Structures retrieved flag set (state.structures_retrieved) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(uniprot_accession, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not uniprot_accession.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Proteins must be validated first
    if not (hasattr(state, 'proteins_validated') and state.proteins_validated):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Initialize pdb_structures list if not exists
    if not hasattr(state, 'pdb_structures') or state.pdb_structures is None:
        state.pdb_structures = []

    # [DATA] Add PDB structure info (populated by MCP server at runtime)
    structure_info = {
        "uniprot_accession": uniprot_accession,
        "pdb_id": "",  # Populated by MCP server
        "resolution": None,  # Populated by MCP server
        "method": "",  # Populated by MCP server (X-ray, NMR, Cryo-EM)
        "source": "pdb"
    }
    state.pdb_structures.append(structure_info)

    # [ENABLER] Gates m_find_compounds
    state.structures_retrieved = True
    # END: Effects

    return state


# --- Action: a_get_alphafold_structure ---

def a_get_alphafold_structure(state: State, uniprot_accession: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: alphafold-server:get_structure

    Action signature:
        a_get_alphafold_structure(state, uniprot_accession)

    Action parameters:
        uniprot_accession: UniProt accession number to get AlphaFold prediction for

    Action purpose:
        Get AlphaFold structure prediction for a protein

    Preconditions:
        - Proteins must be validated first (state.proteins_validated)

    Effects:
        - AlphaFold structure information stored (state.alphafold_structures) [DATA]
        - Structures retrieved flag set (state.structures_retrieved) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(uniprot_accession, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not uniprot_accession.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Proteins must be validated first
    if not (hasattr(state, 'proteins_validated') and state.proteins_validated):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Initialize alphafold_structures list if not exists
    if not hasattr(state, 'alphafold_structures') or state.alphafold_structures is None:
        state.alphafold_structures = []

    # [DATA] Add AlphaFold structure info (populated by MCP server at runtime)
    structure_info = {
        "uniprot_accession": uniprot_accession,
        "model_url": "",  # Populated by MCP server
        "plddt_score": None,  # Populated by MCP server (confidence score)
        "source": "alphafold"
    }
    state.alphafold_structures.append(structure_info)

    # [ENABLER] Gates m_find_compounds
    state.structures_retrieved = True
    # END: Effects

    return state


# --- Action: a_get_compounds_for_target ---

def a_get_compounds_for_target(state: State, uniprot_accession: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: chembl-server:search_by_uniprot

    Action signature:
        a_get_compounds_for_target(state, uniprot_accession)

    Action parameters:
        uniprot_accession: UniProt accession number to find compounds for

    Action purpose:
        Find drug compounds that target the specified protein

    Preconditions:
        - Proteins must be validated first (state.proteins_validated)

    Effects:
        - Compound information stored (state.compounds) [DATA]
        - Compounds found flag set (state.compounds_found) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(uniprot_accession, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not uniprot_accession.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Proteins must be validated first
    if not (hasattr(state, 'proteins_validated') and state.proteins_validated):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Initialize compounds list if not exists
    if not hasattr(state, 'compounds') or state.compounds is None:
        state.compounds = []

    # [DATA] Add compound info (populated by MCP server at runtime)
    compound_info = {
        "target_accession": uniprot_accession,
        "chembl_id": "",  # Populated by MCP server
        "molecule_name": "",  # Populated by MCP server
        "mechanism": "",  # Populated by MCP server
        "source": "chembl"
    }
    state.compounds.append(compound_info)

    # [ENABLER] Gates m_gather_literature
    state.compounds_found = True
    # END: Effects

    return state


# --- Action: a_search_literature ---

def a_search_literature(state: State, query: str, max_results: int = 20) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: pubmed-server:search_articles

    Action signature:
        a_search_literature(state, query, max_results)

    Action parameters:
        query: Search query for PubMed (e.g., 'breast cancer BRCA1 therapeutic')
        max_results: Maximum number of articles to return (default: 20)

    Action purpose:
        Search PubMed for relevant scientific literature

    Preconditions:
        - None (can be called at any point for literature searches)

    Effects:
        - Literature results stored (state.literature) [DATA]
        - Literature gathered flag set (state.literature_gathered) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(query, str):
        return False
    if not isinstance(max_results, int):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not query.strip():
        return False
    if max_results < 1:
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No specific preconditions - literature search can happen at any time
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Initialize literature list if not exists
    if not hasattr(state, 'literature') or state.literature is None:
        state.literature = []

    # [DATA] Add literature search results (populated by MCP server at runtime)
    search_result = {
        "query": query,
        "max_results": max_results,
        "articles": [],  # Populated by MCP server
        "source": "pubmed"
    }
    state.literature.append(search_result)

    # [ENABLER] Workflow completion indicator
    state.literature_gathered = True
    # END: Effects

    return state


# =============================================================================
# END: Actions
# =============================================================================


# =============================================================================
# BEGIN: Methods
# =============================================================================

# --- Method: m_drug_target_discovery ---

def m_drug_target_discovery(state: State, disease_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_drug_target_discovery(state, disease_name)

    Method parameters:
        disease_name: Name of the disease to investigate (e.g., 'breast cancer')

    Method purpose:
        Top-level orchestration method for complete drug target discovery pipeline.
        Coordinates all 8 MCP servers through a hierarchical task decomposition.

    Preconditions:
        - disease_name is a non-empty string

    Task decomposition:
        - a_search_disease: Search for disease in OpenTargets
        - a_get_disease_targets: Get therapeutic targets for the disease
        - validate_targets: Validate targets with UniProt protein data
        - analyze_pathways: Analyze pathway context via Reactome
        - get_structures: Get structural data from PDB and AlphaFold
        - find_compounds: Find drug compounds in ChEMBL
        - gather_literature: Gather supporting literature from PubMed

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(disease_name, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not disease_name.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No state preconditions - this is the entry point method
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Use context variable templates for dynamic data chaining during execution.
    # Step 1 uses actual disease_name, subsequent steps use ${context.var} templates
    # that will be substituted with real extracted data by the execution engine.
    return [
        ("a_search_disease", disease_name),
        ("a_get_disease_targets", "${context.disease_id}"),  # From a_search_disease output
        ("m_validate_targets",),
        ("m_analyze_pathways",),
        ("m_get_structures",),
        ("m_find_compounds",),
        ("m_gather_literature", disease_name),
    ]
    # END: Task Decomposition


# --- Method: m_validate_targets ---

def m_validate_targets(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_validate_targets(state)

    Method parameters:
        None (uses state.disease_targets)

    Method auxiliary parameters:
        disease_targets: List[Dict] (inferred from state.disease_targets)

    Method purpose:
        Validate discovered targets by retrieving protein information from UniProt.
        Iterates over top targets and retrieves detailed protein data.

    Preconditions:
        - Targets must be retrieved (state.targets_retrieved)
        - Disease targets list must exist (state.disease_targets)

    Task decomposition:
        - a_get_protein_by_gene: For each target gene symbol (up to 5 targets)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional state-type checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if not hasattr(state, 'disease_targets'):
        return False
    disease_targets = state.disease_targets
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Targets must be retrieved first
    if not (hasattr(state, 'targets_retrieved') and state.targets_retrieved):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # For dynamic data chaining: use ${context.first_gene} from a_get_disease_targets output.
    # During planning, this validates the plan structure.
    # During execution, the middleware substitutes with real gene symbol.
    #
    # Note: For full multi-target iteration, a future version could use
    # ${context.target_genes[0]}, ${context.target_genes[1]}, etc.
    return [
        ("a_get_protein_by_gene", "${context.first_gene}"),
    ]
    # END: Task Decomposition


# --- Method: m_analyze_pathways ---

def m_analyze_pathways(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_analyze_pathways(state)

    Method parameters:
        None (uses state.validated_proteins)

    Method auxiliary parameters:
        validated_proteins: List[Dict] (inferred from state.validated_proteins)

    Method purpose:
        Analyze pathway context for validated proteins using Reactome.
        Identifies biological pathways containing the target genes.

    Preconditions:
        - Proteins must be validated (state.proteins_validated)
        - Validated proteins list must exist (state.validated_proteins)

    Task decomposition:
        - a_find_pathways_by_gene: For each validated protein gene (up to 3)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional state-type checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if not hasattr(state, 'validated_proteins'):
        return False
    validated_proteins = state.validated_proteins
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Proteins must be validated first
    if not (hasattr(state, 'proteins_validated') and state.proteins_validated):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Use context variable for dynamic data chaining.
    # ${context.first_gene} is extracted from a_get_disease_targets output.
    return [
        ("a_find_pathways_by_gene", "${context.first_gene}"),
    ]
    # END: Task Decomposition


# --- Method: m_get_structures ---

def m_get_structures(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_get_structures(state)

    Method parameters:
        None (uses state.validated_proteins)

    Method auxiliary parameters:
        validated_proteins: List[Dict] (inferred from state.validated_proteins)

    Method purpose:
        Retrieve structural information from PDB and AlphaFold for validated proteins.
        Gets both experimental structures and AlphaFold predictions.

    Preconditions:
        - Proteins must be validated (state.proteins_validated)
        - Validated proteins list must exist (state.validated_proteins)

    Task decomposition:
        - a_get_pdb_structures: For each protein accession
        - a_get_alphafold_structure: For each protein accession

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional state-type checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if not hasattr(state, 'validated_proteins'):
        return False
    validated_proteins = state.validated_proteins
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Proteins must be validated first
    if not (hasattr(state, 'proteins_validated') and state.proteins_validated):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Use context variable for dynamic data chaining.
    # ${context.uniprot_accession} is extracted from a_get_protein_by_gene output.
    return [
        ("a_get_pdb_structures", "${context.uniprot_accession}"),
        ("a_get_alphafold_structure", "${context.uniprot_accession}"),
    ]
    # END: Task Decomposition


# --- Method: m_find_compounds ---

def m_find_compounds(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_find_compounds(state)

    Method parameters:
        None (uses state.validated_proteins)

    Method auxiliary parameters:
        validated_proteins: List[Dict] (inferred from state.validated_proteins)

    Method purpose:
        Find drug compounds for validated protein targets using ChEMBL.
        Searches for known drugs and compounds that interact with each target.

    Preconditions:
        - Proteins must be validated (state.proteins_validated)
        - Validated proteins list must exist (state.validated_proteins)

    Task decomposition:
        - a_get_compounds_for_target: For each protein accession (up to 3)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional state-type checks
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if not hasattr(state, 'validated_proteins'):
        return False
    validated_proteins = state.validated_proteins
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Proteins must be validated first
    if not (hasattr(state, 'proteins_validated') and state.proteins_validated):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Use context variable for dynamic data chaining.
    # ${context.uniprot_accession} is extracted from a_get_protein_by_gene output.
    return [
        ("a_get_compounds_for_target", "${context.uniprot_accession}"),
    ]
    # END: Task Decomposition


# --- Method: m_gather_literature ---

def m_gather_literature(state: State, disease_name: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_gather_literature(state, disease_name)

    Method parameters:
        disease_name: Disease name for literature search context

    Method auxiliary parameters:
        validated_proteins: List[Dict] (inferred from state.validated_proteins)

    Method purpose:
        Gather supporting scientific literature from PubMed.
        Searches for disease-related publications and target-specific articles.

    Preconditions:
        - disease_name must be a non-empty string

    Task decomposition:
        - a_search_literature: Search for disease + drug target articles
        - a_search_literature: Search for each validated gene + therapeutic articles

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(disease_name, str):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not disease_name.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    validated_proteins = getattr(state, 'validated_proteins', [])
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No strict preconditions - literature search can happen anytime
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Primary search: disease + drug target
    # Use the actual disease_name passed to this method
    return [
        ("a_search_literature", f"{disease_name} drug target therapeutic"),
    ]
    # END: Task Decomposition


# =============================================================================
# END: Methods
# =============================================================================

# =============================================================================
# DECLARE ACTIONS TO DOMAIN
# =============================================================================

# Declare all 10 actions to the current domain
declare_actions(
    # OpenTargets server (2 actions)
    a_search_disease,
    a_get_disease_targets,
    # UniProt server (2 actions)
    a_get_protein_by_gene,
    a_get_protein_info,
    # Reactome server (1 action)
    a_find_pathways_by_gene,
    # KEGG server (1 action)
    a_get_kegg_pathway,
    # PDB server (1 action)
    a_get_pdb_structures,
    # AlphaFold server (1 action)
    a_get_alphafold_structure,
    # ChEMBL server (1 action)
    a_get_compounds_for_target,
    # PubMed server (1 action)
    a_search_literature,
)

# =============================================================================
# DECLARE METHODS TO DOMAIN
# =============================================================================

# Declare all 6 methods with their task names
declare_task_methods("m_drug_target_discovery", m_drug_target_discovery)
declare_task_methods("m_validate_targets", m_validate_targets)
declare_task_methods("m_analyze_pathways", m_analyze_pathways)
declare_task_methods("m_get_structures", m_get_structures)
declare_task_methods("m_find_compounds", m_find_compounds)
declare_task_methods("m_gather_literature", m_gather_literature)
