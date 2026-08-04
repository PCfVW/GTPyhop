"""
MCP Orchestration Examples for GTPyhop

This package contains examples of using GTPyhop for orchestrating workflows
that involve Model Context Protocol (MCP) tools. These examples demonstrate
hierarchical task network (HTN) planning for complex scientific workflows
and cross-server coordination.

Examples:
- bio_opentrons: PCR workflow automation with dynamic sample scaling across
  three MCP servers
- cross_server: Cross-server HTN plan execution orchestration demonstrating
  coordination between multiple MCP servers for robot manipulation tasks
- drug_target_discovery: Drug target discovery pipeline using the OpenTargets
  platform
- omega_hdq_dna_bacteria_flex_96_channel: DNA extraction on Opentrons Flex
  across four MCP servers
- rikyu_hpc: HPC job orchestration on the RIKEN R-CCS Rikyu system, where one
  training task routes to Rikyu's Lmod modules, to Rikyu's own unadvertised
  Apptainer runtime, or to a rented GPU, according to facts the plan probes
- tnf_cancer_modelling: Multiscale TNF cancer modeling workflow integrating
  Boolean network modeling (MaBoSS) with agent-based simulation (PhysiCell)

-- Updated 2026-08-04
"""

# Make subpackages available
__all__ = [
    'bio_opentrons',
    'cross_server',
    'drug_target_discovery',
    'omega_hdq_dna_bacteria_flex_96_channel',
    'rikyu_hpc',
    'tnf_cancer_modelling',
]

