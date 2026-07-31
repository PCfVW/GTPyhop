#!/usr/bin/env python3
"""
Check every internal link in the repository's tracked Markdown files.

Two link classes are resolved against the working tree:

  1. Absolute self-links, i.e. links back into this repository on GitHub:
         https://github.com/PCfVW/GTPyhop/{blob,tree}/<ref>/<path>
     The trailing <path> is optional -- `.../tree/pip` addresses the
     repository root at a branch and is valid with no path at all.

  2. Relative Markdown links, e.g. [text](../../docs/logging.md), which
     are resolved relative to the file that contains them.

External hosts, `mailto:` and pure `#anchor` links are counted but never
failed: this tool answers "does this repository still contain what its own
documentation points at", which is checkable offline and deterministic.
Anchor fragments are stripped before resolution -- whether a heading
exists is a separate question this tool does not attempt.

Why this exists: the 2.0.0 restructuring moved every example from
`src/gtpyhop/examples/` to `packages/gtpyhop-examples/src/gtpyhop/examples/`,
which silently invalidated 100+ links and, less obviously, every relative
link that walked `../` up to what used to be the repository root. Grep
finds the first kind; only resolution finds the second.

Usage:
    python tools/link_audit.py           # report, exit 1 if anything is broken
    python tools/link_audit.py --quiet   # totals only
    python tools/link_audit.py --list-external

Intended as a pre-release check: README.md becomes the PyPI
long-description at publish time, where a broken link is more visible and
less fixable than one on GitHub.
"""

import argparse
import os
import re
import subprocess
import sys
import urllib.parse

# A self-link with an optional trailing path (see module docstring).
SELF_LINK = re.compile(
    r"https://github\.com/PCfVW/GTPyhop/(blob|tree)/([A-Za-z0-9._-]+)(?:/([^)\s\"'>]+))?"
)
# [text](target) -- target may carry a title, e.g. [x](path "Title").
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def repo_root():
    """Locate the repository root, so the tool works from any directory."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to this file's parent directory (tools/ -> repo root).
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tracked_markdown(root):
    out = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


def clean_target(raw):
    """Strip an anchor, a link title, and trailing sentence punctuation."""
    target = raw.strip().split()[0] if raw.strip() else ""
    target = urllib.parse.unquote(target)
    target = target.split("#", 1)[0]
    return target.rstrip(".,;")


def audit(root, files):
    result = {
        "ok_absolute": 0, "ok_relative": 0, "anchors": 0,
        "broken_absolute": [], "broken_relative": [],
        "foreign_ref": [], "external": {},
    }

    for rel in files:
        path = os.path.join(root, rel)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError as exc:                      # pragma: no cover
            print("could not read {}: {}".format(rel, exc), file=sys.stderr)
            continue

        for kind, ref, raw_target in SELF_LINK.findall(text):
            if ref != "pip":
                result["foreign_ref"].append((rel, ref))
            target = clean_target(raw_target)
            if not target:
                # `.../tree/pip` -- the repository root itself.
                result["ok_absolute"] += 1
                continue
            if os.path.exists(os.path.join(root, target)):
                result["ok_absolute"] += 1
            else:
                result["broken_absolute"].append(
                    (rel, "{}/{}/{}".format(kind, ref, target)))

        for raw_link in MD_LINK.findall(text):
            link = raw_link.strip()
            if link.startswith("#"):
                result["anchors"] += 1
                continue
            if link.startswith(("http://", "https://", "mailto:")):
                if "github.com/PCfVW/GTPyhop" not in link:
                    host = urllib.parse.urlparse(link).netloc or "mailto:"
                    result["external"][host] = result["external"].get(host, 0) + 1
                continue
            target = clean_target(link)
            if not target:
                continue
            resolved = os.path.normpath(
                os.path.join(os.path.dirname(path), target))
            if os.path.exists(resolved):
                result["ok_relative"] += 1
            else:
                result["broken_relative"].append((rel, target))

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Resolve every internal Markdown link against the working tree.")
    parser.add_argument("--quiet", action="store_true", help="totals only")
    parser.add_argument("--list-external", action="store_true",
                        help="also list external hosts and their link counts")
    args = parser.parse_args()

    root = repo_root()
    files = tracked_markdown(root)
    result = audit(root, files)

    broken = result["broken_absolute"] + result["broken_relative"]

    print("markdown files scanned : {}".format(len(files)))
    print("absolute self-links OK : {}".format(result["ok_absolute"]))
    print("relative links OK      : {}".format(result["ok_relative"]))
    print("anchor-only links      : {}".format(result["anchors"]))
    print("broken                 : {}".format(len(broken)))

    if not args.quiet:
        for label, items in (("absolute", result["broken_absolute"]),
                             ("relative", result["broken_relative"])):
            if items:
                print("\nBROKEN {} ({}):".format(label, len(items)))
                for rel, target in items:
                    print("  {}\n      -> {}".format(rel, target))

        if result["foreign_ref"]:
            print("\nself-links pointing at a ref other than 'pip' "
                  "({}):".format(len(result["foreign_ref"])))
            for rel, ref in result["foreign_ref"]:
                print("  {} -> {}".format(rel, ref))

        if args.list_external:
            print("\nexternal hosts (not checked):")
            for host, count in sorted(result["external"].items(),
                                      key=lambda kv: (-kv[1], kv[0])):
                print("  {:>4}  {}".format(count, host))

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
