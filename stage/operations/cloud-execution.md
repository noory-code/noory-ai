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

## Close

1. Close from a worktree checked out at the card's code commit
   (`git worktree add --detach <path> <code-commit>`), because the review receives
   the paths of the HEAD commit.
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

   The stand-in lets the reviewer write only its verdict file, read the
   changed-path folder, and run `python3 -m unittest`; it may not edit project
   files. Those rules cover only the reviewer's own tool calls, and code the
   tests run can still write, so `close_work.py` compares the repository before
   and after every review command: when any file other than the verdict changed,
   it removes the verdict, names the paths, and fails the close review. Inspect
   and discard those changes before closing again. The project's own Claude
   reviewer command runs through the same stand-in. Never write a verdict file by
   hand.
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
2. Squash it onto the main session's branch as one commit that carries the sub-session's executor
   report: `git merge --squash FETCH_HEAD`, then commit with a message of your own. Its subject
   is `<type>(<scope>): <the card's whole change> (<W-id>)`; the last commit of the sub-session's
   branch names only its last step. Its body is that commit's body, unchanged:
   `git log -1 --format=%b FETCH_HEAD` prints it. Write both to a file outside the repository and
   run `git commit -F <file>`. The review receives the paths of HEAD (O-00000058), so one squash
   commit hands the reviewer every path; no local-only commit is needed.
3. Re-run the card's checks yourself; do not trust the sub-session's transcript.
4. Import the report (`import_executor_report.py <W-id> --commit HEAD`), reserve and write the
   retrospective, link it on the card, and close with the review as in "Close" above. When the
   review fails, commit the card with its new `rejected` review line on the main session's
   branch, keep `.stage/.runtime/driver/logs/<W-id>.md` in place, send the failed criteria to the
   sub-session, and repeat from step 1 after it pushes. The close that passes counts the rejected
   lines and the reports in that log into the card's `- Load at close` line.
5. Archive the card, push, and open the pull request from the main session's branch. The
   sub-session's branch is not merged on its own.

A work session that built an epic leaves one commit per story, each with that story's executor
report. Bring them over one by one instead of squashing (`git cherry-pick <story-commit>`, oldest
first), and run steps 3 and 4 for each story at its commit. Close the stories without `--archive`,
then close and archive the epic.

## What this does not cover

- Running Codex itself in the cloud.
- Promotion of the cards' decisions; those follow the usual promotion path.
