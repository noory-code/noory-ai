# Backlog Items

This directory owns the SSOT of individual backlog items.

Backlog items cover every kind of work — planning, design, development, QA, operations, and anything else the project does.

## Rules

- One backlog item has one file.
- Filenames use the form `B-00000001-short-title.md`.
- `index.md` never duplicates item content; it holds only links and status.
- Items form a hierarchy through the frontmatter `parent` field. Large work stays classifiable by splitting into child items instead of growing one flat list.
- An item selected for execution is realized by a work item: set `realized_by` to the `W-*` ID, and that work item's `source` points back here. A `selected` item without `realized_by` is an audit warning.
- The reason for not doing something is recorded in the item file and, when needed, in `past/decisions/`.
