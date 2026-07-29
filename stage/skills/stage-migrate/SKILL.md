---
name: stage-migrate
description: Migrate an existing Stage project from schema v3 or v4 to the enforced schema v5 work hierarchy. Use when a Stage mutation is denied because the project is behind v5, or before using a newly updated Stage plugin with an older `.stage/` harness.
---

# Stage Schema Migration

Run this one-shot skill when `.stage/settings.json` reports `schema_version: 3` or `4` (or the
Stage schema gate says the project is behind v5). A schema-v5 project needs no migration.

## Preconditions

Complete every item before running the command:

- Close every other agent and editor window for this project.
- For a v3 project, commit or discard every git change outside `.stage/.runtime/`; its
  responsibility relocation uses a clean git transaction. The v4-to-v5 hierarchy migration
  snapshots the durable `.stage/` tree and may run alongside the registered migration work.
- Complete or discard every pending promotion intent and claim under
  `.stage/.runtime/intents/`.
- Remove the legacy `.stage/.runtime/promote-intent.json` only by completing or deliberately
  discarding that pending promotion.
- Resolve a symlinked `.stage` root, case-insensitive destination collision, duplicate work ID,
  missing parent, or mixed flat/hierarchical identity manually.

The migration fails before topology changes when any precondition is not satisfied. It never
guesses how to merge customized topology sections.

## Preview and migrate

Resolve the command relative to the installed Stage plugin root:

```text
python3 <stage-plugin-root>/skills/stage-migrate/migrate_stage.py --project-root <project-root> --dry-run
python3 <stage-plugin-root>/skills/stage-migrate/migrate_stage.py --project-root <project-root>
```

For schema v3, the command first relocates the responsibility topology through the registry with
`git mv` and rewrites recognized durable references. It then performs the schema-v4-to-v5 pass:
flat `W-*.md` cards become independent stories unless their existing parent chain places them
under an epic or story; `parent` frontmatter is removed; live indexes are rebuilt from actual
record paths; work guidance is refreshed; and schema v5 is stamped before strict audit. The
maintenance journal makes every interruption fail closed. The pre-migration audit is the
baseline: findings already present are listed but do not block the move, while findings first
seen after migration fail closed.

While the maintenance marker exists, the guard denies writes only to governed paths in that
project and to its `.stage/` tree. Configured excluded paths, scratchpads outside the project,
and other repositories remain writable so recovery work is not globally locked.

The retired `B-*.md` scan exists only in the v3 compatibility pass. Runtime record scanners never
recognize B cards or the schema-v4 flat work shape.

## Review and commit

The command may stage the v3 responsibility relocation but never commits. Review every changed
path and keep the migration with its plugin update as one intentional commit.

## Abort and rollback

After an interrupted or failed migration and before committing, restore the exact clean v3 tree
with:

```text
python3 <stage-plugin-root>/skills/stage-migrate/migrate_stage.py --project-root <project-root> --abort
```

The abort path restores only the journal transaction whose migration identity matches the active
or failed marker. It reports and ignores an unrelated journal left by an older migration. It
restores the exact durable pre-migration Stage snapshot and, for a chained v3 migration, then
restores the matching original v3 git transaction. Runtime files not owned by the migration are
preserved. A successful migration removes its journals and is no longer abortable; review its
working-tree changes before committing. After commit, rollback is `git revert
<migration-commit>`.
