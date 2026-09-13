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

Gate the **key column** too, and expect it to need its own check. A bijection gate compares titles by containment, which it must, since an index truncates and a `WITHDRAWN` prefix has to keep passing — and containment cannot see a row filed under the wrong key, on a file whose entire purpose is lookup by key. The general form is worth more than the special case: **where a check's stated limit describes a property the artifact's purpose depends on, that limit is a defect to schedule, not a caveat to ship.**

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

### What the budgets are sized against

Every budget above is sized by an **assumption** about how often a layer is read. The assumption is measurable, and cheaply: a harness that keeps session records already holds the answer, so a reader over those records reports how often each document was actually opened and by what. No hook, no instrumentation, no change to how anyone works.

Three properties decide whether such a measurement is worth anything, each learned by getting it wrong:

- **Count the subagent sessions.** An instrument that reads only the orchestrator's records is not a small underestimate — it misses the majority. On one corpus subagents out-read the orchestrator 9,216 to 6,737, and the first version of the instrument globbed one directory level, missed roughly 80% of the corpus, and reported 111 documents as never read that subagents were opening routinely.
- **Report an auto-loaded file as *not measurable*, never as unread.** Nothing can observe a read of a file the harness injects, so the always-loaded index and the operating contract report zero by construction. A report that does not say so invites exactly the wrong conclusion about the two most important files in the bundle.
- **Measure before building the instrument.** The obvious implementation on one harness was a hook logging `Read` calls. In the session that proposed it, 391 of ~418 tool calls were `Bash` and `Read` was used zero times: the hook would have logged nothing and looked healthy doing it.

The first such measurement, against 957 tracked documents, found **446 that had never been read**, with the top 10 taking 44% of all reads. Treat that as a statement about retrieval paths rather than a deletion list — it describes one machine's records over one window, and a document nothing has needed yet is not a document nothing will need.

The payoff is a rule that replaces a guess. **A layer's budget policy is a default, and a measurement overrides it for one document.** Where a document is read at a rate its layer does not predict, budget that document and say why at the site: one bundle's system document is nominally read *only when you are acting on it* and ranks 14th of 579 by recorded reads, which is the entire reason it carries a ratchet. Applied loosely this reintroduces budgets across every layer, which this format deliberately does not want — so it is a permission a measurement buys, not a rule.

The structural finding underneath is worth carrying even if you never build the instrument: **a bundle can be over-enforced and under-read at the same time, and only the second costs something on every use.**

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

**A table that enumerates what your automation does is a derived value too.** The list of checks in a system document, a README's table of gates, a test plan's inventory — each is a hand-stored derivation of a build file, and each drifts exactly as a count does. One bundle's operating contract said "fourteen gates" while the real figure had passed 23, with the same stale number copied into a second document, both authoritative-looking. Name the command that prints the list, or check the table against the thing it describes. This repository's own [automation list](TOOLING.md#optional-automation) is hand-maintained and carries the same exposure.

**When a document states a fact about code, name the test that fails if it changes.** A named test turns a divergence into a failing build; an unanchored assertion is only as fresh as the last person who happened to reread it.

## Original content and restatement

A layer holding **original content** is stable. A layer holding a **restatement** needs mechanical enforcement. That distinction predicts which layers rot better than "keep indexes short" does, and it is how to decide where checks are worth building.

The learnings layer is the stable case: a learning leaf and the incident memo that produced it are genuinely different artifacts — a reusable lesson versus what happened — so they diverge *correctly* rather than duplicating, and neither needs a checker. Index lines, roadmap rows, and spec headers are the unstable case: each restates something owned elsewhere, so each needs either a check or a link that removes the copy.

The layers earn their keep, but their maintenance cost is arithmetic and should be priced rather than assumed away. In one observed session the same handful of facts reached **eight** prose surfaces — roadmap rows, index lines, memo bodies, learning leaves, learning index lines, plan correction blocks, spec headers, and commit messages — which is eight chances to diverge per change. **When a bundle adds a layer, state what makes that layer fail loudly when it diverges.** A layer with no such mechanism will rot quietly.

**The restated thing may be an interface rather than a document.** A route list, a test inventory, a checklist tally, a table of supported flags — each restates something a machine can enumerate, and the same three options apply: link to it, derive it from it, or check it against it. The commit rate is the tell. One API document took 61 commits in 30 days, and a restatement moving at that rate is not maintained by discipline.

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

### Status vocabulary

Status lives in exactly one place — the owning memo's `**Status:**` header — and a small closed vocabulary keeps that place readable: **`active`**, **`blocked`**, **`shipped`**, **`superseded`**, **`withdrawn`**.

Two of them are worth arguing for, because a bundle missing them produces two different lies. **`shipped`** means *the work this document specified is done; it is a record now, not an instruction.* Without it, a finished spec gets marked superseded — false, nothing replaced it — or left active, also false, because it still reads as an instruction. On one bundle finished work was five to ten times more common than partial supersession. And **`archived` is not a status**, however natural it looks: it names a *location*, which the filing flow already owns, and a field carrying both state and location is a field with two meanings.

**`superseded` makes a promise about another file, so it must name it** — `superseded_by:` in frontmatter, pointing at the replacement. Supersession that names no successor is deletion with extra steps.

What a check can do with this, and what it cannot, belongs at the site; it is exactly the class of limit [Designing a check that survives](TOOLING.md#designing-a-check-that-survives) says to write down. It can verify that a successor exists, that the pointer reaches **exactly one** note, and that the chain is **acyclic** — chains do close into loops, and each document in a loop looks individually correct while none of them is current. It cannot tell you that a status is **true**: `active` on an abandoned document passes every gate here.

## Conformance

A PCS bundle is structurally conformant when:

1. `.claude/memory/index.md` contains a non-empty `pcs_version`.
2. Every Markdown file except `index.md` and `log.md` begins with parseable YAML frontmatter containing a non-empty `type`.
3. Reserved `index.md` and `log.md` files follow the structures above.
4. Internal relationships use Obsidian wikilinks that resolve — by filename or by an `aliases:` entry — to **exactly one** note, and are written outside code spans. Resolution is a property of a renderer, not of the text, so this rule is checkable but not reviewable; `pcs_lint.py` implements it.
5. Consumers preserve unknown frontmatter fields and tolerate unknown `type` values.
6. Every document is UTF-8.

Rule 2 carries a trap worth naming, because it defeats rule 4 from underneath: *parseable* is a property of a **specific parser**. A duplicate key is a hard error to Obsidian and a silent last-value-wins to PyYAML, and the permissive one is the parser bundles lint with. A note whose frontmatter fails to parse in the consumer loses its `aliases:` — and with them its link identity — while looking perfectly correct in the file and in review. Parse the way the consumer parses.

## Content quality rules

Keep summaries short, evidence concrete, names stable, timestamps explicit, and canonical docs authoritative. Do not duplicate secrets, transient logs, large generated output, or source-code explanations that Graphify can retrieve. Do not duplicate values another layer owns — link to status, and name the command that derives a count or a size.

### Emphasis markers

If a bundle uses glyphs for emphasis — a prohibition, a hazard, a closed item — the set should be **closed, disjoint, and defined in one place**, and doubling one is a defect rather than more emphasis. The finding that produced this rule was not inconsistency. On one bundle nothing had ever defined what the glyphs meant, across an operating contract, a system document, an index and a register that all used them, so there was no convention to be inconsistent with: that absence was the defect.

Do not inherit anyone's glyph vocabulary, including that bundle's. Inherit the test that makes a marker mean something, applied before typing it: for a hazard, *can you name the incident or the measurement?* — a hazard nobody has hit is a guess, and a guess is prose. For a prohibition, *is there something here a reader could disobey?* In a corpus read under time pressure by something that pattern-matches, emphasis inflation is a real cost, and it is invisible in review.
