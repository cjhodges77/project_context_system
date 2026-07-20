# Adoption guide

Use this sequence to add the Project Context System to a repository.

## 1. Create the structure

```bash
mkdir -p .claude/memory/{project,feedback,learnings,references,archive}
mkdir -p .claude/{agents,hooks}
mkdir -p docs/{specs,plans,runbooks,reference}
touch .claude/memory/{project,feedback,learnings,references,archive}/index.md
```

## 2. Add the operating contract

Create `CLAUDE.md` or `AGENTS.md` at the root. Define tool routing, memory layout, context-update requirements, quality gates, trust-boundary rules, and any agent roles.

## 3. Add the root index

Create `.claude/memory/index.md` from [the index template](templates/index.template.md). Declare `pcs_version`, then add concise sections for active projects, feedback, learning domains, references, and archive guidance. All relationships inside the bundle use Obsidian wikilinks.

## 4. Add the first project memo

Create `.claude/memory/project/project_<slug>.md` from [the project memo template](templates/project_memo.template.md), then add one wikilinked line for it to the root `index.md`.

## 5. Add durable knowledge

Use the [feedback template](templates/feedback.template.md) for behavioral rules, the [learning template](templates/learning.template.md) for reusable discoveries, and the [reference template](templates/reference.template.md) for curated external sources. Add each concept to its directory's `index.md`. Cite external claims in a `## Citations` section.

## 6. Link external views

Add an idempotent `scripts/setup_vault_links.sh` that links repository memory, agents, and docs into an Obsidian vault and links memory into the agent harness. It must refuse to replace real directories or unrelated symlinks.

## 7. Configure Graphify

Create `.graphifyignore` as a privacy fence. At minimum exclude secrets, databases, exports, backups, `.claude/`, dependencies, and build artifacts. Then run the initial extraction:

```bash
PATH="$HOME/.local/bin:$PATH" graphify update .
```

Keep extraction and LLM-based relabeling as separate commands.

## 8. Add enforcement

Optionally add a stop hook that prompts for the seven-point audit in [METHODOLOGY.md](METHODOLOGY.md). CI can check `pcs_version`, frontmatter, duplicate names, Obsidian links, index coverage, citations, graph freshness, and privacy exclusions.

## 9. First use

1. Read the operating contract.
2. Read `.claude/memory/index.md` and relevant project memos.
3. Open the relevant learning-index domain and referenced concepts.
4. Use Graphify for structure and PCS for project history.
5. Ship every context delta with the corresponding change.

## 10. Maintain it

At delivery boundaries, archive shipped or stale memos, transfer durable outcomes to canonical docs, rebuild stale graphs, and supersede contradicted knowledge with dated evidence rather than silently deleting history. Add optional `log.md` files only when exporting a bundle without Git history.
