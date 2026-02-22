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
- `.claude-plugin/plugin.json` — plugin manifest
- `.mcp.plugin.json` — MCP server config using `${CLAUDE_PLUGIN_ROOT}`
- `commands/` — `/evonest:analyze`, `/evonest:improve`, `/evonest:evolve`
- `skills/evonest/` — auto-trigger skill for Claude

**246 tests passing**

---

## Next

- **Analysis depth levels** — `quick / standard / deep` presets; selectable at `evonest init`, overridable with `--level`
- Parallel analysis (run multiple personas concurrently)
- Proposals list UX improvements (filter, sort, search)

---

## Vision

### Persona Community (community, free)
퍼소나와 어드버세리얼을 커뮤니티가 자유롭게 공유하는 공간.
GitHub 기반 레포지토리(`wooxist/evonest-personas`)로 운영.
누구나 기여하고, 누구나 가져다 쓸 수 있다.

```
wooxist/evonest-personas
├── startup/        # 스타트업 특화
├── security/       # 보안 집중
├── data-science/   # 데이터 사이언스
└── community/      # 커뮤니티 기여
```

설치: `.evonest/dynamic-personas.json`에 직접 추가하거나, 향후 `evonest_import` 툴로.

### Nest Hierarchy (long-term)
- **Small nest** (현재): 단일 프로젝트 자율 진화
- **Medium nest**: 여러 모듈 조율 — 의존성, 순서, 인터페이스 진화
- **Large nest**: 서비스 아이덴티티 정의 → 모듈 자동 분해 → 각 모듈 진화 → 통합
