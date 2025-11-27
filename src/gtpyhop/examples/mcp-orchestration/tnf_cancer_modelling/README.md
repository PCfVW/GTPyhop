# TNF Cancer Modeling - GTPyhop HTN Planning Example

## Overview

This example demonstrates hierarchical task network (HTN) planning for a **multiscale TNF cancer modeling workflow**. The workflow integrates:

1. **Boolean Network Modeling** - Using MaBoSS to simulate TNF-responsive gene regulatory networks
2. **Agent-Based Multicellular Simulation** - Using PhysiCell to model cancer cell populations
3. **Multiscale Integration** - Coupling intracellular Boolean dynamics with multicellular spatial behaviors

The planner orchestrates 12 primitive actions across two major phases:
- **Phase 1**: Boolean Network Development (network construction, preprocessing, MaBoSS simulation, validation)
- **Phase 2**: Multicellular Integration (PhysiCell setup, microenvironment configuration, MaBoSS-PhysiCell coupling, simulation execution)

## Planning Problem

**Initial State:**
- TNF-related gene list: `["TNF", "TNFR1", "TNFR2", "NFKB1", "TP53", "MDM2", "CASP3", "CASP8", "MYC", "CCND1"]`
- Omnipath database access available

**Goal:**
- Complete multiscale TNF cancer modeling workflow (`m_multiscale_tnf_cancer_modeling`)

**Task Decomposition:**
The top-level method decomposes into 14 hierarchical methods that coordinate 12 primitive actions.

## MCP Tools Used

This workflow uses three Model Context Protocol (MCP) tool servers:

### 1. **neko** - Network Construction and Analysis
- `neko:create_network` - Generate signaling networks from gene lists using Omnipath
- `neko:remove_bimodal_interactions` - Simplify networks for Boolean modeling
- `neko:check_disconnected_nodes` - Validate network connectivity
- `neko:export_to_bnet` - Export networks to BNET format

### 2. **maboss** - Boolean Network Simulation
- `maboss:create_maboss_files` - Generate MaBoSS configuration files (.bnd, .cfg)
- `maboss:run_simulation` - Execute stochastic Boolean simulations
- `maboss:analyze_results` - Analyze steady-state distributions and trajectories

### 3. **physicell** - Agent-Based Multicellular Simulation
- `physicell:create_project` - Initialize PhysiCell projects from templates
- `physicell:configure_microenvironment` - Set up substrate diffusion (TNF)
- `physicell:add_cell_type` - Define cancer cell types with properties
- `physicell:integrate_boolean_model` - Couple MaBoSS models to cell behaviors
- `physicell:run_simulation` - Execute multiscale simulations

## File Structure

```
tnf_cancer_modelling/
├── domain.py           # Domain definition with 12 actions and 14 methods
├── problems.py         # Initial state definitions
├── __init__.py         # Package initialization with problem discovery
└── README.md           # This file
```

## How to Run

### Option 1: Using the domain directly

```python
import gtpyhop
from gtpyhop.examples.mcp_orchestration.tnf_cancer_modelling import domain, problems

# Find the plan
plan = gtpyhop.find_plan(
    problems.initial_state_scenario_1,
    [('m_multiscale_tnf_cancer_modeling',)]
)

# Display the plan
if plan:
    print(f"Plan found with {len(plan)} actions:")
    for i, action in enumerate(plan, 1):
        print(f"  {i}. {action[0]}")
else:
    print("No plan found")
```

### Option 2: Using PlannerSession (thread-safe, GTPyhop 1.3.0+)

```python
import gtpyhop
from gtpyhop.examples.mcp_orchestration.tnf_cancer_modelling import domain, problems

# Create a planner session
session = gtpyhop.PlannerSession(domain.the_domain, verbose=1)

# Find the plan
plan = session.find_plan(
    problems.initial_state_scenario_1,
    [('m_multiscale_tnf_cancer_modeling',)]
)

# Display the plan
if plan:
    print(f"Plan found with {len(plan)} actions:")
    for i, action in enumerate(plan, 1):
        print(f"  {i}. {action[0]}")
else:
    print("No plan found")
```

### Option 3: Using the benchmarking script

```bash
cd C:\Users\Eric JACOPIN\Documents\Code\Source\GTPyhop\src\gtpyhop\examples\mcp-orchestration
python benchmarking.py
```

## Expected Output

The planner should generate a plan with 12 actions:

1. `a_create_tnf_cancer_network` - Create initial network from TNF genes
2. `a_remove_bimodal_interactions` - Simplify network for Boolean modeling
3. `a_check_network_connectivity` - Verify network connectivity
4. `a_export_network_to_bnet` - Export to BNET format
5. `a_create_maboss_files` - Generate MaBoSS configuration
6. `a_run_maboss_simulation` - Execute Boolean simulation
7. `a_analyze_maboss_results` - Analyze simulation results
8. `a_create_physicell_project` - Initialize PhysiCell project
9. `a_configure_microenvironment` - Set up TNF diffusion
10. `a_add_cancer_cell_type` - Define cancer cell type
11. `a_integrate_maboss_model` - Couple Boolean model to cells
12. `a_execute_multiscale_simulation` - Run multiscale simulation

## Notes

- **Structure**: Follows GTPyhop 1.4.0 new structure pattern (single `domain.py` file)
- **MCP Tools**: Actions reference MCP tools but do NOT execute them (planning only)
- **State Properties**: Actions define preconditions and effects on state properties
- **Workflow Gates**: Properties marked `[ENABLER]` act as workflow gates between phases
- **Format Version**: v1.1 (following gtpyhop-action-format-design-v1.md and gtpyhop-methods-format-design-v1.md)

## References

- MaBoSS: https://maboss.curie.fr/
- PhysiCell: http://physicell.org/
- Omnipath: https://omnipathdb.org/

