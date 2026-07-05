# flow usage

> How you actually use it. In order: install → setup → plan → execute → finish → improve. For the whole picture see [ARCHITECTURE](ARCHITECTURE.md), for per-skill behavior see [SKILLS](SKILLS.md).

---

## 0. Install + activate (one time)

1. **Install from the marketplace** — add the `flow` plugin.
2. **(Recommended) Agent Teams env** — add to `.claude/settings.json`, then **restart the session**:
   ```json
   { "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
   ```
   Even if unset, everything works — you still parallelize via parallel subagents (the Task tool) or your tool's own parallel mechanism; only dependency-serial waves run one at a time.
3. **Run `/flow-config`** — step 1 below. This handles rule syncing and directory creation too.

> ⚠️ The env in `plugin.json` is not applied automatically — you must use `.claude/settings.json` + a session restart.

---

## 1. Setup — `/flow-config`

The step that tames the plugin **to fit this project**. Not a form wizard, but an onboarding where the AI does ground-truth inspection of the project and fills things in through conversation. **It is not one-time** — re-run it (re-tuning) when the stack or task type changes.

**What happens**:
1. The AI does ground-truth inspection of the project (existing skills · rules · plugins · code stack) → **infers and recommends** the playbooks to activate.
2. Branches the conversation into one of 4 cases (empty project / own skills / multiple plugins / composite) → settles the relationship with existing assets (coexist / leverage / override).
3. If a bundled playbook doesn't fit, it scaffolds (DRAFT) a **project-derived playbook** with the 7 elements → approval.
4. Creates `.flow/settings.json` (active playbooks + agents) + the `.flow/{workspace,archives,playbooks}/` directories.
5. **Syncs** the plugin's `rules/` into `.claude/rules/` (delegated to `/flow-upgrade`, created files carry a `DO NOT EDIT` marker) → the rules auto-load on session reload. After a later plugin upgrade, the SessionStart hook notifies of any unsynced state, and the agent first confirms whether to run `/flow-upgrade` before starting the user's requested work.

**What the user does**: only **confirm/correct** the AI's recommendations. (Don't Make Me Think — you don't get handed a blank form.)

```
/flow-config            # understand via conversation
/flow-config feature    # start with a starting-playbook hint
```

> Related: `/flow-config-retro` tunes the retrospective rigor policy (`retrospective.levels` in `.flow/settings.json`) separately, the same way — ground-truth inspection first, then your confirmation.

---

## 2. Planning — decompose work-items in Plan Mode

When starting work, judge the scale and decompose it into work-items. **No level may execute without a plan** (`no-write-without-plan`) — the plan is enforced via deliverables (Action document · playbook field · ultimate purpose) and the hook blocks otherwise.

**Flow** (AI-led, the user approves at checkpoints):
1. **Scale judgment** — the AI first asks for the ultimate purpose (why / higher value) and judges scale in 7 steps. On a borderline, it confirms along with a recommendation.

   | scale | criterion | entry |
   |------|------|------|
   | batch work | simple repetition · format change | commits only, no Epic |
   | Story standalone | 1–3 days / Action ≤5 / single domain | story-planning |
   | Epic | 5+ days / 3+ Stories / multiple domains | epic-planning |
   | Initiative | 2+ Epics / common value proposition | initiative-planning |

2. **Playbook selection** — the AI recommends a playbook matching the task type (feature/bug/refactor/docs/…) → confirm → record in `_epic.md`.
3. **Decomposition** — Discovery (ground-truth code inspection) → Assumption Gate (confirm assumptions) → Alignment (question goal · scope · completion criteria) → Draft (work-item document with a `[DRAFT]` marker) → AI self-review (R1) → Refinement → **user approval** → remove DRAFT.

**When starting from an external source** — throw an issue-tracker ticket / messenger thread / natural language at it as-is, and `trigger-classify` classifies it by task-type + scale and merges it into the flow above.

**Trigger examples**:
```
"make an epic" / "plan an Epic"        → epic-planning
"start a story"                        → story-planning
"handle this issue: <ticket/link/content>"  → trigger-classify → routing
```

---

## 3. Execution — perform Action → verify → commit → retrospective

Once the plan is settled, it executes autonomously. The main (orchestrator) assigns and orchestrates experts (teammates) per the playbook procedure.

**One Action cycle**:
1. **Settle the approach** (action-planning) — "when/why" (business rules) before "how" + minimal change scope + impact-scope Grep.
2. **Execute** (action-execute) — the teammate named in `delegate_to` performs it (not the main directly). Only a meta task with `delegate_to: (direct)` is performed by the main.
3. **Finish** (action-finish, `flow-verify-commit`) — static analysis → AC test (mandatory if the test keyword is present) → R2 code review → atomic commit (`[epic][story][action]`) → state ✅ → retrospective (KPT).

**Triggers**:
```
"next" / "proceed" / "continue"     → auto-judge the next step matching the current state
"run action" / "next action"        → action-planning → execute
"commit" / "finish" (+ Action)      → action-finish
```

**Progress feedback** — even during autonomous execution, always show Loading ("running A-001") / Success ("✅ A-001 (AC passed)") / Error ("❌ verification failed — cause·action").

---

## 4. Finish — Story → Epic → PR

| level | trigger | what happens |
|------|--------|---------|
| **Story done** | "next" or all Actions ✅ | record review·evaluation (RT running) → Story retrospective → **Story→Epic Squash merge** (hierarchical branch mode — automatic, the Epic branch is not shared / **in single branch mode merge = not applicable**, tracked by tagged commits) → `_epic.md` ✅ |
| **Epic done** | "PR" / "finish" (+Epic) | comprehensive review → Epic retrospective → archiving (interactive 2-stage) → **PR creation** (`flow-pr`) |
| **Initiative done** | "finish" (+Initiative) | confirm all Epics ✅ → Φ retrospective → PR |

**Shared-branch protection** — a merge/push to main/develop/release etc. happens only when the **user explicitly instructs it** ("merge to main"). A plain "yes" / "OK" is not a bypass reason. If the AI proceeds automatically, the hook blocks it.

---

## 5. Improve — `/flow-status`

See whether the flow is running well, and get advice on how to run it better.

```
/flow-status            # both current settings + evaluation
/flow-status status     # lookup only (active playbook · team · in-progress work-items · rules)
/flow-status evaluate   # evaluation only (improvement recommendations)
```

**What the evaluation does**: diagnoses the accumulated retrospectives → **proactively recommends improvements** from signals like "N Trys not yet applied to assets", "the same defect repeated N times", "playbook failed ≥2 times". The user only applies/defers. The more recommendations are applied, the more the context evolves into "an environment where the AI works well" (the Φ4 self-improvement loop).

> Related: `/skill-stats` (personal skill-usage statistics — top used + unused skills), `/team-skill-stats` (team monthly totals from the rollup ticket), `/skill-stats-clear` (reset the personal log).

---

## 6. When you're stuck — `/flow-help` + troubleshooting

```
/flow-help          # full guidance
/flow-help hook     # a specific topic only
```

| symptom | cause | action |
|------|------|------|
| a code edit is **blocked** | source edited without an A-NNN.md (hook) | first write the `A-NNN.md` for that Action |
| **commit is blocked** | in-progress Action's retrospective is empty (hook) | write the retrospective (Keep/Problem/Try), then commit |
| **merge/push blocked** | shared branch without an explicit user request (hook) | request explicitly, like "merge to main" |
| **teammate doesn't appear** | Agent Teams env inactive | set the env + restart the session (or it runs via fallback) |
| **playbook not applied** | no `.flow/settings.json` | run `/flow-config` |
| **too many unnecessary questions** | missing purpose anchoring | check the top SSOT's `**ultimate purpose**` — if it derives from the purpose, it won't ask |

---

## Core usage rules (to remember)

- **No execution without a plan** — every level. If there's no deliverable (Action document · playbook · ultimate purpose), the hook blocks it.
- **Checkpoints are non-bypassable** — gates are enforced by default. A bypass takes only explicit wording ("skip / move past / bypass"); "yes / OK / it's urgent" doesn't count.
- **No commit without a retrospective** — the retrospective is an evaluation of AI behavior, not a summary of work.
- **Shared branches take an explicit request only** — no automatic merge/push.
- **The main orchestrates, the teammate only executes** — an Action with an explicit `delegate_to` must not be executed by the main directly.
