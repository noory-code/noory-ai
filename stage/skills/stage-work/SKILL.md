---
name: stage-work
description: Register a Stage work item before starting work. Use when beginning any change to governed files — plan the work, confirm scope with the human, then create the item and its active.md row. Registering first is required: governed writes are denied without an open work item whose scope covers them.
---

# Stage Work Registration

Register work BEFORE modifying governed files. The registration gate denies a governed write when
no open (`active`/`review`/`blocked`) work item has a `scope` covering it. Registering mid-task
leaves early commits ungated (R-00000001's learning).

`.stage/` itself is not governed source, so the item file and `active.md` are free to create.

## Find the purpose first

Before writing the item, locate the real purpose in the upstream SSOT (initiative / epic / plan
doc). Do not guess. If the purpose answers an open question, the question may be unnecessary.

## Draft the item

Copy `present/work/items/_template.md` to `present/work/items/W-NNNNNNNN.md` (next free number) and
fill:

- `id`, `title` — the outcome, not the steps.
- `kind` — the project's work vocabulary (`feature`, `fix`, `chore`, `documentation`, …). Each
  kind's `passed` criterion lives in `operations/verification.md`.
- `venue` — the execution surface that should carry it out (advisory routing hint; see
  `stage-handoff`).
- `scope` — the paths this work may modify. The registration gate matches writes against these,
  so list every governed subtree you will touch. `*` authorizes anything (use sparingly).
- `## Purpose`, `## Scope`, `## Success criteria` — concrete and checkable.

## Confirm, then register

1. Show the human the purpose, scope, and success criteria. Get confirmation before executing —
   this is the one human checkpoint in the flow.
2. Add a row to `present/work/active.md`:
   `| W-NNNNNNNN | <kind> | <venue> | <purpose> | active | <owner> | [items/W-NNNNNNNN.md](items/W-NNNNNNNN.md) |`
3. Verify: `python3 stage/scripts/audit_stage.py --project-root <project-root>` (expect errors=0).

## Then work

Make small, verifiable changes within `scope`. When the work reaches a completion candidate, run
`stage-retrospective` to close it, and `stage-archive` to drain it from the review queue.
