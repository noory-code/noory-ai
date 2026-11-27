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

A criterion that fails on concrete inputs fails for a kind of input, not for those inputs alone.
The reviewer names that kind in the `reason` beside its examples. An executor that accepts the
finding names the kind, fixes every input of that kind, and adds a test for each variant it covers.
Fixing only the quoted examples lets the next round quote the next example, and the cap runs out on
a sequence of near-identical rounds (Dasina R-00000028: one undersized control per round; Dasina
R-00000031: one rejected Japanese sentence per round).

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
