# Roadmap

Where GTPyhop is going, and why. Dates are deliberately absent: this records
**order and reasoning**, not schedule.

## Where 2.0 landed, and where it was aimed

2.0 was originally scoped around a single idea — *"v1.x asked HOW to plan; v2 asks WHICH
plan"* — with three deliverables: a tutorial on writing goals, plan visualisation, and
an iterative-deepening strategy.

That is not what shipped. 2.0 became a **packaging and diagnosability** release instead:

- the split into `gtpyhop-core`, `gtpyhop-examples` and the `gtpyhop` meta-package, so a
  production or CI install no longer carries dozens of example domains;
- `PlanTrace` — structured, opt-in tracing of a search, replacing the practice of
  parsing `verbose=3` output or reaching into `Domain`'s private dictionaries;
- state snapshots (`trace_state=True`), which make it possible to say *why* a search
  stopped rather than only *where*;
- `gtpyhop-diagnostics`, an optional package that turns a dead end into a named
  precondition.

The reason for the change of course was evidence. Measured across a set of
machine-generated GTPyhop domains, the dominant failure was not plan quality but plan
*existence*: "does `find_plan` solve this at all" failed far more often than any other
check, and the tooling to answer "why not" did not exist. Optimisation is not the
pressing problem when the planner cannot tell you what went wrong.

Of the original three, the **goals tutorial is done** — see
[how to write a goal](goals_tutorial.md). The other two moved out, as below.

## Next

### Plan visualisation (2.1)

Render a plan and its decomposition, rather than reading it as a list of tuples:
`result.to_mermaid()`, `to_graphviz()`, `to_gantt()`, plus a `result.decomposition`
tree. The iterative backtracking planner already builds most of the structure this
needs internally; the work is exposing it, not computing it.

This is the natural next step now that `PlanTrace` records what the search did — the
same data, drawn instead of printed.

### `gtpyhop-diagnostics` 0.2

Follow-ons deliberately left out of 0.1:

- **producer analysis** — not only *which* precondition blocked the plan, but which
  action could have made it true, and why it wasn't used;
- **refinement dead ends** — 0.1 reports `task_exhausted` and its siblings honestly but
  does not explain them;
- **delegated guards** — an action whose preconditions live in a helper it calls is
  currently invisible to the analysis.

## Later

### Iterative deepening (IDDFS)

A fourth strategy alongside `recursive_dfs`, `iterative_greedy` and
`iterative_dfs_backtracking`, returning the shortest plan when several exist. The depth
bound must be **primitive-action count**, not decomposition-tree height — compound tasks
expand to wildly different depths, so bounding the tree bounds the wrong thing.

Deferred rather than dropped: it pairs well with visualisation (decomposition trees
visibly shrink as the bound rises), so it reads better after 2.1 than before it.

### Smaller, tracked

- **`max_expansions` is accepted but not enforced.** It currently warns. Implementing it
  means adding an expansion counter to `seek_plan_recursive`, which has none, and
  settling what one "expansion" is — the two iterative strategies count main-loop
  iterations, while `PlanTrace.applied_before_dead_end` counts applied actions.
- **`result.stats["expansions"]` is always `0`** and will stay so until the above lands.
- **`PlannerSession.load_from_file` reports every failure as `None`.** A missing file,
  a corrupt file, a missing required field and an unknown schema version are all
  indistinguishable to a caller: the `SessionPersistenceError` raised inside is caught
  by a broad `except` and swallowed. That is what kept the 2.0.0 session-persistence
  bug invisible for two releases — `load_from_file` returned `None` and looked like
  "no session there" rather than "this release cannot read what it just wrote".

  The fix is to let the error out, or return a result object carrying the reason. Both
  are **breaking API changes** for anyone currently testing `is None`, so this cannot
  ride in a patch release; it wants a 2.1 or 3.0. The narrower half — not swallowing
  the error when the file exists but fails validation — could land sooner, since
  "file absent" is the only case a caller plausibly treats as normal.

  Same shape as the `bool(result)` footgun fixed in 2.0.0: a failure that presents as
  an ordinary empty value. `tools/session_persistence_check.py` pins the current
  behaviour, so a change here will show up there deliberately rather than by surprise.

- **A documentation auditor, to sit beside the example auditor.**
  `gtpyhop.examples.audit` (2.0.1) answers *"does this example still say what it
  does"* by reading `domain.py` and `problems.py`. It cannot answer the same
  question about `docs/`. Nothing checks that `all_examples.md` still quotes the
  right action count, that a README's scenario table matches measured plan
  lengths, or that a `-> N actions` claim in prose survived a domain change.
  Every one of those went stale at least once while `rikyu_hpc` was being
  written, and each was caught only by a throwaway script.

  Deliberately a **separate tool**, not a fourth family inside the example
  auditor: it audits prose against code, so its inputs are the Markdown tree
  and a planning run, not one example directory. Sketch: extract numeric claims
  near a known example name, resolve them against the live domain and measured
  plans, report mismatches with file and line. The precedent to follow is
  `tools/link_audit.py`, which already does exactly this shape of job for links.

## Further out

### Cost-aware planning (3.0)

Costs on actions and methods, and a search that optimises rather than returning the
first plan it finds. Deferred to a major version because it is not a feature but a
change of contract: cost has to be declared, propagated and compared everywhere, and the
open questions are architectural — actions only or methods too; what admissibility means
when decomposition explores semantically equivalent branches; how cost interacts with
the existing "methods are tried in declaration order" rule.

Sequenced after visualisation deliberately. Visualisation makes search behaviour
legible, and that legibility is worth having *before* the search gets harder to reason
about.

## Not planned

Recorded so the answer is findable rather than re-litigated:

- **Partial-order planning.** GTPyhop is a total-order HTN planner; the examples under
  `ipc-2020-total-order/` are named for that reason.
- **PDDL parsing.** Domains are Python. That is the design, not an omission.
- **Dropping the global API.** `gtpyhop.find_plan` and friends stay. `PlannerSession` is
  recommended for new code, but the original interface is what most published GTPyhop
  material uses.
