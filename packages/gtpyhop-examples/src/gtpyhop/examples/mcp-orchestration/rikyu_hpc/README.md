# Rikyu HPC — Containerized Training and Backend Routing

## Overview

This example models HPC job orchestration on **Rikyu**, the RIKEN R-CCS
GB200 NVL4 system, using the tool surface of the
[RIKEN-RCCS/Rikyu-Agent](https://github.com/RIKEN-RCCS/Rikyu-Agent) MCP
servers. Its central case is **containerized training**, and what makes that
case interesting is that the answer is not the same for every image:

> Rikyu runs containers — Apptainer 1.4.5, unprivileged, behind a
> `singularity` symlink — but says so nowhere. The runtime is absent from the
> facility metadata, from the bundled guide, and from `module avail`. A plan
> can only learn it exists by probing the login node. And once it knows, the
> image's **architecture** decides whether the run can stay: an x86_64 image
> converts to SIF perfectly cleanly and then dies at `exec` on the Grace nodes.

So one goal task reaches three different backends, and neither branch is
hard-coded. Scenarios 9, 10 and 11 issue **identical goal tasks with identical
arguments**; what separates them is two facts the plan had to go and get:

| | container needed? | image arch | routes to | actions |
|---|:--:|:--:|---|--:|
| scenario 10 | no | — | Rikyu, Lmod modules | 12 |
| **scenario 11** | yes | aarch64 | **Rikyu, Apptainer** | 14 |
| scenario 9 | yes | x86_64 | rented vast.ai GPU | 18 |

The second thing this example demonstrates is **safety by precondition**. A
rented instance is destroyed only when the checkpoint has already been copied
out, because `a_vast_destroy_instance` requires it. A free-running agent can
emit a destroy at any turn; a planner cannot *produce a plan* that destroys
before collecting. Trap 6 is that claim, made checkable.

## Provenance

Every constant and rule encoded here traces to a file in the Rikyu-Agent
repository. Reviewers from the Rikyu team should be able to check each row.

| Encoded as | Value | Source |
|---|---|---|
| `supported_gpu_counts` | 1, 2, 3, 4, 8, 12, 16 | `server/rikyu_mcp/data/rikyu_config.json` |
| `gpus_per_node` | 4 | `rikyu_config.json` |
| `max_wall_time` | `96:00:00` | `rikyu_config.json`, `rikyu_guide.md` |
| partition `gpu`, 400 nodes | single partition | `rikyu_config.json` |
| `/home` 5 GB, `/data1` 1 TB, `/tmp` 1.5 TB/GPU | storage tiers | `rikyu_config.json`, `rikyu_guide.md` |
| `cluster_arch = aarch64` | Grace CPUs, aarch64 only | `rikyu_guide.md`, `skills/rikyu-monitoring-jobs` |
| stdout at `<directory>/slurm-<job_id>.out` | default output path | `skills/rikyu-monitoring-jobs` |
| terminal states COMPLETED / FAILED / CANCELED | normalised job states | `skills/rikyu-monitoring-jobs` |
| MPI must use `mpirun`, never `srun` | `srun` aborts at `MPI_Init` | `skills/rikyu-submitting-jobs`, `rikyu_guide.md` |
| MPI must set `processes_per_node` | else "not enough slots" | `skills/rikyu-submitting-jobs` |
| login node rejects heavy compute | prohibition | `skills/rikyu-submitting-jobs`, `hpc_server.py` |
| `cancel_job` only on queued/running | scancel semantics | `hpc_server.py` |
| `update_job(job_id, updates)` | scontrol update, e.g. `timeLimit` | `hpc_server.py` |
| `get_job_statuses([])` = recent jobs | batch sweep | `hpc_server.py`, `skills/rikyu-monitoring-jobs` |
| `fs_compress(paths, archive_path, …)` | takes a list of paths | `hpc_server.py` |
| every other `a_fs_*` signature | `fs_ls/stat/tail/mkdir/upload/download/checksum/extract` | `hpc_server.py` |
| `search_docs`, `list_doc_sections`, `read_doc_section` | docs server tools | `docs_server.py`, `skills/rikyu-reference` |

The container facts come from the site's own **Rikyu containerization findings
v1 (2026-08-05)**, every row of which was probed live on the machine:

| Encoded as | Value | Evidence in the findings |
|---|---|---|
| runtime | Apptainer 1.4.5-3.el8, unprivileged, `singularity` symlink | `command -v` probe; `APPTAINER_SUID_INSTALL=0` |
| discovery | only via login-node probe, not `module avail` | PATH set by `/etc/profile.d/apptainer-path.sh` alone |
| absent runtimes | Docker, Podman, Enroot, Buildah, nerdctl, skopeo, umoci | runtime inventory table |
| usable transports | `docker://`, `docker-archive:`, `oci-archive:`, `oci:` | `docker://` verified end-to-end, `exit=0` |
| unusable transports | `docker-daemon:` (no socket), `library://` (no endpoints) | transport probe table |
| conversion privilege | none — no root, no `--fakeroot` | live `docker://alpine:3.20` → SIF as a normal user |
| arch failure mode | x86_64 converts cleanly, fails only at `exec` | `build-arch` label vs `uname -m` |
| `APPTAINER_CACHEDIR` / `_TMPDIR` | unset → 5 GiB `$HOME`; must be redirected | conversion economics table |
| extraction headroom | ≈ 2 × image size | conversion economics table |
| `/data1` not auto-bound | `ls /data1` inside container fails | auto-bind surface table |
| GPU passthrough | `--nv` works; `--nvccli` unavailable | live `nvidia-smi` → GB200, driver 580.173.02 |
| no scheduler integration | no Pyxis, no `oci.conf` | `PlugStackConfig = (null)` |
| site image library | 6 aarch64 SIFs, 35.24 GiB, `/shared/containers/nvcr.io/nvidia/` | staged library table |
| `exec` ignores ENTRYPOINT/CMD | command must be explicit | Docker-semantics table |

The vast.ai side traces to that platform's own documentation:

| Encoded as | Source |
|---|---|
| `search offers`, `create instance`, `show instance`, `copy`, `logs`, `destroy instance` | `docs.vast.ai` CLI reference |
| `--disk` fixed at creation, cannot be resized | `docs.vast.ai` Docker execution environment |
| instance states Creating → Loading → Connecting → Running | `docs.vast.ai` managing instances |
| destroy deletes all instance data permanently | `docs.vast.ai` managing instances |

### What this example assumes, and Rikyu does not say

Two things here are **not** Rikyu facts. They are flagged in the code and
listed here so that no reader mistakes them for documented behavior.

1. **Server 4 (`vastai`) is not a Rikyu-Agent server.** It is the vast.ai
   public CLI/REST API, modelled as a fourth endpoint so that an image Rikyu
   cannot execute still has somewhere to run. Its actions carry
   `MCP_Tool: vastai:…` tags for consistency with the other three servers, not
   because such an MCP server exists in this repository.
2. **The scripted trajectories** (`job_script`, `instance_script`,
   `training_script`) make the scheduler and control plane deterministic so
   that plan lengths are reproducible. A real run polls until the real system
   moves; here the number of polls is fixed per scenario.

#### One assumption that was retired

An earlier version of this example carried a third assumption:
`documented_container_runtime = False`, described as *"a statement about the
guide, not a claim that Rikyu cannot run containers"*. The containerization
findings settled it: **Rikyu does run containers**, and the flag was retired
rather than flipped, because the interesting fact turned out not to be whether
a runtime is documented but that **the runtime is real and unadvertised**.

That distinction is now load-bearing. `a_probe_container_runtime` exists
precisely because no facility query, guide section or `module avail` can answer
the question — and the probe is modelled as *succeeding with a negative result*
when nothing is found, since learning that a runtime is absent is exactly how a
plan discovers it must go elsewhere. The routing criterion moved from an
absence of documentation to a hard physical fact: an x86_64 SIF cannot execute
on Grace nodes. Scenario 9's plan is unchanged; only its reason for leaving the
machine is now defensible.

## Scenarios

All eleven plan identically under `iterative_greedy` (the default),
`recursive_dfs` and `iterative_dfs_backtracking`. Lengths are measured, not
estimated.

| Scenario | What it exercises | Actions | Status |
|---|---|---|---|
| `scenario_1_fire_and_forget` | submit 4 GPUs, check status once | 4 | Valid |
| `scenario_2_upload_run_poll_collect` | stage → submit → poll → tail → download | 10 | Valid |
| `scenario_3_capacity_aware_submit` | size the request from 38 idle nodes | 6 | Valid |
| `scenario_4_walltime_rescue` | raise `timeLimit` on a running job | 10 | Valid |
| `scenario_5_cancel_and_resubmit` | cancel a 1-GPU job, resubmit at 4 | 10 | Valid |
| `scenario_6_archive_and_retrieve` | filesystem only, **no job id anywhere** | 6 | Valid |
| `scenario_7_docs_grounded_setup` | search the guide, then submit | 7 | Valid |
| `scenario_8_gpu_count_sweep` | 3 jobs at 1/4/16 GPUs, swept together | 7 | Valid |
| `scenario_9_containerized_training` | x86_64 image → **routed to vast.ai** | 18 | Valid |
| `scenario_10_backend_routing` | same task, no container → **Rikyu modules** | 12 | Valid |
| `scenario_11_apptainer_training` | same task, aarch64 image → **Rikyu/Apptainer** | 14 | Valid |

### Dependency coverage

Which scenario threads which class of opaque, service-minted datum. This table
is **computed from the measured plans**, not asserted:

| Scenario | job_id | stdout | doc-id | capacity | gpu-count | fs-ls | image/instance |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 fire-and-forget | ● | · | · | · | ● | · | · |
| 2 upload/run/poll/collect | ● | ● | · | · | ● | · | · |
| 3 capacity-aware | ● | · | · | ● | ● | · | · |
| 4 wall-time rescue | ● | ● | · | · | ● | · | · |
| 5 cancel and resubmit | ● | ● | · | · | ● | · | · |
| 6 archive and retrieve | · | · | · | · | · | ● | · |
| 7 docs-grounded setup | ● | · | ● | · | ● | · | · |
| 8 GPU-count sweep | ● | · | · | · | ● | · | · |
| **9 containerized training** | · | · | · | ● | ● | · | ● |
| 10 backend routing | ● | ● | ● | · | ● | · | · |
| **11 Apptainer training** | ● | ● | · | · | ● | ● | ● |

Column definitions: **job_id** = the plan feeds a scheduler-minted id back to
`poll`/`cancel`/`update`/`get_job_statuses`; **stdout** = it reads
`slurm-<job_id>.out` with `fs_tail`; **doc-id** = it calls `read_doc_section`
on an id a search returned; **capacity** = `get_resource` or `search offers`;
**gpu-count** = `submit_job`, `submit_container_job` or `search offers`;
**fs-ls** = `fs_ls` or `list_staged_images`; **image/instance** = any image
build/push/pull, arch verification, or `vastai` action.

Three rows are worth reading carefully:

- **Scenario 6** is the ablation. It removes the scheduler entirely, testing
  whether data is threaded when there is no job id to lean on.
- **Scenario 9** has no job_id and no stdout column, because it never touches
  Slurm at all. Its progress-reading analogue is `vastai logs`, which threads
  the *instance* id and so is counted in the last column. That absence is the
  measurement, not an omission: it is what routing to another backend costs.
- **Scenario 11** is the only row lighting up both the scheduler columns and
  the image column at once — which is precisely what "containers are a payload
  concern, not a scheduler concern" means in practice.

## Traps

Sixteen states that must **not** produce a plan, returned by
`get_trap_problems()` rather than `get_problems()` so that benchmarking reports
eleven successes rather than eleven successes and sixteen failures.

Each trap violates exactly one documented rule. That is verified by
falsification: repair the single offending datum and the plan appears.

| Trap | Violates | Repair that makes it plan |
|---|---|---|
| `trap_1_unsupported_gpu_count` | GPU count not in the supported set | 5 → 4 GPUs |
| `trap_2_cancel_finished_job` | scancel on a COMPLETED job | job → ACTIVE |
| `trap_3_download_before_terminal` | collecting a file an ACTIVE job is writing | job → COMPLETED |
| `trap_4_heavy_compute_on_login_node` | computation on the login node | command → light |
| `trap_5_container_on_rikyu` | container on the module-based path | `container_required` → False |
| `trap_6_destroy_before_copy_out` | destroy before results are retrieved | copy out first |
| `trap_7_vast_disk_too_small` | `--disk` too small and unresizable | 10 → 200 GB |
| `trap_8_x86_artifact_on_aarch64` | x86_64 wheel on Grace nodes | artifact → aarch64 |
| `trap_9_home_quota_exceeded` | 40 GB dataset into a 5 GB `/home` | target → `/data1` |
| `trap_10_srun_for_mpi` | `srun` for MPI | `srun` → `mpirun` |
| `trap_11_mpi_without_processes_per_node` | MPI without `processes_per_node` | ppn 0 → 4 |
| `trap_12_x86_sif_on_rikyu` | x86_64 SIF on Grace nodes | image → aarch64 |
| `trap_13_apptainer_cache_in_home` | 9.61 GiB pull cached in a 5 GiB `$HOME` | cachedir → `/data1` |
| `trap_14_missing_data1_bind` | job reads `/data1` with no `--bind` | add the bind |
| `trap_15_exec_without_command` | `exec` with no command (ENTRYPOINT ignored) | pass a command |
| `trap_16_docker_daemon_transport` | `docker-daemon:` with no daemon | → `docker://` |

**Trap 12 is the one to read.** The pull *succeeds* — an x86_64 image converts
to SIF cleanly, exactly as on the real machine — and the plan dies three
actions later at the architecture gate. Without `a_verify_sif_arch` as a
distinct, explicit step, that failure would only surface at `exec`, after a
job had already been queued and scheduled.

## Architecture

| Server | Real counterpart | Actions |
|---|---|---|
| 1 | `mcp-python-ingestion` (GTPyhop) | 1 initialization |
| 2 | `rikyu-hpc` (`hpc_server.py`) | 3 facility/resources, 5 job, 1 login, 8 filesystem, 6 Apptainer |
| 3 | `rikyu-docs` (`docs_server.py`) | 3 documentation |
| 4 | `vastai` (CLI/SDK/REST, *not* Rikyu-Agent) | 7 instance, plus 4 local image actions |

The Apptainer actions map to `run_command_on_cluster` and `fs_ls` — there is no
container tool on the Rikyu MCP surface, because there is no scheduler
integration to expose. `a_submit_container_job` maps to plain `submit_job`: the
container is a payload, and the JobSpec's executable simply starts with
`singularity exec`.

The three backends mirror each other, which is what makes them comparable:

| | Rikyu modules | Rikyu Apptainer | vast.ai |
|---|---|---|---|
| acquire capacity | `get_resources` → idle nodes | same | `search offers` → offer id |
| obtain the payload | `module load` | `apptainer pull` → SIF | `docker push` → registry |
| launch | `submit_job` → job id | `submit_job` → job id | `create instance` → instance id |
| state machine | QUEUED → ACTIVE → COMPLETED | same | Creating → Loading → Connecting → Running |
| read progress | `fs_tail` on `slurm-<id>.out` | same | `logs` |
| retrieve | `fs_download` | same | `copy INSTANCE:/path local:./` |
| teardown | job ends by itself | same | `destroy instance`, irreversible |

The middle column collapsing onto the left is the finding, not a modelling
shortcut: with no Pyxis and no configured OCI runtime, a container job on Rikyu
*is* an ordinary job.

## `[EXPECTED_EFFECT]` in this domain

Four state changes carry the `[EXPECTED_EFFECT]` tag, all of the
workflow-gating flavor:

- `a_poll_job_status` / `a_get_job_statuses` — **Slurm**, not the tool call,
  advances the job. The poll only observes it.
- `a_poll_job_status` on COMPLETED — the **job**, not the poll, wrote the
  output files that `a_fs_download` will collect.
- `a_vast_poll_instance` — the **vast.ai control plane** pulls the image and
  brings the container up.
- `a_vast_logs` on `done` — the **container**, not the log read, produced the
  checkpoint.

Drop any of them and the corresponding downstream precondition can never be
satisfied, so planning fails outright.

Each polling action also increments a counter (`poll_count`, `instance_polls`,
`log_reads`, `tail_reads`). Without that, a poll observing no change would be
*idempotent*, and GTPyhop elides idempotent actions from the returned plan —
the plan would silently under-report how many times the agent has to look.

## Domain structure

- **38 actions**: 1 initialization + 20 Rikyu + 6 Apptainer + 4 local image + 7 vast.ai
- **42 methods over 35 task names**; seven task names carry two competing
  methods: `m_poll_until_terminal`, `m_sweep_until_all_terminal`,
  `m_dispatch_training`, `m_dispatch_container_backend`, `m_prepare_sif`,
  `m_vast_poll_until_running`, `m_vast_follow_training`

Every one of those seven pairs has **mutually exclusive** preconditions, so the
routing choices are settled before any commitment and hold under all three
planning strategies — including the default greedy one, which cannot backtrack.

Several methods take no arguments and recover their handle from the state
(`last_job_id`, `last_instance_id`, `doc_hits[0]`, `offer_hits[0]`). This is
deliberate: those identifiers are minted by the remote service at execution
time, so a method expanded *before* that call cannot know them. GTPyhop expands
the todo list left to right against the evolving state, so a method placed
after the minting call reads the handle in its Auxiliary Parameter Inference
block.

## Usage

```python
import gtpyhop
from rikyu_hpc import the_domain, get_problems, get_trap_problems

state, tasks, desc = get_problems()['scenario_9_containerized_training']

with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
                            strategy='iterative_greedy') as s:
    result = s.find_plan(state, tasks)

for i, action in enumerate(result.plan, 1):
    print(f"{i:2d}. {action[0]}")
```

Benchmarking, from the `mcp-orchestration` directory:

```bash
python benchmarking.py rikyu_hpc
```

Doctests (53 tests, from the repository root):

```bash
python -m doctest packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/rikyu_hpc/problems.py
```

## File structure

```
rikyu_hpc/
├── __init__.py     # get_problems(), get_trap_problems(), the_domain
├── domain.py       # 38 actions, 42 methods over 35 task names
├── problems.py     # 11 scenarios + 16 traps, 53 doctests
└── README.md       # this file
```

## References

- **Rikyu-Agent**: https://github.com/RIKEN-RCCS/Rikyu-Agent
- **Rikyu containerization findings v1**, 2026-08-05 (site-internal) — the
  source for every Apptainer fact encoded here
- **vast.ai documentation**: https://docs.vast.ai
- **GTPyhop**: https://github.com/PCfVW/GTPyhop
- **MCP**: https://modelcontextprotocol.io/

---
*Generated 2026-08-04*
