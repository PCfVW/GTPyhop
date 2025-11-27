# ============================================================================
# MCP Orchestration - TNF Cancer Modelling Domain
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - State Property Map
#   - Actions (12)
#   - Methods (14)
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

# -------------------- Smart GTPyhop import strategy with secure path handling
import sys
import os
from typing import Optional, Union, List, Tuple, Dict

def safe_add_to_path(relative_path: str) -> Optional[str]:
    """
    Safely add a relative path to sys.path with validation to prevent path traversal attacks.

    Args:
        relative_path: Relative path to add to sys.path

    Returns:
        The absolute path that was added, or None if validation failed

    Raises:
        ValueError: If path traversal is detected
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))

    # Validate the path is within expected boundaries to prevent path traversal
    if not target_path.startswith(os.path.dirname(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")

    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

# ----- Secure GTPyhop import strategy - tries PyPI first, falls back to local
try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    # Fallback to local development with secure path handling
    try:
        safe_add_to_path(os.path.join('..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
    except (ImportError, ValueError) as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("tnf_cancer_modelling")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP (Scenario 1: Multiscale TNF Cancer Modeling)
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Step 1: a_create_tnf_cancer_network
#  (P) tnf_gene_list [ENABLER]
#  (P) omnipath_available [ENABLER]
#  (E) raw_network_file: str [DATA]
#  (E) network_components: List[str] [DATA]
#  (E) network_creation_status: "completed" [ENABLER]
#  (E) current_workflow_step: "network_created" [DATA]
#
# Step 2: a_remove_bimodal_interactions
#  (P) raw_network_file == network_file_path [ENABLER]
#  (P) network_creation_status == "completed" [ENABLER]
#  (E) cleaned_network_file: str [DATA]
#  (E) bimodal_interactions_removed: True [ENABLER]
#  (E) boolean_compatibility: True [DATA]
#  (E) current_workflow_step: "network_simplified" [DATA]
#
# Step 3: a_check_network_connectivity
#  (P) cleaned_network_file == network_file_path [ENABLER]
#  (P) bimodal_interactions_removed is True [ENABLER]
#  (E) network_connectivity_checked: True [DATA]
#  (E) network_is_connected: True [ENABLER]
#  (E) connectivity_verification_status: "passed" [ENABLER]
#  (E) current_workflow_step: "connectivity_verified" [DATA]
#
# Step 4: a_export_network_to_bnet
#  (P) cleaned_network_file == network_file_path [ENABLER]
#  (P) network_is_connected is True [ENABLER]
#  (P) connectivity_verification_status == "passed" [ENABLER]
#  (E) bnet_file_path: str [DATA]
#  (E) bnet_format_ready: True [ENABLER]
#  (E) boolean_modeling_ready: True [ENABLER]
#  (E) current_workflow_step: "bnet_exported" [DATA]
#  (E) network_construction_phase_complete: True [DATA]
#
# Step 5: a_create_maboss_files
#  (P) bnet_file_path == input bnet_file_path [ENABLER]
#  (P) bnet_format_ready is True [ENABLER]
#  (P) boolean_modeling_ready is True [ENABLER]
#  (E) maboss_bnd_file: str [DATA]
#  (E) maboss_cfg_file: str [DATA]
#  (E) maboss_thread_count: int [DATA]
#  (E) maboss_files_created: True [ENABLER]
#  (E) current_workflow_step: "maboss_files_created" [DATA]
#
# Step 6: a_run_maboss_simulation
#  (P) maboss_bnd_file == bnd_file_path [ENABLER]
#  (P) maboss_cfg_file == cfg_file_path [ENABLER]
#  (P) maboss_files_created is True [ENABLER]
#  (E) maboss_simulation_results: str [DATA]
#  (E) state_probability_trajectories: True [DATA]
#  (E) apoptosis_output_nodes: List[str] [DATA]
#  (E) proliferation_output_nodes: List[str] [DATA]
#  (E) maboss_simulation_completed: True [ENABLER]
#  (E) current_workflow_step: "maboss_simulation_completed" [DATA]
#
# (Continued below...)
# ============================================================================

# ============================================================================
# ACTIONS (12)
# ----------------------------------------------------------------------------

# ============================================================================
# MULTISCALE CANCER MODELING WORKFLOW ACTIONS - PART 1: NETWORK CONSTRUCTION
# Generated Actions for Steps 1-4 of the Comprehensive Multiscale TNF Cancer Modeling Workflow
# ============================================================================

# ============================================================================
# ACTIONS FOR NETWORK CONSTRUCTION PHASE (Steps 1-4)
# ============================================================================

def a_create_tnf_cancer_network(state: State, gene_list: List[str], organism: str = "human") -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: neko:create_network

    Action signature:
        a_create_tnf_cancer_network(state, gene_list, organism)

    Action parameters:
        gene_list: list of TNF-related gene symbols
        organism: target organism (default: "human")

    Action purpose:
        Generate initial network capturing TNF signaling pathways affecting cancer cell fate

    Preconditions:
        - TNF-related gene list is defined (state.tnf_gene_list)
        - Omnipath database access is available (state.omnipath_available)

    Effects:
        - Raw interaction network file is created (state.raw_network_file)
        - Network components are identified (state.network_components)
        - Network creation status is set to completed (state.network_creation_status) [ENABLER]
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(gene_list, list): return False
    if not all(isinstance(x, str) for x in gene_list): return False
    if not isinstance(organism, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not all(gene.strip() for gene in gene_list): return False
    if organism not in ["human", "mouse"]: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # TNF-related gene list is defined and Omnipath database access is available
    if not (hasattr(state, 'tnf_gene_list') and state.tnf_gene_list):
        return False
    if not (hasattr(state, 'omnipath_available') and state.omnipath_available):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Raw interaction network file path
    state.raw_network_file = f"tnf_network_{organism}.sif"

    # [DATA] Network components for validation
    state.network_components = ["TNF_sensing", "apoptosis", "proliferation"]

    # [ENABLER] Network creation completed - gates a_remove_bimodal_interactions
    state.network_creation_status = "completed"

    # [DATA] Workflow tracking
    state.current_workflow_step = "network_created"
    # END: Effects

    return state


def a_remove_bimodal_interactions(state: State, network_file_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: neko:remove_bimodal_interactions

    Action signature:
        a_remove_bimodal_interactions(state, network_file_path)

    Action parameters:
        network_file_path: path to the raw network file

    Action purpose:
        Clean network by removing bimodal interactions for Boolean compatibility

    Preconditions:
        - Raw network file exists and matches expected path (state.raw_network_file)
        - Network creation is completed (state.network_creation_status == "completed")

    Effects:
        - Cleaned network file is created (state.cleaned_network_file)
        - Bimodal interactions removal flag is set (state.bimodal_interactions_removed) [ENABLER]
        - Boolean compatibility flag is set (state.boolean_compatibility)
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(network_file_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'raw_network_file') and state.raw_network_file == network_file_path):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Raw network file exists from previous step
    if not (hasattr(state, 'network_creation_status') and state.network_creation_status == "completed"):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Cleaned network file path
    state.cleaned_network_file = network_file_path.replace('.sif', '_cleaned.sif')

    # [ENABLER] Bimodal interactions removed - gates a_check_network_connectivity
    state.bimodal_interactions_removed = True

    # [DATA] Boolean compatibility confirmed
    state.boolean_compatibility = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "network_simplified"
    # END: Effects

    return state


def a_check_network_connectivity(state: State, network_file_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: neko:check_disconnected_nodes

    Action signature:
        a_check_network_connectivity(state, network_file_path)

    Action parameters:
        network_file_path: path to the cleaned network file

    Action purpose:
        Ensure network forms a single connected component for proper signal propagation in Boolean model

    Preconditions:
        - Cleaned network file exists and matches expected path (state.cleaned_network_file)
        - Bimodal interactions have been removed (state.bimodal_interactions_removed)

    Effects:
        - Network connectivity check is completed (state.network_connectivity_checked)
        - Network is connected flag is set (state.network_is_connected) [ENABLER]
        - Connectivity verification status is set (state.connectivity_verification_status) [ENABLER]
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(network_file_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'cleaned_network_file') and state.cleaned_network_file == network_file_path):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Cleaned network file exists from previous step
    if not (hasattr(state, 'bimodal_interactions_removed') and state.bimodal_interactions_removed):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Connectivity check completed
    state.network_connectivity_checked = True

    # [ENABLER] Network is connected - gates a_export_network_to_bnet
    state.network_is_connected = True

    # [ENABLER] Connectivity verification passed - gates a_export_network_to_bnet
    state.connectivity_verification_status = "passed"

    # [DATA] Workflow tracking
    state.current_workflow_step = "connectivity_verified"
    # END: Effects

    return state


def a_export_network_to_bnet(state: State, network_file_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: neko:export_to_bnet

    Action signature:
        a_export_network_to_bnet(state, network_file_path)

    Action parameters:
        network_file_path: path to the connected network file

    Action purpose:
        Convert network to BNET format for MaBoSS compatibility

    Preconditions:
        - Cleaned network file exists and matches expected path (state.cleaned_network_file)
        - Network is confirmed connected (state.network_is_connected)
        - Connectivity verification has passed (state.connectivity_verification_status == "passed")

    Effects:
        - BNET file is generated (state.bnet_file_path)
        - BNET format ready flag is set (state.bnet_format_ready) [ENABLER]
        - Boolean modeling ready flag is set (state.boolean_modeling_ready) [ENABLER]
        - Workflow step is updated (state.current_workflow_step)
        - Network construction phase complete flag is set (state.network_construction_phase_complete)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(network_file_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'cleaned_network_file') and state.cleaned_network_file == network_file_path):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Network is confirmed connected and verified
    if not (hasattr(state, 'network_is_connected') and state.network_is_connected):
        return False
    if not (hasattr(state, 'connectivity_verification_status') and state.connectivity_verification_status == "passed"):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] BNET file path
    state.bnet_file_path = network_file_path.replace('.sif', '.bnet')

    # [ENABLER] BNET format ready - gates a_create_maboss_files
    state.bnet_format_ready = True

    # [ENABLER] Boolean modeling ready - gates a_create_maboss_files
    state.boolean_modeling_ready = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "bnet_exported"

    # [DATA] Phase completion marker
    state.network_construction_phase_complete = True
    # END: Effects

    return state

# ============================================================================
# MULTISCALE CANCER MODELING WORKFLOW ACTIONS - PART 2: BOOLEAN MODELING
# Generated Actions for Steps 5-7 of the Comprehensive Multiscale TNF Cancer Modeling Workflow
# ============================================================================

# ============================================================================
# ACTIONS FOR BOOLEAN NETWORK MODELING PHASE (Steps 5-7)
# ============================================================================

def a_create_maboss_files(state: State, bnet_file_path: str, thread_count: int = 10) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: maboss:create_maboss_files

    Action signature:
        a_create_maboss_files(state, bnet_file_path, thread_count)

    Action parameters:
        bnet_file_path: path to the BNET file
        thread_count: number of threads for simulation (default: 10)

    Action purpose:
        Generate MaBoSS configuration and network definition files

    Preconditions:
        - BNET file exists and matches expected path (state.bnet_file_path)
        - BNET format is ready (state.bnet_format_ready)
        - Boolean modeling is ready (state.boolean_modeling_ready)

    Effects:
        - MaBoSS .bnd file is created (state.maboss_bnd_file)
        - MaBoSS .cfg file is created (state.maboss_cfg_file)
        - Thread count is configured (state.maboss_thread_count)
        - MaBoSS files created flag is set (state.maboss_files_created) [ENABLER]
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(bnet_file_path, str): return False
    if not isinstance(thread_count, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'bnet_file_path') and state.bnet_file_path == bnet_file_path):
        return False
    if not (thread_count > 0):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Valid BNET file exists and Boolean modeling is ready
    if not (hasattr(state, 'bnet_format_ready') and state.bnet_format_ready):
        return False
    if not (hasattr(state, 'boolean_modeling_ready') and state.boolean_modeling_ready):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] MaBoSS network definition file
    state.maboss_bnd_file = bnet_file_path.replace('.bnet', '.bnd')

    # [DATA] MaBoSS configuration file
    state.maboss_cfg_file = bnet_file_path.replace('.bnet', '.cfg')

    # [DATA] Thread count for simulation
    state.maboss_thread_count = thread_count

    # [ENABLER] MaBoSS files created - gates a_run_maboss_simulation
    state.maboss_files_created = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "maboss_files_created"
    # END: Effects

    return state


def a_run_maboss_simulation(state: State, bnd_file_path: str, cfg_file_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: maboss:run_simulation

    Action signature:
        a_run_maboss_simulation(state, bnd_file_path, cfg_file_path)

    Action parameters:
        bnd_file_path: path to MaBoSS network definition file
        cfg_file_path: path to MaBoSS configuration file

    Action purpose:
        Execute Boolean network simulation to analyze cell fate dynamics

    Preconditions:
        - MaBoSS .bnd file exists and matches expected path (state.maboss_bnd_file)
        - MaBoSS .cfg file exists and matches expected path (state.maboss_cfg_file)
        - MaBoSS files have been created (state.maboss_files_created)

    Effects:
        - Simulation results file is created (state.maboss_simulation_results)
        - State probability trajectories are available (state.state_probability_trajectories)
        - Apoptosis output nodes are identified (state.apoptosis_output_nodes)
        - Proliferation output nodes are identified (state.proliferation_output_nodes)
        - MaBoSS simulation completed flag is set (state.maboss_simulation_completed) [ENABLER]
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(bnd_file_path, str): return False
    if not isinstance(cfg_file_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'maboss_bnd_file') and state.maboss_bnd_file == bnd_file_path):
        return False
    if not (hasattr(state, 'maboss_cfg_file') and state.maboss_cfg_file == cfg_file_path):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # MaBoSS .bnd and .cfg files exist
    if not (hasattr(state, 'maboss_files_created') and state.maboss_files_created):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Simulation results file path
    state.maboss_simulation_results = f"{bnd_file_path.replace('.bnd', '_results.txt')}"

    # [DATA] State probability trajectories available
    state.state_probability_trajectories = True

    # [DATA] Apoptosis output nodes
    state.apoptosis_output_nodes = ["apoptosis", "cell_death", "CASP3", "CASP8"]

    # [DATA] Proliferation output nodes
    state.proliferation_output_nodes = ["proliferation", "cell_cycle", "MYC", "CCND1"]

    # [ENABLER] MaBoSS simulation completed - gates a_analyze_maboss_results
    state.maboss_simulation_completed = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "maboss_simulation_completed"
    # END: Effects

    return state


def a_analyze_maboss_results(state: State, results_file_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: maboss:analyze_results

    Action signature:
        a_analyze_maboss_results(state, results_file_path)

    Action parameters:
        results_file_path: path to MaBoSS simulation results file

    Action purpose:
        Validate biological accuracy of Boolean network behavior

    Preconditions:
        - MaBoSS simulation results exist and match expected path (state.maboss_simulation_results)
        - MaBoSS simulation has been completed (state.maboss_simulation_completed)
        - State probability trajectories are available (state.state_probability_trajectories)

    Effects:
        - Network behavior is assessed (state.network_behavior_assessed)
        - Biological plausibility is validated (state.biological_plausibility_validated)
        - Key cell fate nodes are identified (state.key_cell_fate_nodes)
        - Model validation status is set (state.model_validation_status) [ENABLER]
        - Boolean modeling phase complete flag is set (state.boolean_modeling_phase_complete)
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(results_file_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'maboss_simulation_results') and state.maboss_simulation_results == results_file_path):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # MaBoSS simulation results exist
    if not (hasattr(state, 'maboss_simulation_completed') and state.maboss_simulation_completed):
        return False
    if not (hasattr(state, 'state_probability_trajectories') and state.state_probability_trajectories):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Network behavior assessed
    state.network_behavior_assessed = True

    # [DATA] Biological plausibility validated
    state.biological_plausibility_validated = True

    # [DATA] Key cell fate decision nodes
    state.key_cell_fate_nodes = ["TNF", "NFkB", "p53", "MDM2", "CASP3", "CASP8", "MYC", "CCND1"]

    # [ENABLER] Model validation passed - gates a_create_physicell_project
    state.model_validation_status = "passed"

    # [DATA] Phase completion marker
    state.boolean_modeling_phase_complete = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "network_behavior_analyzed"
    # END: Effects

    return state

# ============================================================================
# MULTISCALE CANCER MODELING WORKFLOW ACTIONS - PART 3: MULTICELLULAR INTEGRATION
# Generated Actions for Steps 8-12 of the Comprehensive Multiscale TNF Cancer Modeling Workflow
# ============================================================================

# ============================================================================
# ACTIONS FOR MULTICELLULAR INTEGRATION PHASE (Steps 8-12)
# ============================================================================

def a_create_physicell_project(state: State, project_name: str, template: str = "cancer_biorobots") -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: physicell:create_project

    Action signature:
        a_create_physicell_project(state, project_name, template)

    Action parameters:
        project_name: name of the PhysiCell project
        template: project template type (default: "cancer_biorobots")

    Action purpose:
        Create base PhysiCell simulation framework

    Preconditions:
        - Boolean modeling phase is complete (state.boolean_modeling_phase_complete)
        - Model validation has passed (state.model_validation_status == "passed")

    Effects:
        - PhysiCell project name is set (state.physicell_project_name)
        - PhysiCell project directory is created (state.physicell_project_directory)
        - PhysiCell template is set (state.physicell_template)
        - PhysiCell project created flag is set (state.physicell_project_created) [ENABLER]
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(project_name, str): return False
    if not isinstance(template, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (project_name.strip() and project_name == "TNF_Cancer_Multiscale_Model"):
        return False
    if template not in ["cancer_biorobots", "biorobots", "template"]:
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Boolean modeling phase is complete and validated
    if not (hasattr(state, 'boolean_modeling_phase_complete') and state.boolean_modeling_phase_complete):
        return False
    if not (hasattr(state, 'model_validation_status') and state.model_validation_status == "passed"):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] PhysiCell project name
    state.physicell_project_name = project_name

    # [DATA] PhysiCell project directory
    state.physicell_project_directory = f"./{project_name}"

    # [DATA] PhysiCell template
    state.physicell_template = template

    # [ENABLER] PhysiCell project created - gates a_configure_microenvironment
    state.physicell_project_created = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "physicell_project_created"
    # END: Effects

    return state


def a_configure_microenvironment(state: State, project_path: str, substrates: List[Dict[str, Union[str, float]]]) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: physicell:configure_microenvironment

    Action signature:
        a_configure_microenvironment(state, project_path, substrates)

    Action parameters:
        project_path: path to PhysiCell project directory
        substrates: list of substrate definitions with properties

    Action purpose:
        Set up TNF diffusion in the microenvironment

    Preconditions:
        - PhysiCell project exists and matches expected path (state.physicell_project_directory)
        - PhysiCell project has been created (state.physicell_project_created)
        - Substrates list contains TNF with required properties

    Effects:
        - Microenvironment substrates are configured (state.microenvironment_substrates)
        - TNF diffusion coefficient is set (state.tnf_diffusion_coefficient)
        - TNF decay rate is set (state.tnf_decay_rate)
        - Microenvironment configured flag is set (state.microenvironment_configured) [ENABLER]
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(project_path, str): return False
    if not isinstance(substrates, list): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'physicell_project_directory') and state.physicell_project_directory == project_path):
        return False
    tnf_substrate = next((s for s in substrates if s.get("name") == "TNF"), None)
    if not (tnf_substrate and "diffusion_coefficient" in tnf_substrate and "decay_rate" in tnf_substrate):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # PhysiCell project exists
    if not (hasattr(state, 'physicell_project_created') and state.physicell_project_created):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Microenvironment substrates
    state.microenvironment_substrates = substrates

    # [DATA] TNF diffusion coefficient
    state.tnf_diffusion_coefficient = tnf_substrate["diffusion_coefficient"]

    # [DATA] TNF decay rate
    state.tnf_decay_rate = tnf_substrate["decay_rate"]

    # [ENABLER] Microenvironment configured - gates a_add_cancer_cell_type
    state.microenvironment_configured = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "microenvironment_configured"
    # END: Effects

    return state


def a_add_cancer_cell_type(state: State, project_path: str, cell_type_name: str, cell_properties: Dict[str, float]) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: physicell:add_cell_type

    Action signature:
        a_add_cancer_cell_type(state, project_path, cell_type_name, cell_properties)

    Action parameters:
        project_path: path to PhysiCell project directory
        cell_type_name: name of the cancer cell type
        cell_properties: dictionary of cell properties

    Action purpose:
        Create cancer cell agent with basic properties

    Preconditions:
        - PhysiCell project exists and matches expected path (state.physicell_project_directory)
        - Microenvironment has been configured (state.microenvironment_configured)
        - Cell type name is "cancer_cell"
        - Cell properties contain required properties (proliferation_rate, apoptosis_rate, migration_speed)

    Effects:
        - Cancer cell type name is set (state.cancer_cell_type_name)
        - Cancer cell properties are stored (state.cancer_cell_properties)
        - Cancer cell proliferation rate is set (state.cancer_cell_proliferation_rate)
        - Cancer cell apoptosis rate is set (state.cancer_cell_apoptosis_rate)
        - Cancer cell migration speed is set (state.cancer_cell_migration_speed)
        - Cancer cell type added flag is set (state.cancer_cell_type_added) [ENABLER]
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(project_path, str): return False
    if not isinstance(cell_type_name, str): return False
    if not isinstance(cell_properties, dict): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'physicell_project_directory') and state.physicell_project_directory == project_path):
        return False
    if cell_type_name != "cancer_cell":
        return False
    required_props = ["proliferation_rate", "apoptosis_rate", "migration_speed"]
    if not all(prop in cell_properties for prop in required_props):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Microenvironment is configured
    if not (hasattr(state, 'microenvironment_configured') and state.microenvironment_configured):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Cancer cell type name
    state.cancer_cell_type_name = cell_type_name

    # [DATA] Cancer cell properties
    state.cancer_cell_properties = cell_properties

    # [DATA] Cancer cell proliferation rate
    state.cancer_cell_proliferation_rate = cell_properties["proliferation_rate"]

    # [DATA] Cancer cell apoptosis rate
    state.cancer_cell_apoptosis_rate = cell_properties["apoptosis_rate"]

    # [DATA] Cancer cell migration speed
    state.cancer_cell_migration_speed = cell_properties["migration_speed"]

    # [ENABLER] Cancer cell type added - gates a_integrate_maboss_model
    state.cancer_cell_type_added = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "cancer_cell_type_added"
    # END: Effects

    return state


def a_integrate_maboss_model(state: State, project_path: str, cell_type_name: str, maboss_files: Dict[str, str]) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: physicell:integrate_boolean_model

    Action signature:
        a_integrate_maboss_model(state, project_path, cell_type_name, maboss_files)

    Action parameters:
        project_path: path to PhysiCell project directory
        cell_type_name: name of the target cell type
        maboss_files: dictionary containing paths to .bnd and .cfg files

    Action purpose:
        Link MaBoSS Boolean model to cancer cell behavior

    Preconditions:
        - PhysiCell project exists and matches expected path (state.physicell_project_directory)
        - Cancer cell type exists and matches expected name (state.cancer_cell_type_name)
        - Cancer cell type has been added (state.cancer_cell_type_added)
        - Model validation has passed (state.model_validation_status == "passed")
        - MaBoSS files dictionary contains required file paths (bnd_file, cfg_file)
        - MaBoSS files match previously created files

    Effects:
        - MaBoSS integration files are stored (state.maboss_integration_files)
        - Boolean network integrated flag is set (state.boolean_network_integrated) [ENABLER]
        - TNF sensing enabled flag is set (state.tnf_sensing_enabled) [ENABLER]
        - Cell fate decision control flag is set (state.cell_fate_decision_control)
        - Workflow step is updated (state.current_workflow_step)

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(project_path, str): return False
    if not isinstance(cell_type_name, str): return False
    if not isinstance(maboss_files, dict): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'physicell_project_directory') and state.physicell_project_directory == project_path):
        return False
    if not (hasattr(state, 'cancer_cell_type_name') and state.cancer_cell_type_name == cell_type_name):
        return False
    if not ("bnd_file" in maboss_files and "cfg_file" in maboss_files):
        return False
    if not (hasattr(state, 'maboss_bnd_file') and state.maboss_bnd_file == maboss_files["bnd_file"]):
        return False
    if not (hasattr(state, 'maboss_cfg_file') and state.maboss_cfg_file == maboss_files["cfg_file"]):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Cancer cell type exists and model is validated
    if not (hasattr(state, 'cancer_cell_type_added') and state.cancer_cell_type_added):
        return False
    if not (hasattr(state, 'model_validation_status') and state.model_validation_status == "passed"):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] MaBoSS integration files
    state.maboss_integration_files = maboss_files

    # [ENABLER] Boolean network integrated - gates a_execute_multiscale_simulation
    state.boolean_network_integrated = True

    # [ENABLER] TNF sensing enabled - gates a_execute_multiscale_simulation
    state.tnf_sensing_enabled = True

    # [DATA] Cell fate decision control
    state.cell_fate_decision_control = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "maboss_model_integrated"
    # END: Effects

    return state


def a_execute_multiscale_simulation(state: State, project_path: str, run_parameters: Dict[str, Union[int, float]]) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: physicell:run_simulation

    Action signature:
        a_execute_multiscale_simulation(state, project_path, run_parameters)

    Action parameters:
        project_path: path to PhysiCell project directory
        run_parameters: dictionary containing simulation parameters

    Action purpose:
        Execute complete multiscale simulation

    Preconditions:
        - PhysiCell project exists and matches expected path (state.physicell_project_directory)
        - Boolean network has been integrated (state.boolean_network_integrated)
        - TNF sensing is enabled (state.tnf_sensing_enabled)
        - Run parameters contain required parameters (max_time, output_interval)
        - Parameters have reasonable values (max_time == 7200, output_interval == 60)

    Effects:
        - Simulation max time is set (state.simulation_max_time)
        - Simulation output interval is set (state.simulation_output_interval)
        - Multiscale simulation executed flag is set (state.multiscale_simulation_executed)
        - Cancer population dynamics captured flag is set (state.cancer_population_dynamics_captured)
        - TNF-induced cell fate changes captured flag is set (state.tnf_induced_cell_fate_changes_captured)
        - Workflow step is updated (state.current_workflow_step)
        - Workflow complete flag is set (state.workflow_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(project_path, str): return False
    if not isinstance(run_parameters, dict): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not (hasattr(state, 'physicell_project_directory') and state.physicell_project_directory == project_path):
        return False
    if not ("max_time" in run_parameters and "output_interval" in run_parameters):
        return False
    if not (run_parameters["max_time"] == 7200 and run_parameters["output_interval"] == 60):
        return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Fully integrated multiscale model exists
    if not (hasattr(state, 'boolean_network_integrated') and state.boolean_network_integrated):
        return False
    if not (hasattr(state, 'tnf_sensing_enabled') and state.tnf_sensing_enabled):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Simulation max time
    state.simulation_max_time = run_parameters["max_time"]

    # [DATA] Simulation output interval
    state.simulation_output_interval = run_parameters["output_interval"]

    # [DATA] Multiscale simulation executed
    state.multiscale_simulation_executed = True

    # [DATA] Cancer population dynamics captured
    state.cancer_population_dynamics_captured = True

    # [DATA] TNF-induced cell fate changes captured
    state.tnf_induced_cell_fate_changes_captured = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "multiscale_simulation_completed"

    # [ENABLER] Workflow complete - final step
    state.workflow_complete = True
    # END: Effects

    return state

# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

# Declare all 12 actions to the current domain
gtpyhop.declare_actions(
    a_create_tnf_cancer_network,
    a_remove_bimodal_interactions,
    a_check_network_connectivity,
    a_export_network_to_bnet,
    a_create_maboss_files,
    a_run_maboss_simulation,
    a_analyze_maboss_results,
    a_create_physicell_project,
    a_configure_microenvironment,
    a_add_cancer_cell_type,
    a_integrate_maboss_model,
    a_execute_multiscale_simulation
)
# ============================================================================
# HIGH-LEVEL WORKFLOW METHODS
# ============================================================================

def m_multiscale_tnf_cancer_modeling(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_multiscale_tnf_cancer_modeling(state)

    Method parameters:
        None

    Method auxiliary parameters:
        None (inferred from None)

    Method purpose:
        Complete multiscale TNF cancer modeling workflow

    Preconditions:
        - TNF-related gene list is defined (state.tnf_gene_list)
        - Omnipath database access is available (state.omnipath_available)

    Task decomposition:
        - m_phase1_boolean_network_development: Boolean network construction and validation
        - m_phase2_multicellular_integration: PhysiCell integration and multiscale simulation

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Preconditions
    # Initial state requirements
    if not (hasattr(state, 'tnf_gene_list') and state.tnf_gene_list and
            hasattr(state, 'omnipath_available') and state.omnipath_available):
        return False
    # END: Preconditions

    return [
        ("m_phase1_boolean_network_development",),
        ("m_phase2_multicellular_integration",)
    ]


def m_phase1_boolean_network_development(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_phase1_boolean_network_development(state)

    Method parameters:
        None

    Method auxiliary parameters:
        None (inferred from None)

    Method purpose:
        Phase 1: Boolean Network Development

    Preconditions:
        - TNF-related gene list is defined (state.tnf_gene_list)
        - Omnipath database access is available (state.omnipath_available)

    Task decomposition:
        - m_network_construction: Create initial TNF-responsive cancer cell fate network
        - m_network_preprocessing: Prepare network for Boolean modeling
        - m_maboss_model_preparation: Configure Boolean network simulation
        - m_boolean_model_validation: Verify biological plausibility

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Preconditions
    if not (hasattr(state, 'tnf_gene_list') and state.tnf_gene_list and
            hasattr(state, 'omnipath_available') and state.omnipath_available):
        return False
    # END: Preconditions

    return [
        ("m_network_construction",),
        ("m_network_preprocessing",),
        ("m_maboss_model_preparation",),
        ("m_boolean_model_validation",)
    ]


def m_phase2_multicellular_integration(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_phase2_multicellular_integration(state)

    Method parameters:
        None

    Method auxiliary parameters:
        None (inferred from None)

    Method purpose:
        Phase 2: Multicellular Integration

    Preconditions:
        - Phase 1 must be complete (state.boolean_modeling_phase_complete)
        - Model validation must have passed (state.model_validation_status)

    Task decomposition:
        - m_physicell_project_setup: Initialize multicellular simulation environment
        - m_microenvironment_configuration: Set up TNF diffusion
        - m_cell_type_configuration: Define cancer cell properties and behaviors
        - m_maboss_physicell_integration: Couple Boolean network to cellular behaviors
        - m_multiscale_simulation_execution: Run integrated multiscale simulation

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Preconditions
    # Phase 1 must be complete
    if not (hasattr(state, 'boolean_modeling_phase_complete') and state.boolean_modeling_phase_complete and
            hasattr(state, 'model_validation_status') and state.model_validation_status == "passed"):
        return False
    # END: Preconditions

    return [
        ("m_physicell_project_setup",),
        ("m_microenvironment_configuration",),
        ("m_cell_type_configuration",),
        ("m_maboss_physicell_integration",),
        ("m_multiscale_simulation_execution",)
    ]


# ============================================================================
# PHASE 1 METHODS - BOOLEAN NETWORK DEVELOPMENT
# ============================================================================

def m_network_construction(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_network_construction(state)

    Method parameters:
        None

    Method auxiliary parameters:
        gene_list: List[str] (inferred from state)
        organism: str (inferred from state, default: "human")

    Method purpose:
        1.1 Network Construction - Create initial TNF-responsive cancer cell fate network

    Preconditions:
        - TNF-related gene list is defined (state.tnf_gene_list)
        - Omnipath database access is available (state.omnipath_available)

    Task decomposition:
        - a_create_tnf_cancer_network: Generate initial network from TNF-related genes

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    gene_list = state.tnf_gene_list if hasattr(state, 'tnf_gene_list') else None
    organism = "human"

    if gene_list is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'tnf_gene_list') and state.tnf_gene_list and
            hasattr(state, 'omnipath_available') and state.omnipath_available):
        return False
    # END: Preconditions

    return [
        ("a_create_tnf_cancer_network", gene_list, organism)
    ]


def m_network_preprocessing(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_network_preprocessing(state)

    Method parameters:
        None

    Method auxiliary parameters:
        network_file_path: str (inferred from state)

    Method purpose:
        1.2 Network Preprocessing - Prepare network for Boolean modeling

    Preconditions:
        - Network creation must be complete (state.network_creation_status)

    Task decomposition:
        - a_remove_bimodal_interactions: Remove bidirectional interactions from network
        - m_check_network_connectivity_and_export: Validate connectivity and export to BNET format

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    network_file_path = state.raw_network_file if hasattr(state, 'raw_network_file') else None

    if network_file_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Network creation must be complete
    if not (hasattr(state, 'network_creation_status') and state.network_creation_status == "completed"):
        return False
    # END: Preconditions

    return [
        ("a_remove_bimodal_interactions", network_file_path),
        ("m_check_network_connectivity_and_export",)
    ]


def m_check_network_connectivity_and_export(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_check_network_connectivity_and_export(state)

    Method parameters:
        None

    Method auxiliary parameters:
        network_file_path: str (inferred from state)

    Method purpose:
        1.2.2-1.2.4 Check connectivity and export if connected

    Preconditions:
        - Bimodal interactions must be removed (state.bimodal_interactions_removed)

    Task decomposition:
        - a_check_network_connectivity: Verify network connectivity
        - a_export_network_to_bnet: Export network to BNET format

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    network_file_path = state.cleaned_network_file if hasattr(state, 'cleaned_network_file') else None

    if network_file_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Bimodal interactions must be removed
    if not (hasattr(state, 'bimodal_interactions_removed') and state.bimodal_interactions_removed):
        return False
    # END: Preconditions

    return [
        ("a_check_network_connectivity", network_file_path),
        ("a_export_network_to_bnet", network_file_path)
    ]


def m_maboss_model_preparation(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_maboss_model_preparation(state)

    Method parameters:
        None

    Method auxiliary parameters:
        bnet_file_path: str (inferred from state)
        thread_count: int (default: 10)

    Method purpose:
        1.3 MaBoSS Model Preparation - Configure Boolean network simulation

    Preconditions:
        - BNET export must be complete (state.bnet_format_ready)
        - Boolean modeling must be ready (state.boolean_modeling_ready)

    Task decomposition:
        - a_create_maboss_files: Create MaBoSS configuration files

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    bnet_file_path = getattr(state, 'bnet_file_path', None)
    thread_count = 10

    if bnet_file_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # BNET export must be complete
    if not (hasattr(state, 'bnet_format_ready') and state.bnet_format_ready and
            hasattr(state, 'boolean_modeling_ready') and state.boolean_modeling_ready):
        return False
    # END: Preconditions

    return [
        ("a_create_maboss_files", bnet_file_path, thread_count)
    ]


def m_boolean_model_validation(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_boolean_model_validation(state)

    Method parameters:
        None

    Method auxiliary parameters:
        bnd_file_path: str (inferred from state)
        cfg_file_path: str (inferred from state)

    Method purpose:
        1.4 Boolean Model Validation - Verify biological plausibility

    Preconditions:
        - MaBoSS files must be created (state.maboss_files_created)

    Task decomposition:
        - a_run_maboss_simulation: Execute MaBoSS simulation
        - m_analyze_maboss_results_task: Analyze simulation results

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    bnd_file_path = getattr(state, 'maboss_bnd_file', None)
    cfg_file_path = getattr(state, 'maboss_cfg_file', None)

    if bnd_file_path is None or cfg_file_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # MaBoSS files must be created
    if not (hasattr(state, 'maboss_files_created') and state.maboss_files_created):
        return False
    # END: Preconditions

    return [
        ("a_run_maboss_simulation", bnd_file_path, cfg_file_path),
        ("m_analyze_maboss_results_task",)
    ]


def m_analyze_maboss_results_task(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_analyze_maboss_results_task(state)

    Method parameters:
        None

    Method auxiliary parameters:
        results_file_path: str (inferred from state)

    Method purpose:
        1.4.3 Analyze MaBoSS results for biological plausibility

    Preconditions:
        - MaBoSS simulation must be complete (state.maboss_simulation_completed)

    Task decomposition:
        - a_analyze_maboss_results: Analyze simulation results for biological plausibility

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    results_file_path = getattr(state, 'maboss_simulation_results', None)

    if results_file_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # MaBoSS simulation must be complete
    if not (hasattr(state, 'maboss_simulation_completed') and state.maboss_simulation_completed):
        return False
    # END: Preconditions

    return [
        ("a_analyze_maboss_results", results_file_path)
    ]


# ============================================================================
# PHASE 2 METHODS - MULTICELLULAR INTEGRATION
# ============================================================================

def m_physicell_project_setup(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_physicell_project_setup(state)

    Method parameters:
        None

    Method auxiliary parameters:
        project_name: str (default: "TNF_Cancer_Multiscale_Model")
        template: str (default: "cancer_biorobots")

    Method purpose:
        2.1 PhysiCell Project Setup - Initialize multicellular simulation environment

    Preconditions:
        - Phase 1 must be complete (state.boolean_modeling_phase_complete)
        - Model validation must have passed (state.model_validation_status)

    Task decomposition:
        - a_create_physicell_project: Create PhysiCell project from template

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    project_name = "TNF_Cancer_Multiscale_Model"
    template = "cancer_biorobots"
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Phase 1 must be complete
    if not (hasattr(state, 'boolean_modeling_phase_complete') and state.boolean_modeling_phase_complete and
            hasattr(state, 'model_validation_status') and state.model_validation_status == "passed"):
        return False
    # END: Preconditions

    return [
        ("a_create_physicell_project", project_name, template)
    ]


def m_microenvironment_configuration(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_microenvironment_configuration(state)

    Method parameters:
        None

    Method auxiliary parameters:
        project_path: str (inferred from state)
        substrates: List[Dict] (inferred from state)

    Method purpose:
        2.2 Microenvironment Configuration - Set up TNF diffusion

    Preconditions:
        - PhysiCell project must exist (state.physicell_project_created)

    Task decomposition:
        - a_configure_microenvironment: Configure TNF substrate diffusion

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    project_path = state.physicell_project_directory if hasattr(state, 'physicell_project_directory') else None
    # Default TNF substrate configuration
    substrates = state.tnf_substrates if hasattr(state, 'tnf_substrates') else [
        {"name": "TNF", "diffusion_coefficient": 1000.0, "decay_rate": 0.1}
    ]

    if project_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # PhysiCell project must exist
    if not (hasattr(state, 'physicell_project_created') and state.physicell_project_created):
        return False
    # END: Preconditions

    return [
        ("a_configure_microenvironment", project_path, substrates)
    ]


def m_cell_type_configuration(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_cell_type_configuration(state)

    Method parameters:
        None

    Method auxiliary parameters:
        project_path: str (inferred from state)
        cell_type_name: str (default: "cancer_cell")
        cell_properties: Dict[str, float] (inferred from state)

    Method purpose:
        2.3 Cell Type Configuration - Define cancer cell properties and behaviors

    Preconditions:
        - Microenvironment must be configured (state.microenvironment_configured)

    Task decomposition:
        - a_add_cancer_cell_type: Add cancer cell type with properties

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    project_path = state.physicell_project_directory if hasattr(state, 'physicell_project_directory') else None
    cell_type_name = "cancer_cell"
    # Default cancer cell properties
    cell_properties = state.cancer_cell_properties if hasattr(state, 'cancer_cell_properties') else {
        "proliferation_rate": 0.0005,
        "apoptosis_rate": 0.0001,
        "migration_speed": 0.5
    }

    if project_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Microenvironment must be configured
    if not (hasattr(state, 'microenvironment_configured') and state.microenvironment_configured):
        return False
    # END: Preconditions

    return [
        ("a_add_cancer_cell_type", project_path, cell_type_name, cell_properties)
    ]


def m_maboss_physicell_integration(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_maboss_physicell_integration(state)

    Method parameters:
        None

    Method auxiliary parameters:
        project_path: str (inferred from state)
        cell_type_name: str (inferred from state)
        maboss_files: Dict[str, str] (inferred from state)

    Method purpose:
        2.4 MaBoSS-PhysiCell Integration - Couple Boolean network to cellular behaviors

    Preconditions:
        - Cancer cell type must be added (state.cancer_cell_type_added)
        - Model validation must have passed (state.model_validation_status)

    Task decomposition:
        - a_integrate_maboss_model: Integrate MaBoSS Boolean model with PhysiCell

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    project_path = state.physicell_project_directory if hasattr(state, 'physicell_project_directory') else None
    cell_type_name = getattr(state, 'cancer_cell_type_name', "cancer_cell")  # Default to "cancer_cell"
    maboss_files = {
        'bnd_file': getattr(state, 'maboss_bnd_file', None),
        'cfg_file': getattr(state, 'maboss_cfg_file', None)
    } if hasattr(state, 'maboss_bnd_file') and hasattr(state, 'maboss_cfg_file') else None

    if project_path is None or maboss_files is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Cancer cell type must be added
    if not (hasattr(state, 'cancer_cell_type_added') and state.cancer_cell_type_added and
            hasattr(state, 'model_validation_status') and state.model_validation_status == "passed"):
        return False
    # END: Preconditions

    return [
        ("a_integrate_maboss_model", project_path, cell_type_name, maboss_files)
    ]


def m_multiscale_simulation_execution(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_multiscale_simulation_execution(state)

    Method parameters:
        None

    Method auxiliary parameters:
        project_path: str (inferred from state)
        run_parameters: Dict[str, Union[int, float]] (inferred from state)

    Method purpose:
        2.5 Multiscale Simulation Execution - Run integrated multiscale simulation

    Preconditions:
        - MaBoSS integration must be complete (state.boolean_network_integrated)
        - TNF sensing must be enabled (state.tnf_sensing_enabled)

    Task decomposition:
        - a_execute_multiscale_simulation: Execute PhysiCell multiscale simulation

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    # END: Type Checking

    # BEGIN: Auxiliary Parameter Inference
    project_path = state.physicell_project_directory if hasattr(state, 'physicell_project_directory') else None
    # Default simulation parameters (must match action's expected values)
    run_parameters = state.simulation_parameters if hasattr(state, 'simulation_parameters') else {
        "max_time": 7200,  # 120 hours in minutes (5 days)
        "output_interval": 60
    }

    if project_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # MaBoSS integration must be complete
    if not (hasattr(state, 'boolean_network_integrated') and state.boolean_network_integrated and
            hasattr(state, 'tnf_sensing_enabled') and state.tnf_sensing_enabled):
        return False
    # END: Preconditions

    return [
        ("a_execute_multiscale_simulation", project_path, run_parameters)
    ]


# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# NOTE: Domain must be created BEFORE importing this module
# See examples.py for the correct pattern

# Declare task methods to the current domain
# NOTE: Task names include the m_ prefix to match the new format specification
gtpyhop.declare_task_methods('m_multiscale_tnf_cancer_modeling', m_multiscale_tnf_cancer_modeling)
gtpyhop.declare_task_methods('m_phase1_boolean_network_development', m_phase1_boolean_network_development)
gtpyhop.declare_task_methods('m_phase2_multicellular_integration', m_phase2_multicellular_integration)

# Phase 1 methods
gtpyhop.declare_task_methods('m_check_network_connectivity_and_export', m_check_network_connectivity_and_export)
gtpyhop.declare_task_methods('m_network_construction', m_network_construction)
gtpyhop.declare_task_methods('m_network_preprocessing', m_network_preprocessing)
gtpyhop.declare_task_methods('m_maboss_model_preparation', m_maboss_model_preparation)
gtpyhop.declare_task_methods('m_boolean_model_validation', m_boolean_model_validation)
gtpyhop.declare_task_methods('m_analyze_maboss_results_task', m_analyze_maboss_results_task)

# Phase 2 methods
gtpyhop.declare_task_methods('m_physicell_project_setup', m_physicell_project_setup)
gtpyhop.declare_task_methods('m_microenvironment_configuration', m_microenvironment_configuration)
gtpyhop.declare_task_methods('m_cell_type_configuration', m_cell_type_configuration)
gtpyhop.declare_task_methods('m_maboss_physicell_integration', m_maboss_physicell_integration)
gtpyhop.declare_task_methods('m_multiscale_simulation_execution', m_multiscale_simulation_execution)

# ============================================================================

# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

# Declare all 12 actions to the current domain
declare_actions(
    a_create_tnf_cancer_network,
    a_remove_bimodal_interactions,
    a_check_network_connectivity,
    a_export_network_to_bnet,
    a_create_maboss_files,
    a_run_maboss_simulation,
    a_analyze_maboss_results,
    a_create_physicell_project,
    a_configure_microenvironment,
    a_add_cancer_cell_type,
    a_integrate_maboss_model,
    a_execute_multiscale_simulation
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Declare task methods to the current domain
# NOTE: Task names include the m_ prefix to match the new format specification
declare_task_methods('m_multiscale_tnf_cancer_modeling', m_multiscale_tnf_cancer_modeling)
declare_task_methods('m_phase1_boolean_network_development', m_phase1_boolean_network_development)
declare_task_methods('m_phase2_multicellular_integration', m_phase2_multicellular_integration)

# Phase 1 methods
declare_task_methods('m_check_network_connectivity_and_export', m_check_network_connectivity_and_export)
declare_task_methods('m_network_construction', m_network_construction)
declare_task_methods('m_network_preprocessing', m_network_preprocessing)
declare_task_methods('m_maboss_model_preparation', m_maboss_model_preparation)
declare_task_methods('m_boolean_model_validation', m_boolean_model_validation)
declare_task_methods('m_analyze_maboss_results_task', m_analyze_maboss_results_task)

# Phase 2 methods
declare_task_methods('m_physicell_project_setup', m_physicell_project_setup)
declare_task_methods('m_microenvironment_configuration', m_microenvironment_configuration)
declare_task_methods('m_cell_type_configuration', m_cell_type_configuration)
declare_task_methods('m_maboss_physicell_integration', m_maboss_physicell_integration)
declare_task_methods('m_multiscale_simulation_execution', m_multiscale_simulation_execution)

# ============================================================================
# END OF FILE
# ============================================================================
