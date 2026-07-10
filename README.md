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
/plugin install evonest
```

### [Novel AI](https://github.com/noory-code/novel-ai) — Novel's Open Plugin Stack

Mashbill, Solera, Proof, and Distill live in the public `noory-code/novel-ai`
repository. This repository keeps that project at [`novel-ai/`](novel-ai/) as a
submodule for coordinated development; plugin installation uses Novel AI's own
marketplace so it never depends on recursive submodule checkout.

| Plugin | Responsibility |
|---|---|
| Mashbill | Visual thinking canvas and Novel artifact publisher |
| Solera | Work planning, deterministic gates, and execution order |
| Proof | Append-only decisions referenced by stable ID |
| Distill | Durable knowledge extraction and recall |

**Install:**

```text
/plugin marketplace add noory-code/novel-ai
/plugin install mashbill@novel-ai
/plugin install solera@novel-ai
/plugin install proof@novel-ai
/plugin install distill@novel-ai
```

### [Flutter Cask](flutter-cask/) — Flutter Package Guide Skills

Curated reference skills for Flutter development. Each skill gives Claude instant access to usage patterns, best practices, and code examples for the most common Flutter packages.

- 33 skills across state management, routing, Firebase, UI, testing, and more
- No Python dependencies — pure skill pack
- Covers riverpod, go-router, freezed, hive, admob, and 28 more

**Install:**
```
/plugin marketplace add noory-code/noory-ai
/plugin install flutter-cask
```

### [Stage](stage/) — Durable Execution Harness

Portable `.stage/` harness for LLM-led long-running projects. Stage separates artifact status, context ownership, decision gates, verification, and retrospectives.

- Global artifact time: `past` / `present` / `future`
- Local work lifecycle: `before` / `during` / `after` / `retrospective`
- Plain Markdown templates for Codex, Claude, Windows, Linux, and macOS

**Install:**
```
/plugin marketplace add noory-code/noory-ai
/plugin install stage
```

## Development

Initialize the submodule after cloning this repository:

```bash
git submodule update --init
```

Each package is independent. Work inside the relevant subdirectory:

```bash
cd evonest   # or: cd novel-ai/distill
uv sync
uv run pytest
uv run mypy src/
uv run ruff check src/ tests/
```

See [CLAUDE.md](CLAUDE.md) for full command reference and architecture notes.

## License

Each package is MIT licensed. See individual `pyproject.toml` or `.claude-plugin/plugin.json` for details.
