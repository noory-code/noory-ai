---
name: stage-retrospective
description: Perform the mandatory post-work Stage retrospective and confirm external completion, internal completion, principle application, and context updates before official promotion.
---

# Stage Retrospective

Use this skill after work reaches a completion candidate.

In a hierarchy, close and review each action before the next action runs. A story closes after all
its actions are terminal; an epic closes after all its stories are terminal. Closing the
top-level record is the final whole-outcome review point. Do not collapse action evidence into the
top-level retrospective: each record keeps its own retrospective and the top-level retrospective
judges the aggregated outcome.

## Required confirmations

1. **External-perspective completion**: the user-visible request is satisfied.
2. **Internal-perspective completion**: principles, verification, and structure are satisfied.
3. **Review findings dispositioned**: if any review verdict was produced for this work, every
   finding carries a disposition in the card's `## Verification` — accept, decline, or defer —
   each with a one-line reason. Declines are recorded, not skipped: a finding that leaves no
   trace when declined pushes everyone toward uncritical acceptance. Judge each finding with two
   questions: does the situation it describes actually reach this project, and if accepted,
   could the fix break a situation that does reach it? Reviewer severity (P1/P2) is a code-view
   ranking, not a priority — a P1 may be declined with a recorded reason. Accepted findings are
   fixed in the card or become new cards; deferred findings become planned cards or open
   questions.
4. **Retrospective completion**: what must change in the next work is recorded.

## Retrospective questions

Answer briefly.

- What decision points occurred? (`## Decision points`)
- Which context was missing or stale? (`## Context that was missing`)
- Should any behavior bind future work? (`## Rule candidate`)

`operations/retrospective.md` owns these three sections and what the retrospective leaves to
other records. Next work becomes a planned card or a `state/` record, not a retrospective line.

## Separate the queue from the rule

What happens next — the card to run, the id to close, the thing to watch once — is not written in
the retrospective. Register it as a planned card or a `state/` record, where it is found and closed.

`## Rule candidate` holds how work is done from now on, in any card. It expires only when something
supersedes it. Leave it empty when the work taught nothing durable, which is most of the time.

Two tests promote a candidate into a rule file, and nothing else does: **it happened twice**, or
**something outside the harness had to catch it**. Read
[rule-promotion.md](rule-promotion.md) before writing the section or lifting a candidate — it owns
the tests, where the rule goes, and why amending an existing rule usually beats adding a new one.

A closing session does not gather candidates across retrospectives. A separate consolidation
session does, into `.stage/state/rule-candidates.md`, and it only proposes
([rule-promotion.md](rule-promotion.md), "Consolidating candidates").

Mixing the queue and the rule under one heading is what buried the earlier pile: 217 retrospectives carried a lesson
and no rule file cited any of them.

## Output routing

- Official truth goes to `official/`.
- Living uncertainty stays in `state/`.
- Future improvements go to `work/planned/` or `proposals/`.
- Behavior changes go to project policy in `.stage/operations/` (or upstream to the plugin-owned
  `operations/` when the rule is common to every project).
- The retrospective artifact lives at `work/retrospectives/R-NNNNNNNN.md`.
- Never choose that number by hand. `close_work.py --project-root <root> <ITEM> \
  --allocate-retrospective` reserves the file from the project template and prints its id. It
  derives `R-NNNNNNNN` from the work item's `W-NNNNNNNN`. If the card's `retrospective_ref` or
  that number already names a current retrospective of this item, the command reuses it. If the
  same item's retrospective exists only in the archive, the command reports that lifecycle conflict
  and stops. If another item `W-MMMMMMMM` owns the number (a project that once numbered
  retrospectives in sequence), that item already has its retrospective, so the command tries
  `R-MMMMMMMM` next and follows owners until a number is free. It never counts records to pick
  "the last number plus one", which gave parallel worktrees the same number. It stops and names
  the owners when a number's owner is not a work item or the owners lead back to a number already
  tried.
- The work item's `retrospective_ref` points to that retrospective file.
- A decision this work settled — one it moved to `decided` — goes in the item's `decision_refs`.
  That field records what the item settled, not what it obeyed, so the item that raised a question
  and the item that carried the answer out do not both claim the record: the one that settled it
  owns it, and the other links it in its body. The audit enforces the back-link, and a venue
  exception relies on it to identify the single item it authorized.

## Promotion intent

Promotion to `official/` uses no body markers. Declare the target paths in the verified and
retrospected work item's `promotes`, then create the intent file.

```bash
python3 stage/scripts/promote_intent.py --project-root <project-root> --work-item W-00000001 --path .stage/official/<target>.md
```

When the paths will be written after the close, close with `--promotion deferred`. To write them
later, set the card's `promotion: approved` with its `promotes:` paths, create each intent, write
the paths, then record `promoted`. The promotion gate admits an intent only while the card says
`approved` or `promoted`, and the audit rejects a completed card left at `approved`, so
`approved` lasts only while the paths are being written.

A top-level item closed with `--archive` goes straight into `official/work/archive/`. To move an
item that was closed without it out of the review queue, use the **stage-archive** skill —
archiving needs only an archive intent (or `archive_work.py`), never a new work item.

## Closing the item

Use `close_work.py` (beside this skill) to complete an item, so `verification: passed` is a
byproduct of running the checks, not a hand-typed claim:

```bash
python3 stage/skills/stage-retrospective/close_work.py --project-root <project-root> W-00000001 \
  --check "<test command>" [--check "..."] [--promotion <final-choice>] [--archive]
```

It runs the card's stored `acceptance` checks and each `--check` (a `--check` that repeats a stored
check runs and is recorded once), records the output as evidence, and completes the item only when
they pass —
and also requires a completed retrospective and a FINAL promotion decision. When `decision_refs`
names any decision that does not declare `authorizes: venue_exception`, `not_applicable` is not a
promotion decision: choose another final value with `--promotion`. An item with no linked decision,
or with only one-time venue exceptions, may still use `not_applicable`.

If `.stage/settings.json` configures an `implementation`-stage review (see the plugin-owned
`operations/review.md`), `close_work` runs that review command too. The reviewer writes its verdict
as JSON to `STAGE_REVIEW_VERDICT_FILE`, and `close_work` refuses to close unless the command exits
zero and that file approves — a missing, malformed, or non-approving verdict blocks the close no
matter what the command printed.

For hierarchical records, `close_work` resolves the record by frontmatter ID. It writes no work list
file: the session-start Review candidates view is derived from the card's `status`.

### Close and archive in one command

When you close a top-level epic or story by hand, pass `--archive`. After the close succeeds, the
same command archives the hierarchy and its retrospectives, so the close and the archive land in
one commit beside the work. Commit the source changes before running it: the review judges the
commit at `HEAD`, and the archiver refuses while a path inside the item's scope is uncommitted.

| Case | What happens |
|---|---|
| A check or the review fails | Nothing is closed and nothing is archived. |
| The item sits under an epic or a story | `--archive` is refused before any check runs. Close it without the flag; it is archived with its top-level item. |
| The close succeeds and archiving fails | The command exits non-zero, names the cause, and leaves the item completed in `work/current/`. Fix the cause, then run `archive_work.py` or rerun the same command. |
| The item is already completed | Rerunning with `--archive` refreshes the decision index and archives it. |

Every close also writes a `- Load at close` line into `## Verification`: attempts, review FAIL
rounds, repeated findings, driver rounds, and driver failures, counted from the work log and the
card. `operations/review.md` owns the line's format and `stage/scripts/work_load.py` prints the
counts of closed cards as a table.

The drivers close without `--archive`: their landing step commits the closed card from
`work/current/`, so a driver-run item still waits there, completed, until it is archived.

When the work ran where the shared work log does not exist (for example a cloud session that wrote its
`### Executor report` in the commit body), import the report before closing, so `close_work` can copy
it onto the card's `## Progress`:

```bash
python3 stage/scripts/import_executor_report.py --project-root <project-root> W-00000001 --commit <rev>
```

It joins fields that the commit body wrapped across lines, validates the report against the executor
contract and the paths that commit changed, and leaves the work log unchanged when validation fails.

## Completion rule

Never mark work complete without a retrospective file linked through `retrospective_ref`.
