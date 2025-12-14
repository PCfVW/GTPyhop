# Drug Target Discovery - GTPyhop HTN Planning Example

## Overview

This example demonstrates hierarchical task network (HTN) planning for a **drug target discovery pipeline** using the OpenTargets platform. The workflow integrates:

1. **Disease Search** - Query OpenTargets database for disease information
2. **Target Discovery** - Identify genetic targets associated with the disease
3. **Drug Discovery** - Find known drugs targeting the identified genes
4. **Evidence Analysis** - Analyze supporting evidence for target-drug associations

The planner orchestrates 8 primitive actions across a complete drug discovery workflow.

## Benchmarking Scenarios

| Scenario | Configuration | Actions | Status |
|----------|---------------|---------|--------|
| `scenario_1_breast_cancer` | Disease: breast cancer | 8 | ✅ VALID |
| `scenario_2_alzheimers` | Disease: Alzheimer's disease | 8 | ✅ VALID |
| `scenario_3_diabetes` | Disease: type 2 diabetes | 8 | ✅ VALID |

## Planning Problem

**Initial State:**
- Disease query (e.g., "breast cancer", "Alzheimer's disease", "type 2 diabetes")
- OpenTargets database access available

**Goal:**
- Complete drug target discovery pipeline (`m_drug_target_discovery`)

**Task Decomposition:**
The top-level method decomposes into 6 hierarchical methods that coordinate 10 primitive actions.

## MCP Tools Used

This workflow uses the **opentargets-server** Model Context Protocol (MCP) tool server:

### opentargets-server - Drug Target Discovery
- `search_diseases` - Search for diseases by name or term
- `get_disease_info` - Retrieve detailed disease information
- `get_targets_for_disease` - Find genetic targets associated with disease
- `get_target_info` - Retrieve detailed target information
- `get_drugs_for_target` - Find drugs targeting specific genes
- `get_drug_info` - Retrieve detailed drug information
- `get_evidence` - Analyze evidence supporting target-drug associations

## File Structure

```
drug_target_discovery/
├── domain.py           # Domain definition with 8 actions and 6 methods
├── problems.py         # Initial state definitions (3 scenarios)
├── __init__.py         # Package initialization
└── README.md           # This file
```

## How to Run

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.mcp_orchestration.drug_target_discovery import the_domain, problems

# Create a planner session
session = gtpyhop.PlannerSession(the_domain, verbose=1)

# Get problem instance
state, tasks, desc = problems.get_problems()['scenario_1_breast_cancer']

# Find the plan
result = session.find_plan(state, tasks)

if result.success:
    print(f"Plan found with {len(result.plan)} actions:")
    for i, action in enumerate(result.plan, 1):
        print(f"  {i}. {action[0]}")
```

### Using the benchmarking script

```bash
cd src/gtpyhop/examples/mcp-orchestration
python benchmarking.py drug_target_discovery
```

## Expected Output

The planner should generate a plan with 8 actions:

1. `a_search_disease` - Search OpenTargets for disease
2. `a_get_disease_targets` - Find genetic targets for disease
3. `a_validate_targets` - Validate target associations
4. `a_analyze_pathways` - Analyze biological pathways
5. `a_get_target_structures` - Retrieve protein structures
6. `a_find_compounds` - Find candidate compounds
7. `a_gather_literature` - Gather supporting literature
8. `a_generate_report` - Generate final discovery report

## Domain Statistics

- **Primitive Actions**: 8
- **Methods**: 6
- **Servers**: 1 (opentargets-server)
- **Scenarios**: 3

## Notes

- **Format Version**: Follows GTPyhop 1.7.0+ style guide (v2.0.0)
- **MCP Tools**: Actions reference MCP tools but do NOT execute them (planning only)
- **State Properties**: Actions define preconditions and effects on state properties
- **Workflow Gates**: Properties marked `[ENABLER]` act as workflow gates between phases
- **Unified Scenario Block**: Problems use Configuration → State → Problem structure

## References

- OpenTargets Platform: https://platform.opentargets.org/
- GTPyhop Documentation: https://github.com/dananau/GTPyhop
- MCP Protocol: https://modelcontextprotocol.io/

---
*Generated 2025-12-14*

