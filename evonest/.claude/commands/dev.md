# Dev Workflow

Run full development checks:

1. `uv run ruff check src/ tests/` — lint
2. `uv run ruff format --check src/ tests/` — format check
3. `uv run mypy src/evonest/` — type check
4. `uv run pytest --cov=evonest` — tests with coverage

Fix any issues found, then commit.
