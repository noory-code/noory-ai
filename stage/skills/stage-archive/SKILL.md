---
name: stage-archive
description: Archive completed or rejected Stage work items into official/work/archive/, including planned cards rejected before work started. Use this whenever review.md holds closed items to drain, a rejected card must leave the planned index, or the user asks to clean up, tidy, or archive the Stage work queue. Archiving needs only an archive intent (the archive_work.py fast path handles it) — never a new work item, a mistake that has bitten this project before.
---

# Stage Archive

Archiving is record keeping, not promotion. It moves one closed top-level epic or independent
story hierarchy out of the current or planned flow into `official/work/archive/`, preserving the
top-level terminal status in the archive index. Retrospectives move with current work; a planned
hierarchy rejected before work started has no retrospective to move.

## One rule that prevents the common mistake

Archiving passes exactly ONE gate: a per-path **archive intent**. `.stage/` is excluded from
`is_source_path` (`stage/hooks/stage_paths.py: DEFAULT_EXCLUDED_PREFIXES`), so the registration and
commit gates never fire on `.stage/official/...`. **Do NOT create a new work item to archive** — the
work being archived already has one, and a second would duplicate the record (SSOT).

## Preconditions (per move unit)

- A hierarchy in `work/current/` has `status: completed` or `status: rejected` on every record.
  Every record also has `retrospective: completed` and a `retrospective_ref` whose file exists.
- A hierarchy in `work/planned/` has `status: rejected` on every record. It was never started, so
  its rejection reason stays in the card body and no retrospective is required.
- No `active`/`review`/`blocked` work item remains inside or below that hierarchy.
- No open question, assumption, or risk lists it in `work_items`.

## Fast path (default)

The archiver lives beside this skill (`${CLAUDE_PLUGIN_ROOT}/skills/stage-archive/archive_work.py`;
in this repo, `stage/skills/stage-archive/archive_work.py`).

```bash
python3 stage/skills/stage-archive/archive_work.py --project-root <project-root> W-00000001 [W-00000002 ...]
# or archive every completed item currently in review.md:
python3 stage/skills/stage-archive/archive_work.py --project-root <project-root> --all-completed
```

Pass only the top-level ID. The script looks in `work/current/` first and then `work/planned/`.
It validates every record in that move unit, preserves the epic/story/action relative paths under
`archive/items/<top-level-id>/`, changes every record to `status: archived`, moves every linked
retrospective, appends one top-level `Final status` row, and drops every hierarchy row from its
source lifecycle index. Nested stories and actions are not moved independently; they stay in place
relative to their top-level directory. It is idempotent and stamps `terminal_disposition:
accepted` or `rejected` on every archived record. Then verify:

```bash
python3 stage/scripts/audit_stage.py --project-root <project-root>   # expect errors=0
```

## Manual path (single ad-hoc archive, or when the script is unavailable)

Create one archive intent covering the item, the shared archive index, and each retrospective that
exists. A planned rejection has no retrospective path. Then perform the moves with LITERAL paths
(the hook parses raw command text — a shell variable like `$VAR/W-...` reaches the gate unexpanded
and matches no intent).

```bash
python3 stage/scripts/promote_intent.py --project-root <project-root> --type archive --work-item W-00000001 \
  --path .stage/official/work/archive/items/W-00000001.md \
  --path .stage/official/work/archive/retrospectives/R-00000001.md \
  --path .stage/official/work/archive/index.md
```

Then move the top-level directory as one unit, set each contained record to `status: archived`,
move each existing retrospective verbatim, append one top-level index row (Final status is the
top-level `completed`/`rejected` value the `archived` overwrite erases), delete the source
hierarchy, and remove all of its rows from `work/active.md` and `work/review.md` or from
`work/planned/index.md`.

## Commit

The archive touches only `.stage/`, which is not governed source — no work item and no completion
gate apply to the commit.
