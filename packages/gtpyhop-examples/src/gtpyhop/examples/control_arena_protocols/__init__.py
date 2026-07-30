"""
Control Arena Protocol Examples for GTPyhop

This directory contains examples modeling AI safety micro-protocols from
the Control Arena framework using HTN planning with backtracking.

Available examples:

- **defer_to_trusted_protocol** - Defer to Trusted micro-protocol.
  Backtracking at routing: accept if suspicion <= threshold, else defer.
  (6 actions, 4 methods, 6 scenarios)

- **defer_to_resample_protocol** - Defer to Resample micro-protocol.
  Recursive resampling with backtracking: generate additional samples
  when suspicion is high, defer after exhausting sample budget.
  (6 actions, 5 methods, 6 scenarios)

- **adversarial_protocol** - Adversarial analysis extension.
  Honest vs. attack output generation with calibrated detection rates.
  Identifies protocol vulnerabilities (attack evades monitor).
  (7 actions, 7 methods, 8 scenarios)

All examples use MCP_Tool: None (purely symbolic, no external servers).
"""

__all__ = [
    'defer_to_trusted_protocol',
    'defer_to_resample_protocol',
    'adversarial_protocol',
]
