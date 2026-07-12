# Backlog Index

This document owns the current index of the backlog.

Backlog item bodies live in `items/`. This document manages only order, status, and links.

## Current backlog

| ID | Title | Kind | Status | Priority | Parent | Item |
|---|---|---|---|---|---|---|
| W-00000021 | archive_work review-row removal misses hand-written rows | fix | triaged | harness integrity | | [W-00000021](items/W-00000021.md) |
| W-00000022 | close_work replaces the Verification section | fix | triaged | harness integrity | | [W-00000022](items/W-00000022.md) |
| W-00000023 | archive retrospective overwritten on id collision | fix | triaged | harness integrity | | [W-00000023](items/W-00000023.md) |
| W-00000024 | no global uniqueness guard for retrospective ids | fix | triaged | harness integrity | | [W-00000024](items/W-00000024.md) |
| W-00000025 | Close/archive ordering guard: refuse closure with uncommitted scope changes | development | captured | high |  | [items/W-00000025.md](items/W-00000025.md) |
| W-00000026 | settings.jsonc: commented project settings with tolerant loader | development | captured |  |  | [items/W-00000026.md](items/W-00000026.md) |
| W-00000027 | register_work --backlog appends index rows outside the table | fix | captured | high |  | [items/W-00000027.md](items/W-00000027.md) |

## Status values

- `captured`: captured but not yet organized.
- `triaged`: purpose and impact confirmed.
- `ready`: concrete enough to be an execution candidate.
- `selected`: selected as current or next work.
- `deferred`: on hold.
- `rejected`: decided not to do.
