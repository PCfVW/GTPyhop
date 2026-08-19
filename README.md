# GTPyhop

[![Python Version](https://img.shields.io/badge/python-3%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Clear%20BSD-green.svg)](https://github.com/PCfVW/GTPyhop/blob/pip/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/gtpyhop)](https://pypi.org/project/gtpyhop/)
<!-- UPDATE MANUALLY when doctests are added or removed -->
[![Doctests](https://img.shields.io/badge/doctests-876%20passing-brightgreen)](docs/changelog.md)

GTPyhop is an HTN planning system based on [Pyhop](https://bitbucket.org/dananau/pyhop/src/master/), but generalized to plan for both goals and tasks. You describe a world as **actions** that change state and **methods** that break tasks into smaller ones; GTPyhop searches for a sequence of actions that accomplishes what you asked for.

[Dana Nau](https://www.cs.umd.edu/~nau/) is the original author of GTPyhop.

[This pip branch](https://github.com/PCfVW/GTPyhop/tree/pip) is forked from [Dana Nau's main branch](https://github.com/dananau/GTPyhop) and refactored for PyPI distribution, thread-safe sessions, benchmarking-friendly example layout, and documentation.

---

## Install

```bash
pip install gtpyhop
```

That gives you the planner and every bundled example. Since 2.0.0, GTPyhop is published
as four distributions that all install into the same `gtpyhop` import namespace:

| Install | You get | Use when |
|---|---|---|
| `gtpyhop` | planner **and** all bundled examples | learning, teaching, exploring |
| `gtpyhop-core` | the planner alone | production, CI, embedded |
| `gtpyhop-examples` | the examples (pulls in core) | you installed core first |
| `gtpyhop-diagnostics` | optional failure attribution | you want to know *why* a plan failed |

From a checkout — note there is no root `pyproject.toml` since 2.0.0, so install the
source packages rather than the repository root:

```bash
git clone -b pip https://github.com/PCfVW/GTPyhop.git
cd GTPyhop
pip install packages/gtpyhop-core packages/gtpyhop-examples
```

Add `-e` to both if you intend to modify GTPyhop or contribute an example; the two
source trees only merge into one importable package once installed.

## Check it works

```bash
python -m gtpyhop.examples.simple_htn --session
python -m gtpyhop.examples.regression_tests
```

## Your first plan

A truck fetches a parcel and delivers it. This runs as written:

```python
import gtpyhop

domain = gtpyhop.Domain('delivery')

# An action checks its preconditions, applies its effects, and returns the
# state. Falling off the end means "not applicable here".
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

# A method decomposes a task into subtasks and actions.
def m_deliver(state, parcel, truck, dest):
    return [('drive', truck, state.at[parcel]),
            ('load', parcel, truck),
            ('drive', truck, dest),
            ('unload', parcel, truck)]

gtpyhop.declare_task_methods('deliver', m_deliver)

state = gtpyhop.State('s0')
state.at = {'truck1': 'depot', 'parcel1': 'warehouse'}
state.fuel = {'truck1': 2}

with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(state, [('deliver', 'parcel1', 'truck1', 'shop')])

for step in result.plan:
    print(step)
```

```
('drive', 'truck1', 'warehouse')
('load', 'parcel1', 'truck1')
('drive', 'truck1', 'shop')
('unload', 'parcel1', 'truck1')
```

`PlannerSession` is the recommended entry point: it isolates the domain, verbosity and
strategy so concurrent planning is safe. The older global API (`gtpyhop.find_plan`, …)
still works unchanged.

## When a plan fails

`find_plan` returning nothing tells you only that no plan exists. GTPyhop can say
considerably more. Save the domain above as `delivery.py`, start the truck with an
empty tank, and ask why:

```python
from gtpyhop.diagnostics import explain_dead_end   # pip install gtpyhop-diagnostics

state.fuel = {'truck1': 0}                         # nothing else changes

with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(state, [('deliver', 'parcel1', 'truck1', 'shop')],
                               trace=True, trace_state=True)

print(explain_dead_end(result.trace, "delivery.py").summary())
```

```
drive('truck1', 'warehouse') was blocked by: state.fuel[truck] > 0
```

Not just *which* action failed — *which precondition* of it, and it correctly ignores
the guard that did hold. Walked through step by step in the
**[diagnostics tutorial](docs/diagnostics_tutorial.md)**.

## Where to go next

**Start here**

- **[FAQ](docs/faq.md)** — which package to install, which strategy to pick, what an action must return
- **[Goals tutorial](docs/goals_tutorial.md)** — asking for a *state* instead of a task, four ways
- **[Diagnostics tutorial](docs/diagnostics_tutorial.md)** — from "it failed" to "this precondition blocked it"
- **[All Examples](docs/all_examples.md)** — the full catalogue, with pedagogical notes
- **[Running Examples](docs/running_examples.md)** — how to invoke and benchmark them

**Going further**

- **[Thread-Safe Sessions](docs/thread_safe_sessions.md)** — sessions, planning strategies, memory tracking, `PlanTrace`
- **[Structured Logging](docs/logging.md)** — the logging system
- **[Version History](docs/changelog.md)** — full changelog
- **[Roadmap](docs/ROADMAP.md)** — what is coming, what is deferred, and what is not planned

**Writing your own**

- **[Example Style Guide](docs/gtpyhop_example_style_guide.md)** — folder layout and required files
- **[Domain Style Guide](docs/gtpyhop_domain_style_guide.md)** — conventions for actions and methods
- **[Problems Style Guide](docs/gtpyhop_problems_style_guide.md)** — scenarios and doctests
- **[Example auditor](packages/gtpyhop-examples/src/gtpyhop/examples/audit/README.md)** — `python -m gtpyhop.examples.audit --all` checks a domain against those guides, and against itself

## Project structure

```
GTPyhop/
├── docs/                        guides, style guides, changelog
├── tools/                       repository utilities (link, domain, doctest and persistence checks)
└── packages/                    one folder per published distribution
    ├── gtpyhop-core/            the planner
    ├── gtpyhop-examples/        the bundled example domains
    ├── gtpyhop-diagnostics/     optional failure attribution
    └── gtpyhop/                 meta-package: core + examples, no source
```

Each package keeps its own `src/gtpyhop/` tree; they merge into a single importable
`gtpyhop` package once installed, so `import gtpyhop`, `import gtpyhop.examples` and
`import gtpyhop.diagnostics` all work side by side.

## Credits and licence

GTPyhop was created by [Dana Nau](https://www.cs.umd.edu/~nau/). This branch is
maintained by Eric Jacopin. Released under the Clear BSD License — see
[LICENSE.txt](LICENSE.txt).
