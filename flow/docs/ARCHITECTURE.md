# flow architecture — what kind of plugin is this

> This document explains the **whole picture** of the flow plugin. For a quick start see the [README](../README.md), for the provisional agreement on core concepts see [CONCEPTS](../CONCEPTS.md), and for procedure details see each `skills/flow-*`.

---

## 1. One-line definition

**General-purpose flow planner (task-type based).** A system where AI plans work as Initiative / Epic / Story / Action, executes it autonomously, and evolves to work ever better through retrospectives.

- **It only knows "how to plan"** — the procedures, gates, and retrospective mechanisms are provided by the plugin.
- **It does not know "what to build"** — the language, framework, and implementation are supplied by the project context (the playbooks in `.flow/settings.json` + optional role templates in `.claude/agents/`).
- **North star**: a system where AI understands the purpose and checks for itself whether that purpose has been reached.

Thanks to this separation, the same plugin works identically whether the target is a mobile app, a backend, or a document repository.

---

## 2. Four-tier work-item model

Work is decomposed into four tiers by scale. The SSOT for every work-item's state is the markdown files under `.flow/workspace/` (chat and memos are volatile).

```
Initiative   Groups multiple Epics under a common value proposition   _initiative.md
  └ Epic     5+ days / 3+ Stories / multiple domains                  epic-<name>/_epic.md
      └ Story  1–3 days / 5 or fewer Actions / single domain          US-NNN-<name>/_story.md
          └ Action  one unit of work = one commit                     A-NNN.md
```

- State markers: `⬜` pending / `🔄` in progress / `✅` done.
- Scale judgment is handled by `flow-scale-judgment`. Small work drops into Story-standalone mode; smaller still drops into "batch work mode" (commits only, no Epic).
- Directory standard: `epic-[name]/US-NNN-[name]/A-NNN.md`. Completed Epics are archived to `.flow/archives/`.

### Lifecycle

```
(Initiative) initiative-planning → initiative-setup → [Epic cycle]* → initiative-finish → PR
(Epic cycle) epic-planning → epic-setup
              → [story-planning → story-setup
                  → [action-planning → action-execute → action-finish]*
                → story-finish]*
              → epic-finish (→ Initiative --no-ff merge or PR)
```

The detailed procedure of each Phase and the asset bindings to load are the SSOT of `flow-phases`.

> **Branch mode (hierarchical / single — T5)**: The default is **hierarchical branch mode** (`initiative/`→`epic/`→`story/` branching, with per-tier Squash and `--no-ff` merges). But if everything is meta, small-scale, and single-domain, use **single branch mode** — track boundaries on one branch with `[epic-N][US-N][A-N]` tagged commits, and treat tier merges as "not applicable" (no faking a no-op). On entry, choose via the `**branch mode**` field in `_epic.md`/`_initiative.md`. The integration *gate* (whether to run) is the SSOT of `flow-completion`; the *strategy* (method, single-mode rules) is the SSOT of `flow-branch` (**two-axis separation**).

---

## 3. Components (5 kinds)

The plugin is made of 5 kinds of assets. The roles are divided MECE.

| asset | location | role | load method |
|------|------|------|----------|
| **skills** | `skills/` | planning / execution / retrospective procedures (32) | AI `Read`s them per Phase |
| **hooks** | `hooks/` | quality gates (system-enforced, non-bypassable) | Claude Code runs them on each event |
| **rules** | `rules/` | always-applied text rules (11) | `/flow-upgrade` syncs them into `.claude/rules/` (config delegation) → auto-loaded per session |
| **playbooks** | `playbooks.json` + `playbooks/` | per-task-type way of working (12) | one selected on task entry |
| **commands** | `commands/` | slash commands (8) | user-invoked |

### 3.1 skills — planning and execution procedures

The `flow` skill is the orchestrator (team lead). It classifies the user trigger into a mode and, for the relevant Phase, `Read`s the `flow-*` asset and carries out the procedure. No guessing — detailed procedures must always be executed after loading the asset.

> 📖 **The trigger point, behavior, I/O, and core mechanism of each of the 32 skills**: [SKILLS.md](SKILLS.md).

| group | skill | role |
|------|------|------|
| **orchestrator** | `flow` | state judgment → load asset → carry out procedure → completion handling (user-invocable) |
| | `flow-pr` · `flow-verify-commit` | PR creation / verify→commit→retrospective (user-invocable) |
| **planning** | `flow-trigger-classify` | classify an external source (issue / messenger / natural language) by task-type + scale |
| | `flow-scale-judgment` | judge scale: batch / Story / Epic / Initiative |
| | `flow-playbook-selection` | read settings, select the task-type playbook → record in `_epic.md` |
| | `flow-planning-{epic,story,action}` | per-level planning cycle (Discovery→Gate→Draft→Review→Finalize) |
| **procedure** | `flow-procedure-{initiative,epic,story,action}` | per-level creation/execution procedure |
| **lifecycle** | `flow-phases` | Phase detail + Phase-Asset binding |
| | `flow-completion` | per-level completion Hard Gate |
| | `flow-branch` | branch naming + per-tier merge strategy |
| | `flow-archive` | Epic archiving |
| | `flow-retrospective` (+ `-templates`) | retrospective procedure + templates |
| | `flow-upstream-publish` | publish retrospective-backlog upstream improvements as board tickets (`settings.upstream_board`) |
| | `flow-must-not` · `flow-issue-handling` | prohibitions / 4-path blocker handling |
| **collaboration** | `handoff-protocol` | `delegate_to` handoff protocol |
| | `debate-protocol` · `debate-redteam` | 3-stage design debate + Red Team |
| **meta** | `meta` (+ `meta-{skill,rule,prompt,agent,playbook}-procedure`, `meta-skill-writing`) | procedures for building the plugin assets themselves (for self-improvement) |

### 3.2 hooks — quality gates (system-enforced)

`hooks/hooks.json` hooks 4 events. The four validator hooks run via `uv run --no-project python` (OS-independent); `hooks.json` also wires the pure-Python skill-usage capture scripts (`scripts/append-log.py` on Skill calls, `scripts/report-usage.py` on `git push`/`gh pr create`), invoked via `python3`. The common state discovery is the SSOT of `_flow_state.py`.

| event | script | what it does |
|--------|---------|---------|
| **PreToolUse** | `hook_pre_tool_validate.py` | branch-verify 12 kinds of rules (below) — `deny` on violation |
| **PostToolUse** | `post_tool_validate.py` | audit-log every tool call to `.runtime/hook_audit.jsonl` (the source for retrospective and evolution metrics) |
| **SessionStart** | `inject_flow_context.py` | auto-inject into context the active Initiative/Epic/Story/Action state + the previous session summary. On detecting rule drift, inject a preflight prompt to confirm whether `/flow-upgrade` should run before the user's requested work |
| **Stop** | `session_relay.py` | leave in-progress work in `.runtime/_session_summary.md` so the next session picks it up |

> **Quality gate adapter** (`quality_gate_cli.py` — a verify-stage CLI, not a hook event): the PreToolUse 12 rules above enforce "document existence", but result quality (test/lint/analyze) is checked by this adapter if the project declares it via `commands` in `.flow/settings.json`. The adapter invokes and records it at the verify stage (`flow-verify-commit` Step 1 / `flow-procedure-story` §7-1) (`hook_audit.jsonl` → aggregated by `audit_report`), and on a required failure it takes the **minimal failure action** (non-zero exit — block and report, not a hook deny). If undeclared, it is a no-op (fail-safe). A full failure decision policy is a non-goal.

The 12 kinds of rules that PreToolUse enforces (number 4 is a historical gap):

| Rule | name | block condition | decision |
|:----:|------|----------|------|
| 1 | `no-action-without-doc` | active Epic but source edited without an A-NNN.md | deny |
| 2 | `no-commit-without-retro` | in-progress Action's retrospective is empty or a placeholder | deny |
| 3 | `no-push-workspace` | `git push` suspected of including the workspace | ask (deny on Codex — `ask` unsupported) |
| 5 | `no-shared-branch-merge` | merge/push to a shared branch (main/develop/…) without an explicit user request | deny |
| 6 | `no-story-without-action-doc` | active Story with 0 A-*.md but a non-SSOT file is edited | deny |
| 7 | `no-merge-without-review` | Story with all Actions ✅ but no review/evaluation record | deny |
| 8 | `no-work-without-playbook` | at the execution stage but `_epic.md` has no `**playbook**` field | deny |
| 9 | `no-node-without-purpose` | new node SSOT created without restating the `**ultimate purpose**` | deny |
| 10 | `no-shell-node-write` | workspace node created via shell redirection (>/>>/tee) (gate bypass) | deny |
| 11 | `no-finish-without-archive` | right before PR creation / shared-branch merge, a completed (✅) work-item not yet moved to `.flow/archives/` | deny |
| 12 | `no-action-without-depends-on` | new A-NNN.md created (Write/apply_patch Add) without a `**depends_on**` field | deny |
| 13 | `fan-out-attempt-mandatory` | in a Story with AT on + a parallelizable first wave, source edited with no trace (transcript) of a spawn attempt | deny |

> Path rules are checked as **paths relative to workspace_root** → no false positives even when the repo clone location includes `/apps/` etc. Tool-name aliases absorb environment differences via a frozenset. stdout is forced to UTF-8 to prevent Windows mojibake.

### 3.3 rules — always-applied text rules

Distinguished from playbooks: **rule = common to all work, always loaded** ↔ **playbook = one selected per task**. Claude Code does not auto-load the plugin's `rules/`, so `/flow-upgrade` (invoked by config delegation) copies (creates) them into `.claude/rules/` and attaches a `DO NOT EDIT` marker to sync the canonical source. On a plugin upgrade, the SessionStart hook detects drift, notifies, and re-syncs via `/flow-upgrade`.

| rule | core |
|----|------|
| `flow-rules.md` | the 12 hook-enforced kinds + text rules (`gate-enforcement-default-on` etc.) — the core source |
| `gate-enforcement-default-on` | every gate is enforced by default. "yes / OK / it's urgent" is not a bypass reason — only explicit wording ("skip / move past / bypass") |
| `purpose-anchoring` | before asking the user, try to derive the answer from the ultimate purpose |
| `decision-criteria-first` | a 4-way gate before questions (attribution / insufficient-data / ambiguous-application / criteria-conflict / criteria-absent) |
| `commit` · `directory-standard` · `handoff` · `personas` · `retro-evolution` · `ssot-vocabulary` · `tool-usage` | atomic commit / path standard / handoff / persona / retrospective→evolution / vocabulary / tool-first |

### 3.4 playbooks — per-task-type way of working

One playbook = one task type. A methodology (TDD/BDD/spec-first, etc.) is a variant within a task type. `playbooks.json` is the bundled catalog; a project can **derive** its own way of working via `.flow/playbooks/` overrides.

| playbook | task type |
|----------|---------|
| `feature` | feature development — design→test(Red)→implement(Green)→PR |
| `bug` | bug fix — reproduce→failing test→fix→regression |
| `refactor` | refactoring — pin behavior with characterization tests, then change incrementally |
| `docs` | documentation/spec writing — gather→structure→write→review |
| `research` | investigation — gather→cross-verify→structure→hand off (verification is the core) |
| `qa` | quality verification — risk-based test allocation→exploration→defect→verdict |
| `security` | security hardening — threat modeling→mitigation design→implement→inspect |
| `deploy` | deployment/infrastructure — runbook→plan→approval→incremental deploy→observe |
| `usecase-extraction` | reverse documentation — code analysis→use-case extraction→bidirectional consistency |
| `retro-processing` | retrospective processing — collect→pattern→improvement proposal→review→apply |
| `plugin-dev` | plugin self-development — rule/skill/hook/command changes + full-regression obligation + propagation obligation (rule sync / version bump) + dogfood |
| `general` | general-purpose fallback (when nothing fits any task type) |

A playbook holds only "what, in what order (flow)"; "how to do it with a specific framework (implementation)" is delegated to the lower tier (project agents / guide skills). Every playbook has the **7 elements** of the authoring standard (frontmatter / procedure / AC format / Hard Gate / feedback loop / violation handling / review·evaluation point) — details: `playbooks/README.md`.

> **RT running default-on (element 7 — review·evaluation point)**: every playbook's review gate includes **RT (Red Team) adversarial review** (persona input + the 4 essence attacks: validity / accountability / consistency / methodology — `debate-redteam`) as default-on. A bare-eye (self) review that does not apply the RT payload is not sufficient. Intensity and independence are the SSOT of `flow-procedure-action` §RT intensity matrix + `flow-verify-commit §2.5` (a **two-axis separation** like completion=gate / branch=strategy). This blocks the hole where "a review gets papered over without RT".

### 3.5 commands — slash commands

| command | purpose |
|--------|------|
| `/flow-config` | understand the project + inject `.flow/settings.json` via conversation (initial setup + re-tuning — not one-time) |
| `/flow-config-retro` | set the retrospective rigor policy (`retrospective.levels` in `.flow/settings.json`) — ground-truth inspection + explicit confirmation |
| `/flow-help` | plugin explanation + "what to do when it's not working" troubleshooting |
| `/flow-status` | look up the current settings (status) + diagnose how to run it better and recommend improvements (evaluate) |
| `/flow-upgrade` | sync the plugin's canonical rules → the project's `.claude/rules/` (propagation). Applies unsynced and new rules after a plugin upgrade — the rule-sync SSOT (invoked by config) |
| `/skill-stats` | personal Skill-tool usage statistics (top used + unused skills) |
| `/skill-stats-clear` | reset the personal skill-usage log (with confirmation) |
| `/team-skill-stats` | team monthly skill-usage totals aggregated from the rollup ticket (`scripts/team-usage-report.py`) |

---

## 4. Operation flow (from the user's viewpoint)

```
1. Setup     /flow-config — AI does ground-truth inspection → inject playbook·team → sync .claude/rules/
2. Planning  in Plan Mode, judge scale → select task-type playbook → decompose into Initiative/Epic/Story/Action (user approval)
3. Execution the main agent orchestrates by assigning experts (teammates) per the playbook procedure → verify → commit → retrospective
4. Improve   /flow-status — diagnose accumulated retrospectives → proactively recommend "how to run it better" → context evolution
```

### Delegation (delegate_to)

The Flow Manager (main) does not write code directly but delegates by **assigning teammates**.

- Delegation targets = the per-role teammates the project supplies via `.claude/agents/` (domain / data / presentation / test, etc.).
- The assigner = the main (a single team lead). A teammate cannot spawn another teammate (no middle layer).
- An Action with an explicit `delegate_to` must not be executed by the main directly. But `delegate_to: (direct)` (a meta task) is performed by the main.

---

## 5. Agent Teams mapping (the recommended parallel vehicle on Claude Code)

The plugin maps onto Claude Code **Agent Teams** (experimental). **The recommended default is to run parallelizable waves across multiple agents.** On Claude Code with AT on, Agent Teams is the richest vehicle — a lead + a **peer-to-peer collaboration team** to be **actively leveraged** (not merely the main spawning N workers and collecting results); the team is composed **dynamically** for the work at hand (no static roster). Without Agent Teams (AT off, or a non-Claude tool such as Copilot / Codex) you **still parallelize** — via parallel subagents (the Task tool) or that tool's own parallel mechanism; you drop to a single agent / the main session **only where task dependencies make a wave inherently serial**. In other words, parallel execution is the goal everywhere; Agent Teams is simply the richest way to achieve it (consistent with `flow` D4).

| flow concept | Agent Teams mapping |
|---|---|
| work-items·state·dependencies | shared task list |
| plan approval (user confirm) | plan approval (Plan Mode) |
| collaboration between teammates (peer-to-peer direct — no need to go through the lead) | mailbox messaging |
| quality gate | hooks |
| delegation (delegate_to) — spawn is main-only (No nested teams) | teammate assignment |

Activation: add `"env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" }` to `.claude/settings.json` + restart the session. (`plugin.json`'s `_recommendedEnv` is informational meta — Claude Code does not apply plugin.json's env directly.)

### VS Code Copilot environment (cross-tool)

The `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env is a Claude Code-only feature. In a non-Claude environment (e.g. VS Code Copilot, Codex) this env does not apply — **no AT env ≡ AT off** for the hook's purposes. In such an environment:

- Rule 13 (`fan-out-attempt-mandatory` hook) auto-disables — the AT-off branch passes through
- where the AT-specific team primitives aren't available, parallelize via that tool's own mechanism (or Claude's parallel subagents when AT is merely off); the main runs a wave serially only where dependencies require it
- All other hook / skill / command default behavior works normally in these environments too (ground-truth — user report 2026-06-10)
- Codex sessions are supported natively — the plugin ships a `.codex-plugin/plugin.json` manifest; hooks and scripts fall back to the `CODEX_PROJECT_DIR` env when `CLAUDE_PROJECT_DIR` is absent; skill-usage capture routes to `~/.codex` (a Codex payload is identified by its `turn_id` field — `permission_mode` is a common Claude Code field and never a discriminator); Rule 3 (`no-push-workspace`) returns `deny` instead of `ask` (Codex does not support `ask`)

→ A non-Claude user does not need the AT env — the flow works via the AT-off branch, still parallelizing through the tool's own mechanism.

---

## 6. Self-improvement loop (Φ4)

The plugin's differentiator is that **the retrospective feeds back into assets**.

```
execute → retrospective (evaluate AI behavior) → accumulate Try → (independent) retro-processing applies → update rule/skill/playbook → next execution improves
                                          └ independent of flow unit · human trigger+review (not auto-coupled)
```

- A retrospective is not a "summary of work results" but an **evaluation of AI behavior** (skill triggering, context understanding, retry count, etc.).
- Repeating the same mistake / playbook failing ≥2 times / the same pattern ≥3 times → promoted to a rule, checklist, or new-playbook candidate.
- `/flow-status`'s evaluation realizes this loop user-facing (tracking the Try→asset application rate).
- **RT (Red Team) adversarial review underpins the quality** — R1 (plan review) · R2 (deliverable review, independent agent) · R3 (retrospective self-attack). An independent RT catches defects a self-review misses, and the result feeds back as a retrospective Try. RT running is enforced default-on on the playbook review gate (§3.4) — triggered during the work, not after the fact.

---

## 7. Verification status

| item | status |
|------|------|
| hook unit tests | `hooks/tests/` — 25 files, 290 tests pass (`python -m unittest discover -s tests -p "test_*.py"`) |
| SessionStart hook smoke | confirmed normal context injection when there is no active state |
| PreToolUse hook smoke | confirmed shared-branch push blocking (deny) works normally |
| manifests | `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` valid (version is in the manifests·`CHANGELOG.md` — not pinned in this table, to prevent staleness) |
| OS compatibility | uses pathlib·`os.environ`·`uv run`, no POSIX-only modules (macOS·Windows compatible) |

---

## 8. See also

- Usage (setup→plan→execute→finish→improve): [USAGE.md](USAGE.md)
- Behavior reference for the 32 skills: [SKILLS.md](SKILLS.md)
- **Map of all files (124) with purpose + usage site**: [FILE-MAP.md](FILE-MAP.md)
- Quick start / asset conflict resolution: [README.md](../README.md)
- Provisional agreement on core concepts · unverified items: [CONCEPTS.md](../CONCEPTS.md)
- Change history: [CHANGELOG.md](../CHANGELOG.md)
- Procedure details: each `skills/flow-*/SKILL.md`
- Rule source: `rules/flow-rules.md`
- Playbook authoring standard: `playbooks/README.md`
