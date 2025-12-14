# GTPyhop Version History

## 1.7.0 — MCP Orchestration Enhancements & Consistency Updates (Latest, Recommended)
**In Development**

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

## 1.6.0 — Documentation Fixes
**Soon uploaded to PyPI: https://pypi.org/project/gtpyhop/1.6.0/**

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
