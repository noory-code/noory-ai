---
name: flow-procedure-action
description: "Action execution procedure. action-setup — reference when creating A-NNN.md·Pre-flight 4 axes·delegate_to delegation·RT intensity matrix (when adding a new Action mid-Story)."
user-invocable: false
metadata:
  type: procedure
  version: v1.1.1
---

# Action document creation procedure

The detailed procedure the flow manager loads in the `action-setup` Phase.
Used only when adding a new Action mid-Story (usually already created in story-setup).

> ⚠️ **Prerequisite**: `action-planning` complete (approach confirmed in the Planning Phase)
> For the Planning procedure, see `flow-planning-action`.

## Agent Teams mapping

The core concepts of this procedure map to Agent Teams components as follows.

| This procedure's concept | Agent Teams mapping | Meaning |
|---|---|---|
| Pre-flight 4 axes (Step 0) | hooks | Action entry gate — if not passed, block starting work |
| `delegate_to` assignment | teammate assignment (assignee) | Designate the teammate who performs the Action's main work |
| A-NNN.md user confirmation | plan approval | Main↔user plan approval (Plan Mode) |
| Delegated execution | teammate assignment | Main spawns a teammate to execute |
| Work-item status (⬜/🔄/✅) | shared task list | The single source for Action progress status |

> **Delegation (`delegate_to`) = teammate assignment**. Teammates are supplied by the project via `.claude/agents/`. The teammates' names·responsibility areas·Layer mapping are defined by the project, and this procedure does not hardcode teammate names (see the teammate supply mechanism defined by the project in .claude/agents/).

## Prerequisites

- `action-planning` complete: the implementation approach is user-approved
- Story exists
- Confirmed the need for an additional Action from _story.md

## Procedure

### Step 0: Pre-flight Check — 4-axis validation (mandatory right before Action entry)

> **Origin of this Gate**:
> - **Axis 1 (directory)** — an incident where a delegation simulation proceeded without pre-validating an unsupplied directory (teammate / agents, etc.), causing work on top of a fake SSOT.
> - **Axes 2–4 (Persona/branch/Asset)** — avoiding the same pattern of incidents: using a coined persona / working on the wrong branch / not Reading an Asset.

#### The 4 validation axes

| Axis | Validation target | Validation tool | On violation |
|----|----------|----------|--------|
| **1. Directory** | The `**target**` / `**reference docs**` field paths in A-NNN.md actually exist. Guide/rule/teammate-definition paths, etc. | Confirm existence with `ls` / `find` / `Read` | Work on top of a fake SSOT → defect accumulation |
| **2. Persona** | The applied persona is consistent with the project persona SSOT. 0 coined terms | `grep "As a"` _story.md / A-NNN.md / cross-check the SSOT table | SSOT standard-term violation → damages downstream evaluation consistency |
| **3. Branch** | The current branch is consistent with the active Epic/Story. Epic branch = `epic/[name]` / Story branch = `story/[epic-name]/[ID]-[name]` | `git branch --show-current` + cross-check the active Epic/Story SSOT | Working on the wrong branch → squash merge / broken consistency |
| **4. Asset** | The target guide / rule / procedure doc has been Read. The delegate_to teammate's procedure/guide is loaded | Confirm `Read` was executed (no guessing / memory / context assumption) | Asset not loaded → guesswork → procedure bypass (consistent with `load-skill-on-phase`) |

> **External systems (RAG / external docs / issue tracker / messenger)** are also included in axis 1 (directory/connection existence) — authenticate + ping with that tool.

#### Procedure

1. **Extract A-NNN.md's `**target**` / `**reference docs**` / `**delegate_to**` / `**Persona**` (if any) / active branch**
2. **Validate each of the 4 axes** — run the validation tools in the table above
3. **On validation failure**:
   - Report to the user immediately: "Pre-flight axis [N] failed — `{target}` is [cause]. This work's assumption may break. How should we handle it?"
   - Present options: (a) hold the work (b) do the prerequisite work (SSOT creation / branch switch / Persona correction, etc.) then proceed (c) re-review the assumption
   - Proceed to the next Step only after the user's decision
4. **Validate unsupplied assets** — assets like the teammate-definition directory require explicit confirmation:
   - Exists → treat as an active asset
   - Does not exist → state "inactive at this point / future supply target" (block the fake-SSOT assumption)
5. **Self-check checklist** (output 4 axes one line each — consistent with gate-enforcement-default-on):
   - [ ] Axis 1 (directory): `ls` passed — [path + result, 1 line]
   - [ ] Axis 2 (Persona): SSOT table consistent — [persona name, 1 line]
   - [ ] Axis 3 (branch): active Story consistent — [branch name, 1 line]
   - [ ] Axis 4 (Asset): Read complete — [Asset path, 1 line]

#### Pass criteria (Hard Gate)

- All 4 axes pass, or explicitly recognized as "unsupplied asset / proceed after user decision"
- Self-check checklist 4 lines output (no 0 firings, 0 times)
- On violation: block work progress + record in the retrospective Problem section

#### User-explicit bypass

Bypassing the Pre-flight Check is allowed only on the user's explicit expression (skip / move on / bypass / skip it, etc.). No AI self-judgment bypass. For the expression list + AI self-judgment prohibition details: project rule `gate-enforcement-default-on`.

**AI output format on bypass (required)**:

```
[Bypass notice] Pre-flight bypass: [Phase name — action-execute, etc.]
Reason: user-explicit — "[quote the user's expression]"
Expected risk: [which of the 4 axes goes unvalidated and what incident is possible]
Post-hoc retrospective duty: record the fact of the bypass + the failure that occurred (if any) in this Action's retrospective Problem section
```

**Post-hoc retrospective duty**: a failure that occurs after a bypass must be recorded in the Action/Story/Epic retrospective Problem section (consistent with `gate-enforcement-default-on` §4). Even with no failure, state in the retrospective Try "Pre-flight bypass [N] times — re-review the need to bypass next time for the same work."

#### Examples

```
✅ 4 axes pass (normal):
   AI: "Pre-flight 4-axis self-check:
        - Axis 1 (directory): ls target path → exists ✅
        - Axis 2 (Persona): Manager (Flow Manager) — consistent with persona SSOT ✅
        - Axis 3 (branch): story/[epic-name]/US-001-[name] ✅
        - Axis 4 (Asset): guide/procedure doc Read complete ✅
        → Proceed with A-001."

❌ Axis 1 violation:
   AI: "Main → teammate delegation simulation..."
   (in fact the teammate-definition directory does not exist — work on top of a fake SSOT)
✅ This Gate applied:
   AI: "Pre-flight axis 1: ls directory → absent.
        Judged an unsupplied asset. Hold work + report to the user."

❌ Axis 2 violation:
   The _story.md user-story persona is a coined term outside the persona SSOT.
✅ This Gate applied:
   AI: "Pre-flight axis 2: grep 'As a' → found a coined term outside the SSOT.
        SSOT table consistency violation. Report to the user."
```

### Step 0.5: Full sweep of affected targets (multi-location-impact work — mandatory before starting changes)

> A **personal work completeness** discipline separate from retrospective reflection (independent `retro-processing`). Blocks "closing only half" (touching only some affected targets and missing the rest). The substance the [[retro-evolution]] M2 boundary points at.

**Trigger**: work where a change affects multiple locations — consistency / migration / migration / cross-ref change / "N-kinds·count" consistency, etc. (a single-file single change may be skipped)

**The 4 kinds of affected targets (all fully identified with `grep` / `ls`)**:
1. **Body** — the file changed directly
2. **In-file citations** — repeats of the same concept within the same file (prevent missing residue in the same file after fixing only the body)
3. **Cross-file cross-ref** — every other file that cites that concept
4. **`.claude/rules` synced copies** — the sync targets when the plugin `rules/` change (sync in the same work instead of relying on a flow-config re-run)

**P4 guardrail 4 items (firing duty — checklist output, no 0 firings · `gate-enforcement-default-on`)**:
- [ ] Writing a new rule/doc = cross-check existing SSOT with `grep -rn` (check for duplication/contradiction)
- [ ] "N-kinds·count" consistency = fully `grep` that number string then update all at once
- [ ] Identifier·section-name change = update cross-refs simultaneously (prevent dangling)
- [ ] Quantitative expression (intensity·repetition) = cite the SSOT only (no new self-defined grade · `ssot-vocabulary` consistency)

**Procedure**: fully identify the 4 kinds of affected targets (`grep` / `ls`) → process all at once → **re-`grep` residue (confirm 0)**.

> **Separate from retrospective reflection (M2 boundary)**: this sweep is about the completeness of the *current work* (preventing omissions). It is **not** the automatic reflection of the *immediately preceding retrospective Try* into the current work — retrospective reflection is the independent `retro-processing` ([[retro-evolution]] M2). Do not conflate (personal work completeness ≠ retrospective reflection).

---

### Step 1: Determine the next Action number

```
.flow/workspace/epic-[name]/US-NNN-[name]/
├── A-001.md  (exists)
├── A-002.md  (exists)
└── A-003.md  ← next number
```

### Step 2: Confirm the project structure·convention guide (code-writing Action)

> This Step is mandatory for every code-writing Action

1. **Read the project structure guide**: confirm the standard folder structure (project-supplied)
2. **Confirm the actual project structure**: ground-truth-inspect the target directory (`ls` / `find`)
3. Cross-check standard vs actual → decide the file path
4. **Read the project convention guide**: confirm coding conventions (project-supplied)

> The project structure·convention guide is supplied by the project via `.claude/agents/` or a separate guide. This procedure does not assume the guide exists; it validates existence in the Asset axis (Step 0).

**Prohibited**:
- ❌ Skipping guide loading because it is "direct implementation"
- ❌ Trusting the Action document's paths without validation
- ❌ Following only the standard without confirming the actual structure

### Step 3: Create A-NNN.md

**Header fields**:

| Field | Required | Description | Example |
|------|------|------|------|
| **delegate_to** | Required for code work | The teammate name performing the work (lowercase-kebab) or `(direct)`. **Code work default = specialist** (meta·analysis·docs are `(direct)`) | (specialist teammate name) / `(direct)` |
| **delegation_mode** | Optional | Invocation method (default: `auto` — system auto-decides) | `auto` / `subagent` / `direct` |
| **skill** | Optional | Additional guide the teammate references | (project-supplied guide) |
| **reference docs** | Optional | Additional reference document | (project structure guide, etc.) |
| **target** | Required | Target file/folder of the work | (work target path) |
| **depends_on** | Optional | List of prerequisite Action numbers this Action depends on (omit/empty array if none) — **the SSOT source of Action dependencies** | `[A-001, A-003]` / `[]` |
| **AC mapping** | Required | Story AC item numbers | AC-1, AC-2 |
| **includes tests** | Required | Whether this Action includes writing/running tests | `yes` / `no` (meta/doc work) / `N/A` (delegated teammate's responsibility) |

> 🚨 **delegate_to judgment criteria (code work = specialist team by default / recommended, not enforced)**:
> - **Code-writing Action = specialist teammate + `delegation_mode: auto` by default** — the main does not write it directly but assigns the Action's main work to a specialist (the default path — if left alone, it goes to the team).
> - **To carve code work out to `(direct)`/`direct`, add a one-line reason in A-NNN.md** (e.g., "single-file surgical fix — solo has less integration overhead"). Opting out is free, but leave it a conscious choice.
> - **Meta·analysis·docs·script work → `(direct)`** (Flow Manager directly — no reason needed, this is the default).
> - Teammate names·responsibility areas (Layer mapping / testing / refactoring / Story-level delegation, etc.) are **supplied by the project via `.claude/agents/`**. This procedure does not hardcode specific teammate names.
> - ⚠️ **Recommended, not enforced (hook deny)** — it does not block. It sets the default path of code work to the team so the main does not unconsciously fall into solo.

> 🚨 **`delegation_mode` value meanings**:
> - `auto` (default — recommended for code work): system auto-decides — assign to teammate if a teammate definition exists, else direct
> - `subagent`: force teammate assignment (teammate definition required)
> - `direct`: force Flow Manager direct execution (meta work / bypass teammate assignment)
>
> Details: `handoff-protocol` §3

> 🚨 **teammate matching procedure** (mandatory after deciding delegate_to):
>
> 1. Reference the project teammate mapping (project-supplied `.claude/agents/` or a mapping table) → confirm the priority match per situation
> 2. Confirm that teammate's responsibility area + reference guide
> 3. Enter the main guide the teammate references in A-NNN.md's **skill** field (if applicable)
> 4. Enter the concrete sub-guide in the **reference docs** field (if applicable)
> 5. On teammate assignment — reference the teammate definition's "responsibility area" + "invocation interface"

> 🚨 **Delegation procedure** (teammate assignment):
>
> When executing an Action with a delegate_to, the Flow Manager auto-delegates:
>
> 1. **Teammate assignment** (delegate_to = teammate name — lowercase-kebab):
>    - The main spawns the teammate to execute the Action (a teammate cannot spawn another teammate)
>    - The main orchestrates the Epic/Story/Action (runs the playbook procedure + assigns specialists — consistent with `handoff-protocol §3.4 (b)(c)(d)`)
>    - Return to the user = at Epic wrap-up or when an important decision arises (`§3.4 (d)`)
> 2. **Direct execution** (delegate_to = `(direct)`):
>    - Meta work, etc. — Flow Manager directly executes
>
> For the detailed invocation interface + invocation-flow diagram + 4 deployment-timing items: see `handoff-protocol` §3.2 ~ §3.4

> 🚨 **`depends_on` — Action dependency SSOT (D2)**:
> - **`A-NNN.md`'s `depends_on` field = the single source (SSOT) of Action dependencies**. Format: an array of prerequisite Action numbers (`[A-001, A-003]`), `[]` or omitted if no dependency.
> - **The `_story.md` Action table's dependency column = a derived view** (for at-a-glance visibility, not the source). On conflict, `depends_on` takes precedence (`ssot-write-only` consistency).
> - **Consumer = the lead scheduling decision layer**: the main topologically sorts the `depends_on` graph → splits into execution waves (independent = concurrent · dependent = next wave). Details: `handoff-protocol` §3.1.1 + `flow` SKILL `### lead scheduling decision layer (D3)`.
> - **No circular dependency**: the `depends_on` graph is a DAG. On finding a cycle, block + report to the user.

**A-NNN.md template**:

```markdown
# Action: [1-line title]

**Story**: US-NNN-name
**Action**: A-NNN
**Ultimate purpose**: [restate the parent _story.md's ultimate purpose = the top of this tree (entry scale: one of Story/Epic/Initiative)]
<!-- The tail of the purpose chain. Even in deep work, the 'why' exists next to the document. Merely inherit the top the parent set; do not invent a nonexistent parent -->
**delegate_to**: [teammate name]        <!-- project-supplied teammate name (lowercase-kebab) or (direct) -->
**delegation_mode**: auto             <!-- default auto / subagent or direct when forced -->
**skill**: [reference guide]
**reference docs**: [project structure guide, etc.]
**target**: [work target path]
**depends_on**: []    <!-- D2 SSOT source: list of prerequisite Action numbers (e.g., [A-001, A-003]). The lead scheduling decision layer splits waves by this field. The Story table is a derived view (not the source) -->
**AC mapping**: AC-1, AC-2
**type**: New feature   <!-- auto-determined: see §work type auto-determination below. User override possible -->
**RT applied intensity**: medium (R2)   <!-- auto-decided: see §RT intensity matrix below. R3 is omitted if `retrospective.levels.action.rigor` is `none` -->
**status**: ⬜

## Goal
[concrete 1-2 sentences]

## Completion criteria
| Criterion | Verification method | Result |
|------|----------|------|
| [criterion] | [verification command / manual check] | ⬜ |

## Spec (Spec-Driven)
> Pre-define the concrete shape and quality level of the output.
> - **Design Action**: the deliverable itself is the spec. Describe only the "expected scope". After completion, the result becomes the next Action's spec.
> - **Implementation Action**: the preceding design result is the spec. Pseudo code / interface signatures / before→after mapping, etc.
> - **Documentation Action**: the list of changed items is the spec.
> - Spec changes require user confirmation.

[pseudo code, interface signatures, mapping tables, changed items, etc.]

## Expected deliverables
> A design Action is at the "expected scope" level. Confirmed only after implementing.
- [deliverable path] (create/edit)
- [test path] (create)

## Step 1: Setup
- [ ] Confirm target files
- [ ] Confirm dependencies
- [ ] Load guide

## Step 2: Implementation
- [ ] Implement per the guide procedure
- [ ] When reusing an existing regex·function, ground-truth-inspect 1 example of the matched region (whether the header is included, etc.) + `Read` in advance the function's behavior when a file/directory is absent (`verify-before-assert`)
- [ ] Completion criteria met

## Step 3: Wrap-up
- [ ] Verify completion criteria → result ⬜→✅
- [ ] Cross-check expected deliverables vs actual deliverables
- [ ] Process the Action retrospective (per `.flow/settings.json` `retrospective.levels.action.rigor`. If `none`, skip the mandatory retrospective requirement/R3 + record a settings memo; for other labels, write the retrospective at the corresponding intensity)
- [ ] The corresponding Action Step in _story.md → ✅
- [ ] git add & commit

## Result (written on completion)
## Retrospective or settings memo
> If `retrospective.levels.action.rigor=none`, do not write an Action retrospective; leave only a "Action retrospective skipped" settings memo.
> For other labels, write the retrospective at the corresponding intensity per `flow-retrospective` / `flow-retrospective-templates`.
```

> 🚨 **Pre-definition principle**: completion criteria and expected deliverables are fixed before implementation. No fitting them in after implementation.

### Step 4: Update _story.md status

Change that Action's status ⬜ → 🔄

### Step 5: User confirmation

"Shall I execute Action N: [title]?"

### grep-check related tests when deleting code

> When deleting/moving a code file, pre-check so that leftover references do not cause build/compile errors.

```bash
# Check whether the deletion target file's symbols are referenced in tests
grep -rn "SymbolName" test/
grep -rn "import.*deleted_file" test/

# If there are results, edit/delete those test files too
```

**Checklist**:
- [ ] Grasp the export symbol list of the deletion target file
- [ ] Search for references in the test/ directory with `grep -rn`
- [ ] Edit or delete the referencing test files too

---

## Work type auto-determination (A-NNN.md `**type**` field)

On A-NNN.md creation, auto-label the work type by the following signals. The user can manually override.

| Signal | Determination result |
|------|---------|
| Edit path = rule / guide / hook, etc. meta asset | **Architecture/meta** |
| `delegate_to` = refactoring teammate | **Refactoring** |
| Cross-Layer (multiple Layers edited simultaneously, expected) | **New feature** (intensity ↑) |
| Affected files ≥ 10 | **Refactoring/new** (intensity ↑) |
| Edit path = doc / retrospective section | **Docs/format** |
| Changed lines < 5 + single file | **Simple change** |
| Otherwise a code change | **New feature** (default) |

**Determination timing**:
- Auto-determine right after Step 3 (A-NNN.md creation) → record in the `**type**` field
- If the impact scope grows at Pre-flight Check time, re-determine → promote after user confirmation

**User override**:
- Edit the `**type**` field in A-NNN.md directly. If it differs from the auto-determination, a 1-line reason comment is recommended.

---

## RT intensity matrix (A-NNN.md `**RT applied intensity**` field)

Auto-decide RT intensity from work type + persona + C-grade impact.

| Work type | Persona type | C-grade impact | RT intensity | R1 | R2 | R3 |
|---------|------------|------------|:-------:|:--:|:--:|:--:|
| Architecture/meta | Manager | 1+ | **strong** | ✅ | ✅ | ✅ |
| Architecture/meta | Manager | 0 | strong | ✅ | ✅ | ✅ |
| Architecture/meta | Non-manager | 1+ | **strong** | ✅ | ✅ | ✅ |
| Architecture/meta | Non-manager | 0 | **medium** | △ (optional) | ✅ | △ (optional) |
| New feature | Layer developer | — | medium | △ | ✅ | △ |
| Refactoring | Layer developer | — | **strong** (Refactor > Dev) | ✅ | ✅ | ✅ |
| Bug | Layer developer | — | weak | ❌ | ✅ | ✅ |
| Docs/format | Analyst | — | weak | ❌ | △ | ✅ |
| Simple change | All types | — | weak | ❌ | ❌ | △ |

**Application rules**:
- **C-grade 1+** (this work got a C in evaluation, or this work directly handles a C-grade asset) → auto ↑ RT intensity
- **Manager** → R1+R2 default ✅. R3 applies when the Action retrospective intensity (`retrospective.levels.action.rigor`) is not `none`
- **Refactor > Dev** (conflict priority — refactoring first) → refactoring work is always strong
- **Action retrospective intensity priority**: R3 is a mechanism right after the Action retrospective, so if `.flow/settings.json` `retrospective.levels.action.rigor=none`, it is omitted. R1/R2 are kept in that case.

**R1/R2/R3 mechanism location + payload standard SSOT**:

| Mechanism | Timing | Location SKILL.md | Payload standard SSOT |
|---------|------|--------------|------------------|
| **R1** | After the Planning Draft is complete | `flow-planning-epic` / `flow-planning-story` / `flow-planning-action`'s `## AI Plan Review Gate` | **`debate-redteam` §R1 invocation payload standard** |
| **R2** | Right before the Action commit | `flow-verify-commit` §Step 2.5 | **`debate-redteam` §R2 invocation payload standard** |
| **R3** | Right after writing the retrospective | `flow-verify-commit` §Step 5.5 + `flow-retrospective` §RETRO-1-05 | **`debate-redteam` §R3 invocation standard** |

> SSOT: this matrix is the codification of RT application. **The payload standard is `debate-redteam`** (RT persona SSOT). Reference it when auto-labeling A-NNN.md `**type**`/`**RT applied intensity**`.
> **Executor**: every R1/R2/R3 pass picks its executor per `debate-redteam` §Executor selection — Codex when its plugin is available in a Claude Code session, the plugin's own RT mechanism otherwise.

---

## Reverse verification (prevent becoming a dead letter)

Periodic grep that the R-mechanism location SKILL.md actually cites the `debate-redteam` payload standard (Hard Gate):

```bash
# R2 dead-letter check (flow-verify-commit)
grep -n "R2\|independent review agent\|persona input\|essence attack" skills/flow-verify-commit/SKILL.md
# Expected: ≥ 5 hits (persona input + 4 essence-attack priorities stated)

# R1 dead-letter check (planning-*)
grep -n "R1\|independent review agent\|persona input\|essence attack" skills/flow-planning-action/SKILL.md
grep -n "R1\|independent review agent\|persona input\|essence attack" skills/flow-planning-story/SKILL.md
grep -n "R1\|independent review agent\|persona input\|essence attack" skills/flow-planning-epic/SKILL.md
# Expected: each ≥ 3 hits (including planning-epic — verify all 3 location SKILL.md of the R matrix)

# R3 dead-letter check (retrospective)
grep -n "R3\|retrospective RT" skills/flow-retrospective/SKILL.md
# Expected: ≥ 3 hits
```

**On violation**: the R mechanism itself has become a dead letter — immediately reinforce the body + record in the retrospective Problem.

> This verification is the Hard Gate of this guide (`flow-procedure-action`) — the Flow Skill fires it before Action entry.
