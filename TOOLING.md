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

## Designing a check that survives

A check is worth building only if it is still running in a month. Four properties decide that, and each has a documented failure behind it.

- **Green on a healthy tree.** A check that is red when nothing is wrong gets bypassed, and a bypassed check is worse than none — it reads as coverage while enforcing nothing. Never gate on a condition a healthy bundle legitimately carries, such as a plan with open items or a workstream still in flight.
- **Bind new conventions going forward.** Applying a new rule to an existing corpus reddens every document written before it, which is the fastest route to the bypass above. Scope the check by date and let the pre-convention corpus stay green; date-prefixed filenames make that cutoff mechanical rather than a judgement call.
- **Hang it off a command people already run.** Make it a dependency of the lint or test entry point, not a standalone target. A target nobody invokes is a rule that is still enforced only by memory, with the added cost of looking enforced.
- **State the limit inside the check.** Say what a green run does *not* prove — that it asserts form and never truth, or that it catches copy-paste but not reimplementation. A check whose limits are unwritten gets trusted for things it never verified.

Automation should report drift, not rewrite human-authored knowledge silently.
