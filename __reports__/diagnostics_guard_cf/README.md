# diagnostics_guard_cf

Soundness of gtpyhop-diagnostics' guard extraction over control flow, commit dc3f852: which `if`s
have a requirement at all. This continues [diagnostics_guard_nnf](../diagnostics_guard_nnf/), whose
round 00 proved the splitting of each requirement into atoms and left this second source open (its R6).

## Round 00

- [00-findings_guard_control_flow_v0.nb](00-findings_guard_control_flow_v0.nb) — **latest**. A Wolfram Language
  model of the path-aware analysis and of the `ast.walk` reading it replaces. It proves the analysis sound by
  induction on the statement list, one clause at a time, and cross-checks both readings on every action body of
  up to 6 statements (94,350 bodies). It measures the precision the fix gives up, checks that `guards.py`
  computes exactly what the model predicts, and covers the bundled reproductions. Every result is a live input
  with the output it produced.
- [00-findings_guard_control_flow_v0.pdf](00-findings_guard_control_flow_v0.pdf) — the same notebook as an A4
  PDF, with the appendix printed open. The build regenerates it.
- [00-findings_guard_control_flow_v0-build.wl](00-findings_guard_control_flow_v0-build.wl) — regenerates the
  notebook and the PDF, in about 60 s. Run `wolframscript -file 00-findings_guard_control_flow_v0-build.wl`.
  R5 runs Python, so `python3` and `git` must be on PATH, and the repository must contain dc3f852.
- [scripts/cf_agree.py](scripts/cf_agree.py) — `cf_agree.py OLD_GUARDS NEW_GUARDS programs.json`. It renders each
  enumerated program as a Python action, runs both extractors, and compares their atoms with the model's.
  The build calls it.

## Status

- The fix is proved sound for every program in the model, and the model is checked against the code on every
  enumerated program: 0 mismatches.
- Its precision cost is confined to two places: an `if` inside a loop that is the only way to succeed, and a
  test read twice on one path.
- decision-required: confirm filing the issue with dc3f852 as its fix.
