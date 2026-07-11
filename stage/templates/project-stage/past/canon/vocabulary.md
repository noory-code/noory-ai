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
| Venue | The execution surface a work item is routed to. This project's venues and routing are defined below. |

## Venues

A work item's `venue` names which execution surface should carry it out — the
routing hint a human reads to open the right window when more than one agent or
session works this project. Define this project's venues and the `kind -> venue`
routing here; leave it empty if the project uses a single surface.

The table below is an example for a two-surface setup (a planning window and an
implementation window). Replace the venue names and routing with this project's
own.

| `kind` | `venue` (example) |
|---|---|
| planning, design | `claude` |
| development, qa, ops | `codex` |
