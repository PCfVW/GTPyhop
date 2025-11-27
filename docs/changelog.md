# GTPyhop Version History

## 1.5.0 — Two new examples & Robustness (Latest, Recommended)
**Soon uploaded to PyPI: https://pypi.org/project/gtpyhop/1.5.0/**

🚀 **Major Features:**
- **🔒 Robustness** - Comprehensive code review and testing
- **🌐 MCP Orchestration Examples** - Cross-server coordination and scientific workflows

**MCP Orchestration Documentation:**
- **[Cross-Server Orchestration →](https://github.com/PCfVW/GTPyhop/blob/pip/src/gtpyhop/examples/mcp-orchestration/cross_server/README.md)** - Multi-server robot coordination (9 actions, 5 methods)
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
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/**
- First PyPI distribution
- Iterative planning strategy introduction
- Domain management utilities
