# GTPyhop Thread-Safe Sessions Guide

GTPyhop 1.3.0 introduced a session-based, thread-safe architecture. GTPyhop 1.8.0 adds memory tracking integration. GTPyhop 1.9.0 adds the iterative DFS backtracking strategy and the `strategy` parameter. GTPyhop 2.0.0 adds opt-in execution diagnostics via `PlanTrace`. This guide explains why sessions matter, how to use them, and shows concurrent examples.

## Table of Contents

- [Why Thread-Safe Sessions?](#why-thread-safe-sessions)
- [Basic Session Example](#basic-session-example)
- [Session with Memory Tracking (1.8.0+)](#session-with-memory-tracking-180)
- [Planning Strategy Selection (1.9.0+)](#planning-strategy-selection-190)
- [Execution Diagnostics with PlanTrace (2.0.0+)](#execution-diagnostics-with-plantrace-200)
  - [State snapshots with `trace_state=True`](#state-snapshots-with-trace_statetrue)
- [Concurrent Planning Example](#concurrent-planning-example)
  - [Why This Is Unsafe Without Sessions (Pre-1.3.0)](#why-this-is-unsafe-without-sessions-pre-130)
- [Session APIs Reference](#session-apis-reference)
  - [Core Session APIs (1.3.0+)](#core-session-apis-130)
  - [Persistence APIs (1.3.0+)](#persistence-apis-130)
  - [Memory Tracking APIs (1.8.0+)](#memory-tracking-apis-180)
  - [Execution Diagnostics APIs (2.0.0+)](#execution-diagnostics-apis-200)
- [Dual-Mode Interface](#dual-mode-interface)
- [When to Use Sessions](#when-to-use-sessions)
- [Related Documentation](#related-documentation)

## Why Thread-Safe Sessions?

- **Isolation of global state**: Pre-1.3.0 workflows depended on process-global state (e.g., `current_domain`, verbosity, planning strategy). In concurrent code, runs could interfere with each other.
- **Reliable concurrency**: Each `PlannerSession` has its own configuration, lock, logs, and stats; concurrent planning in threads is safe starting with 1.3.0.
- **Per-session control**: Set per-session verbosity, planning strategy (recursive DFS, iterative greedy, or iterative DFS backtracking), timeouts, and memory tracking. Persist and restore sessions independently.

Key APIs in `gtpyhop` (1.3.0+): `PlannerSession`, `create_session`, `get_session`, `destroy_session`, `list_sessions`, `PlanningTimeoutError`, `SessionSerializer`, `restore_session`, `restore_all_sessions`.

## Basic Session Example

Below is the same logic from `README.md` (Very first HTN example), expressed with the session-based API:

```python
import gtpyhop

# 1) Domain creation
my_domain = gtpyhop.Domain('my_domain')

# 2) Define a state
state = gtpyhop.State('initial_state')
state.pos = {'obj1': 'loc1', 'obj2': 'loc2'}

# 3) Actions
def move(state, obj, target):
    if obj in state.pos:
        state.pos[obj] = target
        return state
    return False

gtpyhop.declare_actions(move)

# 4) Task methods
def transport(state, obj, destination):
    current = state.pos[obj]
    if current != destination:
        return [('move', obj, destination)]
    return []

gtpyhop.declare_task_methods('transport', transport)

# 5) Plan using a session (1.3.0+)
with gtpyhop.PlannerSession(domain=my_domain, verbose=1) as session:
    with session.isolated_execution():
        result = session.find_plan(state, [('transport', 'obj1', 'loc2')])
        if result.success:
            print(result.plan)
        else:
            print('Planning failed:', result.error)
```

Notes:
- `PlannerSession(domain=...)` keeps the planning isolated. The `isolated_execution()` context manager safely sets and restores global knobs during the call.
- You can also pass session-specific controls, e.g. `recursive=True` for the recursive strategy, `strategy="iterative_dfs_backtracking"` for the iterative backtracking strategy (1.9.0+), or a `timeout_ms` to `find_plan`.

Example with a timeout:

```python
result = session.find_plan(state, [('transport', 'obj1', 'loc2')], timeout_ms=500)
```

## Session with Memory Tracking (1.8.0+)

GTPyhop 1.8.0 adds memory tracking integration:

```python
with gtpyhop.PlannerSession(
    domain=my_domain,
    verbose=1,
    memory_tracking=True,
    memory_sampling_interval=0.1  # 100ms sampling
) as session:
    with session.isolated_execution():
        result = session.find_plan(state, tasks)
        if result.success:
            print(f"Plan: {result.plan}")
            print(f"Memory used: {result.stats['memory_mb']:.2f} MB")
            print(f"Peak memory: {result.stats['peak_memory_mb']:.2f} MB")
```

## Planning Strategy Selection (1.9.0+)

GTPyhop 1.9.0 supports three planning strategies. The `strategy` parameter (new in 1.9.0) takes precedence over the legacy `recursive` bool when both are provided.

| Strategy name | Backtracking? | Stack | `PlannerSession` parameter |
|---------------|:------------:|-------|----------------------------|
| Recursive DFS | Yes | Python call stack | `recursive=True` or `strategy="recursive_dfs"` |
| Iterative greedy | No | Explicit stack | `recursive=False` (default) or `strategy="iterative_greedy"` |
| Iterative DFS BT | Yes | Explicit stack | `strategy="iterative_dfs_backtracking"` |

```python
# Iterative DFS with backtracking (1.9.0+)
with gtpyhop.PlannerSession(
    domain=my_domain,
    strategy="iterative_dfs_backtracking"
) as session:
    result = session.find_plan(state, tasks)

# Legacy interface still works identically
with gtpyhop.PlannerSession(domain=my_domain, recursive=True) as session:
    result = session.find_plan(state, tasks)  # recursive DFS

with gtpyhop.PlannerSession(domain=my_domain, recursive=False) as session:
    result = session.find_plan(state, tasks)  # iterative greedy
```

When `strategy` is provided, `recursive` is ignored. The `session.recursive` property remains available and returns `True` only when the strategy is `"recursive_dfs"`.

The strategy name is reported in `result.stats["strategy"]` (e.g. `"iterative_dfs_backtracking"`).

## Execution Diagnostics with PlanTrace (2.0.0+)

GTPyhop 2.0.0 adds opt-in structured tracing of `find_plan`'s search: pass `trace=True` to record every action-application and method-refinement attempt, so you can see *why* a scenario failed to plan, not just that it did. Default `False`; costs nothing when not requested.

```python
with gtpyhop.PlannerSession(domain=my_domain, verbose=0) as session:
    result = session.find_plan(state, tasks, trace=True)

if not result.success:
    dead_end = result.trace.dead_end
    print(f"Failed at depth {dead_end.depth}: {dead_end.item} ({dead_end.status})")
    print(f"{result.trace.applied_before_dead_end} actions applied before the dead end")
    if result.trace.malformed_returns:
        print("Malformed returns found:", result.trace.malformed_returns)
```

`result.trace` is a `PlanTrace` recording every attempt in depth-first order:

| API | Description |
|-----|-------------|
| `result.trace.events` | Ordered list of `TraceEvent(depth, item, status, detail, state)` |
| `result.trace.dead_end` | First terminal event (see statuses below), or `None` if every recorded item succeeded |
| `result.trace.applied_before_dead_end` | Count of applied/idempotent actions recorded strictly before `dead_end` |
| `result.trace.malformed_returns` | All events where an action or method violated its return contract |

`TraceEvent.item` holds whatever todo-list entry the event concerns: an action tuple for the action-level statuses, or a task/unigoal/`Multigoal` for the refinement-level ones.

### State snapshots with `trace_state=True`

`trace=True` alone answers *which* action or method failed. To answer *which precondition* failed, you also need the state that action was evaluated against — pass `trace_state=True` and each event carries a deep copy of it in `TraceEvent.state`:

```python
with gtpyhop.PlannerSession(domain=my_domain, verbose=0) as session:
    result = session.find_plan(state, tasks, trace=True, trace_state=True)

dead_end = result.trace.dead_end
if dead_end is not None and dead_end.state is not None:
    # e.g. the action guards on state.door_unlocked[door] -- now you can see it
    print(dead_end.item, "was blocked in state:", vars(dead_end.state))
```

- `TraceEvent.state` is the state the item was **attempted against** — for an action, the state its preconditions were evaluated on, *not* the state the action returned.
- It is `None` unless `trace_state=True`, and also `None` if the state could not be deep-copied (a domain may put an uncopyable object in a state variable; a diagnostic facility must not crash the planner it is diagnosing).
- `trace_state=True` implies `trace=True`.
- Unlike `trace`, this one is **not** free during a traced search: it deep-copies the state once per recorded event. Leave it off for benchmarking; turn it on when diagnosing a specific failing scenario.

Snapshots are the runtime half of failure attribution; the other half is a source-level analysis of the failing action's preconditions, which stays outside `gtpyhop-core` (see the note below).

| Status | Terminal? | Meaning |
|--------|:---------:|---------|
| `applied` | No | Action returned a changed `State`; recorded in the plan |
| `idempotent` | No | Action returned an unchanged `State`; not recorded, search continued |
| `not_applicable` | Yes | Action returned exactly `False` — a legitimate precondition failure |
| `malformed_return` | Yes | Action returned neither `State` nor `False` (e.g. `True`) — a domain-authoring bug, previously indistinguishable from `not_applicable` |
| `method_applicable` | No | A candidate method for a task/unigoal/multigoal returned a subtask/subgoal list |
| `method_not_applicable` | No | A candidate method returned `False`/`None`; the loop moves to the next candidate |
| `method_malformed_return` | Yes | A candidate method returned something that is neither a list, `False`, nor `None` — terminal because the value is used immediately afterward and raises `TypeError`, so the enclosing `*_exhausted` event is never reached |
| `task_exhausted` / `goal_exhausted` / `multigoal_exhausted` | Yes | Every candidate method was tried and none succeeded |

`PlanTrace` is a mechanical primitive only: it reports *which* action or method, at what depth, with what status, and — with `trace_state=True` — the state it was attempted against. It does not itself attribute failure to a specific precondition or state variable: naming the culprit means reading the domain source to find the failing action's guards and intersecting them with the snapshot, which is a source-level analysis deliberately left to the caller.

`PlanResult` and `ExecutionResult` also correctly support `bool(result)` as of 2.0.0 (equivalent to `result.success`) — previously both were plain dataclasses and therefore always truthy regardless of outcome, so `if result:` silently ignored failures. Always check `.success` explicitly if you're on an earlier version.

## Concurrent Planning Example

Two sessions plan in parallel, each with its own Domain and verbosity. Before 1.3.0, mutating globals concurrently risked races and cross-talk between runs.

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
    threading.Thread(target=worker, args=('A', A, stateA, [('taskA', 'x', 'l2')])),
    threading.Thread(target=worker, args=('B', B, stateB, [('taskB', 'y', 'm2')]))
]

[t.start() for t in threads]
[t.join() for t in threads]

print(plans)  # {'A': [('moveA', 'x', 'l2')], 'B': [('moveB', 'y', 'm2')]}
```

### Why This Is Unsafe Without Sessions (Pre-1.3.0)

Concurrent use of the classic global API is effectively unsafe:

- **Domain swapping contamination:** Thread A sets `current_domain = A`; before `find_plan` completes, Thread B sets `current_domain = B`. A's planner may pick B's methods, producing invalid plans.
- **Strategy/verbosity races:** One thread toggles `set_recursive_planning(True)` while another is planning, leading to nondeterministic behavior.

## Session APIs Reference

### Core Session APIs (1.3.0+)

| API | Description |
|-----|-------------|
| `PlannerSession(domain, verbose, ...)` | Isolated planning context |
| `PlannerSession(strategy=...)` | Strategy selection: `"recursive_dfs"`, `"iterative_greedy"`, `"iterative_dfs_backtracking"` (1.9.0+) |
| `session.recursive` | `True` only when the strategy is `"recursive_dfs"` (read-only property) |
| `session.isolated_execution()` | Context manager for safe execution |
| `session.find_plan(state, tasks, timeout_ms=..., trace=...)` | Plan with optional timeout and execution tracing (2.0.0+); both keyword-only |
| `create_session(session_id, **kwargs)` | Create and register a session |
| `get_session(session_id)` | Fetch existing session |
| `destroy_session(session_id)` | Cleanup and remove session |
| `list_sessions()` | Enumerate active sessions |
| `PlanningTimeoutError` | Exception for timeout |

### Persistence APIs (1.3.0+)

| API | Description |
|-----|-------------|
| `SessionSerializer` | Serialize/deserialize sessions |
| `restore_session(session_id)` | Restore a saved session |
| `restore_all_sessions()` | Restore all saved sessions |
| `set_persistence_directory(path)` | Configure auto-save location |
| `get_persistence_directory()` | Get persistence location |

### Memory Tracking APIs (1.8.0+)

| API | Description |
|-----|-------------|
| `memory_tracking` | Enable memory tracking (default: `False`) |
| `memory_sampling_interval` | Sampling interval: 0.1s default, use 0.001s for fast scenarios (<100ms) |
| `result.stats['memory_mb']` | Memory used during planning |
| `result.stats['peak_memory_mb']` | Peak memory observed |

### Execution Diagnostics APIs (2.0.0+)

| API | Description |
|-----|-------------|
| `session.find_plan(..., trace=True)` | Opt in to recording a `PlanTrace` of the search (default `False`, no cost when unused) |
| `session.find_plan(..., trace_state=True)` | Also snapshot the state each event was attempted against; implies `trace`, costs one deep copy per event |
| `result.trace` | `PlanTrace`, or `None` if `trace=False` |
| `result.trace.events` | Ordered `TraceEvent(depth, item, status, detail, state)` list |
| `result.trace.dead_end` | First terminal event, or `None` |
| `result.trace.applied_before_dead_end` | Actions applied before the dead end |
| `result.trace.malformed_returns` | Events where an action/method violated its return contract |
| `event.state` | Deep copy of the state that event was attempted against, or `None` unless `trace_state=True` |

See [Execution Diagnostics with PlanTrace](#execution-diagnostics-with-plantrace-200) above for the full status table and a worked example.

## Dual-Mode Interface

All core examples support both legacy and session modes:

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
- `--verbose N`: Set verbosity level (0-3)
- `--no-pauses`: Skip interactive pauses

## When to Use Sessions

Use sessions when:
- Running planners concurrently (threads/processes) or from a web/API server
- Needing per-run settings (verbosity, planning strategy) without affecting others
- Requiring timeouts/cancellation, structured logs, or persistence per run
- Tracking memory usage during planning (1.8.0+)
- Diagnosing *why* a scenario failed to plan, not just that it did (2.0.0+)

## Related Documentation

- [Running Examples](https://github.com/PCfVW/GTPyhop/blob/pip/docs/running_examples.md) - How to run all examples
- [Structured Logging](https://github.com/PCfVW/GTPyhop/blob/pip/docs/logging.md) - Logging and memory tracking
- [All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md) - Detailed example documentation
