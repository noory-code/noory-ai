# Portability

This document owns the host and platform portability rules.

## Supported hosts

- Codex
- Claude

## Supported platforms

- Windows
- Linux
- macOS

## Rules

- Stage core artifacts are Markdown and plain files.
- Use relative paths inside `.stage/`.
- The core harness requires no specific shell.
- Host-specific features live in adapters, not in the core Stage structure.

## Host enforcement

- Both hosts run the same `hooks/hooks.json` guard: Claude registers it directly; Codex discovers it from the installed plugin and runs it after a one-time trust approval in the interactive TUI (`/hooks`).
- Untrusted hooks on Codex are silently excluded (including `codex exec`), so enforcement there depends on completing the trust approval after plugin install.
