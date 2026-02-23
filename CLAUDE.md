# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

Python monorepo with two independent MCP (Model Context Protocol) servers. Each package under its own directory with its own `pyproject.toml`, `uv.lock`, and `tests/`.

```
noory-ai/
├── evonest/   — Autonomous code evolution engine (v0.2.0, Alpha)
└── distill/   — Knowledge distillation from Claude conversations (v1.0.0)
```

Each package is developed, tested, and released independently. There is no shared root `pyproject.toml` or workspace config — work inside the relevant subdirectory.

## Commands

All commands run from inside the package directory (`cd evonest` or `cd distill`).

```bash
uv sync                         # install deps
uv run pytest                   # run all tests
uv run pytest tests/test_foo.py # run single test file
uv run pytest -k "test_name"    # run single test by name
uv run mypy src/                # type check
uv run ruff check src/ tests/   # lint
uv run ruff format src/ tests/  # format
```

**Evonest only:**
```bash
uv run evonest                        # run MCP server
uv run mcp dev src/evonest/server.py  # MCP inspector
```

**Distill only:**
```bash
uv run python -m distill  # run MCP server
```

## Language

- All documents, comments, commit messages, and code artifacts must be written in **English**
- Conversation with the user is in **Korean**

## Core Principles

### SSOT (Single Source of Truth)

- If information already exists elsewhere, link to it — do not duplicate
- Every piece of data must have one clear canonical location

### MECE (Mutually Exclusive, Collectively Exhaustive)

- New code/categories must not overlap with existing ones — merge if they do
- Check for missing cases before considering work complete

### SoC (Separation of Concerns)

- Each module has exactly one responsibility
- Review for splitting when a file exceeds 500 lines

### Atomic Commits

- Each commit must pass build + tests on its own
- Each commit contains exactly one purpose
- Commit message explains "what and why", not "how"
- **Commit messages must be written in English** — this is a global open-source project

### Incremental Progress

- Break work into small, verifiable steps
- Verify after each step before proceeding

### After Completing Work

- Summarize changes made
- Ask "Shall I commit?" before committing

### Diagrams

- Use **Mermaid** for all diagrams
- Never use `1.`, `2.` (number + period) in node labels — causes parser errors

### AI-First Documentation

> Write docs so AI executes user intent **deterministically**

- Use structured formats (YAML if/then/when) over prose
- Make conditions explicit (file paths, keywords, thresholds)
- Eliminate ambiguity

**Banned phrases** (these cause AI to make arbitrary judgments):

| Banned | Use Instead |
|--------|-------------|
| "as appropriate" | Specify exact threshold or condition |
| "if needed" | State the explicit trigger condition |
| "depending on the situation" | List each case with its action |
| "as you see fit" | Provide `if: condition then: action` |
| "handle accordingly" | Specify the exact handling logic |

## Code Conventions

- Python 3.11+, pathlib.Path everywhere (never `os.path`)
- Type hints on all functions; mypy strict mode
- Line length: 100 chars (ruff)
- Commit format: `type(scope): description` — types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- Distill uses Pydantic v2; Evonest uses dataclasses

## Architecture

### Evonest

**Tool/Core separation**: `tools/` are thin MCP wrappers. All logic lives in `core/`.

Key files:
- `core/orchestrator.py` — main evolution loop
- `core/phases.py` — Observe → Plan → Execute → Verify phases
- `core/state.py` — all `.evonest/` directory access goes through here (single entry point)
- `core/mutations.py` — persona & adversarial challenge selection
- `core/claude_runner.py` — all `claude -p` subprocess calls (turn limits, error handling)
- `mutations/personas.json` — 19 built-in personas (read-only at runtime)
- `mutations/adversarial.json` — 8 adversarial challenges

Runtime-generated personas/adversarials go to `.evonest/dynamic-*.json` in the target project, never to `mutations/`.

3-tier config: engine defaults < `.evonest/config.json` < runtime args.

### Distill

**Tool/Store/Extractor separation**: `tools/` are thin wrappers; persistence in `store/`; extraction pipeline in `extractor/`.

Key files:
- `store/metadata.py` — SQLite CRUD + FTS5 full-text search
- `store/vector.py` — fastembed + sqlite-vec embeddings
- `store/scope.py` — 3-tier scope: `~/.distill/` (global) → `<git-root>/.distill/` (workspace) → `.distill/` (project)
- `extractor/extractor.py` — MCP Sampling call (primary) with Anthropic API fallback
- `extractor/crystallize.py` — consolidates chunks into `distill-*.md` rule files
- `shared/prompts.md` — extraction prompt SSOT; must stay in sync with `extractor/prompts.py`

Config priority: project > workspace > global > defaults (all optional).
