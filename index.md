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

- [`scripts/pcs_lint.py`](scripts/pcs_lint.py) — size, shape, frontmatter-parse, link-resolution, index-coverage and supersession checks for a bundle, plus opt-in `--admission`; vendor it and hang it off an existing lint target
- [`scripts/check_doc_links.py`](scripts/check_doc_links.py) — dead file and heading-anchor links between a repository's own documents, for the guides that sit outside a bundle
- Both carry `--selftest`, and both run it on the same target as the check itself — see [Designing a check that survives](TOOLING.md#designing-a-check-that-survives)
- [`.github/workflows/lint.yml`](.github/workflows/lint.yml) — what runs `make lint` when nobody remembers to; see [Making it run without you](ADOPTION.md#making-it-run-without-you)

## Field reports

Measurements from bundles running this format. A report is evidence, not spec; each carries the disposition of its items, recorded when it merged.

- [`budgets_rewritten`, 2026-08-17](field-reports/2026-08-17-budgets-rewritten-field-report.md) — ten days against a real corpus: the two `FORMAT.md` claims it falsified, what the checks found once they existed, and why one proposed check was declined
- [`budgets_rewritten`, 2026-09-13](field-reports/2026-09-13-budgets-rewritten-field-report.md) — 27 further days and 950 documents: what a corpus is actually read by, the two pieces of guidance it contradicts, and a defect in this repository's own anchor checker

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
