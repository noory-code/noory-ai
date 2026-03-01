# Contributing to Evonest

## Development Setup

```bash
cd evonest
uv sync
uv run pytest          # run all tests
uv run mypy src/       # type check
uv run ruff check src/ tests/  # lint
uv run ruff format src/ tests/ # format
```

## Commit Format

```
type(scope): description
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

Examples:
```
feat(evonest): add evonest_update_docs tool
fix(phases): clean up zombie subprocesses on timeout
test(orchestrator): add convergence detection tests
```

- Commit messages must be in **English**
- Each commit must pass build + tests on its own
- Each commit contains exactly one purpose

## Pull Request Process

1. Fork the repository and create a branch from `main`
2. Make your changes with tests
3. Ensure all checks pass:
   ```bash
   uv run pytest
   uv run mypy src/
   uv run ruff check src/ tests/
   ```
4. Open a pull request with a clear description of the change

## Architecture

- `tools/` — thin MCP wrappers (no business logic)
- `core/` — all logic lives here
- `core/state.py` — single entry point for `.evonest/` directory access
- `core/claude_runner.py` — all `claude -p` subprocess calls

See [docs/architecture.md](docs/architecture.md) for the full picture.

## Code Conventions

- Python 3.11+, `pathlib.Path` everywhere (never `os.path`)
- Type hints on all functions; mypy strict mode
- Line length: 100 chars (ruff)
- Pydantic is **not** used in evonest (uses dataclasses)

## Testing

- Add tests for any new functionality in `tests/`
- Tests must pass with `uv run pytest`
- 411 tests currently passing — do not regress

## Reporting Issues

Please open an issue at https://github.com/noory-code/noory-ai/issues
