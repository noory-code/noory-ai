# Review

This document owns the external-review gate.

## Gate

When an external review (another agent such as codex, a human reviewer, or a
tool) reports findings, do not accept them uncritically:

1. Anchor on the work's purpose and `past/canon` truth first — the review is
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
  a verdict-emitting review (a reviewer that exits non-zero or prints a line
  starting with `BLOCK:` when it finds a blocker). `off`/empty means no review.
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
`review: pending`: it executes the resolved command, records its output as
evidence, and on success sets `review: passed`. Fail-closed: a pending item whose
stage has a typo'd strength or no bound command is refused until `settings.json`
is fixed (the audit reports `REVIEW001`). This keeps `review: passed` bound to an
executed verdict, never a hand-typed claim. Set the requirement with
`register_work.py --review`, and close with `close_work.py` (not by editing
frontmatter).
