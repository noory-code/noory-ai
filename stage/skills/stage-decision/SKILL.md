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

## Build the losing option once before choosing

Review does not catch a specification that cannot be built. One decision here drew five
independent review rounds and twenty-two findings — two of them security holes — and none of them
reached the contradiction that the first implementation attempt hit on its first pass
(R-00000237). Another fixed a file list by hand, shipped on paper, and cost a different project
its data (R-00000141). A third was written, then implemented, and the implementation surfaced a
check that the record's own text could not show was about to disappear (R-00000239).

**The step: produce the difference between the option you are about to choose and the option you
are about to reject, as real output, before writing the record.** Throw the code away. Only what
came out goes in the record.

### When it fires

Both must hold.

- The decision fixes something that will be executed against inputs — an allow list, a filter, a
  set of conditions, an order of steps, what a command receives or returns.
- **The options differ in what they produce on some input, and one run makes that difference
  visible.** Running only the winner proves nothing; a winner that works is not a loser that
  fails. Run the loser too, on the input where they disagree.

It does not fire when the options differ only over time or in volume. One decision here chose
between loading rule filenames into a session and loading the rule bodies; what settled it was
that a body copied into a session becomes a second owner that never updates, which no single run
shows. A character count settled it, and counting is cheaper. It also does not fire when nothing is
executed at all — a decision that assigns ownership, names a location, or grants a one-time venue
exception.

### What the input has to be

Real, not invented. A finished run's actual change list, the command a record quoted, the
repository's own files. The cases here that paid off found the input already lying around: the
neighbouring commit (R-00000237), the command the observation itself quoted (R-00000247), a run
another record had already captured ten days earlier. Constructing the state is fine when it is
faithful and cheap — one decision built a repository whose declared directory had been wiped
wholesale, and that state is the whole reason its two candidate filters diverged (R-00000250).

Counting is a run too, and an uncounted count is not evidence: a `grep` for `blocker` returned
fourteen where a test returned ten (R-00000242).

If reaching the input requires building the thing this decision specifies, the try is not a
throwaway and this step does not apply. Write the record and say in `## Follow-up` that it was not
tried. The implementation card then carries the burden, and refusing that card is the correct
outcome when the specification does not hold.

### Where the result goes

An `###` subsection under `## Chosen direction`, named for what came out rather than for the fact
that a try happened — "why filtering on existence alone loses deletions", not "what the trial
showed". One table of what each candidate produced on the shared input, and the one line of
underlying behavior that explains the difference (R-00000250).

A sibling step guards the other direction. `stage-work`'s "Run the premise before turning an
observation into a card" checks whether a claim someone already made is still true. This one
checks a specification that is not true yet, because nobody has written it down before now.

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

## Close what the decision answered

A decision usually exists because an observation or a question asked for it. Promoting the decision
does not close that record, and nothing in the harness notices the two now disagree — the audit
checks links, not whether a record's `## Next action` has become false.

So the record keeps asking for a decision that already stands. The next reader takes it at its
word and registers a card for work that shipped. That happened here one day after the decision
promoted: the card was registered, started, and rejected on its first step (R-00000245).

**Promote the decision and close the record it answered in the same pass.** When the record is only
partly answered, say in its `## Status` which part the decision settled and rewrite `## Next
action` to whatever is genuinely left. Either way the record must stop asking for what now exists.

## Hook connection

Modifying `.stage/official/` counts as official promotion. For an intentional promotion, finish
verification and the retrospective, declare the target paths in the work item's `promotes`,
then create the intent with `scripts/promote_intent.py` (one `.stage/.runtime/intents/` file per work item and path — never hand-write the filename). Never put promotion markers in official
artifact bodies.
