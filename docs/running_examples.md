# Running GTPyhop Examples

GTPyhop includes comprehensive examples demonstrating various planning techniques. **All examples support both legacy and session modes** for maximum flexibility and thread safety.

## 🚀 Running Examples

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

## 📋 Available Examples

### **Simple Examples** (Basic concepts and techniques)

| Example | Description | Key Features |
|---------|-------------|--------------|
| `simple_htn.py` | Basic hierarchical task networks | HTN planning, verbosity levels, execution |
| `simple_hgn.py` | Basic hierarchical goal networks | HGN planning, goal-oriented tasks |
| `backtracking_htn.py` | Backtracking demonstration | Method failure handling, alternative paths |
| `simple_htn_acting_error.py` | Error handling patterns | Execution failures, replanning |
| `logistics_hgn.py` | Logistics domain planning | Multi-goal planning, transportation |
| `pyhop_simple_travel_example.py` | Travel planning | Basic domain modeling |

### **Complex Block World Examples** (Advanced planning scenarios)

| Example | Description | Key Features |
|---------|-------------|--------------|
| `blocks_htn/` | Hierarchical task networks | Complex HTN methods, block manipulation |
| `blocks_hgn/` | Hierarchical goal networks | Goal decomposition, multigoals |
| `blocks_gtn/` | Goal task networks | Mixed task/goal planning |
| `blocks_goal_splitting/` | Goal splitting methodology | Built-in goal decomposition methods |

### **IPC 2020 Total Order Planning Problems** (With advanced benchmarking and evaluation)

Two examples from the IPC 2020 Total Order track are included:

| Example | Description | Key Features |
|---------|-------------|--------------|
| `Blocksworld-GTOHP/` | Classic blocks world | HTN planning, stacking, multigoals |
| `Childsnack/` | Resource management in childcare setting | HTN planning, constraint handling, multigoals |

The [IPC 2020 Total Order](https://github.com/panda-planner-dev/ipc2020-domains/tree/master/total-order) examples are located in the `src/gtpyhop/examples/ipc-2020-total-order/` directory and include comprehensive domain definitions, problem instances, and evaluation frameworks. **For detailed instructions on running these advanced examples, including setup requirements, execution procedures, and performance analysis tools, please refer to the comprehensive documentation in [`benchmarking_quickstart.md`](src/gtpyhop/examples/ipc-2020-total-order/benchmarking_quickstart.md)**. This dedicated benchmarking guide provides step-by-step instructions for executing the IPC problems, interpreting results, and conducting comparative performance analysis.

## 🧪 Testing Examples

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

## 💡 Example Usage Patterns

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
from gtpyhop.examples.blocks_htn import actions, methods

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

## 📚 Additional Resources

For advanced benchmarking and performance evaluation using the IPC 2020 Total Order problems, see:
- **`benchmarking_quickstart.md`** - Comprehensive guide to running and analyzing IPC benchmarks
- **`src/gtpyhop/examples/ipc-2020-total-order/`** - Complete IPC problem suite with domain definitions and test cases
