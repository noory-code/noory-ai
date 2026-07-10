# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

Python monorepo of independent plugins/servers. Python packages carry their own `pyproject.toml`, `uv.lock`, and `tests/` (rag's uv project lives in `rag/server/`); `flutter-cask/`, `pencil_m3_flutter/`, and `stage/` are not uv projects. Novel's open plugin stack lives in the `novel-ai/` submodule.

```
noory-ai/
├── evonest/            — Autonomous code evolution engine
├── novel-ai/           — Git submodule: https://github.com/noory-code/novel-ai
│   ├── mashbill/          — Novel canvas + MCP/HTTP server
│   ├── solera/            — deterministic work planning and execution harness
│   ├── proof/             — append-only decision log
│   └── distill/           — durable knowledge extraction and recall
├── rag/                — Project-scoped GraphRAG plugin (uv project in server/)
├── stage/              — Durable execution harness (plain stdlib — no uv; hooks run on any host python3 ≥3.9)
├── flutter-cask/       — Flutter package guide skills
└── pencil_m3_flutter/  — Flutter M3 design system automation
```

Each package is developed, tested, and released independently. There is no shared root `pyproject.toml` or workspace config — work inside the relevant subdirectory.

After cloning, initialize Novel AI with `git submodule update --init`. Changes
inside `novel-ai/` are committed and pushed in that repository first; then
commit the updated submodule gitlink in this repository.

**Stage only:** test with `python3 -m unittest discover -s stage/hooks/tests -q` and `python3 -m unittest discover -s stage/scripts/tests -q` (no uv/mypy/ruff targets).

## Commands

All commands run from inside the package directory (`cd evonest` or `cd novel-ai/distill`).

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

### Plugin Changes

- When any file inside a plugin directory (`evonest/`, `rag/`, `stage/`, `flutter-cask/`, `pencil_m3_flutter/`) is modified:
  1. Bump `version` in `.claude-plugin/plugin.json` (patch for fixes, minor for features/refactors) — `stage/` also carries `.codex-plugin/plugin.json`; bump both
  2. Add entry to `CHANGELOG.md`
  3. Commit + push in one step

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

## Cross-Platform Compatibility

All code must run on **macOS, Linux, and Windows**. Apply these rules to every change:

| Banned | Use Instead |
|--------|-------------|
| Shell scripts (`.sh`, `.bash`) | Python scripts |
| `fcntl` | `fcntl` on Unix, `msvcrt` on Windows (check `sys.platform`) |
| `/tmp/` hardcoded paths | `tempfile.gettempdir()` |
| `.venv/bin/python` | `Scripts/python.exe` on Windows, `bin/python` on Unix |
| `start_new_session=True` | `subprocess.CREATE_NEW_PROCESS_GROUP` on Windows |
| `osascript` (macOS-only) | Platform dispatch: `osascript` / `notify-send` / `powershell` |
| `find`, `grep`, `sed`, `awk` in scripts | Python stdlib (`pathlib`, `re`, etc.) |

Hook commands in `hooks.json` must use `python3` (not `bash`). `${CLAUDE_PLUGIN_ROOT}` is available in hook commands.

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
- `mutations/personas.json` — 20 built-in personas (read-only at runtime)
- `mutations/adversarial.json` — 8 adversarial challenges

Runtime-generated personas/adversarials go to `.evonest/dynamic-*.json` in the target project, never to `mutations/`.

3-tier config: engine defaults < `.evonest/config.json` < runtime args.

### Novel AI

Mashbill, Solera, Proof, and Distill are maintained in the `novel-ai/`
submodule. Read `novel-ai/CLAUDE.md` for their architecture, independence
contracts, version SSOTs, tests, and release rules.
