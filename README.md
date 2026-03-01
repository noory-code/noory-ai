# noory-ai

Plugin collection for Claude Code — MCP servers and skill packs.

## Packages

### [Evonest](evonest/) — Autonomous Code Evolution

Runs 20 specialist personas against your codebase (security auditor, chaos engineer, performance analyst, etc.) and lets adaptive selection determine which approaches work best for your project.

- **Observe → Plan → Execute → Verify** cycle with auto-revert on failure
- Git stash before every change; lock file prevents concurrent runs
- Adaptive persona weights — successful personas run more often over time
- Direct commit or PR mode (`code_output: "pr"`)

**Install:**
```
/plugin marketplace add noory-code/noory-ai
/plugin install evonest@noory-code/noory-ai
```

### [Distill](distill/) — Knowledge Distillation

Extracts reusable patterns, decisions, and lessons from Claude Code conversations — so Claude remembers what matters across sessions. No API key required (uses MCP Sampling).

- Automatic extraction at session end via hooks
- 3-tier scope: global (`~/.distill/`) → workspace → project (`.distill/`)
- FTS5 full-text + semantic vector search
- Crystallizes chunks into `distill-*.md` rule files

**Install:**
```
/plugin marketplace add noory-code/noory-ai
/plugin install distill@noory-code/noory-ai
```

### [Solera](solera/) — Layered Workflow Execution

Structured project execution framework — Phase → Goal → Epic → Story → Action Item. Like the solera aging method, where layers of work blend and deepen over time into something complete.

- 5-level hierarchy: Phase (quarterly) → Goal → Epic → Feature → commit
- Auto-updates HANDOFF.md on session end via Stop hook
- PR creation workflow when Epic is complete

**Install:**
```
/plugin marketplace add noory-code/noory-ai
/plugin install solera@noory-code/noory-ai
```

### [Flutter Cask](flutter-cask/) — Flutter Package Guide Skills

Curated reference skills for Flutter development. Each skill gives Claude instant access to usage patterns, best practices, and code examples for the most common Flutter packages.

- 33 skills across state management, routing, Firebase, UI, testing, and more
- No Python dependencies — pure skill pack
- Covers riverpod, go-router, freezed, hive, admob, and 28 more

**Install:**
```
/plugin marketplace add noory-code/noory-ai
/plugin install flutter-cask@noory-code/noory-ai
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

Each package is MIT licensed. See individual `pyproject.toml` or `.claude-plugin/plugin.json` for details.
