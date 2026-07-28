# Planned Work Cards

This directory owns the SSOT of planned work hierarchies that have not started yet.

One top-level item is either an epic directory or an independent story directory. It is captured
here, moves as one directory to `work/current/` when work starts, and rests in
`official/work/archive/items/` when closed. Folder placement is the hierarchy SSOT.

## Rules

- An epic directory contains `_epic.md` and story directories. A story directory contains
  `_story.md` and action cards. An action cannot live directly in this directory.
- Card ids are allocated from the same `W-*` counter as current work; an id never appears in two
  lifecycle locations at once.
- `index.md` never duplicates card content; it holds only order, status, and links.
- The directory path is the only hierarchy fact; work frontmatter has no `parent` field.
- Planned statuses: `captured`, `triaged`, `ready`, `selected`, `deferred`, `rejected`. Starting
  work is a MOVE of the top-level directory, not a status edit here.
- Copy `_epic.md`, `_story.md`, or `_template.md` for an epic, story, or action respectively.
- The reason for not doing something (`rejected`) is recorded in the card and, when needed, in
  `official/decisions/`.
