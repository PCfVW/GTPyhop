# gtpyhop-diagnostics

Failure attribution for [GTPyhop](https://github.com/PCfVW/GTPyhop) plans: when
`find_plan` fails, name the precondition that blocked it.

`PlanTrace` (in `gtpyhop-core` 2.0.0) tells you *which* action the search died on.
This package tells you *why*:

```
pickup('a') was blocked by: s.clear[x] == True
```

## Install

```bash
pip install gtpyhop-diagnostics
```

It depends only on `gtpyhop-core>=2.0.0` — no bundled examples, no third-party
dependencies, and the analysis uses the standard library's `ast`.

New to this? The **[diagnostics tutorial](../../docs/diagnostics_tutorial.md)** walks one
small domain from *"there is no plan"* to *"the truck had no fuel"*, one step at a time.

## Usage

Plan with **both** `trace=True` and `trace_state=True`, then explain the result:

```python
import gtpyhop
from gtpyhop.diagnostics import explain_dead_end

with gtpyhop.PlannerSession(domain=my_domain, verbose=0) as session:
    result = session.find_plan(state, tasks, trace=True, trace_state=True)

report = explain_dead_end(result.trace, "path/to/domain.py")

print(report.summary())        # "pickup('a') was blocked by: s.clear[x] == True"
report.action                  # 'pickup'
report.args                    # ('a',)
report.blocking                # atoms that evaluated false
report.blocking_vars           # ['clear']
report.candidates              # every guard atom found
report.unevaluated             # atoms that could not be decided, each with a reason
```

`explain_dead_end` accepts a `.py` file or a directory to search, so you can point
it at a whole example collection without knowing which file defines the action.

If an action's guard calls a helper (`simple_htn`'s `is_a`, say), pass the defining
module's globals so those calls can be resolved:

```python
import sys
ns = vars(sys.modules[my_domain.__module__])
report = explain_dead_end(result.trace, "domain.py", namespace=ns)
```

Without it, atoms calling that helper are reported in `unevaluated` — not guessed at.

## How it works

Neither half is sufficient alone:

- **Static analysis** of the domain source yields an action's *candidate*
  preconditions. For `pickup` that is three guards, with no way to tell which one
  blocked the plan.
- **`TraceEvent.state`** — the snapshot recorded when planning with
  `trace_state=True` — is the state the action was actually evaluated on.

Each guard is split into atoms and evaluated against that snapshot. The atoms that
come out false are the blocking preconditions.

Evaluation rather than pattern-matching is what makes this accurate: a `TraceEvent`'s
item tuple carries the action's *actual arguments* (`('pickup', 'a')`), and the
function's AST carries its parameter names. Binding them together lets each conjunct
run exactly as the planner would have, which covers comparisons, helper calls and
arbitrary expressions that pattern-matching could not.

### Both precondition idioms

GTPyhop domains guard preconditions in two structurally inverted shapes, and both
are handled:

```python
# Negative guard-and-bail -- what the domain style guide teaches
def a_open_door(state, door):
    if not (hasattr(state, 'door_unlocked') and state.door_unlocked[door]):
        return False          # the `if` bails, so the requirement is its negation
    ...

# Positive wrapping guard -- GTPyhop's original idiom
def pickup(s, x):
    if s.pos[x] == 'table' and s.clear[x] and s.holding['hand'] == False:
        ...                   # the `if` wraps the effects, so the test IS the requirement
        return s
```

`not (A and B)` is unwrapped before splitting, so a report names the single conjunct
that failed rather than blaming the whole condition.

`or` is deliberately **not** split: with a disjunction it is the combination that
fails, so naming one side as "the blocking precondition" would be false. Such an
expression is kept whole.

### Coverage

Measured against the 293 actions declared across all bundled `gtpyhop-examples`
collections: **285 (97%) have their guards recognised.** The other 8 have no
precondition guard to find — `drive_truck`, `load_truck`, `fly_plane`, `load_plane`
and `putv` are unconditional, and the three `c_pay_driver` commands delegate to
another function. An action whose check lives in a delegate is a known limitation.

## Honest degradation

A diagnostic tool that blows up on an unusual domain is worse than one that says
what it could not determine, so every degraded case is reported rather than raised:

| Situation | What you get |
|---|---|
| `trace=False` / no trace | a report saying which flags to pass |
| `trace_state=False` | candidate preconditions only, with that stated — never a claimed culprit |
| plan succeeded | "no dead end recorded" |
| dead end is `task_exhausted` / `goal_exhausted` / `multigoal_exhausted` | reported as a refinement dead end; precondition attribution does not apply, since no single action's guard is at fault |
| dead end is `malformed_return` | reported as such, with what the action actually returned |
| action's source not found | says so, naming the action and where it looked |
| an atom raises, or calls an unresolvable helper | that atom lands in `unevaluated` with the reason |

## A note on executing domain code

Evaluating a guard means executing an expression from the domain. `find_plan` has
already called those very functions, so this adds no exposure that planning did not.
This is not a sandbox and is not meant to be one: if a domain is untrusted, it was
already untrusted when it was planned with.

## Scope

Deliberately outside `gtpyhop-core` — the planner should not carry a source-analysis
layer, and this is an optional add-on with its own release cadence. It reads only the
public `PlanTrace` API and never touches `Domain`'s private action dictionary.

Not in v0.1: producer/effect analysis (which action *could* set the blocking
variable), and attribution for refinement dead ends.

## License

Clear BSD License, matching the rest of GTPyhop.
