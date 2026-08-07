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
4. **Coverage Gate**: check that cases neither overlap nor leave gaps. A decision that governs
   behavior must name every place that behavior is invoked — see "Count where it applies" below.
5. **Ownership Gate**: assign one owning location per fact, status, and rule.
6. **Failure Gate**: surface broken assumptions and incomplete handling.
7. **Promotion Gate**: promote only verified artifacts.
8. **Retrospective Gate**: record what must change in later behavior.

## Count where it applies

A decision that governs behavior applies wherever that behavior is invoked — not where you
happened to be looking. Before writing the record, find every site and list it. Grep for it, do
not recall it from memory.

**Call sites are one kind of six.** Counting only the code is the single most repeated failure in
this project's retrospectives, and the list below is what those retrospectives converged on, one
kind at a time, each after a card shipped short.

| Kind | What to look for | Learned from |
|---|---|---|
| Code | every call of the behavior | — |
| Config | settings keys, command strings, environment variables the behavior reads | R-00000101 |
| Documents and indexes | prose that describes the behavior, and any index or derived view it writes | R-00000101, R-00000198 |
| Failure paths | what each site leaves behind when it fails, not only when it succeeds | R-00000099 |
| Gates | the hooks that allow or deny this behavior | R-00000199 |
| Audit rules | the checks that read the records this behavior writes | R-00000200, R-00000203 |

The last two are what a change that **moves a record** always touches, and always the ones left
out. Writing and committing are separate sites even for the same path — they run different checks
(R-00000171, R-00000173).

Fill the record's `## Where this applies` with one row per site: the file and line, and which
config or contract each site reads. Two sites that share a command string, a config key, or an
environment variable are one change with two callers — say so, because changing what that
command receives obliges every caller to supply it.

A decision with a single site says so explicitly. An empty section means the count was never
done, and the sites left out surface later as defects: one place gets fixed, the others keep the
old behavior or break outright.

## Say what would prove the decision wrong

Every record carries one line naming the observation that would overturn it. Not a caveat — a
thing that could happen, which if it did means this decision no longer holds.

A decision without it is unfalsifiable, and when reality contradicts it later nobody can tell
whether the decision was wrong or merely applied wrongly. This project overturned a decision three
hours after writing it and had to re-derive the grounds from scratch because that line was missing
(R-00000165). Every record since that carried the line has had it pay off, including one where the
predecessor's line settled the successor's judgement (R-00000180).

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
  question, options, principles applied, chosen direction, and the counted sites under
  `## Where this applies`.
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
