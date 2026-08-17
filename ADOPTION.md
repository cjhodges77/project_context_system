# Adoption guide

PCS scales down, and it is meant to be started small. The layout in the [README](README.md#repository-layout) is what a bundle looks like after a year of a busy repository — not what you begin with, and not a target.

A bundle that starts at the full layout pays for structure it has no content for. Empty `index.md` files in unused directories are not free: they get read, skipped, and maintained, and they tell a new agent the bundle is bigger than it is. **A directory earns its index when it has two entries in it.**

So start at tier 0 and let a **symptom** promote you. Not a schedule, not the size of the repository, and not the ambition of the project — each tier below names the symptom that earns the next one. A bundle that sits at tier 1 for a year is a bundle working correctly, not one that failed to adopt.

## Tiers at a glance

| Tier | What exists | What it costs | Promoted by |
| --- | --- | --- | --- |
| 0 | Operating contract + one `index.md` | Minutes | An entry needs evidence that will not fit on its line |
| 1 | Concept files in the directories you actually use | A file per lesson | Scrolling the index to find something you know you wrote |
| 2 | Per-directory indexes, domain split, `archive/`, the linter | A gate in CI | A second author, or an entry going stale unnoticed |
| 3 | Decisions register, `research/`, ratchets, Graphify, hooks | Ongoing enforcement | Authors who cannot run what they document; absences that mislead |

---

## Tier 0 — two files

```bash
mkdir -p .claude/memory
```

**`CLAUDE.md` or `AGENTS.md`** at the repository root — the operating contract. Tool routing, quality gates, trust-boundary rules, and the obligation to ship a context update with the change that caused it. This is the only file guaranteed to be read every turn, so what goes in it is what must never be missed.

**`.claude/memory/index.md`** — the whole bundle, for now. Declare the version and write one line per thing worth remembering:

```markdown
---
pcs_version: "0.1"
---

# Project context

## Active work

- [[project-checkout-rewrite]] — replacing the legacy cart; open questions live in the memo

## Learned the hard way

- Staging seeds run *after* migrations, so a migration that reads seed data passes locally and fails only in CI
```

No directories, no leaf files, no linter, no Graphify. An entry that never outgrows its line never needs a file of its own. Two rules from [FORMAT.md](FORMAT.md) apply from the first line and never stop applying, because both get more expensive to retrofit than to adopt: write wikilinks bare rather than in backticks, and keep entries [unfalsifiable by progress](FORMAT.md#index-entry-shape).

**Promoted when** an entry needs evidence — a command, a diff, the actual error text — that does not belong on one line.

## Tier 1 — concept files

Create only the directories you have content for. `learnings/` usually comes first; `project/` follows when a workstream outlives a single session.

```bash
mkdir -p .claude/memory/learnings
```

Write the leaf from the matching template — [learning](templates/learning.template.md), [project memo](templates/project_memo.template.md), [feedback](templates/feedback.template.md) — and leave the one-line entry in the root index pointing at it. The line says when to open the file; the file holds the story. Keep the memo's `**Status:**` header as the single place status lives.

Add `references/` and `## Citations` sections only once a claim depends on something external. Add `feedback/` when the first durable behavioural rule appears, which is usually later than expected.

**Promoted when** you scroll the root index looking for a lesson you know you wrote, or the index nears the harness load limit — see [Index size budgets](FORMAT.md#index-size-budgets). In practice the scrolling comes first.

## Tier 2 — sub-indexes and a gate

Four things, in this order, each when its own symptom shows:

1. Give each concept directory its own `index.md`, and let the root index route to those rather than to every leaf.
2. Split a catalog into a hub plus `index_<domain>.md` files once one index outgrows a few kilobytes — see [Domain sub-indexes](FORMAT.md#domain-sub-indexes) and the [domain index template](templates/domain_index.template.md).
3. Add `archive/`. Move, don't delete; preserve the outgoing file verbatim in the same change that rewrites it.
4. Vendor the linter.

### Vendoring the linter

Make [`scripts/pcs_lint.py`](scripts/pcs_lint.py) a dependency of the lint or test target the project already runs, never a target of its own:

```bash
python3 scripts/pcs_lint.py .claude/memory --write-baseline --baseline .claude/memory/.pcs-lint-baseline
```

Baseline first. An existing bundle will have findings, and a check that is red the day it lands gets bypassed; baselining binds the rule to new work and leaves the back catalogue to be cleared deliberately. Then drop entries from the baseline as you fix them.

Expect the link findings to dominate on an existing bundle, and read them before baselining them — a high failure rate there is the normal result, not a misconfiguration. The [field evidence](TOOLING.md#reference-implementation) is a corpus where 404 of 414 wikilinks resolved to nothing.

Two things to confirm once, by hand, the day you wire it in:

- **Mutation-prove it.** Break something on purpose, watch the gate go red naming the file, fix it, watch it go green. A gate whose red path you have never seen is a gate you are trusting on the strength of its docstring.
- **Confirm the check is in reach.** *Wired in* and *reachable* are different properties: verify that the directory the check lives in is inside the scope the invoked command actually traverses. A guard outside the gate's reach is not a weaker guard, it is an absent one.

**Promoted when** a second session or second person edits the bundle in the same week, or an entry goes stale without anyone noticing, or you catch yourself depending on a property review cannot see.

## Tier 3 — registers, research, and ratchets

Everything here exists because a bundle got big enough that *absence* became misleading. None of it pays for itself before then.

- **A decisions register** plus an index gated against it in both directions — see [Optional types for larger bundles](FORMAT.md#optional-types-for-larger-bundles).
- **`research/`** for investigations nobody has ruled on, kept out of `docs/specs/` and `docs/plans/` so it borrows no authority.
- **`## Verification owed`** wherever authors cannot run the code they document, with an owner who can actually run the command named.
- **A ratchet on the operating contract**, since it is the highest read-multiplier file and the one with no natural budget — see [The always-read file above the indexes](FORMAT.md#the-always-read-file-above-the-indexes).
- **Graphify** for structural code questions, behind a `.graphifyignore` privacy fence excluding secrets, databases, exports, backups, `.claude/`, dependencies, and build artifacts. Keep extraction and LLM-based relabeling as separate commands:

  ```bash
  PATH="$HOME/.local/bin:$PATH" graphify update .
  ```

- **External views** — an idempotent `scripts/setup_vault_links.sh` linking memory, agents, and docs into an Obsidian vault and into the agent harness. It must refuse to replace real directories or unrelated symlinks. See [Tooling](TOOLING.md).
- **A stop hook** prompting for the [seven-point audit](METHODOLOGY.md#seven-point-delivery-audit), which may remind but must never fabricate updates.

CI can additionally check frontmatter validity, `pcs_version`, citation coverage, graph freshness, and privacy exclusions — none of which the linter implements, and all of which review genuinely can catch.

**Promoted when** more than one author — human or agent — writes to the bundle, or some authors cannot execute what they document, or a decision's absence from an index would mislead a reader rather than merely inconvenience them.

---

## First use, at any tier

1. Read the operating contract.
2. Read `.claude/memory/index.md` and the project memos it routes to.
3. Open the relevant learning index and referenced concepts, if the bundle has them yet.
4. Use Graphify for structure and PCS for project history.
5. Ship every context delta with the corresponding change.

## Maintaining it

At delivery boundaries: archive shipped or stale memos, transfer durable outcomes to canonical docs, rebuild stale graphs, and supersede contradicted knowledge with dated evidence rather than silently deleting history. Add optional `log.md` files only when exporting a bundle without Git history.

Demotion is legitimate and rarely considered. A domain index that has not been opened in months is a candidate for folding back into its hub; a directory whose last two leaves were archived can go. The tiers describe pressure, not achievement, and pressure comes off as well as on.
