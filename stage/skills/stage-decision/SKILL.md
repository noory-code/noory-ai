---
name: stage-decision
description: |
  Apply the Stage decision harness when work reaches a decision point. Use for work
  that needs principle-based control rather than immediate execution.
---

# Stage Decision

Use this skill at decision points.

## Decision inputs

Read the relevant `.stage/` context.

1. `past/canon/principles.md`: the project's principle catalog — the criteria this decision must cite.
2. `past/`: official truth.
3. `present/`: work in progress and uncertainty.
4. `future/`: plans and proposals.
5. `operations/`: behavior gates.

## Decision gates

Apply the gates in order.

1. **Purpose Gate**: confirm the higher purpose.
2. **Truth Gate**: separate verified context from unknowns.
3. **Question Gate**: ask the user only when the decision is theirs.
4. **Coverage Gate**: check that cases neither overlap nor leave gaps.
5. **Ownership Gate**: assign one owning location per fact, status, and rule.
6. **Failure Gate**: surface broken assumptions and incomplete handling.
7. **Promotion Gate**: promote only verified artifacts.
8. **Retrospective Gate**: record what must change in later behavior.

## Priority values

When principles conflict, use this value order.

1. Truthfulness.
2. User intent.
3. Project essence.
4. Safe completion.
5. Durability.
6. Simplicity.
7. Speed.

## Recording

A decision that shapes the work is recorded, not just made.

- Create a decision record from `present/work/decisions/_template.md` (`DE-NNNNNNNN`), including the
  question, options, principles applied, and chosen direction.
- Set the record's `work_item` to the current work item and add the record to the work item's
  `decision_refs`.
- Trivially reversible how-decisions do not need a record; anything that would surprise the next
  session does.

## Output

Return the following.

- The decision.
- The principles and context used.
- Routing location: `past`, `present`, or `future`.
- The retrospective note needed after execution.

## Hook connection

Modifying `.stage/past/` counts as official promotion. For an intentional promotion, finish
verification and the retrospective, declare the target paths in the work item's `promotes`,
then create `.stage/.runtime/promote-intent.json`. Never put promotion markers in official
artifact bodies.
