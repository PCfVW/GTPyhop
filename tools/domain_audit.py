#!/usr/bin/env python3
"""
Run the example auditor from a repository checkout.

The auditor itself ships inside `gtpyhop-examples`, at
`packages/gtpyhop-examples/src/gtpyhop/examples/audit/`, and for anyone who
installed from PyPI the documented invocation works directly:

    python -m gtpyhop.examples.audit --all

That invocation does **not** work from an editable install, which is what a
contributor has. Both distributions install as a bare `.pth` adding their own
`src/` to `sys.path`; `gtpyhop-core/src/gtpyhop/` has an `__init__.py` and is
therefore a regular package, while `gtpyhop-examples/src/gtpyhop/` has none
and is a namespace portion. Python stops at the first regular package it
finds and discards namespace portions, so `gtpyhop` resolves to core alone and
`gtpyhop.examples` does not exist:

    $ python -m gtpyhop.examples.audit --all
    ModuleNotFoundError: No module named 'gtpyhop.examples'

Installed wheels do not have this problem, because both distributions unpack
into the same physical `site-packages/gtpyhop/` directory and the merge
happens on disk.

This shim points straight at the examples tree in the working copy, so the
audit runs the same way in either situation. It takes the same arguments as
the module.

Usage:
    python tools/domain_audit.py --all --summary
    python tools/domain_audit.py packages/gtpyhop-examples/src/gtpyhop/examples/poetry/structured_poetry
    python tools/domain_audit.py <example-dir> --plan

See the auditor's own README for what each family of check does and why:
packages/gtpyhop-examples/src/gtpyhop/examples/audit/README.md
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(REPO_ROOT, 'packages', 'gtpyhop-examples', 'src',
                        'gtpyhop', 'examples')
CORE = os.path.join(REPO_ROOT, 'packages', 'gtpyhop-core', 'src')


def main():
    if not os.path.isdir(EXAMPLES):
        print(f"error: examples tree not found at {EXAMPLES}", file=sys.stderr)
        return 2
    # The examples tree first, so 'audit' resolves to the packaged auditor;
    # core so that --plan can import gtpyhop without an install.
    sys.path.insert(0, EXAMPLES)
    sys.path.insert(1, CORE)
    from audit.__main__ import main as audit_main       # noqa: PLC0415
    return audit_main()


if __name__ == '__main__':
    sys.exit(main())
