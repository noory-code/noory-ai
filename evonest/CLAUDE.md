# Evonest — Development Guide

## Build & Test

| Command | Action |
|---------|--------|
| `uv sync` | Install dependencies |
| `uv run pytest` | Run all tests |
| `uv run pytest --cov=evonest` | Tests with coverage |
| `uv run mypy src/evonest/` | Type check |
| `uv run ruff check src/ tests/` | Lint |
| `uv run ruff format src/ tests/` | Format |
| `uv run evonest` | Run MCP server (dev) |
| `uv run mcp dev src/evonest/server.py` | MCP inspector |

## Architecture

- `src/evonest/server.py` — MCP server (FastMCP, stdio transport)
- `src/evonest/cli.py` — CLI (argparse, subcommands)
- `src/evonest/tools/` — MCP tool definitions (thin wrappers over core/)
- `src/evonest/core/` — Engine logic (MCP-agnostic, all business logic here)
- `src/evonest/prompts/` — Phase prompt templates (observe, plan, execute, verify, meta)
- `src/evonest/templates/` — Init templates copied to .evonest/
- `mutations/` — Built-in personas and adversarial challenges (read-only at runtime)

## Key Patterns

- **ProjectState**: All file access goes through `core/state.py`. Never construct `.evonest/` paths manually.
- **Static/Dynamic separation**: `mutations/` is read-only. Dynamic mutations go to `.evonest/dynamic-*.json`.
- **Config 3-tier**: Engine defaults < `.evonest/config.json` < runtime parameters.
- **Tool/Core separation**: `tools/` are thin wrappers. Logic lives in `core/`.
- **ClaudeRunner**: All `claude -p` subprocess calls go through `core/claude_runner.py`.

## Version Management

**Single source of truth: `pyproject.toml`**

| File | Rule |
|------|------|
| `pyproject.toml` | **Only place to change the version** |
| `src/evonest/__init__.py` | Reads version dynamically via `importlib.metadata` — never hardcode |
| `.claude-plugin/plugin.json` | Must match `pyproject.toml` version — update together |

When bumping version:
1. `pyproject.toml` → update `version`
2. `.claude-plugin/plugin.json` → update `version` to match
3. Commit both in the same commit

Do NOT manually edit `~/.claude/plugins/` cache directories — Claude Code regenerates them on reload.

## Conventions

- Python 3.11+, type hints required
- `pathlib.Path` everywhere (no `os.path`)
- `dataclass` for data structures (no Pydantic)
- `pytest` for testing
- Commit format: `type(scope): description`
  - Types: feat, fix, refactor, test, docs, chore

## Boundaries (DO NOT modify)

- `.evonest/` in target projects — user data, never auto-delete
- `mutations/` — built-in data, never modified at runtime
