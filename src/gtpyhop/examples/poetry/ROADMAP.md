# Poetry Examples Roadmap

## Background: How LLMs Plan Poems

Anthropic's "Planning in Poems" research (March 2025) discovered that Claude 3.5 Haiku
**plans ahead** when writing rhyming poetry. Rather than improvising word-by-word, the
model:

1. **Forward-plans** the end-word of a line before writing it (e.g., deciding on "rabbit"
   before starting the line)
2. **Backward-constructs** the line to naturally reach that target (e.g., building
   "His hunger was like a starving rabbit" backward from "rabbit")
3. **Maintains multiple candidates** simultaneously ("rabbit", "habit", ...) and selects
   the best fit
4. **Restructures entire lines** when the planned target changes — the target word is a
   control knob, not a patch applied at the end

These findings were obtained by analysing internal model features at the newline token
between lines of a rhyming couplet.

> Prompt: "A rhyming couplet"
> Output: "He saw a carrot and had to grab it, / His hunger was like a starving rabbit"

---

## Existing Examples

### 1. Structured Poetry — Explicit Forward-Backward Planning

Makes the LLM's implicit planning circuit **explicit** via HTN decomposition.
Each rhymed line follows a 3-action cycle:

```
a_select_rhyme_target  →  a_generate_line  →  a_verify_line
   (forward plan)         (backward construct)   (check constraints)
```

This directly models findings 1 and 2 above.

**Forms**: couplet, limerick, haiku, sonnet | **6 actions, 8 methods**

### 2. Backtracking Poetry — Recovery from Rhyme Exhaustion

Extends structured poetry with **two methods** for `m_write_rhymed_line`:
strict (exact rhyme, tried first) and relaxed (near-rhyme, fallback). When a
rhyme label is used 3+ times (e.g., limerick line 5 = 3rd "A"), the strict
action fails and the planner backtracks.

**Demonstrates**: greedy planning fails on limericks; DFS backtracking succeeds.

**Forms**: couplet, limerick, haiku | **7 actions, 9 methods**

---

## Planned Examples

Each new example adds one layer of sophistication, forming a progression:

```
structured  →  backtracking  →  candidate  →  bidirectional  →  replanning
 (1 target)    (fail & retry)   (N targets)   (decomposed       (revise &
                                               construction)     regenerate)
```

### 3. Candidate Planning Poetry — Multiple Candidates

**Paper finding modeled**: *"The model simultaneously maintains multiple candidate
planned words in mind"* — features at the newline token propose several rhyming
words, not just one.

**Core idea**: Replace the single `a_select_rhyme_target` with a generate-rank-commit
pipeline over a candidate pool.

```
m_write_rhymed_line decomposes into:
  a_generate_rhyme_candidates   →  produce N candidate end-words
  a_rank_candidates             →  score by rhyme quality + semantic fit
  a_commit_target               →  select best candidate
  a_generate_line               →  write line toward committed target
  a_verify_line                 →  check constraints
```

**HTN interest**: Backtracking at the candidate level — if the best candidate leads
to an unverifiable line, backtrack and try the next-best candidate.

### 4. Bidirectional Planning Poetry — Decomposed Line Construction

**Paper finding modeled**: Intermediate words (e.g., "like") are determined by
**backward reasoning** from the target ("rabbit"). The model builds a structural
skeleton before generating fluent text.

**Core idea**: Decompose `a_generate_line` into finer-grained backward-planning
and surface-generation steps.

```
m_write_rhymed_line decomposes into:
  a_select_rhyme_target         →  forward: choose end-word
  a_plan_transition             →  backward: plan key intermediate words
  a_generate_surface_text       →  produce fluent text from skeleton
  a_verify_line                 →  check constraints
```

**HTN interest**: A deeper decomposition hierarchy. The transition plan adds an
explicit reasoning step between target selection and text generation.

### 5. Replanning Poetry — Steering and Revision

**Paper finding modeled**: Injecting an alternative planned word causes the model
to **restructure the entire line** (observed in 70% of test poems). The planned
word acts as a control knob for the whole line.

**Core idea**: After initial generation, an evaluation step may trigger replanning
with a different target word, causing complete line regeneration.

```
m_write_rhymed_line decomposes into:
  a_select_rhyme_target         →  choose end-word
  a_generate_line               →  write line toward target
  a_verify_line                 →  check constraints
  m_evaluate_and_replan         →  may replace target and regenerate
```

**HTN interest**: Conditional replanning within the task network. Demonstrates
that changing a single planning decision can cascade through the entire
downstream plan.

---

## Reference

Anthropic, "Circuit Tracing: Revealing Computational Graphs in Language Models",
March 2025 — Section: *Planning in Poems*.

---
*Roadmap Version: 1.0.0 — 2026-02-12*
