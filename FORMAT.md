# Format and lifecycle

## Bundle

`.claude/memory/` is the PCS bundle root and unit of distribution. Product docs and source code remain outside it. The root `index.md` declares the format version:

```yaml
---
pcs_version: "0.1"
---
```

## Knowledge unit

Each concept is one UTF-8 Markdown file with YAML frontmatter and a focused body:

```yaml
---
type: project
name: stable-kebab-case-identity
title: Human-readable title
description: One sentence that lets an agent decide whether to open this file.
resource: docs/specs/example.md
tags:
  - domain-name
timestamp: 2026-07-20T00:00:00Z
metadata:
  type: project
---
```

`type` is required for routing. `name` is a stable identity. `title`, `description`, `resource`, `tags`, and `timestamp` support display, retrieval, provenance, categorization, and freshness. Fields other than `type` are optional. Consumers must preserve unknown fields and tolerate unknown `type` values.

## Concept types

### `project/`

Active workstream state: objective, decisions, shipped scope, open questions, living-document deltas, and related concepts. Move shipped or stale memos to `archive/` after durable outcomes reach canonical docs.

### `feedback/`

Persistent behavioral rules derived from user instruction, review, retrospectives, or observed failure. Include the rule, rationale, application, and enforcement.

### `learnings/`

Reusable technical lessons with symptom, root cause, evidence, fix, generalized rule, and verification. Keep one learning per file and one concise entry in `learnings/index.md` — or, once the catalog outgrows a few kilobytes, in the appropriate `learnings/index_<domain>.md` (see "Domain sub-indexes" below).

### `references/`

Curated external sources and provenance needed to understand bundle claims. A reference concept records the source's canonical URI in `resource`, its relevance, and any scope or reliability notes.

### `archive/`

Searchable historical state that is no longer part of the active retrieval path. Archive rather than silently deleting useful rationale.

## Reserved files

### `index.md`

The root `index.md` is the starting map and declares `pcs_version`. Any bundle directory may contain a lowercase `index.md`. Keep entries concise and use Obsidian wikilinks to concepts. A root index should route to active projects, feedback, learning domains, references, and archive guidance.

### `log.md`

A lowercase `log.md` is optional. Use it when distributing a bundle without Git history. Group entries under ISO `YYYY-MM-DD` headings, newest first. Git remains the primary history layer.

## Index size budgets

Indexes are retrieval surfaces, not summaries of record. Harnesses load the always-read index with a hard size limit and **silently drop the overflow** — observed in practice at ~24 KB. Budget accordingly:

- Keep the always-loaded index well under the harness limit; target roughly two-thirds of it.
- One line per entry: *trigger → consequence → pointer*, around 200–250 characters. Detail lives in the leaf concept, never inline.
- A long entry in a hard-limited index does not merely bloat it — **it deletes the entries below it**. Treat entry length as a correctness property, not a style preference.
- When shortening an entry, check what its tail carried: corrections and caveats often live at the end of a line, and truncation silently reverts them.

## Domain sub-indexes

When a catalog index outgrows a few kilobytes, split it into a **hub** and per-domain files: the hub (`learnings/index.md`) holds a table of domains — each row a wikilink, an entry count, and an "open when touching" scope — and each domain file (`learnings/index_<domain>.md`) holds that domain's one-line entries. Agents grep the domain files for triggers and open only the leaf they need.

Do not hand-maintain a grand total in the hub; it drifts within days. Derive it (`ls learnings/*.md | wc -l`) and say so in a comment where the total would have been. Per-domain counts in the hub rows are acceptable: each is updated by the same edit that files the entry.

## Restructuring an index

Before any whole-file index rewrite or split, preserve the outgoing file verbatim in `archive/` (`archive_<name>_longform_<date>.md`) in the same change. Move, don't delete: content arrives somewhere before it leaves the index. After migrating, verify every entry appears exactly once across the successor files and every leaf still resolves — the check is mechanical and cheap, and skipping it is how entries vanish without anyone deciding they should.

## Index entry shape

A size budget limits how large a duplicate may be, not whether it exists. Under pressure a character limit teaches *"write a shorter duplicate"* rather than *"write a pointer"*: an over-budget entry gets compressed into a terser restatement that still has to be re-edited on every change and still goes stale. Constrain shape, not only length.

An index entry carries a **title, a hook, and at most the one fact that decides priority** — never findings, never numbers, never status. If you are tempted to add a number, the hook is too weak.

The pressure to overfill an index is structural and worth naming: the always-loaded index is the only layer *guaranteed* to be read, so there is a standing incentive to put the payload where it will certainly be seen. A length limit does not touch that incentive. Content that genuinely must be read every session belongs in the operating contract, not smuggled into a routing line.

Shape is also the cheaper thing to check. An index entry containing a number, a currency amount, a commit SHA, or a status word is almost certainly a summary — a much closer proxy for the rule than character count. Flag it and move the content to the leaf.

## Derived values

A value that is copied from somewhere else diverges from it. In one observed session, four of six documents that needed correcting had gone stale within a turn or two of being written, by the author who had just written them — a roadmap phase row, an index one-liner, a preamble byte count, and a status header. None was a judgement; every one was a hand-transcribed derived value. Judgements keep. Restatements rot.

**Never write a computable number into prose — name the command that computes it.** An index preamble once recorded `19,951 bytes — 49 short of the gate`; a later compaction took the file to roughly 16 KB, and an agent then read the stale figure as a live hard blocker, planning around a constraint that had not existed for hours. The number was computable on demand the whole time. Write the command (`make check-memory-budget`) where the figure would have gone. The same applies to error counts, test counts, entry totals, and file sizes.

**Status lives in exactly one place** — the owning project memo's `Status:` header. Roadmap rows, spec headers, and index lines link to it instead of restating it; status is not index content. Status changes on nearly every commit, so each additional copy is a scheduled divergence.

Centralising status raises the stakes rather than removing them: once everything points at one source, that source going stale makes everything downstream wrong at once. Treat the owning header as a field with an owner — updated by the same change that changes the status, and re-read before it is quoted.

**When a document states a fact about code, name the test that fails if it changes.** A named test turns a divergence into a failing build; an unanchored assertion is only as fresh as the last person who happened to reread it.

## Original content and restatement

A layer holding **original content** is stable. A layer holding a **restatement** needs mechanical enforcement. That distinction predicts which layers rot better than "keep indexes short" does, and it is how to decide where checks are worth building.

The learnings layer is the stable case: a learning leaf and the incident memo that produced it are genuinely different artifacts — a reusable lesson versus what happened — so they diverge *correctly* rather than duplicating, and neither needs a checker. Index lines, roadmap rows, and spec headers are the unstable case: each restates something owned elsewhere, so each needs either a check or a link that removes the copy.

The layers earn their keep, but their maintenance cost is arithmetic and should be priced rather than assumed away. In one observed session the same handful of facts reached **eight** prose surfaces — roadmap rows, index lines, memo bodies, learning leaves, learning index lines, plan correction blocks, spec headers, and commit messages — which is eight chances to diverge per change. **When a bundle adds a layer, state what makes that layer fail loudly when it diverges.** A layer with no such mechanism will rot quietly.

## Links and identity

Use Obsidian wikilinks for all relationships inside the PCS bundle, including concept-to-concept, index-to-concept, and supersession links. Prefer stable `name` values as link identities. Repository resources outside the bundle may be identified by `resource` or written as literal paths.

## Citations

Externally sourced claims should end with a `## Citations` section. Cite the corresponding concept in `references/` with an Obsidian wikilink. Keep the canonical URI in that reference concept's `resource` field.

## Lifecycle

1. Create or update a project memo when work begins.
2. Record decisions and verified outcomes during work.
3. Add feedback when a durable behavioral instruction emerges.
4. Extract reusable technical discoveries into learning notes and catalog them.
5. Promote authoritative product behavior to canonical repository docs.
6. Archive completed or stale project state while retaining links.
7. Supersede contradicted knowledge with dated evidence rather than rewriting history invisibly.

## Conformance

A PCS bundle is structurally conformant when:

1. `.claude/memory/index.md` contains a non-empty `pcs_version`.
2. Every Markdown file except `index.md` and `log.md` begins with parseable YAML frontmatter containing a non-empty `type`.
3. Reserved `index.md` and `log.md` files follow the structures above.
4. Internal relationships use resolvable Obsidian wikilinks.
5. Consumers preserve unknown frontmatter fields and tolerate unknown `type` values.
6. Every document is UTF-8.

## Content quality rules

Keep summaries short, evidence concrete, names stable, timestamps explicit, and canonical docs authoritative. Do not duplicate secrets, transient logs, large generated output, or source-code explanations that Graphify can retrieve. Do not duplicate values another layer owns — link to status, and name the command that derives a count or a size.
