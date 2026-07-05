---
name: flow-procedure-epic
description: "Epic execution procedure. References Epic task-list initialization + _epic.md folder/structure + required sections + Story-breakdown table + branch-base decision."
user-invocable: false
metadata:
  type: procedure
  version: v1.2.0
---

# Epic creation procedure

The detailed procedure the flow manager loads in the `epic-setup` Phase.

## Agent Teams mapping (summary)

This procedure runs on top of Agent Teams. Epic-related concept mapping:

| flow concept | Agent Teams mapping |
|---|---|
| work item (Epic/Story/Action) · status (⬜/🔄/✅) · dependency | shared task list |
| Epic/Story folder creation | task list initialization |
| _epic.md status field | task status SSOT |
| delegation (delegate_to) | teammate assignment (main spawns) |
| plan approval (user confirmation) | plan approval (main↔user, Plan Mode) |

> Full mapping-table SSOT: `flow` skill § Agent Teams mapping model.

## Scope (gray-area explicit)

| gray-area case | Primary | Secondary |
|---------------|---------|-----------|
| Epic wrap-up as a whole (PR/branch/retrospective integration) | **flow-procedure-epic** | `flow-archive` (migration step only) |
| Epic archiving (temp→permanent migration) | `flow-archive` | **flow-procedure-epic** (confirm the wrap-up flow) |

**Core Beliefs**:
- **Epic = a bundle of 2 or more Stories** — if there is 1 Story it is not an Epic but a standalone Story mode (`flow-scale-judgment` upper-container necessary condition). An empty-shell Epic ("Epic — 1 Story") is forbidden (symmetric with `procedure-initiative` "1 Epic → Initiative not needed")
- Strict Epic folder structure: `.flow/workspace/epic-[name]/_epic.md` + `US-NNN-[name]/`
- _epic.md required sections: Goal / Scope / Non-goals / Constraints / Story breakdown / Completion criteria / Dependencies + **the `**playbook**` field (work type — no-work-without-playbook hook-enforced)**
- Branch base explicit (if a branch other than the default, record the base in the _epic.md `**Branch**:` line)
- Enter epic-setup only after Epic Planning is complete (confirm the DRAFT marker is removed)

**Anti-patterns**:
- **Wrapping 1 Story into an Epic** (empty-shell container — should be demoted to a standalone Story)
- Missing part of the _epic.md required sections
- Missing the branch-base decision logic (assuming the default branch)
- Entering setup with the DRAFT marker not removed
- Missing the priority/persona/target columns in the Story-breakdown table
- Encroaching on `flow-archive`'s responsibility (duplicating migration detail in this skill)

**Decision Heuristics**:
- Epic Planning DRAFT marker → confirm removal → enter setup
- base branch = other than the default → make it explicit in _epic.md
- Story breakdown ≥ 3 → build the dependency graph (visualize the precedence relations)
- Non-goals explicit → agree on splitting into a follow-up Epic

**Output Quality Bar**:
- All 7 required _epic.md sections written
- Branch notated `**Branch**: epic/[name] (base: [base])`
- Story-breakdown table: ID/title/persona/target/priority
- Completion criteria measurable (grep/ls command)
- Dependency graph (Story ≥ 3)

**Sanity Self-Questions**:
- "Are all required _epic.md sections written?"
- "Is the branch base other than the default, and if so did I make it explicit?"
- "Did I confirm the DRAFT marker was removed?"
- "Did the Story-breakdown table follow the standard columns?"
- "Did I avoid duplicating the archiving procedure in this skill (`flow-archive`'s responsibility)?"

> ⚠️ **Prerequisite required**: `epic-planning` complete (DRAFT-finalized state in the Planning Phase)
> For the Planning procedure, see the `flow-planning-epic` skill.

## Prerequisites

- `epic-planning` complete: the `_epic.md` + `_story.md` DRAFT is finalized by user approval
- Files exist with the `[DRAFT]` marker removed

## Procedure

### Step 1: Confirm the current branch

Confirm the current branch per the project's branch-strategy guide. The branch hierarchy must be parity with the task-list hierarchy (Epic/Story/Action).

**Branch**:
- current Epic branch → ask "You are on the current Epic branch. Create a new Epic branch?"
- otherwise → proceed to Step 2

### Step 2: Create the Epic branch

If the user does not specify a base branch, create it from the **current branch**. Branch creation/naming/base decision follows the project's branch-strategy guide (playbook-supplied). Put the Epic branch as a unit parity with the Epic task-list hierarchy.

### Step 3: Create the Epic folder and _epic.md

```
.flow/workspace/
└── epic-[name]/
    └── _epic.md
```

**_epic.md required sections**:

```markdown
# Epic: [title]

**ultimate purpose**: [if under an Initiative, restate the upper value proposition / if a standalone Epic (Epic-scale entry), this Epic's goal is the ultimate purpose = the top]
<!-- The entry scale sets the top. If an upper _initiative.md exists, inherit its ultimate purpose; if not, this Epic is the tree top. Do not fabricate a nonexistent parent. -->
**Status**: ⬜
<!-- epic-level completion marker (own status). The hook's self_status judges completion from this header field only — not contaminated by lower Step ✅. Changed to ✅ in epic-finish. -->
**Branch**: `epic/[name]` (base: [base])
**Branch mode**: sub | single  <!-- default sub (epic/ · story/ branching). If everything is meta · small · single-domain, use single (commits tagged [epic-N][US-N][A-N] on this single branch). flow-branch §single-branch mode. If single, Story→Epic Squash and Epic→Initiative merge = not applicable. If under an Initiative, inherit the _initiative.md mode -->
**Start date**: [YYYY-MM-DD]
**playbook**: [work-type method name — select and record via `flow-playbook-selection` (e.g. feature / refactor / bug / docs / retro-processing). Mandatory — if unrecorded, the execution-stage hook blocks (no-work-without-playbook)]

## Goal
[This Epic's final goal in 2-3 sentences]

## Discovery Notes
> Summary of current-state research gathered in the Planning Phase
- [research result 1]
- [research result 2]

## Scope
### Included
- [included item]
### Excluded
- [excluded item]

## Constraints
| Type | Constraint | Impact | Mitigation |
|------|----------|------|----------|
| (if applicable) | | | |

## Step 1: Setup
**Skill**: `flow`
**Status**: ⬜
- [ ] Define goal/scope
- [ ] Write the Story outline
- [ ] Initial commit

## Step 2: US-001-[name]
**Status**: ⬜
**Branch**: `story/[epic-name]/US-001-[name]`
**Title**: [Story title]
- [ ] Check out the branch
- [ ] Proceed with the Story flow → [_story.md](US-001-[name]/_story.md)
- [ ] Confirm Story integration complete (criterion = `flow-completion` § upper-integration Hard Gate — sub = Squash commit / single = not applicable · tag boundary)

<!-- Repeat the format above when adding a Step -->

## Step N: Wrap-up
**Status**: ⬜
### Wrap-up procedure (5 steps)
1. **Verify**: confirm all Stories ✅
   - [ ] All Story Steps in _epic.md are ✅
   - [ ] **Change the epic header `**Status**: ⬜/🔄` → `✅`** (epic-level completion marker — the hook self_status judges completion from this field)
   - [ ] Project verification command (playbook-supplied) passes (if code changed)
2. **Commit**: commit uncommitted changes
3. **Retrospective**: write the retrospective section below (🚨 do not leave empty)
   > Retrospective = evaluating whether the AI followed the procedure. Not evaluating code quality/planning ❌
   - [ ] Keep (what worked well during the procedure — skill triggering, checkpoint adherence, etc.)
   - [ ] Problem (procedure the AI missed — missed retrospective, skipped branch, etc.)
   - [ ] Try (procedure-improvement insight — template/rule change proposal)
4. **Archiving**: migrate the retrospective to the permanent store
   - [ ] Create `archives/retro-[name].md` (flat, no folder — 1 per entry-scale unit, `flow-archive`. If a **standalone Epic**, `retro-epic-[name].md`; an Epic under an Initiative is not separate — consolidated in initiative-finish)
   - [ ] Commit: `chore: archive epic-[name] retrospective retro.md`
5. **PR creation**: flow-pr skill (with tags)
   - [ ] Load flow-pr SKILL.md with `Read`
   - [ ] Create the PR per the skill procedure

## Result (write on completion)
## Retrospective
> Retrospective = evaluating AI procedure adherence. Not evaluating code quality/planning ❌
### Keep
### Problem
### Try
```

### Step 4: Create the Story folders and _story.md

For each Story, create the folder and the `_story.md` file:

```
.flow/workspace/epic-[name]/
├── _epic.md
├── US-001-[name]/
│   └── _story.md
├── US-002-[name]/
│   └── _story.md
└── ...
```

**_story.md required sections**:

```markdown
# Story: [title]

**Epic**: [epic-name]
**Story**: [US-NNN-name]
**Branch**: `story/[epic-name]/[ID]-[name]`
**Status**: ⬜
<!-- story-level completion marker (own status) — self_status looks at this header field only -->

## User story
> As a [role],
> I want [feature],
> So that [value].

## Acceptance Criteria
| ID | Condition (Given/When/Then) | Verification method | Owning Action |
|----|------------------------|----------|------------|
| AC-1 | Given... When... Then... | [verification method] | A-NNN |

## Step 1: Setup
- [ ] Create the story/ branch (🚨 do not skip)
- [ ] Create all A-NNN.md files (🚨 do not skip)

## Step 2~N-1: Action Steps

## Step N: Wrap-up
- [ ] Confirm all A-NNN.md ✅
- [ ] Run the AC verification methods → [x] on pass
- [ ] Organize deliverables (expected vs actual comparison)
- [ ] Write the retrospective (🚨 do not leave empty — write only the AI-procedure-adherence evaluation)
- [ ] The corresponding Story in _epic.md → ✅
- [ ] Story integration → epic/[name] (criterion = `flow-completion` § upper-integration Hard Gate — sub = Squash / single = not applicable)

## Deliverables (write on completion)
## Retrospective
> Retrospective = AI procedure-adherence evaluation. Not evaluating code quality/planning ❌
### Keep
### Problem
### Try
```

> ⚠️ Action files (A-NNN.md) are not created at this stage. Create them when the Story starts.

### Step 5: Initial commit

Record the Epic/Story documents as a task-list-initialization commit. The commit format and procedure follow the project's branch-strategy guide (playbook-supplied).

Example commit message: `feat: epic-[name] plan - create Epic + Story documents`

### Step 6: Completion report

```
✅ Epic '[name]' creation complete
- Branch: epic/[name]
- Epic document: .flow/workspace/epic-[name]/_epic.md
- Story documents: [N] created
  - US-001-[name]: [title]
  - US-002-[name]: [title]

📝 Run the first Story with "let's start the story"
```

## Deliverables

| Item | Path |
|------|------|
| Epic branch | `epic/[name]` |
| Epic document | `.flow/workspace/epic-[name]/_epic.md` |
| Story documents | `.flow/workspace/epic-[name]/US-NNN-[name]/_story.md` |
