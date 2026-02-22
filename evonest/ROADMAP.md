# Evonest Roadmap

## ✅ v0.1.0 — Python MCP Server

- Project scaffold, core data layer, progress & history
- Mutations (personas, adversarials, dynamic loading)
- Phase execution: Observe → Plan → Execute → Verify
- MCP server (FastMCP, stdio), CLI, docs

---

## ✅ v0.2.0 — Proposals, PR Mode, Scout

- Business-logic proposals (human-review workflow)
- `code_output: "pr"` — opens GitHub PRs instead of direct commits
- Scout phase (external search-based mutation generation)
- `--all-personas` flag for deterministic persona sweep
- Language injection across all phases
- Rate limit retry logic

---

## ✅ v0.3.0 — Mode Redesign + Plugin

### Modes
- **`evonest analyze`** — Observe only → all improvements → `proposals/` (no code changes)
- **`evonest improve`** — Select proposal → Execute → Verify → commit/PR
- **`evonest evolve`** — Full cycle: Observe → Plan → Execute → Verify → PR
- `--dry-run` deprecated (redirects to analyze)
- `--cautious` flag: pause after Plan for human review

### Observe Efficiency
- `_gather_static_context()`: git log, file tree, test inventory collected once
- Shared across all personas — no redundant LLM tool calls

### Claude Code Plugin
- `.claude-plugin/plugin.json` — plugin manifest with inline `mcpServers`
- `commands/` — `/evonest:analyze`, `/evonest:improve`, `/evonest:evolve`, `/evonest:identity`
- `skills/evonest/` — auto-trigger skill for Claude

### Monorepo & Plugin Compatibility
- `importlib.resources` for all package resource loading (replaces `Path(__file__)`)
- Git pathspec scoping (`-- .`) for monorepo isolation

**329 tests passing**

---

## Next

- **Analysis depth levels** — `quick / standard / deep` presets; selectable at `evonest init`, overridable with `--level`
- Parallel analysis (run multiple personas concurrently)
- Proposals list UX improvements (filter, sort, search)

---

## Vision

### Persona Community (community, free)
A space for the community to freely share personas and adversarials.
Operated as a GitHub-based repository (`noory-code/evonest-personas`).
Anyone can contribute, anyone can use them.

```
noory-code/evonest-personas
├── startup/        # Startup-focused
├── security/       # Security-focused
├── data-science/   # Data science
└── community/      # Community contributions
```

Installation: add directly to `.evonest/dynamic-personas.json`, or via a future `evonest_import` tool.

### Nest Hierarchy (long-term)
- **Small nest** (current): Single-project autonomous evolution
- **Medium nest**: Multi-module orchestration — dependencies, ordering, interface evolution
- **Large nest**: Service identity definition → automatic module decomposition → per-module evolution → integration
