---
name: stage-work
description: Register a Stage work item before you touch governed files. Use this whenever you start a task, feature, fix, refactor, or doc change in a project that has a `.stage/` harness — plan the work, confirm scope with the human, then create the item and its `active.md` row. Registering first is not optional: the hook denies governed writes when no open work item's `scope` covers them, so reach for this at the very start of any Stage work, even if the user just says "let's build X" without mentioning Stage.
---

# Stage Work Registration

Register work BEFORE modifying governed files. The registration gate denies a governed write when
no open (`active`/`review`/`blocked`) work item has a `scope` covering it. Registering mid-task
leaves early commits ungated (R-00000001's learning).

`.stage/` itself is not governed source, so the item file and `active.md` are free to create.

## Judge the scale first

Start with: **"How large is this work?"** Do not start by offering to create one card.

- `epic` — several stories must combine to deliver the outcome.
- `story` — one coherent outcome, either top-level or inside an epic.
- `action` — one indivisible execution step inside a story.

An action can never be top-level. If no story exists, establish the story first, then register the
action beneath it. The folder path is the hierarchy SSOT; never add or maintain a `parent:` field.

After judging scale, locate the real purpose in the upstream SSOT (initiative / epic / plan doc).
Do not guess. If the purpose answers an open question, the question may be unnecessary.

## One hierarchy, three lifecycle columns

A work record is one `W-*` artifact for its whole life (DE-00000007). An epic directory or
independent story directory is one top-level lifecycle unit: captured in `work/planned/`, moved
whole to `work/current/` when work starts, and archived whole under `official/work/archive/` when
closed. The lifecycle CLIs derive these paths; never select them manually. Two flows create work:

- **Capture for later**: `register_work.py --backlog --scale <scale> --title "..." --kind <kind>
  --scope "<this record's paths>" [--parent W-NNNNNNNN]` — a planned record (`status: captured`) in
  `work/planned/` and its index. No venue/split checks run during capture.
- **Start now**: the flow below (direct current registration), or start an existing planned card
  with `python3 stage/scripts/start_work.py --project-root <root> W-NNNNNNNN --scope "..."` — the
  mover moves the top-level directory, sets `active`, requires scope, derives the venue, and
  enforces the split/exception contract at that moment. Each descendant keeps the scope declared
  at capture; the top-level `--scope` does not widen its actions. A deferred descendant blocks the
  start instead of silently becoming active, and rejection propagates through that rejected
  branch. Never hand-move a file or directory.

Use `--parent` only as a placement input:

- `--scale epic` has no parent.
- A top-level `--scale story` has no parent; a story inside an epic passes the epic `W-*`.
- `--scale action` must pass its story `W-*`.

The CLI resolves that record and writes the new record inside its folder. It never writes
`parent:` frontmatter.

## Ask the milestone question for top-level work

Do not ask a milestone question for a nested story or action. Before confirming a top-level epic
or story, run:

```text
python3 stage/skills/stage-work/register_work.py --project-root <root> --count-open-milestones
```

- If the command prints `0`, ask exactly: "there is no open milestone; create one before
  registering this top-level item?" If the human answers yes, use `stage-roadmap` to create and
  begin pursuit of the milestone before registration. If the human answers no, omit
  `--milestone`.
- If the command prints an integer greater than `0`, ask exactly: "does this belong to a
  milestone?" If the human selects one milestone, pass its single `M-NNNNNNNN` id through
  `--milestone`. If the human answers no, omit `--milestone`.
- Never pass more than one milestone id. `milestone:` cardinality is `0..1`.

The detector counts only milestones whose valid decision chain has an effective pursuit head
and no effective closure. A planned milestone, an invalid chain, or a milestone with no decision
record never triggers the question.

## Draft the item

Prepare the inputs for `register_work.py`; the CLI selects the registry template, allocates the
next free number, writes the card, and updates the owning index:

- `id`, `title` — name the work: what this card does, as an action. A reader who sees only the
  title must be able to tell it is work to carry out, not a fact already true. Write "state what
  `decision_refs` holds in the docs", never "the docs state what `decision_refs` holds" — the
  second reads as a settled fact and hides that anything is pending. Keep it to the work itself,
  not its steps; the outcome and the value belong in `## Purpose` and `## User value`.
- `kind` — the project's work vocabulary (`feature`, `fix`, `chore`, `documentation`, …). Each
  kind's `passed` criterion lives in the project's `.stage/operations/verification.md`.
- `venue` — the execution surface that should carry it out. When `settings.json` declares
  `venue_routing` (`kind -> venue`), derive the venue from it instead of asking the human;
  `register_work.py` does this automatically when `--venue` is omitted. A venue that contradicts
  the policy is REFUSED unless `--decision <DE-id>` names a decided/promoted decision record
  declaring `authorizes: venue_exception` (record the decision first, then register; the audit
  enforces the same contract plus the `work_item` back-link). A kind routed to the reserved
  value `split` is mixed by definition: register a planning/design item and an implementation
  item as separate hierarchy records instead of one ambiguous item (see `stage-handoff`); a
  deliberate single item needs the same exception decision.
- `scope` — the paths this work may modify. The registration gate matches writes against these,
  so list every governed subtree you will touch. `*` authorizes anything (use sparingly).
- `scale` and placement — always pass `--scale`. Pass `--parent` only for a story inside an epic
  or an action inside a story.
- `milestone` — include one `M-NNNNNNNN` only when the conditional question above was asked and
  the human selected that active milestone.
- `decision_refs` — leave it empty at registration. It names the decision records this item
  **settles**, and an item settles none before it runs. An item that exists to carry out a
  decision another card already settled links that record in its body, never here: the audit
  requires every referenced record to name this item back, and that one-to-one link is what
  identifies which single item a venue exception authorized.
- The body must answer four questions, each in its own section. A card that leaves any of them
  empty is not a work item — it is a note, and whoever picks it up will invent the missing answer:

  | Question | Section |
  |---|---|
  | 무엇을 하는가 | `## Actions` — the work itself, and `## Scope` for the paths it may touch |
  | 왜 지금 하는가 | `## Purpose` — what is wrong today, with the evidence that it is wrong |
  | 무엇을 이루려는가 | `## User value` — what someone can do afterwards that they cannot do now |
  | 언제 끝나는가 | `## Success criteria` — checkable, and at least one of them names a result a person experiences, not only a structure that exists |

  Capturing a card for later (`--backlog`) does not exempt it. A planned card with an empty body
  cannot be started: the driver refuses an item whose acceptance command is missing, and a human
  reading it has to redo the thinking that was skipped.

- Write the card so it stands on its own. **An identifier is not a meaning.** "Carry what
  DE-00000046 decided into the docs" tells a reader nothing until they open two other files; write
  what was decided, then cite the record. The same holds for audit codes, field names, and sibling
  cards: say what the thing is and why it matters, and put the identifier after that as the place
  to verify it.

- Leave out what the card does not need. Progress notes, tool output, and the order you happened to
  do things belong in the shared work log; the card carries the work, its reason, its goal, and its
  finish line. A card that records every step buries the four answers a reader came for.

## Confirm, then register

1. Show the human the purpose, scope, and success criteria. Get confirmation before executing —
   this is the one human checkpoint in the flow.
2. Run `register_work.py` with the confirmed values. The CLI writes the card and the active index
   row in the topology selected by `.stage/settings.json`.
3. Verify: `python3 stage/scripts/audit_stage.py --project-root <project-root>` (expect errors=0).

## Then work

Make small, verifiable changes within `scope`. When the work reaches a completion candidate, run
`stage-retrospective` to close it, and `stage-archive` to drain it from the review queue.

If an action exhausts its attempts, do not reactivate or rerun it. Read the pending decision and
the failed-action evidence on its blocked story, revise the story decomposition, then register
replacement actions through the same placement rules. Resume only after the story's decision and
status have been explicitly resolved.
