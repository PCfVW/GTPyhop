# MCP Orchestration Examples for GTPyhop

## Overview

This directory contains examples demonstrating **MCP (Model Context Protocol) orchestration** using GTPyhop. The examples show hierarchical task network (HTN) planning for complex scientific workflows and cross-server coordination where the HTN planner generates structural plans and leaf-level actions are delegated to external MCP servers.

These domains illustrate how a single HTN planner can coordinate actions across multiple MCP servers to accomplish multi-step workflows in laboratory automation, drug discovery, and cancer research.

## Available Examples

| Example | Directory | Description |
|---------|-----------|-------------|
| **Bio-Opentrons** | `bio_opentrons/` | PCR workflow automation with dynamic sample scaling across 3 MCP servers |
| **Omega HDQ DNA Extraction** | `omega_hdq_dna_bacteria_flex_96_channel/` | DNA extraction on Opentrons Flex with 4 MCP servers |
| **Drug Target Discovery** | `drug_target_discovery/` | Drug target discovery pipeline using OpenTargets platform |
| **TNF Cancer Modelling** | `tnf_cancer_modelling/` | Multiscale TNF cancer modeling (MaBoSS + PhysiCell) |
| **Cross-Server** | `cross_server/` | Cross-server robot orchestration (pick-and-place) |
| **Rikyu HPC** | `rikyu_hpc/` | HPC job orchestration with containerized training routed to a rented GPU |

### 1. Bio-Opentrons

PCR (Polymerase Chain Reaction) workflow automation:
- 6 scenarios (4 to 96 samples), 55-611 actions
- Three-server architecture: movement, liquid handling, and module control
- Dynamic plan scaling: `plan_length = 31 + 6 x num_samples + 2 x (ceil(n/40) - 1)`

**Use case**: Demonstrating scalable HTN planning for laboratory automation with parameterized scenarios.

### 2. Omega HDQ DNA Extraction

Complete DNA extraction protocol on Opentrons Flex:
- 3 scenarios (standard, dry run, manual mixing), 89-129 actions
- Four-server architecture: HTN planning, liquid handling, module control, gripper operations
- 8-phase workflow from lysis to elution with magnetic bead-based purification

**Use case**: Demonstrating multi-server coordination for a complex, multi-phase laboratory protocol.

### 3. Drug Target Discovery

Drug target discovery pipeline using OpenTargets:
- 3 scenarios (breast cancer, Alzheimer's, type 2 diabetes), 8 actions each
- Integrates disease search, target discovery, drug discovery, and evidence analysis

**Use case**: Demonstrating HTN planning for bioinformatics pipelines.

### 4. TNF Cancer Modelling

Multiscale TNF cancer modeling workflow:
- 1 scenario, 12 actions
- Two-phase workflow: Boolean network modeling (MaBoSS) + agent-based simulation (PhysiCell)
- 14 hierarchical methods coordinating 12 primitive actions

**Use case**: Demonstrating HTN decomposition for multi-tool scientific workflows.

### 5. Cross-Server

Cross-server robot orchestration:
- 2 scenarios (single and multi-block transfer), 9-15 actions
- Three-server architecture: HTN planning, gripper control, arm motion planning

**Use case**: Demonstrating cross-server coordination for robotic pick-and-place tasks.

### 6. Rikyu HPC

HPC job orchestration on the RIKEN R-CCS Rikyu system, modelled on the
[Rikyu-Agent](https://github.com/RIKEN-RCCS/Rikyu-Agent) MCP tool surface:
- 11 scenarios, 4-18 actions, plus 16 traps that must *not* produce a plan
- Four-server architecture: HTN planning, `rikyu-hpc`, `rikyu-docs`, and
  vast.ai for rented GPUs
- Scenarios 9, 10 and 11 issue **identical goal tasks** and reach three
  different backends. Rikyu runs Apptainer but advertises it nowhere, so the
  plan probes the login node; then the image architecture decides, because an
  x86_64 image converts to SIF cleanly and only fails at `exec`
- Traps are exposed through `get_trap_problems()`, not `get_problems()`, and
  each is falsifiable: repair the one datum it names and the plan appears

**Use case**: Demonstrating backend routing driven by facts the plan had to
fetch and probe, and safety invariants that a planner enforces by construction
— a rented instance cannot be destroyed before its results have been retrieved.

## Directory Structure

```
mcp-orchestration/
+-- __init__.py
+-- benchmarking.py                             # Unified benchmarking script
+-- benchmarking_quickstart.md                  # Quick start guide
+-- README.md                                   # This file
+-- bio_opentrons/
|   +-- __init__.py
|   +-- domain.py                               # 15 actions, 8 methods
|   +-- problems.py                             # 6 scenarios
|   +-- README.md
+-- omega_hdq_dna_bacteria_flex_96_channel/
|   +-- __init__.py
|   +-- domain.py                               # 17 actions, 14 methods
|   +-- problems.py                             # 3 scenarios
|   +-- README.md
+-- drug_target_discovery/
|   +-- __init__.py
|   +-- domain.py                               # 8 actions, 6 methods
|   +-- problems.py                             # 3 scenarios
|   +-- README.md
+-- tnf_cancer_modelling/
|   +-- __init__.py
|   +-- domain.py                               # 12 actions, 14 methods
|   +-- problems.py                             # 1 scenario
|   +-- README.md
+-- cross_server/
|   +-- __init__.py
|   +-- domain.py                               # 9 actions, 6 methods
|   +-- problems.py                             # 2 scenarios
|   +-- README.md
+-- rikyu_hpc/
    +-- __init__.py
    +-- domain.py                               # 38 actions, 42 methods / 35 tasks
    +-- problems.py                             # 11 scenarios + 16 traps
    +-- README.md
```

## Quick Start

```bash
cd src/gtpyhop/examples/mcp-orchestration

# List available domains
python benchmarking.py --list-domains

# Run a specific domain
python benchmarking.py bio_opentrons
python benchmarking.py omega_hdq_dna_bacteria_flex_96_channel
python benchmarking.py drug_target_discovery
python benchmarking.py tnf_cancer_modelling
python benchmarking.py cross_server
python benchmarking.py rikyu_hpc

# Run with verbose output
python benchmarking.py tnf_cancer_modelling --verbose 2
```

Note that `benchmarking.py` runs `get_problems()` only. The `rikyu_hpc` traps
live in `get_trap_problems()` and are exercised by that example's doctests.

## Requirements

- GTPyhop 1.7.0+
- psutil (`pip install psutil`)
- Python 3.8+

## See Also

- [benchmarking_quickstart.md](benchmarking_quickstart.md) - Detailed benchmarking usage guide
- [bio_opentrons/README.md](bio_opentrons/README.md) - PCR workflow details
- [omega_hdq_dna_bacteria_flex_96_channel/README.md](omega_hdq_dna_bacteria_flex_96_channel/README.md) - DNA extraction details
- [drug_target_discovery/README.md](drug_target_discovery/README.md) - Drug discovery pipeline details
- [tnf_cancer_modelling/README.md](tnf_cancer_modelling/README.md) - Cancer modeling workflow details
- [cross_server/README.md](cross_server/README.md) - Cross-server orchestration details
- [rikyu_hpc/README.md](rikyu_hpc/README.md) - Rikyu HPC details, including the
  provenance table for every encoded facility constant and rule

---
*Generated 2026-02-12, updated 2026-08-04*
