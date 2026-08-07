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

- index entries containing a number, a currency amount, a commit SHA, or a status word — each is a near-certain sign that a summary has been written where a pointer belongs;
- computable figures in prose — byte counts, file sizes, test counts, error counts, entry totals — which should name the command that derives them instead;
- status stated anywhere but the owning project memo's header.

These are cheap regular expressions and much closer proxies for the real rules than character count. Prefer them to a longer size budget.

Automation should report drift, not rewrite human-authored knowledge silently.
