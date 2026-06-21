# Changelog

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
