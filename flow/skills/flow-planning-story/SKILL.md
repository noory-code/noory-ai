---
name: flow-planning-story
description: "Story Planning procedure. Referenced for Story Action decomposition, AC definition, Pre-flight 4 axes, loading the immediately-prior retrospective, and R1 review. The Plan Mode cycle of the story-planning Phase."
user-invocable: false
metadata:
  type: procedure
  version: v1.1.1
---

# Story Planning procedure

The planning procedure the flow manager (main team lead) loads in `story-planning` mode.

> **Principle**: "no execution without a plan." Every Story is authored (Action decomposition) through human-AI collaboration in **Plan Mode**. Draft review and second confirmation are absorbed into Plan Mode's plan-approval flow. **Only Action execution is autonomous** — a teammate performs the Action's primary work.
>
> **Composition**: Pre-flight 4 axes → Discovery (Step 0 retrospective = independent-reflection input / 0.5 baseline ground-truth inspection / 1–9 exploration) → Assumption Gate → Alignment → Draft (Action decomposition — detailed criteria `references/action-decomposition.md`) → R1 Review → Refinement → Finalize.

## Agent Teams mapping (terminology SSOT)

The flow concepts of this procedure map onto Agent Teams components as follows (consistent with the `flow` skill's "Agent Teams mapping model"):

| Flow concept | Agent Teams mapping |
|---|---|
| Work unit (Epic/Story/Action)·status·dependency | shared task list |
| Work unit↔team (D1): **Story = team scope (teammate persists for the Story) / Action = single-agent unit** | teammate team (Story) ↔ task (Action) |
| Action decomposition | create shared task list items |
| Action dependency declaration (D2): `depends_on` (SSOT origin) | shared task list dependency |
| Plan approval (user confirmation) | plan approval (main ↔ user, Plan Mode) |
| Delegation (`delegate_to`) | teammate assignment (main spawns) |
| lead scheduling (D3): depends_on graph → execution waves | main reads task dependencies and decides serial/parallel |
| Quality gate (Pre-flight / retrospective enforcement) | hooks |

> The planning act (authoring a Story, decomposing Actions) is performed only within the Plan Mode + user-approval boundary. Only Action execution is autonomously delegated to a teammate.

## 7-stage Planning cycle (within Plan Mode)

```
Discovery → [Assumption Gate] → Alignment → Draft → [AI Review] → Refinement → Finalize
(research)  (state/correct assumptions)  (question/agree)  (draft)   (quality review)  (reflect feedback)  (finalize)
```

The entire cycle above proceeds within Plan Mode through human-AI collaboration. Draft review (AI Review) and second confirmation (Refinement → Finalize) are not separate stages but are absorbed into Plan Mode's plan-approval flow.

| Stage | Purpose | Main tools | Deliverable |
|------|------|----------|--------|
| **Discovery** | Grasp status, analyze code/structure | `Read`, `ls`, `Grep` | research notes (conversation) |
| **[Assumption Gate]** | Share findings summary + state assumptions + user correction | — | agreed status understanding (conversation) |
| **Alignment** | Confirm goal/scope/constraints, resolve ambiguity | `AskUserQuestion` | agreed requirements (conversation) |
| **Draft** | Create the plan-draft file | `Write` | a document file with a `[DRAFT]` marker |
| **[AI Review]** | Independent review of plan quality (R1) + immediate fix | — | reviewed DRAFT |
| **Refinement** | Reflect user feedback, revise | `Edit` | revised DRAFT file |
| **Finalize** | Remove `[DRAFT]` after plan approval, commit | `Edit`, `Bash` | finalized document + commit |

---

## Timing & transition

**Timing**: on entering `story-planning` mode (Story start request — entering Plan Mode)
**After completion**: transition to `story-setup` (create branch + create Action item files)

---

## Pre-flight Check 4 axes (mandatory immediately before entering Story Planning)

> **Origin of this rule**: `preflight-gate-enforcement` (plugin rules/). The detailed SSOT for these 4 axes is `flow-procedure-action` Step 0 (at Action entry). This Phase (Story Planning) quotes that detail + specializes it for Story Planning.

#### The 4 verification axes (summary — at Story Planning)

| Axis | Verification target (at Story Planning) | Verification tool |
|----|------------|-----------|
| **1. Directory** | `<workspace>/epic-[name]/US-NNN-[name]/_story.md` exists + the Epic's other SSOT (`_epic.md`, overview) exists | `ls` / `find` |
| **2. Persona** | This Story's user-story persona is consistent with the persona SSOT (plugin rules/) — 0 coined terms | `grep "As a"` _story.md + cross-check the SSOT table |
| **3. Branch** | The current branch is the active Epic's `epic/[name]` (immediately before branching the Story branch) | `git branch --show-current` + compare with the active Epic's _epic.md |
| **4. Asset** | The Story's prerequisite SSOT (retrospective source / evaluation frame / Epic output, etc.) has been `Read` | confirm `Read` was executed |

#### Self-check checklist (one line per axis — consistent with `gate-enforcement-default-on`)

- [ ] Axis 1 (Directory): `ls <workspace>/epic-[name]/US-NNN-[name]/_story.md` passes — [one-line path]
- [ ] Axis 2 (Persona): _story.md "As a [persona]" is consistent with the SSOT table — [one-line persona name]
- [ ] Axis 3 (Branch): consistent with the active Epic `epic/[name]` — [one-line branch name]
- [ ] Axis 4 (Asset): prerequisite SSOT Read complete — [one-line Asset path]

#### Story Planning specialization — emphasis on the Persona axis

This Phase's output (_story.md AC / Action decomposition) is the persona input source for the follow-up Phases (Action Planning / Action Execute) (`debate-redteam` §R1). If a coined-term persona infiltrates _story.md, the consistency of the follow-up R mechanisms is damaged.

→ Pre-flight Axis 2 (Persona) of this Phase is the most important — confirm _story.md persona consistency immediately on entering Story Planning.

#### Story-type branch — User Story vs Technical Story (ssot-vocabulary)

A Story has 2 types (`ssot-vocabulary` §flow unit). During Planning, branch the persona/AC format according to the type (`_story.md` `**Story type**` field).

| | User Story (US-NNN) | Technical Story (TS-NNN) |
|---|---|---|
| Persona | user/role persona ("As a [user]") | **process persona (manager/analyst — `rules/personas.md`)**. "As a user" exempt |
| AC | user value/behavior | **technical verification (grep/test/build/lint, etc. — measurable)** |
| R1 persona input | role persona | run R1 with the **process persona** (manager/analyst) — normal (not a coined term) |
| Applies to | user-value features | technical/infra/refactor/tech-debt/build/CI |

> Axis 2 (Persona) verification applies per type: for US, "As a [user]" consistency; **for TS, process-persona consistency** (manager/analyst). Do not force "As a user" into a TS — technical work uses the process persona as standard (consistent with the ssot-vocabulary TS definition).

#### User-explicit bypass

Pre-flight bypass is allowed only on the user's explicit expression (skip/move on/bypass/skip it) — AI self-judgment bypass is banned. The bypass-notice output format + the after-the-fact retrospective obligation are identical to `flow-procedure-action` Step 0 §user-explicit-bypass SSOT (only the Phase name is story-planning). In particular, bypassing Axis 2 (Persona) risks damaging the consistency of the follow-up R mechanisms.

#### Mistake prevention

- ❌ Pre-flight body run 0 times → coined-term persona infiltration
- ❌ Mistaking Discovery Step 0 (immediately-prior retrospective = independent-reflection input) for a substitute for this Pre-flight — they are separate (Pre-flight = 4 axes / Step 0 = retrospective independent-reflection guidance)
- ✅ This Pre-flight passes → enter Discovery

---

## Discovery (research)

### Step 0: immediately-prior retrospective = independent-reflection input (not automatic reflection)

> Retrospective reflection is not automatically coupled to a flow unit ([[retro-evolution]] M2 — independent reflection). Therefore **Story Planning does not automatically reflect the immediately-prior retrospective into this Story**. The immediately-prior retrospective is merely an input to the independent `retro-processing` (human-triggered + reviewed).

- **Accumulation only**: the prior Story's retrospective is accumulated in the SSOT (`_story.md`) and is extracted/aggregated into `retro.md` on archive (`flow-archive`). Story Planning does not auto-load/reflect this.
- **Personal-work completeness is separate**: fully reflecting the improvements of the prior work into the current work — the "exhaustive sweep of all impacted targets" — is not retrospective reflection but the work-completeness discipline → handled by `flow-procedure-action` exhaustive sweep.
- **When reflection is needed**: process the accumulated retrospectives **separately** via `playbooks/retro-processing.md` (an independent work type — human-triggered → pattern identification → review → reflection). It is human-triggered, not a flow entry.

> The old "auto-load the prior Story retrospective → pre-reflect into this Story" (M2 pre-reflection) contradicted the retro-processing (independent/human-controlled) model and was removed (Epic epic-retro-enforce). Story Planning proceeds from Pre-flight → Discovery Step 0.5 (baseline).

---

### Step 0.5: Epic AC baseline ground-truth inspection

> If the Story Planning stage's estimate differs greatly from the actual baseline, the accuracy of finalizing Action scope is damaged. If the Epic AC includes grep / find / ls-based verification commands, measure the baseline for real in this Step.

**Precondition**: the Epic AC (or Story AC) in `_epic.md` includes a grep-based verifiable command (e.g. `grep -rn "pattern" path/ → 0`).

**0.5-1. Identify the Epic AC verification commands**:
- Read the `## Completion criteria (Epic AC)` or `## Acceptance Criteria` section of `_epic.md`
- Extract the grep / find / ls / wc commands from each AC's "Verification method" column

**0.5-2. Run the baseline ground-truth inspection (mandatory — consistent with `gate-enforcement-default-on`)**:

Actually run each AC verification command at the current point in time. The result = the impact-count baseline of that AC.

```bash
# Example: measure the current impact count with the AC verification command
grep -rn "<pattern>" <target path> | wc -l
# → ground-truth result (compare with the Story Planning estimate)
```

**0.5-3. Analyze estimate vs ground-truth difference**:

| Difference ratio | Interpretation | Handling |
|----------|------|------|
| **ground-truth ≤ estimate × 1.5** | consistent | proceed with Action decomposition as-is |
| **ground-truth > estimate × 1.5 or ≥ 10 absolute difference** | large difference — re-estimate Action scope | re-examine _story.md Action count/targets, report to user |
| **ground-truth = 0** | already handled or no baseline | AC itself is questionable — consider returning to the Epic |

**0.5-4. Record the baseline in _story.md (mandatory)**:

Add a baseline table to the Discovery result section (or background):

```markdown
## Baseline (Story Planning Discovery Step 0.5 ground-truth inspection)

| AC | Verification command | Estimate | baseline (ground-truth) | Difference | Action impact |
|----|----------|--------|----------------|------|------------|
| AC-N | `grep -rn "..." .../` | 2 | 20 | +18 (large difference) | re-estimate A-NNN targets |
```

**0.5-5. User confirmation (at a large difference)**:

- On finding a large difference (per the table above): report to the user — "Baseline ground-truth result: estimate N → ground-truth M (difference +K). Action scope needs re-estimation. Proceed with this Story, or return to the Epic?"
- If consistent: enter Discovery Step 1 as-is

> Step 0 (immediately-prior retrospective = independent-reflection input) and this Step are separate — Step 0 = retrospective independent-reflection guidance, Step 0.5 = Epic AC baseline ground-truth inspection (mandatory run).

---

### Step 1: Status exploration (Stories that include code changes)

A Story that includes code changes grasps the target path's current structure, existing patterns, whether tests exist, and completed/unimplemented status. The exploration itself can be delegated to a teammate (the main assigns an exploration teammate — project agents supply). A Story with only document/config changes skips this and analyzes directly.

The exploration result is used as the status/assumption items of the Assumption Gate.

> **Existing code ≠ the correct answer**. Legacy code may not be the standard. Confirm the current standard pattern first (the reference implementation the project playbook defines) and re-confirm the project architecture rules (plugin rules/). Do not copy an obviously wrong structure on the grounds of "following the existing pattern." When uncertain, state "(uncertain)" at the Assumption Gate then confirm with the user.

### Step 2: Analyze _story.md
- `Read` → confirm existing `_story.md` content (the draft written at Epic creation)
- Determine whether the AC is concrete or TBD

### Step 3: Analyze related deliverables (when exploration delegation was not run)
- Confirm the current structure of the Story's target deliverables (`ls`)
- Grasp the usage of related symbols/references (`Grep`)

### Step 3.5: Interface-change blast-radius sweep (Stories that change an interface/signature)

> When a Story changes an interface, constructor, or signature (public method/function/type), fixing only some call sites and missing mocks/tests breaks the build/tests. Measure the **impact scope of the changed symbol exhaustively** in advance (Step 0.5 baseline's interface specialization — consistent with `verify-before-assert` suspicion of a 0-count negative).

**Precondition**: the Story changes the shape of an existing public symbol (interface/abstract class/constructor/function signature/type).

- **3.5-1. Identify the changed symbols**: list the changing symbol names (class/method/constructor/type).
- **3.5-2. Exhaustive grep (implementation + mock + test)**: search each symbol across the **entire** target path — ① implementation call sites ② mock/fake/stub definitions ③ tests (unit/integration). Do not narrow the path (prevent a false 0-count — if the search returns 0, suspect the path/scope first).
  ```bash
  grep -rn "<symbol name>" <entire target path>   # includes implementation + mock + test
  ```
- **3.5-3. Record impact in _story.md**: connect the impacted files as input to Action decomposition — place the mock/test-sync Action in the same scope as the implementation-change Action (consistent with `no-code-change-without-doc-sync` — the change propagates within the same Action scope).

**Checklist**:
- [ ] Exhaustive grep of the changed symbols (implementation + mock + test — path not narrowed)
- [ ] Impacted files reflected in Action decomposition (0 missed mock/test syncs)

### Step 4: Confirm existing tests
- Whether related tests exist (`ls` / `Grep`)

### Step 5: Confirm dependencies
- Among prior Story outputs, those that affect this Story
- Required packages/libraries/external resources

### Step 6: Domain/design analysis (code-generating Stories — delegated to the project playbook)

> This flow is a general-purpose planner engine (work-type based). It does not prescribe the domain model of a particular framework (layer composition, data flow, state management, etc.).

A Story that includes code generation requires business-structure analysis before implementation. **In this case the domain/design analysis procedure follows the analysis procedure the project playbook supplies** (provided by project agents/guides). The main can assign the analysis work to a suitable teammate.

Record the analysis deliverable in the "Domain analysis" (or "Design analysis") section of `_story.md`. Which components/layers are identified and which verification criteria are set is defined by the project playbook's analysis procedure. This procedure only enforces the requirement that "the analysis deliverable must exist in _story.md."

**Checklist**:
- [ ] For a code-generating Story, load the project playbook's domain/design analysis procedure
- [ ] "Domain analysis" (or "Design analysis") section written in _story.md
- [ ] The analysis result is connected as input to Action decomposition

### Step 7: Pre-confirm the delegation-target (teammate) procedure rules (code-generating Stories)

If the Story includes code generation, pre-confirm the expected teammate per Action and that teammate's deliverable rules (naming/structure/whether tests are enforced). The concrete teammate list and procedure are supplied by the project playbook + agents.

**Step 7-1. Identify the expected delegate_to teammate**: identify the teammate matching each Action's work type (design / implementation / test / infra, etc.) (value = lowercase-kebab teammate name).

**Step 7-2. Confirm that teammate's procedure**: grasp the deliverable rules / whether tests are enforced / required deliverables from the teammate's guide (project agents/guide supply).

**Step 7-3. Compare with the actual structure**: confirm the target path with `ls` and compare against the standard structure.

**Checklist**:
- [ ] Identify the expected delegate_to teammate
- [ ] Confirm the teammate's deliverable rules / whether tests are enforced
- [ ] Compare the actual structure of the target path with `ls`

### Step 8: Scale re-evaluation (consider Story → Epic expansion) ⬅️ optional
- On finding, during the Story, that the scope may grow (expected Action count > 10 / ≥2 domains / ≥3 dependent Stories):
  - Propose Epic expansion: "This Story looks large in scope for [reason]. How about expanding it into an Epic and decomposing into multiple Stories?"
- If keeping the Story: propose reducing the Action count or narrowing scope

### Step 9: Pre-verify completed items

When sizing the Story scope, verify so as not to overestimate "already-completed work."

**Step 9-1. Verify completion claims**: when it is claimed that "X is already implemented," confirm for real with `grep` / `Read`.

**Step 9-2. Judge implementation completeness**:

| Status | Criterion | Action needed |
|------|------|-------------|
| ✅ Complete | deliverable exists + tests pass + AC met | none (verify only) |
| ⚠️ Partial | deliverable exists but AC unmet | fix/complete Action |
| ❌ Unimplemented | no deliverable or inactive | full-implementation Action |

**Step 9-3. Re-estimate the Action count**: estimate only the Actions actually needed per the verification result (completed items are set only as a "verify Action").

**Checklist**:
- [ ] Confirm the actual deliverable per AC (grep/Read)
- [ ] Confirm whether tests exist
- [ ] Completed items set only as a "verify Action"

---

## Assumption Declaration Gate (mandatory after Discovery completes)

Summarize the Discovery result in 3–5 bullets, then present to the user:

**Summary format**:
- **Status**: [the actual state found in code/docs]
- **Assumption [N]**: [the interpretation/judgment the AI made] — state "(uncertain)" if uncertain
- **Unclear**: [what cannot be known for certain, to be confirmed in Alignment]

**Example output**:
```
Sharing the Discovery result:
- Status: target module exists, the existing implementation diverges from the standard pattern (uncertain)
- Assumption 1: replace the existing implementation with the standard pattern (replace with a new deliverable, delete the old)
- Assumption 2: expected delegate_to = [teammate name]
- Unclear: how to handle a specific case (to confirm in Alignment)

Is the above correct? Let me know if anything needs correcting/completing.
```

→ After receiving user corrections, enter Alignment
→ "Correct" / "OK" / "No issues" is also valid (when all assumptions are correct)
→ Corrections are reflected before the Alignment questions

---

## Alignment (question/agreement)

> ⚠️ **Apply the `purpose-anchoring` gate before composing questions**: confirm whether each question is already derivable from the ultimate purpose + lower-level SSOT. If derivable, do not ask — proceed with that answer (report in one line). Include only the non-derivable ones in the questions below.

Ask with the `AskUserQuestion` tool:

**Required questions** (3):
1. **Confirm AC**: "Please review this Story's Acceptance Criteria. Anything to correct/add?"
2. **Implementation direction**: "Any preference on the technical approach? (e.g. pattern, library)"
3. **Test strategy**: "How should we set the test scope? (unit/integration/E2E)"

**Situational extra questions** (up to 2):
- When an existing deliverable must change: "The existing X must be modified. Is that OK?"
- When there is an alternative: "There are approaches A and B. [comparison table]. Which do you prefer?"

---

## Draft (authoring the draft)

1. **Update `_story.md` (DRAFT)**
   - **`**ultimate purpose**` one line** (below the title) — if under an Epic, restate the parent `_epic.md` ultimate purpose / if an independent Story, this Story's goal (= the answer to `flow-scale-judgment` §ultimate-purpose interview) is the top level. Template: `flow-procedure-story`
   - Concretize the AC table (Given/When/Then)
   - Add the Action decomposition result
   - State each Action's delegate_to, target deliverable, AC mapping, **depends_on (prerequisite Action — D2)**
   - **Wave identification (D3)**: `depends_on` graph → identify independent Action bundles (concurrent candidates). Note the expected wave in one line in the Draft (e.g. "wave 1: A-001 / wave 2: A-002·A-003 parallel"). The dependency origin = each A-NNN.md `depends_on`; the table is a derived view.
   - **Expected Action table** (delegate_to + depends_on columns required):
     ```markdown
     | Action | Title | delegate_to | depends_on | Target |
     |--------|------|-------------|-----------|------|
     | A-001 | [title] | [teammate name — lowercase-kebab] | [] | [target] |
     | A-002 | [title] | [teammate name] | [A-001] | [target] |
     ```
   - **Delegation strategy section** (required when there are ≥2 Actions or teammates differ):
     ```markdown
     | Action | teammate | Assignment note | After return |
     |--------|----------|----------|--------|
     | A-001 | **[teammate name]** | "assign [teammate] to [work]" | main: verify/commit |
     ```
   - `<!-- [DRAFT] - awaiting Action-decomposition approval -->` marker

2. **Action decomposition order**: follow the decomposition order the project playbook defines (e.g. design → implementation → test). If there is a domain-model dependency order, the project playbook's analysis-procedure deliverable supplies that order.

### Integration consideration (when ≥2 of the following are met)
- Modifying the same deliverable (≥70% overlap)
- Sequential dependency (A → B → C)
- Same teammate
- Total estimated time < 2 hours

### Separation required (when ≥1 of the following)
- Different teammate
- Independent verification needed (unit test vs integration test)
- Estimated time > 2 hours

### Action decomposition detailed criteria (change batching / simple module / 1:1 wrapper / minimal fix / guide AC)

> 📚 See `references/action-decomposition.md` for the detailed-criteria table. Load and apply it during Draft-stage Action decomposition. Core:
> - **Change batching**: for cleanup/migration/relocation-type Epics, decompose by commit group (a bundle of related changes) rather than by category (source/test/resource)
> - **Integration judgment**: simple module (deliverable files ≤3, external references ≤1) / 1:1 simple wrapper → integrate. Large structure/added logic → separate
> - **Minimal fix scope**: one Action changes ≤ 3 files (surgical). The "better way" urge is promoted to a separate Action/Story (keep the current scope). Remove only orphans (import/variable/function) that your own change created — do not touch existing dead code without a request. Changed lines must be directly traceable to the user request.
> - **Guide-work AC**: define with `grep`/`ls`/`find` auto-discovery verification (avoid subjective manual confirmation)

### delegate_to mapping required during Action decomposition
- Map the teammate suited to each Action's work type/target (project playbook + agents supply)
- Always include the `delegate_to` field in the Action item (omission causes assignment confusion at the execution stage)
- **Code-work Action default = specialist teammate + `delegation_mode: auto`** (not the main directly). To route to `(direct)`/`direct`, give a one-line reason. Meta/analysis/document = `(direct)`. Criteria SSOT: `flow-procedure-action` §delegate_to decision criteria

### Present the Action decomposition summary
```
📋 Action decomposition draft:
- A-001: [title] (delegate_to: X, target: Y)
- A-002: [title] (delegate_to: X, target: Y)
- A-003: [title] (target: Y)  ← main direct (delegate_to: (direct))
Is this decomposition appropriate?
```

### TDD pairing rule
During Action decomposition, state the relationship between test and implementation. Whether tests are enforced is defined by the teammate procedure (project playbook supplies).
- Test-enforcing teammate: the TDD order (test Red → implement Green → Verify) is enforced inside the procedure
- Test-recommending teammate: order not enforced
- The Action description must state "includes test" or "assign a test teammate"
- An Action without a test cannot be completed (verified at the wrap-up Step)

> ⚠️ `[DRAFT]` files are not committed. Commit only after plan approval.

---

## AI Plan Review Gate — R1 spec (right after Draft creation, before presenting to the user)

After creating the DRAFT file, review it with an **independent review agent** (the review teammate the main assigns — project agents supply). The **R1 (Planning AI Review)** mechanism — persona input + essence-attack priority + single-option alternative advisory.

> R1 spec source: `debate-redteam` §R1. The Story persona injects one persona from the Story's primary-work persona (plugin rules/ persona SSOT) matching the work area.

**Run the independent review agent (R1 persona injection)**:

```
Prompt:
"Please review the following Story DRAFT. [_story.md path]

[persona input]
- Work type: {new feature | refactor | architecture/meta | bug | document/format} (auto-determine work type)
- Applied persona: the Story's primary-work persona (persona SSOT — plugin rules/)
- Core Beliefs (quote that persona's Core Beliefs)
- Anti-patterns (quote that persona's Anti-patterns)

[essence-attack priority — check in order]
1. Persona mismatch: does the Action decomposition match the primary persona's beliefs
2. Anti-pattern exposure: has the Anti-pattern above infiltrated the Action body
3. Essential defects:
   - each Action has a delegate_to field
   - dependency order (per the project playbook analysis deliverable)
   - TDD pairing (test included in a test-enforcing-teammate Action)
   - Action decomposition MECE (no duplication/omission)
   - AC has an executable verification method
4. Single-option alternative advisory: if the Action decomposition is a single approach, present ≥1 alternative (a different decomposition)

[output format]
- Essence-attack results: one line per each of the 4 priorities above
- High-priority issues (must resolve): N
- Alternative proposal (optional): ≥1
"
```

→ On finding issues: fix the DRAFT immediately (saves Refinement rounds)
→ After review: present along with "R1 review complete (persona-match 4 axes passed, essence attack [N] fixed / no issues). Please review."

> A teammate cannot do plan approval directly because EnterPlanMode/ExitPlanMode is absent. The R1 review teammate's result is delivered to the main via mailbox, and plan approval is performed between the main ↔ user (consistent with `handoff-protocol` §3.3).

---

## Refinement (reflect feedback)

- Merge/split/reorder Actions
- Revise AC
- **Iteration limit: max 2**. If it exceeds 2, propose finalizing at the current state.

---

## Finalize

1. Receive plan approval (user approval)
2. Remove the `[DRAFT]` marker
3. Transition to `story-setup` (create branch + create Action item files)

---

## `[DRAFT]` file rules

| Rule | Description |
|------|------|
| **Marker format** | `<!-- [DRAFT] - awaiting user approval -->` |
| **Insertion position** | first line of the file (above the title) |
| **No commit** | a file with a `[DRAFT]` marker is not committed |
| **Post-approval handling** | delete the marker line → commit |
| **Existence check** | `Grep` → `[DRAFT]` to find unfinalized files |

---

## MUST NOT

- ❌ Action decomposition without Discovery
- ❌ Creating a DRAFT without Alignment questions
- ❌ Committing a file with a `[DRAFT]` marker
- ❌ Proceeding to Finalize without plan approval (user approval)
- ❌ Continuing without notice when Refinement exceeds 2
- ❌ Throwing ≥10 questions at once
- ❌ Entering Draft directly without sharing the Discovery result with the user
- ❌ Implicitly folding AI assumptions only into the Alignment questions without an Assumption Gate
- ❌ Presenting the DRAFT directly to the user without the AI Plan Review Gate (R1)
- ❌ Pre-flight 4 axes run 0 times (`gate-enforcement-default-on` violation)
