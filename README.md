# noory-ai

MCP server collection for Claude Code — autonomous code evolution and knowledge distillation.

## Packages

### [Evonest](evonest/) — Autonomous Code Evolution

Runs 19 specialist personas against your codebase (security auditor, chaos engineer, performance analyst, etc.) and lets adaptive selection determine which approaches work best for your project.

- **Observe → Plan → Execute → Verify** cycle with auto-revert on failure
- Git stash before every change; lock file prevents concurrent runs
- Adaptive persona weights — successful personas run more often over time
- Direct commit or PR mode (`code_output: "pr"`)

**Install via Claude Code plugin:**
```
/plugin marketplace add wooxist/evonest
/plugin install evonest@wooxist/evonest
```

**Or manually:**
```bash
uvx evonest
# Add to ~/.claude/mcp.json: {"mcpServers": {"evonest": {"command": "uvx", "args": ["evonest"]}}}
```

### [Distill](distill/) — Knowledge Distillation

Extracts reusable patterns, decisions, and lessons from Claude Code conversations — so Claude remembers what matters across sessions. No API key required (uses MCP Sampling).

- Automatic extraction at session end via hooks
- 3-tier scope: global (`~/.distill/`) → workspace → project (`.distill/`)
- FTS5 full-text + semantic vector search
- Crystallizes chunks into `distill-*.md` rule files

**Install:**
```bash
git clone https://github.com/wooxist/distill.git && cd distill && uv sync
# Add to ~/.claude/mcp.json — see distill/README.md
```

## Development

Each package is independent. Work inside the relevant subdirectory:

```bash
cd evonest   # or: cd distill
uv sync
uv run pytest
uv run mypy src/
uv run ruff check src/ tests/
```

See [CLAUDE.md](CLAUDE.md) for full command reference and architecture notes.

## License

Each package is MIT licensed. See [evonest/pyproject.toml](evonest/pyproject.toml) and [distill/pyproject.toml](distill/pyproject.toml).
