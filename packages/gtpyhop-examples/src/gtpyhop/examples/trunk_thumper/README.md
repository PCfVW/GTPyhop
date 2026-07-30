# Trunk Thumper Examples for GTPyhop

A collection of progressive HTN planning examples based on **Troy Humphreys' chapter "Exploring HTN Planners through Example"** in *Game AI Pro 1* (Steve Rabin, ed., CRC Press, 2015, pp. 149–167). The chapter walks through the design of a "Trunk Thumper" troll NPC — a big, lumbering troll that patrols bridges and attacks passing enemies with a tree trunk — and progressively enhances the AI through eight design iterations. Each iteration teaches one HTN concept.

This collection translates the chapter's iterations into self-contained GTPyhop examples, one per chapter section.

## Why this collection exists

HTN planning's historical industrial home is **game NPC behavior selection**. Troy's chapter is the canonical pedagogical reference, describing the production HTN system used in *Transformers: Fall of Cybertron* (HighMoon Studios / Activision, 2012). The chapter is explicit that it documents a "total-order forward decomposition planner" — *which is exactly GTPyhop's architecture*. The pseudocode on pp.155–156 reads almost line-for-line like GTPyhop's `iterative_dfs_backtracking` strategy.

This collection fills a real gap in the GTPyhop example library: the existing examples cover security (`cybersecurity_attack_planning`), AI safety (`control_arena_protocols`), and game replication (`android_netrunner`), but none speak directly to the *game AI developer* audience that has historically been HTN's largest user base.

## How to use this collection with the chapter

The sub-folders are named `sNN_<topic>` where `NN` matches the chapter section number. A reader following the chapter in print can open the corresponding folder and find the exact domain the section describes:

| Folder | Chapter section | Topic |
|---|---|---|
| `s03_basic_attack_or_patrol/` | §12.3 | Putting Together an HTN Domain (baseline) |
| `s06_recursive_trunk_replacement/` | §12.6 | Using Recursion for Greater Expressiveness |
| `s07_expected_effects_chase/` | §12.7 | Planning for World State Changes not Controlled by Tasks |
| `s08_priority_methods/` | §12.8 | How to Handle Higher Priority Plans |
| `s09_simultaneous_navigation_and_guard/` | §12.9 | Managing Simultaneous Behaviors |
| `s10_partial_plans/` | §12.10 | Speeding up Planning with Partial Plans |

Sections 12.1, 12.2 (Introduction, Building Blocks), 12.4 (Finding a Plan), and 12.5 (Running the Plan) introduce concepts that GTPyhop already implements — they do not need separate sub-folders. Section 12.11 is the chapter's conclusion.

## Learning path

Read the chapter section first, then study the matching sub-folder's `domain.py` and run its scenarios. The recommended order matches the chapter's progression:

1. **s03** — Establish the baseline. Two methods, no recursion, no complications.
2. **s06** — Add recursion. The chapter's first non-trivial HTN feature.
3. **s07** — Learn the `[EXPECTED_EFFECT]` tag. Includes a negative-control scenario showing what happens *without* expected effects.
4. **s08** — Priority via method ordering, plus the chapter's "subtle bug" example fixed via `WsIsTired`.
5. **s09** — Simultaneous behaviors via the chapter's *recommended* single-planner approach (non-blocking navigation).
6. **s10** — Partial plans via manual method splits.

## What's modeled and what isn't

GTPyhop is a planner. It produces a plan. It does not model:

- **Plan runners / sensors / re-plan logic (§12.5)** — These are runtime concerns. The chapter spends real estate on plan validation during execution; this collection focuses on planning, not execution.
- **Method Traversal Record (MTR) for runtime priority comparison (§12.8)** — MTR is a *runtime* concept for deciding whether a running plan should be aborted in favor of a higher-priority new plan. GTPyhop produces one plan per `find_plan` call and doesn't expose the decomposition trail. The chapter's *underlying claim* — "higher-priority methods are listed first; backtracking falls back to lower-priority methods when constraints fail" — *is* exactly how GTPyhop's method ordering works. We demonstrate the planning side; the runtime comparison side is out of scope.

The collection notes these scope decisions explicitly in each affected sub-folder's README.

## The `[EXPECTED_EFFECT]` tag

Section 12.7 of the chapter introduces "expected effects" — effects applied to the world state only during planning, to represent sensor-driven changes that *will* happen at runtime but aren't directly caused by the operator. In GTPyhop this distinction collapses (no separate runtime), but the *concept* is pedagogically important, so we preserve it via a comment-level tag:

```python
# BEGIN: Effects
# [DATA] Runner moves to destination
state.location = destination

# [EXPECTED_EFFECT] Vision sensor will set this once we arrive
state.can_see_enemy = True
# END: Effects
```

The tag is documented in `docs/gtpyhop_domain_style_guide.md` alongside `[DATA]` and `[ENABLER]`. See `s07_expected_effects_chase/` for the introducing example, including a negative-control scenario where the tag's effect is removed and the plan correctly fails.

## Reference

[Humphreys 15] Humphreys, T. (2015). "Exploring HTN Planners through Example." In *Game AI Pro* (Steve Rabin, ed.). Boca Raton, FL: CRC Press, pp. 149–167.

Related references cited by the chapter:
- [Erol et al. 94] K. Erol, D. Nau, and J. Hendler, "HTN planning: Complexity and expressivity." *AAAI-94 Proceedings*, 1994.
- [Erol et al. 95] K. Erol, J. Hendler, and D. Nau, "Semantics for Hierarchical Task-Network Planning." Technical report TR 95-9, Institute for Systems Research, 1995.
- [Ghallab et al. 04] M. Ghallab, D. Nau, and P. Traverso, *Automated Planning*. San Francisco, CA: Elsevier, 2004, pp. 229–259.
- [HighMoon 12] *Transformers: Fall of Cybertron*. High Moon Studios / Activision Publishing, 2012.
- [Jorkin 04] J. Orkin, "Applying goal-oriented action planning to games." In *AI Game Programming Wisdom 2*, Steve Rabin, ed., Hingham, MA: Charles River Media, 2004, pp. 217–227.

## Acknowledgment

With warm thanks to **Troy Humphreys** for the chapter that is the structural blueprint for this entire collection. The Trunk Thumper is his.

---
*Generated 2026-05-15*
