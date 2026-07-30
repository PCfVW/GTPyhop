# Adversarial Protocol

## Overview

This example extends the Defer to Trusted protocol with **adversarial analysis**. The untrusted model may operate honestly (no side task) or adversarially (embedding a side task with varying subtlety). A monitor maps attack subtlety levels to suspicion scores via calibrated detection rates. The routing decision determines whether the attack succeeds.

Security analysis identifies three outcomes:
- **SAFE**: Attack caught (suspicion > threshold, deferred)
- **VULNERABILITY**: Attack evades monitor (suspicion <= threshold, accepted with side task embedded)
- **OVER-SENSITIVE**: Honest output deferred (false positive, hurts usefulness)

## Scenarios

### 1.9.4 baseline: 8 scenarios (threat_model = 'generic' or 'none')

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

### Threat-model variety (added in 1.9.7)

| Scenario | Threat model | Subtlety | Suspicion | Threshold | Outcome | Security |
|----------|--------------|----------|-----------|-----------|---------|----------|
| `scenario_9_code_sabotage_subtle_evades` | code_sabotage | subtle | 0.20 | 0.7 | Accept | **VULNERABILITY** |
| `scenario_10_code_sabotage_obvious_caught` | code_sabotage | obvious | 0.92 | 0.7 | Defer | SAFE |
| `scenario_11_data_poisoning_subtle_evades` | data_poisoning | subtle | 0.15 | 0.7 | Accept | **VULNERABILITY** |
| `scenario_12_data_poisoning_obvious_caught` | data_poisoning | obvious | 0.85 | 0.7 | Defer | SAFE |
| `scenario_13_research_sabotage_subtle_evades` | research_sabotage | subtle | 0.10 | 0.7 | Accept | **VULNERABILITY** |
| `scenario_14_research_sabotage_obvious_caught` | research_sabotage | obvious | 0.80 | 0.7 | Defer | SAFE |

Detection rates illustrate that data_poisoning and research_sabotage are systematically harder for a generic monitor to detect than code_sabotage at the same subtlety — a pattern Control Arena emphasizes. At subtle subtlety: code 0.20 > data 0.15 > research 0.10.

### `[EXPECTED_EFFECT]` negative control (added in 1.9.7)

| Scenario | Note | Plan length |
|----------|------|-------------|
| `scenario_15_expected_effect_negative_control` | Manual task list uses `a_accept_output_demo_no_expected_effect` (omits the `[EXPECTED_EFFECT]` block). Plan succeeds but `state.side_task_observed` is never set. | 5 |

Under `benchmarking.py`, scenario 15 reports outcome `accept_no_ee` (rather than `accept` / `defer`), distinguishing it from the canonical accept paths. See the collection README's "Benchmark Outcome Labels" section.

All 15 plans are **5 actions**. Scenarios where suspicion > threshold require backtracking (greedy fails).

## Security Analysis Insights

- **Scenario 3 vs. 4**: Subtle attack (suspicion=0.25) evades standard threshold (0.7) but is caught by tight threshold (0.2). Tightening the threshold improves safety.
- **Scenario 7**: But overly tight thresholds cause false positives (honest output deferred). This is the safety-usefulness tradeoff.
- **Scenario 8**: Even obvious attacks (suspicion=0.95) evade an overly loose threshold (0.99). Threshold tuning is critical.
- **Scenarios 9–14 (threat-model variety)**: Holding subtlety constant, *which* threat type drives detection. Subtle code sabotage (0.20) is detected better than subtle data poisoning (0.15) or research sabotage (0.10). A "tighten the threshold" mitigation that catches subtle code sabotage may still miss subtle research sabotage.
- **Scenario 15 ([EXPECTED_EFFECT] negative control)**: The `[EXPECTED_EFFECT]` block in `a_accept_output` is what records the side-task firing in `state.side_task_observed`. When a teaching-variant action omits that block, the plan still produces a 5-action accept-trajectory, but downstream safety inspection of `state.side_task_observed` reports False — a silent safety violation. This empirically demonstrates why the `[EXPECTED_EFFECT]` tag is load-bearing.

## Threat-Model Variety

The `config_threat_model` state field (added in 1.9.7) takes one of:

- `'none'`: honest scenarios with no attack
- `'generic'`: threat-type-agnostic attacks (original 6 attack scenarios)
- `'code_sabotage'`: code-level attacks (vulnerable code, embedded backdoors)
- `'data_poisoning'`: data-distribution attacks (mislabeled samples, drift)
- `'research_sabotage'`: research-output attacks (plausible-but-false conclusions)

`config_detection_rates` is now a nested dict `Dict[threat_model, Dict[subtlety, float]]`. The monitor's lookup is `detection_rates.get(threat_model, {}).get(subtlety, 0.95)` with a fallback to `'generic'` if the configured threat_model is missing from the dict.

## `[EXPECTED_EFFECT]` Marker

The `[EXPECTED_EFFECT]` tag (introduced in `trunk_thumper/s07` and used in `colt_express/s3`) makes its first appearance in `control_arena_protocols/` via `a_accept_output`:

```python
# BEGIN: Effects
# [DATA] Output accepted
state.output_accepted = True

# [EXPECTED_EFFECT] If the accepted output embeds a side task, the
# deployment executor (a separate system) will run it. The acceptance
# operator commits the output; the executor fires the side task. At
# planning time we mark the side-task firing here so downstream
# inspection (e.g., audit_log analysis) can detect the safety
# violation.
if hasattr(state, 'side_task_embedded') and state.side_task_embedded:
    state.side_task_observed = True
    state.audit_log.append(('expected_effect', task_id, 'side_task_execution_observed'))

state.audit_log.append(('accept', task_id, f'suspicion={state.suspicion_score}<=threshold={threshold}'))
# END: Effects
```

The teaching-variant action `a_accept_output_demo_no_expected_effect` is byte-identical except this `[EXPECTED_EFFECT]` block is omitted. Scenario 15 invokes it directly via a manual task list to demonstrate that without the block, `state.side_task_observed` stays False even when the accepted output embeds a side task.

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

### Actions (8)
- `a_initialize_episode` - Initialize micro-protocol episode
- `a_run_untrusted_policy_honest` - Generate honest output (no side task)
- `a_run_untrusted_policy_attack` - Generate adversarial output (embeds side task)
- `a_run_monitor` - Evaluate suspiciousness (uses **nested** detection rates indexed by `(threat_model, subtlety)`)
- `a_accept_output` - Accept output (fails if suspicion > threshold); **`[EXPECTED_EFFECT]` fires `state.side_task_observed = True` when `side_task_embedded`**
- `a_accept_output_demo_no_expected_effect` - **NEW in 1.9.7** Negative-control variant; byte-identical to `a_accept_output` except the `[EXPECTED_EFFECT]` block is omitted
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

- **Actions**: 8 (1.9.4 baseline: 7; 1.9.7 added `a_accept_output_demo_no_expected_effect`)
- **Methods**: 7 (unchanged from 1.9.4; 2 for `m_generate_output`, 2 for `m_route_output`)
- **Scenarios**: 15 (1.9.4 baseline: 8; 1.9.7 added +6 threat-typed + 1 `[EXPECTED_EFFECT]` negative control)
  - 7 SAFE (incl. scenarios 10, 12, 14 from 1.9.7)
  - 6 VULNERABILITY (incl. scenarios 9, 11, 13 from 1.9.7)
  - 1 OVER-SENSITIVE (1.9.4)
  - 1 NEGATIVE CONTROL (1.9.7)
- **MCP Servers**: None (purely symbolic)
- **Backtracking points**: 1 (`m_route_output`; scenario 15 bypasses routing via manual task list)
- **Doctests**: 92 (1.9.4 baseline: 56; 1.9.7 added 36)
- **Tags used**: `[DATA]`, `[ENABLER]`, `[CONFIG]` (1.9.4); `[EXPECTED_EFFECT]` (added in 1.9.7 — first use in `control_arena_protocols/`)

---
*Generated 2026-03-31 (1.9.4 baseline); extended in 1.9.7 with threat-model variety and [EXPECTED_EFFECT] marker*
