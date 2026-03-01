# Changelog

All notable changes to Evonest are documented here.

## [0.16.0] — 2026-03-01

### Added
- `evonest_update_docs(project, target, dry_run=True)` — sync Claude Code files
  (skills, commands, agents, rules, CLAUDE.md) with current MCP tool definitions
- `dry_run=True` (default): returns JSON diff for review without writing files
- `dry_run=False`: applies changes to disk directly
- `target` parameter: filter to `"all"` / `"skills"` / `"commands"` / `"agents"` / `"rules"` / `"claude_md"`

### Tests
- 17 new tests in `test_update_docs.py` covering `_collect_targets`, `_parse_llm_output`,
  `apply_doc_changes`, `format_changes_summary`

**411 tests passing**

---

## [0.15.0] — 2026-02-27

### Added
- `evonest_improve` now blocks synchronously until the improve cycle completes — PostToolUse hooks fire at the correct time, enabling auto-chaining
- `all` parameter on `evonest_improve`: process all pending proposals sequentially until the queue is empty

### Fixed
- `improve`: shell injection risk in subprocess calls — input paths are now validated before execution (`phases.py`, `process_manager.py`)
- `improve`: git operation failures now raise explicitly instead of silently succeeding (`orchestrator.py`)
- JSON/file I/O errors in `repositories.py` and `state.py` now raise instead of returning stale data
- Rate-limit backoff in `claude_runner.py` uses proper exponential delay; zombie subprocess cleanup added to `process_manager.py`
- Subprocess zombie processes in `phases.py` cleaned up via `proc.wait()` after timeout

### Tests
- 40 new tests across `test_backlog.py`, `test_config.py`, `test_server.py`, `test_meta_observe.py`, `test_phases.py`, `test_scout.py`, `test_repositories.py`

**394 tests passing**

---

## [0.14.0] — 2026-02-24

### Fixed
- `improve`: proposals that produce no file changes are now archived to `done/` regardless of test results — prevents design-only proposals from blocking the queue indefinitely
- `improve`: proposal footer changed from "design-level proposal / no code was changed" to neutral text — prevents Execute phase from misinterpreting all proposals as non-actionable
- Plugin hooks path fixed: `post-improve.sh` used `CLAUDE_PROJECT_DIR` prefix on an already-absolute path, causing auto-chain to never fire
- `hooks.json` schema corrected: removed `matcher` field (invalid), switched to `CLAUDE_PLUGIN_ROOT`
- `__version__` now reads from `importlib.metadata` (SSOT: `pyproject.toml`) instead of hardcoded string
- `test_version` made dynamic — no longer breaks on every version bump

**354 tests passing**

---

## [0.13.0] — 2026-02-23

### Added
- **PostToolUse hook** — `hooks/post-improve.sh` auto-notifies Claude when pending proposals remain after improve completes, enabling easy chaining

### Fixed
- Plugin structure: persona command moved from `commands/` to `skills/` (files in wrong directory caused plugin load failure)
- Plugin structure: `commands/` now correctly uses directory path instead of single-file path

---

## [0.12.0] — 2026-02-23

### Fixed
- Commit messages from auto-improve/evolve now written in English (was Korean due to language config bleed)
- `evonestlock` cleanup on force kill: lock file now removed even when process is SIGKILL'd

### Improved
- 5 autonomous evolve cycles applied (personas.py type hints, JSON handling, backlog improvements)

---

## [0.11.0] — 2026-02-23

### Fixed
- `improve`: skipped proposals (Execute succeeded, no files changed) are now properly archived to `done/` instead of staying in the queue
- `improve`: proposal title logged on selection for easier tracking

### Improved
- `personas.py`: generic `dict` type parameters added (mypy strict compliance, auto-fixed by improve)

---

## [0.10.0] — 2026-02-23

### Fixed
- Ruff lint errors resolved: 17 E501/I001 violations across `cli.py`, `claude_runner.py`, `config.py`, `phases.py`, `server.py`

---

## [0.9.0] — 2026-02-23

### Fixed
- Commands now reject monorepo root as project path — must point to a package directory (`evonest/` or `distill/`)
- `--dangerously-skip-permissions` flag added to all `claude -p` subprocess calls (required for non-interactive execution)

### Improved
- Proposal descriptions wrapped at 80 chars for readability

---

## [0.8.0] — 2026-02-23

### Fixed
- `claude_runner`: reverted to `subprocess.run` — `Popen` with `stdout.read()` caused deadlocks when stderr buffer filled
- `claude_runner`: intermediate Popen + stderr streaming attempts also reverted (unstable across environments)

---

## [0.7.0] — 2026-02-23

### Added
- `claude_runner`: stream-json output format with per-turn logging — each assistant turn now logged as it arrives

---

## [0.6.0] — 2026-02-23

### Fixed
- `observe_turns_min` defaults lowered: quick 50→15, deep 100→30 — previous values caused timeouts in normal runs

---

## [0.5.0] — 2026-02-22

### Same as 0.4.0 tag (intermediate bump, no additional changes)

---

## [0.4.0] — 2026-02-22

### Added
- `claude_runner`: stream-json per-turn logging foundation

### Fixed
- `observe_turns_min` defaults aligned with actual LLM behavior

---

## [0.3.0] — 2026-02-22

### Mode Redesign
- **`evonest analyze`** — Observe-only pass that saves ALL improvements as proposals (no code changes)
- **`evonest improve`** — Execute a single proposal → Verify → commit/PR
- **`evonest evolve`** — Full autonomous cycle: Observe → Plan → Execute → Verify → commit/PR
- `--dry-run` deprecated (redirects to `analyze`)
- `--cautious` flag: pause after Plan phase for human review before executing

### Observe Efficiency
- `_gather_static_context()`: git log, file tree, test inventory collected once and shared across all personas — eliminates redundant LLM tool calls

### Claude Code Plugin
- `.claude-plugin/plugin.json` manifest with inline `mcpServers`
- Slash commands: `/evonest:analyze`, `/evonest:improve`, `/evonest:evolve`, `/evonest:identity`
- Auto-trigger skill for Claude agent integration

### Monorepo Migration
- Moved to `noory-ai/` monorepo alongside `distill` package
- Replaced `Path(__file__)` resource loading with `importlib.resources` in `mutations.py`, `phases.py`, `meta_observe.py`, `scout.py` — fixes plugin cache directory compatibility
- Added `--` pathspec to all `git ls-files` calls for monorepo file isolation
- Scoped git helper functions (`stash`, `add`, `commit`, `revert`) to project directory via `cwd` + `.` pathspec

### New MCP Tools
- `evonest_analyze` — Run analyze mode via MCP
- `evonest_improve` — Run improve mode via MCP

**329 tests passing**

---

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
