---
name: stage-migrate
description: Migrate an existing Stage project from schema v3 to the enforced schema v4 responsibility topology. Use when a Stage mutation is denied because the project is behind v4, or before using a newly updated Stage plugin with a v3 `.stage/` harness.
---

# Stage Schema Migration

Run this one-shot skill when `.stage/settings.json` reports `schema_version: 3` (or the Stage
schema gate says the project is behind v4). A schema-v4 project needs no migration.

## Preconditions

Complete every item before running the command:

- Close every other agent and editor window for this project.
- Commit or discard every git change outside `.stage/.runtime/`; the working tree must be clean.
- Complete or discard every pending promotion intent and claim under
  `.stage/.runtime/intents/`.
- Remove the legacy `.stage/.runtime/promote-intent.json` only by completing or deliberately
  discarding that pending promotion.
- Resolve a symlinked `.stage` root, case-insensitive destination collision, or mixed populated
  v3/v4 topology manually and commit the resolution.

The migration fails before topology changes when any precondition is not satisfied. It never
guesses how to merge customized topology sections.

## Preview and migrate

Resolve the command relative to the installed Stage plugin root:

```text
python3 <stage-plugin-root>/skills/stage-migrate/migrate_stage.py --project-root <project-root> --dry-run
python3 <stage-plugin-root>/skills/stage-migrate/migrate_stage.py --project-root <project-root>
```

The command writes a runtime maintenance marker, relocates through the registry with `git mv`,
rewrites only recognized durable path fields and document references, verifies that no live v3
reference remains, stamps schema v4 last, and runs strict audit.

## Review and commit

The command stages migration changes but never commits them. Review the staged diff, then use the
commit message printed by the command. Keep the migration as one commit so long-lived branches can
rebase onto it and translate old paths through the same registry map.

## Abort and rollback

Before committing, restore the exact clean v3 tree with:

```text
python3 <stage-plugin-root>/skills/stage-migrate/migrate_stage.py --project-root <project-root> --abort
```

The abort path uses the runtime journal and original `HEAD`; it removes only the migration-owned
staged/working-tree transaction. After the migration is committed, do not run abort: rollback is
`git revert <migration-commit>`.
