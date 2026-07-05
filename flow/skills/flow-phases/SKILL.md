---
name: flow-phases
description: "Detailed per-Phase procedures + Phase-Asset binding table. Referenced on Flow Phase transitions."
user-invocable: false
metadata:
  type: reference
  version: v1.0.0
---

# Phases

The detailed procedures for every Phase. This is the **Phase state machine** of the task-type-based planner engine.

## Agent Teams mapping model

This skill's flow concepts map onto the following Agent Teams elements. The procedure body operates on the premise of this mapping.

| Flow concept | Agent Teams element | Meaning |
|----------------|------------------|------|
| Work-item status (⬜ / 🔄 / ✅) | shared task list status | the single source for each Action/Story/Epic's progress |
| User checkpoint (🚦) | plan approval (main ↔ user) | user approval before entering the next Phase |
| Quality Hard Gate (no commit without retrospective / document verification) | hooks (TaskCreated / TaskCompleted / TeammateIdle) | verification auto-enforced at the state-transition point |
| Plan Mode | scale judgment + Epic authoring + Story authoring (Action decomposition) | the planning stage (write operations happen after approval) |
| Autonomous mode | Action execution only | execution per the fixed plan |
| Delegation (delegate_to) | teammate assignment | designating who will do the Action's main work |

## 🚨 Context-loss recovery protocol

> **Must be performed** on returning after a conversation summary (token budget exceeded). Continuing the previous work from memory is prohibited.

1. **Determine the current Phase**: load `_epic.md` → confirm which Story's which Step is in progress
2. **Reload assets**: load the procedure doc for the current Phase (see the Phase-Asset binding table below)
3. **Verify state**: `ls .flow/workspace/epic-*/US-NNN-*/A-*.md` → confirm whether A-NNN.md exists
4. **Recheck _story.md**: confirm the current Story's `delegate_to` field and checklist status
5. **Decide the resume point**: based on the above checks, decide from which Step of which Phase to resume

---

## Phase-Asset binding

> On a Phase transition, **must** `Read`-load the corresponding Asset. This table itself is a Hard Gate.
> ⚠️ **Do not enter the next Phase if the Asset is not loaded**

Asset names are relative references to the `flow-*` skills under this plugin's `skills/`.

| Phase transition | Required Asset | Verification | If not loaded |
|-----------|-------------|------|----------|
| → `trigger-classify` (external-source entry — read an issue tracker/messenger/natural language and classify task type·scale) | `flow-trigger-classify` | classification result → routes to playbook-selection·scale-judgment | entry denied |
| → `initiative-planning` | `flow-procedure-initiative`, `flow-scale-judgment` | - | entry denied |
| → `initiative-setup` | `flow-procedure-initiative`, `flow-branch` | - | entry denied |
| → `epic-planning` | `flow-planning-epic` | - | entry denied |
| → `epic-setup` | `flow-procedure-epic`, `flow-branch` | - | entry denied |
| → `story-planning` | `flow-planning-story` | - | entry denied |
| → `story-setup` | `flow-procedure-story`, `flow-branch` | `ls A-*.md` (Hard Gate) | entry denied |
| → `action-planning` | `flow-planning-action` | - | entry denied |
| → `action-execute` | `A-NNN.md`, **the owner procedure doc** (if delegate_to is present) | `ls A-NNN.md` + confirm `delegate_to` field | entry denied |
| → `action-finish` | `flow-retrospective` (Level 1) | no commit if the retrospective is empty | entry denied |
| → `story-finish` | `flow-completion`, `flow-retrospective` (Level 2) | all Actions ✅ | entry denied |
| → `epic-finish` | `flow-completion`, `flow-retrospective` (Level 3), `flow-archive` | all Stories ✅ | entry denied |
| → `initiative-finish` | `flow-procedure-initiative`, `flow-retrospective` (Level 4), `flow-archive` | all Epics ✅ | entry denied |

**action-execute special condition**:
- If a `delegate_to` field is present: **must** `Read`-load that owner procedure doc
- e.g. `delegate_to: guide-domain-design` → loading that procedure doc is mandatory
- If not loaded, action-execute entry is denied

---

## Phase: Trigger (intake — external-source entry)

The classification stage that runs before Planning when a work item comes in from an **external source** (issue-tracker ticket / messenger thread / natural language). When the task type·scale are already fixed on entry (like keyword entry, "create an epic"), it can be skipped.

1. `Read` → `flow-trigger-classify`
2. Read the source → classify the task type (structured = mapping table / unstructured = inference, confirm with the user when ambiguous) + extract the scale hint
3. Routing: task type → `flow-playbook-selection` / scale hint → `flow-scale-judgment` → enter the Planning Phase

## Phase: Planning

The prerequisite stage for all setup/execute Phases. Load and follow the per-Level Planning procedure doc. (Agent Teams Plan Mode)

### epic-planning

1. `Read` → `flow-planning-epic`
2. Discovery: workspace/source research → current-state analysis
3. **[Assumption Gate]**: share the discovery summary (current state/assumptions/unclear) → receive user corrections
4. Alignment: ask about goal/scope/constraints/priority/completion criteria
5. Draft: create `_epic.md` + `_story.md` in `[DRAFT]` state
6. **[AI Review]**: self-review against the Epic checklist → fix the Draft → "self-review complete, N items" message
7. Refinement: user feedback → revise the DRAFT (up to 3 times)
8. **🚦 Checkpoint**: "Please review the plan draft. Shall we finalize?"
9. Finalize: on approval, remove the `[DRAFT]` marker → transition to `epic-setup`

### story-planning

1. `Read` → `flow-planning-story`
2. Discovery: analyze related sources/tests
3. **[Assumption Gate]**: share the discovery summary (current state/assumptions/unclear) → receive user corrections
4. Alignment: AC negotiation + implementation direction + test-strategy questions
5. Draft: update `_story.md` + Action decomposition `[DRAFT]`
6. **[AI Review]**: self-review against the Story checklist → fix the Draft → "self-review complete, N items" message
7. Refinement: user feedback → revise (up to 2 times)
8. **🚦 Checkpoint**: "Please review the Action decomposition. Shall we finalize?"
9. Finalize: on approval, remove the `[DRAFT]` marker → transition to `story-setup`

### action-planning

1. `Read` → `flow-planning-action`
2. Discovery: analyze the target files/existing patterns
3. Alignment: an implementation-approach confirmation question (1)
4. **🚦 Checkpoint**: "Shall we proceed with this approach?"
5. Finalize: on approval → transition to `action-execute`

---

## Phase: Epic

### epic-setup

> ⚠️ Prerequisite: `epic-planning` must be complete (DRAFT finalized state)

1. `Read` → `flow-procedure-epic`
2. `Read` → `flow-branch`
3. Per the procedure: create the Epic branch → commit the finalized `_epic.md`/`_story.md`
4. **🚦 Checkpoint**: "Epic creation complete. Shall we start the first Story?"

### epic-finish (🚨 order compliance mandatory)

1. Confirm all Stories ✅
2. `Read` → `flow-completion` confirm the Epic finish checklist
3. Write the `_epic.md` result/retrospective sections (retrospective format: `Read` → `flow-retrospective` Level 3)
4. `Read` → `flow-retrospective` → perform the Part 2: interactive 3-stage collection procedure
5. `Read` → `flow-archive` → perform the interactive 2-stage confirmation procedure
6. Create the PR: load the `flow-pr` skill
7. **🚦 Checkpoint**: user confirmation before each stage (retrospective/archiving/PR)

---

## Phase: Story

### story-setup

> ⚠️ Prerequisite: `story-planning` must be complete (Action decomposition finalized state)

1. **🔍 Early delegation-environment diagnosis**:
   - Confirm whether teammate assignment (delegation) is possible
   - When delegation is not possible:
     ```
     ⚠️  Teammate assignment (delegation) is not possible in this environment.
     On Action execution, if a delegate_to field exists use 'delegate to that owner procedure doc',
     otherwise Flow performs it directly.
     ```
2. `Read` → `flow-procedure-story`
3. `Read` → `flow-branch`
4. Create the Story branch (procedure: `flow-branch`)
5. **🚨 Create A-NNN.md** (Hard Gate — absolutely no skipping):
   Create a file for each Action in the `_story.md` Action decomposition table. **Include all required fields**:
   ```markdown
   **Story**: US-NNN-name
   **Action**: A-NNN
   **delegate_to**: [owner procedure doc name — lowercase-kebab]     ← required for delegation-needed Actions
   **reference procedure**: `[skill-name]`
   **target**: `[target path]`
   **AC mapping**: AC-1, AC-2
   **status**: ⬜

   ## Goal
   [concrete 1-2 sentences]

   ## Completion criteria
   | Criterion | Condition/environment | Verification method | Status |
   |------|----------|----------|------|
   | [criterion] | [e.g. runtime environment / input condition] | [test/manual check] | ⬜ |
   <!-- The "condition/environment" column is required (defends against omitted conditional AC).
        Even when no condition is needed, write "-" to leave an explicit review trace. -->


   ## Expected outputs
   - `[target path]`

   ## Step 1: setup
   ## Step 2: implementation
   ## Step 3: finish
   ## Result
   ## Retrospective
   ```
   > 🚨 Completion criteria and expected outputs are finalized before implementation. No TBD.
6. **🚨 Action-file creation verification** (Hard Gate): with `ls .flow/workspace/epic-*/US-NNN-*/A-*.md`, confirm every Action file actually exists → **if any is missing, deny action-execute entry**
7. Update the `_epic.md` Story status ⬜ → 🔄
8. **🚨 delegate_to advance confirmation**: check the `delegate_to` field of every Action in the created A-NNN.md or _story.md and print the list:
   ```
   📋 Per-Action owner mapping:
   - A-001: delegate_to → {owner procedure doc name} (delegation needed)
   - A-002: delegate_to → none (Flow executes directly)
   ```
   → share this list with the user and proceed after confirmation
9. Start executing the first Action
10. **🚦 Checkpoint**: after the first Action completes, "Shall we proceed with the next Action?"

### story-finish (🚨 order compliance mandatory)

**Mode detection**: judge standalone/Epic mode by whether the Epic folder exists

```bash
# Epic-mode condition: .flow/workspace/epic-[name]/ exists
# Standalone-mode condition: .flow/workspace/story-[name]/ exists (no Epic folder)
```

#### Common procedure (1-5)

1. Confirm all Actions ✅
2. Verify AC satisfaction: run each "verification method" in the `_story.md` AC table
3. `Read` → `flow-completion` confirm the Story finish checklist
4. Organize `_story.md` outputs (expected vs actual + Scope Out)
5. Write the `_story.md` retrospective (format: `Read` → `flow-retrospective` Level 2)
   - 🚨 **Hard Gate**: verify that a `## Retrospective` section exists in `_story.md`. If absent, do not proceed with commit/merge.

#### Story standalone mode (6-9)

6. **Archiving**:
   - Organize the main outputs (if migration to a permanent location is needed)
   - Simpler than Epic archiving (interactive confirmation mandatory)
7. **Create the PR**: load the `flow-pr` skill
8. (optional) Delete the Story branch: `git branch -d story/[name]`
9. **🚦 Checkpoint**: "Story standalone mode complete."

#### Epic-based mode (6-9)

6. `_epic.md` corresponding Story Step → ✅
7. **🚨 Upper-integration Hard Gate**:
   - **Criteria SSOT = `flow-completion` § Upper-integration Hard Gate** (including the sub/single-branch mode branching — no re-statement). Execution method (Squash)·commands = `flow-branch`.
   - Sub-branch mode: after running Squash Merge, confirm the integration commit with `git log <base>..HEAD` / single-branch mode: integration = not applicable (the [single] check in completion)
   - If not executed (sub) or not confirmed: **do not** start the next Story
8. **Confirmation output**: "Upper integration confirmed. OK to proceed to the next Story." (single mode: "integration = n/a, tag boundary confirmed")
9. **🚦 Checkpoint**: "Story complete. Shall we start the next Story?"

---

## Phase: Action

### action-setup (only when adding a new Action)

Most Action files are already created in story-setup.
Only when a new Action needs to be added mid-Story:
1. `Read` → `flow-procedure-action`
2. Per the procedure, create `A-NNN.md`

### action-execute

> ⚠️ Prerequisite: `action-planning` must be complete (approach-confirmed state)

0. **🚨 A-NNN.md existence verification** (Hard Gate): with `ls`, etc., confirm the Action file actually exists → **if the file is missing, do action-setup first; deny execution entry**

0.5. **🚨 Pre-flight Check** (Hard Gate):
   - **Before starting implementation**, always run the following verification:
     ```bash
     # 1. Confirm the target path exists (when not a new creation)
     ls [the path in A-NNN.md's "target" field]

     # 2. Confirm the existing verification baseline passes
     [project standard test/verification command]

     # 3. Understand the change-impact scope in advance (for modification work)
     grep -rn "[target identifier]" [related directory]
     ```
   - Failure conditions (entry denied):
     - path missing → correct A-NNN.md's "target" field then re-enter
     - baseline verification failed → resolve the existing code problem first
     - impact scope not understood → run grep then enter
   - Exception: an Action with only new file creation and no impact scope

1. Load `A-NNN.md` → confirm the `delegate_to` field and the reference-procedure field
2. **🔍 Delegation-protocol auto-check**:
   - **When the `delegate_to` field is present**:
     ```
     ⚠️  This Action needs delegation to [{owner procedure doc name}] (teammate assignment).
     Please confirm whether delegation is possible and proceed.
     ```
     → **proceed after user confirmation** (no auto-proceed)
   - **When the `delegate_to` field is absent**: proceed with procedure-based execution
3. **🔍 Test-first check** — when modifying a shared module:
   - When the target is a shared module referenced in multiple places:
     ```bash
     # 1. Confirm impact (reference locations)
     grep -rn "target identifier" [related directory]

     # 2. Confirm test files
     ls [test directory]

     # 3. If tests need modifying, reflect it immediately
     ```

3.5. **🚨 grep full-sweep confirmation** (Hard Gate):
   - For **renaming/deletion/signature-change** work, **must** run the following:
     ```bash
     # Full impact-scope confirmation (must include both source and tests)
     grep -rn "[old name]" [related directory]
     ```
   - Fix every printed location together (omission causes a build error/test fail in the next commit)
   - Applies to: variable/field/method/class name changes, signature changes, file move/deletion
4. **🚨 Template-link check** (Hard Gate):
   - There is a template link (`assets/*-template.md`) in the Action doc or procedure doc → **must `Read`-load the template before proceeding**
   - Block execution if the template is not loaded: guide "You must load the template first"
5. **Delegation decision** (priority):
   - **`delegate_to` present** → **owner procedure doc delegation guide** (procedure below)
   - **`delegate_to` absent + reference procedure present** → **Flow loads and runs the procedure** (SKILL.md `Read` → perform the procedure)
   - **`delegate_to` absent + reference procedure absent** → **Flow executes directly** (perform per the A-NNN.md Steps)
6. **🚦 Checkpoint**: "Shall we commit after verification?"

#### Delegation procedure (teammate assignment)

> 📋 Detailed protocol: `Read` → `handoff-protocol` + plugin `rules/`

When the owner is decided by `delegate_to` or auto-matching:

1. Print the **transition guide message** (🎯 prominently emphasized):
   ```
   🔄 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ⚠️  **Delegation needed (teammate assignment)**
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   This Action runs on **`{owner}`**.

   📋 **Action info**:
   - **title**: {A-NNN.md title}
   - **owner**: `{owner procedure doc name}`
   - **target**: `{target path}`

   👉 **Next steps**:
   1. Delegate the work to `{owner}` (teammate assignment)
   2. The owner does the work
   3. Return to Flow after completion

   ✅ Flow handles verification+commit after the return.
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```
2. Delegate to the owner → the owner implements
3. Owner work complete → return to Flow
4. **Post-processing after return**: proceed to `action-finish` (verify → commit → status update)

#### Auto-matching table

When `delegate_to` is absent, auto-match by owner name: see the per-situation priority matching table in the plugin `rules/`.

### action-finish (🚨 order compliance mandatory)

> ⚠️ On completing each Step during action-execute, immediately update the corresponding `- [ ]` in `A-NNN.md` to `- [x]`.
> Do not batch-check them at the finish stage.

1. **🔍 Pre-flight Check** — required before commit:
   ```bash
   # Run the project standard static analysis/verification (errors only)
   [project standard analysis command]

   # Errors present → fix then retry
   # No errors → proceed to the next step
   ```
2. **Verification 3 stages**:
   - Run the "verification method" in the `A-NNN.md` completion-criteria table → result ⬜→✅
   - Confirm static analysis passes (done above)
   - Run tests (on code change)
3. Confirm all Steps in `A-NNN.md` are already ✅ (since they were updated immediately during execution)
3.5. **🚨 Output-match verification** (Hard Gate):
   ```bash
   # 1. Extract A-NNN.md "expected outputs"
   # 2. Compare against actual changed files
   git diff --name-only HEAD
   ```
   - Confirm whether **expected outputs ⊆ actual changed files**
   - Handling mismatch types:
     - **A file expected but not touched** → report to the user ("expected but actually unnecessary")
     - **A file not expected but changed** → record in the retrospective's Problem ("scope expansion" reason stated)
   - On violation: cannot learn the Action-count over-setting/omission pattern
4. **🤖 AI code review** (on code-file change):
   - Confirm the changed-file list with `git diff --name-only HEAD`
   - Perform self-review on the changed files:
     - general bugs/logic errors
     - project architecture-rule violations (per that project's rules/)
     - report only High-priority issues
   - High severity → fix then re-verify / Low severity → record in the retrospective's Problem / no issues → proceed
5. Process the `A-NNN.md` Action retrospective (settings-aware): if `.flow/settings.json` `retrospective.levels.action.rigor=none`, skip the mandatory retrospective requirement/R3 and record only a settings note. For any other label, write the retrospective per the `flow-retrospective` Level 1 criteria — **no commit if the required retrospective is empty**
6. `_story.md` corresponding Action Step → ✅
7. Commit: `[epic][story][action] work content`
8. **🚦 Checkpoint**: "Action complete. Shall we proceed with the next Action?"

---

## Phase: Retrospective & Archive

### retrospective

1. `Read` → `flow-retrospective`
2. Perform the interactive 3-stage confirmation procedure (Part 2: collect+analyze / identify+reflect / complete+archive)

### archive

1. `Read` → `flow-archive`
2. Perform the interactive 2-stage confirmation procedure (archive: analyze+migrate / final-confirm+cleanup)
</content>
