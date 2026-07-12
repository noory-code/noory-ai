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
python3 stage/scripts/init_stage.py --project-root <project-root> [--language <tag>]
```

When running from an installed plugin, resolve the script relative to the plugin root.

`--language` sets the human-readable Stage document language (lowercase IETF-style tag, e.g.
`en`, `ko`; default `en`). Bundled locale templates are used where available and other files fall
back to English; the tag is stamped into `settings.json` `language` so records generated later
follow it too. Machine-readable fields (IDs, paths, frontmatter keys, enum values, record section
headings) stay language-neutral in every language. Ask the user which language their Stage
documents should use when their conversation language and the project's instruction language
differ.

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
    verification.md
```

`operations/` holds only project-owned policy (the `kind -> passed` verification criteria and any
declared overrides). Common operational rules are plugin-owned and live in the installed Stage
plugin's `operations/` directory — they are not copied into the project. A `.stage/` initialized
by an older plugin still carries full copies; migrate it with
`python3 stage/scripts/migrate_stage.py --project-root <project-root>`.

## Completion gate

Stage initialization is complete only when all of the following hold.

- `.stage/index.md` exists.
- `operations/verification.md` exists, and `settings.json` carries the plugin's current
  `schema_version`.
- `past`, `present`, and `future` all exist.
- Index documents and individual record directories are separated.
- `python3 stage/scripts/audit_stage.py --project-root <project-root>` passes.
- No user-authored file was overwritten without explicit approval.
- The result stays plain Markdown and relative-path based.
