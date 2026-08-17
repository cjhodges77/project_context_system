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
  link     a wikilink that resolves to nothing, or one written inside a code
           span, where Obsidian renders no link at all
  index    a leaf in no index, or in two sibling domain indexes
  name     two concepts claiming the same `name:` identity

Why the link and index checks are machine work
----------------------------------------------
The other checks automate something a careful reviewer could also do. These two
automate something a reviewer *cannot*: **a dead wikilink and a live one are
the same characters in the Markdown diff.** The property only exists in a
resolver that nobody opens during review, so "enforced by review" describes a
procedure that cannot execute. Two consequences were measured on a real bundle
before these were written.

**Backticks are the larger of the two failures and the easier to miss.** A link
written as ``[[x]]`` inside a code span is inert everywhere — no link, no
backlink, no graph edge — while remaining a perfect grep slug. That is the trap:
the working consumer (grep) masks the broken one (the graph), so the convention
looks load-bearing while buying nothing where it was supposed to buy most.

**A `name:` is not a link identity.** Obsidian resolves `[[X]]` by filename or
by an entry in `aliases:`, and never reads `name:`. A corpus that linked by
`name:` had 404 of 414 wikilinks resolving to nothing for the life of the vault.
When a target matches some file's `name:`, the finding says so and names the
repair, because that is the case a reader is most likely to misread as a typo.

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

**Resolution is judged against the bundle, not a vault.** A bundle symlinked
into a wider vault may legitimately link outside itself; `--resolve-root` adds
those directories. Without it, a link out of the bundle reads as unresolved.

**Index coverage asks "at least one", not "exactly one".** A memo routed from
both the root index and `project/index.md` is a normal shape, not drift. The
exactly-one rule is applied only among *sibling domain indexes* — the split
where two homes really does mean one of them goes stale.

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
import tempfile
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

# --- links and identity ------------------------------------------------------
FENCE = re.compile(r"^\s*(?:```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
WIKILINK_ANY = re.compile(r"\[\[([^\[\]]+)\]\]")
# `<angle-bracket>` is this format's documented placeholder spelling. A template
# is not a corpus, and flagging its placeholders would make the templates the
# loudest thing the checker ever reports.
PLACEHOLDER = re.compile(r"[<>]")


def scan_lines(text: str):
    """Yield (lineno, line, code_spans), skipping fenced blocks entirely.

    Fenced blocks are where a document legitimately *shows* the syntax it is
    describing, so nothing inside one is a claim about this bundle.
    """
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield lineno, line, [m.span() for m in INLINE_CODE.finditer(line)]


def wikilinks(line: str, code_spans: list[tuple[int, int]]):
    """Yield (target, inert) per wikilink. `[[a/b#head|display]]` targets `a/b`."""
    for m in WIKILINK_ANY.finditer(line):
        target = m.group(1).split("|", 1)[0].split("#", 1)[0].strip()
        if not target or PLACEHOLDER.search(target):
            continue  # `[[#heading]]` is a same-file jump; `<x>` is a placeholder
        yield target, any(s <= m.start() < e for s, e in code_spans)


def frontmatter(text: str) -> dict:
    """Enough YAML for `name:` and `aliases:`. Stdlib-only is a hard constraint.

    Handles the two spellings a real bundle uses — a block list and an inline
    `[a, b]` — and ignores everything else rather than guessing at it.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict = {}
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith((" ", "\t")):
            item = line.strip()
            if item.startswith("- ") and isinstance(out.get(key), list):
                out[key].append(item[2:].strip().strip("\"'"))
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            out[key] = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
        else:
            out[key] = value.strip("\"'") if value else []
    return out


def link_spellings(rel_no_ext: str) -> list[str]:
    """Every path suffix Obsidian will accept: `a/b/c`, `b/c`, `c`."""
    parts = rel_no_ext.split("/")
    return ["/".join(parts[i:]) for i in range(len(parts))]


class Finding:
    def __init__(self, check: str, path: str, line: int, message: str, snippet: str = "",
                 quote: bool = True):
        self.check = check
        self.path = path
        self.line = line
        self.message = message
        self.snippet = snippet
        # A whole-file finding has no line to quote back; its snippet is a
        # synthetic baseline key, and echoing that at the reader is noise.
        self.quote = quote

    def key(self) -> str:
        """Stable across edits elsewhere in the file — content, not line number."""
        digest = hashlib.sha1(self.snippet.strip().encode("utf-8")).hexdigest()[:12]
        return f"{self.check}:{self.path}:{digest}"

    def render(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        out = f"{where}: {self.message}"
        if self.snippet and self.quote:
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


class Doc:
    """One Markdown file, read once. Corpus checks need every file before any
    verdict, so reading is a separate pass from checking."""

    def __init__(self, path: Path, root: Path, extra: set[str]):
        self.path = path
        self.rel = str(path.relative_to(root.parent) if root.parent != root else path)
        self.key = path.relative_to(root).with_suffix("").as_posix()
        self.archived = "archive" in path.relative_to(root).parts
        self.bad_encoding = False
        try:
            self.text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self.text, self.bad_encoding = "", True
        self.fm = frontmatter(self.text)
        self.index = is_index(path, extra)

    @property
    def leaf(self) -> bool:
        return not self.index and self.path.name != "log.md"


def resolution_set(docs: list[Doc], extra_roots: list[Path]) -> tuple[set[str], dict[str, str]]:
    """Every spelling that resolves, plus a `name:` → file map for repair hints.

    Archived notes are in the resolution set even though they are never linted:
    a live index pointing at archived rationale is the documented shape, not a
    dangling link.
    """
    resolvable: set[str] = set()
    by_name: dict[str, str] = {}
    for doc in docs:
        for spelling in link_spellings(doc.key):
            resolvable.add(spelling.lower())
        aliases = doc.fm.get("aliases") or []
        for alias in aliases if isinstance(aliases, list) else [aliases]:
            if alias:
                resolvable.add(str(alias).strip().lower())
        name = doc.fm.get("name")
        if isinstance(name, str) and name and not PLACEHOLDER.search(name):
            by_name.setdefault(name.lower(), doc.rel)
    for extra_root in extra_roots:
        for path in extra_root.rglob("*.md"):
            rel = path.relative_to(extra_root).with_suffix("").as_posix()
            for spelling in link_spellings(rel):
                resolvable.add(spelling.lower())
    return resolvable, by_name


def check_corpus(docs: list[Doc], args: argparse.Namespace) -> list[Finding]:
    """Checks no single file can answer: does this link land, is this leaf routed."""
    findings: list[Finding] = []
    live = [d for d in docs if not d.archived]

    if not args.no_name:
        seen: dict[str, str] = {}
        for doc in live:
            name = doc.fm.get("name")
            if not isinstance(name, str) or not name or PLACEHOLDER.search(name):
                continue
            first = seen.setdefault(name.lower(), doc.rel)
            if first != doc.rel:
                findings.append(Finding(
                    "name", doc.rel, 0,
                    f"`name: {name}` is already claimed by {first} — a name is a stable "
                    f"identity, and two claims make every reference to it ambiguous",
                    f"name-dup:{name.lower()}:{doc.rel}",
                    quote=False,
                ))

    resolvable, by_name = set(), {}
    if not args.no_resolve:
        resolvable, by_name = resolution_set(docs, [Path(r) for r in (args.resolve_root or [])])

    # leaf key -> the index files that route to it
    routed: dict[str, set[str]] = {d.key: set() for d in live if d.leaf}
    # Every spelling that identifies the leaf counts as routing it, aliases
    # included — otherwise a bundle that links by alias, which is the shape this
    # checker recommends, gets told its leaves are unindexed.
    spelling_owner: dict[str, str] = {}
    leaves = [d for d in live if d.leaf]
    for doc in leaves:
        aliases = doc.fm.get("aliases") or []
        aliases = aliases if isinstance(aliases, list) else [aliases]
        for spelling in link_spellings(doc.key) + [str(a) for a in aliases if a]:
            spelling_owner[spelling.strip().lower()] = doc.key
    # A `name:` routes for coverage purposes even though it does not resolve.
    # The routing intent is unambiguous and the link check already owns that
    # defect; counting it twice would report one mistake as two. Real spellings
    # win a collision, hence setdefault after the loop above.
    for doc in leaves:
        name = doc.fm.get("name")
        if isinstance(name, str) and name and not PLACEHOLDER.search(name):
            spelling_owner.setdefault(name.strip().lower(), doc.key)

    for doc in live:
        for lineno, line, code_spans in scan_lines(doc.text):
            for target, inert in wikilinks(line, code_spans):
                if inert:
                    findings.append(Finding(
                        "link", doc.rel, lineno,
                        f"`[[{target}]]` is inside a code span, where Obsidian renders no "
                        f"link at all — it still greps, which is exactly why this survives "
                        f"unnoticed; drop the backticks",
                        line,
                    ))
                elif not args.no_resolve and target.lower() not in resolvable:
                    owner = by_name.get(target.lower())
                    hint = (
                        f"it is the `name:` of {owner}, which Obsidian never reads — add it "
                        f"to that file's `aliases:` or link by filename"
                        if owner else
                        "nothing in the bundle carries that filename or alias"
                    )
                    findings.append(Finding(
                        "link", doc.rel, lineno,
                        f"`[[{target}]]` resolves to nothing — {hint}",
                        line,
                    ))
                if doc.index:
                    owner_key = spelling_owner.get(target.lower())
                    if owner_key:
                        routed[owner_key].add(doc.rel)

    if args.no_coverage:
        return findings

    for doc in live:
        if not doc.leaf:
            continue
        homes = routed[doc.key]
        if not homes:
            findings.append(Finding(
                "index", doc.rel, 0,
                "no index routes to this leaf — it is unreachable by the documented "
                "retrieval path, so its lesson gets rediscovered rather than reused",
                f"index-none:{doc.key}",
                    quote=False,
            ))
            continue
        # Two sibling domain files claiming one leaf means one of them goes stale.
        # Being routed from both a parent and a domain index is the normal shape.
        domains = sorted(h for h in homes if Path(h).name.startswith("index_"))
        if len(domains) > 1:
            findings.append(Finding(
                "index", doc.rel, 0,
                f"routed from {len(domains)} sibling domain indexes ({', '.join(domains)}) — "
                f"one leaf, one domain home, or the other copy rots",
                f"index-many:{doc.key}",
                    quote=False,
            ))
    return findings


def check_bundle(root: Path, args: argparse.Namespace) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    notes: list[str] = []
    extra = set(args.index or [])

    docs = [Doc(p, root, extra) for p in sorted(root.rglob("*.md"))]
    files = [d for d in docs if not d.archived]
    if not files:
        notes.append(f"no markdown found under {root}")

    findings.extend(check_corpus(docs, args))

    for doc in files:
        path, rel, text = doc.path, doc.rel, doc.text
        if doc.bad_encoding:
            findings.append(Finding("encoding", rel, 0, "not valid UTF-8", rel, quote=False))
            continue

        index = doc.index

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
                    quote=False,
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
                    quote=False,
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
                    quote=False,
                    )
                )

        for lineno, line, _ in scan_lines(text):
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


HEALTHY_BUNDLE = {
    "index.md": (
        '---\npcs_version: "0.1"\n---\n\n# Project context\n\n'
        "## Active projects\n\n- [[project_example]] — what this workstream is for\n\n"
        "## Learnings\n\n- [[learnings_example]] — trigger → consequence\n"
    ),
    "project/project_example.md": (
        "---\ntype: project\nname: example-workstream\n---\n\n"
        "# Example\n\n**Status:** active\n\nBackground.\n"
    ),
    "learnings/learnings_example.md": (
        "---\ntype: learning\nname: example-lesson\n---\n\n"
        "# Example lesson\n\n## Generalized rule\n\nA rule.\n"
    ),
}


def _default_args(**overrides) -> argparse.Namespace:
    base = dict(
        index=None, index_budget=DEFAULT_INDEX_BUDGET, hard_entry=DEFAULT_HARD_ENTRY,
        soft_entry=DEFAULT_SOFT_ENTRY, require_status=False, resolve_root=None,
        no_resolve=False, no_coverage=False, no_name=False,
    )
    base.update(overrides)
    return argparse.Namespace(**base)


def _run_bundle(files: dict[str, str]) -> list[str]:
    """Write a bundle to a temp dir and return the check names it fails."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "memory"
        for rel, body in files.items():
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        findings, _ = check_bundle(root, _default_args())
        return sorted({f.check for f in findings})


def bundle_selftest() -> list[str]:
    """Mutation-prove the corpus checks in both directions.

    A gate whose red path has never been observed is a gate trusted on the
    strength of its docstring. Each case starts from a bundle that must be
    green, introduces exactly one defect, and asserts that *the matching check*
    fires — naming it, so a finding from some other rule cannot pass for a pass.
    """
    failures: list[str] = []
    ran: list[str] = []

    def case(label: str, expect: str | None, **mutations: str | None):
        ran.append(label)
        files = dict(HEALTHY_BUNDLE)
        for rel, body in mutations.items():
            rel = rel.replace("__", "/").replace("_md", ".md")
            if body is None:
                files.pop(rel, None)
            else:
                files[rel] = body
        checks = _run_bundle(files)
        if expect is None and checks:
            failures.append(f"{label}: expected green, got {checks}")
        elif expect is not None and expect not in checks:
            failures.append(f"{label}: expected a {expect!r} finding, got {checks or 'green'}")

    case("healthy bundle", None)

    # The backticked link — inert in every renderer, perfect as a grep slug.
    case("wikilink inside a code span", "link",
         index_md=HEALTHY_BUNDLE["index.md"].replace(
             "[[learnings_example]]", "`[[learnings_example]]`"))

    # `name:` is not a link identity...
    case("link by `name:` with no alias", "link",
         index_md=HEALTHY_BUNDLE["index.md"].replace(
             "[[learnings_example]]", "[[example-lesson]]"))

    # ...until it is declared as one. Same link, opposite verdict.
    case("link by `name:` once aliased", None,
         index_md=HEALTHY_BUNDLE["index.md"].replace(
             "[[learnings_example]]", "[[example-lesson]]"),
         learnings__learnings_example_md=HEALTHY_BUNDLE[
             "learnings/learnings_example.md"].replace(
             "name: example-lesson", "name: example-lesson\naliases:\n  - example-lesson"))

    case("leaf in no index", "index",
         index_md=HEALTHY_BUNDLE["index.md"].replace(
             "- [[learnings_example]] — trigger → consequence\n", ""))

    case("leaf claimed by two sibling domain indexes", "index",
         learnings__index_alpha_md="# Alpha\n\n- [[learnings_example]] — trigger\n",
         learnings__index_beta_md="# Beta\n\n- [[learnings_example]] — trigger\n")

    case("two concepts claiming one `name:`", "name",
         learnings__learnings_other_md=(
             "---\ntype: learning\nname: example-lesson\n---\n\n# Other\n"),
         index_md=HEALTHY_BUNDLE["index.md"] + "- [[learnings_other]] — trigger\n")

    # A link out of the bundle is unresolved by default and forgiven with a root.
    case("link outside the bundle", "link",
         index_md=HEALTHY_BUNDLE["index.md"] + "\nSee [[docs/specs/thing]].\n")

    return failures, len(ran)


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

    bundle_failures, bundle_cases = bundle_selftest()
    failures.extend(bundle_failures)

    if failures:
        print("selftest FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    total = len(flagged) + len(clean) + len(status_flagged) + len(status_clean) + bundle_cases
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
    parser.add_argument("--resolve-root", action="append", metavar="DIR",
                        help="extra directory a wikilink may resolve into, for a bundle "
                             "symlinked inside a wider vault (repeatable)")
    parser.add_argument("--no-resolve", action="store_true",
                        help="skip wikilink resolution (for linting fragments, not a bundle)")
    parser.add_argument("--no-coverage", action="store_true",
                        help="skip the every-leaf-is-indexed check")
    parser.add_argument("--no-name", action="store_true",
                        help="skip the duplicate `name:` check")
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
