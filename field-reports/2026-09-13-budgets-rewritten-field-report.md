# Field report — `budgets_rewritten`, 2026-08-17 → 2026-09-13

**Source:** the same private bundle PCS was extracted from, run for a further 27 days after the
previous report merged as PR #5.
**Status:** ruled on — see [the disposition](#0-disposition--recorded-on-merge). Everything below that
table is the report as filed; nothing in it was rewritten to match what was adopted.

**What changed in that window.** Thirteen further document gates were built (2026-08-18 → 2026-09-07),
the corpus passed 950 documents, and — for the first time — something measured **which documents are
actually read**. That last one is the item this report would keep if it could keep only one, because
it changes what every budget in `FORMAT.md` is sized against.

**How to read it.** Every item carries **What / Evidence / Pro / Con / Recommendation**. The
recommendation is one bundle's opinion and the **Con** line is written to make declining cheap — the
previous round's most useful outcome was §9, an item recommended *against* adoption, and this report
keeps that shape deliberately. Four verdicts are used:

| Verdict | Meaning |
| --- | --- |
| **Adopt** | Belongs in the format or the reference implementation for every bundle |
| **Adopt as tier 3** | Real, but only earns its place once absence starts to mislead |
| **Document only** | A warning or a decision to record; no check, no new type |
| **Project-specific** | Load-bearing where it was built, not PCS's business |

Where a figure is a **live** measurement it names the command that computes it, per
[Derived values](../FORMAT.md#derived-values). Where it is historical it carries the date it was
measured and is not re-derivable. Figures marked **[measured 2026-09-13]** were run while writing
this report, in the source bundle, on macOS.

---

## 0. Disposition — recorded on merge

This document is the recommendation; the table is the ruling, in the shape the previous report's
disposition took. Everything below it is the report as filed — no figure, verdict or **Con** line was
rewritten to match what was adopted.

| § | Disposition | Where it landed |
| --- | --- | --- |
| 1.1 The vault linker is prescribed and was deleted here | Adopted, as a constraint | [Obsidian](../TOOLING.md#obsidian) keeps the script and adds the property idempotence does not cover: **the vault name is the project's identity, never a path basename**. The stronger form is stated as a choice to weigh — linking belongs to whatever provisions the environment, and a repo-side linker nothing calls is worse than none. The [Tier 3 bullet](../ADOPTION.md#tier-3--registers-research-and-ratchets) and the README tree carry the constraint. Not removed: the advice is still right for a single checkout, which is most adopters. |
| 1.2 The graph memory fence was reversed here | Adopted, as a decision with a default | [Whether to graph your own memory](../TOOLING.md#whether-to-graph-your-own-memory). Exclude stays the **default** and is now stated as a choice rather than a rule, with both silent traps at the site and the asymmetry that decides the default — a wrong fence fails privacy, not functionality. The structural / relabel / semantic distinction landed there too: what leaves the machine is the question, not whether an LLM is involved. `.claude/` memory is off the blanket exclusion list in TOOLING and ADOPTION. |
| 1.3 Headings became an egress surface | Adopted, document only | Same section, attached to 1.2 exactly as recommended: bodies stay local, every heading leaves, so heading hygiene is a privacy control rather than a style preference. No check and no new type. |
| 2.1 Measure reads, don't infer them | Adopted as a method | [What the budgets are sized against](../FORMAT.md#what-the-budgets-are-sized-against), a new subsection under the budgets it corrects, with all three properties stated as requirements on any such measurement — count the subagent sessions, report an auto-loaded file as *not measurable*, and measure before building the instrument. The 446-never-read figure is carried as a signal about retrieval paths, never as a deletion list. `report_doc_usage.py` is **not** adopted: it parses one vendor's transcript format, and `pcs_lint.py` stays stdlib-only and corpus-scoped. Pointed at from [Knowledge layers](../README.md#knowledge-layers) and [Maintaining it](../ADOPTION.md#maintaining-it). |
| 2.2 Admission control for indexes | Adopted, opt-in | [Reference implementation](../TOOLING.md#reference-implementation) states coverage and admission as the pair they are, with the second-reference reasoning and the self-certifying-evidence failure shipped alongside it. Built as `pcs_lint.py --admission` and mutation-proven both ways. Opt-in for the reason the item's own **Con** gives — it bites hardest on a young bundle — and listed at [Tier 3](../ADOPTION.md#tier-3--registers-research-and-ratchets). |
| 2.3 Diff-scoping as a third way to bind forward | Adopted | [Three ways to bind forward](../TOOLING.md#three-ways-to-bind-forward), retitled as asked, with both limits: compare the normalised union so a **move is not a touch**, and do not use it where the unit has no identity independent of the diff. The rejection case is kept, because a rule that says where it applies is what makes it safe to adopt. |
| 2.4 A gate's proof runs with the gate, from a derived list | Adopted as a principle | A sixth property in [Designing a check that survives](../TOOLING.md#designing-a-check-that-survives): run the proof on the same command as the check, and derive that list rather than maintain it. `check_gate_proofs.py` is **not** adopted — build-system-coupled, and it tripled one lint's runtime. Both scripts here now carry `--selftest` as a lint prerequisite, which is the Tier 2 weight of the same property. |
| 2.5 The automation list drifts from the automation | Adopted as tier 3, generalised | [Derived values](../FORMAT.md#derived-values): a table that enumerates what automation does is a derived value — name the command or check the table. Not built for this repository, as recommended, and the paragraph says so about TOOLING's own hand-maintained automation list. |
| 2.6 The enforcement layer measured, not budgeted | Adopted into Considered and declined | [Considered and declined](../TOOLING.md#considered-and-declined) gains the second entry the section was argued for, including the mutation-sweep distortion that stops "unbudgeted" from reading as "harmless". Its first replacement commitment — a new check names the defect it has already caught — landed in [Admitting and retiring a check](../TOOLING.md#admitting-and-retiring-a-check). |
| 2.7 A closed marker set | Adopted as tier 3, stated generically | [Emphasis markers](../FORMAT.md#emphasis-markers): closed, disjoint, defined in one place. The three glyphs are deliberately **not** prescribed. What transfers is the test applied before typing one — name the incident or the measurement, or it is prose. |
| 2.8 Ratchet by read volume, not by layer | Adopted, tied to 2.1 | Same section as 2.1, phrased as the permission it is rather than a rule: a layer's budget policy is a default, and a measurement overrides it for one document. The trap is stated with it — applied without measurement it degenerates into budgeting whatever feels important. |
| 3.1 Frontmatter must parse as the consumer parses it | Adopted, and implemented | [Reference implementation](../TOOLING.md#reference-implementation) and [Conformance](../FORMAT.md#conformance), where rule 2's *parseable* is now a property of a named parser and rule 4 requires a link to reach **exactly one** note. `pcs_lint.py` gained a duplicate-key check — scoped to top-level keys, since this format's own templates nest `type:` under `metadata:` — and an ambiguous-link check. §5's half-proposed vault-staleness rule folded in here: name the corpus you measured, not just the parser you measured with. |
| 3.2 Lifecycle vocabulary: `shipped` in, `archived` out | Adopted | [Status vocabulary](../FORMAT.md#status-vocabulary): `shipped` added, `archived` out as a location rather than a state, `superseded` required to name its successor. The project-memo template carries the vocabulary and the optional pointer. `pcs_lint.py` checks existence, uniqueness and **acyclicity**, and the limit it cannot check — whether a status is true — is stated at the site. |
| 3.3 Closing the key-column hole TOOLING already names | Adopted as tier 3 | [Optional types for larger bundles](../FORMAT.md#optional-types-for-larger-bundles), beside the register. The general clause was carried up into the fourth check-design property, where it is worth more: **a written limit is a backlog item, not an absolution.** |
| 3.4 A document enumerating an interface must be derived from it | Adopted as tier 3 | One paragraph in [Original content and restatement](../FORMAT.md#original-content-and-restatement) — the restated thing may be an interface, and the same three options apply. Not a new rule, as recommended. |
| 3.5 What a ratchet actually produced over 27 days | Adopted as an honesty note | [Three ways to bind forward](../TOOLING.md#three-ways-to-bind-forward) now carries the measured outcome, including that six lowerings banked 341 bytes against 17,544 of growth — so an adopter does not expect the downward arm to act as a brake. |
| 3.6 `check_doc_links.py` disagrees with GitHub on em-dash anchors | Adopted, fixed | `scripts/check_doc_links.py`. `--selftest` now pins the slugger against ids read from rendered github.com pages, grades the unverified cases separately, and proves the red path both ways; it runs on the lint target. The general clause landed in the fourth property of [Designing a check that survives](../TOOLING.md#designing-a-check-that-survives). |
| — | **Found while ruling on 3.6** | The same three lines also stripped every underscore as emphasis, where GitHub keeps one inside a word: `budgets_rewritten` anchored as `budgetsrewritten`. Not in the report — found by doing what §3.6 asks and pinning the cases against the ids github.com actually emits for headings in this repository. Both defects were latent, and the pair is the argument for the clause: the first was findable by reading, the second only by asking the consumer. |
| 4.2 "Hang it off a command people already run" needs a level up | Adopted | The third property in [Designing a check that survives](../TOOLING.md#designing-a-check-that-survives) now asks for something other than a person's memory to run the command, and [Making it run without you](../ADOPTION.md#making-it-run-without-you) carries the copyable form, both CI traps, and the question of whether the automatic thing can refuse a merge at all. This repository had exactly the defect described — no `.github`, no hooks — and now runs `make lint` on push and pull request. |
| 4.3 Corpus liveness as a gate-review criterion | Adopted as tier 3 | [Admitting and retiring a check](../TOOLING.md#admitting-and-retiring-a-check), paired with the admission rule from 2.6, and with the proxy limit kept: a quiet corpus nominates its check for **review**, never for removal. |
| 5 Deliberately not proposed | Document only, verdicts unchanged | Both previously-declined items stay declined. Two transferable clauses were taken into [Enforcement](../METHODOLOGY.md#enforcement): a reminder hook is only as good as the list that arms it, so that list needs a test; and a guard that fails closed must be exercised on every platform that loads it. The read-side staleness finding is recorded as not a format concern. |

**Tier 3** above means the concept is documented but not recommended for every bundle — the distinction
[Tiers at a glance](../ADOPTION.md#tiers-at-a-glance) exists to carry.

**Changed on merge.** Renaming *Two ways to bind forward* killed the four inbound links this report
makes to it. They are repointed and the prose is left as filed, since each sentence is about the
section as it stood when the report was written. `check_doc_links.py` caught every one — the second
time that gate has caught a rename it exists because of. Two things this ruling found in the guides
while applying the report: the check-design list said *four properties* above five bullets, a
hand-stored count of the list beneath it and §2.5's shape exactly, now removed rather than corrected;
and the `ADOPTION.md` tier anchor §1.1 had to route around is linkable again, so this table uses it.

---

## Summary — recommendations at a glance

| § | Item | Our recommendation |
| --- | --- | --- |
| 1.1 | `setup_vault_links.sh`: ADOPTION tier 3 and README prescribe a script this bundle **deleted for cause** — it derived the vault name from a path basename, which in a worktree is the instance | **Adopt** (change the guidance) |
| 1.2 | TOOLING tells bundles to exclude `.claude/` memory from the graph. This bundle **reversed** that, and hit two failure modes that are silent by construction | **Adopt** (soften to a decision + record the traps) |
| 1.3 | Once memory is in an LLM-labelled graph, **headings become an egress surface** | **Document only** |
| 2.1 | `report_doc_usage.py` — read-frequency measured from session transcripts already on disk | **Adopt** |
| 2.2 | `check_index_admission.py` — a document **earns** its index entry via a second, independent reference | **Adopt** |
| 2.3 | Diff-scoping ("touched") as a third binding mechanism — **and the case where it must not be used** | **Adopt** |
| 2.4 | `check_gate_proofs.py` — each gate's proof suite runs in the same command as the gate, from a **derived** list | **Adopt** |
| 2.5 | `check_enforcement_table.py` — the document that lists the automation is a hand-stored derivation | **Adopt as tier 3** |
| 2.6 | `gate_prose_ratio.py` + the ruling to leave the enforcement layer **unbudgeted but measured** | **Adopt** (into Considered and declined) |
| 2.7 | `check_marker_convention.py` — `⛔` / `⚠️` / `✅` as a closed, disjoint set | **Adopt as tier 3** |
| 2.8 | `check_context_system_size.py` — ratchet an L3 document because **read volume**, not layer, says to | **Adopt** (depends on 2.1) |
| 3.1 | Frontmatter must parse the way the **consumer** parses it — 119 notes silently lost their aliases | **Adopt** |
| 3.2 | `status: shipped` added, `archived` removed | **Adopt** |
| 3.3 | `check_decisions_numbering.py` — repairs the key-column hole TOOLING already documents | **Adopt as tier 3** |
| 3.4 | A document that enumerates an interface must be derived from that interface | **Adopt as tier 3** |
| 3.5 | 37 baseline changes, +40.5%: what a ratchet buys and what it does not | **Adopt** (honesty note) |
| 3.6 | **Defect found in this repo's own `check_doc_links.py`** — its anchor slug disagrees with GitHub's on any heading with an em dash | **Adopt** (fix + general clause) |
| 4.2 | The command the checks hang off must itself be run by something | **Adopt** |
| 4.3 | Review a gate against the **liveness of the corpus it defends** | **Adopt as tier 3** |
| 5 | Six things deliberately not proposed, including two previously declined | **Document only** |

---

## 1. Two pieces of current guidance this bundle now contradicts

These are first because they are the only items where PCS as written would lead a new adopter into a
failure this bundle has already had.

### 1.1 The vault linker is prescribed, and was deleted here for cause

**What.** [ADOPTION.md](../ADOPTION.md)'s Tier 3 section recommends *"an idempotent
`scripts/setup_vault_links.sh` linking memory, agents, and docs into an Obsidian vault and into the
agent harness. It must refuse to replace real directories or unrelated symlinks."* The
[README layout](../README.md#repository-layout) puts the same file in the canonical tree, and
[Obsidian](../TOOLING.md#obsidian) repeats the idempotence rule. This bundle **deleted that script on
2026-08-24** and does not intend to restore it.

**Evidence.** The script named the vault from `basename "$REPO"`. In a git worktree that basename is
the **instance** (`2`, `3`, `main`), not the project. Every instance therefore linked its own copy
into a vault named after itself, and one vault accumulated a full copy of `memory/` and `docs/` per
instance: **3,699 note instances for 941 distinct notes** (measured 2026-08-22). The visible symptom
was not duplication — it was that `backlinks`, `links` and `orphans` stopped being usable, because a
link resolved into an arbitrary sibling copy. The repair was a cut-over to one vault holding one copy
(2026-08-24); the linking moved to the container bootstrap, which knows the project identity, and the
repo-side script was removed so it could not be called again as a silent no-op.

**Why the current wording does not prevent it.** The script satisfied **every property PCS asks for**.
It was idempotent. It created missing parents. It refused to replace real directories. It left correct
links alone. It was still wrong, because the failure is not in what the script *does* — it is in the
**name it derives**. Idempotence guarantees that running it twice equals running it once; it says
nothing about whether the thing it converges on is the right thing.

**Pro of changing the guidance.** The failure is invisible until someone opens the graph view, and by
then the vault has months of duplicates in it. One sentence prevents it.

**Con.** PCS's advice is not wrong for a single-checkout project, which is most adopters. Over-warning
about worktrees in a guide aimed at Tier 0–1 adds cost to people who will never hit it.

**Recommendation — Adopt, as a constraint rather than a removal.** Keep the script in Tier 3, add the
constraint that decides it: **the vault name must be the project's identity, never a path basename**,
because in a worktree, a container mount or a CI checkout the basename is not the project. Consider
adding the stronger statement this bundle now holds: linking is a property of the *environment*, so it
belongs to whatever provisions the environment, and a repo-side linker that the environment has
stopped calling is worse than none — it reads as the mechanism while enforcing nothing.

### 1.2 "Exclude `.claude/` memory" from the graph — reversed here, with two silent traps

**What.** [Graphify](../TOOLING.md#graphify) says: *"Exclude secrets, databases, exports, backups,
dependency trees, build artifacts, generated data, and `.claude/` memory."* On **2026-09-05** this
bundle ruled the opposite: `.claude/memory/` is now **in** the graph, deliberately, and the rest of
`.claude/` stays out. The ruling was taken with a security gate attached, and the reasoning was that
memory is the part of the corpus whose relationships an agent most needs to traverse, and the one
where "which note does this connect to" is hardest to answer by grep.

**Evidence — two failure modes, both silent.** Implementing the reversal is where the value is, because
both ways of getting it wrong produce **no error**:

1. **Gitignore cannot re-include under an excluded ancestor.** The obvious fence — `.claude/` followed
   by `!.claude/memory/` — leaves memory **excluded**, with no diagnostic. The pattern that works is
   `.claude/*` plus `!.claude/memory/`. A bundle that "enables" memory in the graph the obvious way
   gets a green run, an unchanged graph, and a belief that it worked.
2. **Deleting the bare `.claude/` un-fences secrets.** The anchored patterns elsewhere in the file
   (`deploy/secrets/`, `deploy/pi.local.env`) do not match inside `.claude/worktrees/*/`. The bare
   directory exclusion was load-bearing for those paths, and the edit that looks like a simplification
   is the edit that widens the privacy boundary.

**Related, and stronger than a warning.** PCS names `.graphifyignore` a privacy boundary and enforces
nothing. This bundle now gates the part that actually exfiltrates: **`graphify extract`'s semantic pass
sends whole files to whichever provider a key selects**, and `check_no_semantic_extraction.py` fails the
build if it has ever run here. Structural extraction and LLM relabelling are permitted; the whole-file
pass is not. TOOLING already advises keeping extraction separate from relabelling — this is the same
rule with a check behind it, and the distinction it turns on is *what leaves the machine*, not *whether
an LLM is involved*.

**Pro.** The current sentence reads as settled advice, and the reversal is defensible enough that a
reader following PCS literally is being steered away from a legitimate design without being told it is
a choice. The two traps cost this bundle real time and are pure gift to the next adopter.

**Con.** Putting memory in a graph genuinely raises exposure — see §1.3, which is the bill for it. A
format that says "either way is fine" gives less guidance than one that picks. There is also a real
argument that the default should stay *exclude*, since the trap in point 2 means the failure mode of
getting the fence wrong is a **privacy** failure, not a functionality one.

**Recommendation — Adopt, as a decision with a default.** Keep exclude as the default, restate it as a
choice rather than a rule, and record both traps at the site. Add the semantic-pass distinction to
[Graphify](../TOOLING.md#graphify): *structural extraction is local; a semantic pass uploads file
contents; a bundle that graphs its own memory should gate the second.*

### 1.3 Once memory is in an LLM-labelled graph, headings become an egress surface

**What.** The direct consequence of 1.2, and the item most likely to be missed by someone who adopts
it. `graphify relabel` names each community by sending the model **one prompt line per community built
from verbatim markdown headings** — never body text. So the moment a bundle's memory enters the graph,
**every heading in it becomes text that leaves the machine**, while every body stays local.

**Evidence.** This bundle built `check_memory_heading_hygiene.py` for exactly this, as a condition of
the security gate that approved 1.2. It ratchets hygiene over `.claude/memory/**` — **headings only,
never bodies** — which is the same scoping decision TOOLING already records for the derived-value check
(*indexes, not leaves*), arrived at independently for a different reason.

**Pro.** It reframes a style rule as a privacy control, which is the only framing under which it gets
maintained. It is also cheap: headings are short, few, and already conventional.

**Con.** It is entirely contingent on 1.2 and on a specific tool's relabelling implementation. A bundle
that keeps memory out of the graph needs none of it, and a different graph tool may send different text.

**Recommendation — Document only**, as a sentence attached to 1.2 rather than a check: *if you graph
your memory with an LLM naming pass, find out what text that pass sends; in graphify's case it is your
headings, and that makes heading hygiene an egress control rather than a style preference.*

---

## 2. New mechanisms with no PCS equivalent

### 2.1 Measure reads; do not infer them from the layer

**What.** `report_doc_usage.py` — a **reader over Claude Code session transcripts already on disk**. No
hook, no instrumentation, no change to how anyone works. It reports, per document, how many times it
was read and by whom.

**Evidence [historical, 2026-08-23 run].** Against 957 tracked documents:

- **446 have never been read.**
- The **top 10 documents take 44% of all reads.**
- **111 documents are read only by subagents.**
- **Subagents out-read the orchestrator 9,216 to 6,737.** The first version of the instrument globbed
  one directory level, missed every subagent transcript — about 80% of the corpus — and reported those
  111 as never-read. An orchestrator-only instrument is not a small underestimate; it misses the
  majority.
- **Auto-loaded documents always report zero.** That means **not measurable**, never **unread**. No
  hook and no transcript scan can observe an auto-injected read, and a report that does not say so
  invites exactly the wrong conclusion about the two most important files in the bundle.

**One finding about building it that generalises past this instrument.** The planned implementation was
a `PostToolUse` hook logging `Read` calls. That was **measured before it was built**: in the session
that proposed it, **391 of ~418 tool calls were `Bash`, and `Read` was used zero times.** The hook
would have logged nothing and looked healthy doing it. The transcript reader was chosen because the
measurement said so.

**Pro.** Every budget in [Index size budgets](../FORMAT.md#index-size-budgets) and every layer in
[Knowledge layers](../README.md#knowledge-layers) is currently sized by **assumption** about read
frequency. This is the instrument that turns those into measurements, and it costs nothing to run
because the data already exists. It also directly answers the question a bundle owner cannot otherwise
answer: *is the corpus I am maintaining being used?*

**Con.** It is **harness-specific** — it parses one vendor's transcript format, and a bundle used with a
different agent has no equivalent input. It is also easy to over-read: "never read" is a statement about
one machine's transcripts over one window, and this bundle put a standing caution on its own `446`
figure for exactly that reason. Acting on it as a deletion list would be a mistake.

**Recommendation — Adopt**, but as a **method**, not as `report_doc_usage.py`. The format should say
that read frequency is measurable from whatever session records the harness already keeps, that the
measurement should cover **subagent sessions**, and that auto-loaded files must be reported as *not
measurable* rather than *unread*. The reference implementation can stay out of `pcs_lint.py`, which is
deliberately stdlib-only and corpus-scoped. If any figure from this report changes the format, it
should be this one, because it is the only item that tells you whether the rest is working.

### 2.2 Admission control: a document earns its index entry

**What.** `check_index_admission.py` and rule 15 of the local operating contract: **a document reaches
a loaded index only once something other than an index references it** — an inbound link or a
resolvable wikilink from a non-index document. PCS's `pcs_lint.py` checks the opposite direction (a
leaf must be in at least one index). This is the entry condition.

**Evidence and the reasoning.** The premise is that **episodic pruning cannot beat continuous
addition**: a corpus that admits everything and cleans up periodically is a corpus whose size is set by
how often someone runs a cleanup. The threshold is not arbitrary — **five independent cache-replacement
designs (LRU-K, 2Q, LIRS, TinyLFU, S3-FIFO) converged on a second-reference rule**, because one
reference cannot distinguish a working-set member from a bulk load. Thirty documents written in one
session have exactly one reference each and are invisible to promotion by construction, with no bulk
detector needed.

**The failure worth shipping with it.** A third evidence channel — *a mention in a commit message from a
commit other than the one that created the file* — was added on 2026-08-23 and **removed the same
day**. It fired on its own author within hours: commit messages that named two baselined filenames
purely to explain the ratchet were credited as third-party citations, and the finding count dropped
2 → 0 with **zero real citations added**. The lesson is narrower than "commit messages are bad
evidence" — it is that **an evidence channel the author also writes is not independent**, and
independence is the entire property being tested.

**Pro.** It is the only mechanism in this report that acts on *inflow*. Everything else in PCS — budgets,
ratchets, the filing flow — acts on a corpus that has already grown. It is also ratcheted and
two-sided, so it lands green and cannot bank slack.

**Con.** It bites hardest exactly when a bundle is young and legitimately writing many documents at
once, which is when discouraging writing is most harmful. It needs the ratchet to be usable at all, so
it is not a Tier 1 concept. And it enforces a **routing** property, not a quality one — a bad document
with two references is admitted, a good one with one is not.

**Recommendation — Adopt**, alongside the existing coverage check in
[Reference implementation](../TOOLING.md#reference-implementation), stated as the pair it is: coverage
asks *is this leaf reachable*, admission asks *has this leaf earned a place in something that is
always loaded*. Ship the self-certifying-evidence failure with it; it is the part a reimplementation
will otherwise repeat.

### 2.3 Diff-scoping — a third way to bind forward, and the case where it must not be used

**What.** [Two ways to bind forward](../TOOLING.md#three-ways-to-bind-forward) names date-scoping and the
ratchet. There is a third: **scope by the diff**. `check_touched_entries.py` enforces that an index
entry you **add or modify** comes in under the 400-character cap; pre-existing over-long entries are
exempt indefinitely. It lands green, it never reddens the back catalogue, and it reduces the corpus at
the rate the corpus is worked.

**Why the existing ratchet did not cover it.** The over-long-entry ratchets in `check_memory_budget.py`
are **count-based and increase-only**. Editing an over-long entry into a *different* over-long entry
leaves the count identical and passes. Diff-scoping closes that specific gap, and it is the only one of
the three mechanisms that produces reduction without a campaign — which mattered here because one index
grew twenty-fold in twenty-three days (4,309 bytes on 2026-07-30 to ~86,600 on 2026-08-22) while its
burn-down sat registered and unowned.

**Two limits, and the second is the actual contribution.**

1. **A move is not a touch.** The first implementation compared per file, which meant that splitting an
   85KB index into sub-indexes — *the plan's own prescribed remedy* — would have failed with up to 63
   violations. It now compares the **union of normalised entries across all index files**, so relocating
   an entry byte-identically is not an edit. Verified both ways: a real 50-bullet split of the live file
   passes; the same split plus one changed word fails.
2. **Diff-scoping was deliberately rejected for a different gate in the same bundle.** For a register
   whose rows are read whole on every run, the cap is a **per-row invariant with a shrink-only
   grandfather list**, explicitly *not* a touched-row rule, because "touched" is a git diff: identical
   content would pass or fail depending on merge base, rebase, or a dirty tree, and it races a
   concurrent writer moving `HEAD`. The discriminator is whether the unit of enforcement has a stable
   identity independent of the diff. An index *entry* does, after normalisation. A register *row* in a
   file being appended to by a concurrent process does not.

**Pro.** It fills a real gap between the two existing mechanisms, it is the only one that shrinks
anything, and the rejection case makes it safe to adopt — a rule that says where it applies is worth
more than one that only says what it does.

**Con.** It needs git, a reliable base ref, and a normalisation function that is correct about
re-wrapping; ours treats the same words folded at a different column as untouched, which is essential
and non-obvious. It also does nothing in a corpus nobody edits: *reduction happens at the rate the file
is worked, and if that rate is zero, so is this.*

**Recommendation — Adopt** into [Two ways to bind forward](../TOOLING.md#three-ways-to-bind-forward),
retitled for three, with both limits stated. The section is already the best-argued part of TOOLING and
this completes it.

### 2.4 A gate's proof runs in the same command as the gate, from a derived list

**What.** `check_gate_proofs.py` reads the build file's own lint prerequisite list, finds each target
that invokes a `scripts/<name>.py` gate, and runs `tests/backend/test_<name>.py` if it exists — so every
gate's mutation-proof suite runs whenever the gate runs.

**Evidence.** [Designing a check that survives](../TOOLING.md#designing-a-check-that-survives) already
requires proving the red path in both directions. It does not say **who re-runs that proof next
month**. Measured here on 2026-08-23: two gates shipped with 36- and 42-test proof suites that nothing
routine ran, and a third — the decisions-index gate — **was running in `lint` while its own test suite
was red and unseen.** A gate whose proof nobody runs decays into a gate nobody can trust, and it does so
invisibly, because the gate itself is still green.

**The design decision worth carrying.** The obvious implementation is to hand-list the proof files. That
is the shape this bundle keeps finding stale: a fourth gate added next month, with a test file nobody
remembers to add, reopens exactly the hole. Deriving the list from the build file makes the property
*"a check that runs in lint has its own proof run alongside it"* rather than a list — a new gate is
covered the moment its target and its test file both exist, with no third place to remember.

**Limits, stated in the script and worth copying.** It reads the build file with regular expressions,
not `make`'s parser, so a recipe that builds its path out of a variable is invisible to it. It does not
run the whole test tree — only the subset that is structurally a gate's own proof — because the full
tree takes seven minutes and a lint dependency that costs seven minutes gets routed around. And a
script referenced by a target that is no longer a lint prerequisite is not discovered at all.

**Pro.** It closes a gap the format already implies but does not staff, and the derivation trick is
reusable anywhere PCS currently recommends a hand-maintained list.

**Con.** It is **build-system-coupled** — the regex parse is specific to a Makefile — and it roughly
triples lint's runtime. [measured 2026-09-13] `make lint` takes **2m17s** wall, of which **~101s (74%)**
is the four pytest invocations this gate drives. A vendored `pcs_lint.py` already solves the same
problem differently, with `--selftest` inside the single script, which is the right weight for the
audience and needs no derivation at all.

**Recommendation — Adopt as a principle, not as a script.** Add to
[Designing a check that survives](../TOOLING.md#designing-a-check-that-survives) a sixth property:
**the proof must run on the same command as the check**, and where a bundle has several checks with
several proof files, **derive that list rather than maintain it**. Note that `--selftest` inside a
single vendored script already satisfies this for Tier 2 adopters — which is a point in the reference
implementation's favour worth stating explicitly.

### 2.5 The document that lists the automation drifts from the automation

**What.** `check_enforcement_table.py` — the bundle's system document carries a table of what its lint
target runs, and that table is a **hand-stored derivation** of the build file. The check pairs them.

**Evidence.** This is the same shape as the decisions-index bijection PCS already documents, pointed at
a different pair of files. It arrived after the local contract carried a comment saying "fourteen gates"
while the real figure had passed through 23 to 24, and **the same stale number had been copied into the
system document.** One hand-stored derivation, two divergent copies, both authoritative-looking.

**Pro.** `TOOLING.md` itself contains exactly such a list — implemented / unimplemented / declined —
maintained entirely by hand, and the same drift is available to it. The check is cheap and its failure
message is actionable by construction (it can name the missing row).

**Con.** It is self-referential in a way that reads as excessive to a newcomer, and it only pays off
where the list is long and moving. A bundle with four checks does not need a gate to notice that its
table says three. It is also the weakest-provenance item here: it names no incident of its own beyond
the stale count above.

**Recommendation — Adopt as tier 3**, generalised one level: **any table in a document that enumerates
what automation does is a derived value** and falls under
[Derived values](../FORMAT.md#derived-values) — name the command, or check the table. Do not build it
for PCS itself unless the automation list grows.

### 2.6 The enforcement layer is a corpus too — measured, deliberately not budgeted

**What.** The `scripts/check_*.py` layer in this bundle is majority prose. It was ruled on 2026-08-22 to
leave it **unbudgeted, deliberately**, and to **measure it instead**: `gate_prose_ratio.py` reports the
prose-to-code ratio and is wired into no target on purpose.

**Evidence.** [measured 2026-09-13, `python scripts/gate_prose_ratio.py`] **59% prose across the layer
— 8,121 prose lines to 5,712 code lines.** When first measured on 2026-08-22 it was 64%, and the worst
single gate had gone **102 → 975 lines across 23 commits** while its executable code stayed near 79 —
92% prose. Nothing measured any of this: the scripts were in no budget, no ratchet, and outside the
index checks' scope.

**Why the cap is the wrong instrument.** The prose *is* the mechanism. Raising a ratchet baseline costs
a written justification, and that friction is the whole reason a ratchet ratchets. A gate that capped
comment volume would make **the cheapest way to pass it deleting the reason a rule exists** — the
failure mode being defended against is precisely the one the cap would cause.

**What replaces the budget** — three commitments, and the first is the one PCS should take:

- **A new gate must name the defect it has already caught, not one it might.** [measured 2026-09-13]
  **25 of 30** gate scripts here cite a dated incident in their docstring.
- **Completed records leave the hot path.** A finished burn-down or a closed migration is archived with
  a pointer; what stays inline is the live rule and the current state.
- **Measure rather than cap**, with the ratio recomputable and reported in review.

**The harm that is real and easy to miss.** In a 2026-08-22 mutation sweep, **53 of 71 surviving mutants
landed inside gate comments**, inflating an apparent test-weakness figure from a true 19% to a reported
48%. Prose in the hot path distorts the measurement of the code it explains. So "unbudgeted" must not be
read as "harmless".

**Pro.** [Considered and declined](../TOOLING.md#considered-and-declined) exists precisely to hold
decisions like this, and it currently holds one. A second entry — *we considered budgeting the
enforcement layer and decided to measure it instead, here is why and here is the measured harm we
accepted* — is exactly the third state that section argues for.

**Con.** It is a decision about a corpus most bundles will not have: it presumes enough checks for their
prose to constitute a layer. At Tier 2, with one vendored script, there is nothing to rule on.

**Recommendation — Adopt into Considered and declined**, including the mutation-sweep distortion, which
is the part that keeps it honest.

### 2.7 A closed marker set

**What.** `⛔` prohibition · `⚠️` measured hazard · `✅` shipped or closed. **Everything else is prose.**
Doubling (`⛔⛔`, `⛔ ⛔`, `⛔**⛔**`) is a defect. Gated by `check_marker_convention.py`, with **no
grandfather list, no baseline and no per-file exemption**.

**Evidence.** The finding was not inconsistency. Until 2026-09-04 **nothing had ever defined what the
glyphs meant** — they were used throughout the operating contract, the system document, the index and
the decisions register with no stated semantics anywhere, so there was no convention to be inconsistent
with. That absence was the defect. The test that makes it work is written at the site and is the
transferable part: before typing `⚠️`, *can you name the incident or the measurement?* A hazard nobody
has hit is a guess, and a guess is prose. Before typing `⛔`, *is there something a reader could
disobey?*

**Pro.** In a corpus where every document is read under time pressure by something that pattern-matches,
emphasis inflation is a real cost and it is invisible in review. The rule costs nothing to adopt and the
"can you name the incident" test upgrades a marker from decoration to a claim.

**Con.** It is house style. Adopting a specific glyph vocabulary into a format that already has enough
to argue about would be over-reach, and a bundle using none of them loses nothing. The disjointness
requirement is also strict enough to be irritating early.

**Recommendation — Adopt as tier 3, stated generically**: if a bundle uses emphasis markers, the set
should be **closed and defined in one place**, and each marker should carry the test you apply before
typing it. Do not prescribe these three glyphs.

### 2.8 Ratchet an L3 document when read volume, not layer, says to

**What.** The local system document is L3 by read-pattern — *only the one you are acting on* — and is
byte-ratcheted anyway (`check_context_system_size.py`), on the same fail-both-directions model as the
operating contract. It is the **only** carve-out from "L3 is unbounded".

**Evidence.** It is ranked **14th of 579 documents by recorded reads** (`report_doc_usage.py --union`;
re-run it rather than quoting the rank — an earlier version of this claim said *10th of 487* and was
wrong in both numbers). It had grown 3.7× in sixteen days, at roughly one commit per new gate. The
decision rule that came out of it: **a document is budgeted by how often it is actually read, not by
which layer it nominally belongs to**, and the only way to know that is 2.1.

**Pro.** It is the first concrete payoff of the read instrument, and it is a rule a bundle can act on
without adopting anything else structural. It also names the trap: the digests behind that rank covered
only two months, so the rank predates some of the content it was used to justify budgeting.

**Con.** It is entirely dependent on 2.1 — without measurement it degenerates into "budget the documents
that feel important", which is worse than the layer rule it replaces. And the carve-out is dangerous to
generalise: applied loosely it reintroduces budgets across `docs/**`, which
[Index size budgets](../FORMAT.md#index-size-budgets) deliberately leaves unbounded.

**Recommendation — Adopt**, tied to 2.1, phrased as a permission rather than a rule: *a layer's budget
policy is a default; where measurement shows a document is read at a rate its layer does not predict,
budget that document and say why at the site.*

---

## 3. Refinements to mechanisms PCS already has

### 3.1 Frontmatter must parse the way the consumer parses it

**What.** The local wikilink checker now enforces four properties, not one: frontmatter must **parse as
the consumer parses it** (including rejecting a **duplicate key**, which Obsidian's parser rejects
outright while PyYAML silently keeps the last); the line scanner and the YAML parser must **agree**;
dangling links are ratcheted in both directions; and a **linked** key must resolve to **exactly one**
note, checked across every git-tracked markdown file repo-wide.

**Evidence.** **119 notes** carried an unquoted `description:` whose content broke YAML parsing, which
**silently dropped their `aliases:`** from the consumer's view. Every one of those notes was
unreachable by alias while looking perfectly correct in the file and in review. This is the same
masking effect the previous report's §1.1 identified one layer up: a check on `name:`/`aliases:`
content cannot see a note whose frontmatter never parsed at all. Separately, an ambiguous wikilink key
that matched two notes used to resolve **silently** to one of them.

**Pro.** `pcs_lint.py` already resolves links directly, which is the right design. This adds the
prerequisite: *resolution is only meaningful if your parser and the consumer's parser agree about what
the frontmatter says.* Duplicate-key handling is a concrete divergence between two widely-used parsers,
with opposite behaviours, and the permissive one is the one bundles lint with.

**Con.** It is Obsidian-specific in its details, and a bundle consumed only by agents may not care which
parser is stricter.

**Recommendation — Adopt** into [Reference implementation](../TOOLING.md#reference-implementation) as a
scoping note on the existing link checks: parse frontmatter the way the consumer does, reject duplicate
keys rather than resolving them, and require a linked key to resolve to exactly one note.

### 3.2 Lifecycle vocabulary — `shipped` added, `archived` removed

**What.** [Lifecycle](../FORMAT.md#lifecycle) is already a frontmatter field. This bundle's vocabulary
settled on `active | superseded | shipped | withdrawn`, with `superseded_by:` required when superseded.
**`shipped` was added and `archived` removed** in one ruling (2026-09-05).

**Evidence.** `shipped` means *the work this document specified is done; it is a record, not an
instruction* — neither live nor superseded, and locally **5–10× more common than partial supersession**.
Without it, finished specs get marked `superseded` (false: nothing replaced them) or left `active`
(false: they read as instructions). `archived` was removed because it describes **location**, which the
filing flow already owns, not **state** — and a status field carrying both is a field with two meanings.

**Useful limits from the checker, worth copying.** It cannot tell you a status is *true* —
`status: active` on an abandoned document passes. `superseded_by:` is checked for **existence, type and
acyclicity**, not for correctness. The acyclicity property is real and was added after first ship:
supersession chains can close into a loop, and each document in the loop looks individually fine.

**Pro.** Small, cheap, and fixes a vocabulary gap that otherwise produces two different lies.

**Con.** Vocabulary choices are the easiest thing to bikeshed, and a four-value set is already a
compromise.

**Recommendation — Adopt** the `shipped`/`archived` distinction and the acyclicity property. State the
"cannot tell you a status is true" limit at the site — it is exactly the class of limit
[Designing a check that survives](../TOOLING.md#designing-a-check-that-survives) says to write down.

### 3.3 Closing the key-column hole TOOLING already names

**What.** `check_decisions_numbering.py` — catches two rulings claiming the same identifier, and an
index row whose **key cell** no longer points at that number's own heading.

**Evidence.** TOOLING's fifth check-design property already uses this bundle's own gate as its worked
example: *"one gate never compared its key column, so a row filed under the wrong key passed green, on
a file whose entire purpose was lookup by key."* This is the repair for that named hole. The original
bijection gate compares **titles by containment** — which is load-bearing, since the index truncates at
150 characters and a `WITHDRAWN <title>` prefix must still pass — so the key column genuinely cannot be
folded into it and needs a second check.

**Pro.** It closes a hole the format already documents, and it demonstrates something useful about the
"state the limit" property: **a written limit is a backlog item, not an absolution.** The limit was
correctly written down and then quoted as coverage for months.

**Con.** Only applies to bundles with a decisions register, which is already Tier 3. Two gates over one
register is a lot of machinery.

**Recommendation — Adopt as tier 3**, in
[Optional types for larger bundles](../FORMAT.md#optional-types-for-larger-bundles) beside the register,
with the general note: where a check's stated limit describes a property the artifact's purpose depends
on, the limit is a defect to schedule, not a caveat to ship.

### 3.4 A document that enumerates an interface must be derived from that interface

**What.** Two gates, one shape. `check_api_md_coverage.py` verifies the API document describes **exactly**
the routes the application registers — no more, no less. `check_f_item_tally.py` makes a QA checklist's
own status tally a **checked fact rather than a hand count**.

**Evidence.** Both are instances of a rule PCS already has —
[Original content and restatement](../FORMAT.md#original-content-and-restatement) says a layer holding a
restatement *"needs a link, a derivation, or a check to keep it honest"* — applied to a case the wording
does not obviously cover: a document that restates an **interface** (a route list, a test inventory, a
checklist tally) rather than another document. [measured 2026-09-13] the API document took **61 commits
in 30 days**; a restatement moving at that rate is not maintained by discipline.

**Pro.** It makes the existing rule concrete in the direction adopters most often need it — docs against
code — and the check is mechanical in both directions (a documented route that no longer exists is as
much a defect as an undocumented one).

**Con.** Fully project-specific in implementation: it needs to enumerate a framework's routes. And it is
arguably already covered by the existing rule, so adopting it risks restating the format's own guidance
— which is the defect this very section is about.

**Recommendation — Adopt as tier 3**, as one sentence and two examples under
[Original content and restatement](../FORMAT.md#original-content-and-restatement), not as a new rule:
*the restated thing may be an interface rather than a document — a route list, a test inventory, a
tally — and the same three options apply.*

### 3.5 What a ratchet actually produced over 27 days — an honesty report

**What.** Not a proposal. A measurement of PCS's own mechanism, offered because
[Two ways to bind forward](../TOOLING.md#three-ways-to-bind-forward) makes a specific claim — *"it buys no
compaction, it converts drift into a decision"* — and this bundle now has enough history to say what
that looks like in practice.

**Evidence [measured 2026-09-13].** The operating contract's byte ratchet, from the day it landed:

| | |
| --- | --- |
| Landed | 2026-08-12 at 42,436 bytes |
| Today | 59,639 bytes — **+40.5% in 27 days** |
| Baseline changes | **37** |
| Raises | 31 |
| Lowerings | 6, totalling **−341 bytes** (largest single: −149) |

Every one of those 37 changes was a typed number with a stated reason. The mechanism worked exactly as
specified, and the file still grew two-fifths.

**Pro of recording it.** The claim in TOOLING is correct and is stated carefully — *overselling it is
how the next person concludes it did not work* — and this is the evidence for that sentence rather than
against it. It also gives an adopter a realistic expectation: a ratchet on a live, high-traffic file
will be raised roughly **once a day**, and the cost is real but small.

**The one thing it does show.** Two-directional ratcheting is supposed to bank slack immediately. Six
lowerings totalling 341 bytes against 17,544 bytes of growth suggests the downward direction is doing
almost nothing on a file that is genuinely accreting. It is not broken — there was simply almost no
slack to bank — but an adopter should not expect the downward arm to act as a brake.

**Con.** It is a single data point from one unusually incident-dense file, and the bundle in question
also has a standing ruling *against* compacting that file, which removes the main pressure that would
produce lowerings elsewhere.

**Recommendation — Adopt as an honesty note** in
[Two ways to bind forward](../TOOLING.md#three-ways-to-bind-forward): one line giving a real observed rate
and outcome, so the claim carries a number. It strengthens the section rather than weakening it.

### 3.6 A defect in `check_doc_links.py`, found by writing this report

**What.** `check_doc_links.py`'s `slug()` collapses whitespace with `re.sub(r"\s+", "-", …)` **after**
stripping punctuation. GitHub's slugger converts each space independently. Where a heading contains
punctuation **surrounded by spaces** — an em dash, most obviously — the two disagree: GitHub leaves a
double hyphen, this checker leaves a single one.

**Evidence [measured 2026-09-13].** For the heading `## Tier 3 — registers, research, and ratchets`:

```
$ printf '%s' '## Tier 3 — registers, research, and ratchets' \
    | gh api markdown --method POST --field text=@-
id="user-content-tier-3--registers-research-and-ratchets"     # GitHub: two hyphens

$ python3 scripts/check_doc_links.py .
no heading `#tier-3--registers-research-and-ratchets` in ../ADOPTION.md   # the gate: one
```

So the gate is wrong in **both** directions on the same heading: a link written correctly for GitHub
**fails** it, and a link written to satisfy it is **dead on github.com** — where this repository is
public and read. This is not hypothetical drafting trouble; it is what happened writing §1.1 of this
report, and the reflex it produced was to "fix" a correct link to make the gate green, which is the
bypass the format's own first check-design property warns about.

**Current blast radius: latent, not live.** No file in this repository currently links to an em-dash
heading, so nothing is dead today. But every tier heading in `ADOPTION.md` is of exactly that form —
`Tier 0 — two files`, `Tier 1 — concept files`, `Tier 2 — sub-indexes and a gate`, `Tier 3 — …` — and
those are among the most linkable headings in the guide. §1.1 of this report wanted to link one and
had to route around it.

**The fix** is one line: convert spaces to hyphens **before** stripping punctuation, or strip
punctuation to a space rather than to nothing. Worth a selftest case with an em dash either way.

**Why it belongs in this report rather than a bare issue.** The docstring says *"GitHub's anchor"*, and
that claim was never tested against GitHub. It is the fourth property from
[Designing a check that survives](../TOOLING.md#designing-a-check-that-survives) — state what a green
run does not prove — applied to a checker whose entire job is agreeing with a renderer. The general
form: **a check that reimplements a consumer's behaviour needs at least one test against the actual
consumer**, not only against its own model of it. That is the same shape as §3.1, where a bundle's YAML
parser and Obsidian's disagreed about duplicate keys, and it is worth stating once in TOOLING for both.

**Recommendation — Adopt (fix), and add the general clause** to
[Designing a check that survives](../TOOLING.md#designing-a-check-that-survives).

---

## 4. What running this layer for a month actually cost

The previous report proposed mechanisms. This section reports what having many of them feels like, since
that is the question an adopter reading PCS cannot otherwise answer.

### 4.1 The numbers

[all measured 2026-09-13, in the source bundle]

| | |
| --- | --- |
| Checks on the lint target | **33** prerequisites, **30** gate scripts |
| Size of the enforcement layer | ~17,000 lines, **59% prose** |
| Full lint run | **2m17s** wall, green |
| Tests it runs | **1,190** across four pytest invocations, ~101s — **74% of runtime** |
| Checks defending the knowledge system | **18 of 33** |
| Checks defending the checks themselves | ~5 |
| Checks citing a dated incident they already caught | **25 of 30** |
| Documents in the corpus | 957 tracked; **446 never read** (2026-08-23) |

**The honest reading:** the checks are not the expensive part. Two minutes occasionally is cheap, and
the 30 scripts have caught 25 documented defects between them. The expensive artifacts are the
always-loaded operating contract at 59,639 bytes — read on every turn **and every subagent hop** — and a
corpus where nearly half the documents have never been read by anything. **A bundle can be
over-enforced and under-read at the same time, and only the second one costs per use.**

### 4.2 "Hang it off a command people already run" needs a level up

**What.** [Designing a check that survives](../TOOLING.md#designing-a-check-that-survives)'s third
property says to make a check a dependency of the lint or test entry point rather than a standalone
target, because *"a target nobody invokes is a rule that is still enforced only by memory, with the
added cost of looking enforced."* That is right, and it stops one level too early.

**Evidence.** [measured 2026-09-13] this bundle has **zero tracked `.github` files, no pre-commit
configuration, and no active git hooks**, while merging **500+ pull requests in 31 days**. All 33 checks
and all 1,190 tests fire only when a person or an agent types the command. The property the rule is
reaching for is not *"is it attached to a command"* — it is *"is it attached to something that runs
without anyone deciding to run it."* By that test, a bundle can satisfy the rule as written and still be
enforced entirely by memory, with exactly the *"added cost of looking enforced"* the rule warns about.
That is the state this bundle has been in for its entire life, and it took an outside question to
notice.

**A second-order finding, for adopters who reach for CI.** Making it automatic is not free of the same
trap. Two details found while planning it here: the diff-scoped check of §2.3 resolves its base against
a remote ref and **explicitly errors when that resolves to `HEAD` itself**, which is what a shallow CI
checkout of a pull-request merge ref produces — so the gate fails on every run, and a gate red on a
healthy tree gets switched off, which is the first property in the same section. And the local install
recipe hard-codes a platform-specific binary path, which a clean CI checkout would have caught on day
one had one ever existed.

**Pro.** It is a one-sentence strengthening of an existing rule, it is falsifiable, and the failure it
describes is invisible from inside a bundle — everything looks gated.

**Con.** CI is not available or appropriate to every adopter, and a format that implies it excludes
people working locally. Note also that on this bundle's hosting plan, required status checks are a paid
feature, so a workflow reports rather than blocks — making the honest version of the advice *"attach it
to something automatic, and know whether that thing can actually refuse a merge."*

**Recommendation — Adopt.** Extend the third property: *the command the check hangs off must itself be
run by something other than a person's memory — a hook, a CI trigger, a scheduled job. If nothing runs
it unprompted, the check is a convention with a longer setup.* Add the two CI traps as a short note; the
base-ref one will otherwise be rediscovered by everyone.

### 4.3 Corpus liveness as a gate-review criterion

**What.** PCS requires a new gate to name the defect it has already caught. That is an **admission**
rule. There is no **retention** rule, and this report started out assuming the retention problem was
real here.

**Evidence.** It was not. Measuring commits-per-30-days on each corpus a document gate defends
[measured 2026-09-13, `git log --since='30 days ago' --oneline -- <path> | wc -l`]:

| Corpus | 30-day commits |
| --- | --- |
| The loop register | **490** |
| Decisions register / its index | 155 / 129 |
| Single-owner registry | 93 |
| API document | 61 |
| System document | 54 |
| Working-set index | 49 |
| Operating contract | 32 |
| QA checklist | 9 |

**No gate here defends a dead file.** The prediction going in was that the largest gate — 80KB of
script — was guarding a closed register; it turned out to be guarding the single most-written file in
the repository. Two gates whose registries moved once or twice in 30 days are the quiet ones, and both
still express a live standing rule.

**Pro.** It is a cheap, mechanical periodic review that is the natural counterpart to the admission
rule, and it produces a defensible *keep* as often as a *remove* — which is what makes it safe to run.

**Con.** Liveness is a proxy: a gate defending a file that is rarely written may be *preventing* the
writes. A gate should not be removed on this signal alone, only nominated for review. And it needs
version-control history, so it says nothing about a young bundle.

**Recommendation — Adopt as tier 3**, in
[Designing a check that survives](../TOOLING.md#designing-a-check-that-survives): the same
second-reference logic PCS applies to documents, pointed at checks. *Review a check periodically against
the liveness of what it defends; a check whose corpus has stopped moving is nominated for review, not
removal.*

---

## 5. Deliberately not proposed

Listed so the absence is a decision rather than an oversight. The first two were **declined in the
previous round**; both are still declined here, with what changed noted, because in both cases the
evidence since is interesting even though the verdict is not.

| Item | Why it is not PCS's business |
| --- | --- |
| **Cross-tree write guard** (`PreToolUse` hook) — *declined last round, still declined* | Harness- and worktree-specific. What changed: it now **fails closed**, and the first platform it met that it had not been tested on (`realpath -m` is a GNU extension; macOS ships BSD) made it **refuse every write in the repository, including the edits needed to repair it** — and four internal `\|\| fallback` call sites turned out to be fail-opens wearing a fail-closed's clothes. The transferable sentence, if PCS ever wants one: *a guard whose failure mode is refuse-everything must be exercised on each platform that loads it before it is trusted there.* Not proposed as a mechanism. |
| **Stop-hook delivery-audit arming** — *declined last round, still declined* | Already covered by [the seven-point audit](../METHODOLOGY.md#seven-point-delivery-audit). What changed: the watched-path list that arms it **drifted**, and a deployment-file change behind a total outage never armed the audit; it is now pinned by its own test. If anything reaches the format it is one clause on the existing enforcement bullet: *a reminder hook is only as good as the list that arms it, so that list needs a test.* |
| **Read-side staleness of a symlinked bundle** | Four consecutive reads of one absolute path returned stale, stale, correct, stale — the stale ones byte-identical to a different working tree's copy of the same file. Real, reproducible here, and entirely a property of one harness's file cache. Recorded in case another adopter sees it; not a format concern. |
| Single-owner AST guard, writer guards, tenancy guards | About source code, not knowledge artifacts. Unchanged from last round. |
| Test-typecheck error baseline | Language-toolchain specific. Its only general content — that a burn-down ratchet should fail on **increase only** — is already in TOOLING. |
| UI-copy voice gate | Product copy, not knowledge artifacts. |

One item is **half** proposed, and the split matters: the **vault-staleness** finding. The mechanism —
a vault whose contents are whatever was last pulled by hand, measured at one point **84 commits and six
hours behind** — is environment-specific and not proposed. The **rule** derived from it is general and
is folded into §3.1: *a claim about a consumer ("N links resolve") is a claim about the bytes that
consumer can see, so name the corpus you measured, not just the parser you measured with.*

---

## Verification owed

This document was written by an agent with shell access in the source bundle and **no** access to this
repository's history beyond a clone of `main` at `e118e8a`. Grading per the convention the previous
report established:

| Claim | Status | Owner |
| --- | --- | --- |
| All figures marked **[measured 2026-09-13]** | `[EXEC]` — run in the source bundle while writing | — |
| Historical figures (2026-08-12 → 2026-09-07) | `[READ]` — quoted from the source bundle's own records, not re-derived | source-bundle maintainer |
| Every link and anchor in this file | `[EXEC]` — `python3 scripts/check_doc_links.py .` | — |
| "No PCS equivalent exists" for each §2 item | `[READ]` — established by grepping this repository's guides at `e118e8a`; a maintainer should confirm nothing in flight covers them | PCS maintainer |
| The §5 declines | `[READ]` — taken from the previous report's disposition; re-confirm the verdicts still hold | PCS maintainer |

---

## Provenance

Everything above was measured in `budgets_rewritten` (private) between **2026-08-17** — the day the
previous field report was filed — and **2026-09-13**. Pointers for the maintainer, who has access:

- `docs/CONTEXT_SYSTEM.md` — the layer model, the 17 numbered rules, and the enforcement table.
- `scripts/check_*.py` — the 30 gate scripts; each one's docstring carries its originating incident and
  its stated limits, which are the parts worth reading.
- `scripts/report_doc_usage.py` — §2.1.
- `docs/plans/2026-08-22-context-system-aging-plan.md` and
  `.claude/memory/project/project_context_system_aging_2026-08-24.md` — the workstream §2.2, §2.3 and
  §2.4 came out of, including the phases that were **cut** and why.
- `docs/plans/2026-08-12-claude-md-compaction-plan.md` — marked **DO NOT EXECUTE**; the measurement
  behind §3.5's note that the operating contract does not duplicate its leaves (4% verbatim overlap
  against a 2.2M-character corpus).
- `docs/DECISIONS.md` — the rulings behind §1.2, §1.3 and §3.2.
