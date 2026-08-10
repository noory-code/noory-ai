---
name: stage-drive
description: Run registered Stage work through an executor instead of doing it by hand — the driver accepts a runnable leaf or a parent, picks the next ready item, runs the venue's executor, re-runs its acceptance checks, and has a different venue review the result. Use when asked to drive, auto-run, or batch-execute Stage work, to preview which item the driver would take next, to set up the `executors` commands it needs, or to run a whole subtree unattended. This is execution; registering work is stage-work and passing work to a human-opened window is stage-handoff.
---

# Stage Drive

`drive.py` is the executing end of the harness. Everything else in Stage records intent and truth;
this runs the work. It never creates work items, approves a decomposition, promotes official truth,
or crosses a human-approval gate — it only carries out cards that already exist.

```bash
python3 "<driver>" --project-root <project-root> <TARGET_ID>
```

The driver lives at `../../scripts/drive.py` relative to this skill's directory. The host names
that directory when it loads this skill; resolve the driver from it and substitute the resulting
absolute path for `<driver>` in every command here, keeping the quotes — an installed plugin can
sit under a path containing spaces. No other spelling works everywhere: shell
variables such as `${CLAUDE_PLUGIN_ROOT}` are injected into hook commands only and expand to
nothing in the shell that runs these commands, and a repository-relative path only exists in one
checkout. When developing inside the Stage source checkout itself, `stage/scripts/drive.py` also
resolves — but that form is the exception, not the default. The target can be either a parent or a
runnable leaf work item; no wrapper parent is required for a leaf.

## Run independent cards in parallel worktrees

Resolve `drive_parallel.py` from `../../scripts/drive_parallel.py` relative to this skill, using
the same absolute-path rule as `drive.py`, then pass two or more independent card IDs:

```bash
python3 "<parallel-driver>" --project-root <project-root> W-00000001 W-00000002
```

The command creates `<project-parent>/<project-name>-stage-worktrees/<card-id>` by default. Each
path is a Git worktree on `stage/worktree/<card-id>`, and each worktree runs one supervised
`drive.py --execute` step concurrently with that worktree as `--project-root`. At most two drivers
run at once by default; use `--max-workers <positive-integer>` to choose another ceiling. Each
driver has a 3600-second default timeout; use `--driver-timeout <positive-seconds>` to change it.
Use `--worktree-root <path>` to choose a different parent directory.

The command prints each driver status, worktree path, and `Merge branch:
stage/worktree/<card-id>`. It does not close a successful card. After reviewing and completing the
card in that worktree, resolve `land_run.py` from `../../scripts/land_run.py` relative to this skill
and run the following command. Use the same absolute-path rule as `drive.py`:

```bash
python3 "<land-run>" --project-root <project-root> --worktree <worktree-path> <card-id>
```

The landing command copies the ignored run log back to the project checkout, commits only the
card's declared scope plus the completed card and ancestor lifecycle records and registry-declared
current-work indexes, merges with `--no-ff --no-commit`, and removes the worktree and branch. It
refuses a non-final card, incomplete completion fields, a missing retrospective, a dirty project
checkout, any path outside that allowance, and a merge conflict. If any worktree creation fails,
every tree and branch created by that invocation is cleaned up when Git exposes enough state to do
so. If Git creates the branch but fails before
registering the worktree, the branch can remain; the command reports that cleanup failure and a
later `--cleanup` can remove the retained branch without requiring the absent path. A driver
failure keeps its worktree and branch for inspection. The command refuses to create any worktree
when the project checkout is dirty or a named current card does not exist, so every new tree has
the complete requested input at `HEAD`. If a driver times out, its executor or reviewer may still
be writing to the worktree. The command determines the active external role from the shared work
log, runs the executor or independent-reviewer venue's reaper as applicable, and reports why it
could not otherwise; do not use `--cleanup` until every external job has stopped.

Remove retained worktrees and their branches after inspection with the same project root,
worktree root, and card IDs:

```bash
python3 "<parallel-driver>" --project-root <project-root> --cleanup W-00000001 W-00000002
```

Cleanup accepts only a path registered by Git on the exact
`stage/worktree/<card-id>` branch. It refuses an ordinary directory, a registered worktree on
another branch, and a branch containing commits not merged into the project checkout's `HEAD`.
It also refuses a registered worktree with staged, unstaged, or untracked changes. Inspect and
preserve those changes first, or explicitly discard them with `--cleanup --force-cleanup`. A
retained exact branch can be removed even when its worktree path is absent. Merge or otherwise
preserve unmerged commits first. An absent worktree and branch are reported as absent, never as
removed. Cleanup leaves the shared worktree-root directory itself in place because the command
cannot prove that it created that parent.

Before creating the worktree root or any card worktree, the command compares every named card's
declared `scope`, including every descendant card when the named target is a story or epic. Two
declarations overlap when they name the same path or one path contains the other. Matching
`CHANGELOG.md` declarations are excluded when both are ordinary card work that appends independent
entries to the Unreleased section. A scope that includes `release_plugin.py` can rewrite the
section heading, so its matching changelog is not append-only and remains an overlap. When an
overlap remains, the command creates no worktree and prints every card pair and overlapping path.
Narrow a card's scope, choose different cards, or run those cards sequentially.

Separate worktrees isolate repository observation; they do not make overlapping edits safe. When
the declared directories overlap but the actual files are known to be independent, pass
`--allow-overlap`. The command prints the overridden card pairs and paths before continuing so the
human decision remains visible. The command also rejects a duplicate ID inside one invocation,
and an existing card-named path or branch makes a later invocation fail instead of reusing the
same card.

Each worktree has its own ignored `.stage/.runtime/` evidence. The tracked lifecycle indexes do not
have that isolation after merge: `.stage/work/active.md` and `.stage/work/review.md` can conflict
even when the source scopes are independent. The human resolving the merge owns those index rows.

## The default run is a dry run

Invoked with no mode flag, the driver only reports. It prints the item it would select, the
executor command, the acceptance checks, the independent reviewer, and the next attempt and
iteration counters. It runs no command, creates no `.stage/.runtime/` state, and changes nothing.

Reach for this first, every time. It answers "is this project even wired up to drive?" without
side effects.

## What it will pick

If the target has any non-terminal child, the driver treats it as a parent and considers only its
direct, non-terminal leaf children with a **non-empty `acceptance` list**. It never selects that
target directly while an unfinished child exists. Ties break deterministically by work item ID.

The target may be an epic, story, or action. The driver searches the whole target subtree and
selects the first runnable leaf by work ID. A blocked story suppresses every remaining action in
that story, while sibling stories under the same epic remain eligible. If the target itself is a
runnable leaf, the driver selects it directly.

A card with no acceptance commands is invisible to the driver — there is nothing for it to verify,
so it will not run it. Unattended mode narrows eligibility further to `active` and
`autonomous: true`; for a parent target, it searches the whole subtree rather than only direct
children, while a leaf target can select only itself.

## The card's declared size sets the command timeout

One per-command timeout bounds each executor, acceptance, and reviewer command. The driver fixes it
once at run start. Without `--timeout` it is the largest of three declaration signals, times 900
seconds:

| Signal | How it is counted |
|---|---|
| Unfinished leaves at or below the target | Never below one, so a runnable leaf counts itself |
| Entries in the card's `scope` | Split on commas and semicolons |
| Items under the card's `## Success criteria` | Top-level list items only; indented sub-items do not count |

A leaf card declaring two scope entries and three success criteria therefore gets
`max(1, 2, 3) * 900 = 2700` seconds. The 900-second floor is what the derivation produces at its
smallest — a card declaring one of everything — not what an ordinary card receives.

Override it with a positive number of seconds, on a dry run, `--execute`, `--resume`, or
`--unattended`:

```bash
python3 "<driver>" --project-root <project-root> --timeout 5400 --execute <TARGET_ID>
```

The override replaces the derived value outright and applies to every command in the run.

Decide it with a count, not a judgment. Take the declared size from the three rows above, then count
the files the card will change — read its Actions and Next action, and expand any `scope` entry
naming a directory into the files under it the card will touch:

| Checkable before the run | Seconds it asks for |
|---|---|
| That file count exceeds the declared size | `file count * 900` |
| A prior round on this card timed out | Twice the seconds that round had; its `### Driver failure` entry in the shared work log names them |
| Neither | None — the derived value already covers the work |

Both rows can hold at once. When they do, pass the larger of the two numbers, so exactly one value
always falls out of the table.

A `scope` entry naming a directory counts 1 however many files it holds, which is the most frequent
reason the file count exceeds the declared size. The dry run does not print the derived timeout —
its `Execution time` line reports command time already used against the run's global limit, not the
per-command limit — so take the declared size from the card.

Two cases offer no count beforehand: a card whose paths are unknown until it starts, and a card
whose one file needs many edit-and-test rounds rather than a single pass. No threshold covers those
honestly, so overshoot deliberately instead. The two errors do not cost the same — too large costs
only the delay before a hung command gives up, too small costs the whole round and the work inside
it.

A truncated command costs the round, not an attempt: the driver reads a timeout as venue
infrastructure failure and says so rather than counting a failed card attempt. Raising the number
does not reserve time, only allow it. In `--unattended` each command is additionally clamped to the
run's remaining wall-clock budget, so an override above that ceiling changes nothing until the
ceiling moves too.

`drive_parallel.py`'s `--driver-timeout` bounds one whole driver invocation instead of one command
inside it; the two do not substitute for each other.

## Two settings gates, both fail closed

**`executors` must exist before anything runs.** The `executors` object in `.stage/settings.json`
(or `settings.jsonc`) maps each venue to the command that carries out that venue's work. An absent
section, a missing venue, a malformed map, or an empty command stops the driver where it stands
with an escalation recommendation — it never falls back to running the work itself. The driver
passes the selected card through `STAGE_WORK_ITEM` and `STAGE_WORK_ITEM_PATH`, its root-first
ancestor card paths through the JSON array `STAGE_WORK_ITEM_ANCESTOR_PATHS`, and the project
through `STAGE_PROJECT_ROOT`. Both configured executor venues must instruct the executor to read
the selected action and every ancestor card before working; the command text is shell-expanded,
so its variable syntax is platform-specific.

**The reviewer's venue must differ from the item's.** `review.reviewers` must resolve to exactly
one reviewer whose venue is not the selected item's venue. Configure only the item's own venue and
the driver refuses rather than letting a venue grade its own work.

## What the executor reports is a claim, not a measurement

Re-count any number the executor reports before a judgement rests on it, and open the source behind
any "I verified this" before repeating it. A report is what the run believes happened; it can be
sincere and still wrong (R-00000207, R-00000208, R-00000232).

The same duty runs the other way. When you hand the executor something you measured, mark it as
measured and say how — search, sample size, what you opened. A caution written as a bare statement
comes back as a finding in the executor's record, with your wording and none of your uncertainty
(R-00000231, R-00000236). Separate **what I saw** from **what I was told** in every brief.

An executor that re-counts what the supervisor handed it is not doubting the supervisor; it is
doubting both accounts at once, which is the only version that catches anything. That re-count
overturned three of four stated grounds in one card here (R-00000238), and the population turned
out to be eighteen where the brief said four.

**Never ask the executor to leave something out of its report.** Harness setup and card work are
separated inside the report, not hidden from it. A security check caught this project doing exactly
that (R-00000225).

## Executor autonomy and report contract

Before acting, the executor decides whether the selected action itself serves its stated purpose.
If the action is wrong, it stops without implementing it and reports that decision for the human to
redesign or cancel.

Never change the selected card's `scope`. A human decides whether to widen it. Report a needed
scope crossing without rewriting the declaration, because rewriting it erases the crossing.

When the action is sound, every encountered task follows exactly one row:

| Task | Action | Report |
|---|---|---|
| Needed for the purpose and inside the declared scope | Do it | State the decision and why |
| Needed for the purpose but outside the declared scope | Do it | State the decision, why, and scope boundary crossing |
| Not needed for the purpose | Skip it | No task-specific report |

Every executor command must require exactly one append-only report per attempt in this shape:

```text
### Executor report
What changed: <non-empty one-line summary>
Why: <non-empty one-line reason>
Decisions made: <non-empty one-line decisions, or None>
Work not done: <non-empty one-line needed work left undone, or None>
Changed paths (JSON):
["<repository-relative path>"]
Review dispositions (JSON):
[{"finding":"<exact failed criterion>","disposition":"accept|decline|defer","reason":"<one-line reason>"}]
Review request: <non-empty one-line request>
```

`Review dispositions (JSON)` is present only when a prior verdict has failed criteria. `Decisions
made:` records choices the executor made while doing needed work, including choices to cross
scope. `Work not done:` records needed work it left undone because the action itself was wrong;
scope is never a reason to leave needed work undone. Use `None` instead of leaving either field
empty. Reviewer commands must read both fields and judge whether the purpose and scope-boundary
reporting contract was followed; they must not reconstruct unreported choices only from the code.

## Optional per-venue turn reaping

`reapers` is an optional sibling of `executors` in `.stage/settings.json` (or `settings.jsonc`).
It has the same venue-to-command shape:

```json
{
  "executors": {
    "codex": "<executor command>"
  },
  "reapers": {
    "codex": "<reap command>",
    "claude": null
  }
}
```

After an executor command returns, the driver runs `reapers.<executor venue>`. After a reviewer
command returns — including a blocking reviewer — it runs `reapers.<reviewer venue>`. Unattended
close-time review follows the same rule, and an execution request already at its per-item attempt
cap runs the executor venue's reaper before escalation. The command owns every tool-specific
detail needed to find and stop jobs; the driver only selects it by role venue.

The reaper inherits `STAGE_WORK_ITEM_PATH`, `STAGE_PROJECT_ROOT`, `STAGE_WORK_LOG_PATH`, and
`STAGE_TURN_ROLE` (`executor` or `reviewer`). Use this context to stop only jobs created for that
card and role; a broad cleanup must not stop unrelated work in the same workspace.

Set `reapers.<venue>` to `null` when that venue's command runs synchronously and cannot leave an
external job behind. The driver then runs no reap command and emits no warning. An empty string is
not this sentinel and remains an invalid command.

An absent `reapers` section or missing venue means the cleanup requirement has not been decided.
It does not change the original turn result, but the driver prints a warning and appends it to the
card's shared work log because jobs may remain. A configured reap command that exits unsuccessfully
produces the same output and log warning, and the driver stops before starting another external
turn.

## One `--execute` step, and what it deliberately leaves undone

```bash
python3 "<driver>" --project-root <project-root> --execute <TARGET_ID>
```

This runs exactly one sequence — executor, then each stored acceptance check, then the independent
reviewer — and stops. The reviewer writes its criterion results to
`STAGE_REVIEW_VERDICT_FILE`; the driver reads only that JSON to decide approval. A missing,
malformed, or non-approving verdict file fails the review, as does a nonzero reviewer command.
The step records attempt state under `.stage/.runtime/driver/`, then prints the outcome and the
recommended next action.

If the driver process stops after recording a completed-stage checkpoint, continue that same
attempt with:

```bash
python3 "<driver>" --project-root <project-root> --resume <TARGET_ID>
```

Do not use another `--execute` while an interrupted role remains. Resume selects the item carrying
that role, compares the repository with its saved checkpoint, and refuses to skip work if anything
changed afterward. An `executor` checkpoint runs acceptance and independent review; a `reviewer`
checkpoint reruns only the independent reviewer. If the executor died before a completed checkpoint
was recorded, or a person deliberately changed or committed its result, use `--reset-attempts`
with a one-line reason before starting a new executor turn. The reset targets the interrupted item,
not whichever leaf would otherwise run next.

It does **not** commit, close the card, escalate, promote official truth, advance the parent, or
move on to the next item. Those stay with the human supervising the run, so the recommended next
action is something a person still performs.

Do not edit files, stage or commit changes, switch branches, or run other repository-changing Git
commands in the same checkout while a driver step is running. The executor receives a disposable
Git index, so its `git add` cannot change the human's real index, but the working tree and `HEAD`
remain shared process-wide state. Wait for the step to stop before changing the repository.

Three conditions end a step in `blocked` instead of a retry: an exhausted limit, a `NO-PROGRESS`
fingerprint, and an independent reviewer JSON verdict with failed criteria. All three recommend
`escalate_work.py`; the driver never escalates itself and never claims verified completion. A first
successful no-change round is the narrower exception: it says the work appears complete and sends
the human through explicit verification and review. When the exhausted item is an action,
escalation also blocks its story and creates the human decision at that story: the next instruction
is to re-decompose the story, not to rerun the same action. Other stories in the epic continue.

**A failed verdict is where supervised and unattended part.** The round trip is the same in both —
the next executor dispositions each failed criterion as accept, decline, or defer, with a one-line
reason in its append-only shared-log report — but who starts the next round differs:

- **Unattended** runs the round trip itself, bounded by `max_attempts_per_item`. It restores the
  pre-review lifecycle and executes again without asking.
- **Supervised** stops and hands the decision to the human. `escalate_work.py` is the recommended
  action, not the only legal one: the human may instead run another `--execute` step, which the
  driver treats as the disposition round. It reads the failed criteria from the verdict file before
  the executor starts, gives that executor the same file, and clears the verdict only when the
  reviewer runs again. A round that declines or defers every criterion is allowed to change nothing.

What is forbidden is rerunning with unchanged input. A verdict is a judgment on the result, not a
transient failure, so the same executor over the same card and the same log will earn the same
verdict. A recorded disposition is what makes the next round a different question.

Reviewer prose remains human-readable context, but no label inside it decides the machine result —
only the JSON verdict does.

`NO-PROGRESS` means the fingerprint — staged and unstaged tracked changes against `HEAD`, the path
and content hash of each untracked non-ignored file, and the acceptance output — is identical to
the previous attempt. Separately, a successful executor that leaves the repository state unchanged
must append a valid report. The first such round does not spend an attempt: the driver says the work
appears complete and stops before acceptance or review. Close the card manually with
`close_work.py` so verification and review still run through an explicit path. The same unchanged
repository state in a later round stops as `NO-PROGRESS`.

## `--unattended` — read this before using it

```bash
python3 "<driver>" --project-root <project-root> --unattended <TARGET_ID>
```

This runs the whole ready subtree without stopping: select, execute, verify through
`close_work.py` (acceptance plus mandatory independent review), and repeat while any card success
criterion still fails. Each round is represented by one cumulative checkpoint commit so
close-time review can open every changed path; a later round replaces that checkpoint rather than
stacking partial-result commits. Only a passing review keeps the item commit. Each close attempt
prepares the neutral retrospective required by the closure gate; a failed attempt removes that
temporary lifecycle material, while a passing attempt closes the card and then closes parents as
their children go terminal. It works on a fresh isolated
`stage/driver/<target>-<unixtime>` branch and refuses to start if the working tree is dirty, so the
base branch is never touched. After a successful leaf run, the driver removes its clean worktree
but retains the branch and prints both names. Review the result, then run the landing command above
with that printed path; it recreates the absent worktree when exactly one matching retained branch
exists. A parent run that changed descendant lifecycle records is outside the landing command's
target-and-ancestors allowance and remains an explicit handoff instead of being widened silently.

The card's `max_attempts_per_item` limit is the reviewer/executor round-trip limit. The reviewer
writes `criteria` objects and `approved` to `STAGE_REVIEW_VERDICT_FILE`. The next executor receives
that same path and must append exactly one disposition for every criteria object whose verdict is
`FAIL`:

```text
Review dispositions (JSON):
[{"finding":"<exact criterion string>","disposition":"accept","reason":"<one-line reason>"}]
```

`disposition` is exactly `accept`, `decline`, or `defer`. Findings stay in JSON order and must
match each `criterion` exactly. Every choice requires a non-empty one-line reason. A round that
declines or defers every finding may make no repository change, but it must still append its
executor report with an empty changed-path array. An accepted finding requires repository
progress. Out-of-criteria
observations do not enter this blocking round trip.

When all criteria pass, the cumulative checkpoint becomes the item commit. When the round-trip
cap is reached, the driver removes every item checkpoint while retaining the cumulative files in
the working tree, then escalates for human attention; executor output is not committed. A command
timeout, missing command, or terminated tool is infrastructure failure and does not spend a card
attempt. Reviewer infrastructure is retried without rerunning the executor — but only while the
verdict file holds nothing that blocks. The driver reads that file after the failure: it retries
free when the file is absent (the reviewer never got far enough to judge) or holds a valid
approving verdict (the failure came after the judgment). A malformed or non-approving verdict is
the reviewer's answer, so it spends the attempt even when the output also carries an
infrastructure marker. The global iteration, wall-clock, and reap-failure limits still stop the run, so
unavailable tools cannot create an unbounded loop. Session reuse belongs to the configured executor command; whether it reuses a
session or starts fresh, the shared log is the recovery input for every round.

**It refuses to start without a `limits` config.** An absent `limits` object is not "no ceiling" —
it is a missing decision, and an unbounded autonomous loop is forbidden. Configure
`max_attempts_per_item`, `max_iterations`, and `max_wall_clock_seconds` together, or the run does
not begin. `max_attempts_per_item` remains fixed per selected action. The configured iteration and
wall-clock values are minimums; at run start the driver raises them to at least
`unfinished leaves * attempts` and `unfinished leaves * 900` — or `unfinished leaves * --timeout`
when an override was given — so a top-level run has enough budget for its actual subtree. The
derived per-command timeout does not enter that floor, so a card's declared size never scales the
global time budget twice.

**Status: reviewed in code and known code defects closed, but never exercised on real work.** The
unattended loop has been through independent code review, and the defects those reviews identified
have been fixed and archived, including W-00000075's lifecycle-commit and parent-audit failures.
It has tests, but no run has yet driven actual work through it end to end. Treat it as unproven: do
not present it as an ordinary alternative to `--execute`, and do not point it at work that matters
until someone has watched it complete a real subtree. When a user asks for autonomy, supervised
`--execute` is the default answer.

## Where the contract lives

Do not restate the driver's rules elsewhere — they are owned by:

- `stage/docs/SCHEMA_V4.md` — `### Supervised driver and executor settings` (selection, executor
  settings shape and per-platform variable syntax, dry-run and execute contract, runtime state),
  `### Unattended driver loop`, `### Execution limits settings`.
- Decision records: `DE-00000013` (the driver is a component separate from the gates),
  `DE-00000023` (supervised MVP), `DE-00000024` (unattended mode runs on an isolated branch),
  `DE-00000034` (what the three roles hand each other, what counts as evidence, and what a failed
  turn leaves behind).

## Verify

A dry run against a real parent or runnable leaf is the check that the wiring holds:

```bash
python3 "<driver>" --project-root <project-root> <TARGET_ID>
```

Expect a printed selection with a resolved executor, resolved acceptance commands, and a resolved
independent reviewer. Any `Outcome: blocked — ...` line names the missing piece; fix that before
running with `--execute`.
