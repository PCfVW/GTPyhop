"""
Problem definitions for the Rikyu HPC / vast.ai containerized training example.
-- Generated 2026-08-04

This file defines initial states for HPC workflows orchestrated across four
MCP endpoints:
  - Server 1 (mcp-python-ingestion): HTN planning with GTPyhop
  - Server 2 (rikyu-hpc):  Slurm, filesystem and login node (hpc_server.py)
  - Server 3 (rikyu-docs): documentation search (docs_server.py)
  - Server 4 (vastai):     rented GPU instances (vast.ai CLI / SDK / REST)

Every constant below is taken from the Rikyu-Agent repository:
server/rikyu_mcp/data/rikyu_config.json for the facility numbers,
server/rikyu_mcp/data/rikyu_guide.md and the plugins/rikyu skills for the
operating rules. See README.md for the provenance table and for the three
assumptions this example adds on top of them.

Scenarios (see get_problems):
  - scenario_1_fire_and_forget:          submit and check once
  - scenario_2_upload_run_poll_collect:  the full stage/run/poll/collect loop
  - scenario_3_capacity_aware_submit:    size the request from idle nodes
  - scenario_4_walltime_rescue:          extend a running job's time limit
  - scenario_5_cancel_and_resubmit:      cancel a mis-sized job and redo it
  - scenario_6_archive_and_retrieve:     filesystem only, no scheduler at all
  - scenario_7_docs_grounded_setup:      read the guide before submitting
  - scenario_8_gpu_count_sweep:          one job per GPU count, swept together
  - scenario_9_containerized_training:   x86_64 image, routed to vast.ai
  - scenario_10_backend_routing:         same task, no container, Rikyu modules
  - scenario_11_apptainer_training:      same task, aarch64 image, Rikyu/Apptainer

Scenarios 9, 10 and 11 carry identical goal tasks. What routes them apart is
two facts the plan has to go and fetch: whether the workload needs a container,
and whether its image matches the aarch64 node architecture.

Traps (see get_trap_problems): sixteen states that must NOT produce a plan.
They are deliberately kept out of get_problems() so that the benchmarking
script reports eleven successes rather than eleven successes and sixteen
failures.
"""

import sys
import os
from typing import Dict, Tuple, List

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    # Graceful degradation: supports direct problems.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State


# ============================================================================
# FACILITY CONSTANTS
# ----------------------------------------------------------------------------
# Verbatim from server/rikyu_mcp/data/rikyu_config.json. Note what is NOT
# here: nothing about containers. The facility metadata says nothing on the
# subject, which is exactly why a_probe_container_runtime has to ask the login
# node instead of reading a flag.
# ============================================================================

FACILITY = {
    'supported_gpu_counts': [1, 2, 3, 4, 8, 12, 16],
    'gpus_per_node': 4,
    'max_wall_time': '96:00:00',
    'cluster_arch': 'aarch64',
}

PARTITIONS = {
    # 400 GB200 NVL4 nodes, max_wall_time 4-00:00:00, as sinfo would report them
    'gpu': {'nodes': 400, 'allocated': 360, 'idle': 38, 'other': 2},
}

STORAGE_TIERS = {
    '/home': {'quota_gb': 5.0, 'used_gb': 0.4},        # Lustre SSD, personal config only
    '/data1': {'quota_gb': 1024.0, 'used_gb': 120.0},  # Lustre HDD, 1 TB per group
    '/tmp': {'quota_gb': 1536.0, 'used_gb': 0.0},      # node-local NVMe, 1.5 TB per GPU
}

DOC_CATALOG = {
    'guide#modules': {
        'section': 'Compilers, MPI and modules',
        'query': 'mpi module',
        'facts': {'mpi_module': 'nvhpc-hpcx', 'launcher': 'mpirun'},
    },
    'guide#gpus': {
        'section': 'Requesting GPUs',
        'query': 'gpu count',
        'facts': {'gpu_flag': '--gpus=N'},
    },
    'guide#storage': {
        'section': 'Storage tiers',
        'query': 'storage quota',
        'facts': {'group_dir': '/data1'},
    },
    'guide#spack': {
        'section': 'Spack applications',
        'query': 'spack package',
        'facts': {'spack_setup': '. /shared/software/spack-1.2.0/share/spack/setup-env.sh'},
    },
}

GROUP_DIR = '/data1/spread'
HOME_DIR = '/home/rikyu-user'

# ============================================================================
# CONTAINER CONSTANTS
# ----------------------------------------------------------------------------
# From the 2026-08-05 Rikyu containerization findings (v1). Rikyu does run
# containers: Apptainer 1.4.5 unprivileged, behind a 'singularity' compat
# symlink. None of it is advertised - it is absent from rikyu_config.json, from
# rikyu_guide.md and from 'module avail', reaching PATH only through
# /etc/profile.d/apptainer-path.sh - so a plan has to probe for it.
# ============================================================================

APPTAINER = {
    'name': 'apptainer',
    'version': '1.4.5-3.el8',
    'exposed_as': 'singularity',
    'path': '/shared/software/apptainer/bin/singularity',
    'suid_install': False,          # APPTAINER_SUID_INSTALL=0, unprivileged
    'gpu_flag': '--nv',             # --nvccli unavailable: no nvidia-container-cli
    'scheduler_integrated': False,  # no Pyxis, no /etc/slurm/oci.conf
}

# 'command -v' on the login node: Apptainer only. Docker, Podman, Enroot,
# Buildah, nerdctl, skopeo and umoci are all absent.
LOGIN_BINARIES = {'singularity': APPTAINER}

# Bound into every container by default. Group storage and the shared trees
# are not, which is the operational trap of this whole branch.
AUTO_BIND_PATHS = [HOME_DIR, '/tmp']

# The site image library: 35.24 GiB of ready aarch64 NGC images that nothing
# on the machine points at. Four of the six are larger than the entire 5 GiB
# home tier a naive 'apptainer pull' would land in.
IMAGE_LIBRARY = '/shared/containers/nvcr.io/nvidia'

SITE_IMAGES = {
    f'{IMAGE_LIBRARY}/pytorch:26.04-py3.sif':
        {'arch': 'aarch64', 'size_gb': 9.61},
    f'{IMAGE_LIBRARY}/nvhpc:26.3-devel-cuda_multi-ubuntu24.04.sif':
        {'arch': 'aarch64', 'size_gb': 13.58},
    f'{IMAGE_LIBRARY}/nvhpc:26.3-devel-cuda13.1-ubuntu24.04.sif':
        {'arch': 'aarch64', 'size_gb': 5.98},
    f'{IMAGE_LIBRARY}/nvhpc:26.3-runtime-cuda13.1-ubuntu24.04.sif':
        {'arch': 'aarch64', 'size_gb': 2.63},
    f'{IMAGE_LIBRARY}/cuda:13.1.2-devel-ubuntu24.04.sif':
        {'arch': 'aarch64', 'size_gb': 3.29},
    f'{IMAGE_LIBRARY}/cuda:13.1.2-base-ubuntu24.04.sif':
        {'arch': 'aarch64', 'size_gb': 0.16},
}


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def h_create_base_state(name: str) -> State:
    """
    Create a base state carrying the facility ground truth and empty containers.

    Every scenario starts from this and adds only what it needs, so that the
    difference between two scenarios is exactly the thing under test.
    """
    state = State(name)

    # Ground truth the tools read but never invent
    state.facility = dict(FACILITY)
    state.partitions = {k: dict(v) for k, v in PARTITIONS.items()}
    state.storage_tiers = {k: dict(v) for k, v in STORAGE_TIERS.items()}
    state.doc_catalog = {k: dict(v) for k, v in DOC_CATALOG.items()}

    # Scheduler
    state.next_job_id = 1000
    state.jobs = {}
    state.job_trajectory = {}
    state.job_script = {}
    state.job_outputs = {}
    state.job_artifact = {}
    state.job_launcher = {}
    state.artifact_arch = {}
    state.poll_count = {}
    state.submitted_jobs = []

    # Filesystem
    state.remote_dirs = [HOME_DIR, GROUP_DIR]
    state.remote_files = {}
    state.local_files = {}
    state.listings = {}
    state.checksums = {}
    state.file_owner_job = {}

    # Login node
    state.command_weight = {}
    state.login_binaries = dict(LOGIN_BINARIES)

    # Apptainer on Rikyu: present but unadvertised, so unknown until probed
    state.container_runtime = None
    state.container_runtime_known = False
    state.apptainer_env = {}
    state.apptainer_env_set = False
    state.site_images = {k: dict(v) for k, v in SITE_IMAGES.items()}
    state.staged_images = {}
    state.staged_images_known = False
    state.sif_images = {}
    state.sif_arch_verified = {}
    state.oci_images = {}
    state.container_needs = {}
    state.auto_bind_paths = list(AUTO_BIND_PATHS)

    # Container images (local build, for the rented-GPU branch)
    state.dockerfiles = {}
    state.images = {}
    state.image_arch_verified = {}
    state.pushed_images = []

    # vast.ai
    state.vast_offers = {}
    state.instances = {}
    state.instance_trajectory = {}
    state.instance_script = {}
    state.training_trajectory = {}
    state.training_script = {}
    state.training_state = {}
    state.instance_files = {}
    state.results_copied_out = {}
    state.next_instance_id = 1

    # Workload description consumed by the routing methods
    state.workload = {}

    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: rikyu_hpc

# BEGIN: Scenario: scenario_1_fire_and_forget
# Configuration
_name, _gpus, _duration = 'bench-warmup', 4, '01:00:00'
_directory = f'{GROUP_DIR}/work'

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_fire_and_forget')
initial_state_scenario_1.remote_dirs.append(_directory)
initial_state_scenario_1.job_script[_name] = ['ACTIVE', 'COMPLETED']

# Problem
problems['scenario_1_fire_and_forget'] = (
    initial_state_scenario_1,
    [('m_fire_and_forget_submit', _name, _gpus, _duration, _directory)],
    f'Fire-and-forget: submit {_gpus} GPUs for {_duration}, check once -> 4 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_upload_run_poll_collect
# Configuration
_name, _gpus, _ppn, _duration = 'clt-train', 2, 2, '12:00:00'
_directory = f'{GROUP_DIR}/clt'
_local_input, _remote_input = './dataset.tar', f'{GROUP_DIR}/clt/dataset.tar'

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_upload_run_poll_collect')
initial_state_scenario_2.local_files[_local_input] = 12.0
initial_state_scenario_2.job_launcher[_name] = 'mpirun'
initial_state_scenario_2.job_script[_name] = ['ACTIVE', 'ACTIVE', 'COMPLETED']
initial_state_scenario_2.job_outputs[_name] = {f'{_directory}/checkpoint.pt': 3.5}

# Problem
problems['scenario_2_upload_run_poll_collect'] = (
    initial_state_scenario_2,
    [('m_upload_run_poll_collect', _name, _gpus, _ppn, _duration, _directory,
      _local_input, _remote_input)],
    f'Upload/run/poll/collect: {_gpus} GPUs, {_ppn} ranks per node -> 10 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_capacity_aware_submit
# Configuration
_name, _max_gpus, _duration = 'capacity-probe', 16, '04:00:00'
_directory, _partition = f'{GROUP_DIR}/work', 'gpu'

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_capacity_aware_submit')
initial_state_scenario_3.remote_dirs.append(_directory)
initial_state_scenario_3.job_script[f'{_name}'] = ['ACTIVE', 'COMPLETED']

# Problem
problems['scenario_3_capacity_aware_submit'] = (
    initial_state_scenario_3,
    [('m_capacity_aware_submit', _name, _max_gpus, _duration, _directory, _partition)],
    f'Capacity-aware: 38 idle nodes x 4 GPUs, cap {_max_gpus} -> 6 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_4_walltime_rescue
# Configuration
_name, _gpus = 'md-production', 8
_duration, _new_duration = '02:00:00', '24:00:00'
_directory = f'{GROUP_DIR}/md'

# State
initial_state_scenario_4 = h_create_base_state('scenario_4_walltime_rescue')
initial_state_scenario_4.remote_dirs.append(_directory)
initial_state_scenario_4.job_script[_name] = ['ACTIVE', 'ACTIVE', 'COMPLETED']
initial_state_scenario_4.job_outputs[_name] = {f'{_directory}/trajectory.nc': 8.0}

# Problem
problems['scenario_4_walltime_rescue'] = (
    initial_state_scenario_4,
    [('m_walltime_rescue', _name, _gpus, _duration, _directory, _new_duration)],
    f'Wall-time rescue: raise timeLimit {_duration} -> {_new_duration} -> 10 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_5_cancel_and_resubmit
# Configuration
_name, _wrong_gpus, _right_gpus, _duration = 'qe-relax', 1, 4, '08:00:00'
_directory = f'{GROUP_DIR}/qe'

# State
initial_state_scenario_5 = h_create_base_state('scenario_5_cancel_and_resubmit')
initial_state_scenario_5.remote_dirs.append(_directory)
initial_state_scenario_5.job_script[_name] = ['ACTIVE', 'COMPLETED']
initial_state_scenario_5.job_outputs[_name] = {f'{_directory}/relax.out': 0.2}

# Problem
problems['scenario_5_cancel_and_resubmit'] = (
    initial_state_scenario_5,
    [('m_cancel_and_resubmit', _name, _wrong_gpus, _right_gpus, _duration, _directory)],
    f'Cancel and resubmit: {_wrong_gpus} GPU -> {_right_gpus} GPUs -> 10 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_6_archive_and_retrieve
# Configuration
_source_dir = f'{GROUP_DIR}/results'
_archive_path = f'{GROUP_DIR}/results-2026-08.tar.gz'
_dest_dir, _local_path = f'{GROUP_DIR}/restored', './results-2026-08.tar.gz'

# State
initial_state_scenario_6 = h_create_base_state('scenario_6_archive_and_retrieve')
initial_state_scenario_6.remote_dirs.append(_source_dir)
initial_state_scenario_6.remote_files[f'{_source_dir}/run-a.log'] = 0.1
initial_state_scenario_6.remote_files[f'{_source_dir}/run-b.log'] = 0.1
initial_state_scenario_6.remote_files[f'{_source_dir}/summary.csv'] = 0.05

# Problem
problems['scenario_6_archive_and_retrieve'] = (
    initial_state_scenario_6,
    [('m_archive_and_retrieve', _source_dir, _archive_path, _dest_dir, _local_path)],
    'Archive and retrieve: filesystem only, no job id anywhere -> 6 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_7_docs_grounded_setup
# Configuration
_query, _name, _gpus, _ppn = 'mpi module', 'gromacs-run', 8, 4
_duration, _directory = '06:00:00', f'{GROUP_DIR}/gromacs'

# State
initial_state_scenario_7 = h_create_base_state('scenario_7_docs_grounded_setup')
initial_state_scenario_7.remote_dirs.append(_directory)
initial_state_scenario_7.job_launcher[_name] = 'mpirun'
initial_state_scenario_7.job_script[_name] = ['ACTIVE', 'COMPLETED']

# Problem
problems['scenario_7_docs_grounded_setup'] = (
    initial_state_scenario_7,
    [('m_docs_grounded_setup', _query, _name, _gpus, _ppn, _duration, _directory)],
    f'Docs-grounded setup: search "{_query}" before submitting -> 7 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_8_gpu_count_sweep
# Configuration
_prefix, _gpu_counts, _duration = 'scaling', [1, 4, 16], '00:30:00'
_directory = f'{GROUP_DIR}/scaling'

# State
initial_state_scenario_8 = h_create_base_state('scenario_8_gpu_count_sweep')
initial_state_scenario_8.remote_dirs.append(_directory)

# Problem
problems['scenario_8_gpu_count_sweep'] = (
    initial_state_scenario_8,
    [('m_gpu_count_sweep', _prefix, _gpu_counts, _duration, _directory)],
    f'GPU-count sweep: one job per count in {_gpu_counts} -> 7 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_9_containerized_training
# Configuration
_model, _gpus, _disk_gb = 'clt-7b', 4, 200

# State
initial_state_scenario_9 = h_create_base_state('scenario_9_containerized_training')
initial_state_scenario_9.local_files['./corpus.tar'] = 40.0
initial_state_scenario_9.vast_offers = {
    'offer-8842': {'gpu_name': 'H100_SXM', 'num_gpus': 4, 'arch': 'x86_64',
                   'dph': 6.4, 'max_disk_gb': 512},
    'offer-9137': {'gpu_name': 'H100_SXM', 'num_gpus': 8, 'arch': 'x86_64',
                   'dph': 12.1, 'max_disk_gb': 1024},
}
initial_state_scenario_9.instance_script['clt-7b'] = ['Loading', 'Connecting', 'Running']
initial_state_scenario_9.training_script['clt-7b'] = ['epoch-1', 'epoch-2', 'done']
initial_state_scenario_9.workload = {
    'label': 'clt-7b',
    'container_required': True,
    'image_ref': 'registry.example.org/clt-7b:cu124',
    'base_image': 'nvidia/cuda:12.4.0-devel-ubuntu22.04',
    'target_arch': 'x86_64',
    'image_size_gb': 14.0,
    'registry': 'registry.example.org',
    'gpu_name': 'H100_SXM',
    'onstart_cmd': 'python -m clt.train --data /workspace/corpus.tar',
    'required_disk_gb': 120,
    'dataset_local': './corpus.tar',
    'dataset_remote': '/workspace/corpus.tar',
    'checkpoint_remote': '/workspace/out/clt-7b.pt',
    'checkpoint_local': './clt-7b.pt',
    'checkpoint_gb': 26.0,
}

# Problem
problems['scenario_9_containerized_training'] = (
    initial_state_scenario_9,
    [('m_train_model', _model, _gpus, _disk_gb)],
    f'Containerized training: {_model} needs a container and ships an x86_64 '
    f'image the Grace nodes cannot execute, so the plan probes, then routes to '
    f'a rented {_gpus}-GPU instance -> 18 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_10_backend_routing
# Configuration
_model, _gpus, _disk_gb = 'clt-7b', 4, 200

# State
# Byte-for-byte the same goal task as scenario 9. The only difference is
# container_required, and that single flag moves the whole plan to Rikyu.
initial_state_scenario_10 = h_create_base_state('scenario_10_backend_routing')
initial_state_scenario_10.local_files['./corpus.tar'] = 40.0
initial_state_scenario_10.job_launcher[_model] = 'mpirun'
initial_state_scenario_10.job_script[_model] = ['ACTIVE', 'COMPLETED']
initial_state_scenario_10.job_outputs[_model] = {f'{GROUP_DIR}/clt-7b/clt-7b.pt': 26.0}
initial_state_scenario_10.workload = {
    'label': 'clt-7b',
    'container_required': False,
    'directory': f'{GROUP_DIR}/clt-7b',
    'duration': '48:00:00',
    'processes_per_node': 4,
    'docs_query': 'mpi module',
    'dataset_local': './corpus.tar',
    'dataset_remote_rikyu': f'{GROUP_DIR}/clt-7b/corpus.tar',
}

# Problem
problems['scenario_10_backend_routing'] = (
    initial_state_scenario_10,
    [('m_train_model', _model, _gpus, _disk_gb)],
    f'Backend routing: same task as scenario 9, but {_model} needs no '
    f'container, so the plan stays on Rikyu -> 12 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_11_apptainer_training
# Configuration
_model, _gpus, _disk_gb = 'clt-7b', 4, 200
_directory = f'{GROUP_DIR}/clt-7b'
_image_ref = 'ghcr.io/rikyu-user/clt-7b:arm64'
_sif_path = f'{_directory}/clt-7b.sif'

# State
# Same goal task again. This workload needs a container like scenario 9, but
# its image is built for aarch64, so Rikyu's own Apptainer can execute it and
# nothing has to be rented.
initial_state_scenario_11 = h_create_base_state('scenario_11_apptainer_training')
initial_state_scenario_11.local_files['./corpus.tar'] = 40.0
initial_state_scenario_11.oci_images[_image_ref] = {'arch': 'aarch64', 'size_gb': 11.0}
initial_state_scenario_11.job_script[_model] = ['ACTIVE', 'COMPLETED']
initial_state_scenario_11.job_outputs[_model] = {f'{_directory}/clt-7b.pt': 26.0}
initial_state_scenario_11.container_needs[_model] = [
    f'{_directory}/corpus.tar',
    _directory,
]
initial_state_scenario_11.workload = {
    'label': _model,
    'container_required': True,
    'target_arch': 'aarch64',
    'image_library': IMAGE_LIBRARY,
    'transport': 'docker',
    'image_ref': _image_ref,
    'sif_path': _sif_path,
    'cachedir': f'{GROUP_DIR}/.apptainer/cache',
    'tmpdir': '/tmp',
    'directory': _directory,
    'duration': '48:00:00',
    'container_command': 'python -m clt.train --data /data/corpus.tar',
    'binds': [GROUP_DIR],
    'dataset_local': './corpus.tar',
    'dataset_remote_rikyu': f'{_directory}/corpus.tar',
}

# Problem
problems['scenario_11_apptainer_training'] = (
    initial_state_scenario_11,
    [('m_train_model', _model, _gpus, _disk_gb)],
    f'Apptainer on Rikyu: same task as scenarios 9 and 10, but {_model} ships '
    f'an aarch64 image, so the probe finds singularity and the run stays on '
    f'Rikyu -> 14 actions'
)
# END: Scenario

# END: Domain


# ============================================================================
# TRAPS
# ----------------------------------------------------------------------------
# Eleven states that must NOT produce a plan. Each one isolates a single
# precondition, so a failure is attributable to that rule and nothing else.
# They are returned by get_trap_problems(), not by get_problems().
# ============================================================================

traps = {}

# BEGIN: Domain: rikyu_hpc_traps

# BEGIN: Scenario: trap_1_unsupported_gpu_count
# Configuration
_gpus = 5

# State
trap_state_1 = h_create_base_state('trap_1_unsupported_gpu_count')
trap_state_1.remote_dirs.append(f'{GROUP_DIR}/work')

# Problem
traps['trap_1_unsupported_gpu_count'] = (
    trap_state_1,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_submit_job', 'bad-size', _gpus, 0, '01:00:00', f'{GROUP_DIR}/work')],
    f'{_gpus} GPUs is not in the supported set 1, 2, 3, 4, 8, 12, 16'
)
# END: Scenario

# BEGIN: Scenario: trap_2_cancel_finished_job
# State
trap_state_2 = h_create_base_state('trap_2_cancel_finished_job')
trap_state_2.jobs['1001'] = {
    'name': 'already-done', 'gpus': 4, 'processes_per_node': 0,
    'duration': '01:00:00', 'duration_hours': 1.0, 'directory': f'{GROUP_DIR}/work',
    'stdout': f'{GROUP_DIR}/work/slurm-1001.out', 'state': 'COMPLETED',
}
trap_state_2.job_trajectory['1001'] = []
trap_state_2.submitted_jobs.append('1001')

# Problem
traps['trap_2_cancel_finished_job'] = (
    trap_state_2,
    [('a_initialize_servers',), ('a_cancel_job', '1001')],
    'scancel only affects queued or running jobs, never a COMPLETED one'
)
# END: Scenario

# BEGIN: Scenario: trap_3_download_before_terminal
# Configuration
_checkpoint = f'{GROUP_DIR}/work/checkpoint.pt'

# State
trap_state_3 = h_create_base_state('trap_3_download_before_terminal')
trap_state_3.jobs['1002'] = {
    'name': 'still-running', 'gpus': 4, 'processes_per_node': 0,
    'duration': '12:00:00', 'duration_hours': 12.0, 'directory': f'{GROUP_DIR}/work',
    'stdout': f'{GROUP_DIR}/work/slurm-1002.out', 'state': 'ACTIVE',
}
trap_state_3.job_trajectory['1002'] = ['COMPLETED']
trap_state_3.submitted_jobs.append('1002')
trap_state_3.remote_files[_checkpoint] = 3.5
trap_state_3.file_owner_job[_checkpoint] = '1002'

# Problem
traps['trap_3_download_before_terminal'] = (
    trap_state_3,
    [('a_initialize_servers',), ('a_fs_download', _checkpoint, './checkpoint.pt')],
    'a file still being written by an ACTIVE job must not be collected'
)
# END: Scenario

# BEGIN: Scenario: trap_4_heavy_compute_on_login_node
# Configuration
_command = 'python train.py --epochs 40'

# State
trap_state_4 = h_create_base_state('trap_4_heavy_compute_on_login_node')
trap_state_4.command_weight[_command] = 'heavy'

# Problem
traps['trap_4_heavy_compute_on_login_node'] = (
    trap_state_4,
    [('a_initialize_servers',), ('a_run_command_on_cluster', _command)],
    'the login node is not for computation: heavy work belongs in a job'
)
# END: Scenario

# BEGIN: Scenario: trap_5_container_on_rikyu
# Configuration
_model, _gpus = 'clt-7b', 4

# State
trap_state_5 = h_create_base_state('trap_5_container_on_rikyu')
trap_state_5.workload = {
    'label': 'clt-7b',
    'container_required': True,
    'directory': f'{GROUP_DIR}/clt-7b',
    'duration': '48:00:00',
    'processes_per_node': 4,
    'docs_query': 'mpi module',
    'dataset_local': './corpus.tar',
    'dataset_remote_rikyu': f'{GROUP_DIR}/clt-7b/corpus.tar',
}
trap_state_5.local_files['./corpus.tar'] = 40.0

# Problem
traps['trap_5_container_on_rikyu'] = (
    trap_state_5,
    [('a_initialize_servers',), ('a_get_facility',), ('m_train_on_rikyu', _model, _gpus)],
    'm_train_on_rikyu is the module-based path and cannot host a container; '
    'a containerized workload belongs to m_train_on_rikyu_container'
)
# END: Scenario

# BEGIN: Scenario: trap_6_destroy_before_copy_out
# State
trap_state_6 = h_create_base_state('trap_6_destroy_before_copy_out')
trap_state_6.instances['i-1'] = {
    'offer': 'offer-8842', 'image': 'registry.example.org/clt-7b:cu124',
    'disk_gb': 200, 'disk_used_gb': 80.0, 'onstart': 'python -m clt.train',
    'label': 'clt-7b', 'state': 'Running',
}
trap_state_6.instance_files['i-1'] = {'/workspace/out/clt-7b.pt': 26.0}
trap_state_6.training_state['i-1'] = 'done'
trap_state_6.last_instance_id = 'i-1'

# Problem
traps['trap_6_destroy_before_copy_out'] = (
    trap_state_6,
    [('a_initialize_servers',), ('m_vast_teardown',)],
    'destroying an instance deletes its disk permanently, so no plan may reach '
    'destroy before the checkpoint has been copied out'
)
# END: Scenario

# BEGIN: Scenario: trap_7_vast_disk_too_small
# Configuration
_image_ref, _disk_gb = 'registry.example.org/clt-7b:cu124', 10

# State
trap_state_7 = h_create_base_state('trap_7_vast_disk_too_small')
trap_state_7.vast_offers['offer-8842'] = {
    'gpu_name': 'H100_SXM', 'num_gpus': 4, 'arch': 'x86_64',
    'dph': 6.4, 'max_disk_gb': 512,
}
trap_state_7.images[_image_ref] = {'arch': 'x86_64', 'size_gb': 14.0}
trap_state_7.image_arch_verified[_image_ref] = True
trap_state_7.pushed_images.append(_image_ref)
trap_state_7.workload = {'label': 'clt-7b', 'required_disk_gb': 120}

# Problem
traps['trap_7_vast_disk_too_small'] = (
    trap_state_7,
    [('a_initialize_servers',),
     ('a_vast_search_offers', 'H100_SXM', 4),
     ('a_vast_create_instance', 'offer-8842', _image_ref, _disk_gb, 'python -m clt.train')],
    f'--disk is fixed at creation: {_disk_gb} GB cannot hold a 14 GB image '
    f'plus a 40 GB corpus plus a 26 GB checkpoint'
)
# END: Scenario

# BEGIN: Scenario: trap_8_x86_artifact_on_aarch64
# State
trap_state_8 = h_create_base_state('trap_8_x86_artifact_on_aarch64')
trap_state_8.remote_dirs.append(f'{GROUP_DIR}/work')
trap_state_8.job_artifact['prebuilt-run'] = 'clt-wheel'
trap_state_8.artifact_arch['clt-wheel'] = 'x86_64'

# Problem
traps['trap_8_x86_artifact_on_aarch64'] = (
    trap_state_8,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_submit_job', 'prebuilt-run', 4, 0, '01:00:00', f'{GROUP_DIR}/work')],
    'an x86_64 wheel cannot execute on the aarch64 Grace nodes'
)
# END: Scenario

# BEGIN: Scenario: trap_9_home_quota_exceeded
# Configuration
_dataset = './corpus.tar'

# State
trap_state_9 = h_create_base_state('trap_9_home_quota_exceeded')
trap_state_9.local_files[_dataset] = 40.0

# Problem
traps['trap_9_home_quota_exceeded'] = (
    trap_state_9,
    [('a_initialize_servers',), ('a_fs_upload', _dataset, f'{HOME_DIR}/corpus.tar')],
    'home is 5 GB and is not where datasets go: a 40 GB upload cannot fit'
)
# END: Scenario

# BEGIN: Scenario: trap_10_srun_for_mpi
# State
trap_state_10 = h_create_base_state('trap_10_srun_for_mpi')
trap_state_10.remote_dirs.append(f'{GROUP_DIR}/work')
trap_state_10.job_launcher['mpi-via-srun'] = 'srun'

# Problem
traps['trap_10_srun_for_mpi'] = (
    trap_state_10,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_submit_job', 'mpi-via-srun', 4, 4, '01:00:00', f'{GROUP_DIR}/work')],
    'srun aborts at MPI_Init on Rikyu: MPI jobs must be launched with mpirun'
)
# END: Scenario

# BEGIN: Scenario: trap_11_mpi_without_processes_per_node
# State
trap_state_11 = h_create_base_state('trap_11_mpi_without_processes_per_node')
trap_state_11.remote_dirs.append(f'{GROUP_DIR}/work')
trap_state_11.job_launcher['mpi-no-ppn'] = 'mpirun'

# Problem
traps['trap_11_mpi_without_processes_per_node'] = (
    trap_state_11,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_submit_job', 'mpi-no-ppn', 4, 0, '01:00:00', f'{GROUP_DIR}/work')],
    'mpirun reports "not enough slots" when resources.processes_per_node is unset'
)
# END: Scenario

# BEGIN: Scenario: trap_12_x86_sif_on_rikyu
# Configuration
_ref, _sif = 'ghcr.io/rikyu-user/clt-7b:amd64', f'{GROUP_DIR}/clt-7b-amd64.sif'

# State
trap_state_12 = h_create_base_state('trap_12_x86_sif_on_rikyu')
trap_state_12.oci_images[_ref] = {'arch': 'x86_64', 'size_gb': 11.0}

# Problem
# The conversion itself succeeds - that is the whole point. Only the explicit
# architecture check stops the plan, three actions later.
traps['trap_12_x86_sif_on_rikyu'] = (
    trap_state_12,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_probe_container_runtime',),
     ('a_set_apptainer_env', f'{GROUP_DIR}/.apptainer/cache', '/tmp'),
     ('a_apptainer_pull', 'docker', _ref, _sif),
     ('a_verify_sif_arch', _sif)],
    'an x86_64 image converts to SIF cleanly and only fails at exec, so the '
    'architecture gate is the only thing that catches it before submission'
)
# END: Scenario

# BEGIN: Scenario: trap_13_apptainer_cache_in_home
# Configuration
_ref, _sif = 'nvcr.io/nvidia/pytorch:26.04-py3', f'{GROUP_DIR}/pytorch.sif'

# State
trap_state_13 = h_create_base_state('trap_13_apptainer_cache_in_home')
trap_state_13.oci_images[_ref] = {'arch': 'aarch64', 'size_gb': 9.61}

# Problem
traps['trap_13_apptainer_cache_in_home'] = (
    trap_state_13,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_probe_container_runtime',),
     ('a_set_apptainer_env', f'{HOME_DIR}/.apptainer/cache', '/tmp'),
     ('a_apptainer_pull', 'docker', _ref, _sif)],
    'APPTAINER_CACHEDIR left on the 5 GiB home tier cannot hold a 9.61 GiB '
    'image, let alone the ~2x headroom layer extraction needs'
)
# END: Scenario

# BEGIN: Scenario: trap_14_missing_data1_bind
# Configuration
_sif = f'{IMAGE_LIBRARY}/pytorch:26.04-py3.sif'
_directory = f'{GROUP_DIR}/work'

# State
trap_state_14 = h_create_base_state('trap_14_missing_data1_bind')
trap_state_14.remote_dirs.append(_directory)
trap_state_14.staged_images[_sif] = dict(SITE_IMAGES[_sif])
trap_state_14.staged_images_known = True
trap_state_14.sif_arch_verified[_sif] = True
trap_state_14.container_runtime = APPTAINER
trap_state_14.container_runtime_known = True
trap_state_14.container_needs['ctr-job'] = [f'{_directory}/corpus.tar']

# Problem
traps['trap_14_missing_data1_bind'] = (
    trap_state_14,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_submit_container_job', 'ctr-job', 4, '02:00:00', _directory, _sif,
      'python train.py', [])],
    '/data1 is not in the default bind set, so a job reading group storage '
    'without an explicit --bind cannot see its own input'
)
# END: Scenario

# BEGIN: Scenario: trap_15_exec_without_command
# Configuration
_sif = f'{IMAGE_LIBRARY}/pytorch:26.04-py3.sif'
_directory = f'{GROUP_DIR}/work'

# State
trap_state_15 = h_create_base_state('trap_15_exec_without_command')
trap_state_15.remote_dirs.append(_directory)
trap_state_15.staged_images[_sif] = dict(SITE_IMAGES[_sif])
trap_state_15.staged_images_known = True
trap_state_15.sif_arch_verified[_sif] = True
trap_state_15.container_runtime = APPTAINER
trap_state_15.container_runtime_known = True

# Problem
traps['trap_15_exec_without_command'] = (
    trap_state_15,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_submit_container_job', 'ctr-job', 4, '02:00:00', _directory, _sif,
      '', [GROUP_DIR])],
    'apptainer exec ignores the image ENTRYPOINT and CMD, so a job that '
    'passes no command runs nothing at all'
)
# END: Scenario

# BEGIN: Scenario: trap_16_docker_daemon_transport
# Configuration
_ref, _sif = 'clt-7b:latest', f'{GROUP_DIR}/clt-7b.sif'

# State
trap_state_16 = h_create_base_state('trap_16_docker_daemon_transport')
trap_state_16.oci_images[_ref] = {'arch': 'aarch64', 'size_gb': 11.0}

# Problem
traps['trap_16_docker_daemon_transport'] = (
    trap_state_16,
    [('a_initialize_servers',),
     ('a_get_facility',),
     ('a_probe_container_runtime',),
     ('a_set_apptainer_env', f'{GROUP_DIR}/.apptainer/cache', '/tmp'),
     ('a_apptainer_pull', 'docker-daemon', _ref, _sif)],
    'the docker-daemon: transport needs a Docker daemon, and Rikyu has none; '
    'docker://, docker-archive:, oci-archive: and oci: are the usable ones'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all solvable problem definitions for benchmarking.

    Setup: put the example's parent directory on sys.path and suppress the
    GTPyhop import banner, which would otherwise break output matching.

    >>> import sys, os, io
    >>> _pkg = os.path.dirname(os.path.abspath(__file__))
    >>> _ = sys.path.insert(0, os.path.dirname(_pkg))
    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from rikyu_hpc import the_domain
    >>> sys.stdout = _o
    >>> probs = get_problems()
    >>> len(probs)
    11

    A small helper so each test below is one line. Every scenario is planned
    with the default greedy strategy: this domain never needs backtracking,
    because the two dispatch methods have mutually exclusive preconditions.

    >>> def plan(key, source=None):
    ...     _out = sys.stdout; sys.stdout = io.StringIO()
    ...     try:
    ...         with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...                                    strategy='iterative_greedy') as s:
    ...             r = s.find_plan(*(source or probs)[key][:2])
    ...     finally:
    ...         sys.stdout = _out
    ...     return r

    Scenarios 1 to 3: submit and check, the full stage/run/poll/collect loop,
    and sizing the request from live partition occupancy.

    >>> r = plan('scenario_1_fire_and_forget'); r.success, len(r.plan)
    (True, 4)
    >>> r = plan('scenario_2_upload_run_poll_collect'); r.success, len(r.plan)
    (True, 10)
    >>> r = plan('scenario_3_capacity_aware_submit'); r.success, len(r.plan)
    (True, 6)

    Scenario 3 does not guess its size: 38 idle nodes at 4 GPUs per node give
    152 GPUs of headroom, so the largest supported count under the cap of 16
    is chosen.

    >>> [a for a in plan('scenario_3_capacity_aware_submit').plan
    ...  if a[0] == 'a_submit_job'][0][2]
    16

    Scenarios 4 to 8: wall-time rescue, cancel and resubmit, a filesystem-only
    workflow that never touches the scheduler, a docs-grounded submission, and
    a batch swept with get_job_statuses.

    >>> r = plan('scenario_4_walltime_rescue'); r.success, len(r.plan)
    (True, 10)
    >>> r = plan('scenario_5_cancel_and_resubmit'); r.success, len(r.plan)
    (True, 10)
    >>> r = plan('scenario_6_archive_and_retrieve'); r.success, len(r.plan)
    (True, 6)
    >>> r = plan('scenario_7_docs_grounded_setup'); r.success, len(r.plan)
    (True, 7)
    >>> r = plan('scenario_8_gpu_count_sweep'); r.success, len(r.plan)
    (True, 7)

    Scenario 6 is the ablation: no job id appears anywhere in its plan.

    >>> any('job' in a[0] for a in plan('scenario_6_archive_and_retrieve').plan)
    False

    Scenario 4 raises the limit while the job runs, and only then waits for it.

    >>> [a for a in plan('scenario_4_walltime_rescue').plan
    ...  if a[0] == 'a_update_job'][0][1:]
    ('1000', 'timeLimit', '24:00:00')

    Scenarios 9, 10 and 11 are the routing trio: one goal task, issued with
    identical arguments, reaching three different backends.

    >>> _trio = ['scenario_9_containerized_training', 'scenario_10_backend_routing',
    ...          'scenario_11_apptainer_training']
    >>> len({repr(probs[k][1]) for k in _trio})
    1
    >>> r9 = plan('scenario_9_containerized_training'); r9.success, len(r9.plan)
    (True, 18)
    >>> r10 = plan('scenario_10_backend_routing'); r10.success, len(r10.plan)
    (True, 12)
    >>> r11 = plan('scenario_11_apptainer_training'); r11.success, len(r11.plan)
    (True, 14)

    What separates them is two facts the plan had to fetch: whether a container
    is required at all, and whether the image matches the node architecture.

    >>> [(probs[k][0].workload['container_required'],
    ...   probs[k][0].workload.get('target_arch')) for k in _trio]
    [(True, 'x86_64'), (False, None), (True, 'aarch64')]

    Scenario 10 needs no container, so it never probes for a runtime. Scenarios
    9 and 11 both probe; only 9 leaves the machine, and only because its image
    is x86_64 and the Grace nodes cannot execute it.

    >>> any(a[0] == 'a_probe_container_runtime' for a in r10.plan)
    False
    >>> [any(a[0] == 'a_probe_container_runtime' for a in r.plan) for r in (r9, r11)]
    [True, True]
    >>> any(a[0].startswith('a_vast_') for a in r9.plan)
    True
    >>> [any(a[0].startswith('a_vast_') for a in r.plan) for r in (r10, r11)]
    [False, False]

    Neither Rikyu branch ever calls a vast.ai action, and scenario 9 never
    calls the Slurm scheduler.

    >>> any(a[0] in ('a_submit_job', 'a_submit_container_job') for a in r9.plan)
    False

    The safety invariant on the rented branch: the instance is destroyed only
    after the checkpoint has been copied out, and the copy is the immediately
    preceding action.

    >>> [a[0] for a in r9.plan[-2:]]
    ['a_vast_copy_out', 'a_vast_destroy_instance']

    Scenario 11 looks at the site image library before pulling anything, and
    the architecture gate always precedes the submission.

    >>> [a[0] for a in r11.plan[2:4]]
    ['a_probe_container_runtime', 'a_list_staged_images']
    >>> [a[0] for a in r11.plan
    ...  if a[0] in ('a_verify_sif_arch', 'a_submit_container_job')]
    ['a_verify_sif_arch', 'a_submit_container_job']

    Point the same workload at an image the site already stages and the import
    disappears: no cache redirection, no pull, two actions shorter.

    >>> import copy
    >>> _st, _tk, _ = probs['scenario_11_apptainer_training']
    >>> _st2 = copy.deepcopy(_st)
    >>> _st2.workload['sif_path'] = f'{IMAGE_LIBRARY}/pytorch:26.04-py3.sif'
    >>> _r = plan('x', {'x': (_st2, _tk, '')}); _r.success, len(_r.plan)
    (True, 12)
    >>> [a[0] for a in _r.plan if a[0] in ('a_set_apptainer_env', 'a_apptainer_pull')]
    []

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems


def get_trap_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return the trap problems, every one of which must fail to produce a plan.

    These are kept out of get_problems() so that benchmarking reports the ten
    solvable scenarios without eleven expected failures alongside them. Their
    purpose is attribution: each trap violates exactly one documented rule, so
    a planner that produces a plan for one of them has a specific, nameable bug.

    Setup, as in get_problems.

    >>> import sys, os, io
    >>> _pkg = os.path.dirname(os.path.abspath(__file__))
    >>> _ = sys.path.insert(0, os.path.dirname(_pkg))
    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from rikyu_hpc import the_domain
    >>> sys.stdout = _o
    >>> tr = get_trap_problems()
    >>> len(tr)
    16

    Not one of them may produce a plan, under any of the three strategies.

    >>> def planned(key, strategy):
    ...     _out = sys.stdout; sys.stdout = io.StringIO()
    ...     try:
    ...         with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...                                    strategy=strategy) as s:
    ...             r = s.find_plan(*tr[key][:2])
    ...     finally:
    ...         sys.stdout = _out
    ...     return r.success

    >>> sorted({planned(k, st) for k in tr
    ...         for st in ('iterative_greedy', 'recursive_dfs',
    ...                    'iterative_dfs_backtracking')})
    [False]

    Each trap names the one rule it violates, and every name is distinct.

    >>> len({desc for _, _, desc in tr.values()})
    16

    Returns:
        Dictionary mapping trap IDs to (state, tasks, description) tuples.
    """
    return traps
