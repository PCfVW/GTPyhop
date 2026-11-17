# diagnostics_guard_cf

Soundness and completeness of gtpyhop-diagnostics' guard extraction over control flow, commits dc3f852
and caa3a1b: which `if`s have a requirement at all. This continues [diagnostics_guard_nnf](../diagnostics_guard_nnf/), whose
round 00 proved the splitting of each requirement into atoms and left this second source open (its R6).

## Round 00

- [00-findings_guard_control_flow_v0.nb](00-findings_guard_control_flow_v0.nb). A Wolfram Language
  model of the path-aware analysis and of the `ast.walk` reading it replaces. It proves the analysis sound by
  induction on the statement list, one clause at a time, and cross-checks both readings on every action body of
  up to 6 statements (94,350 bodies). It measures the precision the fix gives up, checks that `guards.py`
  computes exactly what the model predicts, and covers the bundled reproductions. Every result is a live input
  with the output it produced.
- [00-findings_guard_control_flow_v0.pdf](00-findings_guard_control_flow_v0.pdf) — the same notebook as an A4
  PDF, with the appendix printed open. The build regenerates it.
- [00-findings_guard_control_flow_v0-build.wl](00-findings_guard_control_flow_v0-build.wl) — regenerates the
  notebook and the PDF, in about 60 s. Run `wolframscript -file 00-findings_guard_control_flow_v0-build.wl`.
  R5 runs Python, so `python3` and `git` must be on PATH, and the repository must contain dc3f852. R5 reads
  `guards.py` from dc3f852 with `git show`, so later commits do not change its result.
- [scripts/cf_agree.py](scripts/cf_agree.py) — `cf_agree.py OLD_GUARDS NEW_GUARDS programs.json`. It renders each
  enumerated program as a Python action, runs both extractors, and compares their atoms with the model's.
  The builds of both rounds call it.

## Round 01

- [01-findings_guard_completeness_v0.nb](01-findings_guard_completeness_v0.nb) — **latest**. The same model, for
  caa3a1b, which emits atoms straight from the analysis and drops the per-`if` reading. It proves termination
  (at most one step per statement), proves the analysis complete relative to independent tests (each `if` reads
  its own test, no successful return inside a loop: it reports exactly the necessary literals), and checks the
  theorem on every eligible body of up to 6 statements. It states what a reported atom guarantees (a false one
  must be made true by any repair), and the three limits of that guarantee. It counts the misses by cause and
  the literals caa3a1b gains over dc3f852, and checks both commits' `guards.py` against the model.
- [01-findings_guard_completeness_v0.pdf](01-findings_guard_completeness_v0.pdf) — the same notebook as an A4 PDF.
- [01-findings_guard_completeness_v0-build.wl](01-findings_guard_completeness_v0-build.wl) — regenerates both, in
  about 2 min. `GUARD_MAX_SIZE=4` and `GUARD_OUT=draft.nb` give a quick draft elsewhere. R6 needs
  `python3`, `git`, and commits dc3f852 and caa3a1b.

## Status

- The fix is proved sound for every program in the model, and the model is checked against the code on every
  enumerated program: 0 mismatches.
- Its precision cost is confined to two places: an `if` inside a loop that is the only way to succeed, and a
  test read twice on one path. Round 01 proves there is no third: with independent tests and no success inside
  a loop, caa3a1b reports exactly the necessary literals.
- The guarantee runs one way: a false reported atom is necessary, but making every atom true does not ensure
  success, and a requirement that is a disjunction is never an atom. Telling consumers so is a separate change.
- decision-required: confirm filing the issue with dc3f852 and caa3a1b as its fix.
