# `gtpyhop.examples.audit` — does this example still say what it does?

A domain drifts from its own documentation silently, because **nothing
executes a docstring**. Tests check that a plan comes out; they never check
that the section header still says 32 actions when the file now has 38, or
that an action's `Effects:` list still names everything the action assigns.

This tool checks the things nothing else checks.

```bash
python -m gtpyhop.examples.audit mcp-orchestration/rikyu_hpc
python -m gtpyhop.examples.audit --all --summary
python -m gtpyhop.examples.audit PATH --plan
python tools/domain_audit.py --all        # from a repository checkout
```

Exit status is 1 if any **enforced** finding is reported, so it drops straight
into a pre-commit hook or CI. It is the domain-level counterpart of
`tools/link_audit.py`, which does the same job for Markdown links.

---

## Enforced and advisory

| Family | Enforced? | What it means |
|---|:--:|---|
| `STRUCTURE` | yes | the style guide, mechanised |
| `SEMANTICS` | yes | the code and its documentation disagree |
| `BEHAVIOUR` | yes | `--plan` only: a problem does not plan, a trap does, or a length claim is false |
| `HYGIENE` | no | written-but-never-read state |
| `INFO` | no | the domain does not use the `a_`/`m_` convention at all |

`HYGIENE` is advisory on purpose. In a planning domain most write-once state is
a **terminal effect** — `state.grasp_force`, `state.thermocycler_block_temp` —
which an action exists in order to change and nothing later reads. Across the
bundled examples 50 of 52 were exactly that. The check still earns its keep: it
is what caught a retired design flag still being written in `rikyu_hpc`. But it
cannot fail a build without crying wolf. `--strict` enforces it.

## Two ways to adopt it on an existing tree

Neither is needed here — the bundled examples are at zero enforced findings —
but a project with a backlog has both:

```bash
# a ratchet: tolerate today's count, fail on anything worse
python -m gtpyhop.examples.audit --all --fail-on 40

# a baseline: accept today's findings by identity, fail on anything NEW
python -m gtpyhop.examples.audit --all --write-baseline
python -m gtpyhop.examples.audit --all --baseline
```

A baseline records each finding under a hash of (example, family, location,
message), so it survives line-number churn but not a change to the finding
itself. Debt is capped, and new debt still fails.

---

## The three enforced families

### STRUCTURE — the style guide, mechanised

Parses `domain.py` only. Everything in
[gtpyhop_domain_style_guide.md](../../../../../../docs/gtpyhop_domain_style_guide.md)
that a machine can decide: the eight required docstring sections for actions
and seven for methods, the `# BEGIN:`/`# END:` markers, type annotations on
every parameter, `Union[State, bool]` versus `Union[List[Tuple], bool]`,
`state: State` as the first parameter, at least one `[DATA]`/`[ENABLER]`/
`[EXPECTED_EFFECT]` tag in every `Effects` block, `a_`/`m_` prefixes on every
task named in a decomposition, and the counts quoted in section headers.

That last one is duller than it sounds and catches more than anything else:

```
[STRUCTURE] header: '# ACTIONS (10)' but the file has 11 actions
```

### SEMANTICS — where the surprises are

Reads `domain.py` and `problems.py` together and compares what the code
*does* against what the prose *says*.

| Check | What it really finds |
|---|---|
| written but never read | a retired design still being maintained |
| read but never written | a typo, or state a scenario forgot to set |
| `Effects:` omits an attribute the action assigns | a docstring that stopped tracking the code |
| `[ENABLER]` nothing tests | a "workflow gate" that gates nothing |

The `[ENABLER]` check deserves its reputation. The style guide defines an
ENABLER as a property "checked in preconditions of subsequent actions". If no
precondition anywhere tests it, the tag is not merely redundant — it is
**misleading**, and worse than an undocumented gate, because a reader will
believe the sequencing is enforced when it is not.

### BEHAVIOUR — opt-in, needs `--plan`

Imports the example and plans. Every problem in `get_problems()` must plan;
every problem in `get_trap_problems()`, if that function exists, must **not**;
and a description promising `-> N actions` must be telling the truth.

```
[BEHAVIOUR] scenario_1_fire_and_forget: description claims 99 actions, the plan has 4
```

Off by default because it costs an import and a search per problem.

---

## Why it exists

`mcp-orchestration/rikyu_hpc` was written across several sessions, and each
session left the previous session's numbers behind. The first run of this tool
on that one example reported **38 defects**:

- section headers still said `Actions (32)` at 38 actions, and `Methods (19)` at 42
- **17 docstrings** had stopped listing state their action assigns
- a retired design flag was still written by `a_get_facility` with nothing left to read it
- five `[ENABLER]` tags gated nothing
- one scenario advertised a 17-action plan that had become 18

None of it broke a test. All of it was wrong, and a reader would have believed
every word.

Its first run across all 33 bundled examples reported **343 findings**, among
them stale headers in `trunk_thumper/s07_expected_effects_chase` (said 10
actions, had 11) and `s08_priority_methods` (said 13, had 9) — `s07` being the
very example the domain style guide cites as the reference implementation of
`[EXPECTED_EFFECT]`. All 343 were resolved in 2.0.1: 291 repaired in the files,
52 reclassified as advisory once the evidence showed they were terminal
effects. The tree now stands at **zero enforced findings**.

Three of those 343 turned out to be the checks being wrong rather than the
domains, which is worth recording:

- an action with a deliberately **empty** `Effects` block has nothing to tag
  (`a_pass_ice` advances a pointer that is already advanced, and says so);
- state read only behind a `hasattr(state, 'x')` guard with a default is
  **optional by design**, not undefined — flagging it would punish exactly the
  defensive style the style guide encourages;
- `declare_actions(...)` cannot be found by regex when a comment inside the
  argument list contains a `)`.

An auditor that is wrong is worse than no auditor, because people stop reading
it. Each of these was found by checking a sample of findings by hand against
the source before believing the total.

---

## Exemptions: `_audit.json`

Some state is legitimately written and never read — a value a tool genuinely
returns, or bookkeeping kept for state dumps. Declare it beside `domain.py`,
**with a reason each**:

```json
{
  "intentionally_unread": {
    "doc_sections": "list_doc_sections' actual return value; recorded because the tool returns it, not because anything gates on it",
    "server_1_ready": "server 1 is the HTN planner running this domain, so no action can meaningfully gate on it"
  }
}
```

The reason is the point. An exemption without one is just a silenced check.

The audit also reports an exemption that has **gone stale** — state now read
after all, or no longer written — so the file cannot quietly outlive what it
excuses. `mcp-orchestration/rikyu_hpc/_audit.json` is a worked example.

---

## How it works, and two bugs worth knowing about

Everything is `ast`, not regex, wherever a regex would be fragile. Two
concrete reasons:

**A comment can close an argument list.** The obvious way to find declared
actions is `declare_actions\((.*?)\)`. Run that on `bio_opentrons`:

```python
declare_actions(
    # Movement server (Server 1)     <-- the ')' here ends the non-greedy match
    a_load_labware,
    ...
```

Every action after that comment looked undeclared: **44 false positives across
the tree**, all from one paren in a comment. The tool now walks `ast` for
`Call` nodes named `declare_actions` and reads their `Name` arguments.

**`ast` stops a function before its last comment.** `node.end_lineno` is the
last *statement*, so this trailing marker falls outside the node:

```python
    return [("a_task", x)]
    # END: Task Decomposition        <-- outside node.end_lineno
```

Checking markers against `lines[node.lineno-1:node.end_lineno]` reports every
method in the file as missing its `END` marker. `_span_ends()` instead runs
each top-level node to the line before the next one.

**Writes are classified precisely.** `state.jobs[job_id] = {...}` loads
`state.jobs` and stores into the subscript, so a naive "is this `Store`
context" test calls it a read. `_written_attrs()` counts an attribute as
written when it is the base of an assignment target, an augmented assignment,
a `for` target, or the receiver of `.append`/`.update`/`.pop`/… — and
everything else as a read. Getting this wrong in either direction destroys the
dead-state check, which is the most valuable one here.

---

## Testing the auditor itself

```bash
python -m gtpyhop.examples.audit.selftest
```

16 fixtures, each a minimal domain with exactly one planted defect. Every one
asserts **both** halves: the expected finding is reported, **and nothing else
is**. That second half is the important one — a checker that reports too much
gets ignored, which costs more than having no checker.

Five are regression fixtures for bugs this tool actually had, listed under "Why
it exists" above. To convince yourself they bite, re-introduce one: put the old
`declare_actions\((.*?)\)` regex back and the suite drops from 16/16 to 0/16,
with the `")" inside a declare_actions comment` case naming the cause.

## Adding a check

Each family is one function taking the parsed tree and appending `Finding`
objects. A new check is a few lines inside the right one; the CLI, the
`--family` filter and the exit status need no changes.

Add a fixture in `selftest.py` at the same time — one planted defect, asserting
the finding fires and nothing else does. If your new check has a false-positive
mode, some other fixture will fail and tell you which.

Prefer checks that are **decidable**. "This precondition looks wrong" is a
code review; "this docstring names a state variable the function never
touches" is an audit. Only the second kind belongs here.

---

## What it does not do

It does not judge whether a domain is *correct* — only whether it is
*consistent with itself*. A perfectly consistent domain can still model the
wrong world. It also cannot check prose: a provenance table claiming a
constant came from a particular source file is beyond it, and stays a human
job.

Domains translated from PDDL (`ipc-2020-total-order/*`) keep their source
names (`pick_up`, `unstack`) rather than the `a_`/`m_` convention. The tool
detects that, says so once, and skips the prefix-dependent checks instead of
emitting a cascade.
