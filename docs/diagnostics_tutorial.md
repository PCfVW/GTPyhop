# Tutorial: why didn't my plan work?

When `find_plan` comes back empty, GTPyhop can tell you a great deal more than "it
failed". This tutorial walks one small domain from *"there is no plan"* all the way to
*"`drive` was blocked because `truck1` had no fuel"*, one step at a time.

Every snippet here runs as written.

## Table of Contents

- [What you need](#what-you-need)
- [A domain that refuses to plan](#a-domain-that-refuses-to-plan)
- [Step 1: what `find_plan` alone tells you](#step-1-what-find_plan-alone-tells-you)
- [Step 2: `trace=True` — which action failed](#step-2-tracetrue--which-action-failed)
- [Step 3: `trace_state=True` — the state it failed in](#step-3-trace_statetrue--the-state-it-failed-in)
- [Step 4: `explain_dead_end` — which precondition](#step-4-explain_dead_end--which-precondition)
- [Step 5: fix it](#step-5-fix-it)
- [When it can't answer](#when-it-cant-answer)
- [Reference](#reference)

## What you need

```bash
pip install gtpyhop-core gtpyhop-diagnostics
```

Steps 1–3 need only `gtpyhop-core`. Step 4 adds `gtpyhop-diagnostics`, which is optional
and versioned separately.

## A domain that refuses to plan

Save this as `delivery.py`. A truck fetches a parcel and delivers it, and driving
consumes fuel:

```python
import gtpyhop

domain = gtpyhop.Domain('delivery')

def drive(state, truck, dest):
    if state.fuel[truck] > 0 and state.at[truck] != dest:
        state.at[truck] = dest
        state.fuel[truck] -= 1
        return state

def load(state, parcel, truck):
    if state.at[parcel] == state.at[truck]:
        state.at[parcel] = truck
        return state

def unload(state, parcel, truck):
    if state.at[parcel] == truck:
        state.at[parcel] = state.at[truck]
        return state

gtpyhop.declare_actions(drive, load, unload)

def m_deliver(state, parcel, truck, dest):
    return [('drive', truck, state.at[parcel]),
            ('load', parcel, truck),
            ('drive', truck, dest),
            ('unload', parcel, truck)]

gtpyhop.declare_task_methods('deliver', m_deliver)

def initial_state(fuel=2):
    state = gtpyhop.State('s0')
    state.at = {'truck1': 'depot', 'parcel1': 'warehouse'}
    state.fuel = {'truck1': fuel}
    return state
```

Note the shape of each action: **check preconditions, apply effects, return the state**.
When the guard is false the function simply falls off the end and returns `None`, which
GTPyhop reads as "not applicable here". Returning `False` explicitly means the same
thing — see the [FAQ](faq.md#what-must-an-action-return).

## Step 1: what `find_plan` alone tells you

```python
import gtpyhop
from delivery import domain, initial_state

TASK = [('deliver', 'parcel1', 'truck1', 'shop')]

with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(fuel=0), TASK)

print(result.success)   # False
print(result.plan)      # []
```

```
False
[]
```

That is the whole story you get by default: no plan exists from this state. *Which* step
was impossible, and *why*, are invisible. Historically the way forward was to re-run at
`verbose=3` and read the debug print-out — which is what the rest of this tutorial
replaces.

> Check `result.success` rather than the plan. An empty plan is also what a *successful*
> run returns when the goal is already satisfied. (`bool(result)` works correctly too,
> as of 2.0.0.)

## Step 2: `trace=True` — which action failed

```python
with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(fuel=0), TASK, trace=True)

dead_end = result.trace.dead_end
print(dead_end.item)                            # the action, with its arguments
print(dead_end.status)
print(dead_end.depth)
print(result.trace.applied_before_dead_end)
```

```
('drive', 'truck1', 'warehouse')
not_applicable
1
0
```

Now we know the search died on `drive('truck1', 'warehouse')`, at depth 1, having
applied no actions at all. `not_applicable` means the action reported that its
preconditions did not hold — a legitimate refusal, not a bug in the domain. Had `drive`
violated its contract (returning `True`, say, instead of the state), the status would
read `malformed_return` instead, which is a very different problem.

`trace=True` is free when you don't ask for it and cheap when you do: it records events,
nothing more.

## Step 3: `trace_state=True` — the state it failed in

Knowing *which* action failed still leaves the question of why. `drive` guards on two
things, so at this point either could be the culprit. Ask for the state as well:

```python
with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(fuel=0), TASK,
                               trace=True, trace_state=True)

dead_end = result.trace.dead_end
print(dead_end.state.fuel)
print(dead_end.state.at)
```

```
{'truck1': 0}
{'truck1': 'depot', 'parcel1': 'warehouse'}
```

`TraceEvent.state` is a deep copy of the state the action was *attempted against* — the
state its preconditions were evaluated on, not the state it returned. Unlike `trace`,
this one is not free: it copies the state once per recorded event, so leave it off when
benchmarking and turn it on when diagnosing.

You can already see the answer here. But reading it off by eye only works because this
domain is tiny; that is what the next step automates.

## Step 4: `explain_dead_end` — which precondition

```python
from gtpyhop.diagnostics import explain_dead_end

report = explain_dead_end(result.trace, "delivery.py")
print(report.summary())
```

```
drive('truck1', 'warehouse') was blocked by: state.fuel[truck] > 0
```

That is the sentence this whole feature exists to produce. The report carries the parts
separately too:

```python
print(report.action)          # 'drive'
print(report.args)            # ('truck1', 'warehouse')
print(report.blocking_vars)   # ['fuel']
print([a.source for a in report.candidates])
print([a.source for a in report.blocking])
```

```
drive
('truck1', 'warehouse')
['fuel']
['state.fuel[truck] > 0', 'state.at[truck] != dest']
['state.fuel[truck] > 0']
```

Note what did *not* happen: `state.at[truck] != dest` is listed as a **candidate**
precondition but not as **blocking**, because the truck was at `depot` and the
destination was `warehouse`, so that half held. Reading the source alone could only ever
give you the candidate list; it takes the state snapshot to narrow it to the one that
actually failed.

That is the whole idea — the source says *what could block*, the snapshot says *what did*.

## Step 5: fix it

Give the truck fuel and the same task plans:

```python
with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(fuel=2), TASK,
                               trace=True, trace_state=True)

print(result.success)
for step in result.plan:
    print(step)
```

```
True
('drive', 'truck1', 'warehouse')
('load', 'parcel1', 'truck1')
('drive', 'truck1', 'shop')
('unload', 'parcel1', 'truck1')
```

And asking for an explanation of a successful run says so plainly:

```python
print(explain_dead_end(result.trace, "delivery.py").summary())
```

```
no dead end recorded: the search did not abandon any item
```

## When it can't answer

A diagnostic tool that guesses is worse than one that admits ignorance, so every
degraded case is reported rather than raised. The most common is forgetting
`trace_state=True`:

```python
with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(fuel=0), TASK, trace=True)

report = explain_dead_end(result.trace, "delivery.py")
print(report.blocking)
print(report.note)
```

```
[]
candidate preconditions only -- without trace_state=True there is no state to test them against
```

Nothing is claimed as the culprit, and the note says exactly what to pass. The other
cases:

| Situation | What you get |
|---|---|
| Plan succeeded | "no dead end recorded" |
| Dead end is `task_exhausted` / `goal_exhausted` / `multigoal_exhausted` | Reported as a refinement dead end. Every candidate *method* was tried and none worked, so no single action's guard is at fault and precondition attribution does not apply |
| Dead end is `malformed_return` | Reported as such, with what the action actually returned — a domain bug, not a precondition failure |
| A guard calls a helper the analyser can't resolve | That conjunct lands in `report.unevaluated` with the reason, never guessed at |
| The action's guard lives in another function it delegates to | No guard found; reported as such. A known limitation |

For that fourth case, pass the defining module's globals so helper calls resolve:

```python
import sys
ns = vars(sys.modules[domain.__module__]) if hasattr(domain, '__module__') else vars(delivery)
report = explain_dead_end(result.trace, "delivery.py", namespace=ns)
```

Some bundled examples need this — `simple_htn`'s actions guard with `is_a(...)`, for
instance.

## Reference

- [`gtpyhop-diagnostics` README](../packages/gtpyhop-diagnostics/README.md) — API surface,
  both precondition idioms, coverage figures
- [Thread-Safe Sessions](thread_safe_sessions.md#execution-diagnostics-with-plantrace-200) —
  `PlanTrace`, the full status table, and `trace_state`
- [FAQ](faq.md) — shorter answers to adjacent questions
