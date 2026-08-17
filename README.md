# Project Context System

The Project Context System (PCS) is a repository-native knowledge format for preserving project state, decisions, feedback, and reusable lessons across LLM sessions. It combines Markdown, YAML frontmatter, Obsidian wikilinks, Git, and Graphify.

## Goals

- Give agents a small, reliable starting context.
- Preserve rationale without copying canonical product documentation.
- Turn task-specific discoveries into reusable lessons.
- Keep knowledge portable, reviewable, and version-controlled.
- Separate project history from code-structure analysis.
- Cost almost nothing on a small project and stay navigable on a large one.

## Repository layout

```text
project/
├── CLAUDE.md or AGENTS.md
├── docs/
│   ├── specs/
│   ├── plans/
│   ├── runbooks/
│   └── reference/
├── .claude/
│   ├── agents/
│   ├── hooks/
│   └── memory/                  # PCS bundle root
│       ├── index.md             # declares pcs_version
│       ├── log.md               # optional portable history
│       ├── project/index.md
│       ├── feedback/index.md
│       ├── learnings/index.md
│       ├── references/index.md
│       └── archive/index.md
├── graphify-out/
├── .graphifyignore
└── scripts/setup_vault_links.sh
```

`.claude/memory/` is the self-contained PCS bundle and unit of distribution. Repository docs and source remain outside the bundle and are identified through frontmatter resources. Directories provide stable categories, lowercase `index.md` files provide progressive disclosure, Obsidian wikilinks provide relationships, and Git provides chronology, attribution, review, and rollback.

**That is a mature bundle, not a starting point.** A new one is two files — the operating contract and a single `index.md` — and grows a directory only when a symptom earns it. Empty indexes in unused directories cost real context and teach an agent the bundle is bigger than it is. See [Tiers at a glance](ADOPTION.md#tiers-at-a-glance) for what to add and what promotes you to it.

## Knowledge layers

1. **Operating contract** — `CLAUDE.md` or `AGENTS.md` defines behavior, tools, quality gates, and update obligations.
2. **Live memory** — the root index and project memos summarize active state and route retrieval.
3. **Durable knowledge** — feedback, learnings, and references preserve reusable rules and evidence.
4. **Canonical documentation** — specs, plans, runbooks, and reference docs remain authoritative for product behavior.
5. **Code graph** — Graphify answers structural code questions without replacing project history.

Each layer costs maintenance in proportion to how much it restates. Layers that hold original content stay true on their own; layers that hold a restatement of another layer need a link, a derivation, or a check to keep them honest. A bundle that adds a layer should say what makes that layer fail loudly when it diverges — see [Original content and restatement](FORMAT.md#original-content-and-restatement).

## Relationship to OKF

PCS uses the same interoperable core ideas as Google's Open Knowledge Format: one Markdown file per concept, YAML frontmatter with a required `type`, a declared format version, reserved lowercase `index.md` and optional `log.md`, first-class references, UTF-8 content, and progressive disclosure. PCS uses `pcs_version` rather than `okf_version` and deliberately retains Obsidian wikilinks for internal relationships.

## Read next

- [Format and lifecycle](FORMAT.md)
- [Methodology](METHODOLOGY.md)
- [Tooling](TOOLING.md)
- [Adoption guide](ADOPTION.md)
- [Documentation index](index.md)
