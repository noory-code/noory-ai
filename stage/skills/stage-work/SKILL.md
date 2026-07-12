---
name: stage-work
description: Register a Stage work item before you touch governed files. Use this whenever you start a task, feature, fix, refactor, or doc change in a project that has a `.stage/` harness — plan the work, confirm scope with the human, then create the item and its `active.md` row. Registering first is not optional: the hook denies governed writes when no open work item's `scope` covers them, so reach for this at the very start of any Stage work, even if the user just says "let's build X" without mentioning Stage.
---

# Stage Work Registration

Register work BEFORE modifying governed files. The registration gate denies a governed write when
no open (`active`/`review`/`blocked`) work item has a `scope` covering it. Registering mid-task
leaves early commits ungated (R-00000001's learning).

`.stage/` itself is not governed source, so the item file and `active.md` are free to create.

## Find the purpose first

Before writing the item, locate the real purpose in the upstream SSOT (initiative / epic / plan
doc). Do not guess. If the purpose answers an open question, the question may be unnecessary.

## One card, three columns

A work card is one `W-*` artifact for its whole life (DE-00000007): captured as a planned card
in `future/backlog/items/`, moved to `present/work/items/` when work starts, archived when
closed. Two flows create work:

- **Capture for later**: `register_work.py --backlog --title "..." --kind <kind> --scope ""` —
  a planned card (`status: captured`), indexed in `future/backlog/index.md`. No venue/split
  checks yet.
- **Start now**: the flow below (direct registration into present), or start an existing planned
  card with `python3 stage/scripts/start_work.py --project-root <root> W-NNNNNNNN --scope "..."`
  — the mover sets `active`, requires scope, derives the venue, and enforces the split/exception
  contract at that moment. Never hand-move the file.

## Draft the item

Copy `present/work/items/_template.md` to `present/work/items/W-NNNNNNNN.md` (next free number) and
fill:

- `id`, `title` — the outcome, not the steps.
- `kind` — the project's work vocabulary (`feature`, `fix`, `chore`, `documentation`, …). Each
  kind's `passed` criterion lives in the project's `.stage/operations/verification.md`.
- `venue` — the execution surface that should carry it out. When `settings.json` declares
  `venue_routing` (`kind -> venue`), derive the venue from it instead of asking the human;
  `register_work.py` does this automatically when `--venue` is omitted. A venue that contradicts
  the policy is REFUSED unless `--decision <DE-id>` names a decided/promoted decision record
  declaring `authorizes: venue_exception` (record the decision first, then register; the audit
  enforces the same contract plus the `work_item` back-link). A kind routed to the reserved
  value `split` is mixed by definition: register a planning/design item and an implementation
  item with `parent` lineage instead of one ambiguous item (see `stage-handoff`); a deliberate
  single item needs the same exception decision.
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
