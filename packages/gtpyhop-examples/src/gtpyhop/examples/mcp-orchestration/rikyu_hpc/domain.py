# ============================================================================
# MCP Orchestration - Rikyu HPC / vast.ai Containerized Training Domain
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - State Property Map
#   - Helper Functions (3)
#   - Actions (38)
#   - Methods (42, over 35 task names)
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple, Dict

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    # Graceful degradation: supports direct domain.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("rikyu_hpc")
set_current_domain(the_domain)

# ============================================================================
# CONSTANTS
# ============================================================================

# Slurm job states that no longer change (rikyu-hpc get_job_status normalisation)
TERMINAL_JOB_STATES = ("COMPLETED", "FAILED", "CANCELED")

# vast.ai instance state that accepts ssh/exec/copy traffic
VAST_READY_STATE = "Running"

# Apptainer build-source transports that reach a working handler on Rikyu.
# 'docker://' is verified end-to-end; the archive transports reach their
# handlers and share the same conversion machinery.
USABLE_TRANSPORTS = ("docker", "docker-archive", "oci-archive", "oci")

# Transports that are recognised but cannot be used on Rikyu, and why
UNUSABLE_TRANSPORTS = {
    "docker-daemon": "no Docker daemon on Rikyu (unix:///var/run/docker.sock absent)",
    "library": "recognised, but no remote endpoints are configured",
}

# Apptainer unpacks layers before packing squashfs, so a conversion needs
# roughly twice the image size free on the cache tier
CONVERSION_HEADROOM_FACTOR = 2.0

# ============================================================================
# STATE PROPERTY MAP (Rikyu HPC + vast.ai containerized training)
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER]         Property acts as a workflow gate for subsequent steps
#  - [DATA]            Informational/data container
#  - [EXPECTED_EFFECT] Sensor-driven state change applied during planning
#
# Server 1: mcp-python-ingestion (HTN planning with GTPyhop)
# Server 2: rikyu-hpc            (server/rikyu_mcp/hpc_server.py)
# Server 3: rikyu-docs           (server/rikyu_mcp/docs_server.py)
# Server 4: vastai               (vastai CLI / Python SDK / REST API)
#
# --- Ground truth (set by the scenario, never invented by an action) --------
#  facility: Dict          [DATA] what get_facility would return
#  partitions: Dict        [DATA] per-partition node counts
#  doc_catalog: Dict       [DATA] doc_id -> {'section', 'query', 'facts'}
#  storage_tiers: Dict     [DATA] mount prefix -> {'quota_gb', 'used_gb'}
#  job_script: Dict        [DATA] job name -> scripted Slurm state sequence
#  job_outputs: Dict       [DATA] job name -> {remote path: size_gb}
#  job_artifact: Dict      [DATA] job name -> artifact key (or absent)
#  job_launcher: Dict      [DATA] job name -> 'mpirun' | 'srun' (absent = serial)
#  artifact_arch: Dict     [DATA] artifact key -> 'aarch64' | 'x86_64'
#  command_weight: Dict    [DATA] login-node command -> 'light' | 'heavy'
#  login_binaries: Dict    [DATA] what 'command -v' finds on the login node
#  site_images: Dict       [DATA] SIF path -> {'arch', 'size_gb'} under /shared
#  oci_images: Dict        [DATA] registry reference -> {'arch', 'size_gb'}
#  container_needs: Dict   [DATA] job name -> paths that must be visible inside
#  auto_bind_paths: List   [DATA] host paths bound into every container by default
#  workload: Dict          [DATA] container_required, target_arch, sif_path, ...
#  vast_offers: Dict       [DATA] offer_id -> {'gpu_name','num_gpus','arch',...}
#  instance_script: Dict   [DATA] label -> scripted vast.ai state sequence
#  training_script: Dict   [DATA] label -> scripted training log sequence
#
# --- Step 1: a_initialize_servers -------------------------------------------
#  (E) server_1_ready .. server_4_ready: True [ENABLER]
#  (E) rikyu_session_initialized: True [ENABLER]
#
# --- Step 2: a_get_facility -------------------------------------------------
#  (P) server_2_ready [ENABLER]
#  (E) supported_gpu_counts: List[int] [DATA]
#  (E) gpus_per_node, max_wall_time_hours: int [DATA]
#  (E) cluster_arch: str [DATA]
#  (E) max_wall_time: str, max_wall_time_hours: float [DATA]
#  (E) facility_known: True [ENABLER]
#  Note: the facility metadata says nothing about containers. That silence is
#  why a_probe_container_runtime exists.
#
# --- Step 3: a_get_resources / a_get_resource -------------------------------
#  (E) partition_idle: Dict[str,int] [DATA]
#  (E) resources_known: True [ENABLER]
#
# --- Step 4: a_list_doc_sections / a_search_docs / a_read_doc_section -------
#  (E) doc_sections: List[str] [DATA]
#  (E) doc_hits: List[str] [DATA]
#  (E) doc_facts: Dict[str,str] [DATA]
#  (E) docs_grounded: True [ENABLER]
#
# --- Step 5: a_submit_job ---------------------------------------------------
#  (P) facility_known [ENABLER]
#  (P) gpus in supported_gpu_counts, duration <= max_wall_time_hours
#  (P) artifact_arch[job_artifact[name]] == cluster_arch
#  (E) jobs[job_id]: Dict [DATA]
#  (E) job_trajectory[job_id]: List[str] [DATA]
#  (E) last_job_id: str [DATA]
#
# --- Step 6: a_poll_job_status ----------------------------------------------
#  (P) jobs[job_id]['state'] not terminal [ENABLER]
#  (E) jobs[job_id]['state'] [EXPECTED_EFFECT]  # Slurm, not the tool call
#  (E) remote_files[...] on COMPLETED [EXPECTED_EFFECT]  # the job wrote them
#  (E) poll_count[job_id]: int [DATA]
#
# --- Step 7: a_fs_* ---------------------------------------------------------
#  (P) storage tier quota not exceeded (upload)
#  (P) owning job terminal (download), owning job started (tail)
#  (E) remote_dirs, remote_files, local_files, listings, checksums [DATA]
#
# --- Step 8: a_build_image / a_verify_image_arch / a_push_image -------------
#  (E) images[image_ref]: Dict [DATA]
#  (E) image_arch_verified[image_ref]: True [ENABLER]
#  (E) pushed_images: List[str] [ENABLER]
#
# --- Step 9: a_vast_create_instance -----------------------------------------
#  (P) image pushed and arch matches the offer [ENABLER]
#  (P) disk_gb >= workload required disk (static, cannot be resized)
#  (E) instances[instance_id]: Dict [DATA]
#  (E) last_instance_id: str [DATA]
#
# --- Step 10: a_vast_poll_instance / a_vast_logs ----------------------------
#  (E) instances[id]['state'] [EXPECTED_EFFECT]  # vast.ai control plane
#  (E) training_state[id] [EXPECTED_EFFECT]      # the container, not the tool
#  (E) instance_files[id][path] on 'done' [EXPECTED_EFFECT]
#
# --- Step 11: a_vast_copy_out / a_vast_destroy_instance ---------------------
#  (E) results_copied_out[id]: True [ENABLER]
#  (P) results_copied_out[id] is True  <-- the safety invariant
#
# --- Step 12: a_probe_container_runtime -------------------------------------
#  (P) server_2_ready [ENABLER]
#  (E) container_runtime: Dict | None [DATA]   # None is a valid answer
#  (E) container_runtime_known: True [ENABLER]
#
# --- Step 13: a_list_staged_images ------------------------------------------
#  (E) staged_images: Dict [DATA]
#  (E) staged_images_known: True [ENABLER]
#
# --- Step 14: a_set_apptainer_env / a_apptainer_pull ------------------------
#  (E) apptainer_env: Dict [DATA]
#  (E) apptainer_env_set: True [ENABLER]
#  (P) cache tier has ~2x the image size free (state.storage_tiers)
#  (E) sif_images[path]: Dict [DATA]   # carries the SOURCE image's arch
#  (E) remote_files[path]: float [DATA]
#
# --- Step 15: a_verify_sif_arch ---------------------------------------------
#  (P) sif arch == cluster_arch  <-- the only planning-time catch for an
#      x86_64 SIF, which converts cleanly and dies at exec
#  (E) sif_arch_verified[path]: True [ENABLER]
#
# --- Step 16: a_submit_container_job ----------------------------------------
#  (P) container_runtime is not None [ENABLER]
#  (P) sif_arch_verified[sif] [ENABLER]
#  (P) command is non-empty         # exec ignores ENTRYPOINT and CMD
#  (P) every container_needs path is auto-bound or explicitly bound
#  (E) jobs[job_id] with a 'container' record [DATA]
# ============================================================================


# ============================================================================
# HELPER FUNCTIONS (3)
# ----------------------------------------------------------------------------

def h_tier_for_path(state: State, path: str) -> Optional[str]:
    """Return the storage tier prefix owning 'path', or None when untracked."""
    tiers = getattr(state, 'storage_tiers', {})
    best = None
    for prefix in tiers:
        if path.startswith(prefix) and (best is None or len(prefix) > len(best)):
            best = prefix
    return best


def h_job_is_terminal(state: State, job_id: str) -> bool:
    """Return True when 'job_id' is in a Slurm state that no longer changes."""
    jobs = getattr(state, 'jobs', {})
    if job_id not in jobs:
        return False
    return jobs[job_id]['state'] in TERMINAL_JOB_STATES


def h_hours_from_slurm_time(duration: str) -> Optional[float]:
    """
    Convert a Slurm duration to hours, or None when it does not parse.

    Accepts the two forms the Rikyu guide uses: 'HH:MM:SS' (JobSpec
    attributes.duration, e.g. '12:00:00') and 'D-HH:MM:SS' (partition
    max_wall_time, e.g. '4-00:00:00').
    """
    if not isinstance(duration, str) or not duration.strip():
        return None
    days = 0
    body = duration
    if '-' in duration:
        day_part, _, body = duration.partition('-')
        if not day_part.isdigit():
            return None
        days = int(day_part)
    fields = body.split(':')
    if len(fields) != 3 or not all(f.isdigit() for f in fields):
        return None
    hours, minutes, seconds = (int(f) for f in fields)
    return days * 24 + hours + minutes / 60.0 + seconds / 3600.0


# ============================================================================
# ACTIONS (38)
# ----------------------------------------------------------------------------

# ============================================================================
# SERVER INITIALIZATION ACTION (1)
# ============================================================================

def a_initialize_servers(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_initialize_servers(state)

    Action parameters:
        None

    Action purpose:
        Bring up the four MCP endpoints used by the Rikyu HPC domain

    Preconditions:
        None (initialization action)

    Effects:
        - Server 1 (mcp-python-ingestion) is ready (state.server_1_ready) [DATA]
        - Server 2 (rikyu-hpc) is ready (state.server_2_ready) [ENABLER]
        - Server 3 (rikyu-docs) is ready (state.server_3_ready) [ENABLER]
        - Server 4 (vastai) is ready (state.server_4_ready) [ENABLER]
        - Session is initialized (state.rikyu_session_initialized) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No state-type checks needed for initialization
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for initialization action
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Server 1 ready. Recorded for symmetry only: server 1 is the HTN
    # planner running this domain, so no action can meaningfully gate on it.
    state.server_1_ready = True

    # [ENABLER] Server 2 ready - rikyu-hpc (Slurm, filesystem, login node)
    state.server_2_ready = True

    # [ENABLER] Server 3 ready - rikyu-docs (documentation search)
    state.server_3_ready = True

    # [ENABLER] Server 4 ready - vastai (offers, instances, copy)
    state.server_4_ready = True

    # [DATA] Session bookkeeping. The per-server flags above are the real
    # gates; this one summarises them for readers and for state dumps.
    state.rikyu_session_initialized = True
    # END: Effects

    return state


# ============================================================================
# FACILITY AND RESOURCE ACTIONS - Server 2: rikyu-hpc (3)
# ============================================================================

def a_get_facility(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:get_facility

    Action signature:
        a_get_facility(state)

    Action parameters:
        None

    Action purpose:
        Fetch static facility metadata (GPU counts, wall time, architecture)

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Facility ground truth is reachable (state.facility)

    Effects:
        - Supported GPU counts are known (state.supported_gpu_counts) [DATA]
        - GPUs per node is known (state.gpus_per_node) [DATA]
        - Wall-time ceiling is known, raw and parsed (state.max_wall_time,
          state.max_wall_time_hours) [DATA]
        - Node architecture is known (state.cluster_arch) [DATA]
        - Facility lookup completed (state.facility_known) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameter values to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Facility metadata must be reachable
    if not (hasattr(state, 'facility') and state.facility):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] GPU counts Rikyu accepts: 1, 2, 3, 4, 8, 12 or 16
    state.supported_gpu_counts = list(state.facility['supported_gpu_counts'])

    # [DATA] GB200 NVL4 nodes carry 4 GPUs each
    state.gpus_per_node = state.facility['gpus_per_node']

    # [DATA] Wall-time ceiling, kept both as the Slurm string the tool returns
    # and as the parsed hours every precondition compares against
    state.max_wall_time = state.facility['max_wall_time']
    state.max_wall_time_hours = h_hours_from_slurm_time(state.facility['max_wall_time'])

    # [DATA] Grace CPUs: the compute nodes are aarch64 only. This is what
    # decides where a containerized workload can run, since an x86_64 image
    # converts to SIF cleanly and only fails at exec.
    state.cluster_arch = state.facility['cluster_arch']

    # [ENABLER] Facility lookup completed - gates a_submit_job and routing
    state.facility_known = True
    # END: Effects

    return state


def a_get_resources(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:get_resources

    Action signature:
        a_get_resources(state)

    Action parameters:
        None

    Action purpose:
        Fetch live partition occupancy for every partition via sinfo

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Partition ground truth is reachable (state.partitions)

    Effects:
        - Known partition names are recorded (state.known_partitions) [DATA]
        - Resource lookup completed (state.resources_known) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameter values to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Partition data must be reachable
    if not (hasattr(state, 'partitions') and state.partitions):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Partition names returned by sinfo
    state.known_partitions = sorted(state.partitions.keys())

    # [ENABLER] Resource lookup completed
    state.resources_known = True
    # END: Effects

    return state


def a_get_resource(state: State, partition: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:get_resource

    Action signature:
        a_get_resource(state, partition)

    Action parameters:
        partition: Name of the Slurm partition to inspect (Rikyu has only 'gpu')

    Action purpose:
        Fetch live occupancy for one named partition

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - The partition list has been fetched (state.resources_known)
        - The name is one get_resources returned (state.known_partitions)
        - Partition exists (state.partitions[partition])

    Effects:
        - Idle node count is recorded (state.partition_idle) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(partition, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not partition.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # get_resource raises ValueError on an unknown partition name, so the plan
    # must have learned the valid names from get_resources rather than guess.
    # The tool itself would accept a guess and raise; requiring the listing is
    # a plan-level discipline, and it is what makes the partition name an
    # opaque datum threaded between two calls.
    if not getattr(state, 'resources_known', False):
        return False
    if partition not in getattr(state, 'known_partitions', []):
        return False
    # The partition must exist in the facility
    if not (hasattr(state, 'partitions') and partition in state.partitions):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Idle nodes available right now in this partition
    if not hasattr(state, 'partition_idle'):
        state.partition_idle = {}
    state.partition_idle[partition] = state.partitions[partition]['idle']
    # END: Effects

    return state


# ============================================================================
# DOCUMENTATION ACTIONS - Server 3: rikyu-docs (3)
# ============================================================================

def a_list_doc_sections(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-docs:list_doc_sections

    Action signature:
        a_list_doc_sections(state)

    Action parameters:
        None

    Action purpose:
        List every section of the bundled Rikyu guide

    Preconditions:
        - Server 3 is ready (state.server_3_ready)
        - Documentation catalog is reachable (state.doc_catalog)

    Effects:
        - Section titles are recorded (state.doc_sections) [DATA]
        - Section listing completed (state.docs_listed) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameter values to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 3 must be ready
    if not (hasattr(state, 'server_3_ready') and state.server_3_ready):
        return False
    # Documentation catalog must be reachable
    if not (hasattr(state, 'doc_catalog') and state.doc_catalog):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Guide section titles
    state.doc_sections = sorted(
        entry['section'] for entry in state.doc_catalog.values()
    )

    # [DATA] Section listing completed. Nothing gates on it: the guide is
    # advisory, and search_docs works whether or not you listed sections first.
    state.docs_listed = True
    # END: Effects

    return state


def a_search_docs(state: State, query: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-docs:search_docs

    Action signature:
        a_search_docs(state, query)

    Action parameters:
        query: Natural-language question to run against the embedded guide index

    Action purpose:
        Retrieve the doc ids whose chunks match a question

    Preconditions:
        - Server 3 is ready (state.server_3_ready)
        - Documentation catalog is reachable (state.doc_catalog)
        - At least one document matches the query (state.doc_catalog)

    Effects:
        - Matching doc ids are recorded (state.doc_hits) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(query, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not query.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 3 must be ready
    if not (hasattr(state, 'server_3_ready') and state.server_3_ready):
        return False
    # Documentation catalog must be reachable
    if not (hasattr(state, 'doc_catalog') and state.doc_catalog):
        return False
    # The search must return at least one chunk
    hits = sorted(
        doc_id for doc_id, entry in state.doc_catalog.items()
        if query in entry['query']
    )
    if not hits:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Doc ids returned by the embedding search, best match first
    state.doc_hits = hits
    # END: Effects

    return state


def a_read_doc_section(state: State, doc_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-docs:read_doc_section

    Action signature:
        a_read_doc_section(state, doc_id)

    Action parameters:
        doc_id: Identifier of the guide section to read in full

    Action purpose:
        Read one guide section and extract the facts the plan depends on

    Preconditions:
        - Server 3 is ready (state.server_3_ready)
        - Doc id exists (state.doc_catalog[doc_id])
        - Doc id came out of a search (state.doc_hits)

    Effects:
        - Extracted facts are recorded (state.doc_facts) [DATA]
        - Documentation grounding completed (state.docs_grounded) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(doc_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not doc_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 3 must be ready
    if not (hasattr(state, 'server_3_ready') and state.server_3_ready):
        return False
    # The section must exist in the guide
    if not (hasattr(state, 'doc_catalog') and doc_id in state.doc_catalog):
        return False
    # The section must have been surfaced by a search first
    if not (hasattr(state, 'doc_hits') and doc_id in state.doc_hits):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Facts lifted out of the section (module names, flags, paths)
    if not hasattr(state, 'doc_facts'):
        state.doc_facts = {}
    state.doc_facts.update(state.doc_catalog[doc_id]['facts'])

    # [DATA] Documentation grounding completed. Deliberately not a gate: the
    # scheduler will happily accept a JobSpec written without reading the
    # guide, so making submission depend on it would encode a rule Rikyu does
    # not have. What the reading is really for is state.doc_facts above.
    state.docs_grounded = True
    # END: Effects

    return state


# ============================================================================
# JOB ACTIONS - Server 2: rikyu-hpc (5)
# ============================================================================

def a_submit_job(state: State, name: str, gpus: int, processes_per_node: int,
                 duration: str, directory: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:submit_job

    Action signature:
        a_submit_job(state, name, gpus, processes_per_node, duration, directory)

    Action parameters:
        name: JobSpec name
        gpus: JobSpec resources.gpus (must be 1, 2, 3, 4, 8, 12 or 16)
        processes_per_node: JobSpec resources.processes_per_node (MPI rank count
            per node; 0 means the field was left unset)
        duration: JobSpec attributes.duration as a Slurm time string, e.g. '12:00:00'
        directory: JobSpec directory, the remote working directory of the job

    Action purpose:
        Submit a JobSpec to the Slurm scheduler and receive a job id

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Facility metadata has been fetched (state.facility_known)
        - GPU count is supported (state.supported_gpu_counts)
        - Wall time parses and is within the ceiling (state.max_wall_time_hours)
        - Working directory exists (state.remote_dirs)
        - An MPI job uses mpirun, never srun (state.job_launcher)
        - An MPI job sets processes_per_node (state.job_launcher)
        - The job's artifact matches the node architecture (state.artifact_arch)

    Effects:
        - Job record with a fresh job id is created (state.jobs) [DATA]
        - Job id counter is advanced (state.next_job_id) [DATA]
        - Scheduler trajectory is attached (state.job_trajectory) [DATA]
        - Poll counter is initialised (state.poll_count) [DATA]
        - Standard output path is registered (state.file_owner_job) [DATA]
        - Job is added to the submitted list (state.submitted_jobs) [DATA]
        - Most recent job id is recorded (state.last_job_id) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(processes_per_node, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    if not directory.strip(): return False
    if gpus <= 0: return False
    if processes_per_node < 0: return False
    duration_hours = h_hours_from_slurm_time(duration)
    if duration_hours is None or duration_hours <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # submit_job validates the GPU count against the facility, so it must be known
    if not (hasattr(state, 'facility_known') and state.facility_known):
        return False
    # _validate_gpu_count: only 1, 2, 3, 4, 8, 12 and 16 are accepted
    if gpus not in state.supported_gpu_counts:
        return False
    # Every job is capped at the facility wall-time ceiling
    if duration_hours > state.max_wall_time_hours:
        return False
    # The working directory must exist on Lustre
    if not (hasattr(state, 'remote_dirs') and directory in state.remote_dirs):
        return False
    # MPI jobs must be launched with mpirun: srun aborts at MPI_Init on Rikyu,
    # and mpirun reports "not enough slots" when processes_per_node is unset
    launcher = getattr(state, 'job_launcher', {}).get(name)
    if launcher is not None:
        if launcher != 'mpirun':
            return False
        if processes_per_node < 1:
            return False
    # An x86_64 artifact cannot execute on the aarch64 compute nodes
    artifact = getattr(state, 'job_artifact', {}).get(name)
    if artifact is not None:
        arch = getattr(state, 'artifact_arch', {}).get(artifact)
        if arch != state.cluster_arch:
            return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Slurm mints an opaque job id
    job_id = str(state.next_job_id)
    state.next_job_id += 1

    # [DATA] Job record, queued until the scheduler picks it up. Standard output
    # and error default to <directory>/slurm-<job_id>.out
    if not hasattr(state, 'jobs'):
        state.jobs = {}
    stdout_path = f"{directory}/slurm-{job_id}.out"
    state.jobs[job_id] = {
        'name': name,
        'gpus': gpus,
        'processes_per_node': processes_per_node,
        'duration': duration,
        'duration_hours': duration_hours,
        'directory': directory,
        'stdout': stdout_path,
        'state': 'QUEUED',
    }

    # [DATA] Scripted scheduler trajectory for this job
    if not hasattr(state, 'job_trajectory'):
        state.job_trajectory = {}
    state.job_trajectory[job_id] = list(
        getattr(state, 'job_script', {}).get(name, ['ACTIVE', 'COMPLETED'])
    )

    # [DATA] Poll counter, so repeated polling is never elided from the plan
    if not hasattr(state, 'poll_count'):
        state.poll_count = {}
    state.poll_count[job_id] = 0

    # [DATA] The stdout file belongs to this job
    if not hasattr(state, 'file_owner_job'):
        state.file_owner_job = {}
    state.file_owner_job[stdout_path] = job_id

    # [DATA] Submitted job list and the handle later methods infer
    if not hasattr(state, 'submitted_jobs'):
        state.submitted_jobs = []
    state.submitted_jobs.append(job_id)
    state.last_job_id = job_id
    # END: Effects

    return state


def a_poll_job_status(state: State, job_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:get_job_status

    Action signature:
        a_poll_job_status(state, job_id)

    Action parameters:
        job_id: Opaque scheduler identifier returned by submit_job

    Action purpose:
        Read one job's normalised state, observing the scheduler's progress

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Job exists (state.jobs[job_id])
        - Job is not already terminal (state.jobs[job_id]['state'])
        - The scheduler still has a transition to make (state.job_trajectory[job_id])

    Effects:
        - Job state advances (state.jobs[job_id]['state']) [EXPECTED_EFFECT]
        - The consumed transition leaves the trajectory (state.job_trajectory) [DATA]
        - Output files appear once the job completes (state.remote_files) [EXPECTED_EFFECT]
        - Completed outputs are attributed to the job (state.file_owner_job) [EXPECTED_EFFECT]
        - Poll counter is incremented (state.poll_count) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(job_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not job_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # get_job_status raises ValueError when the job is unknown
    if not (hasattr(state, 'jobs') and job_id in state.jobs):
        return False
    # A terminal job never changes again: polling it is pointless
    if h_job_is_terminal(state, job_id):
        return False
    # The scheduler must still have a transition left
    if not state.job_trajectory.get(job_id):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [EXPECTED_EFFECT] Slurm - not this tool call - moves the job forward. The
    # poll only observes it, but the planner must carry the transition or the
    # downstream fs_download precondition could never be satisfied.
    new_state = state.job_trajectory[job_id].pop(0)
    state.jobs[job_id]['state'] = new_state

    # [DATA] Poll counter, guaranteeing this action is never idempotent
    state.poll_count[job_id] = state.poll_count.get(job_id, 0) + 1

    # [EXPECTED_EFFECT] The job - not the poll - wrote its output files. Without
    # this, a plan could never download a checkpoint it legitimately produced.
    if new_state == 'COMPLETED':
        job_name = state.jobs[job_id]['name']
        for path, size_gb in getattr(state, 'job_outputs', {}).get(job_name, {}).items():
            state.remote_files[path] = size_gb
            state.file_owner_job[path] = job_id
    # END: Effects

    return state


def a_get_job_statuses(state: State, job_ids: List[str]) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:get_job_statuses

    Action signature:
        a_get_job_statuses(state, job_ids)

    Action parameters:
        job_ids: Job ids to inspect. An empty list asks for the user's recent
            jobs, which is how the monitoring skill sweeps a whole batch.

    Action purpose:
        Sweep several jobs in one call instead of polling them one by one

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Every requested job exists (state.jobs)
        - At least one requested job is still pending (state.jobs)
        - Every pending job still has a transition (state.job_trajectory)

    Effects:
        - Every pending job advances (state.jobs) [EXPECTED_EFFECT]
        - Consumed transitions leave the trajectories (state.job_trajectory) [DATA]
        - Output files appear for jobs that complete (state.remote_files) [EXPECTED_EFFECT]
        - Completed outputs are attributed to their job (state.file_owner_job) [EXPECTED_EFFECT]
        - Per-job poll counters are incremented (state.poll_count) [DATA]
        - Sweep counter is incremented (state.status_sweeps) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(job_ids, list): return False
    if not all(isinstance(j, str) for j in job_ids): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No further value constraints: an empty list is meaningful
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # There must be something to sweep
    if not getattr(state, 'submitted_jobs', []):
        return False
    # An empty list means "my recent jobs"; otherwise every id must exist
    requested = job_ids or list(state.submitted_jobs)
    if any(j not in getattr(state, 'jobs', {}) for j in requested):
        return False
    # Every pending job must still have a transition, otherwise the sweep loop
    # could never converge
    pending = [j for j in requested if not h_job_is_terminal(state, j)]
    if not pending:
        return False
    for job_id in pending:
        if not state.job_trajectory.get(job_id):
            return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Sweep counter, guaranteeing this action is never idempotent
    state.status_sweeps = getattr(state, 'status_sweeps', 0) + 1

    for job_id in pending:
        # [EXPECTED_EFFECT] Slurm advances each pending job
        new_state = state.job_trajectory[job_id].pop(0)
        state.jobs[job_id]['state'] = new_state
        state.poll_count[job_id] = state.poll_count.get(job_id, 0) + 1

        # [EXPECTED_EFFECT] Completed jobs have written their outputs
        if new_state == 'COMPLETED':
            job_name = state.jobs[job_id]['name']
            for path, size_gb in getattr(state, 'job_outputs', {}).get(job_name, {}).items():
                state.remote_files[path] = size_gb
                state.file_owner_job[path] = job_id
    # END: Effects

    return state


def a_cancel_job(state: State, job_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:cancel_job

    Action signature:
        a_cancel_job(state, job_id)

    Action parameters:
        job_id: Opaque scheduler identifier of the job to cancel

    Action purpose:
        Cancel a queued or running job with scancel

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Job exists (state.jobs[job_id])
        - Job is queued or running, never terminal (state.jobs[job_id]['state'])

    Effects:
        - Job state becomes CANCELED (state.jobs[job_id]['state']) [ENABLER]
        - Remaining scheduler trajectory is discarded (state.job_trajectory) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(job_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not job_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The job must exist
    if not (hasattr(state, 'jobs') and job_id in state.jobs):
        return False
    # scancel only affects queued or running jobs
    if h_job_is_terminal(state, job_id):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] The job is now terminal
    state.jobs[job_id]['state'] = 'CANCELED'

    # [DATA] The scheduler will make no further transitions
    state.job_trajectory[job_id] = []
    # END: Effects

    return state


def a_update_job(state: State, job_id: str, attribute: str, value: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:update_job

    Action signature:
        a_update_job(state, job_id, attribute, value)

    Action parameters:
        job_id: Opaque scheduler identifier of the job to modify
        attribute: Key of the updates dict passed to scontrol update; only
            'timeLimit' is modelled here
        value: New value, as a Slurm time string such as '24:00:00'

    Action purpose:
        Raise a running job's wall-time limit with scontrol update

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Job exists and is not terminal (state.jobs[job_id])
        - Attribute is supported (attribute == 'timeLimit')
        - New wall time parses and is within the ceiling (state.max_wall_time_hours)
        - New wall time is an actual increase (state.jobs[job_id]['duration_hours'])

    Effects:
        - Job wall time is updated (state.jobs[job_id]) [DATA]
        - Update is journalled (state.job_updates) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(job_id, str): return False
    if not isinstance(attribute, str): return False
    if not isinstance(value, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not job_id.strip(): return False
    if attribute != 'timeLimit': return False
    new_hours = h_hours_from_slurm_time(value)
    if new_hours is None or new_hours <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The job must exist
    if not (hasattr(state, 'jobs') and job_id in state.jobs):
        return False
    # scontrol update only affects queued or running jobs
    if h_job_is_terminal(state, job_id):
        return False
    # The facility wall-time ceiling still applies to the new value
    if not (hasattr(state, 'max_wall_time_hours') and new_hours <= state.max_wall_time_hours):
        return False
    # Rescuing a job means giving it more time, not less
    if new_hours <= state.jobs[job_id]['duration_hours']:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] New wall-time limit, kept in both the Slurm and the parsed form
    state.jobs[job_id]['duration'] = value
    state.jobs[job_id]['duration_hours'] = new_hours

    # [DATA] Journal of scontrol updates
    if not hasattr(state, 'job_updates'):
        state.job_updates = []
    state.job_updates.append((job_id, attribute, value))
    # END: Effects

    return state


# ============================================================================
# LOGIN NODE ACTION - Server 2: rikyu-hpc (1)
# ============================================================================

def a_run_command_on_cluster(state: State, command: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:run_command_on_cluster

    Action signature:
        a_run_command_on_cluster(state, command)

    Action parameters:
        command: Shell command to run on the login node

    Action purpose:
        Run a light interactive command on the login node

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - The command is not heavy compute (state.command_weight)

    Effects:
        - Command output is recorded (state.command_output) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(command, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not command.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The login node is not for computation: heavy commands belong in a job
    if getattr(state, 'command_weight', {}).get(command, 'light') != 'light':
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Captured stdout of the login-node command
    if not hasattr(state, 'command_output'):
        state.command_output = {}
    state.command_output[command] = f"output of: {command}"
    # END: Effects

    return state


# ============================================================================
# FILESYSTEM ACTIONS - Server 2: rikyu-hpc (8)
# ============================================================================

def a_fs_mkdir(state: State, path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_mkdir

    Action signature:
        a_fs_mkdir(state, path)

    Action parameters:
        path: Remote directory to create, parents included

    Action purpose:
        Create a working directory on the cluster filesystem

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Directory does not already exist (state.remote_dirs)

    Effects:
        - Directory is registered (state.remote_dirs) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Creating an existing directory would leave the state unchanged
    if path in getattr(state, 'remote_dirs', []):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] The directory now exists and can receive uploads
    if not hasattr(state, 'remote_dirs'):
        state.remote_dirs = []
    state.remote_dirs.append(path)
    # END: Effects

    return state


def a_fs_ls(state: State, path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_ls

    Action signature:
        a_fs_ls(state, path)

    Action parameters:
        path: Remote directory to list

    Action purpose:
        Produce a long-form listing of a remote directory

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Directory exists (state.remote_dirs)

    Effects:
        - Listing is recorded (state.listings) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The directory must exist
    if path not in getattr(state, 'remote_dirs', []):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Files found under that directory
    if not hasattr(state, 'listings'):
        state.listings = {}
    state.listings[path] = sorted(
        p for p in getattr(state, 'remote_files', {}) if p.startswith(path + '/')
    )
    # END: Effects

    return state


def a_fs_upload(state: State, local_path: str, remote_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_upload

    Action signature:
        a_fs_upload(state, local_path, remote_path)

    Action parameters:
        local_path: File on the workstation to send
        remote_path: Destination path on the cluster filesystem

    Action purpose:
        Upload a file with rsync and verify it with a SHA-256 checksum

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Local file exists (state.local_files)
        - Destination directory exists (state.remote_dirs)
        - The storage tier has room for the file (state.storage_tiers)

    Effects:
        - Remote file is registered with its size (state.remote_files) [DATA]
        - Tier usage is increased (state.storage_tiers) [DATA]
        - Transfer checksum is recorded (state.checksums) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(local_path, str): return False
    if not isinstance(remote_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not local_path.strip(): return False
    if not remote_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The local file must exist
    if local_path not in getattr(state, 'local_files', {}):
        return False
    # The destination directory must exist
    parent = remote_path.rsplit('/', 1)[0]
    if parent not in getattr(state, 'remote_dirs', []):
        return False
    # The tier must have room: /home is 5 GB and is not for datasets
    size_gb = state.local_files[local_path]
    tier = h_tier_for_path(state, remote_path)
    if tier is None:
        return False
    quota = state.storage_tiers[tier]
    if quota['used_gb'] + size_gb > quota['quota_gb']:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] The file now exists on Lustre
    if not hasattr(state, 'remote_files'):
        state.remote_files = {}
    state.remote_files[remote_path] = size_gb

    # [DATA] Tier occupancy grows accordingly
    state.storage_tiers[tier]['used_gb'] = quota['used_gb'] + size_gb

    # [ENABLER] rsync verified the transfer with a SHA-256 checksum
    if not hasattr(state, 'checksums'):
        state.checksums = {}
    state.checksums[remote_path] = f"sha256:{remote_path}"
    # END: Effects

    return state


def a_fs_download(state: State, remote_path: str, local_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_download

    Action signature:
        a_fs_download(state, remote_path, local_path)

    Action parameters:
        remote_path: File on the cluster to retrieve
        local_path: Destination path on the workstation

    Action purpose:
        Download a result file with rsync and SHA-256 verification

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Remote file exists (state.remote_files)
        - Any job that owns the file has reached a terminal state (state.file_owner_job)

    Effects:
        - Local copy is registered (state.local_files) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(remote_path, str): return False
    if not isinstance(local_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not remote_path.strip(): return False
    if not local_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The file must already exist on the cluster
    if remote_path not in getattr(state, 'remote_files', {}):
        return False
    # A file still being written by a running job must not be collected
    owner = getattr(state, 'file_owner_job', {}).get(remote_path)
    if owner is not None and not h_job_is_terminal(state, owner):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] The result now exists on the workstation
    if not hasattr(state, 'local_files'):
        state.local_files = {}
    state.local_files[local_path] = state.remote_files[remote_path]
    # END: Effects

    return state


def a_fs_checksum(state: State, path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_checksum

    Action signature:
        a_fs_checksum(state, path)

    Action parameters:
        path: Remote file to hash

    Action purpose:
        Compute the SHA-256 checksum of a remote file

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Remote file exists (state.remote_files)
        - Checksum not already computed (state.checksums)

    Effects:
        - Checksum is recorded (state.checksums) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The file must exist
    if path not in getattr(state, 'remote_files', {}):
        return False
    # Re-hashing a file we already hashed would leave the state unchanged
    if path in getattr(state, 'checksums', {}):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] SHA-256 of the remote file
    if not hasattr(state, 'checksums'):
        state.checksums = {}
    state.checksums[path] = f"sha256:{path}"
    # END: Effects

    return state


def a_fs_tail(state: State, path: str, lines: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_tail

    Action signature:
        a_fs_tail(state, path, lines)

    Action parameters:
        path: Remote file to read from the end
        lines: Number of trailing lines to return

    Action purpose:
        Read the tail of a running or finished job's stdout file

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - File exists, or is the stdout of a job that has started
          (state.remote_files, state.file_owner_job)

    Effects:
        - Tail content is recorded (state.tail_output) [DATA]
        - Read counter is incremented (state.tail_reads) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(path, str): return False
    if not isinstance(lines, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not path.strip(): return False
    if lines <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    owner = getattr(state, 'file_owner_job', {}).get(path)
    if owner is None:
        # An ordinary file simply has to exist
        if path not in getattr(state, 'remote_files', {}):
            return False
    else:
        # Slurm only creates slurm-<id>.out once the job starts running
        if state.jobs[owner]['state'] == 'QUEUED':
            return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Last lines of the file
    if not hasattr(state, 'tail_output'):
        state.tail_output = {}
    state.tail_output[path] = f"last {lines} lines of {path}"

    # [DATA] Read counter, guaranteeing this action is never idempotent
    if not hasattr(state, 'tail_reads'):
        state.tail_reads = {}
    state.tail_reads[path] = state.tail_reads.get(path, 0) + 1
    # END: Effects

    return state


def a_fs_compress(state: State, paths: List[str], archive_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_compress

    Action signature:
        a_fs_compress(state, paths, archive_path)

    Action parameters:
        paths: Remote paths to place in the archive
        archive_path: Destination archive path on the cluster (gzip by default)

    Action purpose:
        Create a gzip tar archive from one or more remote paths

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - The path list is not empty (paths)
        - Every path exists (state.remote_files)
        - Archive does not already exist (state.remote_files)

    Effects:
        - Archive file is registered (state.remote_files) [DATA]
        - Archive contents are recorded (state.archives) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(paths, list): return False
    if not all(isinstance(p, str) for p in paths): return False
    if not isinstance(archive_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not paths: return False
    if not archive_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # tar cannot archive files that are not there
    if any(p not in getattr(state, 'remote_files', {}) for p in paths):
        return False
    # Overwriting an existing archive is not modelled
    if archive_path in state.remote_files:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] The archive, sized from the files it contains
    total_gb = sum(state.remote_files[p] for p in paths)
    state.remote_files[archive_path] = round(total_gb / 2.0, 3)

    # [ENABLER] Archive membership - gates fs_extract
    if not hasattr(state, 'archives'):
        state.archives = {}
    state.archives[archive_path] = list(paths)
    # END: Effects

    return state


def a_fs_extract(state: State, archive_path: str, dest_dir: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_extract

    Action signature:
        a_fs_extract(state, archive_path, dest_dir)

    Action parameters:
        archive_path: Archive to unpack on the cluster
        dest_dir: Destination directory, created when missing

    Action purpose:
        Extract an archive back into a directory on the cluster

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Archive exists and its membership is known (state.archives)

    Effects:
        - Destination directory is registered (state.remote_dirs) [DATA]
        - Extracted members are registered (state.remote_files) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(archive_path, str): return False
    if not isinstance(dest_dir, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not archive_path.strip(): return False
    if not dest_dir.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The archive must exist and we must know what is inside it
    if archive_path not in getattr(state, 'archives', {}):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] fs_extract creates the destination directory when needed
    if not hasattr(state, 'remote_dirs'):
        state.remote_dirs = []
    if dest_dir not in state.remote_dirs:
        state.remote_dirs.append(dest_dir)

    # [DATA] Each member reappears under the destination directory
    for member in state.archives[archive_path]:
        leaf = member.rsplit('/', 1)[-1]
        state.remote_files[f"{dest_dir}/{leaf}"] = state.remote_files[member]
    # END: Effects

    return state


# ============================================================================
# CONTAINER IMAGE ACTIONS - local workstation, no MCP server (4)
# ============================================================================

def a_write_dockerfile(state: State, image_ref: str, base_image: str,
                       arch: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_write_dockerfile(state, image_ref, base_image, arch)

    Action parameters:
        image_ref: Tag the built image will carry
        base_image: Base image the recipe starts from (e.g. a CUDA runtime)
        arch: Target architecture of the build ('aarch64' or 'x86_64')

    Action purpose:
        Write the Dockerfile for the training image

    Preconditions:
        - No recipe for this tag yet (state.dockerfiles)

    Effects:
        - Recipe is recorded (state.dockerfiles) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(image_ref, str): return False
    if not isinstance(base_image, str): return False
    if not isinstance(arch, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not image_ref.strip(): return False
    if not base_image.strip(): return False
    if arch not in ('aarch64', 'x86_64'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Rewriting an identical recipe would leave the state unchanged
    if image_ref in getattr(state, 'dockerfiles', {}):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] The recipe now exists - gates a_build_image
    if not hasattr(state, 'dockerfiles'):
        state.dockerfiles = {}
    state.dockerfiles[image_ref] = {'base': base_image, 'arch': arch}
    # END: Effects

    return state


def a_build_image(state: State, image_ref: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_build_image(state, image_ref)

    Action parameters:
        image_ref: Tag of the image to build from its recipe

    Action purpose:
        Build the container image locally for the recipe's target architecture

    Preconditions:
        - A recipe exists for the tag (state.dockerfiles)
        - The image has not been built yet (state.images)

    Effects:
        - Built image with its architecture is registered (state.images) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(image_ref, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not image_ref.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # You cannot build what has no recipe
    if image_ref not in getattr(state, 'dockerfiles', {}):
        return False
    # Rebuilding an existing image would leave the state unchanged
    if image_ref in getattr(state, 'images', {}):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] The image exists locally, tagged with the architecture it was
    # built for - that architecture is what later gates every execution site
    if not hasattr(state, 'images'):
        state.images = {}
    state.images[image_ref] = {
        'arch': state.dockerfiles[image_ref]['arch'],
        'size_gb': getattr(state, 'workload', {}).get('image_size_gb', 8.0),
    }
    # END: Effects

    return state


def a_verify_image_arch(state: State, image_ref: str, target_arch: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_verify_image_arch(state, image_ref, target_arch)

    Action parameters:
        image_ref: Tag of the built image to inspect
        target_arch: Architecture of the machine that will run it

    Action purpose:
        Refuse an image whose architecture does not match its execution site

    Preconditions:
        - The image has been built (state.images)
        - Image architecture equals the target architecture (state.images[ref]['arch'])

    Effects:
        - Architecture check is recorded (state.image_arch_verified) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(image_ref, str): return False
    if not isinstance(target_arch, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not image_ref.strip(): return False
    if target_arch not in ('aarch64', 'x86_64'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # The image must have been built
    if image_ref not in getattr(state, 'images', {}):
        return False
    # An x86_64 image on an aarch64 host dies with "Exec format error"
    if state.images[image_ref]['arch'] != target_arch:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Architecture verified - gates a_push_image
    if not hasattr(state, 'image_arch_verified'):
        state.image_arch_verified = {}
    state.image_arch_verified[image_ref] = True
    # END: Effects

    return state


def a_push_image(state: State, image_ref: str, registry: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_push_image(state, image_ref, registry)

    Action parameters:
        image_ref: Tag of the verified image to publish
        registry: Registry host the image is pushed to

    Action purpose:
        Publish the image so the rented instance can pull it

    Preconditions:
        - The image architecture has been verified (state.image_arch_verified)
        - The image has not been pushed yet (state.pushed_images)

    Effects:
        - Published image reference is registered (state.pushed_images) [ENABLER]
        - Publication target is recorded (state.image_registry) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(image_ref, str): return False
    if not isinstance(registry, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not image_ref.strip(): return False
    if not registry.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Never publish an image we have not architecture-checked
    if not getattr(state, 'image_arch_verified', {}).get(image_ref):
        return False
    # Pushing twice would leave the state unchanged
    if image_ref in getattr(state, 'pushed_images', []):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] The image is pullable - gates a_vast_create_instance
    if not hasattr(state, 'pushed_images'):
        state.pushed_images = []
    state.pushed_images.append(image_ref)

    # [DATA] Where it was published
    if not hasattr(state, 'image_registry'):
        state.image_registry = {}
    state.image_registry[image_ref] = registry
    # END: Effects

    return state


# ============================================================================
# VAST.AI ACTIONS - Server 4: vastai (7)
# ============================================================================

def a_vast_search_offers(state: State, gpu_name: str, num_gpus: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: vastai:search_offers

    Action signature:
        a_vast_search_offers(state, gpu_name, num_gpus)

    Action parameters:
        gpu_name: GPU model to filter on (e.g. 'H100_SXM')
        num_gpus: Minimum number of GPUs the offer must expose

    Action purpose:
        Find rentable offers matching a GPU model and count

    Preconditions:
        - Server 4 is ready (state.server_4_ready)
        - At least one offer matches (state.vast_offers)

    Effects:
        - Matching offer ids are recorded (state.offer_hits) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(gpu_name, str): return False
    if not isinstance(num_gpus, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not gpu_name.strip(): return False
    if num_gpus <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 4 must be ready
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # 'vastai search offers gpu_name=X num_gpus>=N' must return something
    hits = sorted(
        offer_id for offer_id, offer in getattr(state, 'vast_offers', {}).items()
        if offer['gpu_name'] == gpu_name and offer['num_gpus'] >= num_gpus
    )
    if not hits:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Rentable offer ids - gates a_vast_create_instance
    state.offer_hits = hits
    # END: Effects

    return state


def a_vast_create_instance(state: State, offer_id: str, image_ref: str, disk_gb: int,
                           onstart_cmd: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: vastai:create_instance

    Action signature:
        a_vast_create_instance(state, offer_id, image_ref, disk_gb, onstart_cmd)

    Action parameters:
        offer_id: Offer to rent, taken from the search results
        image_ref: Published image the instance will pull
        disk_gb: Disk partition size, fixed for the instance's whole life
        onstart_cmd: Command the container runs once it comes up

    Action purpose:
        Rent an offer and launch the training container on it

    Preconditions:
        - Server 4 is ready (state.server_4_ready)
        - Offer came out of a search (state.offer_hits)
        - Image has been published (state.pushed_images)
        - Image architecture matches the offer host (state.vast_offers[offer]['arch'])
        - Disk is large enough for image, dataset and checkpoints (state.workload)
        - Disk fits what the host can allocate (state.vast_offers[offer]['max_disk_gb'])

    Effects:
        - Instance record is created (state.instances) [DATA]
        - Instance id counter is advanced (state.next_instance_id) [DATA]
        - Control-plane trajectory is attached (state.instance_trajectory) [DATA]
        - Training trajectory is attached (state.training_trajectory) [DATA]
        - Training starts out unfinished (state.training_state) [DATA]
        - Most recent instance id is recorded (state.last_instance_id) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(offer_id, str): return False
    if not isinstance(image_ref, str): return False
    if not isinstance(disk_gb, int): return False
    if not isinstance(onstart_cmd, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not offer_id.strip(): return False
    if not image_ref.strip(): return False
    if not onstart_cmd.strip(): return False
    if disk_gb <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 4 must be ready
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # The offer must be one the search returned
    if offer_id not in getattr(state, 'offer_hits', []):
        return False
    # The instance pulls the image from a registry, so it must be published
    if image_ref not in getattr(state, 'pushed_images', []):
        return False
    # The image must match the rented host's architecture
    offer = state.vast_offers[offer_id]
    if state.images[image_ref]['arch'] != offer['arch']:
        return False
    # --disk is a static allocation set at creation and cannot be changed later,
    # so it must already hold image + dataset + checkpoints
    required = state.workload['required_disk_gb']
    if disk_gb < required:
        return False
    # The host must be able to allocate that much
    if disk_gb > offer['max_disk_gb']:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] vast.ai mints an opaque instance id
    instance_id = f"i-{state.next_instance_id}"
    state.next_instance_id += 1

    # [DATA] The instance starts in Creating and pulls the image
    label = state.workload['label']
    if not hasattr(state, 'instances'):
        state.instances = {}
    state.instances[instance_id] = {
        'offer': offer_id,
        'image': image_ref,
        'disk_gb': disk_gb,
        'disk_used_gb': state.images[image_ref]['size_gb'],
        'onstart': onstart_cmd,
        'label': label,
        'state': 'Creating',
    }

    # [DATA] Scripted control-plane trajectory: Creating -> Loading -> ... -> Running
    if not hasattr(state, 'instance_trajectory'):
        state.instance_trajectory = {}
    state.instance_trajectory[instance_id] = list(
        getattr(state, 'instance_script', {}).get(
            label, ['Loading', 'Connecting', 'Running'])
    )

    # [DATA] Scripted training trajectory, read back through the container logs
    if not hasattr(state, 'training_trajectory'):
        state.training_trajectory = {}
    state.training_trajectory[instance_id] = list(
        getattr(state, 'training_script', {}).get(label, ['epoch-1', 'done'])
    )
    if not hasattr(state, 'training_state'):
        state.training_state = {}
    state.training_state[instance_id] = 'starting'

    # [DATA] Handles later methods infer from the state
    state.last_instance_id = instance_id
    # END: Effects

    return state


def a_vast_poll_instance(state: State, instance_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: vastai:show_instance

    Action signature:
        a_vast_poll_instance(state, instance_id)

    Action parameters:
        instance_id: Opaque vast.ai instance identifier

    Action purpose:
        Observe an instance moving from Creating to Running

    Preconditions:
        - Server 4 is ready (state.server_4_ready)
        - Instance exists and is not yet Running (state.instances)
        - The control plane still has a transition (state.instance_trajectory)

    Effects:
        - Instance state advances (state.instances[id]['state']) [EXPECTED_EFFECT]
        - The consumed transition leaves the trajectory (state.instance_trajectory) [DATA]
        - Poll counter is incremented (state.instance_polls) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(instance_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not instance_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 4 must be ready
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # The instance must exist
    if instance_id not in getattr(state, 'instances', {}):
        return False
    # A Running instance needs no further polling
    if state.instances[instance_id]['state'] == VAST_READY_STATE:
        return False
    # The control plane must still have a transition left
    if not state.instance_trajectory.get(instance_id):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [EXPECTED_EFFECT] The vast.ai control plane - not this tool call - pulls
    # the image and brings the container up. The planner carries the transition
    # so that copy_in and logs can be planned against a Running instance.
    state.instances[instance_id]['state'] = state.instance_trajectory[instance_id].pop(0)

    # [DATA] Poll counter, guaranteeing this action is never idempotent
    if not hasattr(state, 'instance_polls'):
        state.instance_polls = {}
    state.instance_polls[instance_id] = state.instance_polls.get(instance_id, 0) + 1
    # END: Effects

    return state


def a_vast_copy_in(state: State, local_path: str, instance_id: str,
                   remote_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: vastai:copy

    Action signature:
        a_vast_copy_in(state, local_path, instance_id, remote_path)

    Action parameters:
        local_path: File on the workstation to send
        instance_id: Destination instance
        remote_path: Destination path inside the instance

    Action purpose:
        Copy the training dataset into a running instance

    Preconditions:
        - Server 4 is ready (state.server_4_ready)
        - Local file exists (state.local_files)
        - Instance is Running (state.instances[id]['state'])
        - The static disk allocation still has room (state.instances[id]['disk_gb'])

    Effects:
        - File is registered inside the instance (state.instance_files) [ENABLER]
        - Instance disk usage grows (state.instances[id]['disk_used_gb']) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(local_path, str): return False
    if not isinstance(instance_id, str): return False
    if not isinstance(remote_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not local_path.strip(): return False
    if not instance_id.strip(): return False
    if not remote_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 4 must be ready
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # The local file must exist
    if local_path not in getattr(state, 'local_files', {}):
        return False
    # The instance must exist and accept traffic
    if instance_id not in getattr(state, 'instances', {}):
        return False
    instance = state.instances[instance_id]
    if instance['state'] != VAST_READY_STATE:
        return False
    # The disk was sized at creation and cannot grow
    size_gb = state.local_files[local_path]
    if instance['disk_used_gb'] + size_gb > instance['disk_gb']:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] The dataset is in place - gates the training logs turning 'done'
    if not hasattr(state, 'instance_files'):
        state.instance_files = {}
    state.instance_files.setdefault(instance_id, {})[remote_path] = size_gb

    # [DATA] Disk occupancy inside the static allocation
    instance['disk_used_gb'] = instance['disk_used_gb'] + size_gb
    # END: Effects

    return state


def a_vast_logs(state: State, instance_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: vastai:logs

    Action signature:
        a_vast_logs(state, instance_id)

    Action parameters:
        instance_id: Instance whose container logs are read

    Action purpose:
        Read container logs to follow the training run to completion

    Preconditions:
        - Server 4 is ready (state.server_4_ready)
        - Instance is Running (state.instances[id]['state'])
        - The dataset has been copied in (state.instance_files)
        - Training is not already finished (state.training_state)
        - The run still has a step to report (state.training_trajectory)

    Effects:
        - Training state advances (state.training_state) [EXPECTED_EFFECT]
        - The consumed step leaves the trajectory (state.training_trajectory) [DATA]
        - The checkpoint appears once training finishes (state.instance_files) [EXPECTED_EFFECT]
        - The checkpoint occupies instance disk (state.instances) [EXPECTED_EFFECT]
        - Log read counter is incremented (state.log_reads) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(instance_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not instance_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 4 must be ready
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # The instance must exist and be up
    if instance_id not in getattr(state, 'instances', {}):
        return False
    if state.instances[instance_id]['state'] != VAST_READY_STATE:
        return False
    # The onstart command cannot train on a dataset that is not there
    dataset_path = state.workload['dataset_remote']
    if dataset_path not in getattr(state, 'instance_files', {}).get(instance_id, {}):
        return False
    # A finished run has nothing more to report
    if state.training_state.get(instance_id) == 'done':
        return False
    # The run must still have a step left
    if not state.training_trajectory.get(instance_id):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [EXPECTED_EFFECT] The container - not this tool call - makes progress. The
    # logs only report it, but the planner must carry it so that copy_out can be
    # planned against a finished run.
    step = state.training_trajectory[instance_id].pop(0)
    state.training_state[instance_id] = step

    # [DATA] Log read counter, guaranteeing this action is never idempotent
    if not hasattr(state, 'log_reads'):
        state.log_reads = {}
    state.log_reads[instance_id] = state.log_reads.get(instance_id, 0) + 1

    # [EXPECTED_EFFECT] The training process wrote the checkpoint before exiting
    if step == 'done':
        checkpoint = state.workload['checkpoint_remote']
        size_gb = state.workload['checkpoint_gb']
        state.instance_files[instance_id][checkpoint] = size_gb
        state.instances[instance_id]['disk_used_gb'] += size_gb
    # END: Effects

    return state


def a_vast_copy_out(state: State, instance_id: str, remote_path: str,
                    local_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: vastai:copy

    Action signature:
        a_vast_copy_out(state, instance_id, remote_path, local_path)

    Action parameters:
        instance_id: Instance to copy from
        remote_path: File inside the instance
        local_path: Destination path on the workstation

    Action purpose:
        Retrieve the trained checkpoint before the instance is destroyed

    Preconditions:
        - Server 4 is ready (state.server_4_ready)
        - Instance is Running (state.instances[id]['state'])
        - The file exists inside the instance (state.instance_files)

    Effects:
        - Local copy is registered (state.local_files) [DATA]
        - Results are marked as retrieved (state.results_copied_out) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(instance_id, str): return False
    if not isinstance(remote_path, str): return False
    if not isinstance(local_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not instance_id.strip(): return False
    if not remote_path.strip(): return False
    if not local_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 4 must be ready
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # The instance must exist and still be up
    if instance_id not in getattr(state, 'instances', {}):
        return False
    if state.instances[instance_id]['state'] != VAST_READY_STATE:
        return False
    # The file must exist inside the container
    if remote_path not in getattr(state, 'instance_files', {}).get(instance_id, {}):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] The checkpoint now exists on the workstation
    if not hasattr(state, 'local_files'):
        state.local_files = {}
    state.local_files[local_path] = state.instance_files[instance_id][remote_path]

    # [ENABLER] Results retrieved - the only thing that makes destroy safe
    if not hasattr(state, 'results_copied_out'):
        state.results_copied_out = {}
    state.results_copied_out[instance_id] = True
    # END: Effects

    return state


def a_vast_destroy_instance(state: State, instance_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: vastai:destroy_instance

    Action signature:
        a_vast_destroy_instance(state, instance_id)

    Action parameters:
        instance_id: Instance to terminate

    Action purpose:
        Terminate a rented instance and stop billing

    Preconditions:
        - Server 4 is ready (state.server_4_ready)
        - Instance exists and is not already destroyed (state.instances)
        - Results have been copied out (state.results_copied_out)

    Effects:
        - Instance state becomes Destroyed (state.instances[id]['state']) [ENABLER]
        - Every file inside the instance is lost (state.instance_files) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(instance_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not instance_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 4 must be ready
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # The instance must exist and still be alive
    if instance_id not in getattr(state, 'instances', {}):
        return False
    if state.instances[instance_id]['state'] == 'Destroyed':
        return False
    # Destroying an instance deletes its disk permanently. No plan may reach
    # this action before the results have been retrieved: this single
    # precondition is what a free-running ReAct loop cannot guarantee.
    if not getattr(state, 'results_copied_out', {}).get(instance_id):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] The instance is gone and no longer billed
    state.instances[instance_id]['state'] = 'Destroyed'

    # [DATA] Everything on the instance disk is deleted permanently
    if hasattr(state, 'instance_files'):
        state.instance_files[instance_id] = {}
    # END: Effects

    return state


# ============================================================================
# APPTAINER ACTIONS - Server 2: rikyu-hpc (6)
# ----------------------------------------------------------------------------
# Rikyu runs Apptainer 1.4.5 unprivileged, exposed under the 'singularity'
# name. None of it is advertised: it is absent from the facility metadata, from
# the bundled guide and from 'module avail', reaching PATH only through
# /etc/profile.d/apptainer-path.sh. A plan therefore has to probe the login
# node before it can know the runtime exists.
#
# There is no scheduler integration - no Pyxis (PlugStackConfig is null) and no
# configured Slurm OCI runtime - so a container job is an ordinary sbatch job
# whose executable happens to start with 'singularity exec'.
# ============================================================================

def a_probe_container_runtime(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:run_command_on_cluster

    Action signature:
        a_probe_container_runtime(state)

    Action parameters:
        None

    Action purpose:
        Discover whether a container runtime exists, by probing the login node

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - The runtime has not been probed yet (state.container_runtime_known)

    Effects:
        - The runtime found, or None (state.container_runtime) [DATA]
        - Probe completed, whatever the outcome (state.container_runtime_known) [ENABLER]
        - Probe command output is recorded (state.command_output) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Probing twice would leave the state unchanged
    if getattr(state, 'container_runtime_known', False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] What 'command -v singularity' finds, or None. A negative result is
    # a successful probe: it is how a plan learns it must go somewhere else.
    state.container_runtime = getattr(state, 'login_binaries', {}).get('singularity')

    # [DATA] The probe itself
    if not hasattr(state, 'command_output'):
        state.command_output = {}
    state.command_output['command -v singularity'] = (
        state.container_runtime['path'] if state.container_runtime else '')

    # [ENABLER] The runtime question is now settled - gates backend routing
    state.container_runtime_known = True
    # END: Effects

    return state


def a_list_staged_images(state: State, path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:fs_ls

    Action signature:
        a_list_staged_images(state, path)

    Action parameters:
        path: Directory holding the site's prebuilt SIF images

    Action purpose:
        Discover the site image library, which nothing on the machine points at

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - The directory is a known image root (state.site_images)

    Effects:
        - The staged images become known (state.staged_images) [DATA]
        - Library listing completed (state.staged_images_known) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # There must be an image tree at that path
    if not any(p.startswith(path) for p in getattr(state, 'site_images', {})):
        return False
    # Listing twice would leave the state unchanged
    if getattr(state, 'staged_images_known', False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Prebuilt images the site already provides. Running one of these
    # costs no user quota, while pulling an equivalent image costs its full
    # size on a tier that in the home case cannot even hold it.
    if not hasattr(state, 'staged_images'):
        state.staged_images = {}
    for image_path, meta in state.site_images.items():
        if image_path.startswith(path):
            state.staged_images[image_path] = dict(meta)

    # [ENABLER] The library is now known - gates reusing a staged image
    state.staged_images_known = True
    # END: Effects

    return state


def a_set_apptainer_env(state: State, cachedir: str, tmpdir: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:run_command_on_cluster

    Action signature:
        a_set_apptainer_env(state, cachedir, tmpdir)

    Action parameters:
        cachedir: Value for APPTAINER_CACHEDIR
        tmpdir: Value for APPTAINER_TMPDIR

    Action purpose:
        Redirect the conversion cache and scratch off the small home tier

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Both targets are on known storage tiers (state.storage_tiers)
        - The environment has not been set yet (state.apptainer_env_set)

    Effects:
        - Environment values are recorded (state.apptainer_env) [DATA]
        - Environment is configured (state.apptainer_env_set) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(cachedir, str): return False
    if not isinstance(tmpdir, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not cachedir.strip(): return False
    if not tmpdir.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Both paths must live on a tier we know the size of. Note that this action
    # does NOT reject a home-tier cache: the failure surfaces at the pull, when
    # the layers no longer fit, which is where it surfaces in practice too.
    if h_tier_for_path(state, cachedir) is None:
        return False
    if h_tier_for_path(state, tmpdir) is None:
        return False
    # Setting the same environment twice would leave the state unchanged
    if getattr(state, 'apptainer_env_set', False):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] APPTAINER_CACHEDIR and APPTAINER_TMPDIR, both unset by default,
    # which puts them under a 5 GiB home tier that no real image fits in
    state.apptainer_env = {'APPTAINER_CACHEDIR': cachedir, 'APPTAINER_TMPDIR': tmpdir}

    # [ENABLER] Conversion environment configured - gates a_apptainer_pull
    state.apptainer_env_set = True
    # END: Effects

    return state


def a_apptainer_pull(state: State, transport: str, reference: str,
                     sif_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:run_command_on_cluster

    Action signature:
        a_apptainer_pull(state, transport, reference, sif_path)

    Action parameters:
        transport: Apptainer build-source transport, e.g. 'docker' or 'docker-archive'
        reference: Image reference or archive path for that transport
        sif_path: Destination SIF path on the cluster filesystem

    Action purpose:
        Convert an OCI image to SIF, unprivileged, with no root and no fakeroot

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - A container runtime was found (state.container_runtime)
        - The transport is usable on Rikyu (USABLE_TRANSPORTS)
        - The conversion environment is configured (state.apptainer_env_set)
        - The cache tier has about twice the image size free (state.storage_tiers)
        - The destination directory exists (state.remote_dirs)
        - The image is not already converted (state.sif_images)

    Effects:
        - The SIF exists, carrying the source image's architecture (state.sif_images) [DATA]
        - The SIF is registered on the filesystem (state.remote_files) [DATA]
        - Cache tier usage grows (state.storage_tiers) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(transport, str): return False
    if not isinstance(reference, str): return False
    if not isinstance(sif_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not reference.strip(): return False
    if not sif_path.strip(): return False
    if transport not in USABLE_TRANSPORTS: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The runtime must have been probed and found
    if not getattr(state, 'container_runtime', None):
        return False
    # The cache and scratch must have been redirected off the home tier
    if not getattr(state, 'apptainer_env_set', False):
        return False
    # The source image must be one we can reach
    source = getattr(state, 'oci_images', {}).get(reference)
    if source is None:
        return False
    # Layers are unpacked before squashfs packing, so the cache tier needs
    # roughly twice the image size free
    tier = h_tier_for_path(state, state.apptainer_env['APPTAINER_CACHEDIR'])
    quota = state.storage_tiers[tier]
    needed = source['size_gb'] * CONVERSION_HEADROOM_FACTOR
    if quota['used_gb'] + needed > quota['quota_gb']:
        return False
    # The destination directory must exist
    parent = sif_path.rsplit('/', 1)[0]
    if parent not in getattr(state, 'remote_dirs', []):
        return False
    # Converting twice would leave the state unchanged
    if sif_path in getattr(state, 'sif_images', {}):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] The SIF, carrying the architecture of the image it came from. Note
    # that conversion succeeds whatever that architecture is: an x86_64 image
    # converts cleanly here and only fails later, at exec. That is why
    # a_verify_sif_arch exists as a separate, explicit step.
    if not hasattr(state, 'sif_images'):
        state.sif_images = {}
    state.sif_images[sif_path] = {
        'arch': source['arch'],
        'size_gb': source['size_gb'],
        'source': f'{transport}:{reference}',
    }

    # [DATA] The SIF is now an ordinary file on the cluster
    state.remote_files[sif_path] = source['size_gb']

    # [DATA] The conversion left its layers in the cache
    state.storage_tiers[tier]['used_gb'] = quota['used_gb'] + source['size_gb']
    # END: Effects

    return state


def a_verify_sif_arch(state: State, sif_path: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:run_command_on_cluster

    Action signature:
        a_verify_sif_arch(state, sif_path)

    Action parameters:
        sif_path: SIF whose build-arch label is inspected

    Action purpose:
        Refuse a SIF the compute nodes cannot execute, before submitting it

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - The SIF exists, converted or staged (state.sif_images, state.staged_images)
        - Its build-arch equals the node architecture (state.cluster_arch)

    Effects:
        - Architecture check is recorded (state.sif_arch_verified) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(sif_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not sif_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The facility architecture must be known to compare against
    if not (hasattr(state, 'facility_known') and state.facility_known):
        return False
    # The SIF must exist, either converted here or staged by the site
    image = (getattr(state, 'sif_images', {}).get(sif_path)
             or getattr(state, 'staged_images', {}).get(sif_path))
    if image is None:
        return False
    # An x86_64 SIF converts cleanly and then dies at exec with "Exec format
    # error". This check is the only thing that turns that late, silent failure
    # into a planning-time one.
    if image['arch'] != state.cluster_arch:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] The SIF can execute here - gates a_submit_container_job
    if not hasattr(state, 'sif_arch_verified'):
        state.sif_arch_verified = {}
    state.sif_arch_verified[sif_path] = True
    # END: Effects

    return state


def a_submit_container_job(state: State, name: str, gpus: int, duration: str,
                           directory: str, sif_path: str, command: str,
                           binds: List[str]) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: rikyu-hpc:submit_job

    Action signature:
        a_submit_container_job(state, name, gpus, duration, directory, sif_path,
                               command, binds)

    Action parameters:
        name: JobSpec name
        gpus: JobSpec resources.gpus (must be 1, 2, 3, 4, 8, 12 or 16)
        duration: JobSpec attributes.duration, e.g. '12:00:00'
        directory: JobSpec directory, the working directory of the job
        sif_path: SIF the job runs
        command: Command passed to 'singularity exec', which never inherits
            the image's ENTRYPOINT or CMD
        binds: Host paths bound into the container with --bind

    Action purpose:
        Submit an ordinary sbatch job whose executable wraps singularity exec

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - Facility metadata has been fetched (state.facility_known)
        - A container runtime was found (state.container_runtime)
        - GPU count is supported (state.supported_gpu_counts)
        - Wall time is within the ceiling (state.max_wall_time_hours)
        - Working directory exists (state.remote_dirs)
        - The SIF's architecture has been verified (state.sif_arch_verified)
        - An explicit command is given (command)
        - Every path the job needs is auto-bound or explicitly bound (state.auto_bind_paths)
        - The working directory itself is visible inside the container (binds)

    Effects:
        - Job record with a fresh job id is created (state.jobs) [DATA]
        - Container invocation is recorded (state.jobs[job_id]['container']) [DATA]
        - Job id counter is advanced (state.next_job_id) [DATA]
        - Scheduler trajectory is attached (state.job_trajectory) [DATA]
        - Poll counter is initialised (state.poll_count) [DATA]
        - Standard output path is registered (state.file_owner_job) [DATA]
        - Job is added to the submitted list (state.submitted_jobs) [DATA]
        - Most recent job id is recorded (state.last_job_id) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    if not isinstance(sif_path, str): return False
    if not isinstance(command, str): return False
    if not isinstance(binds, list): return False
    if not all(isinstance(b, str) for b in binds): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    if not directory.strip(): return False
    if not sif_path.strip(): return False
    if gpus <= 0: return False
    duration_hours = h_hours_from_slurm_time(duration)
    if duration_hours is None or duration_hours <= 0: return False
    # apptainer exec ignores the image's runscript, so an empty command would
    # simply run nothing
    if not command.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # The facility must be known, as for any submission
    if not (hasattr(state, 'facility_known') and state.facility_known):
        return False
    # There is no Pyxis and no configured Slurm OCI runtime, so the container
    # is a payload: the runtime has to exist on the login node we submit from
    if not getattr(state, 'container_runtime', None):
        return False
    # The ordinary submission rules still apply
    if gpus not in state.supported_gpu_counts:
        return False
    if duration_hours > state.max_wall_time_hours:
        return False
    if directory not in getattr(state, 'remote_dirs', []):
        return False
    # The SIF must have been architecture-checked
    if not getattr(state, 'sif_arch_verified', {}).get(sif_path):
        return False
    # Only $HOME, /tmp and a couple of /etc files are bound by default. Group
    # storage and the shared trees are not, so every path the job reads or
    # writes must be auto-bound or explicitly bound.
    auto = getattr(state, 'auto_bind_paths', [])
    for needed in getattr(state, 'container_needs', {}).get(name, []):
        visible = (any(needed.startswith(a) for a in auto)
                   or any(needed.startswith(b) for b in binds))
        if not visible:
            return False
    # The working directory is inherited from the host, so a cwd that is not
    # visible inside the container does not exist there either
    if not (any(directory.startswith(a) for a in auto)
            or any(directory.startswith(b) for b in binds)):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Slurm mints an opaque job id, exactly as for a non-container job
    job_id = str(state.next_job_id)
    state.next_job_id += 1

    # [DATA] Job record. --nv is the classic library injection, the only GPU
    # passthrough available: nvidia-container-cli is absent, so --nvccli is not
    # an option.
    if not hasattr(state, 'jobs'):
        state.jobs = {}
    stdout_path = f"{directory}/slurm-{job_id}.out"
    state.jobs[job_id] = {
        'name': name,
        'gpus': gpus,
        'processes_per_node': 0,
        'duration': duration,
        'duration_hours': duration_hours,
        'directory': directory,
        'stdout': stdout_path,
        'state': 'QUEUED',
        'container': {
            'sif': sif_path,
            'command': command,
            'binds': list(binds),
            'nv': gpus > 0,
        },
    }

    # [DATA] Scripted scheduler trajectory for this job
    if not hasattr(state, 'job_trajectory'):
        state.job_trajectory = {}
    state.job_trajectory[job_id] = list(
        getattr(state, 'job_script', {}).get(name, ['ACTIVE', 'COMPLETED'])
    )

    # [DATA] Poll counter, so repeated polling is never elided from the plan
    if not hasattr(state, 'poll_count'):
        state.poll_count = {}
    state.poll_count[job_id] = 0

    # [DATA] The stdout file belongs to this job
    if not hasattr(state, 'file_owner_job'):
        state.file_owner_job = {}
    state.file_owner_job[stdout_path] = job_id

    # [DATA] Submitted job list and the handle later methods infer
    if not hasattr(state, 'submitted_jobs'):
        state.submitted_jobs = []
    state.submitted_jobs.append(job_id)
    state.last_job_id = job_id
    # END: Effects

    return state


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_initialize_servers,
    a_get_facility,
    a_get_resources,
    a_get_resource,
    a_list_doc_sections,
    a_search_docs,
    a_read_doc_section,
    a_submit_job,
    a_poll_job_status,
    a_get_job_statuses,
    a_cancel_job,
    a_update_job,
    a_run_command_on_cluster,
    a_fs_mkdir,
    a_fs_ls,
    a_fs_upload,
    a_fs_download,
    a_fs_checksum,
    a_fs_tail,
    a_fs_compress,
    a_fs_extract,
    a_write_dockerfile,
    a_build_image,
    a_verify_image_arch,
    a_push_image,
    a_vast_search_offers,
    a_vast_create_instance,
    a_vast_poll_instance,
    a_vast_copy_in,
    a_vast_logs,
    a_vast_copy_out,
    a_vast_destroy_instance,
    a_probe_container_runtime,
    a_list_staged_images,
    a_set_apptainer_env,
    a_apptainer_pull,
    a_verify_sif_arch,
    a_submit_container_job,
)

# ============================================================================
# METHODS (42 functions over 35 task names)
# ----------------------------------------------------------------------------
# Several methods take no arguments and recover the handle they need from the
# state (state.last_job_id, state.last_instance_id, state.doc_hits[0],
# state.offer_hits[0]). This is deliberate: job ids, instance ids, doc ids and
# offer ids are minted by the remote service at execution time, so a method
# expanded before that call cannot know them. GTPyhop expands the todo list
# left to right against the evolving state, so a method placed after the call
# that mints the handle reads it out of the state in its Auxiliary Parameter
# Inference block. Every such method documents which handle it recovers.
# ============================================================================

# ============================================================================
# STAGING AND MONITORING METHODS (Rikyu)
# ============================================================================

def m_stage_inputs(state: State, local_path: str, remote_dir: str,
                   remote_path: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_stage_inputs(state, local_path, remote_dir, remote_path)

    Method parameters:
        local_path: File on the workstation to stage
        remote_dir: Working directory to create when it does not exist
        remote_path: Destination path on the cluster filesystem

    Method purpose:
        Create the working directory when needed, then upload the input file

    Preconditions:
        - Server 2 is ready (state.server_2_ready)
        - The local file exists (state.local_files)

    Task decomposition:
        - a_fs_mkdir: Create the working directory when it is missing
        - a_fs_upload: Send the file and let rsync verify its checksum

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(local_path, str): return False
    if not isinstance(remote_dir, str): return False
    if not isinstance(remote_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not local_path.strip(): return False
    if not remote_dir.strip(): return False
    if not remote_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    if local_path not in getattr(state, 'local_files', {}):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = []
    if remote_dir not in getattr(state, 'remote_dirs', []):
        tasks.append(("a_fs_mkdir", remote_dir))
    tasks.append(("a_fs_upload", local_path, remote_path))
    return tasks
    # END: Task Decomposition


def m_verify_submission(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_verify_submission(state)

    Method parameters:
        None

    Method auxiliary parameters:
        job_id: str (recovered from state.last_job_id, minted by submit_job)

    Method purpose:
        Check the freshly submitted job's status, as the submission skill requires

    Preconditions:
        - A job has been submitted (state.last_job_id)

    Task decomposition:
        - a_poll_job_status: Read the new job's normalised state once

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    job_id = getattr(state, 'last_job_id', None)
    if job_id is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if job_id not in getattr(state, 'jobs', {}):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_poll_job_status", job_id)]
    # END: Task Decomposition


def m_poll_until_terminal_done(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_poll_until_terminal_done(state)

    Method parameters:
        None

    Method auxiliary parameters:
        job_id: str (recovered from state.last_job_id)

    Method purpose:
        Base case of the polling loop: a terminal job needs no further polling

    Preconditions:
        - The job has reached COMPLETED, FAILED or CANCELED (state.jobs)

    Task decomposition:
        - (empty): nothing left to observe

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    job_id = getattr(state, 'last_job_id', None)
    if job_id is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not h_job_is_terminal(state, job_id):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_poll_until_terminal_step(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_poll_until_terminal_step(state)

    Method parameters:
        None

    Method auxiliary parameters:
        job_id: str (recovered from state.last_job_id)

    Method purpose:
        Recursive case of the polling loop: observe one transition, then re-check

    Preconditions:
        - The job exists and is not terminal (state.jobs)
        - The scheduler still has a transition to make (state.job_trajectory)

    Task decomposition:
        - a_poll_job_status: Observe one scheduler transition
        - m_poll_until_terminal: Re-evaluate the loop condition

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    job_id = getattr(state, 'last_job_id', None)
    if job_id is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if job_id not in getattr(state, 'jobs', {}):
        return False
    if h_job_is_terminal(state, job_id):
        return False
    if not state.job_trajectory.get(job_id):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_poll_job_status", job_id),
        ("m_poll_until_terminal",)
    ]
    # END: Task Decomposition


def m_collect_results(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_collect_results(state)

    Method parameters:
        None

    Method auxiliary parameters:
        job_id: str (recovered from state.last_job_id)
        stdout: str (recovered from state.jobs[job_id]['stdout'])
        outputs: List[str] (files the completed job wrote, from state.job_outputs)

    Method purpose:
        Read the job's stdout tail, then download every file it produced

    Preconditions:
        - The job has reached a terminal state (state.jobs)

    Task decomposition:
        - a_fs_tail: Read the last lines of slurm-<job_id>.out
        - a_fs_download: Retrieve each output file to the workstation

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    job_id = getattr(state, 'last_job_id', None)
    if job_id is None or job_id not in getattr(state, 'jobs', {}):
        return False
    stdout = state.jobs[job_id]['stdout']
    job_name = state.jobs[job_id]['name']
    outputs = sorted(getattr(state, 'job_outputs', {}).get(job_name, {}))
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not h_job_is_terminal(state, job_id):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = [("a_fs_tail", stdout, 40)]
    for remote_path in outputs:
        leaf = remote_path.rsplit('/', 1)[-1]
        tasks.append(("a_fs_download", remote_path, f"./{leaf}"))
    return tasks
    # END: Task Decomposition


def m_sweep_until_all_terminal_done(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_sweep_until_all_terminal_done(state)

    Method parameters:
        None

    Method purpose:
        Base case of the batch sweep: every submitted job is terminal

    Preconditions:
        - At least one job was submitted (state.submitted_jobs)
        - No submitted job is still pending (state.jobs)

    Task decomposition:
        - (empty): the batch is finished

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    submitted = getattr(state, 'submitted_jobs', [])
    if not submitted:
        return False
    if any(not h_job_is_terminal(state, j) for j in submitted):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_sweep_until_all_terminal_step(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_sweep_until_all_terminal_step(state)

    Method parameters:
        None

    Method purpose:
        Recursive case of the batch sweep: one get_job_statuses call per round

    Preconditions:
        - At least one submitted job is still pending (state.jobs)

    Task decomposition:
        - a_get_job_statuses: Sweep the user's recent jobs in one call
        - m_sweep_until_all_terminal: Re-evaluate the loop condition

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    submitted = getattr(state, 'submitted_jobs', [])
    if not submitted:
        return False
    if all(h_job_is_terminal(state, j) for j in submitted):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_get_job_statuses", []),
        ("m_sweep_until_all_terminal",)
    ]
    # END: Task Decomposition


# ============================================================================
# SCENARIO-LEVEL METHODS (Rikyu)
# ============================================================================

def m_fire_and_forget_submit(state: State, name: str, gpus: int, duration: str,
                             directory: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_fire_and_forget_submit(state, name, gpus, duration, directory)

    Method parameters:
        name: JobSpec name
        gpus: GPU count to request
        duration: Wall time as a Slurm time string
        directory: Remote working directory

    Method purpose:
        Submit a job and check its status once, without waiting for it

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_get_facility: Learn the accepted GPU counts and wall-time ceiling
        - a_submit_job: Submit the JobSpec
        - m_verify_submission: Check the job status right after submission

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    if not duration.strip(): return False
    if not directory.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("a_get_facility",),
        ("a_submit_job", name, gpus, 0, duration, directory),
        ("m_verify_submission",)
    ]
    # END: Task Decomposition


def m_upload_run_poll_collect(state: State, name: str, gpus: int, ppn: int,
                              duration: str, directory: str, local_input: str,
                              remote_input: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_upload_run_poll_collect(state, name, gpus, ppn, duration, directory,
                                  local_input, remote_input)

    Method parameters:
        name: JobSpec name
        gpus: GPU count to request
        ppn: resources.processes_per_node, the MPI rank count per node
        duration: Wall time as a Slurm time string
        directory: Remote working directory
        local_input: Input file on the workstation
        remote_input: Destination path for the input file

    Method purpose:
        Run the full loop: stage inputs, submit, poll to completion, collect

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_get_facility: Learn the accepted GPU counts and wall-time ceiling
        - m_stage_inputs: Create the working directory and upload the input
        - a_submit_job: Submit the JobSpec
        - m_poll_until_terminal: Follow the job to a terminal state
        - m_collect_results: Tail stdout and download the outputs

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(ppn, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    if not isinstance(local_input, str): return False
    if not isinstance(remote_input, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    if not directory.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("a_get_facility",),
        ("m_stage_inputs", local_input, directory, remote_input),
        ("a_submit_job", name, gpus, ppn, duration, directory),
        ("m_poll_until_terminal",),
        ("m_collect_results",)
    ]
    # END: Task Decomposition


def m_capacity_aware_submit(state: State, name: str, max_gpus: int, duration: str,
                            directory: str, partition: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_capacity_aware_submit(state, name, max_gpus, duration, directory, partition)

    Method parameters:
        name: JobSpec name
        max_gpus: Largest GPU count the workload can use
        duration: Wall time as a Slurm time string
        directory: Remote working directory
        partition: Partition to inspect before choosing a size

    Method purpose:
        Size the request from live partition occupancy instead of guessing

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_get_facility: Learn the accepted GPU counts and GPUs per node
        - a_get_resources: List the partitions sinfo reports
        - a_get_resource: Read idle node count for the target partition
        - m_submit_within_capacity: Pick a supported size that fits and submit

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(max_gpus, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    if not isinstance(partition, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    if max_gpus <= 0: return False
    if not partition.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("a_get_facility",),
        ("a_get_resources",),
        ("a_get_resource", partition),
        ("m_submit_within_capacity", name, max_gpus, duration, directory, partition)
    ]
    # END: Task Decomposition


def m_submit_within_capacity(state: State, name: str, max_gpus: int, duration: str,
                             directory: str, partition: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_submit_within_capacity(state, name, max_gpus, duration, directory, partition)

    Method parameters:
        name: JobSpec name
        max_gpus: Largest GPU count the workload can use
        duration: Wall time as a Slurm time string
        directory: Remote working directory
        partition: Partition whose idle nodes were just read

    Method auxiliary parameters:
        gpus: int (largest supported GPU count that fits the idle capacity)

    Method purpose:
        Choose the biggest accepted GPU count the idle nodes can currently serve

    Preconditions:
        - Facility metadata is known (state.facility_known)
        - The partition's idle count has been read (state.partition_idle)
        - Some supported GPU count fits (state.supported_gpu_counts)

    Task decomposition:
        - a_submit_job: Submit the JobSpec at the chosen size
        - m_verify_submission: Check the job status right after submission

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(max_gpus, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    if not isinstance(partition, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    if max_gpus <= 0: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if not (hasattr(state, 'facility_known') and state.facility_known):
        return False
    idle = getattr(state, 'partition_idle', {}).get(partition)
    if idle is None:
        return False
    # Node allocation scales deterministically from the GPU request
    capacity = idle * state.gpus_per_node
    fits = [g for g in state.supported_gpu_counts if g <= min(max_gpus, capacity)]
    if not fits:
        return False
    gpus = max(fits)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if directory not in getattr(state, 'remote_dirs', []):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_submit_job", name, gpus, 0, duration, directory),
        ("m_verify_submission",)
    ]
    # END: Task Decomposition


def m_walltime_rescue(state: State, name: str, gpus: int, duration: str,
                      directory: str, new_duration: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_walltime_rescue(state, name, gpus, duration, directory, new_duration)

    Method parameters:
        name: JobSpec name
        gpus: GPU count to request
        duration: Initial wall time, deliberately too short
        directory: Remote working directory
        new_duration: Extended wall time to apply while the job runs

    Method purpose:
        Rescue a running job that will time out by raising its limit in place

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_get_facility: Learn the wall-time ceiling
        - a_submit_job: Submit the under-sized JobSpec
        - m_rescue_running_job: Observe, inspect stdout, extend the limit
        - m_poll_until_terminal: Follow the rescued job to completion
        - m_collect_results: Tail stdout and download the outputs

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    if not isinstance(new_duration, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    if not new_duration.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("a_get_facility",),
        ("a_submit_job", name, gpus, 0, duration, directory),
        ("m_rescue_running_job", new_duration),
        ("m_poll_until_terminal",),
        ("m_collect_results",)
    ]
    # END: Task Decomposition


def m_rescue_running_job(state: State, new_duration: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_rescue_running_job(state, new_duration)

    Method parameters:
        new_duration: Extended wall time as a Slurm time string

    Method auxiliary parameters:
        job_id: str (recovered from state.last_job_id)

    Method purpose:
        Wait for the job to start, then inspect it and extend its wall time

    Preconditions:
        - The job exists and is not terminal (state.jobs)

    Task decomposition:
        - a_poll_job_status: Observe the job leaving the queue
        - m_inspect_and_extend: Read stdout, then raise the time limit

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(new_duration, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not new_duration.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    job_id = getattr(state, 'last_job_id', None)
    if job_id is None or job_id not in getattr(state, 'jobs', {}):
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if h_job_is_terminal(state, job_id):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_poll_job_status", job_id),
        ("m_inspect_and_extend", new_duration)
    ]
    # END: Task Decomposition


def m_inspect_and_extend(state: State, new_duration: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_inspect_and_extend(state, new_duration)

    Method parameters:
        new_duration: Extended wall time as a Slurm time string

    Method auxiliary parameters:
        job_id: str (recovered from state.last_job_id)
        stdout: str (recovered from state.jobs[job_id]['stdout'])

    Method purpose:
        Read the running job's stdout, then raise its Slurm time limit

    Preconditions:
        - The job is running, so slurm-<job_id>.out exists (state.jobs)

    Task decomposition:
        - a_fs_tail: Read the progress the job has made so far
        - a_update_job: Raise timeLimit with scontrol update

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(new_duration, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not new_duration.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    job_id = getattr(state, 'last_job_id', None)
    if job_id is None or job_id not in getattr(state, 'jobs', {}):
        return False
    stdout = state.jobs[job_id]['stdout']
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if state.jobs[job_id]['state'] == 'QUEUED':
        return False
    if h_job_is_terminal(state, job_id):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_fs_tail", stdout, 40),
        ("a_update_job", job_id, 'timeLimit', new_duration)
    ]
    # END: Task Decomposition


def m_cancel_and_resubmit(state: State, name: str, wrong_gpus: int, right_gpus: int,
                          duration: str, directory: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_cancel_and_resubmit(state, name, wrong_gpus, right_gpus, duration, directory)

    Method parameters:
        name: JobSpec name
        wrong_gpus: GPU count of the first, mis-sized submission
        right_gpus: GPU count of the corrected submission
        duration: Wall time as a Slurm time string
        directory: Remote working directory

    Method purpose:
        Cancel a mis-sized job and resubmit it at the right size

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_get_facility: Learn the accepted GPU counts
        - a_submit_job: Submit the mis-sized JobSpec
        - m_abort_last_job: Observe it, then cancel it
        - a_submit_job: Resubmit at the corrected size
        - m_poll_until_terminal: Follow the new job to completion
        - m_collect_results: Tail stdout and download the outputs

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(wrong_gpus, int): return False
    if not isinstance(right_gpus, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    if wrong_gpus == right_gpus: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("a_get_facility",),
        ("a_submit_job", name, wrong_gpus, 0, duration, directory),
        ("m_abort_last_job",),
        ("a_submit_job", name, right_gpus, 0, duration, directory),
        ("m_poll_until_terminal",),
        ("m_collect_results",)
    ]
    # END: Task Decomposition


def m_abort_last_job(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_abort_last_job(state)

    Method parameters:
        None

    Method auxiliary parameters:
        job_id: str (recovered from state.last_job_id)

    Method purpose:
        Confirm the job is still live, then cancel it

    Preconditions:
        - The job exists and is not terminal (state.jobs)

    Task decomposition:
        - a_poll_job_status: Confirm the job is still queued or running
        - a_cancel_job: Cancel it with scancel

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    job_id = getattr(state, 'last_job_id', None)
    if job_id is None or job_id not in getattr(state, 'jobs', {}):
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if h_job_is_terminal(state, job_id):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_poll_job_status", job_id),
        ("a_cancel_job", job_id)
    ]
    # END: Task Decomposition


def m_archive_and_retrieve(state: State, source_dir: str, archive_path: str,
                           dest_dir: str, local_path: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_archive_and_retrieve(state, source_dir, archive_path, dest_dir, local_path)

    Method parameters:
        source_dir: Directory whose contents are archived
        archive_path: Destination archive path on the cluster
        dest_dir: Directory the archive is unpacked into on the cluster
        local_path: Destination of the archive on the workstation

    Method purpose:
        Archive, verify, retrieve and unpack results using filesystem tools only

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_fs_ls: Discover what the directory contains
        - m_archive_listing: Compress, checksum, download and extract

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(source_dir, str): return False
    if not isinstance(archive_path, str): return False
    if not isinstance(dest_dir, str): return False
    if not isinstance(local_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not source_dir.strip(): return False
    if not archive_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("a_fs_ls", source_dir),
        ("m_archive_listing", source_dir, archive_path, dest_dir, local_path)
    ]
    # END: Task Decomposition


def m_archive_listing(state: State, source_dir: str, archive_path: str,
                      dest_dir: str, local_path: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_archive_listing(state, source_dir, archive_path, dest_dir, local_path)

    Method parameters:
        source_dir: Directory that was just listed
        archive_path: Destination archive path on the cluster
        dest_dir: Directory the archive is unpacked into on the cluster
        local_path: Destination of the archive on the workstation

    Method auxiliary parameters:
        paths: List[str] (the listing produced by fs_ls, passed to fs_compress)

    Method purpose:
        Archive exactly the files the listing reported, then verify and retrieve

    Preconditions:
        - The directory has been listed and is not empty (state.listings)

    Task decomposition:
        - a_fs_compress: Build the gzip archive from the listed paths
        - a_fs_checksum: Hash the archive before moving it
        - a_fs_download: Retrieve the archive to the workstation
        - a_fs_extract: Unpack it back into a directory on the cluster

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(source_dir, str): return False
    if not isinstance(archive_path, str): return False
    if not isinstance(dest_dir, str): return False
    if not isinstance(local_path, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not archive_path.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    paths = getattr(state, 'listings', {}).get(source_dir)
    if not paths:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if archive_path in getattr(state, 'remote_files', {}):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_fs_compress", list(paths), archive_path),
        ("a_fs_checksum", archive_path),
        ("a_fs_download", archive_path, local_path),
        ("a_fs_extract", archive_path, dest_dir)
    ]
    # END: Task Decomposition


def m_docs_grounded_setup(state: State, query: str, name: str, gpus: int, ppn: int,
                          duration: str, directory: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_docs_grounded_setup(state, query, name, gpus, ppn, duration, directory)

    Method parameters:
        query: Question to put to the bundled guide index
        name: JobSpec name
        gpus: GPU count to request
        ppn: resources.processes_per_node, the MPI rank count per node
        duration: Wall time as a Slurm time string
        directory: Remote working directory

    Method purpose:
        Read the guide before submitting, so the module choice is grounded

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_get_facility: Learn the accepted GPU counts and wall-time ceiling
        - a_list_doc_sections: See what the guide covers
        - a_search_docs: Find the sections answering the question
        - m_read_top_hit_and_submit: Read the best hit, then submit

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(query, str): return False
    if not isinstance(name, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(ppn, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not query.strip(): return False
    if not name.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("a_get_facility",),
        ("a_list_doc_sections",),
        ("a_search_docs", query),
        ("m_read_top_hit_and_submit", name, gpus, ppn, duration, directory)
    ]
    # END: Task Decomposition


def m_read_top_hit_and_submit(state: State, name: str, gpus: int, ppn: int,
                              duration: str, directory: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_read_top_hit_and_submit(state, name, gpus, ppn, duration, directory)

    Method parameters:
        name: JobSpec name
        gpus: GPU count to request
        ppn: resources.processes_per_node, the MPI rank count per node
        duration: Wall time as a Slurm time string
        directory: Remote working directory

    Method auxiliary parameters:
        doc_id: str (recovered from state.doc_hits[0], the best search hit)

    Method purpose:
        Read the section the search returned, then submit the grounded JobSpec

    Preconditions:
        - A documentation search returned at least one hit (state.doc_hits)

    Task decomposition:
        - a_read_doc_section: Read the best-matching guide section in full
        - a_submit_job: Submit the JobSpec the section grounds
        - m_verify_submission: Check the job status right after submission

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(ppn, int): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    hits = getattr(state, 'doc_hits', [])
    if not hits:
        return False
    doc_id = hits[0]
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if directory not in getattr(state, 'remote_dirs', []):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_read_doc_section", doc_id),
        ("a_submit_job", name, gpus, ppn, duration, directory),
        ("m_verify_submission",)
    ]
    # END: Task Decomposition


def m_gpu_count_sweep(state: State, name_prefix: str, gpu_counts: List[int],
                      duration: str, directory: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_gpu_count_sweep(state, name_prefix, gpu_counts, duration, directory)

    Method parameters:
        name_prefix: Prefix for each JobSpec name in the sweep
        gpu_counts: GPU counts to submit, one job each
        duration: Wall time as a Slurm time string
        directory: Remote working directory shared by the sweep

    Method purpose:
        Submit one job per GPU count, then sweep all their statuses together

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_get_facility: Learn the accepted GPU counts
        - a_submit_job: One submission per requested GPU count
        - m_sweep_until_all_terminal: Follow the whole batch with get_job_statuses

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(name_prefix, str): return False
    if not isinstance(gpu_counts, list): return False
    if not all(isinstance(g, int) for g in gpu_counts): return False
    if not isinstance(duration, str): return False
    if not isinstance(directory, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not name_prefix.strip(): return False
    if not gpu_counts: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    tasks = [("a_initialize_servers",), ("a_get_facility",)]
    for gpus in gpu_counts:
        tasks.append(("a_submit_job", f"{name_prefix}-g{gpus}", gpus, 0, duration, directory))
    tasks.append(("m_sweep_until_all_terminal",))
    return tasks
    # END: Task Decomposition


# ============================================================================
# BACKEND ROUTING METHODS
# ----------------------------------------------------------------------------
# m_train_model is the only task in this domain with two competing backends.
# The two dispatch methods have mutually exclusive preconditions, so the choice
# is made once, before any commitment, and holds under every planning strategy
# including the default greedy one.
# ============================================================================

def m_train_model(state: State, model: str, gpus: int, disk_gb: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_train_model(state, model, gpus, disk_gb)

    Method parameters:
        model: Name of the model to train
        gpus: GPU count the training run needs
        disk_gb: Disk to allocate when the run is containerized

    Method purpose:
        Train a model, letting the fetched facility decide which backend can host it

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_servers: Bring the MCP endpoints up
        - a_get_facility: Fetch the facts the routing decision reads
        - m_dispatch_training: Route to the backend that can run this workload

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(disk_gb, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    if gpus <= 0: return False
    if disk_gb <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for a top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_servers",),
        ("a_get_facility",),
        ("m_dispatch_training", model, gpus, disk_gb)
    ]
    # END: Task Decomposition


def m_dispatch_via_rikyu(state: State, model: str, gpus: int, disk_gb: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_dispatch_via_rikyu(state, model, gpus, disk_gb)

    Method parameters:
        model: Name of the model to train
        gpus: GPU count the training run needs
        disk_gb: Ignored on this branch, Rikyu allocates storage by tier

    Method purpose:
        Route a non-containerized workload to Rikyu's module-based job path

    Preconditions:
        - The facility has been queried (state.facility_known)
        - The workload does not need a container (state.workload)

    Task decomposition:
        - m_train_on_rikyu: Run the training as an ordinary module-based job

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(disk_gb, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # The routing decision must be grounded in a fetched fact, not assumed
    if not (hasattr(state, 'facility_known') and state.facility_known):
        return False
    if state.workload.get('container_required'):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("m_train_on_rikyu", model, gpus)]
    # END: Task Decomposition


def m_dispatch_containerized(state: State, model: str, gpus: int, disk_gb: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_dispatch_containerized(state, model, gpus, disk_gb)

    Method parameters:
        model: Name of the model to train
        gpus: GPU count the training run needs
        disk_gb: Static disk allocation, used only if the run is rented out

    Method purpose:
        Probe for a container runtime before choosing where a container can run

    Preconditions:
        - The facility has been queried (state.facility_known)
        - The workload needs a container (state.workload)

    Task decomposition:
        - a_probe_container_runtime: Ask the login node what it actually has
        - m_dispatch_container_backend: Choose a backend from what was found

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(disk_gb, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'facility_known') and state.facility_known):
        return False
    if not state.workload.get('container_required'):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # The probe comes first because nothing else can answer the question: the
    # runtime is absent from the facility metadata, from the bundled guide and
    # from 'module avail'. Only the login node knows.
    return [
        ("a_probe_container_runtime",),
        ("m_dispatch_container_backend", model, gpus, disk_gb)
    ]
    # END: Task Decomposition


def m_container_on_rikyu(state: State, model: str, gpus: int, disk_gb: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_container_on_rikyu(state, model, gpus, disk_gb)

    Method parameters:
        model: Name of the model to train
        gpus: GPU count the training run needs
        disk_gb: Ignored on this branch

    Method purpose:
        Keep a containerized run on Rikyu when Apptainer can actually execute it

    Preconditions:
        - The probe found a runtime (state.container_runtime)
        - The image targets the node architecture (state.workload, state.cluster_arch)

    Task decomposition:
        - m_train_on_rikyu_container: Obtain a SIF and run it under Slurm

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(disk_gb, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not getattr(state, 'container_runtime_known', False):
        return False
    if not state.container_runtime:
        return False
    # An x86_64 image would convert cleanly and then fail at exec, so the
    # architecture decides the backend before anything is built
    if state.workload.get('target_arch') != state.cluster_arch:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("m_train_on_rikyu_container", model, gpus)]
    # END: Task Decomposition


def m_container_on_vastai(state: State, model: str, gpus: int, disk_gb: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_container_on_vastai(state, model, gpus, disk_gb)

    Method parameters:
        model: Name of the model to train
        gpus: GPU count the rented offer must expose
        disk_gb: Static disk allocation for the rented instance

    Method purpose:
        Rent a GPU elsewhere when Rikyu cannot execute this container

    Preconditions:
        - The runtime question has been settled by a probe (state.container_runtime_known)
        - Either no runtime was found, or the image cannot run on these nodes
          (state.container_runtime, state.workload, state.cluster_arch)
        - Server 4 is ready (state.server_4_ready)

    Task decomposition:
        - m_train_on_vastai: Build, publish, rent, train, collect and tear down

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(disk_gb, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not getattr(state, 'container_runtime_known', False):
        return False
    # This is the exact complement of m_container_on_rikyu's condition, so
    # exactly one of the two applies and no strategy has to backtrack
    runnable_here = (bool(state.container_runtime)
                     and state.workload.get('target_arch') == state.cluster_arch)
    if runnable_here:
        return False
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("m_train_on_vastai", model, gpus, disk_gb)]
    # END: Task Decomposition


def m_train_on_rikyu(state: State, model: str, gpus: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_train_on_rikyu(state, model, gpus)

    Method parameters:
        model: Name of the model to train, also used as the JobSpec name
        gpus: GPU count the training run needs

    Method auxiliary parameters:
        workload: Dict (directory, duration, dataset paths, docs query)

    Method purpose:
        Train on Rikyu with Lmod modules, the only mechanism the guide documents

    Preconditions:
        - The facility has been queried (state.facility_known)
        - The workload needs no container (state.workload)

    Task decomposition:
        - m_stage_inputs: Create the working directory and upload the dataset
        - a_list_doc_sections: See what the guide covers
        - a_search_docs: Find the section describing the MPI-capable module
        - m_ground_and_submit_training: Read it, submit, follow, collect

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    workload = getattr(state, 'workload', None)
    if not workload:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'facility_known') and state.facility_known):
        return False
    # This is the module-based path: it loads an Lmod module and runs the code
    # directly on the node. A containerized workload has no decomposition here
    # even though Rikyu can run containers - it belongs to
    # m_train_on_rikyu_container, which obtains a SIF first.
    if workload.get('container_required'):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_stage_inputs", workload['dataset_local'], workload['directory'],
         workload['dataset_remote_rikyu']),
        ("a_list_doc_sections",),
        ("a_search_docs", workload['docs_query']),
        ("m_ground_and_submit_training", model, gpus)
    ]
    # END: Task Decomposition


def m_ground_and_submit_training(state: State, model: str, gpus: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_ground_and_submit_training(state, model, gpus)

    Method parameters:
        model: Name of the model to train, also used as the JobSpec name
        gpus: GPU count the training run needs

    Method auxiliary parameters:
        doc_id: str (recovered from state.doc_hits[0])
        workload: Dict (directory, duration, processes_per_node)

    Method purpose:
        Read the module section, submit the training job and collect its results

    Preconditions:
        - A documentation search returned at least one hit (state.doc_hits)
        - The working directory exists (state.remote_dirs)

    Task decomposition:
        - a_read_doc_section: Read the module section in full
        - a_submit_job: Submit the training JobSpec
        - m_poll_until_terminal: Follow the job to a terminal state
        - m_collect_results: Tail stdout and download the checkpoint

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    hits = getattr(state, 'doc_hits', [])
    if not hits:
        return False
    doc_id = hits[0]
    workload = state.workload
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if workload['directory'] not in getattr(state, 'remote_dirs', []):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_read_doc_section", doc_id),
        ("a_submit_job", model, gpus, workload['processes_per_node'],
         workload['duration'], workload['directory']),
        ("m_poll_until_terminal",),
        ("m_collect_results",)
    ]
    # END: Task Decomposition


# ============================================================================
# RIKYU-NATIVE CONTAINER METHODS (Apptainer)
# ============================================================================

def m_train_on_rikyu_container(state: State, model: str, gpus: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_train_on_rikyu_container(state, model, gpus)

    Method parameters:
        model: Name of the model to train, also used as the JobSpec name
        gpus: GPU count the training run needs

    Method auxiliary parameters:
        workload: Dict (image reference, sif path, dataset paths, binds)

    Method purpose:
        Run a containerized training on Rikyu itself, under Apptainer

    Preconditions:
        - A container runtime was found (state.container_runtime)
        - The image targets the node architecture (state.workload)

    Task decomposition:
        - a_list_staged_images: Look at the site library before pulling anything
        - m_prepare_sif: Reuse a staged image, or import one
        - m_stage_inputs: Create the working directory and upload the dataset
        - m_submit_container_and_collect: Submit, follow, collect

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    workload = getattr(state, 'workload', None)
    if not workload:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not getattr(state, 'container_runtime', None):
        return False
    if workload.get('target_arch') != state.cluster_arch:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # Listing the site library first is not decoration: 35 GiB of ready aarch64
    # NGC images sit under /shared/containers with nothing on the machine
    # pointing at them, and four of the six are larger than the entire home
    # tier a naive pull would land in.
    # Staging comes before the SIF is obtained because an imported SIF is
    # written into the same working directory, which has to exist first.
    return [
        ("a_list_staged_images", workload['image_library']),
        ("m_stage_inputs", workload['dataset_local'], workload['directory'],
         workload['dataset_remote_rikyu']),
        ("m_prepare_sif",),
        ("m_submit_container_and_collect", model, gpus)
    ]
    # END: Task Decomposition


def m_prepare_sif_staged(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_prepare_sif_staged(state)

    Method parameters:
        None

    Method auxiliary parameters:
        sif_path: str (the staged image matching state.workload['sif_path'])

    Method purpose:
        Reuse a site-staged image, which costs no quota and needs no conversion

    Preconditions:
        - The library has been listed (state.staged_images_known)
        - The wanted SIF is one of the staged images (state.staged_images)

    Task decomposition:
        - a_verify_sif_arch: Confirm the node architecture even for a staged image

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    sif_path = state.workload.get('sif_path')
    if sif_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not getattr(state, 'staged_images_known', False):
        return False
    if sif_path not in getattr(state, 'staged_images', {}):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_verify_sif_arch", sif_path)]
    # END: Task Decomposition


def m_prepare_sif_import(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_prepare_sif_import(state)

    Method parameters:
        None

    Method auxiliary parameters:
        workload: Dict (transport, image reference, sif path, cache and tmp dirs)

    Method purpose:
        Import an OCI image and convert it to SIF, unprivileged

    Preconditions:
        - The library has been listed (state.staged_images_known)
        - No staged image matches, so one must be imported (state.staged_images)
        - A container runtime was found (state.container_runtime)

    Task decomposition:
        - a_set_apptainer_env: Redirect the cache and scratch off the home tier
        - a_apptainer_pull: Convert the image to SIF
        - a_verify_sif_arch: Catch an architecture mismatch before submitting

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    workload = getattr(state, 'workload', None)
    if not workload:
        return False
    sif_path = workload.get('sif_path')
    if sif_path is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Only import when the site does not already provide the image: this is the
    # exact complement of m_prepare_sif_staged's condition
    if not getattr(state, 'staged_images_known', False):
        return False
    if sif_path in getattr(state, 'staged_images', {}):
        return False
    if not getattr(state, 'container_runtime', None):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # The architecture check is a separate, explicit step because the pull
    # cannot fail on it: an x86_64 image converts cleanly and only dies at exec.
    return [
        ("a_set_apptainer_env", workload['cachedir'], workload['tmpdir']),
        ("a_apptainer_pull", workload['transport'], workload['image_ref'], sif_path),
        ("a_verify_sif_arch", sif_path)
    ]
    # END: Task Decomposition


def m_submit_container_and_collect(state: State, model: str, gpus: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_submit_container_and_collect(state, model, gpus)

    Method parameters:
        model: Name of the model to train, also used as the JobSpec name
        gpus: GPU count the training run needs

    Method auxiliary parameters:
        workload: Dict (sif path, container command, binds, directory, duration)

    Method purpose:
        Submit the singularity-wrapped job, follow it, and collect its results

    Preconditions:
        - The SIF has been architecture-checked (state.sif_arch_verified)
        - The working directory exists (state.remote_dirs)

    Task decomposition:
        - a_submit_container_job: Ordinary sbatch job wrapping singularity exec
        - m_poll_until_terminal: Follow the job to a terminal state
        - m_collect_results: Tail stdout and download the checkpoint

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    workload = getattr(state, 'workload', None)
    if not workload:
        return False
    sif_path = workload.get('sif_path')
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not getattr(state, 'sif_arch_verified', {}).get(sif_path):
        return False
    if workload['directory'] not in getattr(state, 'remote_dirs', []):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_submit_container_job", model, gpus, workload['duration'],
         workload['directory'], sif_path, workload['container_command'],
         list(workload['binds'])),
        ("m_poll_until_terminal",),
        ("m_collect_results",)
    ]
    # END: Task Decomposition


# ============================================================================
# CONTAINER AND VAST.AI METHODS
# ============================================================================

def m_train_on_vastai(state: State, model: str, gpus: int, disk_gb: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_train_on_vastai(state, model, gpus, disk_gb)

    Method parameters:
        model: Name of the model to train
        gpus: GPU count the rented offer must expose
        disk_gb: Static disk allocation for the instance

    Method auxiliary parameters:
        workload: Dict (image_ref, base_image, target_arch, registry, gpu_name)

    Method purpose:
        Run the containerized training on a rented GPU instead of on Rikyu

    Preconditions:
        - Server 4 is ready (state.server_4_ready)

    Task decomposition:
        - m_build_and_publish_image: Write, build, architecture-check and push
        - a_vast_search_offers: Find rentable offers with enough GPUs
        - m_vast_rent_and_run: Rent the best offer and drive the run to the end

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(model, str): return False
    if not isinstance(gpus, int): return False
    if not isinstance(disk_gb, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not model.strip(): return False
    if gpus <= 0: return False
    if disk_gb <= 0: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    workload = getattr(state, 'workload', None)
    if not workload:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'server_4_ready') and state.server_4_ready):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_build_and_publish_image", workload['image_ref'], workload['base_image'],
         workload['target_arch'], workload['registry']),
        ("a_vast_search_offers", workload['gpu_name'], gpus),
        ("m_vast_rent_and_run", disk_gb)
    ]
    # END: Task Decomposition


def m_build_and_publish_image(state: State, image_ref: str, base_image: str,
                              arch: str, registry: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_build_and_publish_image(state, image_ref, base_image, arch, registry)

    Method parameters:
        image_ref: Tag the image will carry
        base_image: Base image the recipe starts from
        arch: Architecture of the machine that will run the image
        registry: Registry the instance will pull from

    Method purpose:
        Produce a publishable image that cannot be the wrong architecture

    Preconditions:
        - The image has not been published already (state.pushed_images)

    Task decomposition:
        - a_write_dockerfile: Write the recipe for the target architecture
        - a_build_image: Build it locally
        - a_verify_image_arch: Refuse an image the target host cannot execute
        - a_push_image: Publish it so the instance can pull it

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(image_ref, str): return False
    if not isinstance(base_image, str): return False
    if not isinstance(arch, str): return False
    if not isinstance(registry, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not image_ref.strip(): return False
    if arch not in ('aarch64', 'x86_64'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if image_ref in getattr(state, 'pushed_images', []):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_write_dockerfile", image_ref, base_image, arch),
        ("a_build_image", image_ref),
        ("a_verify_image_arch", image_ref, arch),
        ("a_push_image", image_ref, registry)
    ]
    # END: Task Decomposition


def m_vast_rent_and_run(state: State, disk_gb: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_vast_rent_and_run(state, disk_gb)

    Method parameters:
        disk_gb: Static disk allocation for the instance

    Method auxiliary parameters:
        offer_id: str (recovered from state.offer_hits[0], the best search hit)
        workload: Dict (image_ref, onstart_cmd)

    Method purpose:
        Rent the best offer the search returned and wait for the container to be up

    Preconditions:
        - A search returned at least one rentable offer (state.offer_hits)

    Task decomposition:
        - a_vast_create_instance: Rent the offer and launch the image on it
        - m_vast_poll_until_running: Wait for Creating/Loading to reach Running
        - m_vast_train_and_collect: Feed it, follow it, retrieve, tear down

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(disk_gb, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if disk_gb <= 0: return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    hits = getattr(state, 'offer_hits', [])
    if not hits:
        return False
    offer_id = hits[0]
    workload = state.workload
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if workload['image_ref'] not in getattr(state, 'pushed_images', []):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_vast_create_instance", offer_id, workload['image_ref'], disk_gb,
         workload['onstart_cmd']),
        ("m_vast_poll_until_running",),
        ("m_vast_train_and_collect",)
    ]
    # END: Task Decomposition


def m_vast_poll_until_running_done(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_vast_poll_until_running_done(state)

    Method parameters:
        None

    Method auxiliary parameters:
        instance_id: str (recovered from state.last_instance_id)

    Method purpose:
        Base case of the instance loop: the container is up and reachable

    Preconditions:
        - The instance has reached Running (state.instances)

    Task decomposition:
        - (empty): nothing left to wait for

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    instance_id = getattr(state, 'last_instance_id', None)
    if instance_id is None or instance_id not in getattr(state, 'instances', {}):
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if state.instances[instance_id]['state'] != VAST_READY_STATE:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_vast_poll_until_running_step(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_vast_poll_until_running_step(state)

    Method parameters:
        None

    Method auxiliary parameters:
        instance_id: str (recovered from state.last_instance_id)

    Method purpose:
        Recursive case of the instance loop: observe one control-plane transition

    Preconditions:
        - The instance is not yet Running (state.instances)
        - The control plane still has a transition (state.instance_trajectory)

    Task decomposition:
        - a_vast_poll_instance: Observe Creating -> Loading -> Connecting -> Running
        - m_vast_poll_until_running: Re-evaluate the loop condition

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    instance_id = getattr(state, 'last_instance_id', None)
    if instance_id is None or instance_id not in getattr(state, 'instances', {}):
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if state.instances[instance_id]['state'] == VAST_READY_STATE:
        return False
    if not state.instance_trajectory.get(instance_id):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_vast_poll_instance", instance_id),
        ("m_vast_poll_until_running",)
    ]
    # END: Task Decomposition


def m_vast_train_and_collect(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_vast_train_and_collect(state)

    Method parameters:
        None

    Method auxiliary parameters:
        instance_id: str (recovered from state.last_instance_id)
        workload: Dict (dataset and checkpoint paths)

    Method purpose:
        Feed the running container, follow the run, then retrieve and tear down

    Preconditions:
        - The instance is Running (state.instances)

    Task decomposition:
        - a_vast_copy_in: Copy the dataset into the instance
        - m_vast_follow_training: Read the logs until the run reports done
        - m_vast_retrieve_and_teardown: Copy the checkpoint out, then destroy

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    instance_id = getattr(state, 'last_instance_id', None)
    if instance_id is None or instance_id not in getattr(state, 'instances', {}):
        return False
    workload = state.workload
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if state.instances[instance_id]['state'] != VAST_READY_STATE:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_vast_copy_in", workload['dataset_local'], instance_id,
         workload['dataset_remote']),
        ("m_vast_follow_training",),
        ("m_vast_retrieve_and_teardown",)
    ]
    # END: Task Decomposition


def m_vast_follow_training_done(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_vast_follow_training_done(state)

    Method parameters:
        None

    Method auxiliary parameters:
        instance_id: str (recovered from state.last_instance_id)

    Method purpose:
        Base case of the training loop: the container logs report the run is done

    Preconditions:
        - Training has finished (state.training_state)

    Task decomposition:
        - (empty): nothing left to follow

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    instance_id = getattr(state, 'last_instance_id', None)
    if instance_id is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if getattr(state, 'training_state', {}).get(instance_id) != 'done':
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return []
    # END: Task Decomposition


def m_vast_follow_training_step(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_vast_follow_training_step(state)

    Method parameters:
        None

    Method auxiliary parameters:
        instance_id: str (recovered from state.last_instance_id)

    Method purpose:
        Recursive case of the training loop: read one more round of logs

    Preconditions:
        - Training has not finished (state.training_state)
        - The run still has a step to report (state.training_trajectory)

    Task decomposition:
        - a_vast_logs: Read the container logs
        - m_vast_follow_training: Re-evaluate the loop condition

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    instance_id = getattr(state, 'last_instance_id', None)
    if instance_id is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if getattr(state, 'training_state', {}).get(instance_id) == 'done':
        return False
    if not getattr(state, 'training_trajectory', {}).get(instance_id):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_vast_logs", instance_id),
        ("m_vast_follow_training",)
    ]
    # END: Task Decomposition


def m_vast_retrieve_and_teardown(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_vast_retrieve_and_teardown(state)

    Method parameters:
        None

    Method auxiliary parameters:
        instance_id: str (recovered from state.last_instance_id)
        workload: Dict (checkpoint_remote, checkpoint_local)

    Method purpose:
        Copy the checkpoint out first, and only then destroy the instance

    Preconditions:
        - Training has finished (state.training_state)
        - The checkpoint exists inside the instance (state.instance_files)

    Task decomposition:
        - a_vast_copy_out: Retrieve the checkpoint to the workstation
        - a_vast_destroy_instance: Destroy the instance and stop billing

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    instance_id = getattr(state, 'last_instance_id', None)
    if instance_id is None or instance_id not in getattr(state, 'instances', {}):
        return False
    workload = state.workload
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if getattr(state, 'training_state', {}).get(instance_id) != 'done':
        return False
    if workload['checkpoint_remote'] not in state.instance_files.get(instance_id, {}):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_vast_copy_out", instance_id, workload['checkpoint_remote'],
         workload['checkpoint_local']),
        ("a_vast_destroy_instance", instance_id)
    ]
    # END: Task Decomposition


def m_vast_teardown(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_vast_teardown(state)

    Method parameters:
        None

    Method auxiliary parameters:
        instance_id: str (recovered from state.last_instance_id)

    Method purpose:
        Destroy the current instance, whatever else has or has not happened

    Preconditions:
        - An instance exists (state.last_instance_id)

    Task decomposition:
        - a_vast_destroy_instance: Destroy it, if its own precondition allows

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No parameters to validate
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    instance_id = getattr(state, 'last_instance_id', None)
    if instance_id is None or instance_id not in getattr(state, 'instances', {}):
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Deliberately none: this method exists so that a scenario can ask for a
    # teardown in isolation. Whether the teardown is safe is decided by
    # a_vast_destroy_instance's own precondition, never by this method.
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_vast_destroy_instance", instance_id)]
    # END: Task Decomposition


# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Staging and monitoring (Rikyu)
declare_task_methods('m_stage_inputs', m_stage_inputs)
declare_task_methods('m_verify_submission', m_verify_submission)
declare_task_methods('m_poll_until_terminal',
                     m_poll_until_terminal_done, m_poll_until_terminal_step)
declare_task_methods('m_collect_results', m_collect_results)
declare_task_methods('m_sweep_until_all_terminal',
                     m_sweep_until_all_terminal_done, m_sweep_until_all_terminal_step)

# Scenario-level entry points (Rikyu)
declare_task_methods('m_fire_and_forget_submit', m_fire_and_forget_submit)
declare_task_methods('m_upload_run_poll_collect', m_upload_run_poll_collect)
declare_task_methods('m_capacity_aware_submit', m_capacity_aware_submit)
declare_task_methods('m_submit_within_capacity', m_submit_within_capacity)
declare_task_methods('m_walltime_rescue', m_walltime_rescue)
declare_task_methods('m_rescue_running_job', m_rescue_running_job)
declare_task_methods('m_inspect_and_extend', m_inspect_and_extend)
declare_task_methods('m_cancel_and_resubmit', m_cancel_and_resubmit)
declare_task_methods('m_abort_last_job', m_abort_last_job)
declare_task_methods('m_archive_and_retrieve', m_archive_and_retrieve)
declare_task_methods('m_archive_listing', m_archive_listing)
declare_task_methods('m_docs_grounded_setup', m_docs_grounded_setup)
declare_task_methods('m_read_top_hit_and_submit', m_read_top_hit_and_submit)
declare_task_methods('m_gpu_count_sweep', m_gpu_count_sweep)

# Backend routing: the order matters only for readability, the two dispatch
# methods have mutually exclusive preconditions
declare_task_methods('m_train_model', m_train_model)
declare_task_methods('m_dispatch_training', m_dispatch_via_rikyu, m_dispatch_containerized)
declare_task_methods('m_dispatch_container_backend',
                     m_container_on_rikyu, m_container_on_vastai)
declare_task_methods('m_train_on_rikyu', m_train_on_rikyu)
declare_task_methods('m_ground_and_submit_training', m_ground_and_submit_training)

# Rikyu-native containers (Apptainer)
declare_task_methods('m_train_on_rikyu_container', m_train_on_rikyu_container)
declare_task_methods('m_prepare_sif', m_prepare_sif_staged, m_prepare_sif_import)
declare_task_methods('m_submit_container_and_collect', m_submit_container_and_collect)

# Container and vast.ai
declare_task_methods('m_train_on_vastai', m_train_on_vastai)
declare_task_methods('m_build_and_publish_image', m_build_and_publish_image)
declare_task_methods('m_vast_rent_and_run', m_vast_rent_and_run)
declare_task_methods('m_vast_poll_until_running',
                     m_vast_poll_until_running_done, m_vast_poll_until_running_step)
declare_task_methods('m_vast_train_and_collect', m_vast_train_and_collect)
declare_task_methods('m_vast_follow_training',
                     m_vast_follow_training_done, m_vast_follow_training_step)
declare_task_methods('m_vast_retrieve_and_teardown', m_vast_retrieve_and_teardown)
declare_task_methods('m_vast_teardown', m_vast_teardown)

# ============================================================================
# END OF FILE
# ============================================================================
