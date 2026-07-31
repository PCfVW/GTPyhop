# FAQ

Short answers to the questions that come up most. Longer treatments live in the guides
linked from each answer.

- [Which package should I install?](#which-package-should-i-install)
- [I get an ImportError about a pre-2.0 gtpyhop install](#i-get-an-importerror-about-a-pre-20-gtpyhop-install)
- [Where did `src/gtpyhop/` go?](#where-did-srcgtpyhop-go)
- [Global functions or `PlannerSession`?](#global-functions-or-plannersession)
- [Which planning strategy should I use?](#which-planning-strategy-should-i-use)
- [What must an action return?](#what-must-an-action-return)
- [Why is my action "not applicable"?](#why-is-my-action-not-applicable)
- [Does GTPyhop find the *best* plan?](#does-gtpyhop-find-the-best-plan)
- [Is GTPyhop thread-safe?](#is-gtpyhop-thread-safe)
- [How do I run the bundled examples?](#how-do-i-run-the-bundled-examples)
- [How do I add my own example?](#how-do-i-add-my-own-example)

## Which package should I install?

Since 2.0.0 GTPyhop is four distributions that all install into the same `gtpyhop`
import namespace:

| Install | You get | Use when |
|---|---|---|
| `gtpyhop` | the planner **and** every bundled example | learning, teaching, exploring |
| `gtpyhop-core` | the planner only | production, CI, embedded — no example baggage |
| `gtpyhop-examples` | the examples (pulls in `gtpyhop-core`) | you want examples but installed core first |
| `gtpyhop-diagnostics` | failure attribution, optional | you want to know *why* a plan failed |

`pip install gtpyhop` is the safe default and is byte-identical in effect to a pre-2.0
install. The split exists for two reasons: install footprint, and keeping the bundled
domains out of environments where an AI agent is being evaluated on writing GTPyhop
domains — where having dozens of worked answers on disk would be a crib channel.

`gtpyhop-diagnostics` is versioned independently (0.x) and released on its own cadence;
the other three ship in lockstep at one version.

## I get an ImportError about a pre-2.0 gtpyhop install

You'll see a message saying a pre-2.0 `gtpyhop` and `gtpyhop-core` are both installed
and their files collide under `site-packages/gtpyhop/`. That is real: before 2.0,
`gtpyhop` shipped those files itself, so whichever package was installed last silently
overwrote the other's.

```bash
pip uninstall gtpyhop gtpyhop-core gtpyhop-examples
pip install gtpyhop          # or gtpyhop-core, whichever you want
```

The guard only fires when the old distribution still owns real files on disk. An old
*editable* install (`pip install -e .` from a checkout) owns no package files, so it is
left alone rather than blocking your imports.

## Where did `src/gtpyhop/` go?

The 2.0.0 restructuring replaced the single `src/gtpyhop/` tree with one directory per
distribution:

```
packages/gtpyhop-core/src/gtpyhop/
packages/gtpyhop-examples/src/gtpyhop/examples/
packages/gtpyhop-diagnostics/src/gtpyhop/diagnostics/
packages/gtpyhop/                       # meta-package, no source
```

Nothing changed about importing — `import gtpyhop` and `import gtpyhop.examples` work
exactly as before, because the trees merge once installed. Working from a checkout,
install both in editable mode so they merge:

```bash
pip install -e packages/gtpyhop-core -e packages/gtpyhop-examples
```

## Global functions or `PlannerSession`?

Both work and both are supported. `PlannerSession` is recommended for anything new:

```python
with gtpyhop.PlannerSession(domain=my_domain, verbose=0) as session:
    result = session.find_plan(state, tasks)
```

A session owns its own domain, verbosity, strategy, logs and statistics, so concurrent
planning is safe and one run cannot perturb another. The global API (`gtpyhop.find_plan`,
`set_current_domain`, …) mutates process-global state, which is fine single-threaded and
is kept for backward compatibility. Only the session API exposes `trace=`/`trace_state=`.

See [Thread-Safe Sessions](thread_safe_sessions.md).

## Which planning strategy should I use?

| Strategy | Backtracks? | Notes |
|---|:---:|---|
| `iterative_greedy` (default) | No | Commits to the first applicable method and never reconsiders. Fastest; fails on domains needing a different choice |
| `recursive_dfs` | Yes | Backtracks via the Python call stack, so deep decompositions can hit the recursion limit |
| `iterative_dfs_backtracking` | Yes | Explicit stack, so no recursion limit. Use when you need backtracking at depth |

```python
with gtpyhop.PlannerSession(domain=d, strategy="iterative_dfs_backtracking") as s:
    result = s.find_plan(state, tasks)
```

If a plan you believe in isn't found, try a backtracking strategy before suspecting the
domain — the default genuinely gives up on alternatives.

## What must an action return?

The state on success; `False` or `None` on failure. All three are normal:

```python
def pickup(s, x):
    if s.clear[x] and s.holding['hand'] == False:
        s.pos[x] = 'hand'
        return s                 # success
    # falls off the end -> None -> "not applicable"
```

`None` is what GTPyhop's original examples have always done — the guard-then-effects
shape simply falls off the end when the guard is false. Returning `False` explicitly is
what the [domain style guide](gtpyhop_domain_style_guide.md) teaches and what the newer
examples do. Both mean "my preconditions did not hold".

Returning anything **else** — `True`, a string, a number — is a bug, and tracing reports
it as `malformed_return`. The case worth watching for is `return True` instead of
`return state`: the action looks successful while silently discarding its own effects.

## Why is my action "not applicable"?

That means the action reported that its preconditions did not hold. To find out *which*
precondition, install `gtpyhop-diagnostics`:

```python
from gtpyhop.diagnostics import explain_dead_end

with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(state, tasks, trace=True, trace_state=True)

print(explain_dead_end(result.trace, "domain.py").summary())
# drive('truck1', 'warehouse') was blocked by: state.fuel[truck] > 0
```

Walked through step by step in the [diagnostics tutorial](diagnostics_tutorial.md).

## Does GTPyhop find the *best* plan?

No. GTPyhop returns the **first** plan its search finds, not the shortest or cheapest.
There is no cost model: actions and methods carry no costs, and no strategy optimises.

Method order is your lever — `declare_task_methods` tries methods in the order given, so
put preferred ones first. Cost-aware planning is a roadmap item for a future major
version, since adding costs touches action and method declarations throughout.

## Is GTPyhop thread-safe?

With `PlannerSession`, yes — that is what it exists for. Each session isolates the
globals that planning touches (current domain, verbosity, strategy) and takes a lock for
the duration of a `find_plan` call.

The global API is **not** thread-safe: concurrent runs share `current_domain` and
friends, so they interfere. See [Thread-Safe Sessions](thread_safe_sessions.md).

## How do I run the bundled examples?

```bash
python -m gtpyhop.examples.simple_htn              # legacy mode
python -m gtpyhop.examples.simple_htn --session    # session mode
python -m gtpyhop.examples.regression_tests        # all of them
```

Requires `gtpyhop` or `gtpyhop-examples`. The catalogue with pedagogical notes is
[All Examples](all_examples.md); invocation details are in
[Running Examples](running_examples.md).

## How do I add my own example?

Read the [example style guide](gtpyhop_example_style_guide.md) — it covers the folder
layout, the required files, and the doctest conventions. Working from a checkout you'll
need the editable install described above, since a new example under
`packages/gtpyhop-examples/` is only importable as `gtpyhop.examples.your_example` once
the two source trees are merged by installation.

The [domain](gtpyhop_domain_style_guide.md) and
[problems](gtpyhop_problems_style_guide.md) style guides cover the file contents.
