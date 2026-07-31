# GTPyhop version 1.9.7

[![Python Version](https://img.shields.io/badge/python-3%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Clear%20BSD-green.svg)](https://github.com/PCfVW/GTPyhop/blob/pip/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/gtpyhop)](https://pypi.org/project/gtpyhop/)
<!-- UPDATE MANUALLY when doctests are added or removed -->
[![Doctests](https://img.shields.io/badge/doctests-789%20passing-brightgreen)](docs/changelog.md)

GTPyhop is an HTN planning system based on [Pyhop](https://bitbucket.org/dananau/pyhop/src/master/), but generalized to plan for both goals and tasks.

[Dana Nau](https://www.cs.umd.edu/~nau/) is the original author of GTPyhop.

---

## Table of Contents

1. [Installation](#installation)
2. [Testing Your Installation](#testing-your-installation)
3. [Quick Start Tutorial](#lets-htn-start)
4. [Thread-Safe Sessions](#thread-safe-sessions-130)
5. [Examples](#examples)
6. [Documentation](#-documentation)
7. [New Features](#new-features)
8. [Project Structure](#project-structure)

---

## The pip Branch

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) is forked from [Dana Nau's GTPyhop main branch](https://github.com/dananau/GTPyhop) and refactored for PyPI distribution, thread-safe sessions, new domain and problems file structure to facilitate LibCST parsing, new example structure to facilitate benchmarking, and documentation.

## Installation

### From PyPI (Recommended)

**GTPyhop 1.9.7** is the latest version. It closes the 1.9 minor on the "examples" theme by adding the Colt Express collection (5 sub-folders mirroring the trunk_thumper pattern catalog applied to the published board game) and extending the existing `adversarial_protocol/` sub-folder of `control_arena_protocols/` with threat-model variety, the `[EXPECTED_EFFECT]` marker (first use in this collection), and a negative-control scenario. Builds on 1.9.6's Trunk Thumper game-AI examples, Android: Netrunner run planning, cybersecurity attack planning, iterative DFS backtracking, poetry generation examples, control arena protocol examples, memory tracking, enhanced MCP orchestration examples, Opentrons Flex domains, and comprehensive style guides.

```bash
pip install gtpyhop>=1.9.7
```

For basic single-threaded planning, any version works:
```bash
pip install gtpyhop
```

[uv](https://docs.astral.sh/uv/) can of course be used if you prefer:

```bash
uv pip install gtpyhop
```

### From GitHub

Alternatively, you can directly install from a checkout. Since 2.0.0 the repository has no root `pyproject.toml` — each distribution lives under `packages/` — so install the two source packages rather than the repository root:

```bash
git clone -b pip https://github.com/PCfVW/GTPyhop.git
cd GTPyhop
pip install packages/gtpyhop-core packages/gtpyhop-examples
```

Install `packages/gtpyhop-core` alone if you want the planner without the bundled example domains. Note that `packages/gtpyhop/` is only a meta-package: it ships no source and depends on the other two *from PyPI*, so it is not the one to install from a checkout.

If you intend to modify GTPyhop or add an example, install both in editable mode instead — the two `src/` trees only merge into a single `gtpyhop` import namespace once installed:

```bash
pip install -e packages/gtpyhop-core -e packages/gtpyhop-examples
```

## Testing Your Installation

We suggest you give gtpyhop a try straight away; open a terminal and start an interactive python session:
```bash
python
```

.. and import gtpyhop to run the regression tests:

```python
# Import the main GTPyhop planning system
import gtpyhop
```

The following should be printed in your terminal:

```code
Imported GTPyhop version 1.9.7
Messages from find_plan will be prefixed with 'FP>'.
Messages from run_lazy_lookahead will be prefixed with 'RLL>'.
Using session-based architecture with structured logging.
```

Now import the regression tests module:

```python
from gtpyhop.examples import regression_tests
```

Be prepared to see a lot of information on the screen about the examples and how to solve them, with different levels of verbosity; with this in mind, run the regression tests:

```python
# Run legacy regression tests (backward compatible)
regression_tests.main()

# Or run session-based regression tests (recommended for 1.3.0+)
regression_tests.main_session()
```

The last line printed in your terminal should be:

```code
Finished without error.
```

**For GTPyhop 1.3.0+:** You can also run regression tests from the command line:

```bash
# Legacy mode
python -m gtpyhop.examples.regression_tests

# Session mode (thread-safe)
python -m gtpyhop.examples.regression_tests --session
```

Happy Planning!

## Let's HTN Start!

You have successfully installed and tested gtpyhop; it's time to declare your own planning problems in gtpyhop.

### Very First HTN Example

The key pattern is: **create a Domain** -> **define actions/methods** -> **declare them** -> **define initial state** -> **use gtpyhop.find_plan() to solve problems**.

**1. Create a Domain**

```python
import gtpyhop

# Create a Domain
gtpyhop.Domain('my_domain')
```

**2. Define Actions**

Actions are atomic operations that directly modify a state. They are Python functions where the first argument is the current `state`, and the others are the action's arguments.

```python
def my_action(state, arg1, arg2):
    # Check preconditions
    if state.pos[arg1] == arg2:
        # Modify state
        state.pos[arg1] = 'new_location'
        state.status[arg2] = 'updated'
        return state  # Success
    return False  # Failure

# Declare actions
gtpyhop.declare_actions(my_action, another_action)
```

**3. Define Task Methods**

Task methods decompose compound tasks into subtasks and actions.

```python
def method_for_task(state, arg1, arg2):
    # Check if this method is applicable
    if some_condition:
        # Return list of subtasks/actions
        return [('subtask1', arg1), ('action1', arg2)]
    return False  # Method not applicable

# Declare task methods
gtpyhop.declare_task_methods('task_name', method_for_task, alternative_method)
```

**4. Define Initial State**

```python
initial_state = gtpyhop.State('initial_state')
initial_state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}
```

**5. Complete Example**

```python
import gtpyhop

# Domain creation
gtpyhop.Domain('my_domain')

# Actions
def move(state, obj, target):
    if obj in state.pos:
        state.pos[obj] = target
        return state
    return False

gtpyhop.declare_actions(move)

# Task methods
def transport(state, obj, destination):
    current = state.pos[obj]
    if current != destination:
        return [('move', obj, destination)]
    return []

gtpyhop.declare_task_methods('transport', transport)

# Define initial state
initial_state = gtpyhop.State('initial_state')
initial_state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}

# Find plan
gtpyhop.set_verbose_level(1)
plan = gtpyhop.find_plan(initial_state, [('transport', 'obj1', 'loc2')])
print(plan)
```

Put this code in a file, say `my_very_first_htn_example.py`, and run it:

```bash
python my_very_first_htn_example.py
```

Increase the verbosity level to 2 or 3 to see more information about the planning process.

### Session-Based Version (Recommended for 1.3.0+)

For better isolation and thread safety:

```python
import gtpyhop

# Domain creation
my_domain = gtpyhop.Domain('my_domain')
state = gtpyhop.State('initial_state')
state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}

# Define actions and methods (same as above)
def move(state, obj, target):
    if obj in state.pos:
        state.pos[obj] = target
        return state
    return False

gtpyhop.declare_actions(move)

def transport(state, obj, destination):
    current = state.pos[obj]
    if current != destination:
        return [('move', obj, destination)]
    return []

gtpyhop.declare_task_methods('transport', transport)

# Use session-based planning
with gtpyhop.PlannerSession(domain=my_domain, verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, [('transport', 'obj1', 'loc2')])
        if result.success:
            print("Plan found:", result.plan)
            print("Planning stats:", result.stats)
```

### Additional Resources

Please read [Dana's additional information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md) for detailed explanations of:
- [States](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#states)
- [Actions](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#actions)
- [Tasks and task methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#3-tasks-and-task-methods)
- [Goals and goal methods](https://github.com/dananau/GTPyhop/blob/main/additional_information.md#4-goals-and-goal-methods)

## Thread-Safe Sessions (1.3.0+)

**GTPyhop 1.3.0 introduces session-based, thread-safe planning** that enables reliable concurrent execution and isolated planning contexts. This is a major architectural enhancement while maintaining 100% backward compatibility.

### Key Benefits
- **Thread-safe concurrent planning**: Multiple planners can run simultaneously
- **Isolated execution contexts**: Each session has its own configuration, logs, and statistics
- **Structured logging system**: Programmatic access to planning traces
- **Timeout management**: Built-in timeout enforcement and resource management
- **Session persistence**: Save and restore planning sessions

### Quick Start with Sessions
```python
import gtpyhop

my_domain = gtpyhop.Domain('my_domain')
# ... define actions and methods ...

with gtpyhop.PlannerSession(domain=my_domain, verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, [('transport', 'obj1', 'loc2')])
        if result.success:
            print(result.plan)
```

**For detailed documentation, see [Thread-Safe Sessions Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md)**

### Migration from Pre-1.3.0

**Existing code continues to work unchanged** - 100% backward compatible.

```python
# Before (still works)
plan = gtpyhop.find_plan(state, tasks)

# After (recommended)
with gtpyhop.PlannerSession(domain=my_domain) as session:
    with session.isolated_execution():
        result = session.find_plan(state, tasks)
        plan = result.plan if result.success else None
```

### Version Selection Guide

| Use Case | Recommended Version |
|----------|-------------------|
| **New projects** | **1.9.0+** |
| **Backtracking with iterative planner** | **1.9.0+** |
| **Memory tracking & benchmarking** | **1.8.0+** |
| **MCP integration** | **1.5.0+** |
| **Concurrent/parallel planning** | **1.3.0+** |
| **Educational/simple scripts** | Any version |

## Examples

GTPyhop includes comprehensive examples demonstrating various planning techniques. **All examples support both legacy and session modes.**

### Quick Example Run

```bash
# Legacy mode (backward compatible)
python -m gtpyhop.examples.simple_htn

# Session mode (thread-safe, recommended)
python -m gtpyhop.examples.simple_htn --session
```

**For comprehensive example documentation, see [All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)**

## Documentation

GTPyhop 1.9.7 includes comprehensive documentation organized in the `docs/` folder:

### Core Documentation
- **[All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)** - Pedagogical details about all HTN planning examples
- **[Running Examples](https://github.com/PCfVW/GTPyhop/blob/pip/docs/running_examples.md)** - Detailed instructions for executing examples
- **[Structured Logging](https://github.com/PCfVW/GTPyhop/blob/pip/docs/logging.md)** - Comprehensive logging system documentation
- **[Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md)** - Complete guide to session-based architecture
- **[Version History](https://github.com/PCfVW/GTPyhop/blob/pip/docs/changelog.md)** - Complete changelog

### Style Guides
- **[Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md)** - How to write GTPyhop examples (folder structure, required files)
- **[Domain Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_domain_style_guide.md)** - Conventions for writing domain files (actions and methods)
- **[Problems Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md)** - Conventions for writing problem files

### Example-Specific Documentation

#### IPC 2020 Total Order Domains (1.4.0+)
- **[Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/ipc-2020-total-order/benchmarking_quickstart.md)** - Performance benchmarking guide
- **[Blocksworld-GTOHP](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/ipc-2020-total-order/Blocksworld-GTOHP/ipc-2020-to-bw-gtohp-readme.md)** - IPC 2020 Blocksworld domain
- **[Childsnack](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/ipc-2020-total-order/Childsnack/ipc-2020-to-cs-gtohp-readme.md)** - IPC 2020 Childsnack domain

#### MCP Orchestration Examples (1.5.0+)
- **[MCP Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/benchmarking_quickstart.md)** - MCP orchestration benchmarking guide
- **[Bio-Opentrons PCR Workflow](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/bio_opentrons/README.md)** - PCR workflow automation (6 scenarios)
- **[Cross-Server Orchestration](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/cross_server/README.md)** - Multi-server coordination (2 scenarios)
- **[Drug Target Discovery](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/drug_target_discovery/README.md)** - OpenTargets platform integration (3 scenarios)
- **[Omega HDQ DNA Extraction](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/omega_hdq_dna_bacteria_flex_96_channel/README.md)** - DNA extraction workflow (3 scenarios)
- **[TNF Cancer Modelling](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/tnf_cancer_modelling/README.md)** - Multiscale cancer modeling (1 scenario)

#### Memory Tracking Examples (1.8.0+)
- **[Memory Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/benchmarking_quickstart.md)** - How to run memory benchmarks
- **[Memory Tracking Overview](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/README.md)** - Memory tracking capabilities with psutil
- **[Scalable Data Processing](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/scalable_data_processing/README.md)** - Memory scaling via data size (10K-1M items)
- **[Scalable Recursive Decomposition](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md)** - Memory scaling via recursion depth (2^k tasks)

#### Poetry Examples (1.9.0+)
- **[Poetry Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/benchmarking_quickstart.md)** - Batch-running scenarios across all 7 poetry sub-folders, with strategy notes for backtracking-required examples
- **[Poetry Overview](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/README.md)** - HTN-planned poetry generation with MCP delegation
- **[Structured Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/structured_poetry/README.md)** - Baseline: couplet, limerick, haiku, sonnet (6 scenarios)
- **[Backtracking Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/backtracking_poetry/README.md)** - Strict/relaxed rhyme methods with backtracking (3 scenarios)
- **[Candidate Planning Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/candidate_planning_poetry/README.md)** - Multi-candidate rhyme selection pipeline (3 scenarios)
- **[Bidirectional Planning Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/bidirectional_planning_poetry/README.md)** - Decomposed backward line construction (3 scenarios)
- **[Replanning Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/replanning_poetry/README.md)** - Post-generation evaluation and steering/revision (3 scenarios)
- **[Formal Mechanism Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/formal_mechanism_poetry/README.md)** - Three planning mechanisms from Anthropic's "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" paper (3 scenarios)
- **[Feature Space Poetry](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/feature_space_poetry/README.md)** - Feature-space interventions with measured data: Gemma 2 2B 426K (Version D) + Llama 3.2 1B 524K (Version L) + Gemma 2 2B 2.5M (Version D 2.5M) (12 scenarios)

#### Control Arena Protocol Examples (1.9.4+)

Baseline collection introduced in 1.9.4; the Adversarial Protocol sub-folder was extended in 1.9.7 (see below).

**1.9.4 baseline:**
- **[Control Arena Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/control_arena_protocols/benchmarking_quickstart.md)** - Batch-running scenarios across all three protocol examples, with outcome-label catalog and per-scenario expected-plan-length tables (added in 1.9.7)
- **[Control Arena Protocols Overview](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/control_arena_protocols/README.md)** - AI safety micro-protocols with backtracking and adversarial analysis
- **[Defer to Trusted](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/control_arena_protocols/defer_to_trusted_protocol/README.md)** - Accept or defer based on suspicion threshold (6 scenarios)
- **[Defer to Resample](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/control_arena_protocols/defer_to_resample_protocol/README.md)** - Recursive multi-sample resampling (6 scenarios)
- **[Adversarial Protocol](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/control_arena_protocols/adversarial_protocol/README.md)** - Honest vs. attack with vulnerability detection (8 scenarios, 7 actions, 7 methods)

**1.9.7 extension ([Adversarial Protocol](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/control_arena_protocols/adversarial_protocol/README.md) sub-folder only):**
- **Threat-model variety**: nested `detection_rates` schema indexed by `(threat_model, subtlety)`; 6 new scenarios across code sabotage / data poisoning / research sabotage
- **`[EXPECTED_EFFECT]` marker**: first use of the tag (introduced in `trunk_thumper/s07`, used in `colt_express/s3`) in this collection; `a_accept_output` now records downstream side-task firing via `state.side_task_observed`
- **Negative-control scenario**: 1 new scenario using teaching-variant action `a_accept_output_demo_no_expected_effect` (omits the `[EXPECTED_EFFECT]` block) to empirically demonstrate why the tag is load-bearing
- **Aggregate after extension**: Adversarial Protocol now has 8 actions, 7 methods, 15 scenarios, 92 doctests
- New `accept_no_ee` outcome label in `benchmarking.py` for the negative-control scenario (see collection README's "Benchmark Outcome Labels" section)

#### Cybersecurity Attack Planning Example (1.9.5+)
- **[Cybersecurity Attack Planning](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/cybersecurity_attack_planning/README.md)** - BAMS-based insider threat planning: physical, network, DMS, and malware attacks with 5 backtracking points (9 scenarios)

#### Android: Netrunner Run Planning Example (1.9.6+)
- **[Android: Netrunner Run Planning](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/android_netrunner/README.md)** - Per-card-fidelity run planning based on the published Android: Netrunner rules (2012 core set); 14 named cards, 24 actions, 6 backtracking points, 8 scenarios — flagship scenario replicates the worked example on page 19 of the core rulebook

#### Trunk Thumper Game-AI Examples (1.9.6+)
- **[Trunk Thumper Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/trunk_thumper/benchmarking_quickstart.md)** - Batch-running scenarios across all sub-folders
- **[Trunk Thumper Collection Overview](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/trunk_thumper/README.md)** - Progressive game-AI tutorial collection based on Troy Humphreys' canonical *Game AI Pro* chapter (2015); sub-folder naming `sNN_<topic>` matches chapter section §12.NN
- **[s03 Basic Attack or Patrol](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/trunk_thumper/s03_basic_attack_or_patrol/README.md)** - §12.3 baseline BeTrunkThumper domain (2 scenarios)
- **[s06 Recursive Trunk Replacement](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/trunk_thumper/s06_recursive_trunk_replacement/README.md)** - §12.6 recursion via m_attack_enemy self-call (3 scenarios)
- **[s07 Expected Effects Chase](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/trunk_thumper/s07_expected_effects_chase/README.md)** - §12.7 the new `[EXPECTED_EFFECT]` tag with a negative-control scenario (3 scenarios)
- **[s08 Priority Methods](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/trunk_thumper/s08_priority_methods/README.md)** - §12.8 multi-method m_attack_enemy with WsPowerUp/WsIsTired/boulder-fallback (4 scenarios)
- **[s09 Simultaneous Navigation and Guard](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/trunk_thumper/s09_simultaneous_navigation_and_guard/README.md)** - §12.9 single-planner non-blocking navigation with guard (3 scenarios)
- **[s10 Partial Plans](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/trunk_thumper/s10_partial_plans/README.md)** - §12.10 manual method-split partial plans (3 scenarios)

#### Colt Express Game-AI Examples (1.9.7+)
- **[Colt Express Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/colt_express/benchmarking_quickstart.md)** - Batch-running scenarios across all sub-folders with per-scenario expected-plan-length table
- **[Colt Express Collection Overview](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/colt_express/README.md)** - Colt Express board game (Raimbault/Valbuena, Ludonaute 2014) as a multi-bandit / Marshal-driven Stealin'-only HTN example; mirrors trunk_thumper's pattern catalog at higher fidelity (5 sub-folders, 26 actions, 16 scenarios, 124 doctests)
- **[s1 Minimal Turn](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/colt_express/s1_minimal_turn/README.md)** - Baseline priority methods: rob-if-loot vs. move-forward (3 scenarios) — pattern source: trunk_thumper s03
- **[s3 Marshal Expected Effects](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/colt_express/s3_marshal_expected_effects/README.md)** - Marshal forced-escape via `[EXPECTED_EFFECT]` tag with negative-control scenario (3 scenarios incl. 1 intentional fail) — pattern source: trunk_thumper s07
- **[s2 Recursive Round](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/colt_express/s2_recursive_round/README.md)** - Recursive deck resolution via `state.deck` head-pop, plus hostage-taking event (3 scenarios) — pattern source: trunk_thumper s06
- **[s4 Character Priorities](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/colt_express/s4_character_priorities/README.md)** - Priority-method ladder for Belle / Tuco / Django / Cheyenne abilities (4 scenarios) — pattern source: trunk_thumper s08
- **[s5 Partial Plan Movement](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/colt_express/s5_partial_plan_movement/README.md)** - Manual method-split partial plans for movement strategy (3 scenarios) — pattern source: trunk_thumper s10

### External Resources
- **[Dana's Additional Information](https://github.com/dananau/GTPyhop/blob/main/additional_information.md)** - Core GTPyhop concepts

## New Features

### Planning Strategies

GTPyhop supports three planning strategies, selectable via `set_recursive_planning` or the `PlannerSession(strategy=...)` parameter:

| Strategy | Backtracking? | Stack | Activation |
|----------|:------------:|-------|------------|
| **Iterative greedy** (default) | No | Explicit stack | `set_recursive_planning(False)` |
| **Recursive DFS** | Yes | Python call stack | `set_recursive_planning(True)` |
| **Iterative DFS BT** (1.9.0+) | Yes | Explicit stack | `set_recursive_planning("iterative_dfs_backtracking")` |

The **iterative greedy** strategy (default since 1.2.0) commits to the first applicable method and never reconsiders that choice. The **recursive DFS** strategy backtracks across methods via the Python call stack. The **iterative DFS backtracking** strategy (new in 1.9.0) combines the iterative planner's explicit stack with the recursive planner's ability to backtrack — it pushes all applicable method continuations onto the stack, so if one path fails, alternatives remain.

```python
# Global API
gtpyhop.set_recursive_planning(False)                        # iterative greedy (default)
gtpyhop.set_recursive_planning(True)                         # recursive DFS
gtpyhop.set_recursive_planning("iterative_dfs_backtracking") # iterative DFS with backtracking

# Session API (1.9.0+)
with gtpyhop.PlannerSession(domain=d, strategy="iterative_dfs_backtracking") as s:
    result = s.find_plan(state, tasks)
```

All existing `True`/`False` callers continue to work identically. See the [changelog](https://github.com/PCfVW/GTPyhop/blob/pip/docs/changelog.md) for full details.

### New Functions by Version

**1.9.0 (Iterative DFS Backtracking)**
- `seek_plan_iterative_backtracking` - Iterative DFS with full backtracking via explicit stack
- `_refine_task_and_continue_iterative_bt` - Multi-continuation task refinement
- `_refine_unigoal_and_continue_iterative_bt` - Multi-continuation unigoal refinement
- `_refine_multigoal_and_continue_iterative_bt` - Multi-continuation multigoal refinement
- `PlannerSession(strategy=...)` - Strategy selection parameter (`"recursive_dfs"`, `"iterative_greedy"`, `"iterative_dfs_backtracking"`)

**1.4.0 (Robustness & Benchmarking)**
- `validate_plan_from_goal` - Plan validation from initial to goal state
- `PlannerBenchmark` - Comprehensive benchmarking with resource tracking

**1.3.0 (Thread-Safe Sessions)**
- `PlannerSession` - Isolated, thread-safe planning context
- `create_session`, `get_session`, `destroy_session`, `list_sessions`
- `SessionSerializer`, `restore_session` - Session persistence

**1.2.1 (Iterative Planning)**
- `set_recursive_planning`, `get_recursive_planning`
- `seek_plan_iterative` and related iterative functions

## Project Structure

```
GTPyhop/
├── LICENSE.txt
├── README.md
├── docs/
│   ├── all_examples.md
│   ├── changelog.md
│   ├── gtpyhop_domain_style_guide.md
│   ├── gtpyhop_example_style_guide.md
│   ├── gtpyhop_problems_style_guide.md
│   ├── logging.md
│   ├── running_examples.md
│   └── thread_safe_sessions.md
└── packages/                     # one folder per published distribution
    ├── gtpyhop-core/             # the planner, no bundled examples
    │   ├── README.md
    │   ├── pyproject.toml
    │   └── src/gtpyhop/
    │       ├── __init__.py
    │       ├── main.py
    │       ├── logging_system.py
    │       ├── memory_tracking/
    │       │   ├── __init__.py
    │       │   ├── monitor.py
    │       │   └── tracker.py
    │       └── test_harness/
    │           ├── __init__.py
    │           └── test_harness.py
    ├── gtpyhop/                  # meta-package: depends on gtpyhop-core and
    │   ├── README.md             #   gtpyhop-examples; ships no source of its own
    │   └── pyproject.toml
    ├── gtpyhop-diagnostics/      # optional add-on, versioned independently:
    │   ├── README.md             #   names the precondition that blocked a plan
    │   ├── pyproject.toml
    │   └── src/gtpyhop/diagnostics/
    │       ├── __init__.py
    │       ├── guards.py         # domain source -> candidate preconditions
    │       └── explain.py        # joins those with the trace's state snapshot
    └── gtpyhop-examples/         # the example domains
        ├── README.md
        ├── pyproject.toml
        └── src/gtpyhop/examples/
            ├── regression_tests.py
            ├── simple_htn.py, simple_hgn.py, ...
            ├── blocks_htn/, blocks_hgn/, blocks_gtn/, blocks_goal_splitting/
            ├── ipc-2020-total-order/
            │   └── Blocksworld-GTOHP/, Childsnack/
            ├── mcp-orchestration/
            │   └── bio_opentrons/, cross_server/, drug_target_discovery/, omega_hdq_dna_bacteria_flex_96_channel/, tnf_cancer_modelling/
            ├── memory_tracking/
            │   └── scalable_data_processing/, scalable_recursive_decomposition/
            ├── poetry/
            │   └── structured_poetry/, backtracking_poetry/, candidate_planning_poetry/, bidirectional_planning_poetry/, replanning_poetry/, formal_mechanism_poetry/, feature_space_poetry/
            ├── cybersecurity_attack_planning/
            ├── android_netrunner/
            ├── control_arena_protocols/
            ├── trunk_thumper/
            │   ├── s03_basic_attack_or_patrol/, s06_recursive_trunk_replacement/, s07_expected_effects_chase/, s08_priority_methods/, s09_simultaneous_navigation_and_guard/, s10_partial_plans/
            └── colt_express/
                ├── s1_minimal_turn/, s3_marshal_expected_effects/, s2_recursive_round/, s4_character_priorities/, s5_partial_plan_movement/
```

`gtpyhop-core` and `gtpyhop-examples` both install into the same `gtpyhop` import namespace, which is why each keeps its own `src/gtpyhop/` tree: once installed they merge, so `import gtpyhop` and `import gtpyhop.examples` work exactly as they did before 2.0.
