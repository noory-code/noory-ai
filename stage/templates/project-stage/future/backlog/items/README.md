# Planned Work Cards

This directory owns the SSOT of planned work cards — `W-*` work items that have not started yet.

A work card is ONE artifact across its whole life: it is captured here, physically moves to
`present/work/items/` when work starts (`scripts/start_work.py`), and rests in
`past/work/archive/items/` when closed — like a card moving across a board. Planned cards cover
every kind of work — planning, design, development, QA, operations, and anything else the
project does.

## Rules

- One planned card has one file, named `W-00000001.md` (an optional `-short-title` suffix is
  allowed).
- Card ids are allocated from the same `W-*` counter as present work; an id never appears in two
  lifecycle locations at once.
- `index.md` never duplicates card content; it holds only order, status, and links.
- Cards form a hierarchy through the frontmatter `parent` field, which may name a planned or an
  already-started card.
- Planned statuses: `captured`, `triaged`, `ready`, `selected`, `deferred`, `rejected`. Starting
  work is a MOVE, not a status edit here: `python3 stage/scripts/start_work.py --project-root .
  W-00000001 --scope "..."` relocates the card to `present/work/items/`, sets `active`, requires
  the scope declaration, and enforces the venue/split contract at that moment.
- Capture new cards with `register_work.py --backlog --title "..." --kind <kind> --scope ""` or
  by copying `_template.md`.
- The reason for not doing something (`rejected`) is recorded in the card and, when needed, in
  `past/decisions/`.
