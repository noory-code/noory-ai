# Changelog

All notable changes to Evonest are documented here.

## [0.2.0] — 2026-02-19

### Added
- **Biz-logic proposals** — Three new built-in personas (Domain Modeler, Product Strategist, Spec Reviewer) generate `category: "proposal"` improvements that are saved to `.evonest/proposals/` instead of modifying code. Business logic evolution stays under human review.
- **PR mode** — `code_output: "pr"` config option creates a branch and opens a pull request via `gh pr create` instead of committing directly. Recommended for self-evolution targets.
- **Scout phase** — External search-based mutation generation. Every `scout_cycle_interval` cycles, Scout extracts keywords from `identity.md`, searches externally, scores findings 1–10 against project alignment, and injects qualifying findings (≥ `scout_min_relevance_score`) as stimuli. Results cached in `.evonest/scout.json`.
- **`evonest_scout` MCP tool** — On-demand Scout execution without waiting for the cycle interval.
- **`--no-scout` CLI flag** — Skip Scout phase for a run.

### Configuration
New fields in `.evonest/config.json`:
- `code_output` (default: `"commit"`) — `"commit"` or `"pr"`
- `scout_enabled` (default: `true`)
- `scout_cycle_interval` (default: `10`)
- `scout_min_relevance_score` (default: `6`)
- `max_turns.scout` (default: `15`)

---

## [0.1.0] — 2026-02-17

### Initial release
- **Autonomous evolution engine** — Observe → Plan → Execute → Verify cycle loop
- **12 built-in personas** — Code quality, testing, performance, security, and more
- **3 adversarial challenges** — Break interfaces, performance regression, security scanner
- **Meta-observe phase** — Analyzes evolution performance, generates project-specific dynamic personas
- **MCP server** (FastMCP, stdio transport) with 10 tools: `evonest_init`, `evonest_run`, `evonest_status`, `evonest_history`, `evonest_config`, `evonest_identity`, `evonest_progress`, `evonest_backlog`, `evonest_stimuli`, `evonest_decide`
- **CLI** — `evonest init`, `evonest run`, `evonest status`, `evonest history`, `evonest progress`, `evonest config`, `evonest identity`, `evonest backlog`
- **3-tier config resolution** — Engine defaults < `.evonest/config.json` < runtime args
- **Weighted mutation selection** — Per-persona success rate tracking
- **Convergence detection** — Areas touched 3+ times flagged as converged
- **Stimulus system** — Inject external context to guide the next cycle
- **Decision drop** — Leave human decisions for the execute phase to consume
- **Git integration** — Stash checkpoint before execute, commit on success, revert on failure
- **223 tests** — Full coverage of core engine, phases, config, state, and all MCP tools
