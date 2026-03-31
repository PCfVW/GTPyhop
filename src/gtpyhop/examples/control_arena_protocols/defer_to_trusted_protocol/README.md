# Defer to Trusted Protocol

## Overview

This example models the **Defer to Trusted** micro-protocol from the Control Arena AI safety framework using GTPyhop HTN planning. An untrusted model proposes output, a monitor scores its suspiciousness, and a routing decision either accepts the output (low suspicion) or defers to a trusted model (high suspicion).

The routing decision demonstrates **HTN backtracking**: two methods compete for `m_route_output`. The first (`m_accept_if_low_suspicion`) decomposes to `a_accept_output`, which checks the suspicion threshold and fails if violated. The greedy planner cannot recover; backtracking planners try `m_defer_to_trusted_fallback`.

## Scenarios

| Scenario | Suspicion | Threshold | Outcome | Actions | Greedy |
|----------|-----------|-----------|---------|---------|--------|
| `scenario_1_low_suspicion` | 0.2 | 0.7 | Accept | 5 | SUCCESS |
| `scenario_2_high_suspicion` | 0.9 | 0.7 | Defer | 5 | **FAIL** |
| `scenario_3_at_threshold` | 0.7 | 0.7 | Accept | 5 | SUCCESS |
| `scenario_4_just_above` | 0.71 | 0.7 | Defer | 5 | **FAIL** |
| `scenario_5_tight_threshold` | 0.4 | 0.3 | Defer | 5 | **FAIL** |
| `scenario_6_loose_threshold` | 0.4 | 0.9 | Accept | 5 | SUCCESS |

## Plan Length

All plans are exactly **5 actions**:

```
a_initialize_episode -> a_run_untrusted_policy -> a_run_monitor ->
(a_accept_output | a_defer_to_trusted) -> a_score_trajectory
```

## HTN Decomposition

```
m_run_defer_to_trusted_protocol(task_id)
├── a_initialize_episode(task_id)
├── a_run_untrusted_policy(task_id)
├── a_run_monitor(task_id)
├── m_route_output(task_id)                    <-- BACKTRACKING POINT
│   ├── [try 1] m_accept_if_low_suspicion
│   │   └── a_accept_output(task_id)           <-- fails if suspicion > threshold
│   └── [try 2] m_defer_to_trusted_fallback
│       └── a_defer_to_trusted(task_id)        <-- always succeeds
└── a_score_trajectory(task_id)
```

## Domain Structure

### Actions (6)
- `a_initialize_episode` - Initialize micro-protocol episode
- `a_run_untrusted_policy` - Generate output from untrusted model
- `a_run_monitor` - Evaluate output suspiciousness
- `a_accept_output` - Accept output (fails if suspicion > threshold)
- `a_defer_to_trusted` - Defer to trusted model
- `a_score_trajectory` - Score the completed trajectory

### Methods (4)
- `m_run_defer_to_trusted_protocol` - Top-level orchestration
- `m_accept_if_low_suspicion` - Route: attempt to accept
- `m_defer_to_trusted_fallback` - Route: defer (backtracking fallback)

## Usage

```python
from gtpyhop.examples.control_arena_protocols.defer_to_trusted_protocol import the_domain, get_problems
import gtpyhop

problems = get_problems()
state, tasks, desc = problems['scenario_2_high_suspicion']

with gtpyhop.PlannerSession(domain=the_domain, verbose=1,
                            strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(state, tasks)
    print(f"Success: {result.success}, Plan: {result.plan}")
```

## File Structure

```
defer_to_trusted_protocol/
├── __init__.py
├── domain.py
├── problems.py
└── README.md
```

## Domain Statistics

- **Actions**: 6
- **Methods**: 4 (2 for m_route_output)
- **Scenarios**: 6 (3 accept, 3 defer)
- **MCP Servers**: None (purely symbolic)
- **Backtracking points**: 1 (m_route_output)

---
*Generated 2026-03-31*
