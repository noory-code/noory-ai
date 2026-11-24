# Cloud Execution

This document owns how a work card runs in an execution environment that lacks the
venue `venue_routing` would pick — typically a Claude Code cloud session, which has
no Stage hooks, no `.stage/.runtime/`, and no Codex. The policy behind it is
DE-00000082; the card field is `environment:` (`docs/SCHEMA_V4.md`).

## Policy

`settings.json` declares which venue runs in each environment:

```json
"environment_venues": { "cloud": "claude" }
```

A card may contradict `venue_routing` without a venue exception decision when all
three hold. `register_work.py`, `start_work.py`, and the audit (VENUE006) check the
same conditions through `stage_work.environment_venue_error()`:

| Condition | Why |
|---|---|
| `environment:` names a declared environment | the project chose that environment on purpose |
| `venue:` is the venue declared for it | `venue` records who actually executed |
| `review:` is `pending` (or `passed` after close) | the routed reviewer venue is absent, so an independent close review is required |

The split rule for mixed kinds still applies; it separates design from
implementation and is not about who executes.

## Register or start

```bash
python3 stage/skills/stage-work/register_work.py --project-root . --title "..." \
  --kind fix --scale story --environment cloud --review --scope "..." \
  --purpose "..." --success-criterion "..."
python3 stage/scripts/start_work.py --project-root . W-00000001 --scope "..." \
  --environment cloud --review
```

`--environment` fills an omitted `--venue` with the environment's venue. Take
decision and other record numbers from `stage/scripts/stage_record_ids.py`; parallel
sessions work on parallel branches. That command, `register_work.py`, and
`manage_roadmap.py` reserve each new id on the remote as `refs/stage-ids/<id>`
(DE-00000092). A cloud session's git proxy may refuse that push — this repository's
did with HTTP 403 (W-00000378) — and the id is then chosen from fetched refs only,
with a `not reserved on the remote` line; fetch before registering and push right after.

## Execute (in the environment)

- Commit and push only to the session branch; never to the base branch.
- Stage hooks do not run, so scope is checked at close by comparing
  `git diff --name-only` with the card's `scope`.
- The shared work log does not exist, so write the `### Executor report` in the
  commit body. Keep each field on one line; the importer also joins wrapped lines.
- The SessionStart text does not exist either. A session started with
  `scripts/subsession_brief.py` gets the same index at the end of its brief ("Session index").

## Session index

A session on the device starts with the SessionStart hook's text: Stage's standing rules and an
index made from the records (DE-00000100). A cloud session has no hook, so
`subsession_brief.py` ends every brief with that index, built by the same function
(`hooks/stage_context.py`, `session_index`).

| The index carries | One line is | Read the body at |
|---|---|---|
| what is being done now | an active milestone, a current card, an open observation, an open question, a selected planned card | the record the line names |
| decisions | a decision's id and title, newest first | `.stage/decisions/pending/<id>.md` or `.stage/official/decisions/records/<id>.md` |
| where rules live | the path of a project instruction file or a `.stage/operations/` file | that file |
| rule candidates | a candidate from `.stage/state/rule-candidates.md` with how often it was seen | that list, then the retrospectives it cites |
| how to find a record | where decision bodies and retrospectives are | — |

The index never carries a record's body. A title says the topic and not what was chosen, so open
the record before relying on it.

```yaml
limit:
  hook_text: 10000 characters, the rules and the index together
  brief: 10000 characters, the brief and the index together
over_the_limit:
  never_shortened: what is being done now, and the rules or the brief itself
  shortened_in_this_order:
    - rule candidates, from the end of the shown list. The index shows `proposed: promote`
      candidates first and `proposed: hold` ones after them, each group in the list's order,
      so the hold ones are left out first.
    - decision titles, from the oldest
    - the previous session's handoff
    - the list of project instruction files
    - the list of `.stage/operations/` files
  each_shortened_block: keeps one line `…<n> <what> not shown — read <where>`
  if_still_over: the end of the text is cut and its last line says so
```

The limit is a first value taken from the size the text had when it was chosen, not from a
measurement. When decision titles start to be left out, that is the reason to look at the number
and the order again (DE-00000100, "Follow-up"). The order was looked at once (W-00000413): with
39 rule candidates the index showed 36 of them and no decision title, so candidates now give way
first. A decision binds work; a candidate is not yet a rule.

## Sessions on the card

A card's `## Sessions` section names each session that worked on it, so a later reader can open
that session's transcript. The main session writes the line when it records the session's report;
a session that works alone on the device writes its own.

```markdown
## Sessions

- session_01AbC… — work — 2026-11-23 — opened from the index: DE-00000094, DE-00000100
- session_01XyZ… — verify — 2026-11-24 — opened from the index: none
```

```yaml
one_line_per_session:
  - the session id as the platform prints it; `unknown` when the host gives the session none
  - its role: `work`, `verify`, `orchestrator`, `discussion`, `planning`, or `consolidation`
    (`orchestrator` aside, the `--role` values of `subsession_brief.py`)
  - the date it reported
  - "opened from the index: <ids>": the records the session says it opened because the session
    index listed them, copied from its report; `none` when it opened none; `not reported` when
    the report does not say
```

The last item is the only record of whether a session used the lines it was given. It is the
session's own account, not a measurement.

What the line does not give: a transcript the platform no longer keeps, a session that ran on
another device, and a run by another executor (codex, agy) cannot be read from this id. Keeping
the raw work log in a committed place is a separate matter and is not decided here.

## Import the report

```bash
python3 stage/scripts/import_executor_report.py --project-root . W-00000001 --commit <code-commit>
```

It validates the report against the executor contract and that commit's changed
paths, and appends it to the work log only when it passes. When the card took
several attempts, pass `--commit` once per attempt commit, oldest first: the
report is read from the last one, and its `Changed paths (JSON)` must list every
path those commits changed, as the contract requires. List the commits instead
of a range so another card's commits in between are left out.

The importer ends the imported report with `Attempt commits: <n> (<sha>, ...)`, the distinct
commits it was given. The close counts the card's `attempts` from that line
(`operations/review.md`), so a squashed card keeps its attempt count although the work log is
not committed.

## Close

1. Close from a worktree checked out at the card's code commit
   (`git worktree add --detach <path> <code-commit>`), because the review receives
   the paths of the HEAD commit. When the code is in other commits than HEAD, pass
   `--review-commit <rev>` to `close_work.py` once per commit instead: the review then receives
   every path those commits changed (O-00000058). `close_work.py` prints a WARNING when the
   paths it is about to hand over are all under `.stage/`.
2. Import the report there, reserve the retrospective
   (`close_work.py --allocate-retrospective` prints its id), and write it. Then link it on the
   card: set `retrospective: completed` and `retrospective_ref: <R-id>` in the card's frontmatter.
   `close_work.py` stops before the checks and the review while either field is unset.
3. When the routed reviewer venue is unavailable too, keep `settings.json`
   unchanged and run the project's configured review through the Claude stand-in:

   ```bash
   STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py \
     python3 stage/skills/stage-retrospective/close_work.py --project-root . W-00000001 \
     --check "<suite>" --promotion <final-choice>
   ```

   `close_work.py` runs the card's stored `acceptance` checks by itself. Pass `--check` only for
   a command the card does not store; one that repeats a stored check runs and is recorded once.
   It appends what those checks printed to the work log as `### Checks at close` before the
   review command starts, so the reviewer reads their output there (`operations/review.md`).

   The reviewer judges by running (DE-00000101; `operations/review.md`, "How the reviewer
   judges"), so the stand-in lets it run any shell command: the card's checks (for example
   `audit_stage.py`) and commands it chooses itself. Its file-edit tools may write only the
   verdict file, and it may read the changed-path folder. The project's own Claude reviewer
   command runs through the same stand-in. Never write a verdict file by hand.

   | What could go wrong | What holds it |
   |---|---|
   | a shell command, or code the tests run, writes a project file | `close_work.py` compares the repository before and after every review command: when any file other than the verdict changed, or was changed and restored, it removes the verdict, names the paths, and fails the close review. Inspect and discard those changes before closing again. |
   | the reviewer writes a file Git ignores, or reads the session record folder (`~/.claude`) or GitHub | `close_work.py` prints a `WARNING` and writes a `- Reviewer traces at close` line on the card; the review is not failed. `operations/review.md`, "What the close sees of the reviewer", says what to do with it and what is not seen. |
   | the reviewer commits or pushes | the stand-in denies `git push` and `git commit`, alone or inside a compound command line. A command hidden inside another program (`sh -c`, a script) is not seen. |
   | the reviewer changes something outside the repository (another checkout, the home folder, a remote service) | nothing. DE-00000101 accepted this weakness; when you see one case, record an observation, because it is that decision's stated reason to be revisited. |
4. State on the card's `## Verification` that the close review was a same-model
   review, not a cross-venue one.

   When the review fails, `close_work.py` leaves a `- Review at close ... rejected` line on the
   worktree's card. Copy that line onto the branch's card and commit it before the next attempt:
   the next close counts those lines into the card's `- Load at close` line
   (`operations/review.md`), and a line left in a removed worktree is lost.
5. Copy the closed card and retrospective back to the branch and run
   `close_work.py <id>` there once more; its reconcile path refreshes the decision index.

## Close a sub-session's card

A card handed to a cloud sub-session (`stage-orchestrate`, "Start a work session") is closed
by the main session, never by the sub-session (DE-00000094). The sub-session's branch starts at the
main session's start commit, so its diff is exactly the card's change.

1. Send the sub-session one message before anything else: the review of commit `<reported-sha>`
   starts, and it pushes no commit until the main session answers. Then
   `git fetch origin <sub-session-branch>` and compare `git rev-parse FETCH_HEAD` with the
   reported commit. When they differ, the sub-session pushed after its report: ask it which
   commit to review, and restart this step with its answer.
   Add the sub-session's line to the card's `## Sessions` ("Sessions on the card") in the same
   commit that records its report.
2. Squash it onto the main session's branch as one commit that carries the sub-session's executor
   report: `git merge --squash FETCH_HEAD`, then commit with a message of your own. Its subject
   is `<type>(<scope>): <the card's whole change> (<W-id>)`; the last commit of the sub-session's
   branch names only its last step. Its body is that commit's body, unchanged:
   `git log -1 --format=%b FETCH_HEAD` prints it. Write both to a file outside the repository and
   run `git commit -F <file>`. The review receives the paths of HEAD (O-00000058), so one squash
   commit hands the reviewer every path; no local-only commit is needed.
3. Re-run the card's checks yourself; do not trust the sub-session's transcript.
4. When a verification session observed a criterion that only a session can observe
   (`stage-orchestrate`, "Start a verification session"), its observation is on the card's
   `## Verification` before this step, committed on the main session's branch. The close review
   is the only gate; no verification session has to pass first.

   ```yaml
   before_closing:
     - if: the card's `## Sessions` has a `verify` line
       then: confirm `## Verification` has a `- Observed ... by verification session <that id>`
         line for each criterion that session was given. When one is missing, write it from the
         session's observation and commit it first: the reviewer fails a criterion it has no
         evidence for, and an observation left in a session's message does not reach it.
     - if: a criterion names something only the user's machine or the user can show
       then: confirm `## Verification` has a `- Checked` or `- User verdict` line for it
         (`operations/review.md`, "A check recorded on the card"). When the check ran and only
         prose records it, write the line from that prose and commit it first. When no check ran,
         take "Merge a card that waits for the user's machine" or ask the user.
   ```

   Import the report (`import_executor_report.py <W-id> --commit HEAD`), reserve and write the
   retrospective, link it on the card, and close with the review as in "Close" above. When the
   review fails, commit the card with its new `rejected` review line on the main session's
   branch, keep `.stage/.runtime/driver/logs/<W-id>.md` in place, send the failed criteria to the
   sub-session, and repeat from step 1 after it pushes ("Import again after a rejected close
   review"). The close that passes counts the rejected lines and the reports in that log into the
   card's `- Load at close` line.
5. Archive the card, push, and open the pull request from the main session's branch. The
   sub-session's branch is not merged on its own.

A work session that built an epic leaves one commit per story, each with that story's executor
report. Bring them over one by one instead of squashing (`git cherry-pick <story-commit>`, oldest
first), and run steps 3 and 4 for each story at its commit. Close the stories without `--archive`,
then close and archive the epic.

### Import again after a rejected close review

The main session's branch already holds the first squash commit and, above it, the commit that
records the `rejected` line. The sub-session's branch holds the first change and the fix as its
own commits, so the second `git merge --squash FETCH_HEAD` conflicts in every file both attempts
changed (W-00000410: six files).

```yaml
first_squash_commit:
  - leave it where it is: do not reset, revert, amend, or rebase it. The branch is pushed, and
    the commit that records the `rejected` line stands on it.
second_squash:
  - run `git merge --squash FETCH_HEAD` as in step 2
  - if: a path conflicts and the sub-session's branch changed it
    then: take the sub-session's file whole — `git checkout FETCH_HEAD -- <path>`
  - if: a path conflicts and it is a `.stage/` record the main session wrote
    then: keep the main session's file — `git checkout HEAD -- <path>`
  - confirm the code equals the sub-session's branch before committing:
    `git diff FETCH_HEAD -- <the card's scope paths and every path the report lists>`
    prints nothing. When it prints a difference, the squash is wrong: resolve again, do not commit.
  - commit as in step 2. The body is the newest report, whose `Changed paths (JSON)` lists every
    path of both attempts.
then:
  - step 3 as before
  - import with one `--commit` per squash commit, oldest first ("Import the report"):
    `import_executor_report.py <W-id> --commit <first-squash> --commit HEAD`
  - the review receives the paths of HEAD, which are the paths the second attempt changed; the
    first attempt's paths are in the imported report. To hand the reviewer both attempts' paths,
    close with `--review-commit <first-squash> --review-commit HEAD`.
  - the retrospective keeps its id: commit it together with the `rejected` line, and rewrite it
    to cover both attempts before the second close
```

### Merge a card that waits for the user's machine

A success criterion that only the user's machine can show (another OS, an installed plugin, a
device) cannot be judged by a command in a cloud session. The close review judges it from a check
recorded on the card (`operations/review.md`, "A check recorded on the card") and fails it while
no check is recorded. Such a card's code may be merged while the card stays open and the check is
outstanding (W-00000372, W-00000407).

```yaml
take_this_path_when:
  - every criterion still open after step 3 names something only the user's machine can show,
    and its check is not recorded on the card yet
  - and the user has said to merge without waiting for that check
otherwise:
  - if: the user has not said so
    then: ask the user: wait for the check, or merge with the card open
  - if: an open criterion can be judged by a command the reviewer can run
    then: this path does not apply; close as in step 4
  - if: every such criterion already has its `- Checked` or `- User verdict` line on the card
    then: this path does not apply; close as in step 4
before_the_merge:
  - steps 1 to 3 as written
  - no close review runs, and no report is imported, no retrospective is written, and the card
    is not closed or archived: it stays in `.stage/work/current/` with its status unchanged
written_on_the_card:
  - under `## Progress` — which checks the main session re-ran at the squash commit, and the
    sentence `This change was merged without a close review.`
  - under `## Next action` — one line per open criterion:
    `Waiting on user: <what to run or look at, and on which machine> (<which criterion>)`
written_outside_the_card:
  - one unchecked line per open criterion, with the card id, in the project's open observation
    that collects checks deferred to the user's machine; open that observation when none exists
    (this repository's is O-00000062)
then: step 5 without archiving — push and open the pull request with the card still open
when_the_users_check_arrives:
  - write it on the card's `## Verification` as one `- Checked` line per criterion
    (`operations/review.md`, "A check recorded on the card", owns the form: the date, the
    machine, the commit, the command or action, and what it showed); remove the
    `Waiting on user:` line and check the observation's line
  - if: the check does not match the criterion's words and the user says how to judge it
    then: add a `- User verdict` line with the user's words under the `- Checked` line
  - close from a worktree at the squash commit as in step 4; that close review is the card's
    first, and it judges every criterion: the ones a command can show by running, the ones
    only the user's machine or the user can show with method `read` from those lines
  - if: the check shows a criterion does not hold, and no user verdict says it holds
    then: the card goes back to a work session; its fix merges through a new pull request
```

## What this does not cover

- Running Codex itself in the cloud.
- Promotion of the cards' decisions; those follow the usual promotion path.
