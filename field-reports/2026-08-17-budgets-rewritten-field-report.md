# Field report — `budgets_rewritten`, 2026-08-07 → 2026-08-17

**Source:** the bundle that PCS was extracted from, run for ten days after the last upstream change.
**Status:** ruled on — see the disposition below. The body is preserved as received; nothing in it was
rewritten to match what was adopted. Each item says what was measured, what was built, and whether it
generalises.

## Disposition, recorded on merge

This document is the recommendation. The table is the ruling — the distinction §8.1 argues for,
applied to the report that argues for it. Everything below the table is the report as filed.

| § | Disposition | Where it landed |
| --- | --- | --- |
| 1.1 `name:` is not a link identity | Adopted, extended | [Links and identity](../FORMAT.md#links-and-identity) and [Conformance](../FORMAT.md#conformance) rule 4, which is now stated as checkable. The proposed *`name:` must appear in its own `aliases:`* check was **not** built: §1.1's own second-order finding shows it is vacuous for a note carrying no `name:`. `pcs_lint.py` resolves links directly, which subsumes the whole class, and names the `name:` repair in the finding when a dead target matches one. Templates now mirror `name` into `aliases`. |
| — | **Found while checking 1.1** | Every wikilink in every PCS template was wrapped in backticks, where Obsidian renders no link at all. Fixing `name:` alone would have left the graph empty. Templates fixed; `pcs_lint.py` checks it. This is the same masking effect §1.1 names, one layer further up. |
| 1.2 Per-domain counts drift | Adopted | [Domain sub-indexes](../FORMAT.md#domain-sub-indexes). Carve-out dropped, coverage invariant in its place, and checked — though as "at least one index" generally, with exactly-one applied only among sibling domain indexes, since a memo routed from both a parent and a domain index is a healthy shape. |
| 2 Some properties are not review-checkable | Adopted | [Reference implementation](../TOOLING.md#reference-implementation); the "enforced by review" sentence is gone, and [Enforcement](../METHODOLOGY.md#enforcement) now states that review must not be assigned it. |
| 3 The ratchet | Adopted | [Two ways to bind forward](../TOOLING.md#two-ways-to-bind-forward), with the both-directions rule and the goal-dependent exception. A `--ratchet` mode is not built as merged. |
| 4 The operating contract has no budget | Adopted | [The always-read file above the indexes](../FORMAT.md#the-always-read-file-above-the-indexes), including the do-not-compact warning and the guaranteed-read/conditionally-read distinction. |
| 5 Deferred bookkeeping | Adopted | [Restructuring an index](../FORMAT.md#restructuring-an-index). |
| 6 Reachability of the check itself | Adopted | [Vendoring the linter](../ADOPTION.md#vendoring-the-linter), and the third property in [Designing a check that survives](../TOOLING.md#designing-a-check-that-survives). |
| 7 `--selftest` is a floor | Adapted | "Prove the red path, in both directions" is now a fifth property, and "state the limit" is strengthened with the wrong-key example. A per-check adversarial suite is **not** required of a vendored script — the weight is wrong for the audience. `--selftest` mutation-proves its own corpus checks instead, and caught a coverage bug while being written. |
| 8.1 Unratified research | Adopted, tier 3 | [Optional types for larger bundles](../FORMAT.md#optional-types-for-larger-bundles), including the never-written-to-a-file variant. |
| 8.2 Decisions register | Adopted, tier 3 | Same section, including the both-arms reporting rule. |
| 8.3 `## Verification owed` | Adopted, tier 3 | Same section, including the owner-must-be-able-to-run refinement. |
| 8.4 Unfalsifiable by progress | Adopted | [Index entry shape](../FORMAT.md#index-entry-shape), stated together with *name the command, not the number* as one principle, as §8.4 asks. |
| 9 The declined prose-number checker | Adopted as a decision | [Considered and declined](../TOOLING.md#considered-and-declined) is now a third state in the automation list, carrying the reasoning and the words-not-digits detail. |

**Tier 3** above means the concept is documented but not recommended for every bundle. The report's
items divided cleanly by scale, which prompted [Tiers at a glance](../ADOPTION.md#tiers-at-a-glance):
registers, research and ratchets earn their place once absence starts to mislead, and cost more than
they return before that.

**Changed on merge.** This report was filed under `feedback/`, which collides with the format's own
`feedback/` concept type for durable behavioural rules; it lives in `field-reports/` instead. Its link
to `ADOPTION.md#8-add-enforcement` broke when that guide was restructured into tiers, and was
repointed — caught by `check_doc_links.py`, which exists because of this report's §2 argument.

The previous round of this feedback landed as issue #1 and became the index-shape rules, the
ownership-not-character-class fix, and `pcs_lint.py`. This round covers what happened next: seven
checks now hang off that bundle's lint target, and running them turned up **two claims in `FORMAT.md`
that a real corpus falsified**, one check `TOOLING.md` deprioritised that found more than any other,
and four concepts the format currently has no home for.

Where a figure below is a live measurement rather than a historical one, the command that computes it
is named — the rule from [Derived values](../FORMAT.md#derived-values), applied to this document.

---

## 1. Two claims in `FORMAT.md` that a real bundle falsified

### 1.1 `name:` is not a link identity — and the spec recommends it as one

[Links and identity](../FORMAT.md#links-and-identity) says:

> Prefer stable `name` values as link identities.

Obsidian resolves `[[X]]` by a note's **filename** or by an entry in its **`aliases:`** frontmatter.
It never reads `name:`. A bundle that follows the sentence above literally gets links that resolve
nowhere.

That is what happened. The corpus wrote `[[a-guard-matches-one-spelling-of-what-it-forbids]]` against
a file named `learnings_a_guard_matches_one_spelling_of_what_it_forbids.md`, carrying the slug in
`name:`, and **404 of 414 wikilinks resolved to nothing for the entire life of the vault** — every
note an orphan, every backlink panel empty, the graph a field of disconnected dots.

**Why nobody noticed for months is the part worth carrying upstream.** The links were never useless:
they work as grep slugs, and grep was the documented retrieval route, so they were being used
successfully every day. What was dead was the *other* consumer — Obsidian's graph, backlinks and
orphan count. **A convention can be load-bearing for one consumer and inert for another, and the
working consumer masks the broken one.** "We use wikilinks" was true and bought nothing where it was
supposed to buy most.

Note also that [Conformance](../FORMAT.md#conformance) rule 4 requires "resolvable Obsidian
wikilinks". A bundle can follow the spec's own linking advice and fail the spec's own conformance
rule, with no signal in either direction.

**Suggested change.** In *Links and identity*: the link identity is the **filename**; a `name:` is a
link identity only if it also appears in that note's `aliases:`. In *Conformance*: say that rule 4
means resolution by filename or alias, so it is checkable rather than aspirational.

**Second-order finding, if you implement the check.** The obvious rule — *`name:` must appear in its
own `aliases:`* — is **vacuous for a note that has no `name:` at all**: it reads the field and skips
when absent. Three leaves shipped unreachable with that check green. It needs a companion rule that a
linkable leaf must declare a `name:` in the first place.

### 1.2 Per-domain counts in hub rows do drift

[Domain sub-indexes](../FORMAT.md#domain-sub-indexes) says:

> Do not hand-maintain a grand total in the hub; it drifts within days. […] Per-domain counts in the
> hub rows are acceptable: each is updated by the same edit that files the entry.

Measured on this corpus: the per-domain counts **had drifted on 9 of 14 rows, and the total was 41
short**. The carve-out rests on exactly the premise every hand-stored derived value rests on — *the
same edit will update it* — and it failed the same way the grand total does, just more slowly, which
is worse because it stays plausible for longer.

**What replaced them is the more useful half of this item.** Deleting the counts would have removed
the only thing anyone ever eyeballed in the hub. So the decoration was swapped for an invariant with
teeth: **every leaf must appear in exactly one domain index**. An unindexed leaf is not a wrong
number, it is a lesson that is unreachable by the documented grep route and will be rediscovered
instead of reused — the precise failure the learnings layer exists to prevent. Double-indexing fails
too, because two homes means one of them goes stale.

**Suggested change.** Drop the per-domain carve-out; recommend index-coverage as the thing to check
instead. The generalisation: when removing a derived value from a surface, ask what the reader was
using it for, and replace it with an invariant rather than with nothing.

---

## 2. The check `TOOLING.md` lists as unimplemented is the one that found the most

[TOOLING.md](../TOOLING.md#reference-implementation) says of `pcs_lint.py`:

> It does not implement the structural checks in the list above — frontmatter validity,
> `pcs_version`, duplicate names, wikilink resolution, index coverage, and citation coverage are all
> still enforced by review alone.

Review had been enforcing wikilink resolution on this corpus for its entire life, at a **97.6%
failure rate**. Index coverage was likewise review-enforced, and leaves were sitting in no index.

**The generalisation, which is not "write more checks":** review cannot enforce a property that is
invisible in the artifact under review. A dead wikilink and a live one are **the same characters in
the Markdown diff**. The property only exists in a renderer that no reviewer opens during review, so
listing it under "enforced by review" describes a procedure that cannot execute. That is a different
category from a check that is merely unbuilt, and it is worth distinguishing in the list: some of
those six are genuinely review-checkable (citation coverage), and some are structurally not
(wikilink resolution, index coverage).

**Suggested change.** Promote wikilink resolution and index coverage from the "review alone" sentence
to the implemented set, or mark them as *not review-checkable* so nobody counts them as covered.

---

## 3. The ratchet — a second mechanism for "bind new conventions going forward"

[Designing a check that survives](../TOOLING.md#designing-a-check-that-survives) is right, and its
second property — bind going forward, don't redden the back catalogue — is implemented there as
**date-scoping**. Date-scoping works when the unit of enforcement has a date. **A file's size does
not**, and neither does a dangling-link count or an error backlog.

The mechanism that covers those is a **ratchet**: a baseline committed at today's measured value,
failing on change. It lands green on day one, and it still closes the drift, because every future
byte has to be typed into the baseline by a human who then has to say why in the commit body.

Three things learned building four of them:

- **It buys no compaction — it converts drift into a decision.** That is the whole claim.
  Overselling it is how the next person concludes it did not work.
- **It must fail in *both* directions.** If it only fails on growth, a file that shrinks leaves
  headroom the next author fills for free, and the number drifts back up inside the slack without
  ever going red. Failing on a decrease too — naming the new number to paste — is what keeps it
  tight.
- **The exception is about the file's goal, not the mechanism.** Where the corpus is being
  deliberately burned down, a two-directional ratchet reddens every legitimate eviction, so those
  ratchets fail on *increase only* and lowering the baseline is always correct and never required.
  Where the goal is stability — the operating contract — unclaimed slack must be banked immediately.
  **Same shape, opposite direction, driven by what the file is supposed to do.** Both are in this
  bundle, and the standing risk is that someone "fixes" one to match the other; the code says so at
  both sites.

**Suggested change.** `TOOLING.md` gains the ratchet alongside date-scoping as the two ways to bind
forward, with the both-directions rule and the goal-dependent exception. `pcs_lint.py` could grow a
`--ratchet` mode next to `--write-baseline`: the difference is that a baseline records findings to
forgive, whereas a ratchet records a *measurement to defend*.

---

## 4. The operating contract has no budget, and compacting it is the wrong fix

The operating contract is layer 1 in [README](../README.md#knowledge-layers), and
[Index size budgets](../FORMAT.md#index-size-budgets) covers indexes only. So the file that is read
**every turn and on every subagent hop** — the highest read-multiplier artifact in the bundle — was
the only one in this memory system with no size check at all. **1,152 bytes went into it during a
single session and nothing noticed:** not the stop hook, not lint, not the author until asked
directly.

**The obvious fix is the wrong one, and it was measured before being abandoned.** A plan to shrink
the contract by moving each long block's *rationale* into the leaf it already links to was written
and verified three times. Its founding premise — that the contract carries summarised copies of what
its leaves already hold — measured **4% verbatim overlap against a 2.2M-character corpus** of every
learnings, feedback and docs file. The contract paraphrases; it does not copy. Worse, for at least
one concrete detail the contract was the **only** copy, so a blanket "replace narrative with a
pointer" would have silently deleted it.

**The structural reason outlives that plan and belongs in the spec:** moving text out of an
always-loaded file converts **guaranteed-read** content into **conditionally-read** content. That is
a real safety cost, paid for a real context saving, and it is only worth paying where the moved text
is rationale — never where a rule stops working once its reason is one click away. Splitting an
oversized domain index is the same operation one layer down and is straightforwardly good there.
**Treating L0 and L2 compaction as one problem is the mistake.**

**Suggested change.** `FORMAT.md` gains an operating-contract row in the budgets section: a
**ratchet, not a budget** (a budget here would be a number someone invented), plus an explicit
warning not to compact it to hit the number. State that the gate cannot tell a good addition from a
bad one and does not try — raising the baseline in the same commit is the *expected* move for an
incident-derived rule; the point is only that a byte change becomes something someone stated.

---

## 5. "Move, don't delete" is checkable — and the check has an operational cost the spec should name

[Restructuring an index](../FORMAT.md#restructuring-an-index) already says to verify every entry
appears exactly once across successor files, and calls the check "mechanical and cheap". It is. It
was built here as a conservation assert: every archived entry must reappear in a live index, in the
history burn-down, or in an explicit corrections allow-list.

**What "mechanical and cheap" does not convey is the cost that shows up later.** Legitimate
supersession and accidental loss are **indistinguishable to the check** — that is the whole reason
the allow-list row exists. So:

- **The correction row is owed in the same commit as the removal.** Deferring it destroys the only
  evidence of which of the two happened, and that evidence decays: the person who removed the entry
  knew why, and three commits later nobody does.
- **The gate fires on the wrong author.** Three edits each skipped the row they owed. The gate stayed
  green through all three and went red later, on an unrelated commit — handing whoever was holding
  the tree three judgement calls about work they did not do.
- **The tell to name in the spec is "I'll add the row when the gate complains."** The gate complains
  to *someone else*, about a decision only *you* can still make correctly.

**Suggested change.** One paragraph in *Restructuring an index*: a bookkeeping row that a check will
later demand is owed in the same commit as the edit that creates the demand — with the reason (the
evidence decays), not just the instruction.

---

## 6. Reachability of the check itself, in a shape the existing rule did not catch

"Hang it off a command people already run" is already in `TOOLING.md`, and this bundle still hit it
again in a variant worth naming: the conservation guard above was a **test file**, living in a test
directory that the lint target's own scope deliberately excludes. It was red for days and nobody saw
it.

**A guard outside the gate's reach is not a weaker guard; it is an absent one.** Wiring it in cost
one narrow target, and it caught the very next in-place edit **in the same session**.

**Suggested change.** In [ADOPTION's enforcement step](../ADOPTION.md#vendoring-the-linter), after wiring: confirm
by mutation that the gate actually goes red, and confirm that the *directory the check lives in* is
inside the scope the invoked command traverses. Existing and invoked are different properties, and a
check can satisfy the first for months while failing the second.

---

## 7. `--selftest` is a floor; a gate deserves an adversarial suite

`pcs_lint.py --selftest` is the right instinct. In practice each gate here also carries a dedicated
test suite — as of 2026-08-17, seven suites over the knowledge-system checks
(`ls tests/backend/test_check_*.py`; count them with
`grep -c "def test_" tests/backend/test_check_*.py`).

**What that bought, concretely.** The decisions-index gate's first implementation matched rulings to
index rows by *substring* and compared totals by *count*. That let two errors cancel: a ghost row was
invisible whenever a ruling went missing in the same edit, and a ruling needed no row at all if some
other row's title happened to contain its prefix. Both were reproduced by an independent QA pass, not
by the author's own selftest — a selftest written by the person holding the mental model tends to
exercise the model, not attack it.

Two habits that came out of it and generalise:

- **Mutation-prove in both directions and record it in the commit**: add the defect → red naming the
  file; remove it → green. A gate whose red path has never been observed is a gate you are trusting
  on the strength of its docstring.
- **State inside the check what a green run does *not* prove.** This is already TOOLING.md's fourth
  property and it was the highest-value one. The decisions gate never compares the key column, so a
  row filed under the *wrong key* passes green — on a file whose entire purpose is lookup by key. A
  green gate quoted as proof of something it never checked is how a check becomes worse than none.

**Suggested change.** Promote "state the limit" from a bullet to a required section of any vendored
check, and add the mutation-proof-both-ways expectation to ADOPTION step 8.

---

## 8. Four concepts PCS currently has no home for

These are the additions we would most like to see considered, in rough order of how general they are.

### 8.1 Unratified research

`docs/specs/` and `docs/plans/` are behaviour and scope truth. **An investigation nobody has ruled on
is neither**, and filing it beside them lends it an authority nobody granted. The failure it produces
has a name here — *a recommendation is not a ruling* — and it was caught four times before the
location was separated out.

A worse variant is worth naming in the same breath: one such document was produced, returned in
conversation, and **never written to a file at all**, while a later ruling cited its conclusions with
**no path**. That is worse than a dangling pointer, because there is nothing to check.

**Proposal.** A `research/` location (or a `type: research`) whose defining property is stated in the
document's own header: *unratified; cite this for reasoning, never as the citation for a decided
fact*. In PCS terms it sits between a learning (durable, reusable) and a project memo (active state):
it is neither, and today it has to pretend to be one of them.

### 8.2 A decisions register as a first-class type

[Lifecycle](../FORMAT.md#lifecycle) step 2 says to record decisions, but there is no concept type for
them and no guidance on their index. This bundle keeps a register plus a generated-by-hand index over
it, gated for equality in both directions (`make check-decisions-index`).

**Why it deserves a type rather than "put it in a memo":** a decisions index is the one index where a
silently missing row is *actively misleading* rather than merely inconvenient. It answers "what has
been decided?" with a confident subset, and the reader has no way to tell. Every other index failure
degrades to "I did not find it."

**Proposal.** A `decision/` concept type, or at minimum a documented pattern in `FORMAT.md`: register
plus index, index gated against the register, and a note that the gate should report *both* arms — a
ruling with no row, and a row with no ruling — before returning, because a drifted title trips both
at once and reporting only the first hides half the diagnosis.

### 8.3 `## Verification owed` — for authors that cannot execute

Four of the planning roles in this project are granted no shell. Everything they produce is
**unverified by construction**: they read, they cannot run. The convention that emerged is that such
documents grade load-bearing claims as read-only and end with a `## Verification owed` section naming
the command and the role that should run it. Form is gated; a merge gate blocks a document that
*rules on* or *closes* another while carrying an open owed item.

**The refinement is the part that took an incident.** The named owner must be **able to run the named
command**. Five items sat owed indefinitely because they required a runtime that is not present in
any agent's container — and to a register, **impossibility and neglect look identical**, so the item
waits forever looking like a to-do. The form gate cannot catch this: it checks that an owed item
names a command, not that its owner can run it. The fix is to mark such items with an owner who can
(here, `owner: user (host-only)`).

**Why it generalises beyond agents:** any bundle with authors who cannot run the code — analysts,
external reviewers, anyone working from a read-only checkout — has the same gap between *asserted*
and *verified*, and no vocabulary for it.

### 8.4 An index entry must be unfalsifiable by progress

[Index entry shape](../FORMAT.md#index-entry-shape) says never findings, never numbers, never status.
That is the prohibition, and it is correct. What was missing is the **constructive, writing-time
test**, and its absence is measurable: one author violated the status rule four times in a single
session, each time within hours of correcting the previous one.

The reason is that each fix rewrote the status to be *currently true*, which guarantees another fix
later. The entry only stopped going stale when it was rewritten to contain **no status at all**.

> An index entry must be **unfalsifiable by progress**. If finishing the work would make the line
> wrong, the line is carrying status and belongs in the owning document.

The cheap test, applicable while writing: *"is this sentence still true after the work lands?"*
*"F6 still blocks"* fails. *"A string check cannot catch a true-but-misbound claim"* passes, because
it is a fact about the problem rather than about the schedule.

**This is the same move as "name the command, not the number"** — both replace a value that expires
with something that cannot. Stating them as one principle would be stronger than stating either
alone.

---

## 9. A counterweight: where we decided *against* more enforcement

Sending only the additions would misrepresent the ten days. One proposal was scoped, costed, and
**rejected by the project owner**: a checker for *"never write a computable number into prose"*,
generalised beyond indexes to all prose.

The reasoning is worth having upstream, because PCS's ratio of convention to enforcement is a feature
and this is the case that tests it:

- Most of the rules in this system are convention by design, and a check on every merge has real
  cost.
- **A check that fires on legitimately narrative numbers gets ignored, then disabled** — the same
  failure as a gate that is red on a healthy tree, which `TOOLING.md` already names. The same session
  had a live example of a false-blocking guard being switched off.
- The evidence for the *rule* was never in dispute (seven wrong sites in one session). **The
  objection was to the enforcement, not to the rule.**

Two details for anyone who revisits it. The narrowest version that catches the expensive ones is: a
line carrying a count/baseline keyword **and** a number **and** no backticked command, date-scoped —
roughly forty lines on the existing template. And **a digit-only rule misses half of them**: *"five
tag axes"*, *"four sibling scope axes"* and *"corrected in all three places"* were spelled out in
words, and all three were wrong.

**Suggested change.** The *Optional automation* list in `TOOLING.md` could distinguish three states
rather than two: implemented, unimplemented, and **considered and declined, with the reason**. The
third is the most useful to a new adopter and the one that currently gets lost.

---

## What is deliberately not proposed

Several checks in that bundle are load-bearing there and have no place in PCS. Listing them so the
absence is a decision rather than an oversight:

| Check | Why it is not PCS's business |
|---|---|
| Single-owner AST guard over duplicated computations | About source code, not knowledge artifacts |
| Test-typecheck error baseline | Language-toolchain specific |
| Cross-tree write guard (`PreToolUse` hook) | Harness- and worktree-specific |
| Stop-hook delivery audit arming | Already covered by METHODOLOGY's seven-point audit |

---

## Provenance

Everything above was measured in `budgets_rewritten` (private) between 2026-08-07 — the last upstream
change — and 2026-08-17. Pointers for the maintainer, who has access:

| Claim | Where it lives |
|---|---|
| Wikilink resolution, `name:`/`aliases:` | `scripts/check_wikilinks.py` docstring; `docs/CONTEXT_SYSTEM.md` §Amendment 2026-08-12 |
| Per-domain counts drifted; index coverage | `check_every_leaf_is_indexed()` in `scripts/check_memory_budget.py` |
| Ratchet contract, both directions, goal-dependent direction | `learnings_a_documented_budget_with_no_gate_drifts.md`; `docs/CONTEXT_SYSTEM.md` enforcement table |
| Operating-contract size; 4% overlap; do-not-compact | `scripts/check_claude_md_size.py` docstring; `learnings_l0_is_the_only_layer_guaranteed_to_be_read.md` |
| Conservation, deferred bookkeeping, innocent commit | `learnings_deferred_bookkeeping_reddens_an_innocent_commit.md` |
| Decisions-index cancellation bugs and stated limits | `scripts/check_decisions_index.py` docstring |
| `## Verification owed`, and the un-runnable owner | `scripts/check_verification_owed.py`; `docs/plans/2026-08-04-planner-agents-cannot-verify.md` |
| Unfalsifiable-by-progress | `docs/CONTEXT_SYSTEM.md` §Amendment 2026-08-11 |
| The declined prose-number checker | `.claude/memory/project/INDEX_backlog_platform.md` |

All seven checks were green (`make lint`, exit 0) at the time of writing, so none of the above is a
report from a broken tree.
