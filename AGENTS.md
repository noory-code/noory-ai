# AGENTS.md

This file guides Codex when working in this repository.

**The repository guide SSOT is [CLAUDE.md](CLAUDE.md) — read it and follow it in full.** It covers the package layout, commands, language rules, core principles, cross-platform rules, code conventions, plugin release steps, and architecture. Everything there applies to Codex sessions identically. Do not duplicate its content here: duplication drifts.

## Codex-specific notes

- References to Claude inside CLAUDE.md are factual product references, not host-specific phrasing — e.g. Distill parses Claude Code conversation transcripts and Evonest's `core/claude_runner.py` invokes `claude -p`. Never mechanically rewrite them to Codex.
- `stage/` and `plainly/` ship two plugin manifests; releases bump both host manifests in each
  plugin.
