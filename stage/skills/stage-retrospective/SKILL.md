---
name: stage-retrospective
description: Perform the mandatory post-work Stage retrospective and confirm external completion, internal completion, principle application, and context updates before official promotion.
---

# Stage Retrospective

Use this skill after work reaches a completion candidate.

## Required confirmations

1. **External-perspective completion**: the user-visible request is satisfied.
2. **Internal-perspective completion**: principles, verification, and structure are satisfied.
3. **Retrospective completion**: what must change in the next work is recorded.

## Retrospective questions

Answer briefly.

- What decision points occurred?
- Which principles governed those decisions?
- Which context was missing, stale, or useful?
- What must be updated in `.stage/`?
- Can the artifact go to `past`, or must it stay in `present`?

## Output routing

- Official truth goes to `past`.
- Living uncertainty stays in `present/state`.
- Future improvements go to `future/backlog/items/` or `future/proposals/`.
- Behavior changes go to project policy in `.stage/operations/` (or upstream to the plugin-owned
  `operations/` when the rule is common to every project).
- The retrospective artifact lives at `present/work/retrospectives/R-NNNNNNNN.md`.
- The work item's `retrospective_ref` points to that retrospective file.

## Promotion intent

Promotion to `past` uses no body markers. Declare the target paths in the verified and
retrospected work item's `promotes`, then create the intent file.

```bash
python3 stage/scripts/promote_intent.py --project-root <project-root> --work-item W-00000001 --path .stage/past/<target>.md
```

To move a closed item out of the review queue into `past/work/archive/`, use the **stage-archive**
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
review command too and refuses to close on a failing or `BLOCK:` verdict.

## Completion rule

Never mark work complete without a retrospective file linked through `retrospective_ref`.
