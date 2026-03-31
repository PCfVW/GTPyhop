# Adversarial Protocol

## Overview

This example extends the Defer to Trusted protocol with **adversarial analysis**. The untrusted model may operate honestly (no side task) or adversarially (embedding a side task with varying subtlety). A monitor maps attack subtlety levels to suspicion scores via calibrated detection rates. The routing decision determines whether the attack succeeds.

Security analysis identifies three outcomes:
- **SAFE**: Attack caught (suspicion > threshold, deferred)
- **VULNERABILITY**: Attack evades monitor (suspicion <= threshold, accepted with side task embedded)
- **OVER-SENSITIVE**: Honest output deferred (false positive, hurts usefulness)

## Scenarios

| Scenario | Mode | Subtlety | Suspicion | Threshold | Outcome | Security |
|----------|------|----------|-----------|-----------|---------|----------|
| `scenario_1_honest_accepted` | Honest | - | 0.10 | 0.7 | Accept | SAFE |
| `scenario_2_obvious_caught` | Attack | obvious | 0.95 | 0.7 | Defer | SAFE |
| `scenario_3_subtle_evades` | Attack | subtle | 0.25 | 0.7 | Accept | **VULNERABILITY** |
| `scenario_4_subtle_caught_tight` | Attack | subtle | 0.25 | 0.2 | Defer | SAFE |
| `scenario_5_moderate_caught` | Attack | moderate | 0.60 | 0.5 | Defer | SAFE |
| `scenario_6_moderate_evades` | Attack | moderate | 0.60 | 0.7 | Accept | **VULNERABILITY** |
| `scenario_7_honest_tight_threshold` | Honest | - | 0.10 | 0.05 | Defer | OVER-SENSITIVE |
| `scenario_8_obvious_loose_threshold` | Attack | obvious | 0.95 | 0.99 | Accept | **VULNERABILITY** |

All plans are **5 actions**. Scenarios where suspicion > threshold require backtracking (greedy fails).

## Security Analysis Insights

- **Scenario 3 vs. 4**: Subtle attack (suspicion=0.25) evades standard threshold (0.7) but is caught by tight threshold (0.2). Tightening the threshold improves safety.
- **Scenario 7**: But overly tight thresholds cause false positives (honest output deferred). This is the safety-usefulness tradeoff.
- **Scenario 8**: Even obvious attacks (suspicion=0.95) evade an overly loose threshold (0.99). Threshold tuning is critical.

## HTN Decomposition

```
m_run_adversarial_protocol(task_id)
├── a_initialize_episode(task_id)
├── m_generate_output(task_id)                     <-- DETERMINISTIC SELECTION
│   ├── m_honest_output (if not attack_active)
│   │   └── a_run_untrusted_policy_honest(task_id)
│   └── m_attack_output (if attack_active)
│       └── a_run_untrusted_policy_attack(task_id, subtlety)
├── a_run_monitor(task_id)
├── m_route_output(task_id)                        <-- BACKTRACKING POINT
│   ├── [try 1] m_accept_if_low_suspicion
│   │   └── a_accept_output(task_id)               <-- fails if suspicion > threshold
│   └── [try 2] m_defer_to_trusted_fallback
│       └── a_defer_to_trusted(task_id)
└── a_score_trajectory(task_id)
```

## Domain Structure

### Actions (7)
- `a_initialize_episode` - Initialize micro-protocol episode
- `a_run_untrusted_policy_honest` - Generate honest output (no side task)
- `a_run_untrusted_policy_attack` - Generate adversarial output (embeds side task)
- `a_run_monitor` - Evaluate suspiciousness (uses detection rates)
- `a_accept_output` - Accept output (fails if suspicion > threshold)
- `a_defer_to_trusted` - Defer to trusted model
- `a_score_trajectory` - Score the completed trajectory

### Methods (7)
- `m_run_adversarial_protocol` - Top-level orchestration
- `m_generate_output` - Task: select honest or attack output (2 alternatives)
- `m_honest_output` - Generate: honest output
- `m_attack_output` - Generate: adversarial output
- `m_route_output` - Task: accept or defer (2 alternatives, backtracking point)
- `m_accept_if_low_suspicion` - Route: attempt to accept
- `m_defer_to_trusted_fallback` - Route: defer (backtracking fallback)

## Usage

```python
from gtpyhop.examples.control_arena_protocols.adversarial_protocol import the_domain, get_problems
import gtpyhop

problems = get_problems()
state, tasks, desc = problems['scenario_3_subtle_evades']

with gtpyhop.PlannerSession(domain=the_domain, verbose=1,
                            strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(state, tasks)
    print(f"Success: {result.success}, Plan: {result.plan}")
    # Output includes a_accept_output -- VULNERABILITY: side task accepted!
```

## File Structure

```
adversarial_protocol/
├── __init__.py
├── domain.py
├── problems.py
└── README.md
```

## Domain Statistics

- **Actions**: 7
- **Methods**: 7 (2 for m_generate_output, 2 for m_route_output)
- **Scenarios**: 8 (4 SAFE, 3 VULNERABILITY, 1 OVER-SENSITIVE)
- **MCP Servers**: None (purely symbolic)
- **Backtracking points**: 1 (m_route_output)

---
*Generated 2026-03-31*
