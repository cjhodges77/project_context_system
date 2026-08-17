# Tooling

## Obsidian

The repository's `.claude/memory/` directory is the PCS bundle and source of truth. Symlink it into an Obsidian vault to gain wikilinks, backlinks, graph navigation, search, and canvases without maintaining a second copy.

Use Obsidian wikilinks for relationships between bundle concepts. Use Obsidian to browse memory, plans, references, and cross-links; do not use it as a substitute for code-structure analysis.

A setup script should be idempotent and conservative: create missing parent directories, create expected symlinks, leave correct symlinks unchanged, and refuse to replace real directories or unrelated links.

## Graphify

Graphify answers structural questions such as where a symbol is defined, which modules depend on it, and which areas a change can affect. Keep extraction separate from LLM-assisted relabeling so routine graph updates remain deterministic.

Use `.graphifyignore` as a privacy and relevance boundary. Exclude secrets, databases, exports, backups, dependency trees, build artifacts, generated data, and `.claude/` memory. Query the graph first, then read the source files and tests it identifies.

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

The reason is a distinction the list above was missing, and it is not "write more checks". **Review cannot enforce a property that is invisible in the artifact under review.** A dead wikilink and a live one are the same characters in the Markdown diff; the property exists only in a resolver that no reviewer opens while reviewing. That is a different category from a check that is merely unbuilt, and the two do not belong in one list. Frontmatter validity, `pcs_version`, and citation coverage are genuinely review-checkable and remain unimplemented here. Wikilink resolution and index coverage never were.

Three scoping decisions in the link checks, each of which prevents a false positive that would have got the check switched off. **Resolution is judged against the bundle**, so `--resolve-root` exists for a bundle symlinked into a wider vault whose links legitimately leave it. **Coverage asks "at least one index", not "exactly one"** — a memo routed from both the root index and `project/index.md` is a normal shape; the exactly-one rule applies only among sibling domain indexes, where two homes really does mean one goes stale. And **an alias counts as routing a leaf**, since linking by alias is what this format now recommends.

One further trap, found by the field report that prompted these checks: the obvious rule — *a `name:` must appear in its own `aliases:`* — is **vacuous for a note carrying no `name:` at all**, and three unreachable leaves shipped with that check green. Checking resolution directly avoids the whole class: a link either lands or it does not, whatever identity it was spelled with. When it does not land and the target happens to match some file's `name:`, the finding says so and names the repair, because that is the case a reader is most likely to dismiss as a typo.

### Documents outside the bundle

`pcs_lint.py` checks a bundle. The guides, specs, and plans around it link to each other by file and by heading anchor, and those links fail the same way and for the same reason — a dead anchor and a live one are identical in the diff. [`scripts/check_doc_links.py`](scripts/check_doc_links.py) resolves them.

It exists because the failure happened here. Restructuring `ADOPTION.md` around tiers deleted a heading that a document elsewhere in the tree pointed at, and the review that made the change did not notice. **Renaming a heading is an interface change**: the inbound pointers are owed in the same commit as the rename, for the reason given in [Restructuring an index](FORMAT.md#restructuring-an-index) — defer them and the gate fires later, on someone who did not make the decision.

## Designing a check that survives

A check is worth building only if it is still running in a month. Four properties decide that, and each has a documented failure behind it.

- **Green on a healthy tree.** A check that is red when nothing is wrong gets bypassed, and a bypassed check is worse than none — it reads as coverage while enforcing nothing. Never gate on a condition a healthy bundle legitimately carries, such as a plan with open items or a workstream still in flight.
- **Bind new conventions going forward.** Applying a new rule to an existing corpus reddens every document written before it, which is the fastest route to the bypass above. Scope the check by date and let the pre-convention corpus stay green; date-prefixed filenames make that cutoff mechanical rather than a judgement call. Where the unit of enforcement has no date, use a ratchet instead — see below.
- **Hang it off a command people already run.** Make it a dependency of the lint or test entry point, not a standalone target. A target nobody invokes is a rule that is still enforced only by memory, with the added cost of looking enforced. A variant this rule missed on first writing: a guard can be wired into an invoked command and still be out of reach, because *the directory it lives in* sits outside the scope that command traverses. One check sat red for days inside a test directory the lint target deliberately excludes. Existing and reachable are different properties, and a check can satisfy the first for months while failing the second.
- **State the limit inside the check.** Say what a green run does *not* prove — that it asserts form and never truth, or that it catches copy-paste but not reimplementation. A check whose limits are unwritten gets trusted for things it never verified. This is the highest-value of the four in practice: one gate never compared its key column, so a row filed under the *wrong key* passed green, on a file whose entire purpose was lookup by key. A green gate quoted as proof of something it never checked is how a check becomes worse than none.
- **Prove the red path, in both directions.** Add the defect and watch it fail naming the file; remove it and watch it pass. A gate whose red path has never been observed is a gate trusted on the strength of its docstring. One gate shipped with two errors that cancelled — a ghost row was invisible whenever a ruling went missing in the same edit — and only an independent adversarial pass found it, because a selftest written by the person holding the mental model tends to exercise the model rather than attack it. `pcs_lint.py --selftest` mutation-proves its own corpus checks this way, and caught a coverage bug during the change that added them.

### Two ways to bind forward

Date-scoping works when the unit of enforcement has a date. **A file's size does not**, and neither does a dangling-link count or an error backlog. Those need a **ratchet**: a baseline committed at today's measured value, failing on change. It lands green on day one and still closes the drift, because every future byte has to be typed into the baseline by a human who then has to say why in the commit body. `--write-baseline` is the ratchet's cousin for findings, and the difference is worth keeping straight — a baseline records findings *to forgive*, a ratchet records a measurement *to defend*.

Three things a ratchet needs stated, each learned by getting one wrong:

- **It buys no compaction — it converts drift into a decision.** That is the whole claim. Overselling it is how the next person concludes it did not work.
- **It must fail in both directions.** If it only fails on growth, a file that shrinks leaves headroom the next author fills for free, and the number drifts back up inside the slack without ever going red. Failing on a decrease too, and naming the new number to paste, is what keeps it tight.
- **The exception is about the file's goal, not the mechanism.** Where a corpus is being deliberately burned down, a two-directional ratchet reddens every legitimate eviction, so those ratchets fail on *increase only* and lowering the baseline is always correct and never required. Where the goal is stability — the operating contract — unclaimed slack is banked immediately. Same shape, opposite direction, decided by what the file is for. The standing risk is that someone later "fixes" one to match the other, so say which it is at the site.

### Considered and declined

An automation list is more useful to an adopter with three states than two. *Implemented* and *unimplemented* both read as "someone should get to it"; the third state is the one that otherwise gets lost and re-proposed every six months.

**A general "never write a computable number into prose" checker**, extended beyond indexes to all prose — *declined*. The rule is not in dispute: one session produced seven wrong sites. The objection was to the enforcement. Most rules in this format are convention by design, and a check that fires on legitimately narrative numbers gets ignored and then switched off, which is the same failure as a gate red on a healthy tree. Two details for anyone who revisits it. The narrowest version that catches the expensive cases is *a line carrying a count or baseline keyword, and a number, and no backticked command*, date-scoped. And **a digit-only rule misses half of them**: "five tag axes", "four sibling scope axes" and "corrected in all three places" were each spelled out in words, and each was wrong.

Automation should report drift, not rewrite human-authored knowledge silently.
