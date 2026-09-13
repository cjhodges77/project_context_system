#!/usr/bin/env python3
"""Fail the build when a link between this repository's own documents is dead.

Why this exists
---------------
`pcs_lint.py` checks a PCS *bundle*. This repository is the specification, not
a bundle, and its guides link to each other heavily — by file and by heading
anchor. Those links have the property the format now names explicitly: **a dead
link and a live one are the same characters in the Markdown diff.** The target
is only resolved by a renderer nobody opens while reviewing.

That is not hypothetical here. Restructuring `ADOPTION.md` deleted the heading
`#8-add-enforcement` while a document elsewhere in the tree still pointed at it,
and the review that made the change did not see it. The check costs one pass
over the tree and hangs off the lint target that already runs.

What it checks
--------------
  file     a relative Markdown link whose target file does not exist
  anchor   a `#fragment` naming no heading in the target document

Limits, all deliberate
----------------------
**It checks that a target exists, never that it is the right one.** A link
pointing at a real heading about the wrong subject passes.

**External URLs are not fetched.** Network state is not a property of this
repository, and a check that fails when a third-party site is down is a check
that gets bypassed.

**Fenced blocks are skipped**, because a document that documents a link syntax
is showing an example rather than making a claim about this tree.

**It models one renderer.** `slug()` reimplements github.com's anchor
generation, including the `-1`, `-2` suffixes for repeated headings. Another
renderer needs its own pass, and `--selftest` is the only thing holding this
model to the renderer it claims to match.

The rule that produced that last limit
--------------------------------------
**A check that reimplements a consumer's behaviour needs at least one test
against the actual consumer**, not only against its own model of it. This file
shipped with a docstring saying "GitHub's anchor" and nothing that had ever
asked GitHub. A field report found one divergence by inspection on 2026-09-13;
pinning the cases in `--selftest` against rendered pages found a second one in
the same three lines. Both were wrong in *both* directions at once — a link
written correctly for GitHub failed the gate, and a link written to satisfy the
gate was dead on github.com — so the reflex each produced was to "fix" a
correct link until the gate went green, which is the bypass the format's first
check-design property warns about.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

FENCE = re.compile(r"^\s*(?:```|~~~)")
MD_LINK = re.compile(r"\[[^\]^]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SKIP_SCHEME = ("http://", "https://", "mailto:", "#!", "tel:")
CODE_SPAN_SPLIT = re.compile(r"(`[^`]*`)")
EMPHASIS_UNDERSCORE = re.compile(r"(?<!\w)_+|_+(?!\w)")


def slug(text: str) -> str:
    """The id github.com actually emits for a heading.

    Two details are load-bearing, and both were wrong here until this function
    was first tested against the renderer it models.

    **Every space becomes its own hyphen.** Punctuation is deleted rather than
    replaced, so `A — B` leaves two spaces behind and GitHub emits `a--b`.
    Collapsing whitespace *after* stripping punctuation yields `a-b`, which is
    dead on github.com. Every tier heading in `ADOPTION.md` is that shape.

    **An underscore inside a word survives.** `check_doc_links.py` anchors as
    `check_doc_linkspy`; only the emphasis spelling of `_` is removed, and
    nothing inside a code span is emphasis at all.
    """
    parts = CODE_SPAN_SPLIT.split(text)
    for i, part in enumerate(parts):
        if len(part) > 1 and part.startswith("`") and part.endswith("`"):
            parts[i] = part[1:-1]  # literal: `__init__` keeps its underscores
            continue
        part = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", part)
        parts[i] = EMPHASIS_UNDERSCORE.sub("", part.replace("*", ""))
    text = re.sub(r"[^\w\s-]", "", "".join(parts).lower())
    return text.replace(" ", "-")


def anchors(text: str) -> set[str]:
    """Every fragment this document offers, with GitHub's duplicate suffixes."""
    seen: dict[str, int] = {}
    out: set[str] = set()
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if not match:
            continue
        base = slug(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        out.add(base if count == 0 else f"{base}-{count}")
    return out


def links(text: str):
    """Yield (lineno, target) for every relative link outside a fenced block."""
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in MD_LINK.finditer(line):
            target = match.group(1)
            if not target.startswith(SKIP_SCHEME):
                yield lineno, target


def scan(root: Path) -> tuple[list[str], int]:
    """Return (findings, documents scanned). Printing is main's job, not this."""
    docs = sorted(p for p in root.rglob("*.md") if ".git" not in p.parts)
    cache: dict[Path, set[str]] = {}
    findings: list[str] = []

    for doc in docs:
        for lineno, target in links(doc.read_text(encoding="utf-8")):
            path_part, _, fragment = target.partition("#")
            resolved = (doc.parent / path_part).resolve() if path_part else doc.resolve()
            where = f"{doc}:{lineno}"

            if not resolved.exists():
                findings.append(f"{where}: no such file — {target}")
                continue
            if not fragment or resolved.suffix != ".md":
                continue
            if resolved not in cache:
                cache[resolved] = anchors(resolved.read_text(encoding="utf-8"))
            if fragment not in cache[resolved]:
                findings.append(f"{where}: no heading `#{fragment}` in {path_part or doc.name}")

    return findings, len(docs)


# Verified against github.com on 2026-09-13 by reading the `user-content-` ids
# it emitted for headings that live in this repository. The point of recording
# where they came from is the point of the whole file: a plausible model of a
# consumer is not a tested one, and this list is the test.
VERIFIED_ANCHORS = [
    ("Tier 0 — two files", "tier-0--two-files"),
    ("Tier 3 — registers, research, and ratchets", "tier-3--registers-research-and-ratchets"),
    ("Summary — recommendations at a glance", "summary--recommendations-at-a-glance"),
    (
        "Field report — `budgets_rewritten`, 2026-08-17 → 2026-09-13",
        "field-report--budgets_rewritten-2026-08-17--2026-09-13",
    ),
    (
        "3.6 A defect in `check_doc_links.py`, found by writing this report",
        "36-a-defect-in-check_doc_linkspy-found-by-writing-this-report",
    ),
    (
        '1.2 "Exclude `.claude/` memory" from the graph — reversed here, with two silent traps',
        "12-exclude-claude-memory-from-the-graph--reversed-here-with-two-silent-traps",
    ),
    (
        "2.4 A gate's proof runs in the same command as the gate, from a derived list",
        "24-a-gates-proof-runs-in-the-same-command-as-the-gate-from-a-derived-list",
    ),
]

# Not verified against the renderer: they follow from the same rules and are
# here so a change to them has to state what it is changing. Graded separately
# on purpose — that distinction is what the list above exists to make.
DERIVED_ANCHORS = [
    ("Two ways to bind forward", "two-ways-to-bind-forward"),
    ("Hello, World!", "hello-world"),
    ("**Bold** and _italic_", "bold-and-italic"),
    ("`__init__` is not emphasis", "__init__-is-not-emphasis"),
    ("A note on pcs_lint.py", "a-note-on-pcs_lintpy"),
]

GREEN_TREE = {
    "GUIDE.md": (
        "# Guide\n\n"
        "## Tier 3 — registers, research, and ratchets\n\n"
        "Body.\n\n"
        "## Repeated\n\n## Repeated\n"
    ),
    "README.md": (
        "# Readme\n\n"
        "See [the tier](GUIDE.md#tier-3--registers-research-and-ratchets).\n"
        "See [the second](GUIDE.md#repeated-1) and [the first](GUIDE.md#repeated).\n\n"
        "```markdown\n[an example](NOTHING.md#nowhere)\n```\n"
    ),
}


def selftest() -> int:
    """Prove the red path in both directions, and pin the model to the renderer.

    Anchor cases come first because they are the ones that were wrong: a gate
    that reimplements a renderer fails quietly, in both directions, and looks
    healthy doing it.
    """
    failures: list[str] = []

    for heading, expected in VERIFIED_ANCHORS + DERIVED_ANCHORS:
        got = slug(heading)
        if got != expected:
            failures.append(f"slug({heading!r}) == {got!r}, expected {expected!r}")

    def tree(label: str, expect: str | None, **mutations: str | None):
        files = dict(GREEN_TREE)
        for rel, body in mutations.items():
            rel = rel.replace("_md", ".md")
            files.pop(rel, None) if body is None else files.update({rel: body})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, body in files.items():
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(body, encoding="utf-8")
            findings, _ = scan(root)
        if expect is None and findings:
            failures.append(f"{label}: expected green, got {findings}")
        elif expect is not None and not any(expect in f for f in findings):
            failures.append(f"{label}: expected {expect!r}, got {findings or 'green'}")

    tree("healthy tree", None)
    tree("dead file link", "no such file",
         README_md=GREEN_TREE["README.md"] + "\n[gone](MISSING.md)\n")
    tree("dead anchor", "no heading",
         README_md=GREEN_TREE["README.md"] + "\n[gone](GUIDE.md#no-such-heading)\n")
    # The 2026-09-13 defect, both ways round. The first case was red before the
    # fix and the second was green, which is exactly backwards: the anchor
    # github.com emits is the one with two hyphens.
    tree("em-dash anchor spelled GitHub's way", None)
    tree("em-dash anchor with collapsed hyphens", "no heading",
         README_md="# Readme\n\n[tier](GUIDE.md#tier-3-registers-research-and-ratchets)\n")

    if failures:
        print("check-doc-links selftest FAILED", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    verified = len(VERIFIED_ANCHORS)
    print(
        f"check-doc-links selftest OK ({verified} anchors verified against github.com, "
        f"{len(DERIVED_ANCHORS)} derived, 5 tree cases)"
    )
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()

    root = Path(argv[1] if len(argv) > 1 else ".")
    findings, scanned = scan(root)

    if findings:
        print("check-doc-links FAILED\n", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        print(
            "\nA heading was renamed or a file moved without its inbound links. "
            "Renaming a heading\nis an interface change; the pointers are owed in the "
            "same commit as the rename.",
            file=sys.stderr,
        )
        return 1

    print(f"check-doc-links OK ({scanned} documents)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
