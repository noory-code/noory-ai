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
output as evidence. The review passes only when the command exits zero **and**
that file holds a valid verdict with `approved: true`. A missing, malformed, or
non-approving verdict fails the close even on a zero exit, and a zero exit with
an approving verdict passes it whatever the command printed — reviewer prose is
human-readable context, and no label inside it decides the machine result. On a
pass it sets `review: passed`. Fail-closed: a pending item whose
stage has a typo'd strength or no bound command is refused until `settings.json`
is fixed (the audit reports `REVIEW001`). This keeps `review: passed` bound to an
executed verdict, never a hand-typed claim. Set the requirement with
`register_work.py --review`, and close with `close_work.py` (not by editing
frontmatter).

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
