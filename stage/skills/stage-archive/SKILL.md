---
name: stage-archive
description: Archive completed or rejected Stage work items out of the review queue into official/work/archive/. Use this whenever review.md holds items whose verification, retrospective, and promotion decision are all closed and you want to drain them — or when the user asks to clean up, tidy, or archive the Stage work queue. Archiving needs only an archive intent (the archive_work.py fast path handles it) — never a new work item, a mistake that has bitten this project before.
---

# Stage Archive

Archiving is record keeping, not promotion. It moves one closed top-level epic or independent
story hierarchy and all of its retrospectives out of the current flow into
`official/work/archive/`, preserving the top-level terminal status in the archive index.

## One rule that prevents the common mistake

Archiving passes exactly ONE gate: a per-path **archive intent**. `.stage/` is excluded from
`is_source_path` (`stage/hooks/stage_paths.py: DEFAULT_EXCLUDED_PREFIXES`), so the registration and
commit gates never fire on `.stage/official/...`. **Do NOT create a new work item to archive** — the
work being archived already has one, and a second would duplicate the record (SSOT).

## Preconditions (per item)

- `status` is `completed` or `rejected`.
- `retrospective: completed` with a `retrospective_ref` whose file exists.
- Every record inside the top-level hierarchy is `completed` or `rejected`.
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

Pass only the top-level ID. The script validates every record in that move unit, preserves the
epic/story/action relative paths under `archive/items/<top-level-id>/`, changes every record to
`status: archived`, moves every linked retrospective, appends one top-level `Final status` row,
and drops every hierarchy row from the current indexes. Nested stories and actions are not moved
independently; they stay in place relative to their top-level directory. It is idempotent and
stamps `terminal_disposition: accepted` or `rejected` on every archived record. Then verify:

```bash
python3 stage/scripts/audit_stage.py --project-root <project-root>   # expect errors=0
```

## Manual path (single ad-hoc archive, or when the script is unavailable)

Create one archive intent covering the item, its retrospective, and the shared index, then perform
the moves with LITERAL paths (the hook parses raw command text — a shell variable like `$VAR/W-...`
reaches the gate unexpanded and matches no intent).

```bash
python3 stage/scripts/promote_intent.py --project-root <project-root> --type archive --work-item W-00000001 \
  --path .stage/official/work/archive/items/W-00000001.md \
  --path .stage/official/work/archive/retrospectives/R-00000001.md \
  --path .stage/official/work/archive/index.md
```

Then move the top-level directory as one unit, set each contained record to `status: archived`,
move each retrospective verbatim, append one top-level index row (Final status is the top-level
`completed`/`rejected` value the `archived` overwrite erases), delete the current hierarchy, and
remove all of its `work/active.md` and `work/review.md` rows.

## Commit

The archive touches only `.stage/`, which is not governed source — no work item and no completion
gate apply to the commit.
