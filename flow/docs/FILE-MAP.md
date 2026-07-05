# flow file map (FILE-MAP) — purpose + where each file is used

> This document tracks **every file of the flow plugin in one place** — file / one-line purpose / where used (who loads·calls it and when). For the big picture see [ARCHITECTURE](ARCHITECTURE.md); for skill behavior details see [SKILLS](SKILLS.md).
>
> **Scope**: all 124 source files (including FILE-MAP itself). Generated artifacts (`__pycache__/*.pyc`, `.pytest_cache/*`) are excluded (build outputs). The work-item SSOT (`.flow/workspace/`) is a project runtime asset, so it is excluded from the plugin file map.
>
> **Verification**: `find . -type f -not -path '*/.git/*' -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' | wc -l` = 124 = the number of table rows in this map.

---

## 1. Top level + manifests (10)

| File | Purpose | Where used |
|------|------|--------|
| `.claude-plugin/plugin.json` | Claude Code plugin manifest — name(flow)·version(see plugin.json)·keywords·`_recommendedEnv` guidance | when Claude Code loads the plugin |
| `.codex-plugin/plugin.json` | Codex plugin manifest — interface metadata for the Codex plugin cache | when Codex loads the plugin |
| `README.md` | Quick start — one-line plugin definition + asset conflict resolution | user entry point |
| `CHANGELOG.md` | SemVer change history | updated on release |
| `CLAUDE.md` | Plugin-local working guidelines (`/flow-upgrade` impact review · no project-specific source names) | when modifying flow assets |
| `CONCEPTS.md` | Record of provisional agreements·unverified items of the core concepts | during design discussion·consistency review |
| `ROADMAP.md` | Harness-engineering roadmap (strategy — not the behavior SSOT) | roadmap planning |
| `config-defaults.json` | Plugin-internal default-settings SSOT (`upstream_board` coordinates · `skill_usage`) — seeded into `.flow/settings.json` by `/flow-config`·`/flow-upgrade` | config seeding |
| `personas-extension.md` | Authoring template for a project to define its own role personas (app developer/planner/designer, etc.) | when authoring project personas |
| `playbooks.json` | Playbook catalog (bundled — 1 task type = 1 playbook, methodology is the variant) | `Read` by `flow-playbook-selection` |

## 2. skills/ — planning·execution·retrospective procedures (34)

> AI `Read`s these per Phase to carry out the procedure. No guessing. 32 SKILL.md + README + 1 reference.

| File | Purpose | Where used (load point) |
|------|------|--------|
| `skills/README.md` | skills directory guide | — |
| `skills/flow/SKILL.md` | **Orchestrator (team lead)** — status judgment→asset load→procedure→completion (user-invocable) | every flow entry point |
| `skills/flow-pr/SKILL.md` | PR creation — PR skeleton for merging shared branches (user-invocable) | "create a PR" |
| `skills/flow-verify-commit/SKILL.md` | After Action implementation: verify→review(R2)→commit→retrospective(R3) (user-invocable) | action-finish |
| `skills/flow-trigger-classify/SKILL.md` | External source (issue/messenger/natural language)→task type+scale classification | on external-source entry |
| `skills/flow-scale-judgment/SKILL.md` | batch/Story/Epic/Initiative scale judgment + ultimate-purpose interview | Planning Discovery |
| `skills/flow-playbook-selection/SKILL.md` | Read settings→select task-type playbook→record in `_epic.md` | on Plan Mode entry |
| `skills/flow-planning-epic/SKILL.md` | Epic Planning 7 stages (Discovery→Gate→Draft→R1→Finalize) | epic-planning |
| `skills/flow-planning-story/SKILL.md` | Story Action decomposition·AC·Pre-flight 4-axis·load latest retrospective | story-planning |
| `skills/flow-planning-story/references/action-decomposition.md` | Detailed Action decomposition criteria (planning-story aid) | referenced during story-planning |
| `skills/flow-planning-action/SKILL.md` | Lightweight Action Planning (Discovery→Alignment→Finalize) | action-planning |
| `skills/flow-procedure-initiative/SKILL.md` | Initiative creation/execution (top of the 4 tiers) | initiative-setup |
| `skills/flow-procedure-epic/SKILL.md` | Epic creation (task-list init·structure·Story decomposition table) | epic-setup |
| `skills/flow-procedure-story/SKILL.md` | Story execution (A-NNN full generation·branch·Squash) | story-setup~finish |
| `skills/flow-procedure-action/SKILL.md` | Action document creation (delegate_to·RT intensity) | action-setup |
| `skills/flow-phases/SKILL.md` | Phase details + Phase-Asset binding SSOT | on Phase transition |
| `skills/flow-completion/SKILL.md` | Per-level completion-decision Hard Gate | on finish |
| `skills/flow-branch/SKILL.md` | Branch naming + per-tier merge (Squash/--no-ff) + shared-branch protection | setup·finish |
| `skills/flow-archive/SKILL.md` | Epic archiving (temporary→permanent migration) | epic-finish |
| `skills/flow-retrospective/SKILL.md` | Retrospective procedure (evaluate AI behavior, not a work summary ❌) | at each level's finish |
| `skills/flow-retrospective-templates/SKILL.md` | Retrospective templates (per-level·code/meta variants·metrics) | when writing a retrospective |
| `skills/flow-upstream-publish/SKILL.md` | Publish retrospective-backlog upstream improvements as detailed board tickets (`settings.upstream_board`, zero board hardcoding) | retro-processing backlog routing |
| `skills/flow-must-not/SKILL.md` | Per-situation prohibitions | when needed |
| `skills/flow-issue-handling/SKILL.md` | Blocker classification + 4 handling paths (immediate/side/retrospective/handoff) | on discovering a blocker |
| `skills/handoff-protocol/SKILL.md` | `delegate_to` delegation protocol (teammate-assignment mechanism) | on Action delegation |
| `skills/debate-protocol/SKILL.md` | Design-debate 3 stages (separating discovery/integration/verification) | structural-improvement debate |
| `skills/debate-redteam/SKILL.md` | RT (Red Team) persona + attack/defense (R1/R2 payloads) + executor-selection SSOT | debate Phase C |
| `skills/meta/SKILL.md` | Skill/Rule/Prompt/Subagent creation·management entry point (self-improvement) | asset meta work |
| `skills/meta-skill-procedure/SKILL.md` | Skill creation procedure (Reference vs Procedure·trigger conflicts) | new skill |
| `skills/meta-skill-writing/SKILL.md` | Skill authoring guide (frontmatter·Progressive Disclosure) | skill authoring |
| `skills/meta-rule-procedure/SKILL.md` | Rule creation procedure (auto-load location·MUST distinction) | new rule |
| `skills/meta-prompt-procedure/SKILL.md` | Prompt asset creation (skill vs prompt boundary) | new prompt |
| `skills/meta-agent-procedure/SKILL.md` | Subagent (teammate) creation/improvement procedure (team operation — process-teammates table + `research.sources` schema in §2.5) | new teammate |
| `skills/meta-playbook-procedure/SKILL.md` | Playbook authoring·editing (7-element standard·task-type primary) | new playbook |

## 3. rules/ — always-applied text rules (12)

> `/flow-upgrade` (delegated call from config) syncs to the project's `.claude/rules/` → auto-loaded per session. Distinct from playbooks (rule = always / playbook = 1 per task).

| File | Purpose | Where used |
|------|------|--------|
| `rules/README.md` | rules directory guide | — |
| `rules/flow-rules.md` | **Core source** — 12 hook-enforced kinds + text rules (`gate-enforcement-default-on`, `fan-out-attempt-mandatory`, etc.) | every session |
| `rules/commit.md` | Git commit rules (Conventional + work-based) | on commit |
| `rules/decision-criteria-first.md` | Pre-question 4-way gate (attribution/data/application/conflict/absence) | just before a user question |
| `rules/purpose-anchoring.md` | Gate to derive the answer from the ultimate purpose (4-way (c) detail) | just before a question |
| `rules/directory-standard.md` | `.flow/` directory standard + 2 rule-kind distinction | workspace work |
| `rules/handoff.md` | Delegation enforcement signal (code Action requires delegate_to) | Action delegation |
| `rules/personas.md` | SSOT for the 3 planner-process personas (manager/attacker/analyst) | persona citation |
| `rules/retro-evolution.md` | Retrospective→evolution loop enforcement (Try 5-way classification·independent reflection·ownership routing) | on retrospective |
| `rules/ssot-vocabulary.md` | SSOT standard-term dictionary + compound-word blocking | when authoring·verifying |
| `rules/tool-usage.md` | Tool priority (dedicated tool > general shell) | on tool selection |
| `rules/verify-before-assert.md` | Ground-truth-first, no-assertion gate | before asserting·concluding |

## 4. hooks/ — quality gates (system-enforced, 35)

> `hooks.json` hooks into 4 events. The validator hooks use `uv run --no-project python` (OS-independent); the skill-usage capture scripts are wired via `python3`.

| File | Purpose | Where used (event) |
|------|------|--------|
| `hooks/README.md` | hooks directory guide | — |
| `hooks/hooks.json` | Hook trigger registration (event↔script mapping — also wires `scripts/append-log.py`·`scripts/report-usage.py`) | loaded by Claude Code |
| `hooks/_flow_state.py` | Common workspace-state discovery SSOT + rule-sync decision·apply helpers (shared module) | imported by other hooks·`/flow-upgrade` |
| `hooks/rule_sync_cli.py` | Rule-sync detect/apply CLI (called by `/flow-upgrade` with `${CLAUDE_PLUGIN_ROOT}`) | `/flow-upgrade` |
| `hooks/hook_pre_tool_validate.py` | PreToolUse — 12-kind rule branch validation (deny on violation) | PreToolUse |
| `hooks/post_tool_validate.py` | PostToolUse — tool-call audit logging (source of retrospective metrics) | PostToolUse |
| `hooks/inject_flow_context.py` | SessionStart — inject active work-item state + previous-session summary | SessionStart |
| `hooks/session_relay.py` | Stop — leave in-progress work as a session summary | Stop |
| `hooks/audit_report.py` | Per-work-item audit aggregation CLI (`hook_audit.jsonl` → measured counts, no embellishment) | retrospective metrics |
| `hooks/quality_gate_cli.py` | Quality-gate adapter CLI — run project-declared checks (settings `checks`, free-form names), record, minimal failure action | verify stage (`flow-verify-commit` Step 1) |
| `hooks/tests/test_flow_state.py` | `_flow_state` completion-marker decision test | `python -m unittest` |
| `hooks/tests/test_pre_tool_rules.py` | Pure-function rule tests for shared branch·no-verify, etc. | regression |
| `hooks/tests/test_no_node_without_purpose.py` | Rule 9 (ultimate-purpose enforcement) test | regression |
| `hooks/tests/test_askuserquestion_gate.py` | AskUserQuestion 4-way gate test | regression |
| `hooks/tests/test_disk_state_rules.py` | T1 safety net — disk-state-dependent rules + shell-redirect guard test | regression |
| `hooks/tests/test_no_depends_on.py` | Rule 12 (`depends_on` field enforcement) test | regression |
| `hooks/tests/test_fan_out_attempt.py` | Rule 13 (fan-out attempt enforcement) test | regression |
| `hooks/tests/test_silent_fallback.py` | Rule 13 silent-fallback / AT-off allowance regression | regression |
| `hooks/tests/test_vscode_tool_aliases.py` | VS Code Copilot tool-alias (`apply_patch`, etc.) regression | regression |
| `hooks/tests/test_rule_drift.py` | Rule-sync drift decision·apply·SessionStart-notification regression | regression |
| `hooks/tests/test_rule_override.py` | Propagated-rule model regression (unconditional override + `.gitignore` registration + orphan deletion) | regression |
| `hooks/tests/test_audit_capture.py` | Audit-record schema (block-entry capture) regression | regression |
| `hooks/tests/test_audit_report.py` | `audit_report` aggregation CLI regression | regression |
| `hooks/tests/test_fail_safe.py` | Fail-safe regression — high-stakes tools deny on a validate() exception (no fail-open) | regression |
| `hooks/tests/test_gate_scope_fixes.py` | Completed-epic scan-scope regression (Rules 1/2/7/13 must ignore ✅ epics) | regression |
| `hooks/tests/test_hook_matcher.py` | `hooks.json` PreToolUse matcher coverage regression (no silently dead rules) | regression |
| `hooks/tests/test_list_all_skills.py` | `scripts/list-all-skills.py` marketplace scan shape guard | regression |
| `hooks/tests/test_nfc_normalization.py` | Hangul NFC/NFD normalization regression (gates + status parsers) | regression |
| `hooks/tests/test_plugin_staleness.py` | Plugin staleness detection regression (env branching + version comparison) | regression |
| `hooks/tests/test_plugin_upgrade.py` | CLI plugin auto-upgrade command resolution regression | regression |
| `hooks/tests/test_quality_commands.py` | `read_quality_commands` fail-safe regression (settings `commands[]`) | regression |
| `hooks/tests/test_quality_gate.py` | `quality_gate_cli` adapter regression (no-op / pass / required failure) | regression |
| `hooks/tests/test_retro_rigor.py` | Retrospective rigor-label hook mapping regression | regression |
| `hooks/tests/test_seed_settings.py` | `seed_settings_defaults` regression (`upstream_board` seeding by `/flow-upgrade`) | regression |
| `hooks/tests/test_skill_usage.py` | Skill-usage capture on/off switch + hook registration regression | regression |

## 5. commands/ — slash commands (11)

| File | Purpose | Where used |
|------|------|--------|
| `commands/README.md` | commands directory guide | — |
| `commands/flow-config.md` | `/flow-config` — understand the project→inject `.flow/settings.json` (rule sync delegated to `/flow-upgrade`) | initial setup·re-tuning |
| `commands/flow-config-retro.md` | `/flow-config-retro` — set the retrospective rigor policy (`retrospective.levels`) via ground-truth inspection + confirmation | retro-policy tuning |
| `commands/flow-help.md` | `/flow-help` — plugin description + troubleshooting | when stuck |
| `commands/flow-status.md` | `/flow-status` — setup view + improvement recommendation (evaluate) | status·diagnosis |
| `commands/flow-upgrade.md` | `/flow-upgrade` — plugin rule canonical → sync (propagate) to `.claude/rules/`. Rule-sync SSOT (config delegates) | after a plugin upgrade |
| `commands/skill-stats.md` | `/skill-stats` — personal Skill-tool usage statistics (top used + unused skills) | usage inspection |
| `commands/skill-stats-clear.md` | `/skill-stats-clear` — reset the personal skill-usage log (with confirmation) | log reset |
| `commands/team-skill-stats.md` | `/team-skill-stats` — team monthly totals from the rollup ticket (calls `scripts/team-usage-report.py`) | team usage inspection |
| `commands/references/flow-config-procedure.md` | `/flow-config` detailed onboarding procedure SSOT | `Read` by `/flow-config` |
| `commands/references/flow-config-retro-procedure.md` | `/flow-config-retro` detailed procedure SSOT | `Read` by `/flow-config-retro` |

## 6. playbooks/ — ways of working per task type (14)

> 1 playbook = 1 task type. Pick 1 on task entry. A project derives from it via `.flow/playbooks/` override.

| File | Purpose (task type) | Where used |
|------|------|--------|
| `playbooks/README.md` | Playbook authoring 7-element standard guide | when authoring a playbook |
| `playbooks/CANDIDATES.md` | Playbook-enhancement candidate backlog | on self-improvement |
| `playbooks/feature.md` | Feature development — design→Red→Green→PR (methodology variant selectable) | on playbook selection |
| `playbooks/bug.md` | Bug fix — reproduce→failing test→fix→regression | 〃 |
| `playbooks/refactor.md` | Refactoring — pin characterization tests then change incrementally | 〃 |
| `playbooks/docs.md` | Documentation·spec authoring — gather→structure→write→review | 〃 |
| `playbooks/research.md` | Investigation — gather→cross-verify→structure→handoff (verification is the core) | 〃 |
| `playbooks/qa.md` | Quality verification — risk-based test allocation→exploration→defect→judgment | 〃 |
| `playbooks/security.md` | Security hardening — threat modeling→mitigation design→implementation→inspection | 〃 |
| `playbooks/deploy.md` | Deployment·infra — runbook→plan→approval→incremental deploy→observe | 〃 |
| `playbooks/usecase-extraction.md` | Reverse documentation — code analysis→use-case extraction→bidirectional consistency | 〃 |
| `playbooks/retro-processing.md` | Retrospective processing — collect→pattern→improvement proposal→review→reflect | 〃 |
| `playbooks/plugin-dev.md` | Plugin self-development — rule/skill/hook/command changes + full regression + propagation + dogfood | 〃 |
| `playbooks/general.md` | General fallback (when no task type fits) | 〃 |

## 7. scripts/ — skill-usage pipeline utilities (4)

> Pure-Python (stdlib) — no external CLI dependencies (except read-only `gh` where noted); invoked as `python3` (see `hooks/hooks.json` and the skill-stats commands). Works in both Claude Code and Codex sessions (`CODEX_PROJECT_DIR` fallback; log routing by the Codex-only `turn_id` payload field).

| File | Purpose | Where used |
|------|------|--------|
| `scripts/append-log.py` | Capture Skill tool invocations into the agent home's skill-usage log (`~/.claude` or `~/.codex`); best-effort — never blocks the tool call | PreToolUse (Skill matcher) |
| `scripts/list-all-skills.py` | List every available skill (project + `~/.claude` + `~/.codex` + plugin caches), plugin-namespaced as `<plugin>:<skill>` | `/skill-stats` (unused-skill detection) |
| `scripts/report-usage.py` | On `git push`/`gh pr create`, roll the personal skill-usage log up into the monthly aggregation ticket; best-effort | PostToolUse (Bash matcher) |
| `scripts/team-usage-report.py` | Monthly team skill-usage totals + unused candidates from the rollup ticket (read-only `gh` lookup) | `/team-skill-stats` |

## 8. docs/ — documents (4)

| File | Purpose | Where used |
|------|------|--------|
| `docs/ARCHITECTURE.md` | Big picture — one-line definition·4 tiers·5 asset kinds·execution flow·self-improvement | understanding the plugin |
| `docs/SKILLS.md` | Trigger point·behavior·I/O reference for each of the 32 skills | skill detail |
| `docs/USAGE.md` | How to use (configure→plan→execute→finish→improve) | user guide |
| `docs/FILE-MAP.md` | (this document) full-file purpose+where-used map | file tracking |

---

> **Update rule**: on adding/removing a file, update this map + the asset count in ARCHITECTURE.md §3 at the same time. Omission check = compare against the row count of the `find` command at the top.
