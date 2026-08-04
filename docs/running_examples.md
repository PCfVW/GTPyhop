# Running GTPyhop Examples

GTPyhop includes comprehensive examples demonstrating various planning techniques. **All examples support both legacy and session modes** for maximum flexibility and thread safety.

## Running Examples

**All examples support dual-mode execution:**

```bash
# Legacy mode (backward compatible)
python -m gtpyhop.examples.simple_htn

# Session mode (thread-safe, recommended for 1.3.0+)
python -m gtpyhop.examples.simple_htn --session

# Session mode with custom verbosity and no pauses
python -m gtpyhop.examples.simple_htn --session --verbose 2 --no-pauses
```

**Command-line arguments (available in all migrated examples):**
- `--session`: Enable thread-safe session mode
- `--verbose N`: Set verbosity level (0-3, default: 1 in session mode)
- `--no-pauses`: Skip interactive pauses for automated testing

## Available Examples

### Simple Examples (Basic concepts and techniques)

| Example | Description | Key Features |
|---------|-------------|--------------|
| `simple_htn.py` | Basic hierarchical task networks | HTN planning, verbosity levels, execution |
| `simple_hgn.py` | Basic hierarchical goal networks | HGN planning, goal-oriented tasks |
| `backtracking_htn.py` | Backtracking demonstration | Method failure handling, alternative paths |
| `simple_htn_acting_error.py` | Error handling patterns | Execution failures, replanning |
| `logistics_hgn.py` | Logistics domain planning | Multi-goal planning, transportation |
| `pyhop_simple_travel_example.py` | Travel planning | Basic domain modeling |

### Complex Block World Examples (Advanced planning scenarios)

| Example | Description | Key Features |
|---------|-------------|--------------|
| `blocks_htn/` | Hierarchical task networks | Complex HTN methods, block manipulation |
| `blocks_hgn/` | Hierarchical goal networks | Goal decomposition, multigoals |
| `blocks_gtn/` | Goal task networks | Mixed task/goal planning |
| `blocks_goal_splitting/` | Goal splitting methodology | Built-in goal decomposition methods |

### IPC 2020 Total Order Planning Problems

Two examples from the IPC 2020 Total Order track:

| Example | Description | Key Features |
|---------|-------------|--------------|
| `Blocksworld-GTOHP/` | Classic blocks world | HTN planning, stacking, multigoals |
| `Childsnack/` | Resource management in childcare setting | HTN planning, constraint handling, multigoals |

Location: `packages/gtpyhop-examples/src/gtpyhop/examples/ipc-2020-total-order/`

**Documentation:** [Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/ipc-2020-total-order/benchmarking_quickstart.md)

### MCP Orchestration Examples (1.5.0+)

Six examples demonstrating MCP (Model Context Protocol) orchestration:

| Example | Description | Scenarios | Actions |
|---------|-------------|-----------|---------|
| `bio_opentrons/` | PCR workflow automation with Opentrons Flex | 6 | 18 |
| `cross_server/` | Cross-server HTN plan execution | 2 | 9 |
| `drug_target_discovery/` | Drug target discovery pipeline | 3 | 8 |
| `omega_hdq_dna_bacteria_flex_96_channel/` | DNA extraction workflow | 3 | 17 |
| `rikyu_hpc/` | HPC jobs and containerized training on Rikyu | 11 (+16 traps) | 38 |
| `tnf_cancer_modelling/` | Multiscale cancer modeling workflow | 1 | 12 |

`rikyu_hpc` also ships 16 deliberately unsolvable *trap* problems. They are
returned by `get_trap_problems()`, not `get_problems()`, so `benchmarking.py`
reports its 11 solvable scenarios without 16 expected failures alongside them:

```bash
python -c "from rikyu_hpc import get_trap_problems; print(len(get_trap_problems()))"
```

Location: `packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/`

**Documentation:**
- [Bio-Opentrons README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/bio_opentrons/README.md)
- [Cross-Server README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/cross_server/README.md)
- [Drug Target Discovery README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/drug_target_discovery/README.md)
- [Omega HDQ README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/omega_hdq_dna_bacteria_flex_96_channel/README.md)
- [Rikyu HPC README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/rikyu_hpc/README.md)
- [TNF Cancer Modelling README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/tnf_cancer_modelling/README.md)
- [MCP Benchmarking Guide](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/benchmarking_quickstart.md)

### Memory Tracking Examples (1.8.0+)

Two examples demonstrating memory tracking capabilities:

| Example | Description | Scenarios | Memory Range |
|---------|-------------|-----------|--------------|
| `scalable_data_processing/` | Memory scaling via data volume | 20 | 1-300+ MB |
| `scalable_recursive_decomposition/` | Memory scaling via recursion depth | 12 | Exponential |

Location: `packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/`

**Documentation:**
- [Memory Tracking README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/README.md)
- [Scalable Data Processing README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/scalable_data_processing/README.md)
- [Scalable Recursive Decomposition README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md)
- [Memory Benchmarking Guide](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/benchmarking_quickstart.md)

## Testing Examples

**Run all examples automatically:**

```bash
# Test all examples in both modes
python test_migration.py

# Test only session mode
python test_migration.py --mode session

# Test only legacy mode
python test_migration.py --mode legacy
```

**Run regression tests:**

```bash
# Legacy regression tests
python -m gtpyhop.examples.regression_tests

# Session-based regression tests
python -m gtpyhop.examples.regression_tests --session
```

### Long-Running Benchmarks in the Background

Some example collections include intentionally extreme scenarios for
stress-testing — e.g. `memory_tracking`'s largest `data` scenarios scale to
~2GB and can run for tens of minutes. If you redirect a long-running
benchmark's output to a file to check on later, force unbuffered output:

```bash
python -u benchmarking.py > run.log 2>&1 &
# or: PYTHONUNBUFFERED=1 python benchmarking.py > run.log 2>&1 &
```

Without `-u`, Python fully buffers stdout whenever it isn't an interactive
terminal, so `run.log` can sit at 0 bytes for a long time even though the
process is actively working — the per-scenario `Success:`/`Failed:` lines
these scripts already print as each scenario finishes are just stuck in an
in-memory buffer until it fills or the process exits. `-u` (or
`PYTHONUNBUFFERED=1`) forces a flush after every line, so the log file is
genuinely tailable in real time (`tail -f run.log`) instead of only showing
everything at once at the end.

## Example Usage Patterns

**Interactive exploration:**
```bash
# Run with pauses to examine output step by step
python -m gtpyhop.examples.blocks_htn.examples --session --verbose 3
```

**Automated testing:**
```bash
# Run without pauses for scripts/CI
python -m gtpyhop.examples.blocks_htn.examples --session --no-pauses
```

**Concurrent planning (session mode only):**
```python
import threading
import gtpyhop

# Load example Domain
from gtpyhop.examples.blocks_htn import actions, methods, the_domain

def plan_worker(session_id, state, goals):
    with gtpyhop.PlannerSession(domain=the_domain, verbose=1) as session:
        with session.isolated_execution():
            result = session.find_plan(state, goals)
            print(f"Session {session_id}: {result.plan}")

# Run multiple planners concurrently
threads = []
for i in range(3):
    t = threading.Thread(target=plan_worker, args=(i, initial_state, goals))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Related Documentation

- [All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md) - Detailed pedagogical information about each example
- [Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md) - Session-based architecture guide
- [Structured Logging](https://github.com/PCfVW/GTPyhop/blob/pip/docs/logging.md) - Logging and memory tracking
- [Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md) - How to write new examples
