---
name: flow-planning-action
description: "Action Planning procedure. Lightweight Discovery→Alignment→Finalize cycle + Pre-flight Check + delegation (teammate assignment) matching reference."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.0
---

# Action Planning procedure

A lightweight planning procedure by which flow orchestration (main) confirms an Action approach.
Action Planning is the **lightweight version** — confirm quickly and proceed.

> **Plan Mode boundary (must be understood)**:
> - **Plan Mode scope of use**: scale judgment + writing the Epic + writing the Story. **Action decomposition / approach confirmation is done inside the Story-writing Plan Mode.**
> - **Autonomous execution scope**: Action execution only (performed by a teammate). Planning acts (Action decomposition / approach confirmation) are done only within the Plan Mode + user-approval boundary.
> - This procedure confirms each Action's approach with a lightweight cycle inside that Plan Mode.

## Agent Teams mapping terms (SSOT)

This flow runs on top of Agent Teams. The core mappings this procedure uses are as follows (full SSOT: `flow/SKILL.md` "Agent Teams mapping model").

| Flow concept | Agent Teams mapping |
|---|---|
| Work item (Epic/Story/Action) · state · dependency | shared task list |
| Delegation (delegate_to) | teammate assignment (assignee) — main spawns |
| Plan approval (user confirm) | plan approval (main ↔ user, Plan Mode) |
| Quality gate (document enforcement / retrospective enforcement) | hooks |

---

## Scope (gray-area declaration)

| Gray-area case | Primary | Secondary |
|---------------|---------|-----------|
| Action approach design (planning stage) | **flow-planning-action** | `flow-procedure-action` (referenced at execution) |
| Action execution (delegation/execution flow) | `flow-procedure-action` | **flow-planning-action** (confirm plan fit) |

**Core Beliefs**:
- Action Planning is lightweight — 3 stages (Discovery→Alignment→Finalize)
- Pre-flight Check is mandatory: grasp the impact scope in advance via Grep
- Delegation matching accuracy (work area ↔ teammate)
- Business rules first (over implementation details)
- Case-by-case analysis (no single-case assertion)

**Anti-patterns**:
- Jumping straight to Planning after skipping Pre-flight
- Guessing the delegation (teammate) (not verifying the work area)
- Single-case assertion (ignoring exception cases)
- No mention of business rules + only implementation details stated
- Forcing more than 1 Refinement round
- Encroaching on `flow-procedure-action` responsibility (duplicating execution details in this skill)

**Decision Heuristics**:
- Impacted files < 5 → Pre-flight quick Grep
- Impacted files ≥ 5 → detailed impact analysis
- Work area cross-cutting → delegation decision hard → confirm with user
- Business rule ambiguous → additional Discovery round
- Delegation matching = target path + work area (teammate responsibility supplied by the project agents)

**Output Quality Bar**:
- All 3 stages completed at least once (Discovery/Alignment/Finalize)
- Pre-flight Check result (Grep output summary)
- Delegation (delegate_to) stated + matching rationale
- AC table (measurable)
- Impact scope auto-collected (where applicable)

**Sanity Self-Questions**:
- "Did I run the Pre-flight Check, or did I Plan by guessing?"
- "Is the delegation-matching rationale based on the work area/path?"
- "Are the business rules stated, or only implementation details?"
- "Did I not make a single-case assertion?"
- "Did I not duplicate execution details in this skill (`flow-procedure-action` responsibility)?"

> **Principle**: "No execution without a plan." Complete the Discovery→Alignment→Finalize cycle in dialogue with the user, then enter execution.

## 3-stage Planning cycle (lightweight)

```
Discovery → Alignment → Finalize
(research)   (confirm approach)   (approval)
```

| Stage | Purpose | Main tools | Artifact |
|------|------|----------|--------|
| **Discovery** | analyze target files/patterns | `Read`, `ls`, `Grep` | approach (dialogue) |
| **Alignment** | confirm approach | `AskUserQuestion` (1) | approval (dialogue) |
| **Finalize** | switch to execution after approval | - | switch to Action execution |

---

## Timing & transition

**Timing**: at the moment of confirming the Action approach (inside the Story-writing Plan Mode)
**After completion**: transition to Action execution (teammate assignment + procedure-doc load + implementation)

---

## Discovery (research)

### 0. 🔥 Pre-flight Check 4 axes (mandatory right before Action Planning starts)

> **Detailed SSOT of these 4 axes**: `flow-procedure-action` Step 0 (the Action-entry moment) — this Phase (Action Planning) cites those details.

#### Verification 4 axes (summary)

| Axis | Verification target (at Action Planning) | Verification tool |
|----|------------|-----------|
| **1. Directory** | A-NNN.md `**target**` / `**reference doc**` paths exist | `ls` / `find` / `Read` |
| **2. Persona** | Action persona = the delegated teammate's persona, or the manager of `(direct)`. Persona SSOT consistent | grep `As a` + SSOT-table cross-check |
| **3. Branch** | current branch consistent with the active Story | `git branch --show-current` |
| **4. Asset** | **`Read` of the delegated teammate's procedure doc/guide complete** | confirm `Read` executed |

#### Asset axis detail

If a `delegate_to` field exists, **always load first** the procedure doc/guide of that work area:
- [ ] Read the guide doc's **directory structure** section and grasp the folder pattern
- [ ] Read the guide doc's **MUST NOT** section and confirm prohibitions
- [ ] Read and internalize the guide doc's **pattern/naming rules**
- [ ] Confirm the new-vs-legacy judgment criteria (where applicable)

**Asset axis example**:
```markdown
# A-003.md
delegate_to: <teammate name supplied by the project agents (lowercase-kebab)>
```
→ mandatory load of that teammate's work-area guide → confirm directory/MUST NOT/pattern

#### Self-check checklist (1 line per axis)

- [ ] Axis 1 (directory): `ls` passed — [path + result, 1 line]
- [ ] Axis 2 (Persona): SSOT table consistent — [persona name, 1 line]
- [ ] Axis 3 (branch): consistent with active Story — [branch name, 1 line]
- [ ] Axis 4 (Asset): Read complete — [Asset path, 1 line]

#### Explicit user bypass

Bypassing the Pre-flight Check is allowed only on explicit user expression (skip / move on / bypass / skip it, etc.). AI self-judged bypass is prohibited.

**AI output format on bypass (mandatory)**:

```
[bypass notice] Pre-flight bypass: action-planning
Reason: user explicit — "[quote of user expression]"
Expected risk: [which of the 4 axes goes unverified and what accident is possible]
Post-hoc retrospective duty: record the bypass fact + any failure that occurred in this Action's retrospective Problem section
```

**Post-hoc retrospective duty**: any failure after a bypass is a mandatory record in the Action/Story/Epic retrospective Problem section. Even with no failure, state "Pre-flight bypass [N] times" in the retrospective Try.

#### Mistake prevention

- ❌ Deciding the pattern from "referring to existing code" alone (the existing may also be legacy)
- ❌ Applying only general coding principles without reading the guide doc
- ❌ 0 self-checks of axes 1–3 (directory/Persona/branch) — violation of the self-review duty
- ✅ Self-check all 4 axes → guide doc → confirm actual structure → apply pattern

---

### 1. **🔥 Business-rule-first verification** — **Why/When before How**

   **Principle**: before presenting the implementation approach ("How"), first confirm the business rule ("Why/When").

   **Checklist**:

   | Item | Confirmation question | Reference |
   |------|----------|------|
   | **Save condition** | When is data saved? (event, batch, real-time) | business logic, existing logic, domain rules |
   | **Delete condition** | When is data deleted? (lifetime, conditional) | domain rules, interface contract |
   | **Query condition** | What filter/sort conditions exist? | interface contract, spec |
   | **Validation rule** | What values are valid? (range, format, dependency) | model definition, domain rules |
   | **State transition** | When does state change? (state machine, event) | domain rules, State Machine |

   **Rationale**: don't start by asking "how do I save?". Confirm "when/why do I save?" first and the implementation approach (single vs batch, etc.) is derived automatically from the business rule. Proposing implementation details without confirming the business rule risks asserting the wrong approach.

   **Reference order**:
   1. Spec/requirements doc (feature spec)
   2. Interface contract (domain boundary)
   3. Model definition
   4. Existing logic (`Grep` + `Read`)
   5. Domain expert (confirm with user)

2. **Target file analysis**
   - `Read` → target file's current content (if it exists)
   - Grasp related file structure (import, dependencies)

3. **Existing pattern analysis**
   - Confirm how similar files in the same work area are implemented
   - Grasp the coding-rule compliance items

4. **🚨 Existing-implementation grasp methodology** — mandatory before generating code

   When modifying/extending existing code or adding a new artifact, grasp the actual state with tools before guessing.

   **Common procedure**:

   | Stage | Tool | Purpose |
   |------|------|------|
   | 1. Grasp current state | `Read` | full content of the target file |
   | 2. Search related symbols | `Grep` | location of related methods/classes |
   | 3. Confirm contract/interface | `Read` | domain boundary or abstract definition |
   | 4. Reference similar implementations | `ls` / `Read` | naming/pattern of other artifacts in the same work area |
   | 5. Confirm test files | `Glob` | whether existing tests exist |

   **✅ Common checklist**:
   - [ ] Read the whole target file (`Read`)
   - [ ] Search related methods/classes (`Grep`)
   - [ ] Confirm interface/contract (where applicable)
   - [ ] Confirm test-file existence (`Glob`)
   - [ ] Reference similar implementations (other artifacts in the same work area)

5. **🚨 Confirm procedure-doc naming/structure rules** (mandatory when generating code)
   - [ ] Confirm the naming rules of that work area's guide
   - [ ] Compare existing similar files' naming patterns against the guide rules
   - [ ] Confirm interface constraints (where applicable)

6. **Impact-scope collection** (❗ mandatory)
   - Collect other files/registration targets affected by the change
   - Confirm referencing files via `grep -rn`
   - State registration/integration targets (barrel/index file updates, etc.)

   **🚨 Minimal modification scope first**:
   - From the impact-scope collection result, decompose Actions starting from the **minimal change unit**. Do not assume a large scope from the start.
   - When additional artifacts (out of Scope) are found → do not absorb them into this Action's scope. Handle as a separate Action or a non-goal.
   - "Better pattern" urge → state it as a Story non-goal then promote to a separate Action (keep the current Action a surgical change)

   **🚨 Refactoring baseline 6 items** (ground-truth inspect at impact-scope collection when work type = refactor/move/delete):
   1. **Unit** (file/line count — change scale)
   2. **Test mapping** (`find test/features` for per-target test existence)
   3. **Reference direction** (dependency direction — whether a layer-boundary violation exists)
   4. **Own-data usage sites** (exhaustive `Grep` of paths where the target imports its own data/dtos)
   5. **Filename vs class name distinction** (the two may differ — search both)
   6. **Symmetry-hypothesis body ground-truth inspection** (a "A and B are the same" assumption is confirmed by directly comparing the bodies — no guessing)
   > No asserting the baseline from a single-pattern grep once (ground-truth authority = the structure-change/DIP measurement row of the `verify-before-assert` rule).

7. **🚨 Chain-change prediction**
   - Confirm whether a major change ripples into other work areas/modules
   - If the ripple scope is ≥ 2× the plan, re-examine splitting the Action

8. **🚨 Merge/porting strategy judgment** (where applicable)

   For Merge/Cherry-pick or cross-branch file porting, analyze the structural difference first.

   **Step 1: evaluate structural difference**
   ```bash
   # Confirm the number of changed files
   git diff --name-only merge-base..origin/source-branch | wc -l

   # Compare folder structures
   diff -r <(cd source && find . -type d | sort) <(cd target && find . -type d | sort)
   ```

   **Step 2: choose strategy**

   | Condition | Strategy | Reason |
   |------|------|------|
   | Structure identical (95%+) | `git cherry-pick` | auto-merge possible |
   | File moves present (30%+) | `git show` + manual apply | conflict-resolution cost > manual apply |
   | Large-scale refactoring | `git show` + per-file apply | safety first |

   **Step 3: manual apply pattern**
   ```bash
   # Apply a file directly (using git show)
   git show origin/source:path/to/file > target/path/to/file

   # Confirm the change
   git diff merge-base..origin/source -- path/to/file
   ```

   **Path mapping on porting**: if the source/target branch structures differ, write a path-mapping table in advance and plan the import-statement conversion. Pre-mapping prevents import-mismatch rework.
   - [ ] Path-mapping table written
   - [ ] Import-statement conversion plan established
   - [ ] Barrel/index file update plan
   - [ ] Whether code generation must be re-run

---

## Alignment (question/agreement)

### Delegation (teammate assignment) judgment (pre-question stage)

Before Action execution, judge whether delegation is needed first. The `delegate_to` value is a **teammate name supplied by the project agents (lowercase-kebab)** or `(direct)`.

> **Delegation = teammate assignment**: declare which work area's teammate to entrust the Action execution to. The concrete teammate's name/responsibility/work area is **supplied by the project's agents definitions**. This procedure does not hold that mapping directly — for work-area (work character) ↔ teammate matching, refer to the project agents and `handoff-protocol`.

**Judgment criteria**:
- The Action's main work belongs to a specific implementation/test/document area → assign to that area's teammate
- The work area is ambiguous or cross-cutting → confirm with user

**When the user asks "shouldn't this be delegated to another area?"**:
- **Always re-examine** (the user detected a delegation need)
- Re-evaluate the `delegate_to` field
- Fix immediately if the judgment was wrong

**Conditions for main to perform directly** (`delegate_to: (direct)`):
- Simple document work (README, writing retrospectives)
- Git work such as branch creation, commit, merge
- Verification/execution work (running tests, confirming builds)
- Meta work (updating the flow SSOT)

---

### Action consolidation judgment (pre-question stage)

At Action Planning start, confirm the Story's total Action count and judge consolidation possibility first:

**Consolidation criteria**:
- **Similar artifact structure**: artifacts with a similar pattern in the same work area can be batch-processed
- **Same-area group**: bundle if it is the same pattern to be performed by the same teammate
- **Action count > 10**: if the Story's expected Action count exceeds 10, re-examine consolidation

**Cautions on consolidation**:
- Each artifact must be independently verifiable (build/test)
- If one Action grows too large it is actually inefficient
- When proposing consolidation, confirm with the user is mandatory

### Question

**Mandatory question** (1):
1. **Approach confirmation**: "I'll proceed with this implementation approach: [approach summary]. Is that OK?"

**Situational additional question** (max 1):
- If there is a design choice: "There's approach A and approach B. Which do you prefer?"
- When proposing consolidation: "Shall I consolidate X, Y, Z into one Action? (est. N min saved)"

### Question pool

| # | Question | Type | Mandatory |
|---|------|------|------|
| A-1 | "I'll proceed with this approach. Is that OK?" | confirm | ✅ |
| A-2 | "Design choice: A vs B. Which do you prefer?" | choice | situational |

---

## AI Plan Review Gate — R1 spec (after Draft, before presenting to user)

Right before the user confirmation, after generating the A-NNN.md DRAFT, review with an **independent review agent (R1)**.

> **R1 (Planning AI Review)** mechanism — apply the `debate-redteam` §R1 call-payload standard.
>
> **SSOT**: the `debate-redteam` §R1/R2 call-payload standard. This Gate cites the SSOT + states the Action Planning location.

**Call**:

```
Prompt (R1 payload standard):
"Please review the following Action DRAFT. [A-NNN.md path]

[Persona input — `debate-redteam` §R1 standard]
- Applied persona: the persona of the Action's main delegated teammate (implementation → implementation persona / meta → manager)
- Core Beliefs (3): {cite that teammate guide's Core Beliefs}
- Anti-patterns (5): {cite those 5 Anti-patterns}

[Essence attack, 4 priorities — `debate-redteam` §R1 standard]
1. Persona mismatch: does the Action decomposition match the main persona's Core Beliefs?
2. Anti-pattern exposure: have the 5 Anti-patterns penetrated the Action body?
3. Essential defect:
   - delegate_to field exists (lowercase-kebab teammate name or `(direct)`)
   - dependency-order consistency
   - TDD pairing (tests included in Actions that need tests)
   - Step decomposition MECE (no duplication/omission)
   - AC measurability (verifiable via grep / tool / command)
4. Single-proposal alternative self-review: if the Action decomposition is the only single approach, present at least 1 alternative

[Output format]
- Result per essence-attack priority (4): 1 line each
- High-priority issues (must resolve): N (file + line + fix)
- Alternative proposal: N (optional)
"
```

- On finding an issue → immediately fix the A-NNN.md DRAFT (save Refinement rounds)
- After review complete → present with "R1 review complete (persona-matching 4 axes passed, essence attack [N] fixed / no issues). Please review."

> **Self-review allowed — objective condition matrix** (blocks arbitrary "burden" judgment):

| # | Case | Objective signal | R1 trigger method |
|---|-------|----------|-----------|
| 1 | **Single guide + clear classification** (e.g. 1-field addition, 1-line cross-ref) | changed lines < 5 + single file + self-modification of a single guide | self-review OK |
| 2 | **Same pattern, multiple files** (e.g. same cross-ref batched across N files) | same change pattern + multiple files (≤ 5) + meta work | self-review OK (but batch quantitative verification — confirm N grep matches) |
| 3 | **Asset consistency** (cross-ref, standard-term correction) | single SSOT update + only cites other SSOT | self-review OK |
| 4 | **New rule file / new guide / large body writing** | changed lines ≥ 50 or new file | **independent review agent mandatory** — self-review blocked |
| 5 | **Code work** | code file change | **independent review agent mandatory** — self-review blocked |

> **Blocking condition**: outside 1–3 above (cases 4, 5) no self-substitution. Independent-review-agent call is mandatory (if impossible, report to the user + request explicit bypass).
> **Self-review attempt duty**: even for cases 1–3, self-checking the 4 essence-attack priorities + stating the result in 1 line is mandatory (even self-review must run — no 0 runs, 0 times).

---

## Finalize

1. Reflect the R1 review result (fix issues immediately)
2. User confirmation ("yes", "proceed", etc.)
3. Transition to Action execution

> Refinement is **max 1 round**. If the user requests a different approach, fix once then confirm.

---

## MUST NOT

- ❌ Deciding the approach without Discovery
- ❌ Starting implementation directly without an approach-confirmation question
- ❌ Transitioning to Action execution without user approval
- ❌ Throwing 3+ questions at once (Action is lightweight)
- ❌ Finalize without running the AI Plan Review Gate (R1)
- ❌ Missing the persona input when running R1 (a plain code review = mechanism void — `debate-redteam` §R1 standard)
