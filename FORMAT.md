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
aliases:
  - stable-kebab-case-identity
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

`type` is required for routing. `name` is a stable identity, and `aliases` is what makes that identity **resolvable as a link** — the two are mirrored above for the reason given in [Links and identity](#links-and-identity). `title`, `description`, `resource`, `tags`, and `timestamp` support display, retrieval, provenance, categorization, and freshness. Fields other than `type` are optional. Consumers must preserve unknown fields and tolerate unknown `type` values.

A small bundle can skip `aliases` entirely and link by filename, which always resolves. Mirror it once you want `[[readable-slug]]` to reach `learnings_some_long_descriptive_filename.md` — which is most bundles, sooner than expected, and cheaper to do at creation than to retrofit across a corpus.

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

### Optional types for larger bundles

Two further types and one section earn their place once a bundle has more than one author or more than a few months of history. Adding them to a small bundle is cost with no benefit — see [Tiers at a glance](ADOPTION.md#tiers-at-a-glance).

#### `decisions/`

A register of rulings with `type: decision`, plus an index gated against the register in both directions. Lifecycle step 2 below says to record decisions but gives them no home, and a memo is the wrong one at scale. A decisions index is the single index where a silently missing row is **actively misleading** rather than merely inconvenient: it answers *"what has been decided?"* with a confident subset and gives the reader no way to tell. Every other index failure degrades to "I did not find it."

If you gate it, report **both arms before returning** — a ruling with no row, and a row with no ruling. A drifted title trips both at once, so reporting only the first hides half the diagnosis.

#### `research/`

Investigations nobody has ruled on, with `type: research`. Specs and plans are behaviour and scope truth; an unratified investigation is neither, and filing it beside them lends it an authority nobody granted. The failure has a name — **a recommendation is not a ruling** — and on one bundle it was caught four times before the location was separated out. Such a document should state its own status in its header: cite it for reasoning, never as the citation for a decided fact. A worse variant belongs in the same breath: one such document was produced, returned in conversation, and never written to a file at all, while a later ruling cited its conclusions with no path. That is worse than a dangling pointer, because there is nothing to check.

#### `## Verification owed`

A section rather than a type, for **authors that cannot execute**. Planning roles with no shell, analysts, external reviewers, anyone working from a read-only checkout produces documents that are unverified by construction: they read, they cannot run. Grade load-bearing claims as read-only and close the document with a section naming the command and the person or role that should run it.

The refinement took an incident: **the named owner must be able to run the named command.** To a register, impossibility and neglect look identical, so an item whose command needs a runtime nobody has waits forever looking like a to-do. A form gate checks that an owed item names a command, not that its owner can run one.

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

### The always-read file above the indexes

Those budgets cover indexes. The operating contract is read **every turn and on every subagent hop** — the highest read-multiplier artifact in the repository — and was the one layer here with no size rule at all. On one bundle, 1,152 bytes entered it during a single session and nothing noticed: not the stop hook, not the linter, not the author until asked directly.

Give it a **ratchet rather than a budget** (see [Designing a check that survives](TOOLING.md#designing-a-check-that-survives)). A budget here would be a number somebody invented; a ratchet is today's measured size, failing on change in either direction. The gate cannot tell a good addition from a bad one and should not try — raising the baseline in the same commit is the *expected* move for a rule an incident just earned. The point is only that a byte change becomes something someone stated.

**Do not compact it to hit the number.** The obvious fix — move each long block's rationale into the leaf it already links to — was scoped on a real bundle and abandoned when its founding premise was measured: the contract's overlap with every learnings, feedback and docs file across a 2.2M-character corpus was **4% verbatim**. It paraphrases; it does not copy, and for at least one detail it was the only copy. The structural reason outlives that one plan: **moving text out of an always-loaded file converts guaranteed-read content into conditionally-read content.** That is a real safety cost paid for a real context saving, worth paying only where the moved text is rationale — never where a rule stops working once its reason is one click away. Splitting an oversized domain index is the same operation one layer down and is straightforwardly good there. Treating the two as one problem is the mistake.

## Domain sub-indexes

When a catalog index outgrows a few kilobytes, split it into a **hub** and per-domain files: the hub (`learnings/index.md`) holds a table of domains — each row a wikilink, an entry count, and an "open when touching" scope — and each domain file (`learnings/index_<domain>.md`) holds that domain's one-line entries. Agents grep the domain files for triggers and open only the leaf they need.

Do not hand-maintain counts in the hub — not the grand total, and not the per-domain figures either. This format carved out the per-domain counts as acceptable on the grounds that *the same edit that files the entry updates the row*, which is the premise every hand-stored derived value rests on. Measured on a real bundle, it failed the same way the grand total does: **9 of 14 rows had drifted, and the total was 41 short**. It fails more slowly, which is worse, because it stays plausible for longer. Derive a count (`ls learnings/*.md | wc -l`) and name the command where the number would have gone.

Deleting the counts removes the only thing anyone actually eyeballs in a hub, so replace them with an invariant rather than with nothing: **every leaf appears in exactly one domain index.** An unindexed leaf is not a wrong number — it is a lesson unreachable by the documented retrieval path, which will be rediscovered instead of reused, the precise failure the learnings layer exists to prevent. Double-indexing is the same problem deferred: two homes means one of them goes stale. `pcs_lint.py` checks both.

The generalisation is the transferable half: **when removing a derived value from a surface, ask what the reader was using it for, and replace it with an invariant.**

## Restructuring an index

Before any whole-file index rewrite or split, preserve the outgoing file verbatim in `archive/` (`archive_<name>_longform_<date>.md`) in the same change. Move, don't delete: content arrives somewhere before it leaves the index. After migrating, verify every entry appears exactly once across the successor files and every leaf still resolves — the check is mechanical and cheap, and skipping it is how entries vanish without anyone deciding they should.

Mechanical and cheap describes the check; it does not describe when the bookkeeping is owed, and that is where it costs something. Legitimate supersession and accidental loss are **indistinguishable to the check** — which is the whole reason an explicit corrections list exists. So **a bookkeeping row that a check will later demand is owed in the same commit as the edit that creates the demand.** Deferring it destroys the only evidence of which of the two happened, and that evidence decays: the person who removed the entry knew why, and three commits later nobody does. It also fires on the wrong author — on one bundle three edits each skipped the row they owed, the gate stayed green through all three and went red later on an unrelated commit, handing whoever was holding the tree three judgement calls about work they had not done. The tell to watch for in yourself is *"I'll add the row when the gate complains"*: it complains to someone else, about a decision only you can still make correctly.

## Index entry shape

A size budget limits how large a duplicate may be, not whether it exists. Under pressure a character limit teaches *"write a shorter duplicate"* rather than *"write a pointer"*: an over-budget entry gets compressed into a terser restatement that still has to be re-edited on every change and still goes stale. Constrain shape, not only length.

An index entry carries a **title, a hook, and at most the one fact that decides priority** — never findings, never numbers, never status. If you are tempted to add a number, the hook is too weak.

That is the prohibition. The constructive version, cheap enough to apply while writing the line, is:

> **An index entry must be unfalsifiable by progress.** If finishing the work would make the line wrong, the line is carrying status and belongs in the owning document.

*"F6 still blocks"* fails the test. *"A string check cannot catch a true-but-misbound claim"* passes it, because it is a fact about the problem rather than about the schedule. The absence of a writing-time test is measurable: one author violated the status rule four times in a single session, each time within hours of correcting the previous one, because every fix rewrote the status to be *currently true* — which guarantees another fix later. The entry stopped going stale only when it was rewritten to carry no status at all. This is the same move as **name the command, not the number**: both replace a value that expires with one that cannot.

The pressure to overfill an index is structural and worth naming: the always-loaded index is the only layer *guaranteed* to be read, so there is a standing incentive to put the payload where it will certainly be seen. A length limit does not touch that incentive. Content that genuinely must be read every session belongs in the operating contract, not smuggled into a routing line.

Shape is also the cheaper thing to check, but the signal is **ownership, not character class**. A number, a currency amount, a commit SHA, or a status word is a strong flag; the question to ask about each is *does another layer own this value?* A count of open defects is owned by the spec and changes every time one is fixed — flag it. A fixed historical observation, the kind that makes an entry findable at all ("a card said £300 about a pot holding £700"), is owned by nothing and will read the same in a year — leave it. That is rule five applied to the check itself: a restatement rots, original content does not, and only the first needs enforcing.

The distinction is load-bearing rather than pedantic. Measured against a real bundle, the character-class version of this rule fires on well over half the entries of a *healthy* index, and a check that is red on a healthy tree gets bypassed.

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

Use Obsidian wikilinks for all relationships inside the PCS bundle, including concept-to-concept, index-to-concept, and supersession links. Repository resources outside the bundle may be identified by `resource` or written as literal paths.

**The link identity is the filename.** Obsidian resolves `[[X]]` against a note's filename or an entry in its `aliases:` frontmatter, and never reads `name:`. A `name:` value is a link identity only when that same string also appears in that note's `aliases:`. This format recommended `name:` as a link identity until 2026-08-17; a bundle that followed the advice had **404 of 414 wikilinks resolving to nothing for the life of the vault** — every note an orphan, every backlink panel empty.

**Write the link bare, never wrapped in backticks.** A wikilink inside a code span renders as literal text: no link, no backlink, no graph edge. Every wikilink in this repository's own templates was written that way until 2026-08-17, so a bundle could follow the templates exactly and still produce a graph with no edges at all.

The two failures share a shape worth carrying well beyond links. **A convention can be load-bearing for one consumer and inert for another, and the working consumer masks the broken one.** Those links were never useless — they work as grep slugs, and grep is the documented retrieval route, so they were being used successfully every day. What was dead was the other consumer. When a convention serves two consumers, check it in the one that fails silently.

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
4. Internal relationships use Obsidian wikilinks that resolve — by filename or by an `aliases:` entry — and are written outside code spans. Resolution is a property of a renderer, not of the text, so this rule is checkable but not reviewable; `pcs_lint.py` implements it.
5. Consumers preserve unknown frontmatter fields and tolerate unknown `type` values.
6. Every document is UTF-8.

## Content quality rules

Keep summaries short, evidence concrete, names stable, timestamps explicit, and canonical docs authoritative. Do not duplicate secrets, transient logs, large generated output, or source-code explanations that Graphify can retrieve. Do not duplicate values another layer owns — link to status, and name the command that derives a count or a size.
