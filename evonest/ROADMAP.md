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

## v0.4.0 — Persona Community

### Goals
Build a GitHub-based persona sharing ecosystem to achieve network effects. Surpass GitHub Copilot's Microsoft lock-in and Aider's individual customization limitations by creating a community-driven persona library that forms a competitive moat.

### Core Features

#### 1. `evonest_import` MCP Tool
```python
evonest_import(
    source="noory-code/evonest-personas/security/owasp-expert.json",
    target_type="persona"  # or "adversarial"
)
```
- Download persona/adversarial JSON directly from GitHub raw URLs
- Auto-merge into `.evonest/dynamic-personas.json` or `.evonest/dynamic-adversarials.json`
- Duplicate detection and version management

#### 2. Initial Persona Packs Release
`noory-code/evonest-personas` repository structure:
```
noory-code/evonest-personas
├── startup/
│   ├── lean-startup-advisor.json
│   ├── product-market-fit.json
│   └── growth-hacker.json
├── security/
│   ├── owasp-expert.json
│   ├── threat-modeler.json
│   └── penetration-tester.json
├── data-science/
│   ├── ml-ops-engineer.json
│   ├── model-optimizer.json
│   └── data-pipeline-architect.json
├── community/
│   └── (community-contributed personas)
└── README.md  # Usage guide and contribution instructions
```

#### 3. Quality Standards and Contribution Guidelines
- **Persona template**: Define required fields (name, role, instruction, temperature, etc.)
- **Automated validation**: JSON schema validation and instruction length checks in CI
- **Curation process**: Maintainer approval initially, community upvote system later
- **License**: MIT (same as the Evonest core)

### Roadmap
1. **Phase 1** (v0.4.0-alpha): Implement `evonest_import` tool + 3 domain packs (startup, security, data-science) with 3 personas each
2. **Phase 2** (v0.4.0-beta): Publish GitHub repository + contribution guidelines documentation + CI validation
3. **Phase 3** (v0.4.0): Community persona collection campaign + official blog/documentation promotion

### Competitive Advantages
- **Copilot**: Locked into Microsoft ecosystem, no customization possible
- **Aider**: Only individual user customization, no sharing mechanism
- **Evonest**: Community-driven persona marketplace → network effects → competitive moat

---

## Next

- **Analysis depth levels** — `quick / standard / deep` presets; selectable at `evonest init`, overridable with `--level`
- Parallel analysis (run multiple personas concurrently)
- Proposals list UX improvements (filter, sort, search)

---

## Vision

### Nest Hierarchy (long-term)
- **Small nest** (current): Single-project autonomous evolution
- **Medium nest**: Multi-module orchestration — dependencies, ordering, interface evolution
- **Large nest**: Service identity definition → automatic module decomposition → per-module evolution → integration
