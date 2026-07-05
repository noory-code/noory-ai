# commands/

Flow plugin slash commands.

- `/flow-config` — inject `.flow/settings.json` (the AI grasps the project + configures through conversation) — initial setup + re-tuning
- `/flow-config-retro` — set the retrospective rigor policy (`retrospective.levels` in `.flow/settings.json`) from ground-truth inspection, applied on explicit user confirmation
- `/flow-status` — query current settings (status) + diagnose and recommend improvements for running it better (evaluation — Φ1·Φ4)
- `/flow-help` — plugin overview + "what to do when it breaks" troubleshooting
- `/flow-upgrade` — sync the plugin rule canonical source → project `.claude/rules/` (propagation). Applies unsynced/new rules after a plugin upgrade. The single SSOT for rule sync (config delegates to it)
- `/skill-stats` — personal Skill-tool usage statistics (top used + unused skills)
- `/skill-stats-clear` — reset the personal skill-usage log (with confirmation)
- `/team-skill-stats` — team monthly skill-usage totals, aggregated from the month's rollup ticket (flags unused-skill candidates)

> Detailed procedures for `/flow-config` and `/flow-config-retro` live in `references/`.
