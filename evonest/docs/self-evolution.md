# Self-Evolution — Running Evonest on Evonest

Evonest runs on itself. This repo has its own `.evonest/` and evolves through the same cycle every other project does. Dogfooding is a first-class use case.

## Setup

The `.evonest/identity.md` in this repo already describes the project. No additional init needed.

Key boundaries already set:
```markdown
## Boundaries (DO NOT touch)
- .evonest/
- mutations/
- .claude/
- .mcp.plugin.json
- .claude-plugin/
```

These protect the plugin manifest, built-in personas, and the evolution data itself from being auto-modified.

## Running analysis

```bash
# From the evonest repo root
evonest analyze -p .

# Or via MCP tool
evonest_analyze(project="/path/to/evonest")

# All personas (broader coverage)
evonest analyze -p . --all-personas
```

## Cautious mode (recommended for self-evolution)

Before executing any proposal on the engine itself, review the plan:

```bash
evonest evolve -p . --cautious
# → shows plan, waits for [y/N] before executing
```

Or via MCP:
```
evonest_evolve(project="...", cautious=True)
# → review plan summary
evonest_evolve(project="...", resume=True)   # proceed
evonest_evolve(project="...", resume=False)  # cancel
```

## What to watch for

- **Test gate**: `uv run pytest` must pass before any commit. Set in `config.json`:
  ```json
  { "verify": { "test": "uv run pytest" } }
  ```
- **Type safety**: proposals touching `core/` should pass `uv run mypy src/evonest/`
- **Boundaries**: double-check `identity.md` Boundaries before running evolve — the engine will respect them but verify they're complete

## Workflow

```
analyze → review proposals → improve one → verify tests pass → repeat
```

Not every proposal needs to be executed immediately. The `proposals/` queue accumulates — pick the ones that align with the current phase.
