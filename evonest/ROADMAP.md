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

### 목표
GitHub 기반 페르소나 공유 생태계 구축으로 네트워크 효과 확보. GitHub Copilot의 Microsoft 종속, Aider의 개별 커스터마이징 한계를 넘어 커뮤니티 주도 페르소나 라이브러리로 진입 장벽 형성.

### 핵심 기능

#### 1. `evonest_import` MCP Tool
```python
evonest_import(
    source="noory-code/evonest-personas/security/owasp-expert.json",
    target_type="persona"  # or "adversarial"
)
```
- GitHub raw URL에서 페르소나/adversarial JSON 직접 다운로드
- `.evonest/dynamic-personas.json` 또는 `.evonest/dynamic-adversarials.json`에 자동 병합
- 중복 체크 및 버전 관리

#### 2. 초기 페르소나 팩 공개
`noory-code/evonest-personas` 저장소 구조:
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
│   └── (커뮤니티 기여 페르소나)
└── README.md  # 사용법, 기여 가이드
```

#### 3. 품질 기준 및 기여 가이드라인
- **페르소나 템플릿**: 필수 필드(name, role, instruction, temperature 등) 정의
- **검증 자동화**: CI에서 JSON schema validation, instruction 길이 제한 체크
- **큐레이션 프로세스**: 초기에는 maintainer approval, 이후 community upvote 시스템
- **라이선스**: MIT (evonest 본체와 동일)

### 로드맵
1. **Phase 1** (v0.4.0-alpha): `evonest_import` 툴 구현 + 3개 도메인 팩 (startup, security, data-science) 각 3개씩
2. **Phase 2** (v0.4.0-beta): GitHub 저장소 공개 + 기여 가이드라인 문서 + CI 검증
3. **Phase 3** (v0.4.0): 커뮤니티 페르소나 수집 캠페인 + 공식 블로그/문서 홍보

### 경쟁 우위
- **Copilot**: Microsoft 생태계에 종속, 커스터마이징 불가
- **Aider**: 개별 사용자 커스터마이징만 가능, 공유 메커니즘 없음
- **Evonest**: 커뮤니티 주도 페르소나 마켓플레이스 → 네트워크 효과 → 진입 장벽

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
