---
description: Flow rule sync — propagates the plugin rules/ canonical source to the project .claude/rules/ (propagated-rule model). Triggers "rule sync", "rule upgrade", "flow-upgrade", "apply rules after plugin update"
argument-hint: "(no arguments — auto-detect and apply)"
allowed-tools: Bash(uv:*), Bash(claude:*), Read
---

# /flow-upgrade

You are the Flow Manager responsible for **rule propagation** in the flow plugin. Because Claude Code does not auto-load the plugin `rules/`, you **copy-deliver** the canonical rules into the project `.claude/rules/`. This command is the single SSOT for **canonical → copy** synchronization. (Historical `.claude/rule-details/` copies installed by an earlier sync — i.e. registered per-file in `.gitignore` — are removed automatically as orphans on apply; unregistered files are treated as hand-authored and left untouched.)

## Model (propagated rules)

- **Propagated rules** (canonical copies) = **generated artifacts** — registered per-file in `.gitignore` (git-ignored). Sync **unconditionally overrides** them from the canonical source (overwrites even hand-edits) and **deletes** them when they disappear from the canonical source (orphan).
- **Consumer-authored rules** (project-specific rules absent from the canonical source) = outside `.gitignore` → git-tracked + **preserved as-is** (`protected` — never touched).
- Application is human-triggered (this command). The SessionStart hook only detects and notifies (read-only).

## Plugin freshness (auto for CLI / guidance for non-CLI)

Rule sync is only meaningful **against the latest canonical source**, so check whether the plugin is stale before syncing.

- **CLI environment**: When this command detects a stale plugin, it **auto-runs** the plugin upgrade commands and guides you to restart the session (Step 0 below). Run it again after restart and rule sync proceeds.
- **Non-CLI environment** (VS Code, etc.): There is no way to auto-run, so follow the SessionStart hook guidance to **manually upgrade + restart**, then run this command.

> Why a restart is involved: `claude plugin update` requires a session restart to take effect (platform constraint) — even automated, one restart remains.

## Procedure

> Decisions and application are handled by `rule_sync_cli.py` — do not reimplement, call it only via the CLI (shares logic with the SessionStart hook).

### 0. Plugin auto-upgrade (CLI — when stale)

```bash
uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/rule_sync_cli.py" upgrade-plan
```

Interpret the JSON `{stale, env, commands}`:
- **`commands` empty** (up to date, or non-CLI environment) → proceed directly to Step 1 (detect).
- **`commands` present** (CLI + stale) → run those commands **exactly in the listed order** (refresh marketplace → update plugin; the values are already filled in with the actual marketplace, plugin, and scope), then:
  > ⚠ Upgraded the plugin from v{installed} to the latest. **Restart the session**, then run `/flow-upgrade` again to sync the rules.

  → Do NOT proceed with rule sync (Steps 1–5) — **stop here** (sync against the new canonical source after restart).

> Auto-run is CLI-only — `upgrade-plan` returns empty `commands` for non-CLI/up-to-date, so it is naturally skipped. Application (loading new code) is a restart, which is the human's part.

### 0.5 Seed settings defaults (idempotent, non-destructive)

Separately from rule sync, seed the plugin's internal defaults (`config-defaults.json` — e.g. the retrospective upstream board `upstream_board`) into the project `.flow/settings.json`. **Fill only when empty; leave existing values untouched** (preserve team customizations). This step lets already-installed setups receive new defaults through an update alone, without reworking settings.

```bash
uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/rule_sync_cli.py" seed-settings
```

Interpret the JSON `{seeded, preserved, settings_missing}`:
- `seeded` not empty → "✅ Injected defaults {seeded} (e.g. retrospective upstream board)."
- `settings_missing: true` → "ℹ️ Settings not configured — run `/flow-config` first (config fills board defaults)."
- All `preserved` → no change (already set).

> Non-destructive and idempotent, so repeated runs are safe. The board coordinates themselves have their SSOT in `config-defaults.json` (never hardcoded in skill/command bodies).

### 1. detect

```bash
uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/rule_sync_cli.py" detect
```

JSON keys: `in_sync` / `stale` (canonical changed) / `missing_new` (new propagated rule) / `orphan` (propagated rule that disappeared from the canonical source → copy to be deleted) / `protected` (authored rule — preserved) / `plugin_version`.

### 2. No drift
`stale`, `missing_new`, and `orphan` are all empty arrays →
> ✅ Rules in sync (plugin v{plugin_version}) — no changes to apply.

→ Stop.

### 3. Summary report (Clear Feedback)
- `stale` / `missing_new` / `orphan` — **auto-apply targets** (override · add · delete).
- `protected` (if any) — consumer-authored rules, untouched by sync (informational).

### 4. apply (automatic — no approval argument)

```bash
uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/rule_sync_cli.py" apply --applied-at "current_ISO8601"
```

> Propagated rules are generated artifacts — they are auto-overridden/added and registered in `.gitignore`, and orphans are deleted. Just before overwriting/deleting, one backup of the copy is saved to `.flow/.runtime/rules-backup/` (restore if needed). Authored rules (`protected`) are untouched. `--applied-at` is the current ISO8601 (optional).

### 5. Result report
Interpret the apply JSON (`applied`/`deleted`/`registered`/`protected`/`backups`):
> ✅ Synced {applied count} rules + deleted {deleted count} (orphan) (plugin v{version}). Preserved (authored) {protected count}. Backup: `.flow/.runtime/rules-backup/`.
> ⚠ New rules are loaded **after a session restart** (the `.claude/rules/` auto-load timing).

## Upgrade propagation boundary (always applies)

| Asset type | Propagation path | This command |
|-----------|----------|----------|
| **Rule canonical source** (`rules/`) | plugin → project `.claude/rules/` copy | ✅ detect/apply sync |
| **Skill / Command / Hook / Docs / Playbook / Manifest** | plugin self-upgrade (CLI: auto-run in Step 0 / non-CLI: user) + restart | ⚠ CLI auto-runs Step 0, application is a restart |

→ **Rule changes** are handled by this command; **everything else** by a plugin upgrade (+ restart). Both are required for a complete installation freshness. Per-release changed assets have their SSOT in `CHANGELOG.md` — do not accumulate them in this command.

## Recommended flow

1. **`/flow-upgrade`** — on CLI, when stale, auto-upgrade the plugin (Step 0) + restart guidance; on non-CLI, manual-upgrade guidance.
2. **Restart the session**, then rerun **`/flow-upgrade`** — sync canonical rules → copies.
3. (If accompanied by a settings schema change) rerun `/flow-config`.

> Each session the SessionStart hook detects and notifies of drift on 2 axes (plugin version · rule copies) (read-only). Before starting work, check whether `/flow-upgrade` has been run — if the user says "later/skip/work first", proceed (once per session).
> `flow-config`'s rule sync/validation delegates to this command/helper (no duplicate implementation — DRY/SSOT).
