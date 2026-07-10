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
