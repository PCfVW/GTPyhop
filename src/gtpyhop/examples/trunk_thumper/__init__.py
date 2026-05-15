"""
Trunk Thumper Examples for GTPyhop

A collection of progressive HTN planning examples based on Troy Humphreys'
*Game AI Pro* chapter "Exploring HTN Planners through Example" (Chapter 12).
Each sub-folder corresponds to a specific section of the chapter and lets a
reader of the book match the code to the chapter text by section number.

Available examples (folder naming sNN_ matches chapter section number §12.NN):

- **s03_basic_attack_or_patrol** - §12.3 baseline.
  Root BeTrunkThumper task with two methods: attack visible enemy, else
  patrol bridges. (5 actions, 1 task name / 2 methods, 2 scenarios)

- **s06_recursive_trunk_replacement** - §12.6 recursion.
  AttackEnemy compound task recurses to find a new trunk when broken.
  (8 actions, 2 task names, 3 scenarios)

- **s07_expected_effects_chase** - §12.7 expected effects.
  Chase enemy with regain-LOS roar, demonstrating the [EXPECTED_EFFECT]
  tag for sensor-driven world state. (10 actions, 2 task names, 3 scenarios)

- **s08_priority_methods** - §12.8 multi-method priorities.
  Recovery, boulder fallback, whirlwind combo with WsIsTired guarding
  against premature combos. (13 actions, 2 task names, 4 scenarios)

- **s09_simultaneous_navigation_and_guard** - §12.9 simultaneous behaviors.
  Single-planner approach with non-blocking navigation enabling a guard
  action during travel. (9 actions, 1 task name, 3 scenarios)

- **s10_partial_plans** - §12.10 partial plans.
  Method-split partial plans for shorter, more reactive plans.
  (5 actions, 2 task names, 3 scenarios)

All examples use MCP_Tool: None (purely symbolic, no external servers).

Credit: This collection is built on the structural blueprint of Troy
Humphreys' chapter. Troy was an AI programmer on *Transformers: Fall of
Cybertron* (HighMoon Studios / Activision, 2012) where the production HTN
system the chapter describes was developed.
"""

__all__ = [
    's03_basic_attack_or_patrol',
    's06_recursive_trunk_replacement',
    's07_expected_effects_chase',
    's08_priority_methods',
    's09_simultaneous_navigation_and_guard',
    's10_partial_plans',
]
