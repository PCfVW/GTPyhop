"""
Colt Express Examples for GTPyhop

A collection of progressive HTN planning examples based on the Colt Express
board game (Christophe Raimbault / Jordi Valbuena, Ludonaute 2014). Each
sub-folder demonstrates one HTN concept applied to the game's mechanics,
mirroring the structural template of the trunk_thumper collection.

Scope: only the **Stealin' phase** is modeled. The programmed deck is
pre-encoded in `state.deck` and the planner resolves it action-by-action,
filling in the parameter choices the rules leave open (Move direction, Fire
target, Robbery pick). The Schemin' phase (strategic card selection under
imperfect information) is out of scope for this collection.

Available examples:

- **s1_minimal_turn** - baseline priority methods.
  Root `m_take_turn` task with two methods: rob loot at the bandit's
  position (priority), else move forward.
  (3 actions, 1 task name / 2 methods, 3 scenarios)

- **s3_marshal_expected_effects** - [EXPECTED_EFFECT] tag + negative control.
  Marshal forced-escape encoded as a planning-time effect inside `a_move`;
  scenario 3 demonstrates plan failure when the tag is omitted.
  (7 actions incl. demo variant, ~5 methods, 3 scenarios)

- **s2_recursive_round** - recursion over the programmed deck.
  `m_resolve_programmed_deck` decomposes recursively into action + recursive
  subtask, terminating via head-pop on `state.deck`.
  (5 actions, 3 task names, 3 scenarios)

- **s4_character_priorities** - priority methods + character abilities.
  Belle (target-immunity guard), Tuco (fire-through-floor), Django
  (knockback fire), Cheyenne (keep-punched-purse) dispatched via priority-
  ordered method ladders on `m_resolve_fire` / `m_resolve_punch`.
  (~10 actions, ~5 task names, 3 scenarios)

- **s5_partial_plan_movement** - manual method-split for partial plans.
  `m_resolve_move_partial_plan` returns one action; the planner can re-run
  on the resulting state to pick the next action based on updated context.
  (5 actions reused, 2 task names, 3 scenarios)

Build order rationale: s1 -> s3 -> s2 -> s4 -> s5. s3 locks the Marshal-push
and bandit-level state shape (the trickiest part of Colt Express) before
later sub-folders are built on top of it.

All examples use MCP_Tool: None (purely symbolic, no external servers).

Credit: This collection is built on the structural blueprint of the
trunk_thumper collection (based on Troy Humphreys' Game AI Pro chapter
"Exploring HTN Planners through Example", CRC Press 2015) applied to the
Colt Express board game by Christophe Raimbault and Jordi Valbuena
(Ludonaute, 2014).
"""

__all__ = [
    's1_minimal_turn',
    's3_marshal_expected_effects',
    's2_recursive_round',
    's4_character_priorities',
    's5_partial_plan_movement',
]
