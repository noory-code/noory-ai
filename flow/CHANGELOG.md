# Changelog

All notable changes to this plugin are documented here.

## [0.1.3]

### Fixed

- Quality gate silently no-opped when checks used custom names: the reader only recognized the hardcoded keys `test`/`lint`/`analyze`, so a config like `test-engine`/`typecheck-viewer` was ignored entirely. Check names are now free-form.

### Changed

- Settings field renamed for clarity: `commands` → `checks`, inner `required_checks` → `required` (the old name collided with the plugin's `commands/` slash-command directory). Legacy names are still read; `/flow-upgrade` offers a one-time rename migration.
- A required check name with no declared command is now always a loud config error (previously unknown names were silently dropped — a typo could silently weaken the gate).

## [0.1.2]

### Removed

- The `agents` field in `.flow/settings.json` — no code ever read it, making it a dead derived index (SSOT violation). Role templates live in `.claude/agents/` and are discovered natively by the tool; docs, the flow-config procedure, and test fixtures no longer reference a settings-side roster.

## [0.1.1]

### Fixed

- `/flow-config` no longer interrogates the user about agents/team composition: `agents[]` is scan-filled silently from `.claude/agents/` (empty stays `[]`), and the Agent Teams env note moved from a Phase 7 guidance step to a single optional line in the final report.

## [0.1.0]

First public release.
