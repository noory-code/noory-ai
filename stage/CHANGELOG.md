# Changelog

## 0.4.0 — 2026-07-10

- Audit: SSOT001 (duplicate record IDs across files), OWN001 (records outside
  their owning catalog location, including body-only heading IDs), ROUTE001/002
  (existing artifact locations and operations documents missing from index.md
  routing). Template index now routes the model record directories.

## 0.3.0 — 2026-07-10

- SessionStart injects the newest three open questions and up to three
  `status: selected` backlog records as bounded one-line entries.

## 0.2.0 — 2026-07-10

- Multi-session `.runtime/`: per-(work item, path) promotion intents consumed
  by atomic rename reservation, per-session Stop handoffs with skew-safe
  pruning, per-session question-gate markers, lazy migration of 0.1.0 slots.

## 0.1.0 — 2026-07-10

- Initial release: `.stage/` artifact structure, init/audit/promote-intent
  CLIs, entry skills, and one hook set enforcing registration, promotion,
  hierarchy, commit, and portability gates on Claude Code and Codex.
