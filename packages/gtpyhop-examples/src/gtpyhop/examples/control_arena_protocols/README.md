# Control Arena Protocol Examples for GTPyhop

## Overview

This directory contains examples that formalize **AI safety micro-protocols** from the [Control Arena](https://github.com/UKGovernmentBEIS/control-arena) framework using GTPyhop HTN planning. Each example models a different micro-protocol as a GTPyhop domain where the routing decision (accept vs. defer) is driven by HTN backtracking.

All examples use `MCP_Tool: None` (purely symbolic, no external MCP servers).

## What is Control Arena?

Control Arena is a Python library developed by the UK AI Security Institute (AISI) and Redwood Research for running **AI Control** experiments (Greenblatt et al. 2024). It tests whether control protocols can prevent unsafe actions by AI systems, even if those systems are misaligned and actively trying to subvert safeguards.

A control protocol orchestrates three resources: an **untrusted model** (powerful but untrustworthy), a **trusted model** (weaker but safe), and **human auditors** (expert but scarce). Each protocol is evaluated in two modes: **honest** (measures usefulness) and **attack** (measures safety). Every protocol occupies a point on a **safety-usefulness Pareto frontier**.

### Micro-protocols

These examples model **micro-protocols** — stateless, single-task pipelines that follow a three-step pattern:

1. **Propose**: Invoke the untrusted policy to generate an output.
2. **Monitor**: Score the output's suspiciousness (normalized to [0.0, 1.0]).
3. **Route**: Accept, defer, resample, or edit based on the suspicion score.

Control Arena ships with four built-in micro-protocols:

| Micro-protocol | Routing logic | GTPyhop example |
|---|---|---|
| **Trusted Monitoring** | Non-intervening baseline. Attaches scores but does not act. | — |
| **Defer to Trusted** | If suspicion > threshold, defer to trusted model. | `defer_to_trusted_protocol/` |
| **Trusted Editing** | If suspicion > threshold, trusted model edits the output. | — |
| **Defer to Resample** | If suspicion > threshold, generate more samples; defer if all high. | `defer_to_resample_protocol/` |

The adversarial example (`adversarial_protocol/`) extends Defer to Trusted with attack strategies and vulnerability detection.

### Why GTPyhop?

Control Arena's protocol logic — what gates what, what must happen before what — is implicit in Python classes. GTPyhop makes protocol structure **explicit and extractable**: `[ENABLER]` properties declare hard workflow gates (e.g., "monitor must complete before output is accepted"), `[DATA]` properties declare information flow, and HTN backtracking naturally models the routing decision between accept and defer. This **complements** (not replaces) Control Arena's empirical evaluation with structural analysis.

### Concept Mapping

| Control Arena | GTPyhop | Role |
|---|---|---|
| Micro-protocol pipeline | Top-level method | `m_run_*_protocol` decomposes into propose -> monitor -> route -> score |
| Routing decision | Alternative methods | `m_route_output` with accept and defer alternatives; backtracking selects |
| Policy invocation | Primitive action | `a_run_untrusted_policy` (symbolic state update) |
| Monitor invocation | Primitive action | `a_run_monitor` (reads config, sets suspicion score) |
| Workflow gate | `[ENABLER]` property | `monitor_evaluation_complete` gates `a_accept_output` |
| Suspicion score | `[DATA]` property | `suspicion_score` read by routing methods |
| Side-task firing on accept | `[EXPECTED_EFFECT]` property | `state.side_task_observed` set by `a_accept_output` when `side_task_embedded` (deployment executor's downstream effect, modeled at planning time) — first use of the `[EXPECTED_EFFECT]` tag in this collection (introduced in `adversarial_protocol/` in **1.9.7**) |
| Threat model | `[CONFIG]` property | `state.config_threat_model` ('none' / 'generic' / 'code_sabotage' / 'data_poisoning' / 'research_sabotage'); used by `a_run_monitor` to look up the nested detection-rate dict (added in **1.9.7**) |
| EvalMode (HONEST/ATTACK) | Scenario config | Different `problems.py` scenarios model each mode |

## Available Examples

| Example | Directory | Actions | Methods | Scenarios | Key Feature |
|---------|-----------|---------|---------|-----------|-------------|
| **Defer to Trusted** | `defer_to_trusted_protocol/` | 6 | 4 | 6 | Backtracking on routing |
| **Defer to Resample** | `defer_to_resample_protocol/` | 6 | 5 | 6 | Recursive resampling + backtracking |
| **Adversarial** | `adversarial_protocol/` | 8 | 7 | 15 | Adversarial analysis + vulnerability detection + threat-model variety + `[EXPECTED_EFFECT]` |

**Total**: 20 actions, 16 methods, 27 scenarios, ~200 doctests.

## Planning Strategy Requirements

All three examples require the **iterative DFS backtracking** strategy for scenarios where the accept action fails (suspicion > threshold). The greedy planner commits to the first method and cannot recover.

| Strategy | Accept scenarios | Defer scenarios |
|----------|-----------------|-----------------|
| Greedy (`iterative_greedy`) | SUCCESS | **FAIL** |
| Backtracking (`iterative_dfs_backtracking`) | SUCCESS | SUCCESS |

## Benchmark Outcome Labels

`benchmarking.py` classifies each completed plan via the actions it contains:

| Label | Plan contains | Meaning |
|---|---|---|
| `accept` | `a_accept_output` | Output accepted; `[EXPECTED_EFFECT]` block fires if `side_task_embedded` |
| `defer` | `a_defer_to_trusted` | Output deferred to trusted model |
| `accept_no_ee` | `a_accept_output_demo_no_expected_effect` | Adversarial protocol scenario 15 only: negative-control teaching variant. Plan is an accept-trajectory but the `[EXPECTED_EFFECT]` block is omitted, so `state.side_task_observed` is never set |
| `unknown` | none of the above | Should never appear under normal use; indicates a custom task list that bypasses both canonical and demo routing actions |

## Quick Start

```bash
cd src/gtpyhop/examples/control_arena_protocols

# Run defer_to_trusted protocol (default)
python benchmarking.py

# Run resample protocol
python benchmarking.py --example resample

# Run adversarial protocol
python benchmarking.py --example adversarial

# Run specific scenario
python benchmarking.py --example adversarial --scenario scenario_3_subtle_evades

# List available scenarios
python benchmarking.py --list-scenarios --example adversarial

# Run doctests
python -m doctest -v ../../../gtpyhop/examples/control_arena_protocols/defer_to_trusted_protocol/problems.py
```

## Directory Structure

```
control_arena_protocols/
+-- __init__.py
+-- benchmarking.py                        # Unified benchmarking script
+-- README.md                              # This file
+-- defer_to_trusted_protocol/
|   +-- __init__.py
|   +-- domain.py                          # 6 actions, 4 methods
|   +-- problems.py                        # 6 scenarios
|   +-- README.md
+-- defer_to_resample_protocol/
|   +-- __init__.py
|   +-- domain.py                          # 6 actions, 5 methods
|   +-- problems.py                        # 6 scenarios
|   +-- README.md
+-- adversarial_protocol/
    +-- __init__.py
    +-- domain.py                          # 7 actions, 6 methods
    +-- problems.py                        # 8 scenarios
    +-- README.md
```

## Three Levels of Integration

These examples implement **Level 1** (protocol specification) from the broader integration plan. The three levels are:

| Level | What | GTPyhop role | These examples |
|---|---|---|---|
| **1. Specification** | Write protocols as GTPyhop domains; extract structure via LibCST; run static safety checks | Specification language | **Yes** |
| **2. Planning + Execution** | Use `find_plan` to generate action sequences; dispatch to real MCP servers at execution time | Runtime planner | Future work |
| **3. Adversarial Planning** | Add attacker methods; analyze whether protocol gates prevent all modeled attack strategies | Structural red-teaming | Demonstrated in `adversarial_protocol/` |

**Macro-protocols** (deployment-level, stateful across many episodes, Bayesian belief updating) are out of scope. GTPyhop plans within a single micro-protocol episode; macro-protocol analysis consumes episode results as data points.

## References

- **Control Arena**: https://github.com/UKGovernmentBEIS/control-arena
- **AI Control** (Greenblatt et al. 2024): "AI Control: Improving Safety Despite Intentional Subversion" — https://arxiv.org/abs/2312.06942
- **GTPyhop**: https://github.com/PCfVW/GTPyhop/tree/pip
- **GTPyhop Domain Style Guide**: `docs/gtpyhop_domain_style_guide.md`
- **Nau et al. 2021**: "GTPyhop: A Hierarchical Goal+Task Planner Implemented in Python" — https://www.cs.umd.edu/~nau/papers/nau2021gtpyhop.pdf

---
*Generated 2026-03-31*
