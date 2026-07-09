# Work Items

This directory owns the SSOT of in-progress work items.

Work items cover every kind of work — planning, design, development, QA, operations, and anything else the project does. A work item is not a code change; it is a unit of accountable work.

## Rules

- One work item has one file.
- `active.md` and `review.md` are current views and never duplicate bodies.
- When work becomes a completion candidate, link its verification, retrospective, and promotion decision.
- Hooks use each work file's frontmatter as the status SSOT.
- When work no longer belongs to the current flow, set `status: archived` and move it to `past/work/archive/items/`.

## Status fields

The document SSOT of the work status enum is `operations/artifacts.md`.

- `kind`: what kind of work this is (for example `planning`, `design`, `development`, `qa`, `ops`). The project defines its own taxonomy in `past/canon/vocabulary.md`.
- `parent`: optional ID of the parent work item. Hierarchy keeps large work classifiable — a parent is not complete while a child is open.
- `scope`: paths this work owns. Separate multiple entries with commas. An empty value owns no path. Declare `*` only for a truly global scope.
- `promotes`: `.stage/past/` paths this work may promote. Separate multiple entries with commas.
- `retrospective_ref`: the retrospective file ID or path linked when `retrospective: completed`.
- `decision_refs`: optional decision record IDs or paths in `present/work/decisions/`.
- `source`: optional backlog item ID this work realizes; the backlog item's `realized_by` points back.
