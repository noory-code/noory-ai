# Changelog

All notable changes to this plugin are documented here.

## [0.3.0] — 2026-07-12

- Added complete Codex marketplace and installation support.
- Replaced the nonexistent `CODEX_PROJECT_DIR` assumption with an explicit Codex workspace-cwd
  contract. `uv run --project` preserves cwd while selecting the bundled Python project.
- Added a shared Claude Code/Codex host contract to every RAG skill and made question/tool
  capability names host-neutral.
- Updated troubleshooting and usage documentation for both hosts.
- Updated the Flutter Cask integration fixture from legacy `guide-lib-*` paths to the current
  `flutter-*` skill layout.

## [0.2.1]

Review fixes (no schema or wire changes).

- Fixed: `relate()` no longer silently drops relations whose endpoint
  entities are not yet upserted — missing endpoints are merged as stub
  Entity nodes and enriched by a later real upsert.
- Fixed: `rag_export` computes stats before closing DB handles, so the
  snapshot tarball is read from fully-flushed files.
- Fixed: `expand_depth=0` is honored as "no graph expansion" instead of
  being silently clamped to 1; `k`/`expand_depth`/`depth` are validated
  against their advertised schema bounds at the tool entry points.
- Fixed: a corrupt `manifest.json` still degrades to a full reindex but the
  `rag_diff_files` / `rag_upsert_chunks` responses now carry a warning.
- Fixed: `rag_import` wraps corrupt/unreadable tarball errors and
  `rag_search` wraps missing-settings errors into the structured
  `{ok: false, error}` shape.
- Fixed: external edits to `settings.json` are picked up by the next tool
  call (mtime-based container rebuild) instead of being served stale.
- Removed: dead `Indexer.commit_manifest` production path (manifest is
  written incrementally per file by the tool layer) and the unused
  `RAG_PLUGIN_ROOT` env from `.mcp.json` and docs.

## [0.2.0]

First public release.
