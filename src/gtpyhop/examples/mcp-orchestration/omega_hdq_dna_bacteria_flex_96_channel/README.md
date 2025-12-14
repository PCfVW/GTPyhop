# Omega HDQ DNA Bacteria Extraction Domain

## Overview

This example demonstrates **multi-server HTN (Hierarchical Task Network) plan execution orchestration** for DNA extraction workflow automation using GTPyhop 1.7.0 and the Opentrons Flex robot platform with magnetic bead-based purification.

### Key Features

- **Complete DNA Extraction Protocol**: 8-phase workflow from lysis to elution
- **Four-Server Architecture**: HTN planning, liquid handling, module control, and gripper operations
- **Configurable Scenarios**: Standard, dry run, and manual mixing modes

## Benchmarking Scenarios

| Scenario | Configuration | Actions | Status |
|----------|---------------|---------|--------|
| `scenario_1_standard` | Heater-shaker, 3 washes, full timings | 129 | ✅ VALID |
| `scenario_2_dry_run` | 1 wash, reduced timings (testing) | 91 | ✅ VALID |
| `scenario_3_manual_mixing` | No heater-shaker, tip mixing | 89 | ✅ VALID |

## Four-Server MCP Architecture

### Server 1: HTN Planning Server
- **Role**: Plan generation via GTPyhop
- **Function**: Decomposes high-level DNA extraction goal into executable action sequences

### Server 2: Liquid Handling Server
- **Role**: 96-channel pipetting operations
- **Actions**:
  - `a_pick_up_tip` - Pick up tips from rack
  - `a_return_tip` - Return tips to rack
  - `a_aspirate` - Aspirate liquid from well
  - `a_dispense` - Dispense liquid to well
  - `a_blow_out` - Blow out residual liquid
  - `a_air_gap` - Create air gap in tip
  - `a_mix` - Mix solution in well
  - `a_set_flow_rate` - Set aspirate/dispense rates
  - `a_home` - Home pipette

### Server 3: Module Control Server
- **Role**: Heater-shaker, temperature module, timing control
- **Actions**:
  - `a_hs_set_temperature` - Set heater-shaker temperature
  - `a_hs_set_shake_speed` - Set shake speed and start
  - `a_hs_deactivate_shaker` - Stop shaking
  - `a_hs_open_latch` / `a_hs_close_latch` - Latch control
  - `a_temp_set_temperature` - Set temp module temperature
  - `a_delay` - Wait for specified time

### Server 4: Gripper/Movement Server
- **Role**: Labware transfers between deck positions
- **Actions**:
  - `a_move_labware` - Move labware with gripper

### Server Architecture Rationale

| Server | Separation Rationale |
|--------|---------------------|
| **liquid-handling-server** | 96-channel pipette requires precise volume tracking |
| **module-control-server** | Modules run independently, enabling parallel incubations |
| **gripper-server** | Physical labware movement separate from liquid operations |

## Hierarchical Decomposition Structure

```
m_hdq_dna_extraction                           [ENTRY POINT]
├── m_initialize_protocol                       [INIT]
│   └── [close latch + pick up tip]
├── m_tl_lysis_phase                           [PHASE 1]
│   ├── [mix TL+PK buffers]
│   ├── [transfer to samples]
│   └── [incubate with shaking]
├── m_transfer_sample_to_new_plate             [PHASE 2]
│   └── [200µL sample transfer]
├── m_al_lysis_phase                           [PHASE 3]
│   ├── [add AL buffer]
│   └── [incubate 4 min]
├── m_bead_binding_phase                       [PHASE 4]
│   ├── [mix beads]
│   ├── [transfer to samples]
│   └── [incubate 10 min]
├── m_magnetic_separation_initial              [PHASE 5]
│   ├── [move to magblock]
│   ├── [wait for settling]
│   └── m_remove_supernatant
├── m_wash_all_cycles                          [PHASE 6]
│   └── m_single_wash_cycle (×3)
│       ├── [add wash buffer]
│       ├── [shake/mix]
│       ├── [magnetic separate]
│       └── [remove supernatant]
├── m_dry_beads                                [PHASE 7]
│   └── [10 min air dry]
├── m_elution_phase                            [PHASE 8]
│   ├── [add elution buffer]
│   ├── [mix/shake]
│   ├── [magnetic separate]
│   └── [collect DNA]
└── m_finalize_protocol                        [FINISH]
    └── [home pipette]
```

**Decomposition Depth: 4 Levels**

## Protocol Phases

1. **TL Lysis** - Mix TL+PK buffers, transfer to samples, incubate
2. **Sample Transfer** - Transfer 200µL lysed sample to deep well plate
3. **AL Lysis** - Add AL buffer, mix, incubate 4 min
4. **Bead Binding** - Add magnetic beads + binding buffer, incubate 10 min
5. **Magnetic Separation** - Move to magblock, remove supernatant
6. **Wash Cycles** - 3× wash with VHB/SPM buffers
7. **Drying** - Air dry beads 10 min
8. **Elution** - Add elution buffer, collect purified DNA

## Domain Statistics

- **Primitive Actions**: 17
- **Methods**: 14
- **Servers**: 4 (planning + 3 execution)
- **Scenarios**: 3

## Usage Examples

### Session-Based Planning (Recommended)

```python
import sys
sys.path.insert(0, r'path/to/mcp-orchestration')

from omega_hdq_dna_bacteria_flex_96_channel import the_domain, get_problems
import gtpyhop

# Create planner session
session = gtpyhop.PlannerSession(the_domain, verbose=1)

# Get problem instance
state, tasks, desc = get_problems()['scenario_1_standard']

# Find plan
result = session.find_plan(state, tasks)

if result.success:
    print(f"Plan found with {len(result.plan)} actions:")
    for i, action in enumerate(result.plan, 1):
        print(f"  {i}. {action[0]}")
```

### Running Benchmarks

```bash
cd src/gtpyhop/examples/mcp-orchestration
python benchmarking.py omega_hdq_dna_bacteria_flex_96_channel
```

## Key Challenges Addressed

1. **Conditional Branching**: Protocol adapts based on `heater_shaker_available`, `dry_run`, and `tip_mixing` flags
2. **Complex Mixing Patterns**: `m_resuspend_pellet` method handles multi-position mixing
3. **Dynamic Volumes**: Volumes computed from state parameters (TL, AL, wash, elution)
4. **Module Coordination**: Heater-shaker, temperature module, and magnetic block orchestration
5. **Wash Loop Variations**: Different waste destinations per wash cycle

## File Structure

```
omega_hdq_dna_bacteria_flex_96_channel/
├── domain.py      # Domain definition (17 actions, 14 methods)
├── problems.py    # Initial states (3 scenarios)
├── __init__.py    # Package initialization
├── README.md      # This file
└── Omega_HDQ_DNA_Bacteria-Flex_96_channel.py  # Original protocol (reference)
```

## Attribution

Based on [Opentrons Flex protocol](https://library.opentrons.com/p/HDQ_DNA_Flex_96-Bacteria) by Zach Galluzzo <zachary.galluzzo@opentrons.com>

## References

- [Opentrons Python API v2](https://docs.opentrons.com/v2/)
- [GTPyhop Documentation](https://github.com/dananau/GTPyhop)
- [MCP Protocol](https://modelcontextprotocol.io/)

---
*Generated 2025-12-14*

