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
reviewer — and stops. A reviewer that exits non-zero or emits a `BLOCK:` verdict is a failure. The
step records attempt state under `.stage/.runtime/driver/`, then prints the outcome and the
recommended next action.

It does **not** commit, close the card, escalate, promote official truth, advance the parent, or
move on to the next item. Those stay with the human supervising the run, so the recommended next
action is something a person still performs.

Do not edit files, stage or commit changes, switch branches, or run other repository-changing Git
commands in the same checkout while a driver step is running. The executor receives a disposable
Git index, so its `git add` cannot change the human's real index, but the working tree and `HEAD`
remain shared process-wide state. Wait for the step to stop before changing the repository.

Three conditions end a step in `blocked` instead of a retry: an exhausted limit, a `NO-PROGRESS`
fingerprint, and an independent reviewer `BLOCK:` verdict. A reviewer BLOCK escalates
unconditionally — it is a judgment on the result, not a transient failure, so rerunning the step
is never the answer to it. All three recommend `escalate_work.py`; the driver never escalates
itself and never claims completion. When the exhausted item is an action, escalation also blocks
its story and creates the human decision at that story: the next instruction is to re-decompose
the story, not to rerun the same action. Other stories in the epic continue.

A BLOCK puts the reviewer's voice in front of the human; it does not decide for the human. After
any verdict, disposition each finding — accept, decline, or defer — with a one-line reason in the
card's `## Verification` (stage-retrospective checks this at close). Reviewer severity (P1/P2)
ranks code-view impact, not this project's priorities: a P1 may be declined with a recorded
reason. Out-of-criteria observations never block the card; they enter the same disposition step.

`NO-PROGRESS` means the fingerprint — staged and unstaged tracked changes against `HEAD`, the path
and content hash of each untracked non-ignored file, and the acceptance output — is identical to
the previous attempt. Separately, an attempt whose repository state is identical before and after
the executor fails immediately, even on its first run and regardless of exit code. If the work was
already complete before the step, close the card manually with `close_work.py` so verification and
review still run through an explicit path.

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
base branch is never touched; the human reviews and merges that branch.

The card's `max_attempts_per_item` limit is the reviewer/executor round-trip limit. When a reviewer
logs failed criteria, the next executor receives the same `STAGE_WORK_LOG_PATH` and must append
exactly one disposition for every latest `CRITERIA VERDICT:` line containing `FAIL`:

```text
Review dispositions (JSON):
[{"finding":"<exact FAIL line>","disposition":"accept","reason":"<one-line reason>"}]
```

`disposition` is exactly `accept`, `decline`, or `defer`. Findings stay in reviewer order and must
match exactly. Every choice requires a non-empty one-line reason. A round that declines or defers
every finding may make no repository change, but it must still append its executor report with an
empty changed-path array. An accepted finding requires repository progress. Out-of-criteria
observations do not enter this blocking round trip.

When all criteria pass, the cumulative checkpoint becomes the item commit. When the round-trip
cap is reached, the driver removes every item checkpoint while retaining the cumulative files in
the working tree, then escalates for human attention; executor output is not committed. A command
timeout, missing command, or terminated tool is infrastructure failure and does not spend a card
attempt. Reviewer infrastructure is retried without rerunning the executor. The global iteration,
wall-clock, and reap-failure limits still stop the run, so unavailable tools cannot create an
unbounded loop. Session reuse belongs to the configured executor command; whether it reuses a
session or starts fresh, the shared log is the recovery input for every round.

**It refuses to start without a `limits` config.** An absent `limits` object is not "no ceiling" —
it is a missing decision, and an unbounded autonomous loop is forbidden. Configure
`max_attempts_per_item`, `max_iterations`, and `max_wall_clock_seconds` together, or the run does
not begin. `max_attempts_per_item` remains fixed per selected action. The configured iteration and
wall-clock values are minimums; at run start the driver raises them to at least
`unfinished leaves * attempts` and `unfinished leaves * per-command timeout`, respectively, so a
top-level run has enough budget for its actual subtree.

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
