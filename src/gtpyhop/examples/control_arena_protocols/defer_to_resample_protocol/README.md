# Defer to Resample Protocol

## Overview

This example models the **Defer to Resample** micro-protocol from the Control Arena AI safety framework using GTPyhop HTN planning. When the untrusted model's output has high suspicion, instead of immediately deferring, the protocol generates additional samples and monitors each. It accepts the first low-suspicion sample, or defers to the trusted model after exhausting the sample budget.

This combines two GTPyhop mechanisms:
- **Backtracking** at the routing decision (accept vs. resample vs. defer)
- **Recursive method decomposition** for multi-round resampling

## Scenarios

| Scenario | Scores | Max | Threshold | Outcome | Actions | Greedy |
|----------|--------|-----|-----------|---------|---------|--------|
| `scenario_1_first_accepted` | [0.2] | 3 | 0.7 | Accept sample 0 | 5 | SUCCESS |
| `scenario_2_second_accepted` | [0.9, 0.3] | 3 | 0.7 | Accept sample 1 | 7 | **FAIL** |
| `scenario_3_third_accepted` | [0.9, 0.8, 0.4] | 3 | 0.7 | Accept sample 2 | 9 | **FAIL** |
| `scenario_4_all_high_defer` | [0.9, 0.8, 0.85] | 3 | 0.7 | Defer | 9 | **FAIL** |
| `scenario_5_single_sample` | [0.9] | 1 | 0.7 | Defer | 5 | **FAIL** |
| `scenario_6_five_samples` | [0.9, 0.8, 0.85, 0.75, 0.3] | 5 | 0.7 | Accept sample 4 | 13 | **FAIL** |

## Plan Length Formula

Plan length = `2*S + 3`, where S = number of samples tried before resolution.

- **Accept on 0-indexed sample N**: `2*(N+1) + 3` actions (S = N+1 samples tried)
- **Defer after max_samples**: `2*max_samples + 3` actions (S = max_samples)

Breakdown: `init + S*(run_untrusted + run_monitor) + (accept|defer) + score`

## HTN Decomposition

```
m_run_resample_protocol(task_id)
├── a_initialize_episode(task_id)
├── a_run_untrusted_policy(task_id, 0)            <-- first sample
├── a_run_monitor(task_id, 0)
├── m_route_or_resample(task_id, 1, max)           <-- BACKTRACKING POINT
│   ├── [try 1] m_accept_best_sample
│   │   └── a_accept_output(task_id)               <-- fails if suspicion > threshold
│   ├── [try 2] m_resample_loop                    <-- RECURSIVE
│   │   ├── a_run_untrusted_policy(task_id, 1)
│   │   ├── a_run_monitor(task_id, 1)
│   │   └── m_route_or_resample(task_id, 2, max)   <-- recurse
│   │       └── ...
│   └── [try 3] m_defer_after_resampling
│       └── a_defer_to_trusted(task_id)            <-- always succeeds
└── a_score_trajectory(task_id)
```

## Domain Structure

### Actions (6)
- `a_initialize_episode` - Initialize micro-protocol episode
- `a_run_untrusted_policy` - Generate sample output (parameterized by sample_num)
- `a_run_monitor` - Evaluate sample suspiciousness (reads per-sample score)
- `a_accept_output` - Accept output (fails if suspicion > threshold)
- `a_defer_to_trusted` - Defer to trusted model
- `a_score_trajectory` - Score the completed trajectory

### Methods (5)
- `m_run_resample_protocol` - Top-level orchestration
- `m_accept_best_sample` - Route: attempt to accept current sample
- `m_resample_loop` - Route: generate another sample (recursive)
- `m_defer_after_resampling` - Route: defer after exhaustion (fallback)

## Usage

```python
from gtpyhop.examples.control_arena_protocols.defer_to_resample_protocol import the_domain, get_problems
import gtpyhop

problems = get_problems()
state, tasks, desc = problems['scenario_3_third_accepted']

with gtpyhop.PlannerSession(domain=the_domain, verbose=1,
                            strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(state, tasks)
    print(f"Success: {result.success}, Plan length: {len(result.plan)}")
```

## File Structure

```
defer_to_resample_protocol/
├── __init__.py
├── domain.py
├── problems.py
└── README.md
```

## Domain Statistics

- **Actions**: 6
- **Methods**: 5 (3 for m_route_or_resample)
- **Scenarios**: 6
- **MCP Servers**: None (purely symbolic)
- **Backtracking points**: 1 (m_route_or_resample, with recursive resampling)

---
*Generated 2026-03-31*
