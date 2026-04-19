# Changelog

## [0.1.0] — 2026-04-19

Initial release.

### Added

- Command **Solera Map: Open** launches the viewer in a VSCode webview panel.
- Spawns `uv run python -m solera_map` against the current workspace folder, reusing an existing server when one is already healthy on the configured port.
- Detects v4 (`.solera/`) or v3 (`workspace/`) Solera workspaces; shows an info notification + suggests `/solera-migrate-workspace-to-dotsolera` for v3.
- Onboarding panel for non-Solera workspaces with prerequisite + install instructions.
- All four canvases (Service / Plan / Build / Live) render via the bundled `viewer/dist/` (copied from `../solera-map/viewer/dist/` during `vscode:prepublish`).
- Server lifecycle: SIGTERM with 5s grace period, then SIGKILL on extension deactivation.
- Per-load CSP nonce; `connect-src` opens `http://127.0.0.1:{port}` and `ws://127.0.0.1:{port}` only.

### Prerequisites

- Python 3.11+ and `uv` (https://docs.astral.sh/uv/) on PATH.
- The `solera-map` Python package resolvable to `uv` (installed via the Solera Map Claude Code plugin marketplace).

### Notes

- VSCode Marketplace policy bans extensions that download executables — this extension cannot install `uv` for you. If `uv` is missing, the spawn fails with a clear "Open Output" notification.
- No telemetry. Privacy-first per [Solera's PRIVACY.md](https://github.com/noory-code/noory-ai/blob/main/solera/PRIVACY.md).
