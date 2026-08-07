#!/usr/bin/env python3
"""Fail the build when a PCS bundle index restates what another layer owns.

Why this exists
---------------
The one-line rule was enforced by a character budget alone, and a character
budget bounds how large a duplicated summary may be but never whether it
exists. Under pressure it teaches "write a shorter duplicate" rather than
"write a pointer": the compressed entry is still a restatement, still has to be
re-edited on every change, and still goes stale. Measured against a real
46-entry index that passed its size gate clean, most entries carried a value
some other document owned.

This checks *shape*, keyed on **ownership rather than character class** — the
distinction that keeps it usable. A count of open defects is owned by the spec
and changes every time one is fixed; `a card said £300 about a pot holding
£700` is a fixed observation owned by nothing and reads the same in a year.
The first is a restatement, the second is a hook. Only the first is a finding.

What it checks
--------------
  size     file byte budgets — the always-loaded index has a hard harness load
           limit and overflow is dropped in silence, so an oversized index
           deletes the entries below the cut point with no error anywhere
  entry    per-entry character budget
  derived  a computable figure written into prose — name the command instead
  status   a status word in an index entry — status lives in the owning memo
  owner    a project memo with no single `**Status:**` header, or several

Limits, all deliberate
----------------------
**It checks form, never truth.** A green run does not mean the index is
accurate, only that it is not carrying the shapes that rot. Nothing here reads
a leaf file to confirm a pointer still describes it.

**Ownership is approximated by unit and tally, not understood.** A number
carrying a unit (`19,951 bytes`, `~24 KB`, `3 tests`) or forming a tally
(`2 of 6`, `4 defects`) is treated as owned by whatever computes it. A bare
quantity or a currency amount is left alone. That is a proxy: a derived value
written without a unit passes, and an invented tally that never changes is
flagged. Precision was chosen over recall on purpose — see below.

**It must stay green on a healthy bundle.** A check that is red when nothing is
wrong gets bypassed, and a bypassed check is worse than none because it reads
as coverage while enforcing nothing. That is why the status vocabulary is
narrow and unambiguous (`in flight`, `not fixed`, `landed`) rather than
including words a healthy entry uses innocently (`open`, `done`, `pending`),
and why bare numbers are not flagged. It is also why `--write-baseline` exists:
adopt the rule going forward on an existing corpus instead of reddening every
document written before it.

Wire it into a command people already run — a dependency of `lint` or `test`,
not a standalone target. A target nobody invokes is a rule still enforced only
by memory, with the added cost of looking enforced.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# --- budgets -----------------------------------------------------------------
# Set below the cliff, not at it: fail while there is still headroom to compact
# calmly, rather than after content has already been dropped.
DEFAULT_INDEX_BUDGET = 16_000  # ~2/3 of the ~24KB harness limit
DEFAULT_HARD_ENTRY = 400  # narrative, not an index line
DEFAULT_SOFT_ENTRY = 250  # the documented one-line rule; reported, not enforced

# --- noise stripped before matching ------------------------------------------
CODE_SPAN = re.compile(r"`[^`]*`")
WIKILINK = re.compile(r"\[\[[^\]]*\]\]")
MD_LINK_TARGET = re.compile(r"\]\([^)]*\)")
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
HEADING_ANCHOR = re.compile(r"#\S+")

# --- what "another layer owns this" looks like -------------------------------
UNIT = (
    r"%|KB|MB|GB|bytes?|chars?|characters?|lines?|tests?|failures?|errors?"
    r"|warnings?|files?|entries|commits?|PRs?"
)
DERIVED_UNIT = re.compile(rf"\b\d[\d,]*(?:\.\d+)?\s*(?:{UNIT})\b", re.I)
# `2 of 6` is a tally. Bare `2/7` is not: it collides with enumerations
# (`items 2/7/9/10`), fractions, and versions, and flagging it made the check
# noisy on a healthy index — which is how a check gets switched off.
TALLY_OF = re.compile(r"\b\d+\s+of\s+\d+\b", re.I)
TALLY_N = re.compile(
    r"\b\d+\s+(?:findings?|defects?|bugs?|issues?|items?|tasks?|steps?"
    r"|phases?|todos?|remaining|outstanding)\b",
    re.I,
)

# Narrow on purpose. Every word here means status and nothing else; ambiguous
# ones ("open", "done", "pending") are omitted so a healthy index stays green.
STATUS = re.compile(
    r"\b(in flight|in-flight|in progress|not started|not fixed|half done"
    r"|half-done|shipped|landed|merged|deployed|blocked|wip|underway"
    r"|undispatched|awaiting review)\b",
    re.I,
)

# Accepts `**Status:**`, `Status:`, and `**Status: DONE.**` — the spellings a
# real corpus actually uses. Matching only the template's exact form would
# report a formatting preference as a finding.
STATUS_HEADER = re.compile(r"^\s*\*{0,2}Status\b\s*:", re.I | re.M)
BULLET = re.compile(r"^\s*[-*]\s+\S")


class Finding:
    def __init__(self, check: str, path: str, line: int, message: str, snippet: str = ""):
        self.check = check
        self.path = path
        self.line = line
        self.message = message
        self.snippet = snippet

    def key(self) -> str:
        """Stable across edits elsewhere in the file — content, not line number."""
        digest = hashlib.sha1(self.snippet.strip().encode("utf-8")).hexdigest()[:12]
        return f"{self.check}:{self.path}:{digest}"

    def render(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        out = f"{where}: {self.message}"
        if self.snippet:
            preview = self.snippet.strip()
            if len(preview) > 100:
                preview = preview[:97] + "..."
            out += f"\n      {preview}"
        return out


def strip_noise(text: str) -> str:
    """Remove spans that legitimately contain digits: paths, commands, links, dates."""
    text = CODE_SPAN.sub(" ", text)
    text = WIKILINK.sub(" ", text)
    text = MD_LINK_TARGET.sub(" ", text)
    text = HEADING_ANCHOR.sub(" ", text)
    text = ISO_DATE.sub(" ", text)
    return text


# A hedged or bounded figure is a threshold being declared, not a measurement
# being transcribed: `~24KB`, `≤ 200 chars`, `max 400 chars`. Thresholds are
# owned by whoever set them and do not drift on their own. Every bundle that
# documents its own budget states one, so flagging them is systematic noise.
HEDGE = re.compile(r"(?:[~≈≤<≥>]|\b(?:max|maximum|min|minimum|budget|limit|cap|"
                   r"threshold|target|about|approx\w*|roughly|around|up to|"
                   r"at most|no more than|under|over)\b)\s*$", re.I)


def derived_hits(text: str) -> list[str]:
    clean = strip_noise(text)
    hits = []
    for rx in (DERIVED_UNIT, TALLY_OF, TALLY_N):
        for m in rx.finditer(clean):
            if HEDGE.search(clean[: m.start()]):
                continue
            hits.append(m.group(0).strip())
    return hits


def status_hits(text: str) -> list[str]:
    return [m.group(0) for m in STATUS.finditer(strip_noise(text))]


def is_index(path: Path, extra: set[str]) -> bool:
    name = path.name
    return (
        name == "index.md"
        or name.startswith("index_")
        or name.upper() == "INDEX.MD"
        or name.upper().startswith("INDEX_")
        or name in extra
    )


def is_memo(path: Path) -> bool:
    return path.parent.name == "project" and path.name.startswith("project_")


def check_bundle(root: Path, args: argparse.Namespace) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    notes: list[str] = []
    extra = set(args.index or [])

    files = sorted(p for p in root.rglob("*.md") if "archive" not in p.relative_to(root).parts)
    if not files:
        notes.append(f"no markdown found under {root}")

    for path in files:
        rel = str(path.relative_to(root.parent) if root.parent != root else path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(Finding("encoding", rel, 0, "not valid UTF-8", rel))
            continue

        index = is_index(path, extra)

        if index:
            size = path.stat().st_size
            if size > args.index_budget:
                findings.append(
                    Finding(
                        "size",
                        rel,
                        0,
                        f"{size:,} bytes exceeds the {args.index_budget:,}-byte budget "
                        f"(over by {size - args.index_budget:,}); the always-loaded index "
                        f"drops its overflow in silence — move detail to the leaf",
                        f"size:{rel}",
                    )
                )

        if is_memo(path):
            headers = len(STATUS_HEADER.findall(text))
            # More than one is drift by definition — the rule is that status
            # lives in exactly one place, and this memo is the place.
            if headers > 1:
                findings.append(
                    Finding(
                        "owner",
                        rel,
                        0,
                        f"memo declares status {headers} times — status needs exactly "
                        f"one owner that everything else links to",
                        f"owner-many:{rel}",
                    )
                )
            # None at all is a convention this bundle may not have adopted yet.
            # Defaulting it on would redden every memo in an existing corpus,
            # and a check red on a healthy tree gets switched off — so opt in.
            elif headers == 0 and args.require_status:
                findings.append(
                    Finding(
                        "owner",
                        rel,
                        0,
                        "memo has no `**Status:**` header, so nothing can link to its "
                        "status without copying it",
                        f"owner-none:{rel}",
                    )
                )

        for lineno, line in enumerate(text.splitlines(), 1):
            entry = bool(BULLET.match(line))

            # Scoped to indexes on purpose. A leaf holds original content — a
            # learning's evidence is *meant* to carry concrete measurements, and
            # they never change because they describe what happened once. Only a
            # layer holding a restatement needs enforcing, and running this over
            # leaves produced hundreds of findings on a healthy bundle.
            for value in derived_hits(line) if index else []:
                findings.append(
                    Finding(
                        "derived",
                        rel,
                        lineno,
                        f"computable figure in prose ({value!r}) — name the command "
                        f"that computes it instead of transcribing the value",
                        line,
                    )
                )
                break  # one finding per line is enough to act on

            if not index or not entry:
                continue

            if len(line) > args.hard_entry:
                findings.append(
                    Finding(
                        "entry",
                        rel,
                        lineno,
                        f"entry is {len(line)} chars (max {args.hard_entry}) — "
                        f"that is narrative, not an index line",
                        line,
                    )
                )
            elif len(line) > args.soft_entry:
                notes.append(f"{rel}:{lineno}: {len(line)} chars, over the {args.soft_entry}-char guide")

            hits = status_hits(line)
            if hits:
                findings.append(
                    Finding(
                        "status",
                        rel,
                        lineno,
                        f"status word in an index entry ({hits[0]!r}) — status lives in "
                        f"the owning memo's header; link to it rather than restating it",
                        line,
                    )
                )

    return findings, notes


def load_baseline(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def selftest() -> int:
    """Cases that must hold for the ownership distinction to mean anything."""
    flagged = [
        "- 19,951 bytes — 49 short of the gate",
        "- the suite is at 3 failures",
        "- 2 of 6 landed",
        "- TARGET MATHS — 4 defects, 2 are one bug",
        "- index is 24 KB now",
    ]
    # Known miss, recorded rather than hidden: a hedge cannot be told from a
    # threshold mechanically, so a hedged *measurement* passes. Losing this
    # costs less than reddening every bundle that documents its own budget.
    known_misses = ["- index is ~24 KB now"]
    clean = [
        '- B1 — a card said "£300 in the pot" about a pot holding £700',
        "- pot naming a deleted tag reads £0 forever with nothing saying why",
        "- agreed 2026-08-06 — ordered by restatement risk",
        "- see `scripts/check_memory_budget.py` and [[learnings/index]]",
        "- the rounding rule changed in v2 of the spec",
        # declared thresholds, not transcribed measurements
        "**One line per entry, ≤ ~200 chars. Detail lives in the topic file.**",
        "Hard read limit ~24KB; anything past it is silently dropped on load.",
        "- entries are capped at max 400 chars",
        # an enumeration is not a tally
        "- QA intake — on-device Budgets + Tag map; items 2/7/9/10 OPEN.",
        "- URL-backed period — piece 1/3 shipped behind the flag",
    ]
    status_flagged = ["- OWED REGISTER — ready but undispatched", "- STATIC half done"]
    status_clean = ["- open questions about the tag model", "- done deliberately, see the memo"]

    failures = []
    for case in flagged:
        if not derived_hits(case):
            failures.append(f"should flag as derived but did not: {case}")
    for case in clean:
        hits = derived_hits(case)
        if hits:
            failures.append(f"should be clean but flagged {hits}: {case}")
    for case in status_flagged:
        if not status_hits(case):
            failures.append(f"should flag as status but did not: {case}")
    for case in status_clean:
        hits = status_hits(case)
        if hits:
            failures.append(f"should be clean but flagged {hits}: {case}")

    for case in known_misses:
        if derived_hits(case):
            failures.append(f"known miss is now caught — update the docstring: {case}")

    if failures:
        print("selftest FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    total = len(flagged) + len(clean) + len(status_flagged) + len(status_clean)
    print(f"selftest OK ({total} cases, {len(known_misses)} known miss)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint a PCS bundle for entries that restate what another layer owns.",
        epilog="Run it from a command people already invoke, not as a standalone target.",
    )
    parser.add_argument("bundle", nargs="?", default=".claude/memory", help="bundle root")
    parser.add_argument("--index", action="append", metavar="NAME",
                        help="additional filename to treat as an index (repeatable)")
    parser.add_argument("--index-budget", type=int, default=DEFAULT_INDEX_BUDGET)
    parser.add_argument("--hard-entry", type=int, default=DEFAULT_HARD_ENTRY)
    parser.add_argument("--soft-entry", type=int, default=DEFAULT_SOFT_ENTRY)
    parser.add_argument("--baseline", type=Path, metavar="FILE",
                        help="findings recorded here are reported but do not fail")
    parser.add_argument("--write-baseline", action="store_true",
                        help="record current findings to --baseline and exit 0")
    parser.add_argument("--require-status", action="store_true",
                        help="also fail memos with no Status header (opt-in: reddens a "
                             "corpus that has not adopted the convention)")
    parser.add_argument("--quiet", action="store_true", help="suppress soft-rule notes")
    parser.add_argument("--selftest", action="store_true", help="check the rules, not a bundle")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    root = Path(args.bundle)
    if not root.is_dir():
        print(f"pcs-lint: no bundle at {root}", file=sys.stderr)
        return 2

    findings, notes = check_bundle(root, args)

    if args.write_baseline:
        if not args.baseline:
            print("pcs-lint: --write-baseline needs --baseline FILE", file=sys.stderr)
            return 2
        args.baseline.write_text(
            "# pcs-lint baseline — pre-existing findings, so the rule binds new work only.\n"
            "# Delete a line to start enforcing it. Regenerate deliberately, never on a whim.\n"
            + "".join(f"{f.key()}\n" for f in sorted(findings, key=lambda f: f.key())),
            encoding="utf-8",
        )
        print(f"pcs-lint: baselined {len(findings)} finding(s) to {args.baseline}")
        return 0

    baseline = load_baseline(args.baseline)
    live = [f for f in findings if f.key() not in baseline]
    suppressed = len(findings) - len(live)

    if notes and not args.quiet:
        for note in notes[:10]:
            print(f"  note: {note}")
        if len(notes) > 10:
            print(f"  note: ...and {len(notes) - 10} more")

    if live:
        print("\npcs-lint FAILED\n", file=sys.stderr)
        for f in sorted(live, key=lambda f: (f.path, f.line)):
            print(f"  - {f.render()}\n", file=sys.stderr)
        print(
            "An index entry carries a title, a hook, and at most the one fact that\n"
            "decides priority. See FORMAT.md — 'Index entry shape' and 'Derived values'.",
            file=sys.stderr,
        )
        return 1

    tail = f" ({suppressed} baselined)" if suppressed else ""
    print(f"pcs-lint OK{tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
