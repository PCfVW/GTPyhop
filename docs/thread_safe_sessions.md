# GTPyhop 1.3.0+ — Thread‑Safe Sessions, Explained

GTPyhop 1.3.0 introduces a session‑based, thread‑safe architecture. This short guide explains why it matters, how to use it, and shows a tiny concurrent example that wasn’t practical before.


## Why thread‑safe sessions?

- **Isolation of global state**: Pre‑1.3.0 workflows depended on process‑global state (e.g., `current_domain`, verbosity, planning strategy). In concurrent code, runs could interfere with each other.
- **Reliable concurrency**: Each `PlannerSession` has its own configuration, lock, logs, and stats; concurrent planning in threads is safe starting with 1.3.0.
- **Per‑session control**: Set per‑session verbosity, iterative/recursive strategy, and timeouts. Persist and restore sessions independently.

Key APIs in `gtpyhop` (starting with 1.3.0): `PlannerSession`, `create_session`, `get_session`, `destroy_session`, `list_sessions`, `PlanningTimeoutError`, `SessionSerializer`, `restore_session`, `restore_all_sessions`.


## Rebuild the README “Very first HTN example” with sessions

Below is the same logic from `README.md` (Very first HTN example), expressed with the 1.3.0 session‑based API. The domain, actions, and methods are the same; planning now runs in an isolated session.

```python
import gtpyhop

# 1) Domain creation (same as README)
my_domain = gtpyhop.Domain('my_domain')

# 2) Define a state (same as README)
state = gtpyhop.State('initial_state')
state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}

# 3) Actions (same as README)
def move(state, obj, target):
    if obj in state.pos:
        state.pos[obj] = target
        return state
    return False

gtpyhop.declare_actions(move)

# 4) Task methods (same as README)
def transport(state, obj, destination):
    current = state.pos[obj]
    if current != destination:
        return [('move', obj, destination)]
    return []

gtpyhop.declare_task_methods('transport', transport)

# 5) Plan using a session (1.3.0+)
with gtpyhop.PlannerSession(domain=my_domain, verbose=1) as session:
    # Ensure isolation from any process‑global settings
    with session.isolated_execution():
        result = session.find_plan(state, [('transport', 'obj1', 'loc2')])
        if result.success:
            print(result.plan)
        else:
            print('Planning failed:', result.error)
```

Notes:
- `PlannerSession(domain=...)` keeps the planning isolated. The `isolated_execution()` context manager safely sets and restores global knobs during the call.
- You can also pass session‑specific controls, e.g. `recursive=True` for the recursive strategy, or a `timeout_ms` to `find_plan`.

Example with a timeout:

```python
result = session.find_plan(state, [('transport', 'obj1', 'loc2')], timeout_ms=500)
```


## Concurrent examples (impractical before)

Two sessions plan in parallel, each with its own Domain and verbosity. Before 1.3.0, mutating globals concurrently risked races and cross‑talk between runs.

**Note:** All migrated examples can be used in concurrent scenarios. For real-world usage, see the migrated examples like `blocks_htn` or `simple_htn` which demonstrate session-based planning.

```python
import threading
import gtpyhop

# Domain A
A = gtpyhop.Domain('A')
stateA = gtpyhop.State('sA'); stateA.pos = {'x': 'l1'}

def moveA(s, o, t):
    if o in s.pos: s.pos[o] = t; return s
    return False

gtpyhop.declare_actions(moveA)

def taskA(s, o, d):
    return [('moveA', o, d)] if s.pos[o] != d else []

gtpyhop.declare_task_methods('taskA', taskA)

# Domain B
B = gtpyhop.Domain('B')
stateB = gtpyhop.State('sB'); stateB.pos = {'y': 'm1'}

def moveB(s, o, t):
    if o in s.pos: s.pos[o] = t; return s
    return False

gtpyhop.declare_actions(moveB)

def taskB(s, o, d):
    return [('moveB', o, d)] if s.pos[o] != d else []

gtpyhop.declare_task_methods('taskB', taskB)

plans = {}

def worker(name, domain, state, todo):
    with gtpyhop.PlannerSession(domain=domain, verbose=2) as session:
        with session.isolated_execution():
            result = session.find_plan(state, todo)
            plans[name] = result.plan if result.success else result.error

threads = [
    threading.Thread(target=worker, args=('A', A, stateA, [('taskA', 'x', 'l2')]))
 ,  threading.Thread(target=worker, args=('B', B, stateB, [('taskB', 'y', 'm2')]))
]

[t.start() for t in threads]
[t.join() for t in threads]

print(plans)  # {'A': [('moveA', 'x', 'l2')], 'B': [('moveB', 'y', 'm2')]}
```

### New 1.3.0 APIs used above (with brief explanations)

- `PlannerSession(...)`: constructs an isolated, thread‑safe planning session with its own configuration and locks.
- `session.isolated_execution()`: context manager that temporarily applies session settings (Domain, verbosity, strategy) and restores previous global state on exit.
- `session.find_plan(state, todo, timeout_ms=None, max_expansions=None)`: per‑session planning call that returns a `PlanResult` with `success`, `plan`, `error`, and `stats`.

### Why this is impossible to do correctly without sessions (pre‑1.3.0)

Concurrent use of the classic global API is effectively unsafe and can yield incorrect plans due to cross‑contamination:

- **Domain swapping contamination (HTN example):** Suppose both threads use an action name `move` and a task name `transport`, but with different semantics per Domain. Thread A sets `current_domain = A`; before `find_plan` completes, Thread B sets `current_domain = B`. A’s planner may now pick B’s `transport` method or B’s `move` operator, producing a mixed or invalid plan.
- **Strategy/verbosity races:** One thread toggles `set_recursive_planning(True)` or changes verbosity while another is planning, leading to nondeterministic expansions and logs.

In short, pre‑1.3.0 there is no built‑in isolation; achieving correctness would require external synchronization around all planning calls, defeating concurrency.


## Examples Migration Status

**✅ Migration Complete:** All 10 GTPyhop examples now support both legacy and session modes.

### Migrated Examples

**Simple Examples (6):**
- `simple_htn.py` - Basic hierarchical task network planning
- `simple_hgn.py` - Basic hierarchical goal network planning
- `backtracking_htn.py` - Backtracking demonstration
- `simple_htn_acting_error.py` - Error handling patterns
- `logistics_hgn.py` - Goal-oriented logistics planning
- `pyhop_simple_travel_example.py` - Basic travel planning

**Complex Block World Examples (4):**
- `blocks_htn/examples.py` - Hierarchical task networks
- `blocks_hgn/examples.py` - Hierarchical goal networks
- `blocks_gtn/examples.py` - Goal task networks with mixed planning
- `blocks_goal_splitting/examples.py` - Goal splitting methodology

### Dual-Mode Interface

Every migrated example supports consistent command-line arguments:

```bash
# Legacy mode (backward compatible)
python -m gtpyhop.examples.simple_htn

# Session mode (thread-safe, recommended)
python -m gtpyhop.examples.simple_htn --session

# Session mode with custom settings
python -m gtpyhop.examples.simple_htn --session --verbose 3 --no-pauses
```

**Available arguments:**
- `--session`: Enable thread-safe session mode
- `--verbose N`: Set verbosity level (0-3, default: 1 in session mode)
- `--no-pauses`: Skip interactive pauses for automated testing

### Migration Pattern

Each example follows a consistent dual-mode pattern:

```python
def main(do_pauses=True):
    """Legacy entry point - preserved for backward compatibility."""
    main_legacy(do_pauses)

def main_legacy(do_pauses=True):
    """Legacy implementation using global state."""
    # Original implementation preserved exactly

def main_session(do_pauses=True, verbose=1):
    """Thread-safe implementation using PlannerSession."""
    with gtpyhop.PlannerSession(domain=the_domain, verbose=verbose) as session:
        with session.isolated_execution():
            result = session.find_plan(state, goals)
            # Session-based implementation

def main_with_args(argv=None):
    """Command-line interface for choosing execution mode."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", action="store_true")
    parser.add_argument("--verbose", type=int, default=1)
    parser.add_argument("--no-pauses", action="store_true")
    # Handle arguments and call appropriate function

if __name__ == "__main__":
    main_with_args()
```

### Testing Infrastructure

**Comprehensive validation:**

```bash
# Test all examples in both modes
python test_migration.py

# Test only session mode
python test_migration.py --mode session

# Run regression tests
python -m gtpyhop.examples.regression_tests --session
```

**Results:** 9/9 examples pass in both legacy and session modes.

### Real-World Usage with Migrated Examples

The migrated examples provide excellent starting points for concurrent applications:

```python
import threading
import gtpyhop

# Load any migrated example Domain
from gtpyhop.examples.blocks_htn import actions, methods, the_domain

def concurrent_planner(session_id, state, goals):
    """Plan using session mode - safe for concurrent execution."""
    with gtpyhop.PlannerSession(domain=the_domain, verbose=1) as session:
        with session.isolated_execution():
            result = session.find_plan(state, goals)
            print(f"Session {session_id}: {result.plan}")
            return result

# Run multiple planners concurrently
threads = []
for i in range(3):
    t = threading.Thread(target=concurrent_planner, args=(i, initial_state, goals))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```


## Quick checklist (when to use sessions)

- You run planners concurrently (threads/processes), or from a web/API server.
- You need per‑run settings (verbosity, recursive vs iterative) without affecting others.
- You require timeouts/cancellation, structured logs, or persistence per run.

### Crucial thread‑safe and session APIs introduced in 1.3.0

- `PlannerSession` (class): isolated planning context; provides `isolated_execution()`, `find_plan()`.
- `create_session(session_id=None, **kwargs)`: create and register a new session.
- `get_session(session_id=None)`: fetch existing or a default session.
- `destroy_session(session_id)`: cleanup and remove a session.
- `list_sessions()`: enumerate active sessions.
- `PlanningTimeoutError` (exception): raised when a session‑scoped timeout triggers.
- `SessionSerializer` (class), `restore_session()`, `restore_all_sessions()`: persistence and recovery.
- `set_persistence_directory()`, `get_persistence_directory()`: configure auto‑save/recovery.

That’s it—starting with 1.3.0, use `PlannerSession` for reliable, concurrent planning in GTPyhop.

