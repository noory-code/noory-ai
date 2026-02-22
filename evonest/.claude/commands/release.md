# Release Checklist

Before tagging a release:

1. All tests pass: `uv run pytest`
2. Type check clean: `uv run mypy src/evonest/`
3. Lint clean: `uv run ruff check src/ tests/`
4. Version bumped in `pyproject.toml` and `src/evonest/__init__.py`
5. ROADMAP.md updated
6. README.md up to date
7. `git tag v{VERSION}` and push
