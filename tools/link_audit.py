#!/usr/bin/env python3
"""
Check every internal link in the repository's tracked Markdown files.

Three things are resolved against the working tree:

  1. Absolute self-links, i.e. links back into this repository on GitHub:
         https://github.com/PCfVW/GTPyhop/{blob,tree}/<ref>/<path>
     The trailing <path> is optional -- `.../tree/pip` addresses the
     repository root at a branch and is valid with no path at all.

  2. Relative Markdown links, e.g. [text](../../docs/logging.md), which
     are resolved relative to the file that contains them.

  3. Anchor fragments, e.g. [text](faq.md#what-must-an-action-return) or a
     same-file [text](#installation). The fragment is slugified the way
     GitHub renders headings and matched against the target's actual
     headings.

External hosts and `mailto:` are counted but never failed: this tool answers
"does this repository still contain what its own documentation points at",
which is checkable offline and deterministic.

Why this exists. The 2.0.0 restructuring moved every example from
`src/gtpyhop/examples/` to `packages/gtpyhop-examples/src/gtpyhop/examples/`,
silently invalidating 100+ links and, less obviously, every relative link
that walked `../` up to what used to be the repository root. Grep finds the
first kind; only resolution finds the second.

Anchor checking was added after an earlier version of this tool reported a
clean run while all fourteen table-of-contents entries in
`docs/all_examples.md` were dead: each pointed at `#-learning-path` and
friends, a leading hyphen left behind when emoji were stripped from the
headings. Every target file existed, so target-only checking saw nothing
wrong. A link can name a real file and a section that does not exist.

A fourth rule applies only to `packages/*/README.md`. Each package declares
`readme = "README.md"` relative to its OWN directory, so those four files --
and not the repository root README -- are what PyPI renders as each
project's long description. PyPI renders them standalone, with no
repository around them, so a relative link that resolves perfectly here is
broken there. Relative links in those files are therefore reported even
when their target exists.

Usage:
    python tools/link_audit.py           # report, exit 1 if anything is broken
    python tools/link_audit.py --quiet   # totals only
    python tools/link_audit.py --list-external

Intended as a pre-release check: a broken link on PyPI is more visible and
much less fixable than one on GitHub, since correcting it means publishing
a new version.
"""

import argparse
import os
import re
import subprocess
import sys
import urllib.parse

# A self-link with an optional trailing path and optional #fragment.
SELF_LINK = re.compile(
    r"https://github\.com/PCfVW/GTPyhop/(blob|tree)/([A-Za-z0-9._-]+)(?:/([^)\s\"'>]+))?"
)
# [text](target) -- target may carry a title, e.g. [x](path "Title").
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


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


def slugify(heading):
    """
    Render a heading the way GitHub derives its anchor: strip inline
    formatting, lowercase, drop punctuation, and hyphenate spaces.

    Close enough for this repository's headings. It is deliberately strict
    about punctuation, since that is exactly where the all_examples.md
    breakage lived.
    """
    text = heading.strip()
    text = re.sub(r"`([^`]*)`", r"\1", text)              # code spans
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)        # bold
    text = re.sub(r"\*([^*]*)\*", r"\1", text)            # italics
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links -> their text
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)                  # drop punctuation
    return text.strip().replace(" ", "-")


def anchors_of(path, _cache={}):
    """Every anchor a Markdown file offers, from its headings."""
    if path in _cache:
        return _cache[path]
    found = set()
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            in_code = False
            for line in handle:
                if line.lstrip().startswith("```"):
                    in_code = not in_code          # ignore # inside code fences
                    continue
                if in_code:
                    continue
                match = HEADING.match(line)
                if match:
                    found.add(slugify(match.group(2)))
    except OSError:                                # pragma: no cover
        pass
    _cache[path] = found
    return found


def split_target(raw):
    """Return (path_part, fragment) from a link target, both unquoted."""
    target = raw.strip().split()[0] if raw.strip() else ""
    target = urllib.parse.unquote(target)
    if "#" in target:
        filepart, frag = target.split("#", 1)
    else:
        filepart, frag = target, ""
    return filepart.rstrip(".,;"), frag.strip()


def audit(root, files):
    result = {
        "ok_absolute": 0, "ok_relative": 0, "ok_anchor": 0,
        "broken_absolute": [], "broken_relative": [], "broken_anchor": [],
        "pypi_relative": [], "foreign_ref": [], "external": {},
    }

    def is_pypi_readme(rel_path):
        """A packages/<dist>/README.md, i.e. a PyPI long description."""
        parts = rel_path.replace("\\", "/").split("/")
        return (len(parts) == 3 and parts[0] == "packages"
                and parts[2].lower() == "readme.md")

    def check_anchor(source_rel, target_path, frag):
        if not frag:
            return
        if not os.path.isfile(target_path):
            return          # the target failure is already reported
        if frag.lower() in anchors_of(target_path):
            result["ok_anchor"] += 1
        else:
            result["broken_anchor"].append(
                (source_rel, os.path.relpath(target_path, root), frag))

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
            target, frag = split_target(raw_target)
            if not target:
                # `.../tree/pip` -- the repository root itself.
                result["ok_absolute"] += 1
                continue
            resolved = os.path.join(root, target)
            if os.path.exists(resolved):
                result["ok_absolute"] += 1
                check_anchor(rel, resolved, frag)
            else:
                result["broken_absolute"].append(
                    (rel, "{}/{}/{}".format(kind, ref, target)))

        for raw_link in MD_LINK.findall(text):
            link = raw_link.strip()
            if link.startswith(("http://", "https://", "mailto:")):
                if "github.com/PCfVW/GTPyhop" not in link:
                    host = urllib.parse.urlparse(link).netloc or "mailto:"
                    result["external"][host] = result["external"].get(host, 0) + 1
                continue
            target, frag = split_target(link)
            if not target:
                # A same-file anchor, e.g. a table of contents entry.
                check_anchor(rel, path, frag)
                continue
            if is_pypi_readme(rel):
                # Resolves here, but PyPI renders this file standalone.
                result["pypi_relative"].append((rel, target))
                continue
            resolved = os.path.normpath(
                os.path.join(os.path.dirname(path), target))
            if os.path.exists(resolved):
                result["ok_relative"] += 1
                check_anchor(rel, resolved, frag)
            else:
                result["broken_relative"].append((rel, target))

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Resolve every internal Markdown link, and its #anchor, "
                    "against the working tree.")
    parser.add_argument("--quiet", action="store_true", help="totals only")
    parser.add_argument("--list-external", action="store_true",
                        help="also list external hosts and their link counts")
    args = parser.parse_args()

    root = repo_root()
    files = tracked_markdown(root)
    result = audit(root, files)

    broken = (result["broken_absolute"] + result["broken_relative"]
              + result["broken_anchor"] + result["pypi_relative"])

    print("markdown files scanned : {}".format(len(files)))
    print("absolute self-links OK : {}".format(result["ok_absolute"]))
    print("relative links OK      : {}".format(result["ok_relative"]))
    print("anchors resolved       : {}".format(result["ok_anchor"]))
    print("broken                 : {}".format(len(broken)))

    if not args.quiet:
        for label, items in (("absolute", result["broken_absolute"]),
                             ("relative", result["broken_relative"])):
            if items:
                print("\nBROKEN {} ({}):".format(label, len(items)))
                for rel, target in items:
                    print("  {}\n      -> {}".format(rel, target))

        if result["broken_anchor"]:
            print("\nBROKEN anchors ({}) — the file exists, the heading does "
                  "not:".format(len(result["broken_anchor"])))
            for rel, target, frag in result["broken_anchor"]:
                print("  {}\n      -> {}#{}".format(rel, target, frag))

        if result["pypi_relative"]:
            print("\nRELATIVE links in a PyPI long description ({}) — these "
                  "resolve here but break on PyPI; use an absolute "
                  "https://github.com/... URL:".format(len(result["pypi_relative"])))
            for rel, target in result["pypi_relative"]:
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
