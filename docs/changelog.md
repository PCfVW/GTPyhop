# GTPyhop Version History

## 2.0.0 — gtpyhop-core / gtpyhop-examples / gtpyhop Package Split (Latest, Recommended)

This is a packaging-only major release: no planner algorithm changes. GTPyhop is now published as three coordinated PyPI distributions instead of one — plus the optional, independently versioned `gtpyhop-diagnostics`, described below, which is not part of this lockstep release. `pip install gtpyhop` is unaffected and remains a full install, byte-identical to pre-2.0 installs; `pip install gtpyhop-core` is new and gives a lean, examples-free install.

### Package Split (breaking, packaging only)

| Distribution | Contents | Import surface |
|---|---|---|
| `gtpyhop-core` | Planner, structured logging, test_harness, memory_tracking — no bundled examples | `gtpyhop` |
| `gtpyhop-examples` | Bundled example domains; merges into `gtpyhop.examples` as a namespace subpackage; depends on `gtpyhop-core==2.0.0` | `gtpyhop.examples` |
| `gtpyhop` | Meta-package, ships no source of its own; depends on `gtpyhop-core==2.0.0` and `gtpyhop-examples==2.0.0` | `gtpyhop` + `gtpyhop.examples` |

Motivated by two independent concerns: install footprint for production/CI/embedded use, and eliminating the bundled example domains (many files named exactly `domain.py`/`problems.py`) as an unintended "crib channel" reachable by AI agents being evaluated on authoring GTPyhop-format domains.

Repo restructured into `packages/gtpyhop-core/`, `packages/gtpyhop-examples/`, and `packages/gtpyhop/`, each with its own `pyproject.toml`; the old root `src/gtpyhop/` layout and root `pyproject.toml` are gone. `gtpyhop-core`'s `__init__.py` now also carries a mutual-exclusivity guard that detects a pre-2.0 `gtpyhop` install colliding with `gtpyhop-core` in the same environment and raises a clear `ImportError` instead of letting their files silently overwrite each other under `site-packages/gtpyhop/`.

### Execution Diagnostics: `PlanTrace` and correct result truthiness (new)

- **`PlanResult.__bool__` / `ExecutionResult.__bool__`**: both were plain dataclasses with no `__bool__` override, so `bool(result)` was always `True` regardless of `.success` — a documented footgun for any caller tempted to write `if result:` instead of `if result.success:`. Both now return `self.success`.
- **`PlannerSession.find_plan(..., trace=True)`**: opt-in (default `False`, costs nothing when unused — mirrors the existing `memory_tracking` convention). Populates `result.trace`, a `PlanTrace` recording every action-application **and method-refinement** attempt made during the search, in depth-first order: `.events` (depth, item, status), `.dead_end`, `.applied_before_dead_end`, `.malformed_returns`. Covers actions (`_apply_action_and_continue_*`) and task/unigoal/multigoal method refinement (all 9 `_refine_*_and_continue_*` functions) uniformly across all three planning strategies (`recursive_dfs`, `iterative_greedy`, `iterative_dfs_backtracking`), since iterative DFS backtracking shares its action-application code path with plain iterative, and refinement events use one shared recording helper across all three. `result.trace` now also survives an exception raised mid-search (e.g. by a malformed return crashing downstream), instead of being silently lost.
- **`PlannerSession.find_plan(..., trace_state=True)`**: opt-in state snapshots, layered on `trace` (implies it; `trace=True` alone remains free of any snapshotting cost). Each `TraceEvent` gains a `state` field holding a deep copy of the state that item was attempted against — for an action, the state its preconditions were evaluated on, **not** the state the action returned. This supplies the half of failure attribution that static source analysis cannot: reading the domain source yields only the *candidate* set of preconditions guarding a failing action, so naming *which* one actually blocked it requires the state at the moment of the attempt. `TraceEvent.state` is `None` unless requested, and also `None` if the state could not be deep-copied — a domain may put an uncopyable object in a state variable, and a diagnostic facility must not introduce a failure mode into the search it is diagnosing (note GTPyhop already deep-copies the state itself on every action application, so such a domain cannot plan regardless of tracing; the guard only ensures tracing adds nothing new). Snapshots use `copy.deepcopy` rather than `State.copy()` deliberately: the latter renames the copy and increments the global `_next_state_number`, which would let merely *observing* a search change the auto-generated names of states produced after it. Threaded through `isolated_execution()` and all three strategy wrappers via a `_trace_state` global saved and restored alongside `_trace_collector`, so all 33 recording sites snapshot through the one shared helper. Unlike `trace`, this one is not free during a traced search — it costs one deep copy of the state per recorded event, so it is off by default even when tracing: leave it off for benchmarking, turn it on to diagnose a specific failing scenario.
- **An action returning `None` is `not_applicable`, not `malformed_return`.** The first cut of this status set took the failure contract to be "an action returns a `State` or `False`", making every other value — `None` included — a domain-authoring bug. That is wrong for GTPyhop specifically: the canonical `if <preconditions>: <effects>; return s` shape has no `else` and no explicit return, so it falls off the end and yields `None` whenever the guard is false. A census of the bundled examples found **48 of 293 declared actions** rely on exactly that, and they are precisely the nine original collections — `blocks_htn`, `blocks_gtn`, `blocks_hgn`, `blocks_goal_splitting`, `simple_htn`, `simple_hgn`, `logistics_hgn`, `backtracking_htn` and `simple_htn_acting_error`. Tracing them reported GTPyhop's own teaching examples as malformed on every ordinary precondition failure, and contradicted the method-refinement paths, which have always accepted `None` as a plain "not applicable" (`subtasks != False and subtasks != None`). The classification now lives in one place, `_action_failure_status`, shared by the recursive and iterative action paths. `True`, strings and ints remain `malformed_return`, so the motivating real-world defect — an LLM-authored domain whose every action returned `True` instead of the state, silently discarding its effects while appearing to succeed — is still caught exactly as before.
- New `status="malformed_return"` / `"method_malformed_return"` distinguish an action or method that violates its return contract (an action must return `State` or `False`; a method must return a list or `False`/`None`) from a legitimate `"not_applicable"` / exhausted-refinement failure — a domain-authoring bug that was previously indistinguishable from correct behavior. `method_malformed_return` is treated as terminal (unlike `method_applicable`): in practice a malformed method return is used immediately afterward (`subtasks + todo_list`), which raises `TypeError` before the enclosing task/unigoal/multigoal's exhaustion event would ever be reached, so `dead_end` reports the true proximate cause instead of missing it.
- New `status="task_exhausted"` / `"goal_exhausted"` / `"multigoal_exhausted"`, recorded once a task/unigoal/multigoal has tried every candidate method with none succeeding. This closes a real gap found by testing against a genuinely unsolvable scenario from the bundled examples (`ipc-2020-total-order`'s `Blocksworld-GTOHP`, scenario `BW_rand_43`, verified failing in `1.9.7` and `2.0.0` alike): its failure is a goal with no applicable method (`('on', 'b17', 'b42')` at depth 230, after 120 successfully applied actions) — a refinement-level dead end that the original action-only `PlanTrace` was structurally blind to, reporting `dead_end: None` despite the plan definitively failing. `check_solvability.py` (the `mcp-python-ingestion` eval harness this feature was built for) has the same gap in its own attribution logic, which also assumes the dead end is always an action.
- Replaces two fragile patterns for callers that need to know *why* a scenario failed to plan: regex-parsing `verbose=3` debug print output, and reaching into `Domain`'s private `_action_dict`/`_task_method_dict`/`_unigoal_method_dict`/`_multigoal_method_list`. `PlanTrace` provides only mechanical facts (which action or method, at what depth, with what status, and — with `trace_state=True` — the state it was attempted against) — it does not itself attribute failure to a specific precondition or state variable. Naming the culprit means reading the domain source for the failing action's guards and intersecting them with the snapshot; that source-level analysis stays deliberately outside `gtpyhop-core` (tracked separately, not yet built), so the planner ships the runtime evidence without taking on a static-analysis layer.

### `max_expansions` now fails loudly instead of silently doing nothing

`PlannerSession.find_plan(..., max_expansions=N)` has been part of the signature since 1.3.0 but was never implemented: the value is logged and discarded, never reaching `_plan_recursive` / `_plan_iterative` / `_plan_iterative_bt` or any `seek_plan_*` function, none of which even accept such a parameter. A caller asking for a bounded search has silently been given an exhaustive one — a particularly bad failure mode next to `timeout_ms`, its sibling in the same signature, which *is* enforced via `ResourceManager.with_timeout`. Passing a non-`None` value now emits a `UserWarning` (with `stacklevel=2`, so it points at the caller) stating plainly that the parameter is not enforced and suggesting `timeout_ms` instead; the docstring says the same. Behavior is otherwise unchanged, and omitting the parameter — or passing `None` explicitly — stays silent, so no existing caller breaks.

The parameter is deliberately **kept rather than removed**: a deterministic search-effort cap is genuinely wanted alongside `timeout_ms`'s wall-clock cap, notably for bounding a possibly-adversarial machine-generated domain reproducibly. Implementing it is not a small change, which is why it is not in this release: `seek_plan_recursive` has no expansion counter at all (only `seek_plan_iterative` and `seek_plan_iterative_backtracking` keep one, as a local variable driving their periodic cancellation check), and "one expansion" would need a settled definition — those two count main-loop iterations, whereas `PlanTrace.applied_before_dead_end` counts applied *actions*, following `check_solvability.py`'s convention. Related and still outstanding: `result.stats["expansions"]` is always `0`, read as `getattr(self, '_last_expansions', 0)` where `_last_expansions` is never assigned anywhere, so the `getattr` default supplies a plausible-looking zero forever.

### Companion package: `gtpyhop-diagnostics` 0.1.0 (new, versioned separately)

`trace_state` exists to serve a consumer, and that consumer now ships: **`gtpyhop-diagnostics`**, a fourth distribution under `packages/`, which turns *"action `pickup` was not applicable"* into *"`pickup('a')` was blocked by: `s.clear[x] == True`"*. It reads the failing action's guards out of the domain source with the standard library's `ast`, then evaluates each conjunct against the state snapshot the trace recorded — neither half being sufficient alone, since static analysis yields only the *candidate* preconditions and the snapshot alone says nothing about which of them the action required.

Both GTPyhop precondition idioms are handled, which matters because they are structurally inverted: the negative guard-and-bail this project's style guide teaches (`if not (...): return False`, where the requirement is the negation of the test) and the original positive wrapping guard (`if <cond>: <effects>; return s`, where the test *is* the requirement). Measured against every action declared across the bundled collections, **285 of 293 have their guards recognised**; the remaining 8 have no precondition guard to find, being either unconditional (`drive_truck`, `load_truck`, `fly_plane`, `load_plane`, `putv`) or delegating their check to another function (the three `c_pay_driver` commands).

Deliberately **not** versioned in lockstep with the other three: it is `0.1.0`, depends on `gtpyhop-core>=2.0.0` rather than an exact pin, and publishes under its own `diagnostics-v*` tag namespace via its own workflow, so the `v2.0.0` tag sequence is untouched. `publish-one-package.yml` gained an optional `tag_prefix` input (defaulting to `v`) so the tag-vs-`pyproject.toml` version guard still works for a prefixed tag instead of silently skipping. See [its README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-diagnostics/README.md) for usage, coverage and the degradation table.

### Documentation rewritten for the release

`README.md` cut from 556 lines to roughly a third of that, and turned into a landing
page: what GTPyhop is, how to install it, one complete **runnable** first plan, a
one-glance look at failure diagnosis, and an annotated index of everything else. Most of
the reduction was deleting second copies rather than losing material — a 53-entry
example catalogue that [All Examples](all_examples.md) already covers in 62 sections, a
version-by-version function list that is this changelog's job, and sections restating
[Thread-Safe Sessions](thread_safe_sessions.md) and [Running Examples](running_examples.md).
The old Quick Start was abstract skeleton code (`my_action`, `arg1`, `some_condition`)
that could not be pasted and run; it is now a small delivery domain that executes and
prints the plan shown beneath it.

Two new guides:

- **[FAQ](faq.md)** — which of the four distributions to install, the pre-2.0 conflict
  `ImportError`, where `src/gtpyhop/` went, global API versus `PlannerSession`, choosing
  a planning strategy, what an action must return and why `None` is fine, why an action
  is "not applicable", whether GTPyhop optimises plans (it does not), thread safety, and
  running or adding examples.
- **[Diagnostics tutorial](diagnostics_tutorial.md)** — a narrative walkthrough of one
  failing domain, from `find_plan` returning nothing, through `trace=True` (*which*
  action), `trace_state=True` (the state it failed in), to `explain_dead_end` (*which*
  precondition), ending with the cases the analysis honestly cannot answer.

Every code block in both new documents, and in the README, was extracted from the
finished file and executed against a clean install; the outputs shown are the outputs
produced, not reconstructions.

### `gtpyhop-diagnostics` 0.1.0 published

Released to PyPI ahead of the 2.0.0 lockstep tag, deliberately, as a low-stakes canary
for the new publishing setup — an independently versioned package whose rejection would
have cost nothing. It earned its keep: see the note above on publishing from the
top-level workflows, a failure this canary caught that would otherwise have struck the
`v2.0.0` tag itself. The release carries verified PEP 740 attestations.

### Documentation repointed at the new layout

The restructuring left 103 references to the pre-2.0 `src/gtpyhop/examples/` path across `README.md`, `all_examples.md`, `running_examples.md`, `logging.md`, and all three style guides — 75 of them GitHub `blob/pip/src/gtpyhop/examples/...` links that had been 404 since the move, the other 28 copy-pasteable `cd` and `python -m doctest` commands plus prose locations that simply failed. All now point at `packages/gtpyhop-examples/src/gtpyhop/examples/...`; every rewritten link was checked to resolve to a file that exists in the tree, and the corrected `doctest` and `cd`-then-`benchmarking.py` commands were run verbatim from a clean venv install. The worst of these was `gtpyhop_example_style_guide.md` §6, which told a new contributor to create their example at a path that no longer exists in any package.

Two related gaps closed while there. `README.md`'s "Project Structure" diagram still showed the old single-`src/` tree and a root `pyproject.toml` that no longer exists; it now shows the three `packages/` distributions. And "From GitHub" still said `pip install .`, which cannot work without a root `pyproject.toml` — it now installs the two source packages (`pip install packages/gtpyhop-core packages/gtpyhop-examples`, verified end-to-end in a fresh venv, including a full `regression_tests` run), with the editable variant given for contributors. That editable install is now stated as a prerequisite in the example and problems style guides, since the two `src/` trees only merge into one `gtpyhop` import namespace once installed — the next thing that would have failed for a contributor after the paths were corrected.

`changelog.md`'s own occurrences of the old path are deliberately left alone: they are period-accurate descriptions of where files were at the time each version shipped.

### The pre-2.0 conflict guard now tests for an actual collision

`gtpyhop-core`'s import-time guard against a colliding pre-2.0 `gtpyhop` install decided purely on the version number, never checking whether the older distribution still owned any files. That made it fire on a case where nothing collides: an **editable** pre-2.0 install (`pip install -e .` from a dev checkout — how anyone working on GTPyhop itself had it) installs no `gtpyhop/` package directory at all, only a `.pth` pointing at the source tree plus its own dist-info. Every import of `gtpyhop-core` in such an environment raised an `ImportError` describing a file collision that did not exist, and prescribed uninstalling and reinstalling everything to fix a non-problem.

The guard now raises only when the pre-2.0 distribution still owns at least one real `gtpyhop/*.py` file **that exists on disk** — so a stale `RECORD` left by a half-removed install does not resurrect the false alarm either. Where ownership genuinely cannot be determined (no readable `RECORD`), it stays conservative and blocks unless the install is marked editable: being wrong in that direction only asks the user to check, whereas the opposite lets silently overwritten files cause confusing failures later. The message now also states that the files are actually owned, rather than asserting a collision it has not verified.

### Bug Fixes (found while moving files; unrelated to the split itself)

- **`ipc-2020-total-order/benchmarking.py`**: `Blocksworld-GTOHP` and `Childsnack`'s `get_problems()` return `(state, goal, description)` 3-tuples, but this collection's own `main()` passed them straight to the shared `run_multiple()` — which is also called directly by `colt_express`, `trunk_thumper`, `mcp-orchestration`, and `poetry`'s `benchmarking.py`, all of which normalize to a plain `(state, goal)` 2-tuple *before* calling it. `ipc-2020-total-order/main()` was missing that same normalization step, so every batch run of either of its own domains crashed with `ValueError: too many values to unpack`. Fixed by adding the same normalization `main()` already needed, matching the other four callers, rather than changing `run_multiple()`'s shared 2-tuple contract (which would have broken those other four). Confirmed pre-existing and unrelated to the 2.0 restructuring; surfaced while re-running every example collection's benchmarking script after the split.
- **`backtracking_htn.py`, `regression_tests.py`**: both imported `get_recursive_planning` via `from src.gtpyhop.main import ...`, which only ever worked from this specific repo's own dev checkout layout, never from an installed package. Collapsed a 3-tier try/except fallback to `from gtpyhop import get_recursive_planning`, already re-exported publicly.
- **`gtpyhop-examples`** now declares `numpy` as a dependency — used by the `omega_hdq_dna_bacteria_flex_96_channel` MCP-orchestration example, previously undeclared anywhere.

### Verification

Built all three wheels and, in fresh venvs, confirmed: `gtpyhop-core` alone has no `gtpyhop.examples` module; `gtpyhop-core` + `gtpyhop-examples` together pass the full `regression_tests` suite; the `gtpyhop` meta-package transitively installs both with an identical import surface to a pre-2.0 install; and the mutual-exclusivity guard fires correctly against a simulated legacy install. Ran every example collection's benchmarking script (`colt_express`, `ipc-2020-total-order`, `mcp-orchestration`, `poetry`, `trunk_thumper`, `control_arena_protocols` — all three protocol types, `memory_tracking` — light and moderate scenarios) and both doctest-based examples (`android_netrunner`, `cybersecurity_attack_planning`) with no regressions beyond the bugs fixed above, re-run after the `PlanTrace` refinement extension with the same result.

`PlanTrace` verified against a purpose-built synthetic domain covering all three planning strategies × every event type: action `applied`/`idempotent`/`not_applicable`/`malformed_return`; task/unigoal/multigoal `method_applicable`/`method_not_applicable`/`method_malformed_return`; and `task_exhausted`/`goal_exhausted`/`multigoal_exhausted`, each split into a clean-failure case (no crash) and a malformed-method case (search crashes on use, confirming `method_malformed_return`'s terminal status correctly captures the true cause instead of the never-reached exhaustion event) — 27 assertions across 9 scenarios × 3 strategies, plus zero-cost confirmation when `trace=False` and correct behavior under nested `isolated_execution()` usage. Cross-checked end-to-end against the real `BW_rand_43` scenario: `dead_end` now reports the exact goal, depth, and `applied_before_dead_end` count matching a hand-verified `verbose=3` trace.

`trace_state` verified separately by 39 assertions over a purpose-built precondition-guard domain: across all three strategies, that the dead-end event's snapshot exposes the blocking state variable, that every event carries one, and that plain `trace=True` records none; that an action's snapshot is the *pre*-action state while the next action's reflects the previous one's effect; that snapshots are deep copies unaffected by later search mutation; that `trace_state=True` implies `trace=True` while requesting neither still leaves `result.trace` as `None`; that snapshotting preserves state names (guarding the `_next_state_number` regression that `State.copy()` would have caused); and that an uncopyable state variable degrades the snapshot to `None`, leaves the partial trace inspectable, and reports GTPyhop's own pre-existing copy failure rather than a tracing failure. The full `regression_tests` suite was re-run in both legacy and session mode afterward with no regressions.

---

> **Everything below predates the 2.0.0 restructuring.** These entries describe the repository as it was when each version shipped, so bare paths and shell commands in them refer to the old single-`src/` layout — `src/gtpyhop/examples/...`, where today the same files live under `packages/gtpyhop-examples/src/gtpyhop/examples/...`. They are left as written because rewriting them would misreport what those releases actually contained; a command copied from a pre-2.0 entry therefore needs its path adjusted before it will run. Links in these entries *are* kept current, since a link's job is to reach the file as it exists now. See the 2.0.0 entry above for the current layout.

## 1.9.7 — Colt Express Collection + Control Arena adversarial_protocol Extension

This version closes the 1.9 minor on the "examples" theme. It adds the **Colt Express** example collection (a 5-sub-folder pedagogical collection mirroring `trunk_thumper`'s pattern catalog applied to the published board game) and **extends the existing `adversarial_protocol/`** sub-folder of `control_arena_protocols/` with three additive features. No planner changes; pure additions to the example library.

### Colt Express Example Collection (new)

Added a new example collection under `colt_express/` modeled on the [Colt Express board game](http://www.coltexpress.ludonaute.fr) (Christophe Raimbault / Jordi Valbuena, Ludonaute 2014). The collection mirrors the structural template of the `trunk_thumper` collection — each sub-folder demonstrates one HTN concept with a direct lineage to a `trunk_thumper` sub-folder, but applied to a richer multi-bandit / Marshal-driven domain.

| Aspect | Value |
|--------|-------|
| Sub-folders | 5 |
| Total actions across sub-folders | 26 |
| Total scenarios | 16 (incl. 1 designed-failure negative control) |
| Doctests | 124 |
| `MCP_Tool:` | `None` (purely symbolic) |
| LOC | ~6,600 |

**Sub-folder layout** (numeric prefix reflects **build order**, not pattern depth):

| Folder | Pattern source | Topic |
|---|---|---|
| `s1_minimal_turn/` | trunk_thumper `s03` | Priority methods: rob-if-loot vs. move-forward baseline |
| `s3_marshal_expected_effects/` | trunk_thumper `s07` | `[EXPECTED_EFFECT]` tag for Marshal forced-escape + negative control |
| `s2_recursive_round/` | trunk_thumper `s06` | Recursive deck resolution (head-pop termination) + hostage-taking event |
| `s4_character_priorities/` | trunk_thumper `s08` | Priority-method ladder for Belle / Tuco / Django / Cheyenne abilities |
| `s5_partial_plan_movement/` | trunk_thumper `s10` | Method-split partial plans for movement strategy |

**Scope:** Stealin'-phase only. The programmed deck is pre-encoded in `state.deck` and the planner resolves it action-by-action, filling in parameter choices (Move direction, Fire target, Robbery pick). The Schemin' phase (strategic card selection under imperfect information) is out of scope for classical HTN.

**Key features:**
- Canonical state schema shared **byte-identically** across all 5 sub-folders (`h_create_base_state`, `h_sample_car_loot`, `COLT_EXPRESS_LOOT_DISTRIBUTION`)
- Documented physical loot distribution + deterministic `h_sample_car_loot(seed, num_jewels, num_purses)` sampler
- 4 of 6 characters modeled (Belle, Tuco, Django, Cheyenne); Ghost and Doc deferred
- s3 includes a negative-control scenario demonstrating why `[EXPECTED_EFFECT]` is needed (mirrors trunk_thumper s07 scenario 3)
- s5 demonstrates the partial-plan reactivity argument via same-state contrast between full-plan and partial-plan task names

**Files added (24):**
- Collection: `colt_express/{__init__.py, README.md, benchmarking.py, benchmarking_quickstart.md}`
- Per sub-folder (×5): `{__init__.py, domain.py, problems.py, README.md}`

**Reference:** Raimbault, C., and Valbuena, J. *Colt Express*. Ludonaute / Asmodee, 2014.

---

### Control Arena `adversarial_protocol/` Extension

Extended the existing `adversarial_protocol/` sub-folder (1.9.4 baseline) with three additive changes. No new sub-folders; all changes within the sub-folder.

**Threat-model variety:**
- New state field `config_threat_model: str` — `'none' | 'generic' | 'code_sabotage' | 'data_poisoning' | 'research_sabotage'`
- `config_detection_rates` schema migrated from flat `Dict[subtlety, float]` to nested `Dict[threat_model, Dict[subtlety, float]]`
- 6 new scenarios — one VULNERABILITY + one SAFE per threat type. Detection rates encode the empirical pattern that generic monitors are systematically weaker against data-distribution and research-output attacks than against code-level sabotage at the same subtlety
- Existing 8 scenarios migrated to `threat_model='generic'` or `'none'`, preserving exact numerics

**`[EXPECTED_EFFECT]` marker — first use in this collection:**
- `a_accept_output` gains an `[EXPECTED_EFFECT]` block: when the accepted output embeds a side task, `state.side_task_observed = True`. This models the deployment executor's downstream side-task firing — a sensor-driven effect, not directly produced by the acceptance operator. Pattern source: `trunk_thumper/s07` and `colt_express/s3`.

**Negative-control variant action:**
- `a_accept_output_demo_no_expected_effect` — byte-identical to `a_accept_output` except the `[EXPECTED_EFFECT]` block is omitted. Used only in scenario_15 (manual task list bypassing routing methods). The plan succeeds with 5 actions, but `state.side_task_observed` is never set — empirically demonstrating why the tag is load-bearing.

**Benchmark classifier:**
- `benchmarking.py` adds a new `accept_no_ee` outcome label (in addition to `accept`, `defer`, `unknown`) so the negative-control scenario is visually distinguishable from canonical accept paths in the summary table.

**Aggregate (1.9.4 → 1.9.7):** actions 7 → 8, methods 7 → 7 (unchanged), scenarios 8 → 15, doctests 56 → 92.

**Files modified (4):** `adversarial_protocol/{domain.py, problems.py, README.md}`, `control_arena_protocols/{README.md, benchmarking.py}`.

---

### Doctest count

Current total: **789 doctests** across all `problems.py` files. Verified during 1.9.7 prep by running `python -m doctest -v` on every example's `problems.py`. The 1.9.7 release adds **+160 doctests** (+124 from the Colt Express collection, +36 from the `adversarial_protocol/` extension); the pre-1.9.7 baseline is therefore 789 − 160 = 629.

Note: the previous Doctests badge value of `208` (used on `pip`-branch READMEs since 1.9.x) was a stale incremental estimate, not an audited total. The 1.9.7 badge update reflects the audited count.

---

### Documentation

- `docs/all_examples.md` gets a new top-level "Colt Express Game-AI Examples (1.9.7+)" section and an extended "Adversarial Protocol (1.9.4 baseline, extended in 1.9.7)" subsection
- `README.md` (main) restructures the Control Arena Protocol Examples list into "1.9.4 baseline" and "1.9.7 extension" subsections so readers can see at a glance which content shipped in which version
- All version-context references in user-facing READMEs use **1.9.4 / 1.9.7** language (date stamps in source files like `# Generated 2026-05-16` kept as historical metadata)
- New `src/gtpyhop/examples/control_arena_protocols/benchmarking_quickstart.md` (~150 LOC), matching the quickstart pattern used by the other 5 multi-folder example collections. Outcome-label catalog (`accept` / `defer` / `accept_no_ee` / `unknown`) and per-scenario expected-plan-length tables for all 27 scenarios across the three sub-folders
- Missing main-README link to `poetry/benchmarking_quickstart.md` added; "MCP Benchmarking" link relabeled to "MCP Benchmarking Quickstart" for naming consistency across all 7 quickstart links

### Style guide update

`docs/gtpyhop_domain_style_guide.md` §8.4 (EXPECTED_EFFECT Tag Guidelines) was expanded to reflect the tag's new in-repo usages:

- The "When to use" criteria now distinguish **two flavors of load-bearing role**:
  - **Workflow-gating flavor** — omitting the tag breaks a downstream action's precondition; the plan *fails* (trunk_thumper s07, colt_express s3)
  - **Observability flavor** — omitting the tag leaves a state property unset that downstream inspection or scoring reads; the plan *succeeds* but a safety/correctness invariant is silently broken (adversarial_protocol — new in 1.9.7)
- The "Pedagogical reference" paragraph was replaced with a **3-row table** covering all three in-repo example implementations: `trunk_thumper/s07_expected_effects_chase/` (1.9.6, workflow-gating), `colt_express/s3_marshal_expected_effects/` (1.9.7, workflow-gating), and `control_arena_protocols/adversarial_protocol/` (1.9.7, observability)
- New "Note on the two flavors" paragraph after the table elaborates why the observability flavor is subtler: the tag's value comes from making implicit external-system side effects auditably present in the planner's state, even when no downstream precondition reads them

The observability-flavor distinction is new to 1.9.7 because it's a property of the `adversarial_protocol` extension. trunk_thumper's §8.4 introduction (1.9.6) implicitly assumed the workflow-gating flavor; 1.9.7's `adversarial_protocol` is the first example whose negative-control scenario *succeeds* rather than failing.

---

## 1.9.6 — Android: Netrunner + Trunk Thumper Game-AI Examples

This version adds two new example domains: Android: Netrunner (one-shot card-game run planning) and Trunk Thumper (progressive game-AI tutorial based on Troy Humphreys' canonical *Game AI Pro* chapter).

### Trunk Thumper Game-AI Example Collection (new)

Added a new example collection under `trunk_thumper/` that translates **Troy Humphreys' "Exploring HTN Planners through Example"** (*Game AI Pro 1*, Steve Rabin, ed., CRC Press, 2015, pp. 149–167) into self-contained GTPyhop examples — one sub-folder per chapter section. The chapter is the canonical pedagogical reference for HTN planning in game NPC behavior selection, based on the production system used in *Transformers: Fall of Cybertron* (HighMoon Studios / Activision, 2012). This collection fills a real gap: GTPyhop now has a first-class example targeting the **game AI developer** audience that has historically been HTN's largest user base.

| Aspect | Value |
|--------|-------|
| Sub-folders | 6 (one per chapter section) |
| Total actions across sub-folders | 33 |
| Total scenarios | 18 (incl. 1 designed-failure negative control) |
| Doctests | ~85 (sub-folder by sub-folder) |
| `MCP_Tool:` | `None` (purely symbolic) |

**Sub-folder layout** (naming `sNN_<topic>` maps to chapter section §12.NN):

| Folder | Chapter | Topic |
|---|---|---|
| `s03_basic_attack_or_patrol/` | §12.3 | Baseline BeTrunkThumper domain (attack or patrol) |
| `s06_recursive_trunk_replacement/` | §12.6 | Recursion: m_attack_enemy recurses via FindTrunk → UprootTrunk → AttackEnemy |
| `s07_expected_effects_chase/` | §12.7 | The new `[EXPECTED_EFFECT]` tag, demonstrated with a negative-control scenario |
| `s08_priority_methods/` | §12.8 | Multi-method m_attack_enemy with WsPowerUp / WsIsTired / boulder fallback |
| `s09_simultaneous_navigation_and_guard/` | §12.9 | Single-planner non-blocking navigation with simultaneous guard |
| `s10_partial_plans/` | §12.10 | Manual method-split partial plans for reactivity |

**Key features:**
- Sub-folder names match chapter section numbers — readers of the book can match code to text by §
- Self-contained sub-folders: each has its own `__init__.py / domain.py / problems.py / README.md`
- `[EXPECTED_EFFECT]` tag introduced for the chapter's "expected effects" concept (semantically identical to `[DATA]` in GTPyhop; pedagogical/documentary)
- s07 includes a deliberate negative-control scenario that uses a teaching-variant action omitting the `[EXPECTED_EFFECT]` — the plan correctly fails, empirically demonstrating *why* the tag is needed
- s08 implements both sub-stories from §12.8 together (boulder fallback + WsIsTired-gated whirlwind combo)
- Collection-level `benchmarking.py` and `benchmarking_quickstart.md` mirror the `poetry/` infrastructure for batch-running sub-folder scenarios
- MTR (runtime priority comparison from §12.8) and plan runner / sensors (§12.5) are documented as out of scope — GTPyhop's planning-time method ordering captures the chapter's underlying priority concept

**Files added (28):**
- Collection: `trunk_thumper/{__init__.py, README.md, benchmarking.py, benchmarking_quickstart.md}`
- Per sub-folder (×6): `{__init__.py, domain.py, problems.py, README.md}`

**Style guide update:** `docs/gtpyhop_domain_style_guide.md` Section 8 was renamed "Metadata Tags: DATA, ENABLER, and EXPECTED_EFFECT" and gained a new subsection 8.4 with definition, usage guidelines, and reference to s07.

**Reference:**
Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, pp. 149–167.

**Acknowledgment:** With warm thanks to Troy Humphreys, whose chapter is the structural blueprint for this entire collection. The Trunk Thumper is his.

---

### Release-infrastructure improvements

The PyPI publish workflow (`.github/workflows/publish-new-GTPyhop-to-pypi.yml`) was reworked. None of these changes affect the runtime API; they change how releases are produced and observed.

- **Tag-triggered** instead of `pyproject.toml`-touch-triggered. Pushes to `pip` no longer publish; only pushes of tags matching `vMAJOR.MINOR.PATCH` do (e.g. `v1.9.7`). Hyphenated tags (e.g. `v1.9.7-rc1`) are git-only checkpoints and never publish. A new consistency step verifies the pushed tag matches `pyproject.toml`'s version and fails loudly if they diverge.
- **Dry-run mode** via `workflow_dispatch` with a `dry_run` boolean input (default `true`). Manual runs build, validate, and run every check *except* the upload, then print a `⚠ DRY RUN` markdown banner to `$GITHUB_STEP_SUMMARY` listing the artifacts that would have been published. The Actions UI also prefixes dry-runs with `[DRY RUN]` via a dynamic `run-name:`, so a successful dry-run is visually distinguishable from a real publish in the run list.
- **`twine check dist/*`** validates wheel/sdist metadata after build, before publish. Catches metadata problems (`long_description` rendering, classifiers, version format) that PyPI would otherwise reject post-upload.
- **`actions/checkout` and `actions/setup-python` bumped to `@v6`** for Node 24 compatibility (Node 20 deprecated on GitHub Actions runners; full removal scheduled September 2026).

**Pattern source:** Trigger conventions adapted from sibling Rust-crate publish workflows (`candle-mi/`, `hf-fetch-model/`, `anamnesis/`).

---

### Android: Netrunner Run Planning Example (new)

Added a new example domain under `android_netrunner/` that models a single Runner-side **run** against a configured Corporation server stack, using the published mechanics of Fantasy Flight Games' *Android: Netrunner* (2012 core set rulebook). The flagship scenario faithfully replicates the worked run example on **page 19 of the core rulebook**: Bart's run against Olivia's remote server with Enigma, Wall of Thorns, Akitaro Watanabe, and a Nisei MK II agenda — Jinteki Personal Evolution identity included.

| Aspect | Value |
|--------|-------|
| Actions | 24 (Setup: 3, Run flow: 4, Encounter: 5, Sub resolution: 5, Cleanup: 3, Access: 4) |
| Methods | 31 method functions across 17 task names (6 backtracking points) |
| Scenarios | 8 (5 require backtracking, 2 designed greedy failures) |
| Doctests | 64 |
| `MCP_Tool:` | `None` (purely symbolic) |
| Card subset | 14 named cards from the core set (full per-card fidelity) |

**Key features:**
- Per-card fidelity for the 14 cards used in the rulebook's run example: Ice Wall, Wall of Thorns, Enigma, Data Raven, AstroScript Pilot Program, Nisei MK II, Aggressive Secretary, Akitaro Watanabe, Corroder, Gordian Blade, Wyrm, Crypsis, The Toolbox, Sacrificial Construct
- Three state scopes distinguished: encounter (Corroder/Crypsis pumps, Wyrm drain), run (Gordian pump), persistent (virus counters)
- 6 backtracking points: icebreaker selection (8 alternatives), Crypsis end-of-encounter cleanup (4), Data Raven on-encounter ability (2), ambush firing (2), asset/upgrade trash decisions (2 each)
- Greedy planner failure on scenarios 3 (rulebook replication) and 6 (accept net damage), demonstrating deep credit-management backtracking
- Per-scenario Corp policy configuration: rez plan, ambush firing, trace budget, ambush trash priorities — Corp is configured environmental state rather than a planning agent

**Files added (4):** `android_netrunner/{__init__.py, domain.py, problems.py, README.md}`

**Style guide update:** `docs/gtpyhop_example_style_guide.md` gained a new section 8 ("Debugging Tips") documenting `verbose=3` and GTPyhop's idempotent-action elision — actions that produce no state change are processed but omitted from `result.plan`. This was discovered while building scenario 3, where `a_pass_ice` and `a_resolve_lose_click` are both idempotent in context (Ice Wall not rezzed; Runner has 0 clicks remaining).

**Reference:**
Garfield, R. (designer), and Litzsinger, L. (developer). *Android: Netrunner — The Card Game, Rules of Play* (Fantasy Flight Games, 2012). The page-19 worked example drives the flagship scenario.

---

## 1.9.5 — Cybersecurity Attack Planning Example

### Cybersecurity Attack Planning Example (new)

Added a new example domain under `cybersecurity_attack_planning/` that models insider attacks against a network Document Management System, based on the BAMS (Behavioral Adversary Modeling System) domain from Boddy et al. (ICAPS 2005) and the hierarchy design by Pragst (2013/2014).

| Aspect | Value |
|--------|-------|
| Actions | 21 (5 Physical, 4 Process, 2 Network, 6 DMS, 4 Malware) |
| Methods | 16 (5 backtracking points) |
| Scenarios | 9 |
| Doctests | 71 |
| `MCP_Tool:` | `None` (purely symbolic) |

**Key features:**
- Two top-level attack strategies: legitimate DMS access vs. covert malware relay
- 5 backtracking points across credential acquisition, document access, exfiltration, DMS authentication, and malware deployment
- 4 scenarios demonstrating greedy planner failure and backtracking recovery (S4, S7, S8, S9)
- Covers both sides of AI safety/security together with the control arena protocol examples (attacker vs. defender)

**Files added (4):** `cybersecurity_attack_planning/{__init__.py, domain.py, problems.py, README.md}`

**References:**
1. Boddy, M. et al. (2005). "Course of Action Generation for Cyber Security Using Classical Planning." ICAPS 2005.
2. Boddy, M., Shackleton, H. (2007). "The BAMS — Console Based Generator." ICKEPS 2007.
3. Pragst, L. (2013). "Hybrid Planning in Cyber Security Applications." BSc thesis, Ulm University.
4. Pragst, L. et al. (2014). "Introducing Hierarchy to Non-Hierarchical Planning Models." PuK 2014.

---

## 1.9.4 — Control Arena Protocol Examples & MCP_Tool: None

### Control Arena Protocol Examples (new)

Added **3 new example domains** under `control_arena_protocols/` that formalize AI safety micro-protocols from the [Control Arena](https://github.com/UKGovernmentBEIS/control-arena) framework (Greenblatt et al. 2024) using HTN planning with backtracking. All use `MCP_Tool: None`.

| Example | Actions | Methods | Scenarios | Key feature |
|---------|---------|---------|-----------|-------------|
| `defer_to_trusted_protocol/` | 6 | 4 | 6 | Backtracking on routing (accept vs. defer) |
| `defer_to_resample_protocol/` | 6 | 5 | 6 | Recursive resampling + backtracking |
| `adversarial_protocol/` | 7 | 7 | 8 | Adversarial analysis + vulnerability detection |

**Total:** 19 actions, 16 methods, 20 scenarios, 144 doctests.

**Files added (15):**
- Collection: `control_arena_protocols/{__init__.py, benchmarking.py, README.md}`
- Per example: `{__init__.py, domain.py, problems.py, README.md}` (x3)

### MCP_Tool: None for non-MCP domains

The domain style guide now allows `MCP_Tool: None` for actions that have no external MCP server binding and operate purely on the planning state. Previously, non-MCP examples were forced to invent fictitious server names (e.g., `memory_server:initialize`) to satisfy the mandatory `MCP_Tool:` docstring field.

**Style guide changes:**

| File | Change |
|------|--------|
| `docs/gtpyhop_domain_style_guide.md` (line 281) | Table: `MCP server:tool mapping` → `MCP server:tool mapping (or "None" if no external server)` |
| `docs/gtpyhop_domain_style_guide.md` (line 784) | BNF: `"MCP_Tool:" server_name ":" tool_name` → `"MCP_Tool:" ( "None" \| server_name ":" tool_name )` with explanatory comment |

**Memory tracking examples updated:**

| File | Lines changed | Before | After |
|------|--------------|--------|-------|
| `memory_tracking/scalable_data_processing/domain.py` | 6 actions | `MCP_Tool: memory_server:*` | `MCP_Tool: None` |
| `memory_tracking/scalable_recursive_decomposition/domain.py` | 3 actions | `MCP_Tool: memory_server:*` | `MCP_Tool: None` |

### Documentation updates

- **[All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)** — Added Control Arena Protocol Examples section (3 examples, scenario tables, educational value, benchmarking commands)

**Verified:** All 20 control arena scenarios, all 12 memory tracking scenarios, and all 7 poetry example doctests (137 tests) pass.

**Compatibility:** 100% backward compatible with GTPyhop 1.9.3. No API changes. Existing `MCP_Tool: server:tool` values remain valid.

---

## 1.9.3 — Doctests for All Poetry Examples

Added **doctests** to `get_problems()` in all 6 remaining poetry examples, matching the pattern established in `feature_space_poetry/problems.py`. Every poetry example now includes inline plan verification tests.

**Files updated:**

| Example | Scenarios tested | Key verifications |
|---------|-----------------|-------------------|
| `structured_poetry/problems.py` | 6 | Plan lengths: 8, 17, 8, 44, 8, 17 |
| `backtracking_poetry/problems.py` | 3 + greedy failure | Relaxed rhyme on limerick line 4; greedy fails |
| `bidirectional_planning_poetry/problems.py` | 3 | Plan lengths: 10, 22, 8 |
| `candidate_planning_poetry/problems.py` | 3 | Plan lengths: 12, 27, 8 |
| `formal_mechanism_poetry/problems.py` | 3 + stage inspection | Formulated stage names; plan lengths: 19, 7, 13 |
| `replanning_poetry/problems.py` | 3 + greedy failures | `a_evaluate_line` / `a_steer_target` sequences; greedy fails on couplet and limerick |

**Total:** 137 doctests across all 7 poetry examples (including the existing 31 in `feature_space_poetry`).

**Running all doctests:**

```bash
python -m doctest -v src/gtpyhop/examples/poetry/structured_poetry/problems.py
python -m doctest -v src/gtpyhop/examples/poetry/backtracking_poetry/problems.py
python -m doctest -v src/gtpyhop/examples/poetry/bidirectional_planning_poetry/problems.py
python -m doctest -v src/gtpyhop/examples/poetry/candidate_planning_poetry/problems.py
python -m doctest -v src/gtpyhop/examples/poetry/formal_mechanism_poetry/problems.py
python -m doctest -v src/gtpyhop/examples/poetry/replanning_poetry/problems.py
python -m doctest -v src/gtpyhop/examples/poetry/feature_space_poetry/problems.py
```

**Style guide updates:**
- **[Problems Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md)** — Updated reference implementations section to note all 7 poetry examples include doctests
- **[Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md)** — Updated section 7 to reference all 7 poetry examples as implementations

**Compatibility:** 100% backward compatible with GTPyhop 1.9.2. No API changes.

---

## 1.9.2 — Feature Space Poetry: Word-Level CLT 2.5M Scenarios

**Feature Space Poetry** expanded from 8 to **12 scenarios** with the addition of 4 Gemma 2 2B + CLT 2.5M (Version D 2.5M) scenarios:

| Scenario | Description | Actions | Backtracking | Greedy |
|----------|-------------|---------|-------------|--------|
| 8: 2.5M star result | Ground truth (out→an, "can" at 48.2%) | 34 | No | SUCCESS |
| 9: 2.5M weakest first | "plan" before "can" | 34 | Yes (2 failures) | **FAIL** |
| 10: 2.5M planning layer | Only L25 encoded | 9 | No | SUCCESS |
| 11: 2.5M different group | oo→an, lower threshold | 10 | Yes (1 failure) | **FAIL** |

**Key upgrade over 426K CLT:** 2.5M CLT provides 98,304 features/layer (vs 16,384), giving word-level resolution — 209/209 words ranked #1 in their own dedicated feature. The star result "can" (L25:82839) achieved 48.2% redirect probability with a 160-billion-fold spike. Same Gemma 2 2B model, finer CLT = word-level control.

**Feature Space Poetry now covers three configurations:**

| Configuration | Scenarios | Layers | CLT Resolution | Star Result |
|---------------|-----------|--------|----------------|-------------|
| Gemma 2 2B (Version D) | 0-3 | 26 | 426K | "around" at 48.3% |
| Llama 3.2 1B (Version L) | 4-7 | 16 | 524K | "that" at 77.7% |
| Gemma 2 2B (Version D 2.5M) | 8-11 | 26 | 2.5M | "can" at 48.2% |

**Documentation updates:**
- **[All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)** — Updated Feature Space Poetry section (8→12 scenarios, added 2.5M scenario table)
- **[Poetry README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/README.md)** — Updated scenario counts, strategy table, directory structure; added 2.5M scenario table
- **[Poetry Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/benchmarking_quickstart.md)** — Updated expected results with all 12 scenarios; updated troubleshooting
- **[Feature Space Poetry README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/feature_space_poetry/README.md)** — Added 2.5M scenarios, empirical grounding, decomposition examples; updated domain statistics

**Compatibility:** 100% backward compatible with GTPyhop 1.9.1. No API changes.

---

## 1.9.1 — Poetry Examples & Bug Fixes

🚀 **Major Features:**
- **🔀 Iterative DFS Backtracking** - Third planning strategy combining the iterative planner's explicit stack with full backtracking across methods
- **📝 Poetry Examples** - Seven poetry generation domains demonstrating structured, backtracking, candidate planning, bidirectional, replanning, formal mechanism, and feature-space HTN planning

**Iterative DFS Backtracking:**

GTPyhop 1.8.0 provided two planning strategies: recursive DFS (backtracks via Python call stack) and iterative greedy (commits to first applicable method, no backtracking). The iterative greedy planner could not recover when a chosen method's subtasks failed downstream.

GTPyhop 1.9.1 adds a third strategy — **iterative DFS with backtracking** — that pushes all applicable method continuations onto an explicit stack. If one path fails, the planner falls back to the next alternative. This provides the same correctness as recursive DFS without Python's recursion depth limit.

| Strategy | Backtracking? | Stack | Activation |
|----------|:------------:|-------|------------|
| Recursive DFS | Yes | Python call stack | `set_recursive_planning(True)` |
| Iterative greedy | No | Explicit stack | `set_recursive_planning(False)` |
| **Iterative DFS BT** | **Yes** | **Explicit stack** | `set_recursive_planning("iterative_dfs_backtracking")` |

**New Internal Functions (purely additive — no existing function removed or modified):**
- `seek_plan_iterative_backtracking` - Main iterative loop with multi-continuation stack
- `_refine_task_and_continue_iterative_bt` - Returns all applicable task method continuations
- `_refine_unigoal_and_continue_iterative_bt` - Returns all applicable unigoal method continuations
- `_refine_multigoal_and_continue_iterative_bt` - Returns all applicable multigoal method continuations

**API Changes (backward-compatible):**
- **`set_recursive_planning(strategy)`** - Now accepts string values in addition to `True`/`False`:
  - `"recursive_dfs"` (same as `True`)
  - `"iterative_greedy"` or `"iterative_irrevocable_commitment"` (same as `False`)
  - `"iterative_dfs_backtracking"` (new)
  - Existing `True`/`False` callers are unaffected (`isinstance(strategy, bool)` dispatch)
- **`PlannerSession(strategy=...)`** - New optional keyword parameter:
  - `PlannerSession(strategy="iterative_dfs_backtracking")` activates the new strategy
  - When `strategy` is `None` (default), the existing `recursive` bool parameter drives behavior identically to 1.8.0
  - `PlannerSession.recursive` is now a derived property (`self._strategy == "recursive_dfs"`)
- **`PlannerSession.isolated_execution()`** - Restore logic simplified to direct function reference assignment, correctly handling all three strategies
- **`SessionSerializer`** - Serialization includes the `strategy` field; deserialization falls back to `recursive` bool for data from older versions
- **Result stats `"strategy"` field** - Now reports the full strategy name (`"recursive_dfs"`, `"iterative_greedy"`, or `"iterative_dfs_backtracking"`) instead of the previous binary `"recursive"` / `"iterative"`

**Usage Examples:**
```python
# Global API
import gtpyhop
gtpyhop.set_recursive_planning("iterative_dfs_backtracking")
plan = gtpyhop.find_plan(state, tasks)

# Session API
with gtpyhop.PlannerSession(
    domain=my_domain,
    strategy="iterative_dfs_backtracking"
) as session:
    result = session.find_plan(state, tasks)
```

**New Examples:**

The seven poetry examples form a progression, each extending the baseline with a different aspect of Anthropic's "[Planning in Poems](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems)" (March 2025) findings:

| # | Example | Directory | Description | Strategy |
|---|---------|-----------|-------------|----------|
| 1 | **Structured Poetry** | `poetry/structured_poetry/` | Baseline: select → generate → verify (6 scenarios) | Any |
| 2 | **Backtracking Poetry** | `poetry/backtracking_poetry/` | Strict/relaxed methods with backtracking (3 scenarios) | Backtracking |
| 3 | **Candidate Planning Poetry** | `poetry/candidate_planning_poetry/` | Multi-candidate rhyme selection pipeline (3 scenarios) | Any |
| 4 | **Bidirectional Planning Poetry** | `poetry/bidirectional_planning_poetry/` | Decomposed backward line construction (3 scenarios) | Any |
| 5 | **Replanning Poetry** | `poetry/replanning_poetry/` | Post-generation evaluation and steering/revision (3 scenarios) | Backtracking |
| 6 | **Formal Mechanism Poetry** | `poetry/formal_mechanism_poetry/` | Three planning mechanisms from Anthropic's [paper](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems) (3 scenarios) | Any |
| 7 | **Feature Space Poetry** | `poetry/feature_space_poetry/` | Feature-space interventions with measured data: Gemma 2 2B (Version D) + Llama 3.2 1B (Version L) (8 scenarios) | Backtracking |

- **Backtracking Poetry** (example 2) — Tests action-level failure triggering method-level backtracking at the line composition level:

| Strategy | Couplet (8) | Limerick (17) | Haiku (8) |
|----------|:-------:|:--------:|:-----:|
| Recursive DFS | 8 actions | 17 actions | 8 actions |
| Iterative greedy | 8 actions | **Fails** | 8 actions |
| Iterative DFS BT | 8 actions | 17 actions | 8 actions |

- **Replanning Poetry** (example 5) — Tests action-level failure triggering method-level backtracking at the evaluation level. Models the paper's finding that injecting an alternative planned word causes the model to restructure the entire line in 70% of test poems:

| Strategy | Couplet (12) | Limerick (28) | Haiku (8) |
|----------|:-------:|:--------:|:-----:|
| Recursive DFS | 12 actions | 28 actions | 8 actions |
| Iterative greedy | **Fails** | **Fails** | 8 actions |
| Iterative DFS BT | 12 actions | 28 actions | 8 actions |

- **Candidate Planning Poetry** (example 3) — Replaces single rhyme target selection with a 3-action pipeline (generate candidates → rank → commit). Plan lengths: Couplet: 12, Limerick: 27, Haiku: 8.

- **Bidirectional Planning Poetry** (example 4) — Splits line generation into backward transition planning and forward surface text generation. Plan lengths: Couplet: 10, Limerick: 22, Haiku: 8.

- **Formal Mechanism Poetry** (example 6) — Implements three planning mechanisms from the paper (full pipeline, commitment focus, three-stage). All 3 scenarios succeed with any strategy. Plan lengths: 19, 7, 13.

- **Feature Space Poetry** (example 7) — Probability-based evaluation using measured experimental data. Eight scenarios across two models: Gemma 2 2B (Version D, 4 scenarios) and Llama 3.2 1B (Version L, 4 scenarios). Each model has a ground truth replication plus counterfactual what-ifs. Scenarios requiring backtracking fail with the greedy strategy:

| Strategy | Gemma S0 (34) | Gemma S1 (34) | Gemma S2 (9) | Gemma S3 (10) | Llama S4 (24) | Llama S5 (24) | Llama S6 (9) | Llama S7 (10) |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Iterative DFS BT | 34 | 34 | 9 | 10 | 24 | 24 | 9 | 10 |
| Iterative greedy | 34 | **Fails** | 9 | **Fails** | 24 | **Fails** | 9 | **Fails** |

**Poetry benchmarking script** updated with `--strategy` option:
```bash
cd src/gtpyhop/examples/poetry
python benchmarking.py structured_poetry                                    # default strategy
python benchmarking.py backtracking_poetry --strategy recursive_dfs         # requires backtracking
python benchmarking.py replanning_poetry --strategy iterative_dfs_backtracking  # requires backtracking
python benchmarking.py formal_mechanism_poetry                                 # works with any strategy
python benchmarking.py feature_space_poetry --strategy iterative_dfs_backtracking  # requires backtracking
```

**Documentation & Style Guides:**
- **[All Examples Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/all_examples.md)** — Updated with examples 6-7 (sections, summary table, benchmarking commands)
- **[Poetry README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/README.md)** — Updated with examples 6-7 (tables, directory structure, server architectures); fixed example 6 strategy classification (Backtracking → Any); added comprehensive MCP section (Why MCP?, server configurations, MCP reference summary)
- **[Poetry Benchmarking Quickstart](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/benchmarking_quickstart.md)** — Updated with examples 6-7 (expected results, troubleshooting, strategy tables)
- **[Feature Space Poetry README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/poetry/feature_space_poetry/README.md)** — Added Llama 3.2 1B scenarios (4-7); fixed server architecture (suppress_group moved to clt_server); fixed method count (5, not 7); added Appendix on state restoration and backtrack with MI and AI planning implications
- **[Problems Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md)** — v2.2.0: added section 2.3 on doctests in `get_problems()` with template and conventions
- **[Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md)** — v1.2.0: added section 7 on doctests for plan verification; updated checklist and quick start template

**Bug Fixes:**
- Fixed Unicode encoding issue in IPC benchmarking `print_summary`: replaced non-ASCII characters (Delta, checkmark, cross) with ASCII equivalents for Windows cp1252 compatibility
- Fixed `--verbose` flag handling in poetry `benchmarking.py` (was not being passed to planner sessions)
- Added plan validation to poetry benchmarking (verifies plan is a list, not just truthy)

**Compatibility:** 100% backward compatible with GTPyhop 1.8.0. All existing `True`/`False` callers produce identical behavior.

---

## 1.8.0 — Memory Tracking & Scalability Examples
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.8.0/**

🚀 **Major Features:**
- **📊 Memory Tracking** - Real-time memory monitoring during planning with `psutil`
- **🔬 Scalability Examples** - Two new examples demonstrating HTN planning complexity
- **⚡ Zero-Overhead Design** - Memory tracking has no overhead when disabled

**Memory Tracking Architecture:**
- **`ResourceManager`** - Singleton manager for memory monitoring
  - `ResourceManager.reset()` - Clear all cached state for fresh benchmarking
  - `ResourceManager.sample_memory()` - Explicit memory sampling for fast operations
- **`MemoryMonitor`** - Background thread for continuous memory sampling
  - Configurable sampling interval (default 0.1s, use 0.001s for fast scenarios)
  - `sample_now()` - Force immediate memory sample
  - `stop()` - Fully terminate monitoring thread
- **`PlannerSession` Integration** - New parameters:
  - `memory_tracking=True` - Enable memory monitoring
  - `memory_sampling_interval=0.001` - Set sampling interval in seconds
- **Session Statistics** - New result fields:
  - `result.stats['memory_mb']` - Memory used during planning
  - `result.stats['peak_memory_mb']` - Peak memory observed

**New Examples:**

| Example | Directory | Description |
|---------|-----------|-------------|
| **Scalable Data Processing** | `memory_tracking/scalable_data_processing/` | Memory scaling via data size (10K-1M items) |
| **Scalable Recursive Decomposition** | `memory_tracking/scalable_recursive_decomposition/` | Memory scaling via recursion depth (2^k tasks) |

- **Scalable Data Processing** - 20 scenarios testing data types, transforms, and accumulation
  - Data types: `int` (~28 bytes), `string` (~500 bytes), `dict` (~1KB+)
  - Configurable: `num_transforms`, `accumulate`, `cleanup`
  - Memory range: 1 MB to 300+ MB

- **Scalable Recursive Decomposition** - 12 scenarios based on Alford et al. (2015) Theorem 4.1
  - Binary recursive decomposition: depth k yields 2^k leaf tasks
  - Demonstrates PSPACE-complete HTN planning complexity
  - Payload scaling: 100B to 100KB per task
  - Memory formula: `2^depth × payload_size`

**Benchmarking Script:**
```bash
cd src/gtpyhop/examples/memory_tracking

# Run data processing scenarios
python benchmarking.py --example data

# Run recursive decomposition scenarios
python benchmarking.py --example recursive

# Accurate peak measurement (recommended)
python benchmarking.py --example recursive --scenario scenario_10 \
    --disable-gc --sampling-interval 0.001
```

**Command-Line Options:**
- `--example {data,recursive}` - Select example type
- `--scenario NAME` - Run specific scenario
- `--disable-gc` - Disable garbage collection during planning
- `--sampling-interval FLOAT` - Memory sampling interval (default: 0.1)
- `--list-scenarios` - List available scenarios
- `--performance-test` - Compare overhead with/without memory tracking

**Usage Example:**
```python
from gtpyhop import PlannerSession
from gtpyhop.examples.memory_tracking.scalable_recursive_decomposition import (
    the_domain, get_problems
)

problems = get_problems()
state, tasks, description = problems['scenario_10']

with PlannerSession(
    domain=the_domain,
    memory_tracking=True,
    memory_sampling_interval=0.001
) as session:
    result = session.find_plan(state, tasks)

    if result.success:
        print(f"Plan: {len(result.plan)} actions")
        print(f"Peak memory: {result.stats['peak_memory_mb']:.2f} MB")
```

**Requirements:**
- Python 3.8+
- `psutil>=5.8.0` (automatically installed with GTPyhop from PyPI)

(https://github.com/PCfVW/GTPyhop/blob/pip/

**Documentation:**
- [Example Style Guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_example_style_guide.md) - How to write GTPyhop examples
- [Memory Tracking README](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/README.md)
- [Benchmarking Quick Start](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/benchmarking_quickstart.md)
- [Scalable Data Processing](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/scalable_data_processing/README.md)
- [Scalable Recursive Decomposition](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/memory_tracking/scalable_recursive_decomposition/README.md)

**References:**
- Ron Alford, Pascal Bercher, & David Aha (2015). ["Tight Bounds for HTN Planning."](https://ojs.aaai.org/index.php/ICAPS/article/view/13721) 25th ICAPS, pp. 7-15. [Video Recording](https://www.icaps-conference.org/recording/tight-bounds-for-htn-planning/)

---

## 1.7.0 — MCP Orchestration Enhancements & Consistency Updates
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.7.0/**

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

## 1.6.0 — Two new examples & Two new style guides
**Uploaded to PyPI: https://pypi.org/project/gtpyhop/1.6.0/**

🚀 **Major Features:**
- **📖 Documentation** - `domain.py` and `problems.py` style guides
- **🌐 MCP Orchestration Opentrons Flex Examples** - Omega HDQ 96-channel and PCR Workflow Automation with dynamic sample scaling (4 to 96 samples)

**Opentrons Flex Examples Documentation:**
- **[PCR Workflow Automation →](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/bio_opentrons/README.md)** - Multi-server robot coordination for Polymerase Chain Reaction (PCR) workflow automation (3 servers, 18 actions, 15 methods)
- **[Omega HDQ 96-channel →](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/omega_hdq_dna_bacteria_flex_96_channel/README.md)** - Multi-server robot coordination for DNA extraction (3 servers, 17 actions, 14 methods)

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
- **[Cross-Server Orchestration →](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/cross_server/README.md)** - Multi-server robot coordination (2 servers, 9 actions, 5 methods)
- **[TNF Cancer Modelling →](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/tnf_cancer_modelling/README.md)** - Multiscale biological modeling (12 actions, 3 methods)
- **[MCP Benchmarking →](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/mcp-orchestration/benchmarking_quickstart.md)** - Performance benchmarking for MCP domains

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
- **[Benchmarking documentation →](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/ipc-2020-total-order/benchmarking_quickstart.md)**
- **[Blocksworld-GTOHP documentation →](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/ipc-2020-total-order/Blocksworld-GTOHP/ipc-2020-to-bw-gtohp-readme.md)**
- **[Childsnack documentation →](https://github.com/PCfVW/GTPyhop/blob/pip/packages/gtpyhop-examples/src/gtpyhop/examples/ipc-2020-total-order/Childsnack/ipc-2020-to-cs-gtohp-readme.md)**

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
