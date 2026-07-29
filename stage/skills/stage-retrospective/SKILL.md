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

- What decision points occurred?
- Which principles governed those decisions?
- Which context was missing, stale, or useful?
- What must be updated in `.stage/`?
- Can the artifact go to `official`, or must it stay in a mutable family?

## Output routing

- Official truth goes to `official/`.
- Living uncertainty stays in `state/`.
- Future improvements go to `work/planned/` or `proposals/`.
- Behavior changes go to project policy in `.stage/operations/` (or upstream to the plugin-owned
  `operations/` when the rule is common to every project).
- The retrospective artifact lives at `work/retrospectives/R-NNNNNNNN.md`.
- The work item's `retrospective_ref` points to that retrospective file.

## Promotion intent

Promotion to `official/` uses no body markers. Declare the target paths in the verified and
retrospected work item's `promotes`, then create the intent file.

```bash
python3 stage/scripts/promote_intent.py --project-root <project-root> --work-item W-00000001 --path .stage/official/<target>.md
```

To move a closed item out of the review queue into `official/work/archive/`, use the **stage-archive**
skill — archiving needs only an archive intent (or `archive_work.py`), never a new work item.

## Closing the item

Use `close_work.py` (beside this skill) to complete an item, so `verification: passed` is a
byproduct of running the checks, not a hand-typed claim:

```bash
python3 stage/skills/stage-retrospective/close_work.py --project-root <project-root> W-00000001 \
  --check "<test command>" [--check "..."] [--promotion not_applicable]
```

It runs each `--check`, records the output as evidence, and completes the item only when they pass —
and also requires a completed retrospective and a FINAL promotion decision. If `.stage/settings.json`
configures an `implementation`-stage review (see the plugin-owned `operations/review.md`), `close_work` runs that
review command too. The reviewer writes its verdict as JSON to `STAGE_REVIEW_VERDICT_FILE`, and
`close_work` refuses to close unless the command exits zero and that file approves — a missing,
malformed, or non-approving verdict blocks the close no matter what the command printed.

For hierarchical records, `close_work` resolves the record by frontmatter ID and writes the exact
nested link into `work/review.md`; do not substitute a flat `<id>.md` path.

## Completion rule

Never mark work complete without a retrospective file linked through `retrospective_ref`.
