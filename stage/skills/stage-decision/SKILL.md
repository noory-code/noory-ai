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

1. `official/canon/principles.md`: the project's principle catalog — the criteria this decision must cite.
2. `official/`: official truth.
3. `work/`, `decisions/`, and `state/`: work in progress and uncertainty.
4. `proposals/`, `roadmap/`, and `work/planned/`: plans and proposals.
5. `operations/`: behavior gates — common rules are plugin-owned (the installed Stage plugin's
   `operations/`); `.stage/operations/` holds only project policy and declared overrides.

## Decision gates

Apply the gates in order.

1. **Purpose Gate**: confirm the higher purpose.
2. **Truth Gate**: separate verified context from unknowns. Host-project instructions (`CLAUDE.md`, `AGENTS.md`, rules, skills) count as context to use — and to challenge with a correction request (open question + proposal) when they contradict observed reality.
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

- Create a decision record from `decisions/pending/_template.md` (`DE-NNNNNNNN`), including the
  question, options, principles applied, and chosen direction.
- Set the record's `work_item` to the current work item and add the record to the work item's
  `decision_refs`.
- Record a decision when ANY of these holds; otherwise skip the record:
  - it changes a file under `official/` (official truth), or
  - it selects between two or more viable options where the alternatives were plausible, or
  - reversing it later would require editing more than one file, or
  - it sets a value another work item depends on (a name, path, schema, or interface).
  A pure how-detail that touches one file and is reverted by undoing that file needs no record.

## Output

Return the following.

- The decision.
- The principles and context used.
- Routing location: `official/` or the owning mutable responsibility family.
- The retrospective note needed after execution.

## Hook connection

Modifying `.stage/official/` counts as official promotion. For an intentional promotion, finish
verification and the retrospective, declare the target paths in the work item's `promotes`,
then create the intent with `scripts/promote_intent.py` (one `.stage/.runtime/intents/` file per work item and path — never hand-write the filename). Never put promotion markers in official
artifact bodies.
