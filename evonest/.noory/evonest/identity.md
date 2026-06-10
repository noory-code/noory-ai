# Project Identity

## Mission
MCP-native autonomous code evolution engine that sends 19 specialist personas at your codebase with adaptive learning and built-in safety mechanisms.

## Core Values
- Adaptive intelligence — successful personas run more often through weighted selection
- Safety first — auto-revert on failed build/test, git stash before execute, hard API caps
- Multiple perspectives — diverse personas (security, performance, product, quality) prevent tunnel vision
- Autonomous yet human-directed — proposals, pull request mode, cautious approval workflow
- Verification always — every change runs verify.build and verify.test before commit

## Current Phase
v0.3.0 released. Mode redesign complete (analyze/improve/evolve). Claude Code plugin launched with slash commands. Monorepo integration and plugin cache compatibility achieved. Next: analysis depth levels (quick/standard/deep) and parallel persona execution.

## Quality Standards
- All tests pass: `uv run pytest` (329 tests passing)
- Type checking passes: `uv run mypy src/evonest/` (strict mode)
- Linting passes: `uv run ruff check src/ tests/`
- Code formatting required: `uv run ruff format src/ tests/`

## Product Direction
Open-source MIT license. Designed as a first-class participant in Claude Code (MCP-native), not a standalone tool. Vision includes persona community sharing, multi-module orchestration ("Nest hierarchy"), and large-scale service identity-driven decomposition.

## Ecosystem
**Key dependencies:**
- `mcp[cli] >=1.0` — Model Context Protocol framework
- `pytest` — Testing framework
- `mypy` — Type checking
- `ruff` — Linting and formatting

**Python version:** 3.11+

**Tech stack:** Python-native CLI + MCP server (FastMCP, stdio transport). No external APIs — runs within Claude environment. Uses `claude -p` subprocess calls for persona execution.

## Boundaries (DO NOT touch)
- `.evonest/` — User evolution data, config, proposals, history — never auto-delete or modify
- `mutations/` — Built-in persona and adversarial definitions — read-only at runtime
- `.mcp.json` — User's MCP configuration
- `.env` — Environment secrets
- `credentials*`, `secrets*` — Any credential files
- `.claude/settings.local.json` — User's Claude Code settings