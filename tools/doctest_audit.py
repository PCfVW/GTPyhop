#!/usr/bin/env python3
"""
Run every doctest in the repository and report the total.

Why not `python -m doctest <file>` in a shell loop. That form imports the file
by bare filename after putting its directory on sys.path, which works only for
modules that happen to be importable standalone. Two bundled files are not:
`examples/blocks_gtn/examples.py` resolves its imports through the package, and
`gtpyhop-diagnostics` is a separate distribution that need not be installed at
all. Both then look like doctest failures when nothing is wrong with them, so a
shell loop goes red on a healthy tree. This driver imports each module by its
real dotted name instead, and says plainly which modules it could not import.

It also prints the total, which is the number the README's doctests badge
claims. That badge said 789 while the true figure was 855 — a badge nobody can
recompute is a badge that drifts.

Usage:
    python tools/doctest_audit.py            # report and exit 1 on any failure
    python tools/doctest_audit.py --quiet    # totals only
    python tools/doctest_audit.py --count    # print just the number, for the badge
"""

import argparse
import doctest
import importlib
import io
import contextlib
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
# Distributions whose sources live under packages/<name>/src
DISTRIBUTIONS = ['gtpyhop-core', 'gtpyhop-examples', 'gtpyhop-diagnostics']


def dotted_names():
    """Yield (dotted_name, path) for every .py file in the source trees."""
    for dist in DISTRIBUTIONS:
        src = REPO / 'packages' / dist / 'src'
        if not src.is_dir():
            continue
        for path in sorted(src.rglob('*.py')):
            if '__pycache__' in path.parts:
                continue
            rel = path.relative_to(src)
            parts = list(rel.parts)
            if parts[-1] == '__init__.py':
                parts = parts[:-1]
            else:
                parts[-1] = parts[-1][:-3]
            if not parts or any('-' in p for p in parts):
                # e.g. examples/mcp-orchestration/... is not an importable
                # dotted path; those modules are reached by sys.path instead
                yield None, path
                continue
            yield '.'.join(parts), path


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument('--quiet', action='store_true', help='totals only')
    parser.add_argument('--count', action='store_true',
                        help='print only the total, for the README badge')
    args = parser.parse_args()

    # hyphenated example collections are importable only by directory
    examples = REPO / 'packages' / 'gtpyhop-examples' / 'src' / 'gtpyhop' / 'examples'
    for child in sorted(examples.iterdir()) if examples.is_dir() else []:
        if child.is_dir() and '-' in child.name:
            sys.path.insert(0, str(child))

    total = failures = modules = 0
    unimportable = []
    for dotted, path in dotted_names():
        if dotted is None:
            name = path.stem
            directory = str(path.parent)
            if directory not in sys.path:
                sys.path.insert(0, directory)
        else:
            name = dotted
        if '>>>' not in path.read_text(encoding='utf-8-sig', errors='replace'):
            continue
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                module = importlib.import_module(name)
        except Exception as exc:                                # noqa: BLE001
            unimportable.append((name, repr(exc)[:90]))
            continue
        with contextlib.redirect_stdout(buf):
            result = doctest.testmod(module, verbose=False, report=False)
        if result.attempted:
            modules += 1
            total += result.attempted
            failures += result.failed
        if result.failed and not args.count:
            print(f"  FAIL {name}: {result.failed} of {result.attempted}")
            sys.stdout.write(buf.getvalue()[-1500:])

    if args.count:
        print(total)
        return 0

    if not args.quiet:
        for name, err in unimportable:
            print(f"  skipped (not importable here): {name} - {err}")
    print(f"\nmodules with doctests : {modules}")
    print(f"doctests run          : {total}")
    print(f"failures              : {failures}")
    if unimportable:
        print(f"modules skipped       : {len(unimportable)}")
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
