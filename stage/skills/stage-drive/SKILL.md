---
name: stage-drive
description: Run registered Stage work through an executor instead of doing it by hand — the driver picks the next ready leaf under a parent work item, runs the venue's executor on it, re-runs its acceptance checks, and has a different venue review the result. Use when asked to drive, auto-run, or batch-execute Stage work, to preview which item the driver would take next, to set up the `executors` commands it needs, or to run a whole subtree unattended. This is execution; registering work is stage-work and passing work to a human-opened window is stage-handoff.
---

# Stage Drive

`drive.py` is the executing end of the harness. Everything else in Stage records intent and truth;
this runs the work. It never creates work items, approves a decomposition, promotes official truth,
or crosses a human-approval gate — it only carries out cards that already exist.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/drive.py" --project-root <project-root> <TARGET_PARENT_ID>
```

The driver ships beside this skill, so `${CLAUDE_PLUGIN_ROOT}/scripts/drive.py` is the path that
resolves wherever the plugin is installed — every command here uses it. The one exception is the
Stage source checkout itself, where the driver is a repository file: there, and only there,
substitute `stage/scripts/drive.py`. The target is a **parent** work item — the driver works on
its children, never on the target itself.

## The default run is a dry run

Invoked with no mode flag, the driver only reports. It prints the item it would select, the
executor command, the acceptance checks, the independent reviewer, and the next attempt and
iteration counters. It runs no command, creates no `.stage/.runtime/` state, and changes nothing.

Reach for this first, every time. It answers "is this project even wired up to drive?" without
side effects.

## What it will pick

A candidate must be a direct, non-terminal child of the target, be a leaf (no non-terminal children
of its own), and carry a **non-empty `acceptance` list**. Ties break deterministically by work item
ID, so the same repository state always selects the same item.

A card with no acceptance commands is invisible to the driver — there is nothing for it to verify,
so it will not run it. Unattended mode narrows further: `active`, `autonomous: true`, and anywhere
in the subtree rather than only a direct child.

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
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/drive.py" --project-root <project-root> --execute <TARGET_PARENT_ID>
```

This runs exactly one sequence — executor, then each stored acceptance check, then the independent
reviewer — and stops. A reviewer that exits non-zero or emits a `BLOCK:` verdict is a failure. The
step records attempt state under `.stage/.runtime/driver/`, then prints the outcome and the
recommended next action.

It does **not** commit, close the card, escalate, promote official truth, advance the parent, or
move on to the next item. Those stay with the human supervising the run, so the recommended next
action is something a person still performs.

Three conditions end a step in `blocked` instead of a retry: an exhausted limit, a `NO-PROGRESS`
fingerprint, and an independent reviewer `BLOCK:` verdict. A reviewer BLOCK escalates
unconditionally — it is a judgment on the result, not a transient failure, so rerunning the step
is never the answer to it. All three recommend `escalate_work.py`; the driver never escalates
itself and never claims completion.

`NO-PROGRESS` means the fingerprint — the tracked-file `git diff` plus the acceptance output — is
identical to the previous attempt. Untracked files are invisible to `git diff`, so an executor
whose only output is new files fingerprints as no progress even though it worked. Read the label
as "nothing the fingerprint watches changed", not as proof that the executor did nothing.

## `--unattended` — read this before using it

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/drive.py" --project-root <project-root> --unattended <TARGET_PARENT_ID>
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

**Status: reviewed in code, never exercised on real work.** The unattended loop has been through
two independent code reviews; both demanded changes, all eleven findings were fixed, and no pass
verdict exists on record — the reviewer's final verdict was never retrieved. It has tests, but no
run has yet driven actual work through it end to end. Treat it as unproven: do not present it as an ordinary alternative to `--execute`, and do not
point it at work that matters until someone has watched it complete a real subtree. When a user
asks for autonomy, supervised `--execute` is the default answer.

## Where the contract lives

Do not restate the driver's rules elsewhere — they are owned by:

- `stage/docs/SCHEMA_V4.md` — `### Supervised driver and executor settings` (selection, executor
  settings shape and per-platform variable syntax, dry-run and execute contract, runtime state),
  `### Unattended driver loop`, `### Execution limits settings`.
- Decision records: `DE-00000013` (the driver is a component separate from the gates),
  `DE-00000023` (supervised MVP), `DE-00000024` (unattended mode runs on an isolated branch).

## Verify

A dry run against a real parent is the check that the wiring holds:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/drive.py" --project-root <project-root> <TARGET_PARENT_ID>
```

Expect a printed selection with a resolved executor, resolved acceptance commands, and a resolved
independent reviewer. Any `Outcome: blocked — ...` line names the missing piece; fix that before
running with `--execute`.
