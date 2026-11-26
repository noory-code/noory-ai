# Review

This document owns the external-review gate.

## Gate

When an external review (another agent such as codex, a human reviewer, or a
tool) reports findings, do not accept them uncritically:

1. Anchor on the work's purpose and `official/canon` truth first — the review is
   measured against the goal, not the other way around.
2. Judge each finding against that purpose: does it protect a behavior an honest
   user relies on, or is it an edge that never arises from honest use?
3. Rebut findings that do not serve the goal. State the rebuttal and the essence
   it is measured against, then send the rebuttal back for a counter-review.
4. Process only findings that survive the counter-review — purpose-aligned, with
   real impact. Record what was accepted and what was rebutted, and why.
5. Rebuttal is goal-alignment verification, not avoidance. Contrarian rejection
   or nitpicking that scatters the essence is itself a violation of this gate.
6. When rounds stop converging (the finding count does not shrink), the
   remaining edges are best-effort: document the boundary in the relevant
   artifact and stop, rather than chasing a full reimplementation.

## Sequence

`external review → local rebuttal (against purpose) → counter-review → process
survivors`. The rebuttal and its outcome are recorded so the decision is
auditable, not just made.

## Configuring when a review runs (`settings.json`)

The `review` block of `.stage/settings.json` declares, per lifecycle stage, HOW
STRONG a review runs — bound to a real command, never a bare label:

- `strengths` maps each level (`off`, `light`, `standard`, `deep`, `red-team`) to
  the command that level runs. The harness fixes no command; the project fills in
  a review that writes the reviewer-owned JSON verdict to the file named by
  `STAGE_REVIEW_VERDICT_FILE` (required shape and validation rules: the `review`
  comment in `templates/v4/project-stage/settings.jsonc`). `off`/empty means no
  review.
- `stages` picks the level for each stage: `design`, `implementation`, `promotion`.

Review is OPTIONAL and driven by the work item's own `review` field
(`not_required` | `pending` | `passed`; absent defaults to `not_required`):

- An item that never declares review (`not_required`/absent) completes with no
  review — the bypass. Most work needs no gate here.
- An item that declares `review: pending` opts THAT item in: it cannot be
  completed until `review: passed`. The completion gate blocks it, so even
  hand-editing `status: completed` is refused while `review: pending` — this is
  stronger than the verification field, which has no such requirement.

`close_work.py` runs the `implementation`-stage review only when the item is
`review: pending`: it deletes any prior verdict file, exports
`STAGE_REVIEW_VERDICT_FILE`, executes the resolved command, and records its
output as evidence. The review command, and an autonomous item's independent
review alike, runs under `--review-timeout` (default 3600 seconds), separate
from the per-check `--timeout` (default 900 seconds), so a high-effort review is
not cut off at the check budget. A review that exceeds it fails the close with
`[TIMED OUT after <n>s] (--review-timeout)`; a check that exceeds its budget
reads `(--timeout)` instead, so the evidence names the budget that ran out. The
unattended driver passes the larger of 3600 seconds and its per-command timeout
as `--review-timeout`, capped by the run's remaining wall clock, and bounds the
whole `close_work.py` run by every check's budget plus that review budget. The
review passes only when the command exits zero **and**
that file holds a valid verdict with `approved: true`. A missing, malformed, or
non-approving verdict fails the close even on a zero exit, and a zero exit with
an approving verdict passes it whatever the command printed — reviewer prose is
human-readable context, and no label inside it decides the machine result. On a
pass it sets `review: passed` and records the verdict on the card (see below).
Fail-closed: a pending item whose
stage has a typo'd strength or no bound command is refused until `settings.json`
is fixed (the audit reports `REVIEW001`). This keeps `review: passed` bound to an
executed verdict, never a hand-typed claim. Set the requirement with
`register_work.py --review`, and close with `close_work.py` (not by editing
frontmatter).

## How the reviewer judges

The reviewer judges by running, not by reading the executor's account (DE-00000101). Every
criterion in the verdict names its `method`:

| `method` | Meaning | Allowed verdict |
|---|---|---|
| `ran` | the reviewer ran a command or observed the behavior itself | `PASS` or `FAIL` |
| `read` | the reviewer read files or records | `PASS` or `FAIL` |
| `unable` | the reviewer could not gather the evidence the criterion needs | `FAIL` only |

```yaml
reviewer_rules:
  - if: the reviewer did not see a criterion's evidence itself
    then: the criterion is FAIL; the executor report, the work log, and code comments are claims
  - if: a criterion asks for a command result or observed behavior
    then: method is ran, from at least one command the reviewer chose itself; its reason names the command and what it showed
  - if: a criterion asks for a result that only a whole session, the user's machine, or the user can show
    then: method is read, from a line on the card's `## Verification` and under the rules of "A check recorded on the card"; without such a line method is unable
  - if: a criterion states a fact of the records (a decision exists, a document says something)
    then: method is read
  - if: the reviewer could not run what a criterion needs
    then: method is unable and the verdict is FAIL
close_work_rules:
  - if: a criterion has no method, or a method other than ran, read, unable
    then: the verdict is invalid and the close fails
  - if: a criterion is PASS with method unable
    then: the verdict is invalid and the close fails
  - if: a criterion is FAIL with method unable
    then: the close fails and names that criterion's number; the rejection line goes on the card
```

`close_work.py` runs the card's stored `acceptance` checks before the review. Running one of them
again on the same tree shows the reviewer nothing new, so the review commands ask for a probe of
the reviewer's own instead.

What those checks printed reaches the reviewer through the work log, which every review command
reads (`$STAGE_WORK_LOG_PATH`). Before the review command starts, `close_work.py` appends one
`### Checks at close` section (`skills/stage-retrospective/review_material.py`):

```yaml
checks_at_close_section:
  holds: each passed check's command and the end of its output, in the order run
  bound_per_check: the last 60 lines and 6000 bytes
  bound_per_close: 30000 bytes of output; with more than five checks each gets an equal share
  when_cut: one line says how many earlier lines were left out
  output_lines: indented by four spaces, so a line of output is never read as a work-log heading
    or a report field
  written_when: a review runs at this close; a card that needs no review gets no section
  not_written: on the card, which keeps the commands only
```

The reviewer reads the paths the HEAD commit changed. `close_work.py --review-commit <rev>`
(repeatable) hands it the paths of the named commits instead, for a card whose code is not in
HEAD (O-00000058); `close_work.py` warns when the default list holds only `.stage/` paths.

The method is what the reviewer reports about itself. `close_work.py` does not read the
reviewer's tool calls, so it cannot tell a reviewer that wrote `ran` without running, and the
reviewer decides which criteria need a run. DE-00000101 chose this knowingly; a verdict that
claims to have seen what its named command cannot show is the stated reason to add a check of
the tool calls.

## What the close sees of the reviewer

A reviewer that may run any shell command can also do what a judgment should not rest on. The
close looks for it after every review command it runs (`skills/stage-retrospective/review_containment.py`,
W-00000416). The supervised driver's reviews between rounds get the first row only.

| What the reviewer, or the code its commands run, does | What the close does |
|---|---|
| leaves a tracked or untracked file changed, created, or deleted | fails the review, removes the verdict, names the paths |
| changes such a file and puts the earlier content back (`git checkout`, `git restore`, `git stash`, writing the same bytes) | fails the review, removes the verdict, names the paths |
| writes, creates, or deletes a file Git ignores | passes or fails as the verdict says; prints a `WARNING` with the paths and writes the traces line on the card |
| runs a command, or calls a file tool, whose text names the session record folder (`~/.claude`, `$HOME/.claude`, the home folder's absolute path, `$CLAUDE_CONFIG_DIR`) or GitHub (`gh <subcommand>`, `api.github.com`) | the same: a `WARNING` with the commands, and the traces line |

```yaml
restored_file:
  seen_by: the file's inode, modified time, and change time differ although its content is the same
  why_it_fails: a reviewer that restores a file hides what its commands or the tests wrote (W-00000413)
  also_fails: anything else that rewrites a repository file during the review, for example an
    editor that saves an unchanged file
ignored_file:
  seen_by: its mode, size, or modified time differ, or it appeared or went away; content is not read
  not_compared: `.stage/.runtime/`, where the verdict, the work log, and the driver's state are written
  why_it_does_not_fail: test runs write caches (`__pycache__`, `.pytest_cache`, build output) into
    ignored folders, and those cannot be told from a write that matters
outside_record:
  seen_by: the text of each tool call the reviewer command wrote to `$STAGE_REVIEW_TOOL_CALLS_FILE`,
    one JSON object per line; `scripts/claude_review_companion.py` writes it from the reviewer's
    stream. A call the host refused is left out.
  why_it_does_not_fail: the text is matched, not the act; a command that searches the project for
    the string `~/.claude` is named too. The person who closes reads the commands and decides.
  when_the_record_is_cut_short: a `WARNING` says the record is incomplete
card_line: "- Reviewer traces at close <date>: ignored files written <n> (<paths>); commands naming
  <what> <n>; tool-call record incomplete" — only the parts that apply, on the line after that
  review's `- Review at close` line; no line when the review left none of them
when_you_see_a_warning:
  - if: the ignored paths are caches of the commands the reviewer ran
    then: nothing to do
  - if: an ignored path is a setting, a secret, or an input of the checks
    then: inspect it, put it back, and close again; the verdict was reached on a changed input
  - if: a command read session records or GitHub and a criterion's reason rests on what it read
    then: that criterion was not judged from the checkout; close again, or record an observation
```

The Claude stand-in also adds these rules to every prompt (`REVIEWER_RULES`): leave a changed file
in place and name it, do not restore it, and do not read the session record folder or GitHub.

### A change to what the reviewer may do

```yaml
reviewer_permission_change:
  if: a change touches the allow or deny rules a reviewer command passes to `claude` — in
    `scripts/claude_review_companion.py` the `Edit(<verdict file>)` rule, `shell_tools`,
    `DENIED_COMMANDS`, `denied_rules`, or the `--allowedTools` and `--disallowedTools` lists of
    `claude_command` — or the same two options in a project's own reviewer command
  then: before the card closes, run the real `claude` under the new rules on each platform whose
    rules changed, once on a call they must allow and once on a call they must refuse
  read_from: the output of `claude -p --output-format stream-json --verbose`, where each `tool_use`
    block names the tool the reviewer called and `permission_denials` in the `result` event
    names the calls that were refused
  record: both results on the card's `## Verification`, with the command line of each run
  platform_the_session_cannot_run: both results are a `- Checked` line from that machine
    ("A check recorded on the card")
  not_enough: a unit test of the lists, which checks the text of the rules and not how `claude`
    matches them
```

The verdict-file write rule in W-00000359 and the Windows PowerShell rule in W-00000374 were each
checked by running `claude` (R-00000374; first occurrence W-00000359).
`LiveReviewerWriteProbeTest` in `scripts/tests/test_claude_review_guard.py` is such a run for the
file-edit rule alone: a `Write` call is refused and shell commands run. It is skipped unless
`STAGE_LIVE_REVIEW_PROBE=1` is set and `claude` is on `PATH`.

Not held back, and not seen:

| What | Why |
|---|---|
| a change outside the repository: another checkout, the home folder, a temporary folder, a remote service | the comparison lists the repository's files only. DE-00000101 accepted this; one observed case is its stated reason to be revisited. |
| a read of an outside record by a command inside a script file, through `cd` into the folder, or through a path built at run time | only the text of the reviewer's own tool calls is matched |
| any outside read by a reviewer command that writes no tool-call record (Codex, a project's own command) | the close has nothing to read; it prints no warning for a missing record |
| reads of the remote through Git (`git fetch`, `git ls-remote`) and of any site other than `api.github.com` | they are not in the matched list |
| a change inside `.git` (a stash, a ref, a fetched object) or inside `.stage/.runtime/` | neither is in the comparison |
| a restore that also sets the file's times back. On POSIX the change time cannot be set, so this needs a changed clock; on Windows a tool that restores the modified time in place is not seen | the restore is seen through the file's identity and times only |
| `git push` or `git commit` inside another program (`sh -c`, a script) | the deny rules match the reviewer's own command line (W-00000408) |

Stopping these reads instead of naming them needs the reviewer's shell to be narrowed: an OS
sandbox that hides the home folder and the network, which is not available on every host Stage
supports, or a home folder of the reviewer's own, which takes its credentials away. DE-00000101
widened the shell, so this document names the reads and does not stop them.

## A check recorded on the card

Some criteria cannot be judged by any command in the reviewer's checkout. The reviewer judges
each of them with method `read` from one line on the card's `## Verification`, and from nothing
else. The line is written before the close and committed with the card.

| What the criterion needs | Line on `## Verification` | Who writes it |
|---|---|---|
| a whole session doing the thing (a new cloud session takes a role and does something) | `- Observed <date> by verify session <session-id> ...`; `stage-orchestrate`, "Start a verify session", owns its form | the PO session, from the verify session's observation |
| the user's machine: another OS, an installed plugin, a device; or a trial of a changed procedure or a new path (`operations/verification.md`, "Rules"), done by a session other than the PM session that built the card | `- Checked <date> on <machine> at <commit>: <criterion> — <held\|did not hold>; <the command or action> — <what it showed>` | the session that ran the check on that machine, or the PO session from what the user or that session reported; for a trial, the session that did the trial, or the PO session from that session's report |
| the user's own judgment, or the user's reading of a check that does not match the criterion's words | `- User verdict <date>: <criterion> — <held\|did not hold>; "<the user's words>"; rests on <the `- Checked` line's date and machine, or what the user looked at>` | the PO session, from the user's message |

```yaml
line_parts:
  date: the day the check ran or the user answered, as YYYY-MM-DD
  machine: the OS and what else decides the result there — architecture, locale, the installed
    version of the thing checked; for a trial, the environment the session ran in (for example
    a cloud session's container)
  commit: the commit the checked tree was at
  criterion: the card's criterion, copied, or its number in `## Success criteria`
  command_or_action: what was run or done, exactly; for a command, the command line
  what_it_showed: the result that decides the criterion (for example `121 passed`), not `passed` alone
never_written_by: the PM session that built the card
not_a_record:
  - a statement in the executor report, the work log, a commit message, or a session's message
  - a paragraph under `## Verification` or `## Progress` that is not one of the three lines
reviewer_rules:
  - if: the card has no line for the criterion
    then: method is unable and the verdict is FAIL, as before
  - if: the line lacks a part named above
    then: method is read and the verdict is FAIL; the reason names the missing part
  - if: a `- Checked` or `- Observed` line names a commit that does not hold the card's change
      (`git merge-base --is-ancestor <code-commit> <named-commit>` fails, and
      `git diff <code-commit> <named-commit> -- <the changed paths>` prints a difference)
    then: method is read and the verdict is FAIL; the check ran on another tree
  - if: the newest line for the criterion says `did not hold` or `could not observe`
    then: method is read and the verdict is FAIL
  - if: the newest line for the criterion says `held` and has every part
    then: method is read and the verdict is PASS
  - if: a `- Checked` line says `did not hold` and a later `- User verdict` line says `held`
    then: the user's verdict decides — method is read and the verdict is PASS; the reason names both lines
  - always: the reason names the line's kind and date, for a `- Checked` line its machine too,
      and says the reviewer did not run the check
  - if: the reviewer's checkout can run what the criterion needs
    then: none of this applies; method is ran
```

The verify session and the session on the user's machine do not decide the close: the
reviewer still writes the verdict, and it fails a line that does not say what the criterion asks.
A `- User verdict` line is the user's judgment of the criterion, which the user owns; the
reviewer checks that the line has its parts and names the criterion, not whether the user judged
well.

What this does not give: the reviewer cannot tell a line that describes a check nobody ran. It
reads the record; it does not see the machine. The card's `- Review at close` line marks such a
criterion `read`, the same mark a fact of the records gets, so the count of `read` marks does not
say how many criteria rest on a recorded check. The line itself stays on the card and says who
checked, where, and when.

## What close writes on the card

`close_work.py` completes the card only after every check and any required review
has passed. Before that point it writes one thing: when a review at close returns a
valid verdict that rejects the work, `## Verification` gains that review's line (below)
and every frontmatter field stays as it was. A failing check, a review command that
fails, and a missing or malformed verdict leave the card unchanged.

- Frontmatter: `verification: passed`, the final `promotion` value,
  `status: completed`, and `review: passed` when a review ran.
- When the work log holds an executor report, `## Progress` gains
  `### Executor report at close — <date>`: one fenced block with the latest
  report's `What changed:`, `Why:`, `Decisions made:`, and `Work not done:`
  lines, verbatim. A card closed without a driver run has no report and gains
  nothing here.
- `## Verification` gains one line for the checks that passed:
  ``- Checks at close <date>: <count> passed — `<command>`; `<command>` ``.
  Check output is not copied onto the card.
- Each review that `close_work.py` runs and that returns a valid verdict adds one
  line to `## Verification`, whether it approved or rejected:
  `- Review at close <date> by <reviewer>: <approved|rejected> (1 PASS ran, 2 FAIL read, ...)`.
  The numbers follow the verdict's criterion order, and each carries that criterion's verdict
  and `method`. A line written before the `method` key existed has the verdict only.
  `<reviewer>` is the reviewing
  venue for an autonomous item; otherwise it is the review command's `--label`, or the
  file name of the `STAGE_CODEX_COMPANION` override when that replaced a `codex`
  label, or `reviewer` when the command names none. Counting the `rejected` lines of
  archived cards gives the number of reviews at close that sent work back; counting the
  `ran`, `read`, and `unable` marks gives how the reviewers judged.
- `## Verification` gains the card's load, counted by `scripts/work_load.py` from the work log
  and the card as they stand at close:
  `- Load at close <date>: attempts <n>, review FAIL rounds <n>, repeated findings <n|unknown>, driver rounds <n>, driver failures <n> (timed out <n>)`,
  followed by one `  - Driver failure: <role> — <reason>` line per driver failure.

  | Count | Counted from |
  |---|---|
  | `review FAIL rounds` | the larger of: executor reports in the work log with a non-empty `Review dispositions (JSON):`; `rejected` review lines already on the card |
  | `attempts` | the largest of: `### Executor report` sections in the work log; `review FAIL rounds` + 1; the count in an imported report's `Attempt commits: <n> (...)` line, which `import_executor_report.py` writes from its `--commit` arguments |
  | `repeated findings` | adjacent answered rounds in the work log that share a `finding`; `unknown` when the work log holds fewer answered rounds than `review FAIL rounds` |
  | `driver rounds` | `### Driver commands` sections in the work log; `0` means no driver ran the card from this checkout |
  | `driver failures` | `### Driver failure` sections in the work log; `timed out` counts those whose `Reason:` contains `timed out` |

  `python3 stage/scripts/work_load.py --project-root . --closed-since <YYYY-MM-DD>` prints these
  counts for closed cards as a Markdown table with a totals row. A card closed before this line
  existed shows its `rejected` review lines and `not recorded` in the other columns.
  The table's last three columns, `Ran`, `Read`, and `Unable`, count the criteria of the card's
  last `- Review at close` line by `method`. That line is the verdict the close rests on; an
  earlier line is a round that sent the work back. `no review` means the card closed without a
  review, and `not recorded` that the line was written before verdicts named a method.
- A review that left traces adds `- Reviewer traces at close <date>: ...` after its review line
  ("What the close sees of the reviewer"). The paths are on the card; the commands are printed at
  close and are not copied.
- The reviewer's reasons and report are not copied onto the card. They stay in the
  work log (`.stage/.runtime/driver/logs/<work-id>.md`), which is not committed.
- Reviews that the drivers run between rounds are recorded in the work log only.

The executor report lines, the criteria with their methods, and the load counts live on the card because
the work log and the verdict file sit under `.stage/.runtime/`, which is not committed.
The card is the only durable record of what the executor decided, what the
passing review checked and how, and what the card took to land.

## Cross-venue review

When a project runs more than one venue (see `stage-handoff`, Delegated
execution), the default review posture is cross-venue: the venue that executed a
card does not review it. Same-model review shares the author's blind spots; the
counter-venue's review is what catches them.

- The executor of a card and the reviewer of that card must be different venues.
  This holds whether the card ran in its own window or by delegation.
- A delegated card is reviewed by the hosting window as part of closing it: the
  host verifies the delegated output against the card's success criteria before
  `close_work.py` runs. The host must not forward its own review back to the
  executing venue's model.
- A card executed by the window that will also close it binds the counter-venue
  through the review gate above: declare `review: pending` on the card
  (`register_work.py --review`) and bind the counter-venue's review command as
  the `implementation` (or `design`) stage strength in `settings.json`. The gate
  then refuses completion until the counter-venue's verdict passes.
- The rebuttal sequence at the top of this document applies to cross-venue
  findings unchanged: purpose first, rebut what does not serve it, process the
  survivors.
