# Bio-Opentrons Flex HTN Domain

## Overview

This example demonstrates **cross-server HTN (Hierarchical Task Network) plan execution orchestration** for PCR (Polymerase Chain Reaction) workflow automation using GTPyhop 1.7.0 and the Opentrons Flex robot platform.

### Key Features

- **Dynamic Sample Scaling**: Supports 4 to 96 samples (full 96-well plate) with automatic plan generation
- **Plan Length Formula**: `plan_length = 31 + 6 × num_samples + 2 × (ceil(n/40) - 1)`
- **Three-Server Architecture**: Movement, liquid handling, and module control separated for parallel execution potential

## Benchmarking Scenarios

| Scenario | Configuration | Actions | Status |
|----------|---------------|---------|--------|
| `scenario_1` | 4 samples, 25 cycles | 55 | ✅ VALID |
| `scenario_2` | 8 samples, 30 cycles | 79 | ✅ VALID |
| `scenario_3` | 16 samples, 35 cycles | 127 | ✅ VALID |
| `scenario_4` | 32 samples, 25 cycles | 223 | ✅ VALID |
| `scenario_5` | 48 samples, 30 cycles | 321 | ✅ VALID |
| `scenario_6` | 96 samples (full plate), 35 cycles | 611 | ✅ VALID |

**Note:** Maximum 96 samples due to 96-well plate hardware constraint (8 rows × 12 columns).

## Three-Server MCP Architecture

### Server 1: Movement Server
- **Role**: Pipette movement and tip operations
- **Actions**:
  - `a_load_labware` - Load labware onto deck slots
  - `a_load_pipette` - Load pipettes (1-channel, 8-channel)
  - `a_pick_up_tip` - Pick up tips from rack
  - `a_drop_tip` - Drop tips to waste
  - `a_move_to_well` - Move pipette to well position

### Server 2: Liquid Handling Server
- **Role**: Liquid transfer operations
- **Actions**:
  - `a_aspirate` - Aspirate liquid from wells
  - `a_dispense` - Dispense liquid to wells
  - `a_mix` - Mix solutions in wells
  - `a_blow_out` - Blow out residual liquid

### Server 3: Module Control Server
- **Role**: Temperature module and thermocycler control
- **Actions**:
  - `a_set_temperature` - Set temperature module temp (4°C reagent cooling)
  - `a_close_thermocycler_lid` - Close thermocycler lid
  - `a_open_thermocycler_lid` - Open thermocycler lid
  - `a_set_thermocycler_temperature` - Set thermocycler block temp
  - `a_execute_thermocycler_profile` - Execute PCR thermal profile
  - `a_deactivate_thermocycler` - Deactivate thermocycler

### Server Architecture Rationale

| Server | Separation Rationale |
|--------|---------------------|
| **movement-server** | Hardware-specific motion control with independent calibration |
| **liquid-server** | Liquid class-specific optimizations, volume accuracy calibration |
| **module-server** | Temperature modules run independently, enabling parallel execution |

## Hierarchical Decomposition Structure

```
m_initialize_and_run_pcr(num_samples, num_cycles)      [ENTRY POINT]
├── a_initialize_servers                                [ACTION]
└── m_complete_pcr_workflow(num_samples, num_cycles)   [TOP-LEVEL]
    ├── m_phase1_deck_initialization                    [PHASE]
    │   ├── m_setup_labware                             [SUB-METHOD]
    │   │   └── [5 a_load_labware actions]
    │   └── m_setup_instruments                         [SUB-METHOD]
    │       └── [4 actions: pipettes + temp module]
    ├── m_phase2_reagent_preparation                    [PHASE]
    │   ├── m_prepare_master_mix                        [SUB-METHOD]
    │   │   └── [11 liquid handling actions]
    │   └── m_distribute_master_mix                     [SUB-METHOD]
    │       └── [4 + num_samples dispense actions]
    ├── m_phase3_sample_loading                         [PHASE]
    │   └── m_transfer_samples                          [SUB-METHOD]
    │       └── [5 × num_samples actions]
    ├── m_phase4_thermocycling                          [PHASE]
    │   ├── m_prepare_thermocycler                      [SUB-METHOD]
    │   │   └── [2 actions: close lid + initial temp]
    │   └── m_run_pcr_profile                           [SUB-METHOD]
    │       └── [3 actions: profile + extension + hold]
    └── m_phase5_post_processing                        [PHASE]
        └── [2 actions: deactivate + open lid]
```

**Decomposition Depth: 5 Levels**

## Protocol Phases

1. **Deck Initialization** - Load labware (plates, tip racks) and pipettes
2. **Reagent Preparation** - Prepare master mix from components
3. **Master Mix Distribution** - Dispense master mix to all sample wells
4. **Sample Loading** - Transfer samples to PCR plate with mixing
5. **Thermocycling** - Execute PCR thermal profile (denaturation, annealing, extension)
6. **Post-Processing** - Deactivate thermocycler, open lid

## Domain Statistics

- **Primitive Actions**: 18
- **Methods**: 14
- **Servers**: 3 (movement, liquid, module)
- **Scenarios**: 6

## Plan Length Formula

```
plan_length = 31 + 6 × num_samples + 2 × (ceil(n/40) - 1)
```

**Formula breakdown:**
- **31 fixed actions**: Initialization, labware loading, pipette setup, master mix prep, thermocycling
- **6 actions per sample**: 1 dispense (master mix) + 5 transfer actions (pick_up, aspirate, dispense, mix, drop_tip)
- **Multi-cycle aspirate**: Pipette max capacity is 1000 µL; at 25 µL/sample, one aspirate covers 40 samples max. For >40 samples, additional aspirate cycles are needed.

## Usage Examples

### Using PlannerSession (Recommended)

```python
import gtpyhop
from gtpyhop.examples.mcp_orchestration.bio_opentrons import the_domain, problems

# Create planner session
session = gtpyhop.PlannerSession(the_domain, verbose=1)

# Get problem instance
state, tasks, desc = problems.get_problems()['scenario_1']

# Find plan
result = session.find_plan(state, tasks)

if result.success:
    print(f"Plan found with {len(result.plan)} actions:")
    for i, action in enumerate(result.plan, 1):
        print(f"  {i}. {action[0]}")
```

### Using the benchmarking script

```bash
cd src/gtpyhop/examples/mcp-orchestration
python benchmarking.py bio_opentrons
```

## Key Challenges Addressed

1. **Dynamic Sample Scaling**: Plan length scales linearly with sample count
2. **Multi-Cycle Aspirate**: For >40 samples, pipette capacity requires additional aspirate cycles
3. **Master Mix Distribution**: Efficient reagent distribution across variable sample counts
4. **Thermocycler Coordination**: Module operations interleaved with liquid handling
5. **Volume Tracking**: Simplified symbolic tracking for plan validation

## File Structure

```
bio_opentrons/
├── domain-V3.py      # Domain definition (18 actions, 14 methods)
├── problems.py       # Initial states (6 scenarios: 4-96 samples)
├── __init__.py       # Package initialization
└── README.md         # This file
```

## Opentrons SDK Mapping

The domain actions map directly to Opentrons API commands:

| Domain Action | Opentrons API |
|---------------|---------------|
| `a_load_labware` | `protocol.load_labware()` |
| `a_load_pipette` | `protocol.load_instrument()` |
| `a_pick_up_tip` | `pipette.pick_up_tip()` |
| `a_aspirate` | `pipette.aspirate()` |
| `a_dispense` | `pipette.dispense()` |
| `a_mix` | `pipette.mix()` |
| `a_close_thermocycler_lid` | `thermocycler.close_lid()` |
| `a_execute_thermocycler_profile` | `thermocycler.execute_profile()` |

## Limitations and Considerations

1. **Simulation vs. Real Hardware**: Domain works in simulation; real execution requires Opentrons Flex connection
2. **Deck Layout**: Thermocycler occupies D1-D3 slots; domain doesn't validate conflicts
3. **Volume Tracking**: Simplified symbolic tracking; production needs liquid class definitions
4. **Error Recovery**: No retry logic modeled; production systems need recovery methods
5. **Parallelism**: HTN planning is sequential; real opportunity for concurrent thermocycler + robot operations

## Notes

- **Format Version**: Follows GTPyhop 1.7.0+ style guide (v2.0.0)
- **Unified Scenario Block**: Problems use Configuration → State → Problem structure
- **MCP Tools**: Actions reference MCP tools but do NOT execute them (planning only)

## References

- [Opentrons Python API v2](https://docs.opentrons.com/v2/)
- [GTPyhop Documentation](https://github.com/dananau/GTPyhop)
- [MCP Protocol](https://modelcontextprotocol.io/)

---
*Generated 2025-12-14*

