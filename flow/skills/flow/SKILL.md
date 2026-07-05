---
name: flow
description: |
  Epic/Story/Action flow management. Handles planning, execution, status tracking, and retrospectives for epics, stories, and actions. Manages work items in the .flow/workspace/epic-* directory.
  Use in the following situations: (1) "create an epic/story/action", "create a work item", (2) "next", "proceed", "continue" (when there is an in-progress work item),
  (3) "make a plan", "Planning", (4) "write a retrospective", "commit" (in a work-item context), (5) status check when .flow/workspace/epic-* files exist.
  Use this skill for any request related to work-item management, flow, epics, or stories.
user-invocable: true
metadata:
  type: procedure
  version: v1.1.1
---

# Flow Manager

A generic planner engine that autonomously manages an Epic/Story/Action-based flow (work-type based).
It analyzes the state, executes the appropriate Phase, and proceeds to the next step after user confirmation.

This skill is not tied to a specific language·framework. The actual implementation work is delegated to the teammate supplied by the project (`.claude/agents/`), while the Flow Manager orchestrates planning·status·verification·retrospectives.

> **First-time setup / re-tuning**: to configure this plugin for the project (`.flow/settings.json` — playbook·team injection) or to update it later, run **`/flow-config`**. The AI understands the project and fills it in through a dialogue with the person (not one-time — re-run when the project changes). Detail: `commands/flow-config.md`.
> **Help / when stuck**: **`/flow-help`** — plugin description + "what to do when it doesn't work" troubleshooting. Detail: `commands/flow-help.md`.
> **Status / improvement**: **`/flow-status`** — query the current setup (status) + "how to run it better" diagnosis·improvement recommendation (evaluation — Φ1·Φ4). Detail: `commands/flow-status.md`.

---

## Agent Teams mapping model (SSOT)

This flow runs on top of Agent Teams. The mapping between flow concepts and Agent Teams components uses the following table as the SSOT. Use this table as the reference vocabulary.

| Flow concept | Agent Teams mapping |
|---|---|
| Work-item unit (Epic/Story/Action)·status (⬜/🔄/✅)·dependency | shared task list |
| Work-item↔team mapping (D1): **Action = a single agent's minimal unit / Story = team scope (a teammate persists for the Story) / main = Story-team orchestrator + scheduler** | task(Action) ↔ teammate team(Story) |
| Plan approval (user confirm) | plan approval (main↔user, Plan Mode) |
| Collaboration between teammates (peer-to-peer — no lead relay needed) | mailbox messaging (teammate ↔ teammate directly) |
| Quality gate (document enforcement/retrospective enforcement/autonomous-stop prevention) | hooks (TaskCreated/TaskCompleted/TeammateIdle) |
| Delegation (delegate_to) — 1 Action = 1 teammate | teammate assignment (main spawns; a teammate cannot spawn another teammate) |
| Lead scheduling decision layer (D3): dependency graph → execution wave | the main reads task dependencies and decides serial·parallel |

### Work-item↔team model (D1)

- **Action = the minimal unit of work a single agent executes**. 1 Action = performed by 1 teammate.
- **Story = team scope**. The teammates of a Story **persist** until that Story ends (not disposable, vanishing after 1 Action). The main is the orchestrator of the Story-team.
- **Epic = a bundle of teams (Stories)**. The main orchestrates the entire Epic.

### Team-structure principles

- **Main = the single team lead (orchestrator + scheduler, fixed)**. All specialists are teammates, and no hierarchy can be built among teammates (no intermediate orchestration layer — the main does it directly).
- A teammate cannot spawn another teammate (**No nested teams** — a platform hard constraint). All teammate **assignment (spawn)** is performed by the main.
- **But collaboration (messages between teammates) is peer-to-peer direct** — the lead is not a central hub (the essence of Agent Teams). Teammates share the shared task list and directly exchange information·reviews via **mailbox**. **Only spawn·assignment·plan approval must go through the lead.** → This is a **real team collaboration** different from "the main spawns N workers in parallel and just aggregates results."
- **Tool branching**: Claude Code (AT on) = **actively use** the peer-to-peer collaboration team above (the richest parallel vehicle) / AT off = still run independent Actions **in parallel via parallel subagents (the Task tool)**, main aggregating / a tool with no spawn mechanism at all (e.g. VS Code Copilot) = the main runs the wave order itself (`ARCHITECTURE.md §5`).

### Lead scheduling decision layer (D3)

The main (lead) reads a Story's Action dependency graph and decides the **execution schedule (waves)** — not the serial enforcement of "one next Action at a time" but a dependency-based serial·parallel mix.

1. **Collect the dependency graph**: the `depends_on` of each `A-NNN.md` (SSOT source — `flow-procedure-action`) → the per-Story graph. The Story table is a derived view (not the source).
2. **Topological sort → wave split**: Actions with no dependency (or whose predecessors are complete) = the same wave (candidates for concurrent execution). Dependent Actions = the next wave.
3. **Conflict check**: if within the same wave there are Actions that modify the **same target path** (the `**target**` field), exclude them from concurrent execution → drop them to serial (best-effort; if isolation is needed, the worktree option — limits exist).
4. **User confirm = per wave**: confirm per wave (a concurrent-execution bundle), not per single Action (if a single Action, the wave size is 1).

### Parallel execution — with / without Agent Teams (D4)

- **Agent Teams active (on)**: run the independent Actions of the same wave as **truly parallel peer-to-peer teammates** — the richest vehicle.
- **Agent Teams inactive (off)**: still run the independent Actions of the same wave **in parallel via parallel subagents (the Task tool)**, the main aggregating results. Dependency order is guaranteed either way.
- **Serial only when forced**: a wave drops to serial execution only when dependencies / same-target-path conflicts make it inherently serial, or the tool provides no spawn mechanism at all. Parallel is the recommended default everywhere; AT changes the coordination richness, not the goal.

### Plan Mode boundary

- **Plan Mode usage scope**: scale judgment + Epic authoring + Story authoring (Action decomposition).
- **Autonomous-execution scope**: Action execution only. Planning acts (Epic/Story authoring) are performed only within the Plan Mode + user-approval boundary.

### G-defect — plan-approval bypass pattern

A teammate (Subagent) does not have the `EnterPlanMode`/`ExitPlanMode` tools, so it cannot perform plan approval directly.

→ **Alternative path**: the teammate sends a "plan proposal" message to the lead via mailbox, and the lead approves. (A teammate's direct plan approval is forbidden.)

---

## Rules (procedure/principle — SKILL body only)

> **Core source rule**: `flow-rules.md` of the plugin rules/ (Hook enforcement + text rules). This section is SKILL procedure/principle only.
> External rule references: atomic commit → `commit.md`, Planning First → `flow-rules.md#no-write-without-plan`, tool-first → `tool-usage.md`, purpose anchoring (derive the answer from the ultimate purpose before asking) → `purpose-anchoring.md`, immediate Step update → the project guideline "update Action Step progress". (All in the plugin rules/)

1. **Manager role**: follow the flow of state judgment → asset load → run procedure → completion handling.
2. **Asset-based execution**: always load the asset file with `Read` to run the detailed procedure. No guessing.
3. **Context saving**: skip full loading of completed (✅) Action files — load only in-progress (🔄).
4. **Context-loss recovery**: on return after a conversation summary, load `_epic.md` → judge the Phase → reload assets. Detail: `flow-phases` §context-loss recovery.
5. **Plan Mode usage scope**: the Flow Planning Phase itself is not run in Plan Mode. But **authoring a pre-plan in Plan Mode → ExitPlanMode → call the flow skill → enter the Planning Phase** is a normal flow.

---

## Mode Detection

| Trigger | Mode |
|--------|------|
| External-source input (issue-tracker ticket / messenger thread / natural-language request — work type·scale undetermined) | `trigger-classify` (route to the planning matching the scale after classification) |
| "create an initiative", "Initiative plan" | `initiative-planning` → `initiative-setup` |
| "create an epic", "Epic plan" | `epic-planning` → `epic-setup` |
| "start a story" | `story-planning` → `story-setup` |
| "run an action", "next action" | `action-planning` → `action-execute` |
| "next", "proceed", "continue" | `auto` (logic below) |
| "commit", "wrap up" + Action | `action-finish` |
| "merge", "wrap up" + Story | `story-finish` |
| "PR", "wrap up" + Epic | `epic-finish` |
| "wrap up" + Initiative (all Epics ✅) | `initiative-finish` |

### Auto Mode Logic

```
0. External-source input (issue-tracker/messenger/natural-language) + work type·scale undetermined → trigger-classify (classify → scale-judgment/playbook-selection → merge into the steps below)
0. DRAFT file exists → continue the Planning Phase
0.5. Active Initiative + all Epics ✅ → initiative-finish
1. No Epic → epic-planning (but if 2+ Epics + a common value proposition are expected, initiative-planning first)
2. Epic exists + all Stories ✅ → epic-finish
3. Story waiting (⬜) → story-planning
4. Story in progress (🔄) + all Actions ✅ → story-finish
5. Action waiting (⬜) → action-planning → **scheduling decision layer (D3) + AT env detection** (`fan-out-attempt-mandatory` rule): dependency graph → wave split (independent = concurrent candidate · dependent = next wave, same-target-path conflict is serial) + AT on = `Flow.parallel` peer-to-peer spawn / AT off = parallel subagents (the Task tool) → action-execute. User confirm is per wave. Detail: `flow-procedure-story` Step 6. A tool without the AT env (e.g. VS Code Copilot) parallelizes via its own mechanism, or runs serially if it has none — see `ARCHITECTURE.md §5`.
6. Action in progress (🔄) → continue the action (independent Actions of the same wave run in parallel — AT on = teammates / AT off = parallel subagents)
```

---

## Quick Phase Reference

### Full lifecycle

```
(Initiative scale) initiative-planning → initiative-setup → [Epic cycle]* → initiative-finish → PR
(Epic cycle / Epic standalone) epic-planning → epic-setup → [story-planning → story-setup → [action-planning → action-execute → action-finish]* → story-finish]* → epic-finish (→ Initiative --no-ff merge or PR)
```

| Phase | Description | Main Asset |
|-------|------|-----------|
| epic-planning | Agree on scope/Story decomposition | flow-planning-epic |
| epic-setup | Create branch + finalize Epic document | flow-procedure-epic, flow-branch |
| story-planning | Agree on Action decomposition | flow-planning-story |
| story-setup | Story document + create branch | flow-procedure-story, flow-branch |
| action-planning | Design the approach | flow-planning-action |
| action-execute | AC-satisfying implementation + commit | delegate_to teammate assignment |
| action-finish | Verify → commit → retrospective → status update | flow-verify-commit |
| story-finish | Squash merge + Story retrospective | flow-branch, flow-retrospective |
| epic-finish | Archive + PR | flow-archive, flow-retrospective |

📚 Phase detailed procedure + Asset binding: `../flow-phases/SKILL.md`

---

## Work-style selection (required before creating an Epic)

| Style | When to use | Rule |
|------|----------|------|
| **Batch work** | Simple repetition, formal change | Commit only, no Epic |
| **Work-item management** | Complex work, judgment needed | Retrospective required, 100% procedure adherence |

> No mixing. Selecting "work-item management" and then proceeding like "batch work" loses tracking/retrospective/verification.

---

## Context Optimization

Context-saving strategy when checking work-item status:

| Status | A-NNN.md load | Reason |
|------|---------------|------|
| ✅ Complete | ❌ Skip | Context saving |
| 🔄 In progress | ✅ Full load | Need to grasp the current Step |
| ⬜ Waiting | Header only | Confirm only the title/skill/target |

---

## Asset Files

Load the assets below with `Read` to run the detailed procedure. Paths are relative within this plugin's skills/.

| Asset | Use | Load timing |
|-------|------|----------|
| `../flow-procedure-initiative/SKILL.md` | Initiative creation/execution (top of the 4 layers — multiple Epics) | initiative-setup |
| `../flow-procedure-epic/SKILL.md` | Epic creation procedure | epic-setup |
| `../flow-procedure-story/SKILL.md` | Story start procedure | story-setup |
| `../flow-procedure-action/SKILL.md` | Action document creation | action-setup (when newly added) |
| `../flow-retrospective/SKILL.md` | Retrospective form + collection procedure | at each level wrap-up, epic-finish |
| `../flow-archive/SKILL.md` | Epic archiving procedure | epic-finish (archiving) |
| `../flow-branch/SKILL.md` | Branch creation/merge | epic-setup, story-setup, story-finish |
| `../flow-planning-epic/SKILL.md` | Epic Planning procedure | epic-planning |
| `../flow-trigger-classify/SKILL.md` | Read an external source (issue-tracker/messenger/natural-language) and classify work type + scale → route to playbook-selection·scale-judgment | trigger-classify (on external-source entry) |
| `../flow-playbook-selection/SKILL.md` | AI playbook selection mechanism (settings Read → work type → recommend → finalize → record in _epic + override Read) | epic-planning / story-planning (Plan Mode entry) |
| `../flow-planning-story/SKILL.md` | Story Planning procedure | story-planning |
| `../flow-planning-action/SKILL.md` | Action Planning procedure | action-planning |
| `../flow-scale-judgment/SKILL.md` | Work-scale determination | epic-planning Discovery |
| `../flow-phases/SKILL.md` | Phase detailed procedure | at each Phase execution |
| `../flow-completion/SKILL.md` | Completion-judgment conditions | at Action/Story/Epic wrap-up |
| `../flow-must-not/SKILL.md` | Situational reference prohibitions | when needed |
| `../flow-issue-handling/SKILL.md` | Classify blockers found during work + 4 handling paths | on blocker discovery (during Action/Story) |

---

## User Checkpoints

At the following points, **always stop** and confirm with the user (plan approval — main↔user):

| Point | Question |
|------|------|
| Epic plan draft | "I have drafted the Epic plan. Please review it." |
| Epic plan finalize | "Shall I finalize the plan and create the Epic?" |
| Story plan draft | "This is the Story Action-decomposition draft. Please review it." |
| Story plan finalize | "Shall I finalize the Action decomposition and start the Story?" |
| Action approach confirm | "Shall I proceed with this approach?" |
| Before wave execution (D3) | "Wave [N]: run Action [list] in parallel (AT on = teammates / off = parallel subagents). Shall I proceed?" — dependency-independent Actions are bundled into one wave for confirmation (if a single Action, wave size 1) |
| After wave completion (D3) | "Wave [N] complete. Shall I proceed to the next wave?" |
| After Story completion | Run Story → Epic Squash Merge → "Shall I start the next Story?" |
| After Epic completion | "Epic complete. Shall I create a PR?" |

#### Story → Epic Squash Merge

On Story completion, merge the Story branch into the Epic branch as a Squash (`--no-ff` forbidden). Since the Epic branch is not a shared branch, this can be done automatically. Protection of a shared branch (integration branch) follows the project branch-strategy guide (`flow-branch`). Detailed procedure: `../flow-branch/SKILL.md`.

---

## Progress feedback (Clear Feedback)

Even during autonomous execution, always let the user know "what is happening now" — so autonomy does not become a black box (visibility instead of suspicion). Every unit of work is accompanied by **an immediate status display + a status-SSOT update**.

### 3 states (Loading / Success / Error)

| State | Display | Example |
|------|------|-----|
| **Loading (in progress)** | What is being done now | "Running A-001 — redesigning the config skeleton" |
| **Success (complete)** | ✅ + what was done + verification | "✅ A-001 complete (AC-1·5 pass)" |
| **Error (fail)** | ❌ + cause + action | "❌ Verification failed — [cause]. Trying [action]" |

### Per-level feedback

| Level | Start (Loading) | Complete (Success) | Status-SSOT update |
|------|---------------|---------------|-----------|
| **Action** | "Running A-NNN — [work]" | "✅ A-NNN (AC pass)" | `A-NNN.md` ⬜→🔄→✅ immediately |
| **Story** | "Starting US-NNN — [goal]" | "✅ US-NNN (all AC / retrospective)" | `_story.md` status + Story table |
| **Epic** | "Epic progress: N/M Story" | "✅ Epic (overall review / retrospective)" | `_epic.md` Story status table |

### Principles
- **Immediacy**: update the SSOT + report right after a Step completes (not at commit time)
- **During autonomous execution**: report at each milestone (Story/Epic completion) + always show Error immediately. Per-tool-call narration may be omitted
- **purpose-anchoring parity**: progress reports also keep the "how far against the ultimate purpose" context

---

## Completion Rules

📚 Detail: `../flow-completion/SKILL.md`

---

## Retrospective Rules

Retrospective = **AI-behavior evaluation** (not a summary of work results)

| Level | Focus | Evaluation target |
|------|------|----------|
| Action | AI-behavior efficiency | Skill firing, context understanding, retry count |
| Story | Plan quality | Action splitting, spec clarity |
| Epic | Strategy appropriateness | Story composition, scope setting |

---

## Delegation (delegate_to)

When implementation is needed, the Flow Manager does not execute directly but delegates via **teammate assignment**.

- **Delegation target = the teammate supplied by the project**. The project supplies role-specific teammates (e.g. domain/data/presentation/test/UI/general, etc.) via `.claude/agents/`.
- **Assigning actor = the main (team lead)**. Since a teammate cannot spawn another teammate, the teammate specified in an Action's `delegate_to` is assigned by the main.
- **No direct execution of a delegate_to-specified Action** (`no-direct-handoff-exec`). The Flow Manager does not write code directly; the assigned teammate does. But `delegate_to: (direct)` (meta work, etc.) is performed by the Flow Manager directly.
- **Teammate lifetime = Story scope** (D1): a delegated teammate is not disposable, vanishing after 1 Action, but **persists** for that Story. A subsequent Action of the same Story can be taken over by the same teammate (main re-assignment). The team disbands at Story end.
- **Collaboration-path separation**: information sharing·review between already-active teammates is done peer-to-peer via direct mailbox. Only when a new teammate spawn·assignment change·plan approval is needed does it go through the main (mailbox → main approval).

---

## MUST NOT

📚 Detail: `../flow-must-not/SKILL.md`
