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
sessions work on parallel branches.

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
   (`close_work.py --allocate-retrospective`), and write it.
3. When the routed reviewer venue is unavailable too, keep `settings.json`
   unchanged and run the project's configured review through the Claude stand-in:

   ```bash
   STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py \
     python3 stage/skills/stage-retrospective/close_work.py --project-root . W-00000001 \
     --check "<suite>" --promotion <final-choice>
   ```

   The stand-in lets the reviewer write only its verdict file, read the
   changed-path folder, and run `python3 -m unittest`; it may not edit project
   files. Never write a verdict file by hand.
4. State on the card's `## Verification` that the close review was a same-model
   review, not a cross-venue one.
5. Copy the closed card and retrospective back to the branch and run
   `close_work.py <id>` there once more; its reconcile path updates the indexes.

## What this does not cover

- Running Codex itself in the cloud.
- Promotion of the cards' decisions; those follow the usual promotion path.
