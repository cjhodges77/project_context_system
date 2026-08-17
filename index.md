# Project Context System documentation

## Guides

- [Overview](README.md)
- [Format and lifecycle](FORMAT.md)
- [Methodology](METHODOLOGY.md)
- [Tooling](TOOLING.md)
- [Adoption guide](ADOPTION.md)

## Templates

- [Bundle index](templates/index.template.md)
- [Project memo](templates/project_memo.template.md)
- [Learning note](templates/learning.template.md)
- [Feedback note](templates/feedback.template.md)
- [Reference concept](templates/reference.template.md)
- [Domain sub-index](templates/domain_index.template.md)

## Checks

- [`scripts/pcs_lint.py`](scripts/pcs_lint.py) — size and shape checks for a bundle; vendor it and hang it off an existing lint target

## Field reports

Measurements from bundles running this format. Findings, not rulings — each says what was observed and whether it generalises.

- [`budgets_rewritten`, 2026-08-17](feedback/2026-08-17-budgets-rewritten-field-report.md) — two `FORMAT.md` claims a real corpus falsified (`name:` is not a link identity; per-domain hub counts drift), the ratchet as a second way to bind a convention forward, and four concepts the format has no home for

## Bundle concept types

| Type | Conventional path | Purpose |
| --- | --- | --- |
| Root index | `index.md` | Declares `pcs_version` and routes retrieval |
| Project memo | `project/project_<slug>.md` | Active workstream state and decisions |
| Feedback | `feedback/<slug>.md` | Durable behavioral rule |
| Learning | `learnings/<slug>.md` | Reusable technical lesson |
| Reference | `references/<slug>.md` | Curated external source and provenance |
| Archived memo | `archive/project_<slug>.md` | Shipped or stale state retained for search |
| Portable log | `log.md` | Optional chronology when Git is unavailable |
