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
in the active topology's planned-work location, moved to its current-work location when work
starts, and archived when closed. The lifecycle CLIs read `.stage/settings.json` and select the
schema-v3 or schema-v4 paths; never select those paths manually. Two flows create work:

- **Capture for later**: `register_work.py --backlog --title "..." --kind <kind> --scope ""` —
  a planned card (`status: captured`) in the active topology's planned index. No venue/split
  checks run during capture.
- **Start now**: the flow below (direct current registration), or start an existing planned card
  with `python3 stage/scripts/start_work.py --project-root <root> W-NNNNNNNN --scope "..."` — the
  mover sets `active`, requires scope, derives the venue, and enforces the split/exception
  contract at that moment. Never hand-move the file.

## Ask the milestone question conditionally

Before confirming registration, run:

```text
python3 stage/skills/stage-work/register_work.py --project-root <root> --count-open-milestones
```

- If the command prints `0`, do not ask a milestone question and omit `--milestone`.
- If the command prints an integer greater than `0`, ask exactly: "does this belong to a
  milestone?" If the human selects one milestone, pass its single `M-NNNNNNNN` id through
  `--milestone`. If the human answers no, omit `--milestone`.
- Never pass more than one milestone id. `milestone:` cardinality is `0..1`.

The C5 detector returns `0` until C6 supplies the pursuit/closure decision-chain evaluator. A
milestone record without a proven open pursuit never triggers the question.

## Draft the item

Prepare the inputs for `register_work.py`; the CLI selects the topology template, allocates the
next free number, writes the card, and updates the owning index:

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
- `milestone` — include one `M-NNNNNNNN` only when the conditional question above was asked and
  the human selected that milestone. It is inert until C6 lands roadmap semantics.
- `## Purpose`, `## Scope`, `## Success criteria` — concrete and checkable.

## Confirm, then register

1. Show the human the purpose, scope, and success criteria. Get confirmation before executing —
   this is the one human checkpoint in the flow.
2. Run `register_work.py` with the confirmed values. The CLI writes the card and the active index
   row in the topology selected by `.stage/settings.json`.
3. Verify: `python3 stage/scripts/audit_stage.py --project-root <project-root>` (expect errors=0).

## Then work

Make small, verifiable changes within `scope`. When the work reaches a completion candidate, run
`stage-retrospective` to close it, and `stage-archive` to drain it from the review queue.
