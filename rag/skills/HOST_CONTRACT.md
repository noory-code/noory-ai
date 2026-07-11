# RAG Host Contract

Apply these mappings before executing any RAG skill.

- "active AI session" means the current Claude Code or Codex session.
- Capability names such as Read, Edit, Bash, and image viewing are semantic. Use the host's
  available tool that performs that capability; do not require the literal Claude Code tool name.
- When a workflow requests `AskUserQuestion`, use `AskUserQuestion` on Claude Code,
  `request_user_input` on Codex when available, or ask one concise conversational question.
- A `/rag:<skill>` example is Claude Code invocation syntax. On Codex, invoke the same installed
  skill by name or use one of the natural-language trigger phrases in its description.
- Claude Code plugin management uses `/plugin ...`; Codex plugin management uses
  `codex plugin ...` in a terminal.
- On Claude Code, the MCP server receives the project root through `RAG_PROJECT_ROOT`. On Codex,
  the plugin preserves the workspace cwd and explicitly opts into using it. Never invent or depend
  on `CODEX_PROJECT_DIR`.
