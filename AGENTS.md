# AGENTS.md

This file guides Codex when working in this repository.

**The repository guide SSOT is [CLAUDE.md](CLAUDE.md) — read it and follow it in full.** It covers the package layout, commands, language rules, core principles, cross-platform rules, code conventions, plugin release steps, and architecture. Everything there applies to Codex sessions identically. Do not duplicate its content here: duplication drifts.

## Codex-specific notes

- References to Claude inside CLAUDE.md are factual product references, not host-specific phrasing — e.g. Distill parses Claude Code conversation transcripts and Evonest's `core/claude_runner.py` invokes `claude -p`. Never mechanically rewrite them to Codex.
- Every local plugin ships Claude Code and Codex manifests; releases bump both host manifests.
- When working under `evonest/`, also read and follow `evonest/CLAUDE.md`; Codex does not discover
  that filename automatically.
