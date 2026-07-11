# Pencil M3 Flutter Host Contract

Apply these mappings before executing any Pencil M3 Flutter skill.

- The active host may be Claude Code or Codex. Use the host's available question, file, shell,
  image, and Pencil MCP tools; tool names in a workflow describe capabilities, not mandatory IDs.
- Resolve `<plugin-root>` as the directory two levels above the active `SKILL.md`. Use that absolute
  path in shell commands. Do not assume `CLAUDE_PLUGIN_ROOT` is available in an agent shell.
- Claude Code project skills live under `.claude/skills/`; Codex repository skills live under
  `.agents/skills/`. When `pmf-init` creates the project `design` skill, write the same generated
  content to both locations.
- Claude Code plugin management uses `/plugin ...`; Codex plugin management uses
  `codex plugin ...` in a terminal.
- When reconnecting Pencil, use the active host's MCP management surface and start a new session if
  that host requires it.
