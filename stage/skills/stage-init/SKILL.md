---
name: stage-init
description: Create or repair the project-local `.stage/` execution harness. Existing files are preserved unless replacement is explicitly requested.
---

# Stage Init

Create or repair the project's `.stage/` structure.

## Preconditions

1. Confirm the project root.
2. Check whether `.stage/` exists.
3. Preserve existing files unless the user explicitly requests replacement.

## Procedure

Prefer the cross-platform helper.

```bash
python3 stage/scripts/init_stage.py --project-root <project-root>
```

When running from an installed plugin, resolve the script relative to the plugin root.

If the helper is unavailable, create the same structure as `templates/project-stage/`.

## Required structure

```text
.stage/
  index.md
  settings.json
  past/canon/
    principles/
    vocabulary/
    invariants/
  past/model/
    components/
    boundaries/
    interfaces/
  past/decisions/
    records/
  past/work/archive/
    items/
    retrospectives/
  present/work/
    items/
    retrospectives/
    decisions/
  present/state/
    observations/
    questions/
    assumptions/
    risks/
  future/roadmap/
    milestones/
    themes/
  future/backlog/
    items/
    views/
  future/proposals/
  operations/
```

## Completion gate

Stage initialization is complete only when all of the following hold.

- `.stage/index.md` exists.
- `operations/before.md`, `operations/during.md`, `operations/after.md`, `operations/retrospective.md`, `operations/artifacts.md`, and `operations/hooks.md` exist.
- `past`, `present`, and `future` all exist.
- Index documents and individual record directories are separated.
- `python3 stage/scripts/audit_stage.py --project-root <project-root>` passes.
- No user-authored file was overwritten without explicit approval.
- The result stays plain Markdown and relative-path based.
