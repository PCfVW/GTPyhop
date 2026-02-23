# GTPyhop Version History

## 1.9.2 — Feature Space Poetry: Word-Level CLT 2.5M Scenarios (Latest, Recommended)

**Feature Space Poetry** expanded from 8 to **12 scenarios** with the addition of 4 Gemma 2 2B + CLT 2.5M (Version D 2.5M) scenarios:

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 8: 2.5M star result | Ground truth (out→an, "can" at 48.2%) | 34 | No | SUCCESS |
| 9: 2.5M weakest first | "plan" before "can" | 34 | Yes (2 failures) | **FAIL** |
| 10: 2.5M planning layer | Only L25 encoded | 9 | No | SUCCESS |
| 11: 2.5M different group | oo→an, lower threshold | 10 | Yes (1 failure) | **FAIL** |

**Key upgrade over 426K CLT:** 2.5M CLT provides 98,304 features/layer (vs 16,384), giving word-level resolution — 209/209 words ranked #1 in their own dedicated feature. The star result "can" (L25:82839) achieved 48.2% redirect probability with a 160-billion-fold spike. Same Gemma 2 2B model, finer CLT = word-level control.

**Feature Space Poetry now covers three configurations:**

| Configuration | Scenarios | Layers | CLT Resolution | Star Result |
|---------------|-----------|--------|----------------|-------------|
| Gemma 2 2B (Version D) | 0-3 | 26 | 426K | "around" at 48.3% |
| Llama 3.2 1B (Version L) | 4-7 | 16 | 524K | "that" at 77.7% |
| Gemma 2 2B (Version D 2.5M) | 8-11 | 26 | 2.5M | "can" at 48.2% |

**Documentation updates:**
- **[All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)** — Updated Feature Space Poetry section (8→12 scenarios, added 2.5M scenario table)
- **[Poetry README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/README.md)** — Updated scenario counts, strategy table, directory structure; added 2.5M scenario table
- **[Poetry Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/benchmarking_quickstart.md)** — Updated expected results with all 12 scenarios; updated troubleshooting
- **[Feature Space Poetry README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/feature_space_poetry/README.md)** — Added 2.5M scenarios, empirical grounding, decomposition examples; updated domain statistics

**Compatibility:** 100% backward compatible with GTPyhop 1.9.1. No API changes.

---

## 1.9.1 — Poetry Examples & Bug Fixes

🚀 **Major Features:**
- **🔀 Iterative DFS Backtracking** - Third planning strategy combining the iterative planner's explicit stack with full backtracking across methods
- **📝 Poetry Examples** - Seven poetry generation domains demonstrating structured, backtracking, candidate planning, bidirectional, replanning, formal mechanism, and feature-space HTN planning

**Iterative DFS Backtracking:**

GTPyhop 1.8.0 provided two planning strategies: recursive DFS (backtracks via Python call stack) and iterative greedy (commits to first applicable method, no backtracking). The iterative greedy planner could not recover when a chosen method's subtasks failed downstream.

GTPyhop 1.9.1 adds a third strategy — **iterative DFS with backtracking** — that pushes all applicable method continuations onto an explicit stack. If one path fails, the planner falls back to the next alternative. This provides the same correctness as recursive DFS without Python's recursion depth limit.

| Strategy | Backtracking? | Stack | Activation |
|----------|:------------:|-------|------------|
| Recursive DFS | Yes | Python call stack | `set_recursive_planning(True)` |
| Iterative greedy | No | Explicit stack | `set_recursive_planning(False)` |
| **Iterative DFS BT** | **Yes** | **Explicit stack** | `set_recursive_planning("iterative_dfs_backtracking")` |

**New Internal Functions (purely additive — no existing function removed or modified):**
- `seek_plan_iterative_backtracking` - Main iterative loop with multi-continuation stack
- `_refine_task_and_continue_iterative_bt` - Returns all applicable task method continuations
- `_refine_unigoal_and_continue_iterative_bt` - Returns all applicable unigoal method continuations
- `_refine_multigoal_and_continue_iterative_bt` - Returns all applicable multigoal method continuations

**API Changes (backward-compatible):**
- **`set_recursive_planning(strategy)`** - Now accepts string values in addition to `True`/`False`:
  - `"recursive_dfs"` (same as `True`)
  - `"iterative_greedy"` or `"iterative_irrevocable_commitment"` (same as `False`)
  - `"iterative_dfs_backtracking"` (new)
  - Existing `True`/`False` callers are unaffected (`isinstance(strategy, bool)` dispatch)
- **`PlannerSession(strategy=...)`** - New optional keyword parameter:
  - `PlannerSession(strategy="iterative_dfs_backtracking")` activates the new strategy
  - When `strategy` is `None` (default), the existing `recursive` bool parameter drives behavior identically to 1.8.0
  - `PlannerSession.recursive` is now a derived property (`self._strategy == "recursive_dfs"`)
- **`PlannerSession.isolated_execution()`** - Restore logic simplified to direct function reference assignment, correctly handling all three strategies
- **`SessionSerializer`** - Serialization includes the `strategy` field; deserialization falls back to `recursive` bool for data from older versions
- **Result stats `"strategy"` field** - Now reports the full strategy name (`"recursive_dfs"`, `"iterative_greedy"`, or `"iterative_dfs_backtracking"`) instead of the previous binary `"recursive"` / `"iterative"`

**Usage Examples:**
```python
# Global API
import gtpyhop
gtpyhop.set_recursive_planning("iterative_dfs_backtracking")
plan = gtpyhop.find_plan(state, tasks)

# Session API
with gtpyhop.PlannerSession(
    domain=my_domain,
    strategy="iterative_dfs_backtracking"
) as session:
    result = session.find_plan(state, tasks)
```

**New Examples:**

The seven poetry examples form a progression, each extending the baseline with a different aspect of Anthropic's "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" (March 2025) findings:

| # | Example | Directory | Description | Strategy |
|---|---------|-----------|-------------|----------|
| 1 | **Structured Poetry** | `poetry/structured_poetry/` | Baseline: select → generate → verify (6 scenarios) | Any |
| 2 | **Backtracking Poetry** | `poetry/backtracking_poetry/` | Strict/relaxed methods with backtracking (3 scenarios) | Backtracking |
| 3 | **Candidate Planning Poetry** | `poetry/candidate_planning_poetry/` | Multi-candidate rhyme selection pipeline (3 scenarios) | Any |
| 4 | **Bidirectional Planning Poetry** | `poetry/bidirectional_planning_poetry/` | Decomposed backward line construction (3 scenarios) | Any |
| 5 | **Replanning Poetry** | `poetry/replanning_poetry/` | Post-generation evaluation and steering/revision (3 scenarios) | Backtracking |
| 6 | **Formal Mechanism Poetry** | `poetry/formal_mechanism_poetry/` | Three planning mechanisms from Anthropic's [paper](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems) (3 scenarios) | Any |
| 7 | **Feature Space Poetry** | `poetry/feature_space_poetry/` | Feature-space interventions with measured data: Gemma 2 2B (Version D) + Llama 3.2 1B (Version L) (8 scenarios) | Backtracking |

- **Backtracking Poetry** (example 2) — Tests action-level failure triggering method-level backtracking at the line composition level:

| Strategy | Couplet (8) | Limerick (17) | Haiku (8) |
|----------|:-------:|:--------:|:-----:|
| Recursive DFS | 8 actions | 17 actions | 8 actions |
| Iterative greedy | 8 actions | **Fails** | 8 actions |
| Iterative DFS BT | 8 actions | 17 actions | 8 actions |

- **Replanning Poetry** (example 5) — Tests action-level failure triggering method-level backtracking at the evaluation level. Models the paper's finding that injecting an alternative planned word causes the model to restructure the entire line in 70% of test poems:

| Strategy | Couplet (12) | Limerick (28) | Haiku (8) |
|----------|:-------:|:--------:|:-----:|
| Recursive DFS | 12 actions | 28 actions | 8 actions |
| Iterative greedy | **Fails** | **Fails** | 8 actions |
| Iterative DFS BT | 12 actions | 28 actions | 8 actions |

- **Candidate Planning Poetry** (example 3) — Replaces single rhyme target selection with a 3-action pipeline (generate candidates → rank → commit). Plan lengths: Couplet: 12, Limerick: 27, Haiku: 8.

- **Bidirectional Planning Poetry** (example 4) — Splits line generation into backward transition planning and forward surface text generation. Plan lengths: Couplet: 10, Limerick: 22, Haiku: 8.

- **Formal Mechanism Poetry** (example 6) — Implements three planning mechanisms from the paper (full pipeline, commitment focus, three-stage). All 3 scenarios succeed with any strategy. Plan lengths: 19, 7, 13.

- **Feature Space Poetry** (example 7) — Probability-based evaluation using measured experimental data. Eight scenarios across two models: Gemma 2 2B (Version D, 4 scenarios) and Llama 3.2 1B (Version L, 4 scenarios). Each model has a ground truth replication plus counterfactual what-ifs. Scenarios requiring backtracking fail with the greedy strategy:

| Strategy | Gemma S0 (34) | Gemma S1 (34) | Gemma S2 (9) | Gemma S3 (10) | Llama S4 (24) | Llama S5 (24) | Llama S6 (9) | Llama S7 (10) |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Iterative DFS BT | 34 | 34 | 9 | 10 | 24 | 24 | 9 | 10 |
| Iterative greedy | 34 | **Fails** | 9 | **Fails** | 24 | **Fails** | 9 | **Fails** |

**Poetry benchmarking script** updated with `--strategy` option:
```bash
cd src/gtpyhop/examples/poetry
python benchmarking.py structured_poetry                                    # default strategy
python benchmarking.py backtracking_poetry --strategy recursive_dfs         # requires backtracking
python benchmarking.py replanning_poetry --strategy iterative_dfs_backtracking  # requires backtracking
python benchmarking.py formal_mechanism_poetry                                 # works with any strategy
python benchmarking.py feature_space_poetry --strategy iterative_dfs_backtracking  # requires backtracking
```

**Documentation & Style Guides:**
- **[All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)** — Updated with examples 6-7 (sections, summary table, benchmarking commands)
- **[Poetry README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/README.md)** — Updated with examples 6-7 (tables, directory structure, server architectures); fixed example 6 strategy classification (Backtracking → Any); added comprehensive MCP section (Why MCP?, server configurations, MCP reference summary)
- **[Poetry Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/benchmarking_quickstart.md)** — Updated with examples 6-7 (expected results, troubleshooting, strategy tables)
- **[Feature Space Poetry README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/poetry/feature_space_poetry/README.md)** — Added Llama 3.2 1B scenarios (4-7); fixed server architecture (suppress_group moved to clt_server); fixed method count (5, not 7); added Appendix on state restoration and backtrack with MI and AI planning implications
- **[Problems Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md)** — v2.2.0: added section 2.3 on doctests in `get_problems()` with template and conventions
- **[Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md)** — v1.2.0: added section 7 on doctests for plan verification; updated checklist and quick start template

**Bug Fixes:**
- Fixed Unicode encoding issue in IPC benchmarking `print_summary`: replaced non-ASCII characters (Delta, checkmark, cross) with ASCII equivalents for Windows cp1252 compatibility
- Fixed `--verbose` flag handling in poetry `benchmarking.py` (was not being passed to planner sessions)
- Added plan validation to poetry benchmarking (verifies plan is a list, not just truthy)

**Compatibility:** 100% backward compatible with GTPyhop 1.8.0. All existing `True`/`False` callers produce identical behavior.

---

## 1.8.0 — Memory Tracking & Scalability Examples
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.8.0/**

🚀 **Major Features:**
- **📊 Memory Tracking** - Real-time memory monitoring during planning with `psutil`
- **🔬 Scalability Examples** - Two new examples demonstrating HTN planning complexity
- **⚡ Zero-Overhead Design** - Memory tracking has no overhead when disabled

**Memory Tracking Architecture:**
- **`ResourceManager`** - Singleton manager for memory monitoring
  - `ResourceManager.reset()` - Clear all cached state for fresh benchmarking
  - `ResourceManager.sample_memory()` - Explicit memory sampling for fast operations
- **`MemoryMonitor`** - Background thread for continuous memory sampling
  - Configurable sampling interval (default 0.1s, use 0.001s for fast scenarios)
  - `sample_now()` - Force immediate memory sample
  - `stop()` - Fully terminate monitoring thread
- **`PlannerSession` Integration** - New parameters:
  - `memory_tracking=True` - Enable memory monitoring
  - `memory_sampling_interval=0.001` - Set sampling interval in seconds
- **Session Statistics** - New result fields:
  - `result.stats['memory_mb']` - Memory used during planning
  - `result.stats['peak_memory_mb']` - Peak memory observed

**New Examples:**

| Example | Directory | Description |
|---------|-----------|-------------|
| **Scalable Data Processing** | `memory_tracking/scalable_data_processing/` | Memory scaling via data size (10K-1M items) |
| **Scalable Recursive Decomposition** | `memory_tracking/scalable_recursive_decomposition/` | Memory scaling via recursion depth (2^k tasks) |

- **Scalable Data Processing** - 20 scenarios testing data types, transforms, and accumulation
  - Data types: `int` (~28 bytes), `string` (~500 bytes), `dict` (~1KB+)
  - Configurable: `num_transforms`, `accumulate`, `cleanup`
  - Memory range: 1 MB to 300+ MB

- **Scalable Recursive Decomposition** - 12 scenarios based on Alford et al. (2015) Theorem 4.1
  - Binary recursive decomposition: depth k yields 2^k leaf tasks
  - Demonstrates PSPACE-complete HTN planning complexity
  - Payload scaling: 100B to 100KB per task
  - Memory formula: `2^depth × payload_size`

**Benchmarking Script:**
```bash
cd src/gtpyhop/examples/memory_tracking

# Run data processing scenarios
python benchmarking.py --example data

# Run recursive decomposition scenarios
python benchmarking.py --example recursive

# Accurate peak measurement (recommended)
python benchmarking.py --example recursive --scenario scenario_10 \
    --disable-gc --sampling-interval 0.001
```

**Command-Line Options:**
- `--example {data,recursive}` - Select example type
- `--scenario NAME` - Run specific scenario
- `--disable-gc` - Disable garbage collection during planning
- `--sampling-interval FLOAT` - Memory sampling interval (default: 0.1)
- `--list-scenarios` - List available scenarios
- `--performance-test` - Compare overhead with/without memory tracking

**Usage Example:**
```python
from gtpyhop import PlannerSession
from gtpyhop.examples.memory_tracking.scalable_recursive_decomposition import (
    the_domain, get_problems
)

problems = get_problems()
state, tasks, description = problems['scenario_10']

with PlannerSession(
    domain=the_domain,
    memory_tracking=True,
    memory_sampling_interval=0.001
) as session:
    result = session.find_plan(state, tasks)

    if result.success:
        print(f"Plan: {len(result.plan)} actions")
        print(f"Peak memory: {result.stats['peak_memory_mb']:.2f} MB")
```

**Requirements:**
- Python 3.8+
- `psutil>=5.8.0` (automatically installed with GTPyhop from PyPI)

(https://github.com/PCfVW/GTPyhop/blob/pip/

**Documentation:**
- [Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md) - How to write GTPyhop examples
- [Memory Tracking README](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/README.md)
- [Benchmarking Quick Start](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/benchmarking_quickstart.md)
- [Scalable Data Processing](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_data_processing/README.md)
- [Scalable Recursive Decomposition](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md)

**References:**
- Ron Alford, Pascal Bercher, & David Aha (2015). ["Tight Bounds for HTN Planning."](https://ojs.aaai.org/index.php/ICAPS/article/view/13721) 25th ICAPS, pp. 7-15. [Video Recording](https://www.icaps-conference.org/recording/tight-bounds-for-htn-planning/)

---

## 1.7.0 — MCP Orchestration Enhancements & Consistency Updates
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.7.0/**

🚀 **Major Features:**
- **🔧 Bug Fixes** - Fixed critical planning issues in MCP orchestration examples
- **📖 Documentation Consistency** - Comprehensive consistency pass on all README files and benchmarking documentation
- **✅ Validation** - All 5 MCP orchestration examples now pass benchmarking tests
- **🧪 New Example** - Added `drug_target_discovery` domain for OpenTargets platform integration

**MCP Orchestration Fixes:**
- **cross_server** - Fixed multi-object transfer scenario (scenario_2_multi_transfer)
  - Fixed `m_pick_object` method to conditionally open gripper only when needed
  - Removed incorrect gripper state precondition that prevented sequential pick operations
  - Updated `__init__.py` to properly delegate to `problems.get_problems()`
  - Corrected action counts: scenario_2 now produces 15 actions (was incorrectly showing 9)
- **drug_target_discovery** - Fixed method declarations and module structure
  - Created missing `__init__.py` file with proper exports
  - Fixed all `declare_task_methods()` calls to use `m_` prefix for task names
  - Fixed task decomposition to use `m_` prefix for method calls
  - All 3 scenarios now produce correct 8-action plans
- **tnf_cancer_modelling** - Fixed `__init__.py` to delegate to `problems.get_problems()`
- **bio_opentrons** - Fixed problems.py task name prefixes (was missing `m_` prefix)

**Documentation Updates:**
- **README Consistency Pass** - Updated all 5 MCP orchestration example READMEs:
  - bio_opentrons: Fixed scenario counts (7→6) and action counts
  - drug_target_discovery: Fixed action counts (10→8), removed duplicate sections
  - omega_hdq_dna_bacteria_flex_96_channel: Updated generation date
  - cross_server: Updated action counts for scenario_2 (18→15)
  - All READMEs now match actual benchmark results
- **benchmarking_quickstart.md** - Complete rewrite to match actual implementation:
  - Fixed command-line flags (`--mode session` → `--legacy-mode`)
  - Updated planning mode descriptions (session is now default, not legacy)
  - Replaced example outputs with actual benchmarking script format
  - Added detailed column descriptions (Status, Plan Len, Time, CPU %, Mem Δ, Peak Mem)
  - Fixed all scenario and action counts to match reality

**Benchmarking Improvements:**
- **Thread-Safe Sessions by Default** - All benchmarks now use `PlannerSession` by default
  - Legacy mode available via `--legacy-mode` flag
  - Displays "Thread-Safe Sessions" in benchmark output
  - All 5 examples verified to run with thread-safe sessions
- **Problem Discovery** - All `__init__.py` files now properly delegate to `problems.get_problems()`
  - Ensures consistency between problem definitions and benchmarking
  - Prevents overriding of problem scenarios

**Testing & Validation:**
- All 5 MCP orchestration examples pass benchmarking:
  - bio_opentrons: 6 scenarios (55-611 actions) ✅
  - omega_hdq_dna_bacteria_flex_96_channel: 3 scenarios (89-129 actions) ✅
  - drug_target_discovery: 3 scenarios (8 actions each) ✅
  - tnf_cancer_modelling: 1 scenario (12 actions) ✅
  - cross_server: 2 scenarios (9, 15 actions) ✅

**File Structure Updates:**
- Added `drug_target_discovery/__init__.py`
- Updated file tree in README.md to include drug_target_discovery
- Renamed `docs/gtpyhop_actions_methods_style_guide.md` → `docs/gtpyhop_domain_style_guide.md` (better reflects content)

**Style Guide Updates:**
- **Domain Style Guide** (formerly "Actions and Methods Style Guide")
  - Renamed to better reflect that it covers the entire domain file
  - Updated to version 1.1.0
  - Updated all references in documentation
- **Problems Style Guide**
  - Updated to version 2.1.0
  - Consistent with GTPyhop 1.7.0

## 1.6.0 — Two new examples & Two new style guides
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.6.0/**

🚀 **Major Features:**
- **📖 Documentation** - `domain.py` and `problems.py` style guides
- **🌐 MCP Orchestration Opentrons Flex Examples** - Omega HDQ 96-channel and PCR Workflow Automation with dynamic sample scaling (4 to 96 samples)

**Opentrons Flex Examples Documentation:**
- **[PCR Workflow Automation →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/bio_opentrons/README.md)** - Multi-server robot coordination for Polymerase Chain Reaction (PCR) workflow automation (3 servers, 18 actions, 15 methods)
- **[Omega HDQ 96-channel →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/omega_hdq_dna_bacteria_flex_96_channel/README.md)** - Multi-server robot coordination for DNA extraction (3 servers, 17 actions, 14 methods)

[Opentrons Flex](https://en.wikipedia.org/wiki/Opentrons) is a modular liquid handling robot platform.

## 1.5.1 — Documentation Fixes
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.5.1/**

🚀 **Changes:**
- **📖 Documentation** - Fixed missing version update in README.md
- **🔧 PyPI Badge** - Added PyPI version badge to README.md (fixed typo: gtpythop → gtpyhop)

## 1.5.0 — Two new examples & Robustness

🚀 **Major Features:**
- **🔒 Robustness** - Comprehensive code review and testing
- **🌐 MCP Orchestration Examples** - Cross-server coordination and scientific workflows

**MCP Orchestration Documentation:**
- **[Cross-Server Orchestration →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/cross_server/README.md)** - Multi-server robot coordination (2 servers, 9 actions, 5 methods)
- **[TNF Cancer Modelling →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/tnf_cancer_modelling/README.md)** - Multiscale biological modeling (12 actions, 3 methods)
- **[MCP Benchmarking →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/benchmarking_quickstart.md)** - Performance benchmarking for MCP domains

**MCP** stands for [Model Context Protocol](https://modelcontextprotocol.io/), [an open-source standard from Anthropic](https://www.anthropic.com/news/model-context-protocol/) for connecting AI applications to external systems.

## 1.4.0 — Robustness, Validation & Benchmarking
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.4.0/**

🚀 **Major Features:**
- **🔒 Robustness** - Explicit state copying when applying actions
- **❌ No-op Detection** - When applied, idempotent actions are detected and skipped
- **🔧 IPC 2020 Total Order Domains** - Blocksworld-GTOHP and Childsnack
- **📖 Documentation** - Reorganized, updated and expanded documentation for many features
- **📈 Resource monitoring for Benchmarking** - Memory (Total and Peak Kb) and CPU usage (%) tracking

**IPC 2020 Total Order Documentation:**
- **[Benchmarking documentation →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/benchmarking_quickstart.md)**
- **[Blocksworld-GTOHP documentation →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/Blocksworld-GTOHP/ipc-2020-to-bw-gtohp-readme.md)**
- **[Childsnack documentation →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/ipc-2020-total-order/Childsnack/ipc-2020-to-cs-gtohp-readme.md)**

## 1.3.0 — Thread-Safe Sessions
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.3.0/**

**Major Features:**
- **🔒 Thread-safe session-based architecture** - Reliable concurrent planning
- **⏱️ Timeout management** - Built-in timeout enforcement and resource management
- **💾 Session persistence** - Save and restore planning sessions
- **📊 Structured logging** - Programmatic access to planning logs and statistics
- **🔧 Enhanced error handling** - Graceful degradation and comprehensive error reporting
- **📚 Complete example migration** - All 10 examples support both legacy and session modes

**Examples Migration Status:** ✅ **Complete** - All examples now support dual-mode execution:
- 6 simple examples: `simple_htn`, `simple_hgn`, `backtracking_htn`, `simple_htn_acting_error`, `logistics_hgn`, `pyhop_simple_travel_example`
- 4 complex block world examples: `blocks_htn`, `blocks_hgn`, `blocks_gtn`, `blocks_goal_splitting`
- Unified command-line interface: `--session`, `--verbose N`, `--no-pauses`
- Comprehensive test coverage: 9/9 examples pass in both legacy and session modes

**Compatibility:** 100% backward compatible with GTPyhop v1.2.1

**When to use:** New projects, concurrent planning, production systems, web APIs

📖 **[Complete 1.3.0 Thread‑Safe Sessions documentation →](thread_safe_sessions.md)**

---

## 1.2.1 — Cosmetics & Documentation
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.2.1/**
- Documentation improvements and bug fixes
- Enhanced README with examples
- Iterative planning strategy refinements

## 1.2.0 — Initial PyPI Release
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.2.0/**
- First PyPI distribution
- Iterative planning strategy introduction
- Domain management utilities
