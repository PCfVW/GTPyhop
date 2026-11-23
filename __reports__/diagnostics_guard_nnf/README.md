# diagnostics_guard_nnf

Soundness of gtpyhop-diagnostics' guard extraction, 0.1.0 → 0.1.1: which atoms
`explain_dead_end` may name as the precondition that blocked a plan.

## Round 00

- [00-findings_guard_soundness_v0.nb](00-findings_guard_soundness_v0.nb) — **latest**. Wolfram Language proof
  that every atom the fixed extractor yields is a real precondition: the lemmas, an induction on the guard
  expression, an exhaustive cross-check of every guard tree up to 7 nodes, precision, the reported
  reproduction, and a second (control-flow) source of unsound atoms that the fix does not address. Every
  result is a live input with the output it produced.
- [00-findings_guard_soundness_v0.pdf](00-findings_guard_soundness_v0.pdf) — the same notebook as a 12-page
  A4 PDF, appendix printed open, for reading without Mathematica. Regenerate it whenever the notebook changes.
- [00-findings_guard_soundness_v0-build.wl](00-findings_guard_soundness_v0-build.wl) — regenerates the
  notebook: `Get["00-findings_guard_soundness_v0-build.wl"]`, about 25 s.
- [scripts/](scripts/) — the Python measurements behind the counts the notebook cites but cannot prove. Each
  takes paths to `guards.py` versions; get 0.1.0's with
  `git show diagnostics-v0.1.0:packages/gtpyhop-diagnostics/src/gtpyhop/diagnostics/guards.py`.
  - `prop.py GUARDS SEED N` — truth-table soundness and precision over N random guards in 4 guard forms.
  - `examples_diff.py OLD NEW EXAMPLES_DIR` — per declared action, atom sets before and after, over the
    bundled examples.
  - `corpus.py ROOT OLD FIX NNF` — the same over a corpus of generated domains, plus an upper-bound count of
    the control-flow class (`SHOW=1` lists the actions).
  - `cf.py GUARDS` — the control-flow shapes that still yield unsound atoms.

## Status

- The fix is proved sound for every guard expression.
- decision-required: confirm, on keeping commit 3948b54 (the De Morgan split). It refines atoms that were
  already sound, so it is separable from the fix.
- The control-flow source (nested ifs, alternative success branches) is fixed in dc3f852 and proved in
  [diagnostics_guard_cf](../diagnostics_guard_cf/).
