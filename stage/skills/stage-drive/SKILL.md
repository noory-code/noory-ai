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

If the target has no non-terminal child, the driver selects the target itself when it is
non-terminal and has non-empty acceptance. Otherwise there is nothing to select.

A card with no acceptance commands is invisible to the driver — there is nothing for it to verify,
so it will not run it. Unattended mode narrows eligibility further to `active` and
`autonomous: true`; for a parent target, it searches the whole subtree rather than only direct
children, while a leaf target can select only itself.

## Two settings gates, both fail closed

**`executors` must exist before anything runs.** The `executors` object in `.stage/settings.json`
(or `settings.jsonc`) maps each venue to the command that carries out that venue's work. An absent
section, a missing venue, a malformed map, or an empty command stops the driver where it stands
with an escalation recommendation — it never falls back to running the work itself. The driver
passes the selected card to that command through `STAGE_WORK_ITEM`, `STAGE_WORK_ITEM_PATH`, and
`STAGE_PROJECT_ROOT`; the command text is shell-expanded, so its variable syntax is
platform-specific.

**The reviewer's venue must differ from the item's.** `review.reviewers` must resolve to exactly
one reviewer whose venue is not the selected item's venue. Configure only the item's own venue and
the driver refuses rather than letting a venue grade its own work.

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
itself and never claims completion.

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

This runs the whole ready subtree without stopping: select, execute, commit, write a neutral
retrospective, close through `close_work.py` (which re-runs acceptance and the mandatory
independent review), then repeat, closing parents as their children go terminal. It works on a
fresh isolated `stage/driver/<target>-<unixtime>` branch and refuses to start if the working tree
is dirty, so the base branch is never touched; the human reviews and merges that branch.

**It refuses to start without a `limits` config.** An absent `limits` object is not "no ceiling" —
it is a missing decision, and an unbounded autonomous loop is forbidden. Configure
`max_attempts_per_item`, `max_iterations`, and `max_wall_clock_seconds` together, or the run does
not begin.

**Status: reviewed in code, never exercised on real work, known defects open.** The unattended
loop has been through two independent code reviews; both demanded changes, and no pass verdict
exists on record — the reviewer's final verdict was never retrieved. Open defects remain, tracked
as W-00000075 in the Stage source repository: three of the four places where the loop commits
Stage bookkeeping do not check that the commit succeeded, and a parent whose card carries its own
acceptance list closes without the structural audit. It has tests, but no run has yet driven
actual work through it end to end. Treat it as unproven: do not present it as an ordinary
alternative to `--execute`, and do not point it at work that matters until someone has watched it
complete a real subtree. When a user asks for autonomy, supervised `--execute` is the default
answer.

## Where the contract lives

Do not restate the driver's rules elsewhere — they are owned by:

- `stage/docs/SCHEMA_V4.md` — `### Supervised driver and executor settings` (selection, executor
  settings shape and per-platform variable syntax, dry-run and execute contract, runtime state),
  `### Unattended driver loop`, `### Execution limits settings`.
- Decision records: `DE-00000013` (the driver is a component separate from the gates),
  `DE-00000023` (supervised MVP), `DE-00000024` (unattended mode runs on an isolated branch).

## Verify

A dry run against a real parent or runnable leaf is the check that the wiring holds:

```bash
python3 "<driver>" --project-root <project-root> <TARGET_ID>
```

Expect a printed selection with a resolved executor, resolved acceptance commands, and a resolved
independent reviewer. Any `Outcome: blocked — ...` line names the missing piece; fix that before
running with `--execute`.
