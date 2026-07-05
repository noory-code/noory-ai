---
name: flow-planning-epic
description: "Epic Planning procedure. Referenced when drafting an Epic plan, agreeing on scope, decomposing Story outlines, and running the R1 review. The epic-planning Phase's 7 stages: Discovery→Assumption Gate→Alignment→Draft→R1→Finalize."
user-invocable: false
metadata:
  type: procedure
  version: v1.1.0
---

# Epic Planning procedure

A procedure the flow manager loads when drafting an Epic plan. It runs inside Plan Mode as human-AI collaboration.

> **Principle**: "No execution without a plan". After completing the Discovery→[Assumption Gate]→Alignment→Draft→[AI Review]→Refinement→Finalize cycle in dialogue with the user, enter execution.

## Plan Mode boundary (settled design)

This procedure is performed inside **Plan Mode**. It aligns with the Agent Teams plan-approval (main↔user) boundary.

- **Plan Mode = scale judgment + Epic authoring (goal + Story outline) + Story authoring (Action decomposition)**. All of these are human-AI collaboration acts.
- **Autonomous execution = Action execution only**. The main assigns and orchestrates expert teammates per the playbook procedure. Planning acts (Epic/Story authoring) are performed only inside the Plan Mode + user-approval boundary.
- Flow: author Epic → ExitPlanMode → finalize the Epic file → on entering each Story, **go back into Plan Mode** to author the Story (Action decomposition).

## The 7-stage Planning cycle

```
Discovery → [Assumption Gate] → Alignment → Draft → [AI Review] → Refinement → Finalize
(research)  (state/correct assumptions) (question/agree) (draft) (quality review) (apply feedback) (finalize)
```

| Stage | Purpose | Main tools | Output |
|------|------|----------|--------|
| **Discovery** | Grasp the status, analyze code/structure | `Read`, `ls`, `Grep`, `Glob` | research notes (dialogue) |
| **[Assumption Gate]** | Share the discovery summary + state assumptions + user correction | — | agreed status understanding (dialogue) |
| **Alignment** | Confirm goal/scope/constraints, resolve ambiguity | `AskUserQuestion` | agreed requirements (dialogue) |
| **Draft** | Create the plan draft file | `Write` | a document file with the `[DRAFT]` marker |
| **[AI Review]** | Self-verify plan quality + fix immediately | — | reviewed DRAFT |
| **Refinement** | Apply user feedback, revise | `Edit` | revised DRAFT file |
| **Finalize** | After approval, remove `[DRAFT]`, commit | `Edit`, `Bash` | finalized document + commit |

> This entire cycle is performed inside Plan Mode, and Finalize's user approval is the plan approval.

---

## Timing & transition

**Timing**: on entering Epic plan drafting (the user requests Epic creation)
**After completion**: transition to Epic Setup (create branch + finalize-file commit) → ExitPlanMode

---

## Discovery (research)

1. **Explore the workspace directly** (main's responsibility — the Epic Planning Phase is centered on main + user dialogue):
   - The main directly explores `.flow/workspace/`, the target source paths, and the related test paths (`Grep`/`Glob`/`Read`)
   - Grasp the current code structure, existing patterns, dependencies, completed/unimplemented status
   - Result → used as the status/assumption items of the Assumption Gate
   > ⚠️ In the Epic Planning Phase, do not assign teammates such as an exploration agent. Expert teammates are brought in after Planning Finalize (`handoff-protocol` bring-in-timing principles (a)(b)).
2. **Analyze the workspace**: grasp `.flow/workspace/`, the source structure
3. **Analyze related code**: explore existing code with `Grep`/`Glob`
4. **Check existing docs**: explore related specs / documents
5. **Analyze domain boundaries**: review the domain overlap/split criteria across Stories; on multiple domains, propose a split
6. **Summarize research results**: share status/dependencies/risks with the user
7. **Status scan**: inspect doc quality and missing files. When thresholds are exceeded (missing>20%, Action>15), propose a separate Story/Epic split
8. **Scale judgment (Story vs Epic)**: see `flow-scale-judgment`. **§Ultimate-purpose interview first** (why / higher value — the primary scale signal + the source of the `_epic.md` ultimate-purpose field) → judge by duration (1-3 days vs 5+ days), task count (Action≤5 vs Story≥3), domain (single vs multiple), dependencies (simple vs complex), uncertainty, file count (3-5 vs 10+), then confirm with the user

> ⚠️ **When "make an epic" is stated explicitly**: skip the scale-judgment stage and go straight into Epic Planning

### AC "pre-check" marker

Epic ACs are classified in the Planning stage with the following markers:

| Marker | Meaning | Discovery handling |
|------|------|--------------|
| `(pre-check)` | Immediately verifiable via Discovery's grep / ls / Read — possibly already achieved | Run the verification command in the Discovery stage → if achieved, exclude from Action decomposition |
| `(external asset)` | Depends on an external asset the AI cannot ground-truth-inspect (external runtime / CI-CD / external policy, etc.) — cannot be settled at Epic time | **Settle after a user interview in Story Planning** (no AC assertion at Epic time — `verify-before-assert`) |
| (no marker) | Needs implementation/documentation in this Epic | normal Action decomposition |

**Applied example** (shrinking the Action count via pre-check):
```
| AC-1 | Domain layer extraction complete (interface + implementation) | auto-verify (pre-check) |
→ Discovery grep: implementation already exists → AC-1 pre-satisfied → shrink the Story's Action count
```

**Discovery activation**: on finding an AC `(pre-check)` marker, run the following in the Discovery stage:
- `grep -rn "{keyword}" {target path}` or the relevant area
- `ls {path}` existence check
- `Read {path}` content verification

→ On confirming pre-satisfaction: note "Discovery pre-satisfied — excluded from Action decomposition" next to the AC. After user confirmation, shrink the Action count.
→ On confirming non-satisfaction: proceed with normal Action decomposition.

> **Handling the `(external asset)` marker**: do not verify/settle it in Epic Planning. On entering Story Planning, confirm the external asset's actual state via a user interview, then settle/adjust the AC — writing an AC on top of external-asset assumptions leads to repeated large-scale shrinkage in Story Planning (`verify-before-assert` external asset = interview consistency).

---

## Assumption Declaration Gate (required after Discovery completes)

Summarize the Discovery result in 3-5 bullets, then present it to the user:

**Summary format**:
- **Status**: [the actual state found in the code/docs]
- **Assumption [N]**: [the interpretation/judgment the AI made] — if uncertain, state "(uncertain)"
- **Unclear**: [what cannot be known for sure, to confirm in Alignment]

**Example output**:
```
Sharing the Discovery result:
- Status: no .flow/workspace/epic-auth/, no target module (new implementation)
- Assumption 1: token-based authentication is used (the same pattern was found in other existing features)
- Assumption 2: only email/password is supported (no social-login-related code)
- Unclear: the session-retention-period policy (to confirm in Alignment)

Is the above correct? Let me know if anything needs correcting/supplementing.
```

→ After receiving the user's corrections, enter Alignment
→ "Correct" / "OK" / "No issues" are also valid (when all assumptions are correct)
→ Corrections are applied before the Alignment questions

---

## Alignment (question/agree)

> ⚠️ **Apply the `purpose-anchoring` gate before composing questions**: check whether each question is already derivable from the ultimate purpose + the sub-SSOT. If it is derivable, don't ask — proceed with that answer (report in 1 line). Include only what is not derivable in the questions below.

Ask the core questions with the `AskUserQuestion` tool:

**Required questions** (5):
1. **Goal**: "What is the final goal of this Epic? What problem does it solve?"
2. **Scope**: "Please split what is included from what is excluded"
3. **Constraints**: "Are there deadlines, technical constraints, or compatibility requirements?"
4. **Priority**: "Is there a priority among the Stories? What should be done first?"
5. **Done criteria**: "When this Epic is finished, what state should it be in?"

**Situational additional questions** (up to 3):
- When an external dependency is found: "I found a dependency on X. How should we handle it?"
- When there is a possible conflict with existing code: "This may conflict with existing Y. Replace? Coexist?"
- When the scope is large: "How about splitting the Epic? A Epic + B Epic"

---

## Draft (draft authoring)

### 0. **Create the folder structure** (required)

```bash
mkdir -p .flow/workspace/epic-[name]/{US-001-[name],US-002-[name],...}
```

**Correct structure**: `epic-[name]/` → `US-NNN-[name]/` → `_story.md`
**❌ Forbidden**: creating flat files at the `.flow/workspace/` root

---

### 1. **Create `_epic.md`** (path: `epic-[name]/_epic.md`)
   - Insert the `<!-- [DRAFT] - awaiting user approval -->` marker
   - **`**Ultimate purpose**` 1 line** (right below the title) — record the answer from the Discovery §Ultimate-purpose interview. For an independent Epic, this Epic's goal is the top; under an Initiative, restate the higher value proposition. Template: `flow-procedure-epic` Step 3
   - Include goal/scope/constraints, Story decomposition (Story outline), Discovery Notes

> Epic authoring = at the goal + Story-outline level. Each Story's Action decomposition is performed by re-entering Plan Mode when that Story is entered.

### 2. **Create each `_story.md`** (path: `US-NNN-[name]/_story.md`)
   - **`**Ultimate purpose**` 1 line** (below the title) — restate the parent `_epic.md`'s ultimate purpose (a Story inherits it as a sub-unit of the Epic). Template: `flow-procedure-story`
   - Include the goal, draft AC, expected Actions

### 3. **Request DRAFT review**: "I've written the plan draft. Please review it."

> ⚠️ Do not commit `[DRAFT]` files. Commit only after approval.

---

## AI Plan Review Gate — R1 spec (right after Draft creation, before presenting to the user)

After creating the DRAFT file, run the **R1 (Planning AI Review)** review. In Epic Planning, the main immerses itself in the R1 reviewer persona and performs it directly (no teammate assignment — the RT rules/payload are the single SSOT in `debate-redteam` §R1, only the actor differs per Phase). Persona input + essence-attack priority + single-option advisory.

> The R1 spec resolves #1, #2, #4 of the RT (Red Team) 4 weaknesses (viewing only High-priority / single-option evaluation / one-shot review / absence of persona input).
> ⚠️ The Epic Planning Phase's R1 is performed directly by the main, immersed in the persona (Epic Planning Phase = main's responsibility — no teammate assignment). Expert teammates are brought in after Planning Finalize (`handoff-protocol` bring-in-timing principles (a)(b)).

**R1 review (Epic Planning: performed by the main, immersed in the persona)**:

```
[Review input — immerse in and apply the R1 persona]
"Review the following Epic DRAFT. [_epic.md path]

[Persona input]
- Work type: architecture/meta (Epic creation is a system-structure decision)
- Applied persona: manager (Flow Manager — the plugin rules/ persona SSOT)
- Core Beliefs (3): SSOT single source / no execution without a plan / the user-confirmation checkpoint cannot be bypassed
- Anti-patterns (5): Story decomposition MECE violation, unmeasurable AC, missing dependency, ambiguous scope boundary, missing non-goal

[Essence-attack priority — check in order]
1. Persona mismatch: does the Epic goal align with the manager persona's core beliefs (SSOT/MECE/measurable AC)
2. Anti-pattern exposure: have the 5 anti-patterns above infiltrated the DRAFT
3. Essential defect: is the goal measurable / Story decomposition MECE / dependency order / AC verifiability
4. Single-option advisory: if the DRAFT presents only a single split approach, propose at least 1 alternative (a different Story decomposition)

[Output format]
- Essence-attack result: 1 line per each of the 4 priorities above ('no issues' allowed)
- High-priority issues (must resolve): N
- Alternative proposal (optional): 1 or more
"
```

→ On finding issues: fix the DRAFT immediately (save Refinement rounds)
→ After the review: present it with "R1 review complete (persona match on 4 axes passed, essence attack [N] fixed / no issues). Please review."

---

## Refinement (apply feedback)

- Revise the DRAFT file per user feedback
- Add/remove/restructure Stories
- Adjust scope, revise AC
- **Iteration limit: max 3**. If it exceeds 3, propose finalizing at the current state.

---

## Structure Validation (Hard Gate)

**Timing**: after Refinement completes, before entering Finalize
**Purpose**: block an incorrect folder structure

### Validation items

```bash
# required structure
ls .flow/workspace/epic-[name]/_epic.md
ls .flow/workspace/epic-[name]/US-*/
for dir in .flow/workspace/epic-[name]/US-*/; do ls ${dir}_story.md; done

# flat-pollution check (fatal)
ls .flow/workspace/[DRAFT]*.md 2>/dev/null  # if it exists, ERROR
ls .flow/workspace/_epic*.md 2>/dev/null     # if it exists, ERROR
ls .flow/workspace/_story*.md 2>/dev/null    # if it exists, ERROR
```

**Pass condition**: Epic folder ✅, _epic.md ✅, Story folder ✅, _story.md ✅, flat pollution ❌

**On failure**: return to Refinement, fix the structure, re-validate
**On success**: enter Finalize

---

## Finalize (finalize = plan approval)

1. Receive the user's "approve" / "OK" / "sounds good" response (= plan approval)
2. Remove all `[DRAFT]` markers: delete `<!-- [DRAFT] - awaiting user approval -->`
3. Transition to Epic Setup (create branch + finalize commit) → ExitPlanMode

> After Finalize, on entering each Story re-enter Plan Mode to author the Story (Action decomposition). Only Action execution is the autonomous-execution area outside Plan Mode.

---

## `[DRAFT]` file rules

| Rule | Description |
|------|------|
| **Marker format** | `<!-- [DRAFT] - awaiting user approval -->` |
| **Insertion position** | first line of the file (above the title) |
| **No commit** | do not commit a file with the `[DRAFT]` marker |
| **After approval** | delete the marker line → commit |
| **Existence check** | `Grep` → find unfinalized files via `[DRAFT]` |

### DRAFT re-entry handling

- `[DRAFT]` file exists → continue the Planning Phase (enter Refinement)
- No `[DRAFT]` file → start a new Planning Phase, or proceed to Setup

---

## MUST NOT

- ❌ Deciding scope/Story without Discovery
- ❌ Creating a DRAFT without Alignment questions
- ❌ **Creating flat files at the `.flow/workspace/` root in the Draft stage**
  - The Epic file must be under the `epic-[name]/` folder
  - The Story file must be under the `US-NNN-[name]/` folder
- ❌ **Creating _epic.md/_story.md files without creating the folder structure**
- ❌ Committing a file with the `[DRAFT]` marker
- ❌ Proceeding to Finalize without user approval (plan approval)
- ❌ Continuing without notice when Refinement exceeds 3 rounds
- ❌ Throwing 10+ questions at once
- ❌ Entering Draft directly without sharing the Discovery result with the user
- ❌ Implicitly folding AI assumptions into the Alignment questions without the Assumption Gate
- ❌ Presenting the DRAFT to the user directly without the AI Plan Review Gate
- ❌ **Performing planning acts (Epic/Story authoring) as autonomous execution outside Plan Mode** (planning acts belong only inside the Plan Mode + user-approval boundary)
