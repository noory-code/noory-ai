# Review

This document owns the external-review gate.

## Gate

When an external review (another agent such as codex, a human reviewer, or a
tool) reports findings, do not accept them uncritically:

1. Anchor on the work's purpose and `official/canon` truth first — the review is
   measured against the goal, not the other way around.
2. Judge each finding against that purpose: does it protect a behavior an honest
   user relies on, or is it an edge that never arises from honest use?
3. Rebut findings that do not serve the goal. State the rebuttal and the essence
   it is measured against, then send the rebuttal back for a counter-review.
4. Process only findings that survive the counter-review — purpose-aligned, with
   real impact. Record what was accepted and what was rebutted, and why.
5. Rebuttal is goal-alignment verification, not avoidance. Contrarian rejection
   or nitpicking that scatters the essence is itself a violation of this gate.
6. When rounds stop converging (the finding count does not shrink), the
   remaining edges are best-effort: document the boundary in the relevant
   artifact and stop, rather than chasing a full reimplementation.

## Sequence

`external review → local rebuttal (against purpose) → counter-review → process
survivors`. The rebuttal and its outcome are recorded so the decision is
auditable, not just made.

## Configuring when a review runs (`settings.json`)

The `review` block of `.stage/settings.json` declares, per lifecycle stage, HOW
STRONG a review runs — bound to a real command, never a bare label:

- `strengths` maps each level (`off`, `light`, `standard`, `deep`, `red-team`) to
  the command that level runs. The harness fixes no command; the project fills in
  a review that writes the reviewer-owned JSON verdict to the file named by
  `STAGE_REVIEW_VERDICT_FILE` (required shape and validation rules: the `review`
  comment in `templates/v4/project-stage/settings.jsonc`). `off`/empty means no
  review.
- `stages` picks the level for each stage: `design`, `implementation`, `promotion`.

Review is OPTIONAL and driven by the work item's own `review` field
(`not_required` | `pending` | `passed`; absent defaults to `not_required`):

- An item that never declares review (`not_required`/absent) completes with no
  review — the bypass. Most work needs no gate here.
- An item that declares `review: pending` opts THAT item in: it cannot be
  completed until `review: passed`. The completion gate blocks it, so even
  hand-editing `status: completed` is refused while `review: pending` — this is
  stronger than the verification field, which has no such requirement.

`close_work.py` runs the `implementation`-stage review only when the item is
`review: pending`: it deletes any prior verdict file, exports
`STAGE_REVIEW_VERDICT_FILE`, executes the resolved command, and records its
output as evidence. The review command, and an autonomous item's independent
review alike, runs under `--review-timeout` (default 3600 seconds), separate
from the per-check `--timeout` (default 900 seconds), so a high-effort review is
not cut off at the check budget. A review that exceeds it fails the close with
`[TIMED OUT after <n>s] (--review-timeout)`; a check that exceeds its budget
reads `(--timeout)` instead, so the evidence names the budget that ran out. The
unattended driver passes the larger of 3600 seconds and its per-command timeout
as `--review-timeout`, capped by the run's remaining wall clock, and bounds the
whole `close_work.py` run by every check's budget plus that review budget. The
review passes only when the command exits zero **and**
that file holds a valid verdict with `approved: true`. A missing, malformed, or
non-approving verdict fails the close even on a zero exit, and a zero exit with
an approving verdict passes it whatever the command printed — reviewer prose is
human-readable context, and no label inside it decides the machine result. On a
pass it sets `review: passed` and records the verdict on the card (see below).
Fail-closed: a pending item whose
stage has a typo'd strength or no bound command is refused until `settings.json`
is fixed (the audit reports `REVIEW001`). This keeps `review: passed` bound to an
executed verdict, never a hand-typed claim. Set the requirement with
`register_work.py --review`, and close with `close_work.py` (not by editing
frontmatter).

## How the reviewer judges

The reviewer judges by running, not by reading the executor's account (DE-00000101). Every
criterion in the verdict names its `method`:

| `method` | Meaning | Allowed verdict |
|---|---|---|
| `ran` | the reviewer ran a command or observed the behavior itself | `PASS` or `FAIL` |
| `read` | the reviewer read files or records | `PASS` or `FAIL` |
| `unable` | the reviewer could not gather the evidence the criterion needs | `FAIL` only |

```yaml
reviewer_rules:
  - if: the reviewer did not see a criterion's evidence itself
    then: the criterion is FAIL; the executor report, the work log, and code comments are claims
  - if: a criterion asks for a command result or observed behavior
    then: method is ran, from at least one command the reviewer chose itself; its reason names the command and what it showed
  - if: a criterion states a fact of the records (a decision exists, a document says something)
    then: method is read
  - if: the reviewer could not run what a criterion needs
    then: method is unable and the verdict is FAIL
close_work_rules:
  - if: a criterion has no method, or a method other than ran, read, unable
    then: the verdict is invalid and the close fails
  - if: a criterion is PASS with method unable
    then: the verdict is invalid and the close fails
  - if: a criterion is FAIL with method unable
    then: the close fails and names that criterion's number; the rejection line goes on the card
```

`close_work.py` runs the card's stored `acceptance` checks before the review. Running one of them
again on the same tree shows the reviewer nothing new, so the review commands ask for a probe of
the reviewer's own instead.

The method is what the reviewer reports about itself. `close_work.py` does not read the
reviewer's tool calls, so it cannot tell a reviewer that wrote `ran` without running, and the
reviewer decides which criteria need a run. DE-00000101 chose this knowingly; a verdict that
claims to have seen what its named command cannot show is the stated reason to add a check of
the tool calls.

A criterion that only a whole session can observe (a new cloud session takes a role and does
something) is observed by a verification session before the close (`stage-orchestrate`, "Start a
verification session"). The orchestrator writes that observation on the card's `## Verification`,
and the reviewer judges the criterion from it with method `read`. The verification session does
not decide the close.

## What close writes on the card

`close_work.py` completes the card only after every check and any required review
has passed. Before that point it writes one thing: when a review at close returns a
valid verdict that rejects the work, `## Verification` gains that review's line (below)
and every frontmatter field stays as it was. A failing check, a review command that
fails, and a missing or malformed verdict leave the card unchanged.

- Frontmatter: `verification: passed`, the final `promotion` value,
  `status: completed`, and `review: passed` when a review ran.
- When the work log holds an executor report, `## Progress` gains
  `### Executor report at close — <date>`: one fenced block with the latest
  report's `What changed:`, `Why:`, `Decisions made:`, and `Work not done:`
  lines, verbatim. A card closed without a driver run has no report and gains
  nothing here.
- `## Verification` gains one line for the checks that passed:
  ``- Checks at close <date>: <count> passed — `<command>`; `<command>` ``.
  Check output is not copied onto the card.
- Each review that `close_work.py` runs and that returns a valid verdict adds one
  line to `## Verification`, whether it approved or rejected:
  `- Review at close <date> by <reviewer>: <approved|rejected> (1 PASS ran, 2 FAIL read, ...)`.
  The numbers follow the verdict's criterion order, and each carries that criterion's verdict
  and `method`. A line written before the `method` key existed has the verdict only.
  `<reviewer>` is the reviewing
  venue for an autonomous item; otherwise it is the review command's `--label`, or the
  file name of the `STAGE_CODEX_COMPANION` override when that replaced a `codex`
  label, or `reviewer` when the command names none. Counting the `rejected` lines of
  archived cards gives the number of reviews at close that sent work back; counting the
  `ran`, `read`, and `unable` marks gives how the reviewers judged.
- `## Verification` gains the card's load, counted by `scripts/work_load.py` from the work log
  and the card as they stand at close:
  `- Load at close <date>: attempts <n>, review FAIL rounds <n>, repeated findings <n|unknown>, driver rounds <n>, driver failures <n> (timed out <n>)`,
  followed by one `  - Driver failure: <role> — <reason>` line per driver failure.

  | Count | Counted from |
  |---|---|
  | `review FAIL rounds` | the larger of: executor reports in the work log with a non-empty `Review dispositions (JSON):`; `rejected` review lines already on the card |
  | `attempts` | the larger of: `### Executor report` sections in the work log; `review FAIL rounds` + 1 |
  | `repeated findings` | adjacent answered rounds in the work log that share a `finding`; `unknown` when the work log holds fewer answered rounds than `review FAIL rounds` |
  | `driver rounds` | `### Driver commands` sections in the work log; `0` means no driver ran the card from this checkout |
  | `driver failures` | `### Driver failure` sections in the work log; `timed out` counts those whose `Reason:` contains `timed out` |

  `python3 stage/scripts/work_load.py --project-root . --closed-since <YYYY-MM-DD>` prints these
  counts for closed cards as a Markdown table with a totals row. A card closed before this line
  existed shows its `rejected` review lines and `not recorded` in the other columns.
- The reviewer's reasons and report are not copied onto the card. They stay in the
  work log (`.stage/.runtime/driver/logs/<work-id>.md`), which is not committed.
- Reviews that the drivers run between rounds are recorded in the work log only.

The executor report lines, the criteria with their methods, and the load counts live on the card because
the work log and the verdict file sit under `.stage/.runtime/`, which is not committed.
The card is the only durable record of what the executor decided, what the
passing review checked and how, and what the card took to land.

## Cross-venue review

When a project runs more than one venue (see `stage-handoff`, Delegated
execution), the default review posture is cross-venue: the venue that executed a
card does not review it. Same-model review shares the author's blind spots; the
counter-venue's review is what catches them.

- The executor of a card and the reviewer of that card must be different venues.
  This holds whether the card ran in its own window or by delegation.
- A delegated card is reviewed by the hosting window as part of closing it: the
  host verifies the delegated output against the card's success criteria before
  `close_work.py` runs. The host must not forward its own review back to the
  executing venue's model.
- A card executed by the window that will also close it binds the counter-venue
  through the review gate above: declare `review: pending` on the card
  (`register_work.py --review`) and bind the counter-venue's review command as
  the `implementation` (or `design`) stage strength in `settings.json`. The gate
  then refuses completion until the counter-venue's verdict passes.
- The rebuttal sequence at the top of this document applies to cross-venue
  findings unchanged: purpose first, rebut what does not serve it, process the
  survivors.
