---
name: flow-procedure-story
description: "Story execution procedure. story-setup~story-finish — referenced when generating all A-NNN.md files, the Story branch, Squash merge, and the retrospective."
user-invocable: false
metadata:
  type: procedure
  version: v1.1.3
---

# Story start procedure

The detailed procedure the flow manager (the main team lead) loads in `story-setup` mode.

> ⚠️ **Prerequisite required**: `story-planning` complete (Action decomposition confirmed in Plan Mode + plan approval done)
> For the Planning procedure, see `flow-planning-story`.

## Agent Teams mapping (terminology SSOT)

This procedure's flow concepts map to Agent Teams components as follows (consistent with the `flow` skill's "Agent Teams mapping model"):

| Flow concept | Agent Teams mapping |
|---|---|
| Task (Epic/Story/Action) · state · dependency | shared task list |
| Task↔team (D1): **Story = team scope (teammate persists for the Story) / Action = single-agent unit** | teammate team (Story) ↔ task (Action) |
| Generating all A-NNN.md files | shared task list item creation + hooks (creation enforced) |
| No merge if the retrospective is empty | hooks (TaskCompleted gate) |
| Squash · confirm proceeding to the next Story | plan approval (main ↔ user) + mailbox messaging |
| Delegation (`delegate_to`) | teammate assignment (main spawns) |
| lead scheduling (D3): depends_on graph → execution waves | main reads task dependencies and decides serial/parallel |

> Generating all A-NNN.md files and enforcing the retrospective are reinforced by hooks — regardless of whether the hook blocks, perform this procedure's Hard Gate (`ls` verification) directly. The planning act (Action decomposition) is already finished inside Plan Mode; this procedure covers only execution (setup ~ finish).

## Preconditions

- `story-planning` complete: `_story.md` AC + Action decomposition confirmed by plan approval
- The `[DRAFT]` marker is removed

## Procedure

### Step 1: Mode detection and precondition check

**Mode detection**: ① Decide standalone/Epic mode by whether an Epic folder exists ② **Read the branch mode (sub/single)** — the `**branch mode**` field of the active `_epic.md` (inherits from `_initiative.md` if it is under an Initiative). The single-mode branches in Step 1.5 · §7-4 query this value (unrecorded = default sub).

```bash
# Check whether the Epic folder exists
ls .flow/workspace/epic-*/

# Epic mode condition: the .flow/workspace/epic-[name]/[Story-ID]-[name]/ structure exists
# Standalone mode condition: no Epic folder, or the .flow/workspace/story-[name]/ structure

# Query the branch mode (single/sub branch trigger — flow-branch §single branch mode)
grep "branch mode" .flow/workspace/epic-*/_epic.md   # if absent, _initiative.md / default = sub
```

**Epic mode preconditions**:
```bash
ls .flow/workspace/epic-[name]/[Story-ID]-[name]/_story.md
```
+ Check that the Epic branch exists (branch strategy: see `flow-branch`)

If absent, stop: "You must create the Epic first"

**Standalone mode preconditions**:
```bash
ls .flow/workspace/story-[name]/_story.md
```

If absent, stop: "You must complete Story Planning first"

**Check for an existing folder**:

```bash
# Epic mode
ls .flow/workspace/epic-[name]/

# Standalone mode
ls .flow/workspace/
```

On finding a duplicate folder:
1. Confirm with the user (reuse / delete then create new / migrate)
2. After handling, confirm that **exactly 1** Story folder exists

---

### Step 1.5: Confirm the previous Story's integration (Squash) (🚨 Hard Gate)

> **Always** confirm when starting the 2nd or later Story in Epic mode.
> If the previous Story's integration (Squash) is not complete, **story-setup entry is forbidden**.

> **Integration *criterion* SSOT = `flow-completion` § upper-integration Hard Gate** (including the sub/single branch-mode branch). This Step only cites that criterion and applies it to the *previous Story* — it does not restate the criterion.

**Execution**: In sub-branch mode, confirm that the previous Story's integration (Squash) commit exists in the upper-branch log (`flow-branch` supplied command). In **single-branch mode**, apply completion's [single-branch mode] check to the previous Story (do not look for a Squash commit).

If incomplete: "The previous Story ([Story-ID])'s integration (Squash) is not complete. Please run story-finish first." (Single-branch mode: "Previous Story ([Story-ID]) Actions incomplete or retrospective missing — story-finish first.")

---

### Step 2: Create the Story branch (🚨 never skip)

> **Under any circumstances** you must create the Story branch.
> No "proceed on the current branch".

The branch naming/creation commands are supplied by the **project branch strategy guide** (`flow-branch`). Follow the base branch and naming rules for standalone mode / Epic mode respectively.

---

### Step 3: Create the Action files (A-NNN.md) (🚨 required — never skip)

> **Hard Gate**: All Action files must be created to enter action-execute (creating all shared-task-list items = hooks enforced).
> If files are not created → action-execute entry forbidden → return to this Step to create them.

Create a file for each Action:

**Standalone mode**:
```
.flow/workspace/story-[name]/
├── _story.md
├── A-001.md  ← create
├── A-002.md  ← create
└── ...
```

**Epic mode**:
```
.flow/workspace/epic-[name]/[Story-ID]-[name]/
├── _story.md
├── A-001.md  ← create
├── A-002.md  ← create
└── ...
```

### Large-Story intermediate-commit guide

> For a large Story with 5 or more Actions, apply an intermediate-commit strategy.

| Action count | Commit strategy |
|-----------|----------|
| ≤ 4 | Commit on each Action completion (default) |
| 5-7 | Intermediate verification + commit on completing 2-3 Actions |
| 8+ | Intermediate commits per layer/domain, running the project verification command at each commit |

**Post-creation verification** (always run):
```bash
# Standalone mode
ls .flow/workspace/story-[name]/A-*.md

# Epic mode
ls .flow/workspace/epic-[name]/[Story-ID]-[name]/A-*.md
# Expected: A-001.md A-002.md ... (must match the Story's Action count)
```

**A-NNN.md required structure**:

```markdown
**Story**: [Story-ID]-name
**Action**: A-NNN
**Ultimate Purpose**: [restate the ultimate purpose of the parent _story.md — inherited without alteration. 🚨 hook `no-node-without-purpose` enforced — on omission, A-NNN.md creation is blocked]
**delegate_to**: [teammate name — lowercase-kebab or (direct)]     ← code work default = expert (meta/analysis is (direct)); details in flow-procedure-action §delegate_to decision criteria
**delegation_mode**: auto | subagent | direct      ← default auto (`handoff.md` standard)
**Target**: `[work target path]`
**AC mapping**: AC-1, AC-2
**Status**: ⬜

## Goal
[concrete 1-2 sentences]

## Completion criteria
| Criterion | Verification method | Status |
|------|----------|------|
| [criterion] | [measurable verification command / manual check] | ⬜ |

## Expected output
- `[output path]` (create/modify)

## Step 1: Setup
## Step 2: Implement
## Step 3: Wrap up
## Result (write on completion)
## Retrospective
```

> 🚨 The completion criteria and expected output are **fixed before implementation**. No retrofitting after implementation.
> Already fixed in the Planning Phase — there can be no TBD Action.

---

### Step 4: Update the _story.md Action table + Handoff strategy (🚨 required)

> When a Story has multiple Actions, the whole delegation (teammate assignment) plan must be graspable at a glance.

**_story.md required sections**:

**Required header — `**Ultimate Purpose**` 1 line** (right below the title) — 🚨 hook `no-node-without-purpose` enforced (on omission, _story.md creation is blocked):

```markdown
**Ultimate Purpose**: [restate the ultimate purpose of the parent _epic.md / for a standalone Story (Story-scale entry), this Story's goal is itself the ultimate purpose = the top]
**Story Type**: User | Technical    <!-- default User. For tech/infra/refactor/tech-debt/build/CI, Technical (TS-NNN) — user persona exempt, process persona + technical AC. ssot-vocabulary consistency -->
```

> The entry scale is the top. If under an Epic, inherit the ultimate purpose of the _epic.md directly above; for a standalone Story, this Story is the top of the tree — do not invent a nonexistent parent. The value's origin = `flow-scale-judgment` §ultimate-purpose interview. The child A-NNN.md restates this 1 line.
> **Story Type** (`ssot-vocabulary`): User Story (US-NNN — user persona / value AC) / Technical Story (TS-NNN — process persona / technical verification AC). Directory and number also match the type (`US-NNN-*`/`TS-NNN-*`). The persona/AC branch is `flow-planning-story` §Story-type branch.

**Expected Action table** (delegate_to + depends_on columns required):

```markdown
## Expected Actions

| Action | Title | delegate_to | depends_on | Target |
|--------|------|-----------|-----------|------|
| A-001 | [title] | [owner — lowercase-kebab] | [] | [target] |
| A-002 | [title] | [owner] | [A-001] | [target] |
```

> 🚨 **The `depends_on` column = a derived view (at-a-glance visibility)** (D2). The dependency SSOT origin is each `A-NNN.md`'s `depends_on` field (`flow-procedure-action`). On conflict, A-NNN.md wins (`ssot-write-only`). Main topologically sorts this graph → schedules it into execution waves (D3 — `handoff-protocol` §3.1.1).

**Handoff strategy section** (required when there are 2+ Actions or the owners differ):

```markdown
## Handoff strategy

| Action | Owner | Call guidance | After return |
|--------|------|----------|--------|
| A-001 | **[owner — lowercase-kebab]** | "Delegate to [owner] to [work content]" | Flow: verify/commit |

> **Principle**: The delegated owner (teammate) only implements. Verification, commit, retrospective, and status update are handled after returning to main (Flow).
```

> If there are Actions with different owners, add: `**Delegation caution**: A-001 is [owner1], A-002 is [owner2] — owners differ, so confirm assignment.`

> Teammate assignment (delegation) mechanism details: see `handoff-protocol`.

---

### Step 5: Update _epic.md status

Change the corresponding Story status ⬜ → 🔄 (shared-task-list status update)

---

### Step 6: Compute the schedule + run the first wave (D3)

> Story start = activate the lead-scheduling decision layer → proceed through running the first wave

0. **Compute the schedule (lead-scheduling decision layer — D3)**: collect the `depends_on` of all A-NNN.md → topological sort → split into execution waves (independent = same wave · dependent = next wave). Same-target-path conflicts within one wave are lowered to serial. User confirmation is per wave. Details: `handoff-protocol` §3.1.1.
0.5. **Team/solo self-judgment (1 line — judgment enforced, use is free / not blocked)**: at each wave entry, judge and record in one line — **for code work, an expert team is the default** (`delegate_to`=expert); for analysis/baseline/meta work, main handles directly (solo). **On choosing solo, 1 line of reason** (e.g. "single-file surgical fix"). Not an enforcement (deny) — it prevents main from unconsciously slipping into solo. Criterion SSOT: `flow-procedure-action` §delegate_to decision criteria.
1. **For each Action in the first wave** load A-NNN.md → check `delegate_to` / `delegation_mode` / `depends_on`. **Detect the AT env (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`)** — **AT on = parallel spawn of independent Actions as a peer-to-peer team (`Flow.parallel`)** / **AT off = still parallelize independent Actions via parallel subagents (the Task tool), main aggregating; drop to serial only where dependencies force it** (D4 consistency). A non-Claude tool (e.g. VS Code Copilot / Codex) does not support the AT env — parallelize via that tool's own mechanism; see `ARCHITECTURE.md §5`.
   - **AT-on aggressive team pattern**: beyond simple parallel spawn (main aggregates), actively use patterns where teammates collaborate **peer-to-peer directly** — multi-perspective investigation/review / competing hypotheses cross-rebutting each other / cross-layer independent ownership (`handoff-protocol` §3.2.2). Only spawn, assignment, and plan approval must go through the lead.

2. **Delegation decision + spawn mechanism** (`delegate_to` — `handoff.md` / `no-direct-handoff-exec` / `handoff-protocol` consistency):
   - **`delegate_to` = procedure name** (lowercase-kebab) → **load that procedure and guide its execution**
   - **`delegate_to` = teammate name** (lowercase-kebab) → **main spawns the teammate** (main only — a teammate cannot spawn another teammate)
     - **Multiple independent Actions** in the same wave (AT on) → `Flow.parallel([thunk1, thunk2, ...])`
     - Explicit **dependency chain** + per-stage verification (optional) → `Flow.pipeline(items, stage1, stage2, ...)`
     - **Single spawn** or an analysis task → `Agent({description, subagent_type, prompt})` (`subagent_type='Explore'` for analysis / teammate name for work)
     - **`delegation_mode`**: `auto` (default — system decides automatically) / `subagent` (force spawn) / `direct` (main directly)
   - **`delegate_to: (direct)`** → **main (Flow Manager) performs directly** (meta work, etc.). But **main can also spawn sub-tasks with the `Flow.parallel` / `Agent` tools** (e.g. parallel meta-work analysis — this procedure's dogfood).
   - **No `delegate_to`** → Flow runs directly (fallback)

3. **Wrap up** (verify + commit + retrospective)

> **Spawn call examples**:
> - **Independent parallel** (same wave):
>   ```
>   Flow.parallel([
>     () => Agent({description: 'A-001 work', subagent_type: 'X', prompt: ...}),
>     () => Agent({description: 'A-002 work', subagent_type: 'Y', prompt: ...})
>   ])
>   ```
> - **Single spawn** (Agent):
>   ```
>   Agent({description: 'A-001 analysis', subagent_type: 'Explore', prompt: 'A-NNN context + mission'})
>   ```
> - **`delegate_to:(direct)` meta-work parallel** (main spawns sub-tasks):
>   ```
>   Flow.parallel([
>     () => Agent({description: 'A-001 meta analysis', subagent_type: 'Explore', prompt: ...}),
>     () => Agent({description: 'A-002 meta analysis', subagent_type: 'Explore', prompt: ...})
>   ])
>   // after aggregating results, main applies the change in this context
>   ```

**Post-completion report**:

**Standalone mode**:
```
🚀 Story '[name]' started
- Branch: [Story branch]
- Action files: [N] created
- Current progress: wave 1 — [Action list]

Proceed to the next wave?
```

**Epic mode**:
```
🚀 Story '[Story-ID]-[name]' started
- Branch: [Story branch]
- Action files: [N] created
- Current progress: wave 1 — [Action list]

Proceed to the next wave?
```

---

### Step 7: Story wrap-up (after all Actions complete)

> Enter when all Actions are ✅.

> **Story-finish order (fixed)**: verify (7-1) → review/evaluate (7-2) → remediation (handle unmet) → status ✅ (7-5) → integrate/commit (7-4). 🚨 **No early ✅** — do not mark an Action/Story ✅ before review/evaluation (7-2) and remediation are complete (`ssot-write-only`, to avoid polluting the state origin). "Implementation is done, so ✅" is a violation — ✅ is the marker of passing review/evaluation.

#### 7-0. Pre-check the hook enforcement trigger conditions (right before entering Story-finish)

Story-finish triggers the following PreToolUse hooks in a chain — rather than correcting after being blocked, satisfy them in advance right before entry (`verify-before-assert` — pre-confirm the hook trigger conditions):
- **Rule 2 (`no-commit-without-retro`)**: Is the retrospective section of in-progress Actions substantive (no placeholder / too-short retrospective)?
- **Rule 7 (`no-merge-without-review`)**: For a Story whose Actions are all ✅, is there a `## Review/Evaluation` record (7-2) in `_story.md`?
- **Rule 11 (`no-finish-without-archive`)**: For a completed (✅) task, was `archives/retro-<name>.md` extracted/consolidated before PR/merge?

#### 7-1. Full verification

Run the **project verification commands** (code generation / static analysis / tests, etc.). The verification command set is supplied by the project playbook (e.g. code generation → static analysis → tests order).

> **Quality-gate adapter**: If the project declared checks via `commands` (test/lint/analyze/required_checks) in `.flow/settings.json`, in this full verification call the declared checks and record them via `uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/quality_gate_cli.py" run`, and block on a required failure (minimal-failure behavior). If undeclared, no-op. (A verification-stage call convention, not a hook deny — consistent with `flow-verify-commit` Step 1.)

#### 7-2. Output review/evaluation (Hard Gate)

> **HARD GATE**: If Story output review/evaluation is not run, integration (Squash)/merge is blocked. **Same enforcement standing** as the retrospective gate (`no-commit-without-retro`) — not a flow word that "happens only if the author remembers", but procedural enforcement.

Per the **review points** the playbook declared (`## Feedback loop locations` + the procedure's review stage), review the output and record the evaluation result:

1. **Run the review (including behavior review)** — perform the review the playbook specified (design review / code review / PR review, etc.). If the project supplies a review teammate, delegate to that teammate; otherwise main reviews directly against the playbook criteria. Prioritize essence defects (contract violation / layer intrusion / missing boundary). **Behavior review — check whether the agent's output followed the standard**: for code-generation output, check each of **① structure** (standard directory) **② location** (shared packages vs app apps) **③ naming** (prefix/convention) for violations. This is the post pair of the code-generation agent's **pre-work gate (F8 — load structure/location/naming before creating files)** — the pre-gate is the first line, this review is the second line of defense. (The concrete standard is supplied by the project guide / app CLAUDE.md.)
2. **AC evaluation** — run each AC's verification method → decide met/unmet (Story completion-criteria table ⬜→✅).
3. **Record** — record the review result (High-priority issues + handling) + AC evaluation result in `_story.md`.

> **On unmet**: integration/merge blocked — complete review/evaluation first.
> **Bypass**: only on the user's explicit expression (skip / move on / bypass / skip over). The bypass fact = obligation to record in the retrospective Problem.
>
> ⚠️ **Universal principle**: This gate enforces only "whether review/evaluation **was run**". **What to review and how to evaluate (the concrete) is declared by the playbook** (review stage · AC format). Plugin = the gate (enforcement); playbook / project review teammate = the concrete.

#### 7-3. Write the Story retrospective

> Retrospective = evaluation of AI procedure compliance. Not code-quality / planning evaluation ❌

**Add a retrospective section to _story.md**:

```markdown
## Story retrospective

### Keep (procedures followed well)
- [e.g. ran after creating all Action files, followed delegate_to delegation]

### Problem (violations/inefficiencies)
- [e.g. ran only a scope different from what was agreed, ran without loading the procedure]

### Try (improvements)
- [e.g. strengthen loading the procedure into a Hard Gate, reflect violation items into the procedure]
| Priority | Item | Target | Content |
|---------|------|------|------|
| [High/Mid/Low] | [item] | [procedure/rule file] | [concrete change] |
```

> 🚨 No merge if the retrospective is empty (hooks enforced — TaskCompleted gate).

#### 7-4. Story integration (Squash) → upper branch

> **Integration *criterion* SSOT = `flow-completion` § upper-integration Hard Gate** (including the sub/single branch-mode branch). This subsection does not restate the criterion — it holds only the **execution method (how)**.

**Execution (sub-branch mode)**: **Integrate (Squash)** the Story branch into the upper branch (Epic mode: the Epic branch / standalone mode: the project branch strategy definition). The concrete command/branch naming is supplied by `flow-branch`. In **single-branch mode**, the integration step is "not applicable" per the completion criterion (no merge command to run — only a merge record in `_story.md`).

> Merging into a shared branch (e.g. main/base/release branch) is **forbidden without the user's explicit expression** (`no-shared-branch-merge`).

#### 7-5. Update _epic.md status

Change the corresponding Story status 🔄 → ✅

#### 7-6. Completion report

```
✅ Story '[Story-ID]-[name]' complete
- Retrospective: Keep [N], Problem [N], Try [N]
- Story integration (Squash): [upper branch] ← [Story branch]
- _epic.md status: ✅

Proceed to the next Story?
```

---

## 1 file = 1 Action principle

```
✅ Correct decomposition:
A-001: [output 1] (1 file)
A-002: [output 2] (1 file)

❌ Wrong decomposition:
A-001: [the whole domain] (multiple files at once)
```

**Exception**: part files (main + generated file), barrel export

## Outputs

**Standalone mode**:

| Item | Path |
|------|------|
| Story branch | (project branch strategy definition) |
| Action files | `.flow/workspace/story-[name]/A-NNN.md` |

**Epic mode**:

| Item | Path |
|------|------|
| Story branch | (project branch strategy definition) |
| Action files | `.flow/workspace/epic-[name]/[Story-ID]-[name]/A-NNN.md` |
