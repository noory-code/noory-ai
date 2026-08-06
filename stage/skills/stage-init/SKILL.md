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

For git repositories, initialization registers `.stage/.runtime/` in the project `.gitignore` so
Stage's machine-owned state is not committed. This check runs on every initialization.

`--language` sets the human-readable Stage document language (lowercase IETF-style tag, e.g.
`en`, `ko`; default `en`). Bundled locale templates are used where available and other files fall
back to English; the tag is stamped into `settings.json` `language` so records generated later
follow it too. Machine-readable fields (IDs, paths, frontmatter keys, enum values, record section
headings) stay language-neutral in every language. Ask the user which language their Stage
documents should use when their conversation language and the project's instruction language
differ.

If the helper is unavailable, copy `templates/v4/project-stage/` — the tree the helper deploys,
whose `v4` names the active topology rather than the schema version — and overlay
`templates/v4/locales/<tag>/` on it for a non-English language.

`templates/project-stage/` is the previous topology and stays for projects that have not migrated:
the audit compares such a project against it, and migration reads its `operations/verification.md`.

## Required structure

```text
.stage/
  index.md
  settings.json
  official/canon/
    principles/
    vocabulary/
    invariants/
  official/model/
    components/
    boundaries/
    interfaces/
  official/decisions/
    records/
    archive/
  official/state/archive/
  official/proposals/archive/
  official/work/archive/
    items/
    retrospectives/
  work/
    planned/
    current/
    retrospectives/
    views/
  decisions/pending/
  state/
    observations/
    questions/
    assumptions/
    risks/
  roadmap/
    milestones/
    themes/
  proposals/
  operations/
    verification.md
```

`operations/` holds only project-owned policy (the `kind -> passed` verification criteria and any
declared overrides). Common operational rules are plugin-owned and live in the installed Stage
plugin's `operations/` directory — they are not copied into the project. A `.stage/` initialized
by an older plugin must be migrated with the `stage-migrate` skill. Do not run stage-init over a
v3 tree: that would mix topologies and is refused.

## Completion gate

Stage initialization is complete only when all of the following hold.

- `.stage/index.md` exists.
- `operations/verification.md` exists, and `settings.json` carries the plugin's current
  `schema_version`.
- `official`, `work`, `decisions`, `state`, `proposals`, and `roadmap` all exist.
- Index documents and individual record directories are separated.
- `python3 stage/scripts/audit_stage.py --project-root <project-root>` passes.
- No user-authored file was overwritten without explicit approval.
- The result stays plain Markdown and relative-path based.
