# Vocabulary

This document owns the index and core summary of project terms.

The detailed SSOT of each term lives in `vocabulary/`.

| Term | Meaning |
|---|---|
| Past | Officially approved artifact status. |
| Present | In-progress or provisional artifact status. |
| Future | Planned or proposed artifact status. |
| Decision Point | A choice point where action is decided by principles and context. |
| Retrospective | The mandatory post-work review performed before official promotion. |
| Venue | The execution surface a work item is routed to. This project's venue meanings are defined below. |

## Venues

A work item's `venue` names which execution surface should carry it out — the
routing signal a human reads to open the right window when more than one agent
or session works this project. This document owns only what each venue MEANS
(which responsibilities it carries). The machine-readable `kind -> venue`
routing map is owned by `settings.json` `venue_routing`: registration derives
each item's venue from it, and the audit enforces consistency (a
policy-contradicting venue needs a decision record with
`authorizes: venue_exception`; a kind mapped to the reserved value `split`
must register as separate design and implementation items with `parent`
lineage). Leave both empty if the project uses a single surface.

Describe this project's venues here, for example: a planning/design window
(e.g. `claude`) and an implementation/QA window (e.g. `codex`). Replace with
this project's own venue names — the harness fixes none.
