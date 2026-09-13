# Tooling

## Obsidian

The repository's `.claude/memory/` directory is the PCS bundle and source of truth. Symlink it into an Obsidian vault to gain wikilinks, backlinks, graph navigation, search, and canvases without maintaining a second copy.

Use Obsidian wikilinks for relationships between bundle concepts. Use Obsidian to browse memory, plans, references, and cross-links; do not use it as a substitute for code-structure analysis.

A setup script should be idempotent and conservative: create missing parent directories, create expected symlinks, leave correct symlinks unchanged, and refuse to replace real directories or unrelated links.

**Those properties are not sufficient, and one bundle deleted its linker to prove it.** The script satisfied every one of them — idempotent, created missing parents, refused to replace real directories, left correct links alone — and was still wrong, because it named the vault from `basename "$REPO"`. In a git worktree that basename is the *instance* (`2`, `3`, `main`), not the project, so each instance linked its own copy into a vault named after itself: **3,699 note instances for 941 distinct notes** (measured 2026-08-22). The visible symptom was not duplication. It was that backlinks, outgoing links and the orphan count stopped being usable, because a link resolved into an arbitrary sibling copy.

So state the property idempotence does not cover: **the vault name must be the project's identity, never a path basename** — in a worktree, a container mount, or a CI checkout, the basename is the instance. Running twice equalling running once says nothing about whether the thing converged on is the right thing.

The stronger version is worth weighing before writing the script at all. **Linking is a property of the environment**, so it belongs to whatever provisions the environment and already knows the project's identity — the container bootstrap, the dotfiles, the setup step. A repo-side linker the environment has stopped calling is worse than none: it reads as the mechanism while enforcing nothing.

## Graphify

Graphify answers structural questions such as where a symbol is defined, which modules depend on it, and which areas a change can affect. Keep extraction separate from LLM-assisted relabeling so routine graph updates remain deterministic.

Use `.graphifyignore` as a privacy and relevance boundary. Exclude secrets, databases, exports, backups, dependency trees, build artifacts, and generated data. Query the graph first, then read the source files and tests it identifies.

### Whether to graph your own memory

This format excluded `.claude/` memory outright until a bundle running it ruled the opposite way (2026-09-05) and reported what implementing the reversal cost. **Exclude is still the default** — but the reversal is defensible enough that a reader following the old sentence literally was being steered away from a legitimate design without being told it was a choice. Memory is the part of the corpus whose relationships an agent most needs to traverse, and the one where *which note does this connect to* is hardest to answer by grep. Against that, graphing it raises exposure, and **both ways of getting the fence wrong fail silently**:

- **A gitignore-style file cannot re-include under an excluded ancestor.** The obvious fence — `.claude/` followed by `!.claude/memory/` — leaves memory **excluded, with no diagnostic**. The spelling that works is `.claude/*` plus `!.claude/memory/`. A bundle that enables memory the obvious way gets a green run, an unchanged graph, and a belief that it worked.
- **Deleting the bare `.claude/` line un-fences whatever it was covering.** Anchored patterns elsewhere in the file do not match inside `.claude/worktrees/*/`, so the directory exclusion was load-bearing for paths that look fenced by their own rules. The edit that reads as a simplification is the edit that widens the privacy boundary.

Because the failure mode of a wrong fence is a **privacy** failure rather than a functionality one, a bundle that does not need the graph edges should not take the trade.

**What leaves the machine is the distinction that matters, not whether an LLM is involved.** Structural extraction is local. A semantic pass uploads whole file contents to whichever provider a key selects. A relabelling pass sends something much narrower — in graphify's case one prompt line per community, built from **verbatim markdown headings** and never from bodies. Know which of the three your tool runs before pointing it at memory, and gate the whole-file pass rather than trusting a convention to hold.

That narrow case has a consequence worth carrying even if you never build the gate: **once memory is in an LLM-labelled graph, its headings are an egress surface.** Bodies stay local; every heading leaves. That reframes heading hygiene from a style preference into a privacy control, which is the only framing under which it gets maintained — and it is cheap, because headings are short, few, and already conventional.

## Git

Git is the primary chronology and audit layer. Commit PCS changes with the work that caused them so rationale, implementation, tests, and documentation remain reviewable together. Use `log.md` only when portable history must survive outside Git.

## Agent harness

If an agent harness has its own memory location, symlink the repository bundle into it rather than copying notes. Repository memory remains authoritative. The same refusal-to-clobber rules used for Obsidian links apply.

## Optional automation

Validation may check:

- valid YAML frontmatter and required `type`;
- a root `index.md` with a supported `pcs_version`;
- duplicate `name` values;
- unresolved Obsidian wikilinks;
- active indexes pointing into `archive/`;
- learning files absent from `learnings/index.md`;
- project files absent from the root `index.md`;
- external claims without references or citations;
- Graphify inputs that cross privacy exclusions.

Shape checks catch the drift that size checks miss. A character budget bounds how large a duplicated summary may be but never whether it exists, so also flag:

- computable figures in prose — byte counts, file sizes, test counts, error counts, entry totals — which should name the command that derives them instead;
- status stated anywhere but the owning project memo's header;
- index entries carrying a value that another layer owns.

The third is the one to get right, because the obvious implementation of it is wrong. Keying on character class — *flag any entry containing a number, a currency amount, a commit SHA, or a status word* — is a one-line regular expression, and measured against a real bundle it fired on more than half the entries of an index that was working fine. Most of those numbers were fixed observations that no other document owns and that will never change. Key on ownership instead: flag a value some other layer maintains, leave a value that is simply a fact about the past.

### Reference implementation

`scripts/pcs_lint.py` implements the size and shape checks above. It is stdlib-only Python with no dependencies, meant to be vendored into a consuming project and hung off that project's existing lint target:

```bash
python3 scripts/pcs_lint.py .claude/memory
```

`--selftest` exercises the rules themselves rather than a bundle, so a change to a pattern has something that fails when it is wrong. `--write-baseline` records an existing corpus's findings so the rule binds new work only.

Two scoping decisions in it are worth carrying into any reimplementation, because both were forced by running it on a real bundle. **The derived-value check applies to indexes, not leaves** — a learning's evidence is *meant* to carry concrete measurements, they describe what happened once, and they never drift; scanning leaves produced hundreds of findings on a healthy bundle. **A missing status header is opt-in** (`--require-status`) while a duplicated one always fails: the second is drift, the first is a convention the bundle may not have adopted, and defaulting it on reddens every memo in an existing corpus.

It also implements **wikilink resolution, index coverage, and duplicate `name:` detection**. Those three sat on the unimplemented list until a bundle running this format reported what the omission cost: review had been enforcing wikilink resolution there for the corpus's entire life, at a **97.6% failure rate**, and leaves were sitting in no index at all.

The reason is a distinction the list above was missing, and it is not "write more checks". **Review cannot enforce a property that is invisible in the artifact under review.** A dead wikilink and a live one are the same characters in the Markdown diff; the property exists only in a resolver that no reviewer opens while reviewing. That is a different category from a check that is merely unbuilt, and the two do not belong in one list. `pcs_version` and citation coverage are genuinely review-checkable and remain unimplemented here. Wikilink resolution and index coverage never were. Frontmatter validity has since split across the line: most of it is reviewable, and the part where **two parsers disagree** is not, which is why the duplicate-key case is implemented and the rest is not.

Three scoping decisions in the link checks, each of which prevents a false positive that would have got the check switched off. **Resolution is judged against the bundle**, so `--resolve-root` exists for a bundle symlinked into a wider vault whose links legitimately leave it. **Coverage asks "at least one index", not "exactly one"** — a memo routed from both the root index and `project/index.md` is a normal shape; the exactly-one rule applies only among sibling domain indexes, where two homes really does mean one goes stale. And **an alias counts as routing a leaf**, since linking by alias is what this format now recommends.

One further trap, found by the field report that prompted these checks: the obvious rule — *a `name:` must appear in its own `aliases:`* — is **vacuous for a note carrying no `name:` at all**, and three unreachable leaves shipped with that check green. Checking resolution directly avoids the whole class: a link either lands or it does not, whatever identity it was spelled with. When it does not land and the target happens to match some file's `name:`, the finding says so and names the repair, because that is the case a reader is most likely to dismiss as a typo.

**Resolution is only as good as the parse underneath it, so parse the frontmatter the way the consumer parses it.** On one bundle **119 notes** carried an unquoted `description:` that broke YAML parsing and silently dropped their `aliases:` from the consumer's view: every one was unreachable by alias while looking perfectly correct in the file and in review. That is the masking effect above, one layer further down — a check on `aliases:` content cannot see a note whose frontmatter never parsed at all. The concrete divergence to start from is a **duplicate key**, where two widely-used parsers behave in opposite ways: Obsidian rejects the block outright, PyYAML keeps the last value, and the permissive one is the parser bundles lint with. `pcs_lint.py` reports one, scoped to top-level keys, because this format's own templates carry `type:` at the root and again under `metadata:` — a nesting, not a collision.

**A key that reaches two notes is not a link that works.** Obsidian resolves an ambiguous key silently to one of them, so the text says one thing and the graph says another and neither is visible in review. Require a linked key to resolve to **exactly one** note.

There is a reporting rule behind both: **name the corpus you measured, not just the parser you measured with.** A claim about a consumer — *404 of 414 links resolve* — is a claim about the bytes that consumer can see, and one vault was measured at 84 commits and six hours behind the repository it mirrored.

**Coverage and admission are a pair, and only the second acts on inflow.** Coverage asks *is this leaf reachable* — in at least one index. Admission asks the entry question: *has this leaf earned a place in something that is always loaded?* A document reaches a loaded index once something **other than an index** references it. The premise is that episodic pruning cannot beat continuous addition — a corpus that admits everything and cleans up periodically is a corpus whose size is set by how often somebody runs a cleanup. The second-reference threshold is not arbitrary: five independent cache-replacement designs (LRU-K, 2Q, LIRS, TinyLFU, S3-FIFO) converged on it, because one reference cannot distinguish a working-set member from a bulk load. Thirty documents written in one session have exactly one reference each and are invisible to promotion by construction, with no bulk detector needed.

Ship the failure alongside it, because a reimplementation will otherwise repeat it. A third evidence channel — *a mention in a commit message from some commit other than the one that created the file* — was added to one bundle and removed the same day: commit messages that named two files purely to explain a ratchet were credited as third-party citations, and the finding count fell 2 → 0 with **zero real citations added**. The lesson is narrower than "commit messages are bad evidence": **an evidence channel the author also writes is not independent**, and independence is the entire property being tested.

`--admission` implements it, and is opt-in for the reasons that keep it out of Tier 1: it bites hardest exactly when a bundle is young and legitimately writing many documents at once, it needs a baseline or a ratchet to land green on an existing corpus, and it enforces a **routing** property rather than a quality one — a weak document with two references is admitted, a strong one with a single reference is not.

**Supersession is checkable for shape and nothing else.** `superseded_by:` is verified for existence, uniqueness, and **acyclicity**; a chain can close into a loop in which every document points at a successor, each one looks individually correct, and none of them is current. What no checker can tell you is whether a status is *true* — `active` on an abandoned document passes every gate here.

### Documents outside the bundle

`pcs_lint.py` checks a bundle. The guides, specs, and plans around it link to each other by file and by heading anchor, and those links fail the same way and for the same reason — a dead anchor and a live one are identical in the diff. [`scripts/check_doc_links.py`](scripts/check_doc_links.py) resolves them.

It exists because the failure happened here. Restructuring `ADOPTION.md` around tiers deleted a heading that a document elsewhere in the tree pointed at, and the review that made the change did not notice. **Renaming a heading is an interface change**: the inbound pointers are owed in the same commit as the rename, for the reason given in [Restructuring an index](FORMAT.md#restructuring-an-index) — defer them and the gate fires later, on someone who did not make the decision.

It also models a renderer, and that model was wrong twice before anything tested it against the renderer. `slug()` collapsed runs of whitespace where GitHub converts each space independently — so `Tier 3 — registers, research, and ratchets` anchors as `tier-3--registers-research-and-ratchets`, with two hyphens — and it stripped every underscore as emphasis where GitHub keeps one inside a word. Each defect was wrong in **both directions at once**: a link written correctly for GitHub failed the gate, and a link written to satisfy the gate was dead on github.com. The reflex both produced was to "fix" the correct link until the gate went green, which is the bypass the first check-design property warns about. `--selftest` now pins the cases against ids read from rendered pages and grades the unverified ones separately.

## Designing a check that survives

A check is worth building only if it is still running in a month. These properties decide that, and each has a documented failure behind it.

- **Green on a healthy tree.** A check that is red when nothing is wrong gets bypassed, and a bypassed check is worse than none — it reads as coverage while enforcing nothing. Never gate on a condition a healthy bundle legitimately carries, such as a plan with open items or a workstream still in flight.
- **Bind new conventions going forward.** Applying a new rule to an existing corpus reddens every document written before it, which is the fastest route to the bypass above. Scope the check by date and let the pre-convention corpus stay green; date-prefixed filenames make that cutoff mechanical rather than a judgement call. Where the unit of enforcement has no date, use a ratchet or the diff instead — see below.
- **Hang it off a command people already run.** Make it a dependency of the lint or test entry point, not a standalone target. A target nobody invokes is a rule that is still enforced only by memory, with the added cost of looking enforced. A variant this rule missed on first writing: a guard can be wired into an invoked command and still be out of reach, because *the directory it lives in* sits outside the scope that command traverses. One check sat red for days inside a test directory the lint target deliberately excludes. Existing and reachable are different properties, and a check can satisfy the first for months while failing the second. And the rule as written stops one level short of the property it is reaching for, which is not *is it attached to a command* but **is it attached to something that runs without anyone deciding to run it** — a hook, a CI trigger, a scheduled job. One bundle merged 500+ pull requests in 31 days while its 33 checks and 1,190 tests fired only when a person typed the command: fully gated by the rule as written, enforced entirely by memory in fact, at exactly the added cost of looking enforced. Reaching for CI carries the same trap twice over, so know **whether the automatic thing can actually refuse a merge** — where required status checks are a paid feature a workflow reports rather than blocks, which is a weaker claim than enforced — and see [Making it run without you](ADOPTION.md#making-it-run-without-you) for the two details that otherwise get rediscovered.
- **State the limit inside the check.** Say what a green run does *not* prove — that it asserts form and never truth, or that it catches copy-paste but not reimplementation. A check whose limits are unwritten gets trusted for things it never verified. This is the highest-value of them in practice: one gate never compared its key column, so a row filed under the *wrong key* passed green, on a file whose entire purpose was lookup by key. A green gate quoted as proof of something it never checked is how a check becomes worse than none. Two corollaries, both learned *after* a limit had been correctly written down. **A written limit is a backlog item, not an absolution** — where it describes a property the artifact's purpose depends on, it is a defect to schedule rather than a caveat to ship, and that key-column limit was quoted as coverage for months. And **a check that reimplements a consumer's behaviour needs at least one test against the actual consumer**, not only against its own model of it: a linter whose YAML parser disagreed with Obsidian about duplicate keys, and an anchor slugger that disagreed with github.com in two separate ways, were both written from a plausible reading of a consumer that nothing had ever asked.
- **Prove the red path, in both directions.** Add the defect and watch it fail naming the file; remove it and watch it pass. A gate whose red path has never been observed is a gate trusted on the strength of its docstring. One gate shipped with two errors that cancelled — a ghost row was invisible whenever a ruling went missing in the same edit — and only an independent adversarial pass found it, because a selftest written by the person holding the mental model tends to exercise the model rather than attack it. `pcs_lint.py --selftest` mutation-proves its own corpus checks this way, and caught a coverage bug during the change that added them.
- **Run the proof on the same command as the check.** A red path proven once and never re-run decays into a gate nobody can trust, and it does so invisibly, because the gate itself is still green. Measured on one bundle: two gates shipped with 36- and 42-case proof suites that nothing routine ran, and a third was running in `lint` while its own suite was red and unseen. Where a bundle has several checks with several proof files, **derive that list rather than maintain it** — read the build file's own prerequisites and run the proof belonging to each check it invokes, so a new gate is covered the moment its target and its proof both exist, with no third place to remember. A vendored single script gets this for free by carrying the proof inside itself, which is the right weight for this audience: `pcs_lint.py --selftest` and `check_doc_links.py --selftest` are dependencies of the same target as the checks they prove.

### Admitting and retiring a check

Two rules, one at each end of a check's life. Both are the second-reference logic this format applies to documents, pointed at the checks instead.

**A new check must name the defect it has already caught, not one it might.** A hazard nobody has hit is a guess, and a guess costs everyone who runs the gate. One bundle holding itself to this had 25 of its 30 gate scripts citing a dated incident in the docstring.

**Review a check periodically against the liveness of what it defends.** Commits per 30 days over the corpus a gate guards is mechanical, cheap, and produces a defensible *keep* as often as a *remove* — which is what makes it safe to run at all. It is a proxy and not a verdict: a gate defending a file that is rarely written may be *preventing* the writes, so a quiet corpus nominates its check for review, never for removal. It also says nothing about a young bundle, since it needs history to read.

### Three ways to bind forward

Date-scoping works when the unit of enforcement has a date. **A file's size does not**, and neither does a dangling-link count or an error backlog. Those need a **ratchet**: a baseline committed at today's measured value, failing on change. It lands green on day one and still closes the drift, because every future byte has to be typed into the baseline by a human who then has to say why in the commit body. `--write-baseline` is the ratchet's cousin for findings, and the difference is worth keeping straight — a baseline records findings *to forgive*, a ratchet records a measurement *to defend*.

Three things a ratchet needs stated, each learned by getting one wrong:

- **It buys no compaction — it converts drift into a decision.** That is the whole claim. Overselling it is how the next person concludes it did not work.
- **It must fail in both directions.** If it only fails on growth, a file that shrinks leaves headroom the next author fills for free, and the number drifts back up inside the slack without ever going red. Failing on a decrease too, and naming the new number to paste, is what keeps it tight.
- **The exception is about the file's goal, not the mechanism.** Where a corpus is being deliberately burned down, a two-directional ratchet reddens every legitimate eviction, so those ratchets fail on *increase only* and lowering the baseline is always correct and never required. Where the goal is stability — the operating contract — unclaimed slack is banked immediately. Same shape, opposite direction, decided by what the file is for. The standing risk is that someone later "fixes" one to match the other, so say which it is at the site.

**What a ratchet actually produced, measured over 27 days.** One operating contract's byte ratchet, from the day it landed: 42,436 bytes to 59,639, **+40.5%**, across **37** baseline changes — 31 raises against 6 lowerings totalling **−341 bytes**. Every one of the 37 was a typed number with a stated reason. The mechanism worked exactly as specified and the file still grew two-fifths. Two expectations follow: a ratchet on a live, high-traffic file gets raised roughly **once a day**, and the downward arm does almost nothing on a file that is genuinely accreting, because there is no slack to bank. That is evidence for the first bullet rather than against it, and an adopter who expects a brake will conclude the mechanism failed.

**The third way is to scope by the diff.** Enforce the rule on an entry you **add or modify**, and exempt pre-existing ones indefinitely. It lands green, it never reddens the back catalogue, and — alone among the three — it produces reduction, at the rate the corpus is actually worked. It closes a gap the other two leave: a count-based ratchet on over-long entries is increase-only, so editing an over-long entry into a *different* over-long entry leaves the count identical and passes.

Two limits, and the second is the more useful:

- **A move is not a touch.** Comparing per file means that splitting an oversized index into sub-indexes — the remedy this format prescribes — registers as dozens of edits and fails. Compare the **union of normalised entries across the files**, so relocating an entry byte-identically is not an edit, and make the normalisation robust to re-wrapping: the same words folded at a different column must count as untouched.
- **Do not use it where the unit has no identity outside the diff.** For a register whose rows are read whole on every run and which a concurrent process appends to, "touched" is a git diff: identical content passes or fails depending on merge base, rebase, or a dirty tree, and it races a writer moving `HEAD`. Use a per-row invariant with a shrink-only grandfather list there instead. The discriminator is whether the unit of enforcement has a stable identity independent of the diff — an index *entry* does, after normalisation; a register row being appended to concurrently does not.

The standing limit on the third way: **reduction happens at the rate the file is worked, and where that rate is zero, so is this.**

### Considered and declined

An automation list is more useful to an adopter with three states than two. *Implemented* and *unimplemented* both read as "someone should get to it"; the third state is the one that otherwise gets lost and re-proposed every six months.

**A general "never write a computable number into prose" checker**, extended beyond indexes to all prose — *declined*. The rule is not in dispute: one session produced seven wrong sites. The objection was to the enforcement. Most rules in this format are convention by design, and a check that fires on legitimately narrative numbers gets ignored and then switched off, which is the same failure as a gate red on a healthy tree. Two details for anyone who revisits it. The narrowest version that catches the expensive cases is *a line carrying a count or baseline keyword, and a number, and no backticked command*, date-scoped. And **a digit-only rule misses half of them**: "five tag axes", "four sibling scope axes" and "corrected in all three places" were each spelled out in words, and each was wrong.

**A budget on the enforcement layer itself** — *declined, and replaced with a measurement.* The `check_*.py` layer of a mature bundle is a corpus like any other: measured at **59% prose, 8,121 prose lines to 5,712 of code**, with the worst single gate going 102 → 975 lines across 23 commits while its executable code stayed near 79. Nothing measured any of it — the scripts sat in no budget, no ratchet, and outside every index check. A cap is still the wrong instrument, because **the prose is the mechanism**: the cheapest way to pass a comment budget is deleting the reason a rule exists, which is precisely the failure being defended against. What replaced it: measure the ratio and report it in review, require a new gate to name the defect it already caught, and archive completed records out of the hot path with a pointer. Two things keep the decision honest. "Unbudgeted" is not "harmless" — in one mutation sweep **53 of 71 surviving mutants landed inside gate comments**, inflating an apparent test-weakness figure from a true 19% to a reported 48%, so prose in the hot path distorts the measurement of the code it explains. And the decision presumes a bundle with enough checks for their prose to constitute a layer; at Tier 2, with one vendored script, there is nothing to rule on.

Automation should report drift, not rewrite human-authored knowledge silently.
