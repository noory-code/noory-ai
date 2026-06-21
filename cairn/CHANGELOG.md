# Changelog

## [0.3.0] — 2026-06-21

Cairn is now a Claude Code plugin, so agents can discover and use it.

### Added

- **Plugin manifest** (`.claude-plugin/plugin.json`).
- **Skills** — `cairn-help` (what it is + commands) and `cairn-record` (how to
  write a well-formed decision: context / decision / alternatives / consequences,
  status, about, supersedes).

## [0.2.0] — 2026-06-21

Adds the link a decision-type work-item's gate needs.

### Added

- **`about` tag** on a decision — the ids it is about (a work-item leaf, a
  decision-topic slug, a feature). Optional, defaults to empty.
- **`in-force --about <id>`** filters to in-force decisions tagging that id.
- **`check --about <id>`** — a gate command: exits 0 when an in-force decision
  tags the id, 1 otherwise. This is what a Solera decision leaf's gate runs.

## [0.1.0] — 2026-06-21

Initial release — an append-only decision log (v1: the log itself; Plot/Solera
integration comes later).

### Added

- **`Decision`** — a Markdown file with frontmatter (title, status, supersedes)
  plus a prose body (context / decision / alternatives / consequences). Identity
  is the file name; fail-fast parser (`FormatError`).
- **`Log`** — append-only store under `.noory/cairn/`. `record` writes a new
  immutable decision (never edits); `in_force` is **derived** — an accepted
  decision that no accepted decision supersedes. Supersession is a relation, not
  an edit, so history is preserved.
- **CLI** — `cairn record / list / in-force / show`. Body via `--body` or stdin.
- **Independence guard** — cairn imports neither Plot nor Solera; they point at
  decisions by id (by value), one-way dependency.
