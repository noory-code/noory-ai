---
name: flow-issue-handling
description: "Procedure for classifying and handling problems found during work. Blocker definition + classification decision table (blocker × scope × non-goal) + 4 handling paths (immediate fix / side commit / retrospective record / user handoff) + Epic non-goal conflict handling + teammate boundary reference."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.1
---

# Procedure for handling problems found during work

The classification and handling procedure when an unintended problem is found during work (hook block, permission denial, external tool bug, procedure gap, broken SSOT consistency, etc.).

> **Core rule**: The plugin rules' `no-defer-blockers` is the SSOT of this procedure. No handing off a blocker.

## Agent Teams mapping

The decisions in this procedure map to Agent Teams components as follows.

| This procedure's concept | Agent Teams mapping |
|---|---|
| Return to main + user decision on finding a blocker | plan approval (main↔user) / mailbox report |
| Handling-path classification (blocker × scope × non-goal) | planner (Flow Manager) decision |
| Handling a teammate boundary intrusion | teammate delegation boundary (block work outside the assigned scope) |

## Scope (gray-zone clarification)

| Gray-zone case | Primary | Secondary |
|---------------|---------|-----------|
| Classify a found problem + decide the handling path | **flow-issue-handling** | `flow-must-not` (check prohibition rules) |
| Retrospective record (write Problem/Try) | retrospective procedure | **flow-issue-handling** (hand off the classification result) |
| User explicit handoff trigger (checkpoint) | `flow` skill (User Checkpoints) | **flow-issue-handling** (state the handoff reason) |

**Anti-patterns**:
- Ad-hoc handling without classification (fixing a hook defect immediately / handing off another defect — inconsistent)
- Handling a blocker with only a retrospective record (the same defect recurs after the next Story starts)
- Violating an Epic non-goal without explicit user agreement
- Just bundling a side commit into the main Action commit (hard to trace)
- Trying to handle an external tool bug as this Action's responsibility (waste of time)
- Interpreting a simple user affirmation ("yes"/"OK") as agreement to bypass an Epic non-goal

**Decision Heuristics**:
- Blocks progress of this Action/Story → **blocker** (hook deny, permission denial, missing dependency)
- Undermines the evaluation quality of a subsequent Action/Story → **blocker** (missing required tool, broken SSOT)
- Try High + a precondition for a subsequent Story → **blocker**
- This work can proceed + subsequent impact is negligible → **non-blocker** (handoff allowed)
- External policy/tool/non-goal conflict → **user explicit handoff** obligation
- Fixable immediately within this Action's scope → **immediate fix** (main commit + retrospective Problem)
- Change outside this Action + separable from the work flow → **side commit** (`[side][scope] content`)

**Output Quality Bar**:
- Output the classification-table result in 1 line (blocker/scope/non-goal + handling path)
- Follow the side-commit message format `[side][scope] content`
- On user explicit handoff, present an options table (handle now / separate Story / hand off)
- Record the finding + handling in ≥1 line in the retrospective § Problem
- On an Epic non-goal conflict, add "exception agreement (date, reason)" to the non-goal section of `_epic.md`

**Sanity Self-Questions**:
- "Did I apply the classification decision table immediately on finding it, rather than judging ad hoc?"
- "Am I trying to hand off a blocker with only a retrospective record? (`no-defer-blockers` violation)"
- "On an Epic non-goal conflict, did I get explicit user agreement?"
- "Did I follow the side-commit message format `[side][scope]`?"
- "On an external policy/tool block, am I not trying to handle it as this Action's responsibility?"
- "Did I not misinterpret a simple user affirmation as non-goal agreement?"

## Classification decision table

3-axis classification (blocker × scope × non-goal) → handling-path mapping:

| Blocker? | Within this Action's scope? | Epic non-goal conflict? | Handling path |
|:---:|:---:|:---:|--------|
| ✅ | ✅ | ❌ | **Immediate fix** (main commit + retrospective Problem) |
| ✅ | ✅ | ✅ | **User explicit handoff (non-goal agreement)** → immediate fix after agreement |
| ✅ | ❌ | ❌ | **Side commit** (separate commit + same branch as this Action's commit) |
| ✅ | ❌ | ✅ | **User explicit handoff (non-goal agreement)** → after agreement, side commit or split into a separate Story |
| ❌ | (any) | (any) | **Retrospective record + handoff** (Try item, handled at Epic wrap-up) |
| (external policy/tool block) | — | — | **User explicit handoff** (external handling — add permission, file an issue tracker report, etc.) |
| (teammate boundary violation) | — | — | Apply **§2.5 teammate boundary**, then the 5-step handling path (detect → classify → return to main → main classifies → handle) |

## §2.5 teammate boundary

Handles situations where a teammate finds, or tries to directly perform, work outside its assigned scope.

> **Teammate definition handoff**: A teammate's (expert's) **concrete name · responsibility · assigned scope** is defined by the project (in .claude/agents/). This procedure only specifies "how to classify/handle work outside the assigned scope" and does not cover "who is responsible for what".

### §2.5.1 Boundary violation definition

**A situation where a teammate finds work outside its own assigned scope**. Examples:
- A role teammate, while working, develops the urge to produce another role's output
- A teammate, while performing this task, recognizes a new work type (another role's responsibility)
- A teammate tries to directly perform the flow-management (planning · state · verification · retrospective) area

### §2.5.2 Distinguishing a boundary violation vs a normal collaboration request

| Signal | Boundary violation (block) | Collaboration request (normal) |
|------|------------------|---------------------|
| Handling method | Fixes it directly itself (direct handling outside the assigned scope) | Info/review among active team members is a direct peer-to-peer request / if a new teammate is needed, request a spawn from main |
| Permission | Fixes only within the caller's assigned scope (no external) | A teammate cannot spawn another teammate — spawn/assignment is main's; info/review collaboration is direct |
| Handling | **Block + return to main** | **Peer-to-peer mailbox or a spawn request to main** (normal) |

### §2.5.3 Boundary classification (new axis)

Add **1 new axis** = "boundary violation" to the existing classification decision table (3 axes: blocker × scope × non-goal):

| Boundary classification | Handling path |
|----------------|-----------|
| Not a violation (collaboration request possible) | Request info/review directly from an active team member. If a new teammate is needed, request a spawn from main — end of procedure |
| Violation — urge for another stage of this role | Return to the caller (main) + decide the branch to the appropriate stage |
| Violation — another role's responsibility area | Return to main + assign the appropriate teammate (close the Story / split into a subsequent Story / Epic non-goal decision) |
| Violation — flow-management (planning · state · verification · retrospective) area | Return to main + the Flow Manager handles it directly |

### §2.5.4 Handling path (5 steps)

1. **Detect** — teammate self-check ("Is this work within my assigned scope?")
   - Example self-question: "Is this work within my role's process flow, or another teammate's area?"
2. **Classify** — apply the new-axis decision table of §2.5.3
   - Not a violation (collaboration request) → direct peer-to-peer request among active team members, or a spawn request to main if a new teammate is needed (end of procedure)
   - Violation — pick 1 of the violation classification categories
3. **Return to main** — report to the caller (main)
   - Report format: "Boundary violation detected — [work content] is [appropriate role]'s responsibility area. Recommend main assignment."
4. **Main classifies** — main applies this classification decision table (3 axes + this new boundary axis)
   - Is it a blocker for this Action/Story? / Within this Action's scope? / Epic non-goal conflict?
5. **Handle** — apply 1 of the 4 handling paths in §3
   - Immediate fix / side commit / retrospective record + handoff / user explicit handoff

### §2.5.5 Violation cases (examples — to accumulate over time)

Accumulate the boundary-violation cases discovered after this SSOT settles in this section:

| Violation case | Violating teammate | Appropriate teammate | Classification | Handling |
|----------|--------------|--------------|------|------|
| (real-call cases to be accumulated) | — | — | — | — |

## The 4 handling paths in detail

### 1. Immediate fix (blocker + within this Action's scope + no non-goal conflict)

**Condition**: Directly blocks this Action's progress and is solvable within this Action's output scope.

**Procedure**:
1. Stop work immediately on finding it → state the defect precisely (hook message, block reason, error message)
2. Write the fix code/doc → include it in the same commit as the main output
3. Record "defect + fix content" in 1 line in the retrospective § Problem
4. State the side output in the commit message (e.g. "side output: defect fix")

### 2. Side commit (blocker + outside this Action's scope + no non-goal conflict)

**Condition**: A defect in an area outside this Action but separable in the work flow.

**Procedure**:
1. Pause the main Action work → fix the defect in a separate commit
2. Commit message format: `[side][scope] content`
   - `[scope]`: the module/directory where the defect is located, etc.
3. Accumulate on the same branch as this Action's commit
4. Record the side-commit hash + content in the retrospective § Problem

### 3. Retrospective record + handoff (non-blocker)

**Condition**: This work can proceed + subsequent impact is negligible. SSOT consistency, integration improvements, etc.

**Procedure**:
1. Add an item to the retrospective § Try (priority / item / target / content / apply timing)
2. Review in bulk via the retrospective procedure at Epic wrap-up
3. After a handling decision, hand off to a separate Action or a subsequent Epic

### 4. User explicit handoff (external policy/tool or Epic non-goal conflict)

**Condition**: Not solvable by the AI's own judgment — external policy (config permission, IDE classifier), external tool (SDK bug, etc.), Epic non-goal violation.

**Procedure**:
1. Stop work → report the classification to the user (blocker reason + reason external handling is needed)
2. Present the user decision options:
   - Handle now (config change, issue-tracker report, etc. — user action)
   - Create a separate Story (after Epic non-goal agreement)
   - Hand off (demote to non-blocker — user explicit decision)
3. Record the decision result in this Action's retrospective + the `_epic.md` non-goal section (if applicable)

**Epic non-goal conflict agreement flow**:
1. AI: "This defect conflicts with Epic non-goal 'X'. Defect classification: [blocker/non-blocker]. Handling options: [...]. Which way should we go?"
2. User explicit decision (a simple affirmative "yes" must not be interpreted as agreement — an explicit option choice is required)
3. After the decision, add "exception agreement (date, reason)" to the `_epic.md` non-goal section

## Hard Gate

- [ ] Applied the classification decision table on finding a blocker (no ad-hoc handling)
- [ ] Got explicit user agreement on an Epic non-goal conflict
- [ ] Followed the side-commit message format `[side][scope] content`
- [ ] Recorded the finding + handling in ≥1 line in the retrospective § Problem
- [ ] Got user explicit handoff on an external policy/tool block

## Verification

```bash
# Find side commits in this Action's commit log
git log --oneline | grep -E "^\[side\]"

# Trace found items in the retrospective
grep -rE "side output|defect fix" <retrospective task path>
```

## Related SSOT

- Plugin rules `no-defer-blockers` (no handing off a blocker — the higher-level rule of this procedure)
- `handoff-protocol` §3 (delegation call flow + boundary-intrusion fallback)
- `flow-must-not` (situation-specific prohibitions)
- Project `.claude/agents/` (the concrete teammate definitions — name · responsibility · assigned scope)
