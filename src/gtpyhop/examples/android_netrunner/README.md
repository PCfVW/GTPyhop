# Android: Netrunner Run Planning

## Overview

Models a single Runner-side **run** against a configured Corporation server stack, using the published mechanics of Fantasy Flight Games' *Android: Netrunner* (2012 core set rulebook). The Runner is the HTN planning agent; the Corp is configured environmental state (ice stack, rez policy, ambush firing decisions, trace budget).

The flagship scenario faithfully replicates the worked run example on **page 19 of the core rulebook**: Bart's run against Olivia's remote server with Enigma, Wall of Thorns, Akitaro Watanabe, and a Nisei MK II agenda — Jinteki Personal Evolution identity included.

The domain demonstrates:
- **Per-card fidelity** for 14 named cards from the core set (4 ice, 4 icebreakers, 4 Corp non-ice, 2 Runner hardware/resources)
- **HTN decomposition** of runs into initiate → traverse ice stack → access → end
- **Backtracking** across icebreaker choice and break-completeness (full vs. partial subroutine breaks)
- **Encounter / run / persistent state scopes** distinguished (Crypsis pump = encounter, Gordian pump = run, virus counters = persistent)
- **Greedy planner failure** on scenarios that require backtracking through deep credit-management decisions

## Scenarios

| # | Scenario | Plan | Greedy | Notes |
|---|----------|------|--------|-------|
| 1 | `empty_server_walk_in` | 3 | OK | Baseline: no ice, walk in |
| 2 | `single_barrier_corroder` | 6 | OK | Corroder vs. Ice Wall |
| 3 | `rulebook_run_example` | 13 | **FAIL** | p.19 replication; Gordian + Crypsis + SC vs. Enigma + Wall of Thorns; Jinteki PE |
| 4 | `sentry_needs_ai_fallback` | 9 | OK | Corroder fails subtype match on Data Raven; Crypsis (AI) succeeds |
| 5 | `wyrm_drain_path` | 9 | OK | Wyrm-only vs. Wall of Thorns: pump + drain + breaks |
| 6 | `accept_net_damage_to_save_credits` | 11 | **FAIL** | Greedy full-breaks Wall of Thorns and runs out; backtrack takes net damage |
| 7 | `crypsis_no_sc_must_trash` | 8 | OK | Cleanup chain: counter fails → SC fails → trash Crypsis |
| 8 | `ambush_secretary_showcase` | 9 | OK | Aggressive Secretary ambush fires on access, trashes Corroder |

### What makes each scenario interesting

- **S1-S2**: Domain sanity tests. Demonstrate that the run pipeline produces sensible plans before introducing card complexity.
- **S3** (**flagship**): Bart's run from the rulebook. The planner must backtrack because committing to a full Enigma break leaves insufficient credits to handle Wall of Thorns. The successful plan partial-breaks Enigma (lose-click sub fires as a no-op since clicks=0), pumps Crypsis to strength 5 at Wall of Thorns, partial-breaks it (accepting 2 net damage), saves Crypsis with Sacrificial Construct, then steals Nisei MK II (Jinteki PE does 1 more net damage on steal).
- **S4**: Subtype-affinity routing. Corroder (fracter) and Gordian Blade (decoder) don't match Data Raven (sentry); the planner falls back to Crypsis (AI). Data Raven's on-encounter ability fires (take 1 tag).
- **S5**: Wyrm's mandatory `ice_strength_le_zero` break predicate. Wyrm pumps to ice strength to interact, then drains ice strength to zero, then breaks each subroutine — a different cost structure than other icebreakers.
- **S6**: Tight-credit two-ice run. Greedy planner full-breaks Wall of Thorns (5 credits) and has nothing for Enigma; backtracking discovers that partial Wall of Thorns + partial Enigma is feasible.
- **S7**: Crypsis end-of-encounter cleanup chain. No virus counters, no Sacrificial Construct — Crypsis is lost, but only after breaking the ice.
- **S8**: Aggressive Secretary ambush. Corp policy fires the ambush on access (paying 2 credits) and trashes Corroder per priority list.

## Domain Structure

### Card subset (14 cards)

**Corp ice (4)**: Ice Wall, Wall of Thorns, Enigma, Data Raven
**Corp non-ice (4)**: AstroScript Pilot Program, Nisei MK II, Aggressive Secretary, Akitaro Watanabe
**Corp identity (1)**: Jinteki Personal Evolution
**Runner icebreakers (4)**: Corroder, Gordian Blade, Wyrm, Crypsis
**Runner hardware/resources (2)**: The Toolbox, Sacrificial Construct

### Actions (24)

| Group | Actions |
|---|---|
| Setup (3) | `a_install_program`, `a_install_hardware`, `a_install_resource` |
| Run flow (4) | `a_initiate_run`, `a_approach_ice`, `a_pass_ice`, `a_end_run` |
| Encounter mechanics (5) | `a_pump_breaker`, `a_pump_gordian`, `a_drain_ice_strength`, `a_break_subroutine`, `a_end_encounter` |
| Subroutine resolution (5) | `a_resolve_end_run`, `a_resolve_net_damage`, `a_resolve_lose_click`, `a_resolve_trace`, `a_take_tag` |
| Cleanup (3) | `a_spend_virus_counter`, `a_trash_crypsis`, `a_trash_sacrificial_construct` |
| Access (4) | `a_steal_agenda`, `a_pay_trash_cost`, `a_fire_ambush`, `a_trash_program` |

### Methods (17 task names, with alternatives)

| Task | Alternatives | Backtracking point |
|---|---|---|
| `m_steal_agenda` | 1 | — |
| `m_run_on_server`, `m_traverse_ice_stack` | 1 each | — |
| `m_handle_approach`, `m_post_approach` | 1 each | — |
| `m_handle_encounter` | 1 | — |
| `m_handle_data_raven_on_encounter` | 2 | take tag vs. end run |
| `m_break_ice` | **8** | matched vs. AI breaker × full vs. partial |
| `m_resolve_unbroken_subs` | 1 | — |
| `m_crypsis_cleanup` | 4 | counter → SC → trash → skip |
| `m_access_server`, `m_access_one_*` | 1 each | — |
| `m_handle_ambush` | 2 | fire vs. skip |
| `m_decide_trash_asset`, `m_decide_trash_upgrade` | 2 each | pay vs. skip |

## Usage

```python
import copy
import gtpyhop
from gtpyhop.examples.android_netrunner import the_domain, get_problems

problems = get_problems()

# Run the flagship rulebook scenario
state, tasks, desc = problems['scenario_3_rulebook_run_example']
with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
        strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(copy.deepcopy(state), tasks)

print(f"Success: {result.success}, Actions: {len(result.plan)}")
for i, action in enumerate(result.plan):
    print(f"  {i:2d}: {action}")
```

Run doctests (64 tests covering all 8 scenarios + 2 greedy-failure checks):

```bash
python -m doctest -v src/gtpyhop/examples/android_netrunner/problems.py
```

## Modeling notes

The model makes a few deliberate simplifications relative to a full game:

- **Single-agent**: Only the Runner plans. The Corporation is configured environmental state — ice rez timing, ambush firing decisions, and trace credit budgets are specified per scenario.
- **Determinized randomness**: Net damage is modeled as a grip-count decrement, not a multiset trash. Identity of trashed cards is not tracked.
- **Scope A**: Only one run, no setup turn, no multi-run play. The Runner's rig is pre-configured in initial state.
- **Idempotent action elision**: GTPyhop omits actions from the returned plan if they produce no state change. In the rulebook scenario, `a_pass_ice` (Ice Wall not rezzed) and `a_resolve_lose_click` (Runner has 0 clicks) are no-ops and don't appear in `result.plan`.
- **Position-shift sensitivity**: Cards are accessed by *name* rather than by index in the contents list, because stealing/trashing shifts indices.

## Reference

Garfield, R. (designer), and Litzsinger, L. (developer). *Android: Netrunner — The Card Game, Rules of Play* (Fantasy Flight Games, 2012). The page-19 worked example drives the flagship scenario.

## File Structure

```
android_netrunner/
├── __init__.py     # Package initialization
├── domain.py       # 24 actions, 31 method functions (17 task names, 6 with alternatives)
├── problems.py     # 8 scenarios, 64 doctests
└── README.md       # This file
```

---
*Generated 2026-05-15*
