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

**Anchor generation follows GitHub's rules**, including the `-1`, `-2` suffixes
for repeated headings. A renderer with different rules would need its own pass.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(?:```|~~~)")
MD_LINK = re.compile(r"\[[^\]^]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SKIP_SCHEME = ("http://", "https://", "mailto:", "#!", "tel:")


def slug(text: str) -> str:
    """GitHub's anchor: strip formatting and punctuation, spaces to hyphens."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_]", "", text)
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"\s+", "-", text.strip())


def anchors(path: Path) -> set[str]:
    """Every fragment this document offers, with GitHub's duplicate suffixes."""
    seen: dict[str, int] = {}
    out: set[str] = set()
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
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


def links(path: Path):
    """Yield (lineno, target) for every relative link outside a fenced block."""
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in MD_LINK.finditer(line):
            target = match.group(1)
            if not target.startswith(SKIP_SCHEME):
                yield lineno, target


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".")
    docs = sorted(p for p in root.rglob("*.md") if ".git" not in p.parts)
    cache: dict[Path, set[str]] = {}
    findings: list[str] = []

    for doc in docs:
        for lineno, target in links(doc):
            path_part, _, fragment = target.partition("#")
            resolved = (doc.parent / path_part).resolve() if path_part else doc.resolve()
            where = f"{doc}:{lineno}"

            if not resolved.exists():
                findings.append(f"{where}: no such file — {target}")
                continue
            if not fragment or resolved.suffix != ".md":
                continue
            if resolved not in cache:
                cache[resolved] = anchors(resolved)
            if fragment not in cache[resolved]:
                findings.append(f"{where}: no heading `#{fragment}` in {path_part or doc.name}")

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

    print(f"check-doc-links OK ({len(docs)} documents)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
