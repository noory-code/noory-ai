---
name: stage-work
description: Draw out what the human wants to achieve, then register a Stage work item before you touch governed files. Use this whenever you start a task, feature, fix, refactor, or doc change in a project that has a `.stage/` harness — ask until the purpose, the achievement it reaches, and the finish line are answered, agree on the work, and only then judge scale and create the item. Registering first is not optional: the hook denies governed writes when no work item is open, so reach for this at the very start of any Stage work, even if the user just says "let's build X" or "it doesn't work" without mentioning Stage.
---

# Stage Work Registration

Register work BEFORE modifying governed files. The registration gate denies a governed write when
no work item is open (`active`/`review`/`blocked`). Scope is an advisory signal: a write outside
the selected leaf's scope passes, and the hook tells the executor to report the boundary crossing.
Registering mid-task leaves early commits ungated (R-00000001's learning).

`.stage/` itself is not governed source, so the item file and `active.md` are free to create.

## Draw out the purpose before anything else

**Ask what the human wants to achieve, and keep asking until you can write three things without
inventing any of them:**

- **The one sentence** — what they want to achieve, not what is broken.
- **The larger achievement it reaches** — which milestone criterion moves, or none.
- **How they will know it is done** — a result they will experience.

Do not judge scale, name a kind, propose a card, or open a file before those three are answered.
Scale, kind, scope, and success criteria are all downstream: they only have answers once the
purpose is settled. Judging size first means sizing the visible breakage instead.

**One question is never enough.** The first answer names a symptom; the purpose surfaces after
several exchanges. Ask again, in a different direction, rather than accepting the first answer
and starting.

**The stopping rule is what you received, not the human's patience.** When any of the three is
still blank, you have not asked enough. When all three are answered, stop asking and proceed —
asking further past that point wastes the human's time.

Never fill a blank from repository records. Commits, open observations, and existing cards produce
a plausible purpose that is a repetition of what already exists, not what this human is trying to
achieve. **"It doesn't work" carries a purpose too** — something was being attempted; draw out
what, instead of taking the breakage story at face value.

An upstream SSOT (initiative, epic, plan doc) confirms a stated purpose; it does not supply one.
When none exists, ask — that is the case this procedure is for.

Confirm the three back to the human and get agreement that this is the work to do. Only then
continue.

## Judge the scale

With the purpose agreed, ask: **"How large is this work?"**

- `epic` — several stories must combine to deliver the outcome.
- `story` — one coherent outcome, either top-level or inside an epic.
- `action` — one indivisible execution step inside a story.

An action can never be top-level. If no story exists, establish the story first, then register the
action beneath it. The folder path is the hierarchy SSOT; never add or maintain a `parent:` field.

If the purpose answers an open question, the question may be unnecessary.

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
python3 stage/skills/stage-work/register_work.py --project-root <root> --list-open-milestones
```

- If the command prints `No open milestones.`, ask exactly: "there is no open milestone; create
  one before registering this top-level item?" If the human answers yes, use `stage-roadmap` to
  create and begin pursuit of the milestone before registration. If the human answers no, omit
  `--milestone`.
- If the command lists open milestones, show the command output, including each completion
  criterion, then ask exactly: "does this work move one of these milestone completion criteria?"
  If the human answers yes, ask them to select that milestone and pass its single `M-NNNNNNNN` id
  through `--milestone`. If the human answers no, omit `--milestone`.
- Never pass more than one milestone id. `milestone:` cardinality is `0..1`.

The listing includes only milestones whose valid decision chain has an effective pursuit head and
no effective closure. A planned milestone, an invalid chain, or a milestone with no decision record
never triggers the question.

## Count affected places before drafting

Before writing scope, risks, or success criteria, ask: **"Where can this change have an effect?"**
Answer by walking all four checks below. A place is a distinct entry path, actor, state transition,
responsibility, or observable result; a file name alone is not a place.

| Check | Question |
|---|---|
| Entry paths and actors | Who or what reaches this behavior, including people, automation, and each hierarchy level? |
| Lifecycle and state changes | When can the owned fact change, including create, update, close, archive, interruption, and recovery? |
| Replaced or removed responsibilities | What other job does the behavior being changed or removed perform? |
| Results, failures, and durable evidence | Where must the result, notice, failure, or evidence be visible and remain after the command or session ends? |

For each row, list concrete places and record the count. When the count is zero, name what was checked
and why it is unaffected; bare `none` is not evidence. Use the findings to correct the existing
`## Scope`, `## Risks`, and `## Success criteria` answers. Do not add a duplicate section to the
card.

Show this table during confirmation:

| Check | Count | Concrete places and effect | Checked but unaffected |
|---|---:|---|---|
| Entry paths and actors |  |  |  |
| Lifecycle and state changes |  |  |  |
| Replaced or removed responsibilities |  |  |  |
| Results, failures, and durable evidence |  |  |  |

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
- `scope` — the paths this work expects to modify. List every governed subtree known at
  registration time. The hook reports but does not block a needed write outside this list; the
  executor must report every such boundary crossing. `*` suppresses useful boundary signals, so
  use it sparingly.
- `scale` and placement — always pass `--scale`. Pass `--parent` only for a story inside an epic
  or an action inside a story.
- `milestone` — include one `M-NNNNNNNN` only when the conditional question above was asked and
  the human selected that active milestone.
- `decision_refs` — leave it empty at registration. It names the decision records this item
  **settles**, and an item settles none before it runs. An item that exists to carry out a
  decision another card already settled links that record in its body, never here: the audit
  requires every referenced record to name this item back, and that one-to-one link is what
  identifies which single item a venue exception authorized.
- Every scale asks for one `## Purpose` sentence, `## User value`, `## Scope`, `## Risks`,
  `## Success criteria`, and `## Next action`. Registration refuses `--purpose` when a `.`, `!`,
  or `?` sentence boundary is followed by more text; it does not impose a character limit.
  Lower levels name only their own contribution instead of repeating an ancestor's purpose.

  | Scale | Scale-specific sections |
  |---|---|
  | `epic` | `## Stories` — the stories that combine into the epic |
  | `story` | `## Actions` — the actions that combine into the story |
  | `action` | `## Source` and `## Dependencies` — what produced the indivisible step and what it waits for |

  A current card keeps those same questions and adds only the lifecycle sections that execution
  fills: `## Related truth`, `## Progress`, `## Verification`, `## Retrospective`, and
  `## Promotion decision`. Capturing a card for later (`--backlog`) does not exempt it. A card that
  leaves its questions empty is a note, and whoever picks it up will invent the missing answer.
  A planned card with an empty body cannot be started: the driver refuses an item whose acceptance
  command is missing, and a human reading it has to redo the thinking that was skipped.

- Store the smallest command that fails when this card's own result breaks — one test file, or one
  test name. A card that only changes documents can store the audit alone. If the command can fail
  for a reason unrelated to this card, it is still too wide.

  The driver re-runs the stored command on every round, so its cost is paid again each time a
  review sends the work back. The whole suite belongs at the finish instead: `close_work.py` runs
  the stored commands **and** every `--check` passed to it, so a narrow card still meets the full
  suite before it closes.

  This buys speed with lateness. A narrow command watches this card's result and nothing else, so
  a change that breaks something elsewhere passes every round and surfaces only at close — before
  the human commits, which is what makes the trade safe.

- Write the card so it stands on its own. **An identifier is not a meaning.** "Carry what
  DE-00000046 decided into the docs" tells a reader nothing until they open two other files; write
  what was decided, then cite the record. The same holds for audit codes, field names, and sibling
  cards: say what the thing is and why it matters, and put the identifier after that as the place
  to verify it.

- Leave out what the card does not need. Progress notes, tool output, and the order you happened to
  do things belong in the shared work log; the card carries the work, its reason, its goal, and its
  finish line. A card that records every step buries the four answers a reader came for.

## Cover included outcomes with success criteria

Before confirmation, list every outcome allowed by `## Scope` > `### Included`. An outcome is a
result the finished work permits or promises, not a path to edit or a task to perform. Pair each
outcome with at least one existing `## Success criteria` item that would prove it happened. One
criterion may prove more than one outcome, but a path-only scope entry needs no pair.

Show this table during confirmation:

| Included outcome | Success criterion that proves the outcome |
|---|---|
|  |  |

Do not confirm or register while any included outcome is unmatched. Add a criterion when the
outcome belongs to this item; otherwise remove or narrow the outcome in `### Included`.

## Confirm, then register

1. Show the human the affected-place count, included-outcome coverage, purpose, scope, and success
   criteria. Get confirmation before executing — this is the one human checkpoint in the flow.
2. Run `register_work.py` with the confirmed values. The CLI writes the card and the active index
   row in the topology selected by `.stage/settings.json`.
3. Verify: `python3 stage/scripts/audit_stage.py --project-root <project-root>` (expect errors=0).

## Then work

Make small, verifiable changes for the stated purpose. Use `scope` as the expected-path plan, and
do and report purpose-needed work that crosses it. When the work reaches a completion candidate,
run `stage-retrospective` to close it, and `stage-archive` to drain it from the review queue.

If an action exhausts its attempts, do not reactivate or rerun it. Read the pending decision and
the failed-action evidence on its blocked story, revise the story decomposition, then register
replacement actions through the same placement rules. Resume only after the story's decision and
status have been explicitly resolved.
