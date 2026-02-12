"""
Poetry Examples for GTPyhop

This package contains examples of using GTPyhop for neuro-symbolic poetry
generation via HTN planning. These examples demonstrate hierarchical task
network (HTN) planning for structured poetry workflows where the HTN planner
produces structural plans (form, rhyme scheme, meter) and leaf-level actions
are delegated to external servers (LLM for text generation, phonetics for
rhyme selection and verification).

Examples:
- structured_poetry: Structured poetry generation with support for couplet,
  limerick, haiku, and Shakespearean sonnet forms. Demonstrates coordination
  between a phonetics server (rhyme selection/verification) and an LLM server
  (constrained text generation).
- backtracking_poetry: Extension of structured poetry that tests HTN
  backtracking. Provides two methods for rhymed line composition (strict
  and relaxed) where strict fails on saturated rhyme labels, requiring
  the planner to backtrack. Key test: limerick fails with greedy planner.
- candidate_planning_poetry: Extension of structured poetry that models
  multi-candidate rhyme selection. Replaces the single rhyme target
  selection with a 3-action pipeline (generate candidates, rank, commit)
  modeling the LLM's simultaneous consideration of multiple end-words.
- bidirectional_planning_poetry: Extension of structured poetry that models
  decomposed line construction. Splits line generation into backward
  transition planning (from target word, plan intermediate words) and
  surface text generation (produce fluent text from structural skeleton).
- replanning_poetry: Extension of structured poetry that models post-generation
  evaluation and steering/revision. After initial generation, an evaluation
  step may trigger replanning with a different target word, causing complete
  line regeneration. Uses HTN backtracking at the evaluation level.

-- Generated 2026-02-12
"""

# Make subpackages available
__all__ = ['structured_poetry', 'backtracking_poetry', 'candidate_planning_poetry', 'bidirectional_planning_poetry', 'replanning_poetry']
