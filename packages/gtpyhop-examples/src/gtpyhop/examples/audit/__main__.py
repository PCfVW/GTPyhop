#!/usr/bin/env python3
"""Command-line entry point: python -m gtpyhop.examples.audit [PATH]"""

import argparse
import hashlib
import json
import os
import sys

from . import audit_example, find_examples

# Families that fail the build by default. HYGIENE and INFO are reported but
# do not set the exit status unless --strict is given: HYGIENE is dominated by
# terminal effects, which are correct in a planning domain, and INFO records a
# domain that does not follow the a_/m_ naming convention at all.
ENFORCED = ('STRUCTURE', 'SEMANTICS', 'BEHAVIOUR')
ADVISORY = ('HYGIENE', 'INFO')
ORDER = {f: i for i, f in enumerate(ENFORCED + ADVISORY)}

DEFAULT_BASELINE = 'audit_baseline.json'


def fingerprint(example, finding):
    """Stable identity for a finding, independent of line numbers."""
    key = f"{os.path.basename(os.path.normpath(example))}|{finding.family}|" \
          f"{finding.where}|{finding.message}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]


def main():
    parser = argparse.ArgumentParser(
        prog='python -m gtpyhop.examples.audit',
        description='Audit a GTPyhop example against the style guides and '
                    'against itself.')
    parser.add_argument('path', nargs='?',
                        help='example directory (one holding domain.py)')
    parser.add_argument('--all', action='store_true',
                        help='audit every bundled example')
    parser.add_argument('--plan', action='store_true',
                        help='also import and plan: every problem must plan, '
                             'every trap must not, and "-> N actions" claims '
                             'must be true')
    parser.add_argument('--summary', action='store_true',
                        help='one line per example instead of every finding')
    parser.add_argument('--family', choices=sorted(ORDER),
                        help='report only this family')
    parser.add_argument('--strict', action='store_true',
                        help=f'also enforce {" and ".join(ADVISORY)}, which are '
                             f'advisory by default')
    parser.add_argument('--fail-on', type=int, metavar='N', default=0,
                        help='tolerate up to N enforced findings before failing '
                             '(default 0). Use to ratchet a number down over '
                             'time without a baseline file.')
    parser.add_argument('--baseline', metavar='FILE', nargs='?',
                        const=DEFAULT_BASELINE,
                        help=f'ignore findings recorded in FILE (default '
                             f'{DEFAULT_BASELINE}). Anything new still fails, '
                             f'so accepted debt cannot grow.')
    parser.add_argument('--write-baseline', metavar='FILE', nargs='?',
                        const=DEFAULT_BASELINE,
                        help='record the current findings as accepted and exit 0')
    args = parser.parse_args()

    if args.all:
        targets = find_examples()
    elif args.path:
        targets = [args.path]
    else:
        parser.error('give a PATH or --all')

    accepted = {}
    if args.baseline and os.path.exists(args.baseline):
        accepted = json.load(open(args.baseline, encoding='utf-8')).get('accepted', {})

    enforced_families = set(ENFORCED) | (set(ADVISORY) if args.strict else set())
    results, to_record = [], {}
    n_enforced = n_advisory = n_baselined = clean = 0

    for target in targets:
        findings, counts = audit_example(target, plan=args.plan)
        if args.family:
            findings = [f for f in findings if f.family == args.family]
        findings.sort(key=lambda f: (ORDER.get(f.family, 9), f.where))

        kept = []
        for finding in findings:
            fid = fingerprint(target, finding)
            to_record[fid] = f"{os.path.basename(os.path.normpath(target))}: {finding}"
            if fid in accepted:
                n_baselined += 1
                continue
            kept.append(finding)
            if finding.family in enforced_families:
                n_enforced += 1
            else:
                n_advisory += 1
        results.append((target, counts, kept))
        clean += not kept

    if args.write_baseline:
        with open(args.write_baseline, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({
                '_comment': 'Findings accepted as pre-existing. Anything not '
                            'listed here still fails the audit, so this file '
                            'caps existing debt without permitting new debt. '
                            'Delete entries as they are fixed.',
                'accepted': to_record,
            }, fh, indent=2, sort_keys=True)
            fh.write('\n')
        print(f"wrote {len(to_record)} accepted findings to {args.write_baseline}")
        return 0

    for target, counts, findings in results:
        name = os.path.basename(os.path.normpath(target))
        if args.summary:
            shape = (f"{counts.get('actions', 0):3d}a {counts.get('methods', 0):3d}m"
                     if counts else '  -     -')
            status = 'clean' if not findings else f"{len(findings):3d} findings"
            print(f"  {name:<46} {shape}   {status}")
            continue
        print(f"\n=== {name} ({target}) ===")
        if counts:
            print(f"  {counts['actions']} actions, {counts['methods']} methods "
                  f"over {counts['task_names']} task names, "
                  f"{counts['helpers']} helpers")
        if not findings:
            print("  clean")
        for finding in findings:
            print(f"  {finding}")

    if len(targets) > 1 or n_advisory or n_baselined:
        print(f"\n{clean}/{len(targets)} examples clean; "
              f"{n_enforced} enforced, {n_advisory} advisory"
              + (f", {n_baselined} baselined" if n_baselined else ""))
    if n_enforced > args.fail_on:
        if args.fail_on:
            print(f"FAIL: {n_enforced} enforced findings exceeds --fail-on {args.fail_on}")
        return 1
    if args.fail_on and n_enforced:
        print(f"OK: {n_enforced} enforced findings within --fail-on {args.fail_on}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
