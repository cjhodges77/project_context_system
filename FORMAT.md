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

`type` is required for routing. `name` is a stable identity. `title`, `description`, `resource`, `tags`, and `timestamp` support display, retrieval, provenance, categorization, and freshness. Fields other than `type` are optional. Consumers must preserve unknown fields and tolerate unknown `type` values.

## Concept types

### `project/`

Active workstream state: objective, decisions, shipped scope, open questions, living-document deltas, and related concepts. Move shipped or stale memos to `archive/` after durable outcomes reach canonical docs.

### `feedback/`

Persistent behavioral rules derived from user instruction, review, retrospectives, or observed failure. Include the rule, rationale, application, and enforcement.

### `learnings/`

Reusable technical lessons with symptom, root cause, evidence, fix, generalized rule, and verification. Keep one learning per file and one concise entry in `learnings/index.md`.

### `references/`

Curated external sources and provenance needed to understand bundle claims. A reference concept records the source's canonical URI in `resource`, its relevance, and any scope or reliability notes.

### `archive/`

Searchable historical state that is no longer part of the active retrieval path. Archive rather than silently deleting useful rationale.

## Reserved files

### `index.md`

The root `index.md` is the starting map and declares `pcs_version`. Any bundle directory may contain a lowercase `index.md`. Keep entries concise and use Obsidian wikilinks to concepts. A root index should route to active projects, feedback, learning domains, references, and archive guidance.

### `log.md`

A lowercase `log.md` is optional. Use it when distributing a bundle without Git history. Group entries under ISO `YYYY-MM-DD` headings, newest first. Git remains the primary history layer.

## Links and identity

Use Obsidian wikilinks for all relationships inside the PCS bundle, including concept-to-concept, index-to-concept, and supersession links. Prefer stable `name` values as link identities. Repository resources outside the bundle may be identified by `resource` or written as literal paths.

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

## Conformance

A PCS bundle is structurally conformant when:

1. `.claude/memory/index.md` contains a non-empty `pcs_version`.
2. Every Markdown file except `index.md` and `log.md` begins with parseable YAML frontmatter containing a non-empty `type`.
3. Reserved `index.md` and `log.md` files follow the structures above.
4. Internal relationships use resolvable Obsidian wikilinks.
5. Consumers preserve unknown frontmatter fields and tolerate unknown `type` values.
6. Every document is UTF-8.

## Content quality rules

Keep summaries short, evidence concrete, names stable, timestamps explicit, and canonical docs authoritative. Do not duplicate secrets, transient logs, large generated output, or source-code explanations that Graphify can retrieve.
