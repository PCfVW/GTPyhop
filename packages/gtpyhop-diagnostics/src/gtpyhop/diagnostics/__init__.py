"""
gtpyhop.diagnostics -- failure attribution for GTPyhop plans.

`PlanTrace` says *which* action a search died on. This says *why*:

    >>> from gtpyhop.diagnostics import explain_dead_end
    >>> report = explain_dead_end(result.trace, "domain.py")   # doctest: +SKIP
    >>> report.summary()                                       # doctest: +SKIP
    "pickup('a') was blocked by: s.clear[x] == True"

It works by joining two halves, neither of which is sufficient alone:
reading the domain source gives an action's *candidate* preconditions, and
`TraceEvent.state` -- recorded when planning with
`find_plan(..., trace_state=True)` -- gives the state those preconditions
were actually evaluated on. Intersecting them names the one that failed.

Deliberately kept out of gtpyhop-core: the planner should not carry a
source-analysis layer, and this is an optional add-on with its own release
cadence. It reads only the public `PlanTrace` API, never `Domain`'s private
action dictionary.

Analysis uses the standard library's `ast`, and stays within the 3.8 syntax
floor that gtpyhop-core declares.
"""

from .guards import (
    ActionGuards,
    GuardAtom,
    extract_action_guards,
    parse_source,
)
from .explain import (
    AtomResult,
    DeadEndReport,
    explain_dead_end,
    load_guards,
)

__version__ = "0.1.0"

__all__ = [
    "explain_dead_end",
    "DeadEndReport",
    "AtomResult",
    "load_guards",
    "GuardAtom",
    "ActionGuards",
    "extract_action_guards",
    "parse_source",
    "__version__",
]
