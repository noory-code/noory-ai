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
| Venue | The execution surface that carries out a work item. This project's venues: `claude` (planning, design, documentation, decisions) and `codex` (implementation, fixes, tests, QA, operations, chores). The machine `kind -> venue` routing map is owned by `settings.json` `venue_routing` and enforced by the audit; `feature` is mixed by definition and splits into design/implementation items with `parent` lineage; exceptions require a decided decision record declaring `authorizes: venue_exception`. |
