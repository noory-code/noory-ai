---
name: handoff-protocol
description: "Delegation protocol. Meaning of the delegate_to field, the teammate-assignment mechanism, gray-zone Primary/Secondary, delegation-failure fallback reference. Owns 'how to delegate' (the protocol) — 'who does what' (the actual teammate definitions) belongs to the project (.claude/agents/)."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.3
---

# Handoff Protocol — delegation protocol

The protocol for delegating work between the flow orchestration (main) ↔ a teammate (specialist).

> **This skill's boundary (must understand)**:
> - **This skill = "how to delegate"** — the delegation protocol, the `delegate_to` field structure, the teammate-assignment mechanism, gray-zone decisions, and failure fallback (project-agnostic, general).
> - **The project (.claude/agents/) = "who does what"** — the concrete teammate (specialist) definitions — each teammate's name, responsibilities, model, and effort value — are defined by the project (in .claude/agents/). This skill does not deal with those teammate names or responsibility mappings.
>
> **Scope**: every moment when the main (team lead) → delegates an Action's execution to a specialist teammate.

---

## §1 The meaning of `delegate_to` (SSOT)

**`delegate_to` = "designates the teammate that will execute the Action's main work"**
- Value 1: **teammate name** (lowercase-kebab — the name of a specialist teammate)
- Value 2: `(direct)` — the main (team lead) performs it directly (meta work, etc.)
- Essence: declares who performs the Action's main work

> The **concrete list and responsibilities** of teammate names are defined by the project (in .claude/agents/). This skill specifies only the **field structure** — that `delegate_to` points at a teammate.

### Agent Teams mapping model

This flow runs on top of Agent Teams. The delegation concept is implemented via the following mapping:

| Flow concept | Agent Teams implementation |
|----------------|-----------------|
| Delegation (`delegate_to`) | **teammate assignment** (the main spawns a teammate) |
| Team structure | main = a single team lead / specialists = teammates (no hierarchy — "No nested teams") |
| teammate-spawn authority | **main only** — a teammate cannot spawn another teammate |
| Peer collaboration (info · review) | **mailbox directly** (teammate ↔ teammate — peer-to-peer, no routing through the lead) |
| Plan approval | **plan approval** (main ↔ user, Plan Mode) |

**Team-structure constraint (core)**: the main is a single team lead. A teammate cannot **spawn** another teammate ("No nested teams"). Therefore, **if a new teammate is needed**, it requests the main via mailbox and the main spawns it (no hierarchical delegation — spawn is a single-subject operation owned by the main). **However, collaboration between already-active teammates (info sharing · review) is peer-to-peer direct mailbox** — no routing through the lead (the essence of Agent Teams). What requires the lead is spawn · assignment · plan approval. (Claude Code AT-on only — Copilot falls back to AT-off.)

---

## §2 The `delegate_to` field in A-NNN.md

```markdown
# Action: [work title]

**Target**: [work-output path]
**delegate_to**: [teammate name]              ← the teammate to delegate to (lowercase-kebab)
```

**Rules**:
- Required (for an Action that has main work)
- Value: **teammate name** (lowercase-kebab) or `(direct)`
- For meta work, etc., with no separate delegation, use `(direct)`
- Unassigned teammate → warning + fallback (the main handles it itself)

---

## §3 Invocation flow

### §3.1 Basic delegation flow (main ↔ teammate assignment)

```
┌────────────────────────────────────────────────────────────┐
│ Main (team lead) — enters action-execute                   │
│ 1. Load A-NNN.md                                           │
│ 2. Detect delegate_to (value = teammate name)              │
│ 3. Assign that teammate (spawn)                            │
│ 4. Pass context to the teammate                            │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│ teammate (performs the main work)                          │
│ 1. Follows its own procedure                               │
│ 2. Loads sub-guides (if needed)                            │
│ 3. Creates/modifies outputs                                │
│ 4. Reports completion ("verify/commit stage notice")       │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│ Main (team lead) — enters action-finish                    │
│ 1. Invoke the verification procedure                       │
│ 2. Update A-NNN.md status                                  │
│ 3. Write the retrospective                                 │
│ 4. Commit                                                  │
│ 5. Update _story.md                                        │
└────────────────────────────────────────────────────────────┘
```

### §3.1.1 The lead scheduling decision layer (a first-class stage — parallel/serial decision)

> **Topology (D3)**: parallel assignment is not an incidental "capability" but **a first-class scheduling stage that the main (lead) always runs whenever it executes a Story's Actions**. The decision layer always spins, and whether its *output* is parallel or serial depends on dependencies, conflicts, and AT activation. Model SSOT: `flow` SKILL `### lead scheduling decision layer (D3)`.

The main does not flow Actions linearly "one at a time next"; it decides the schedule via **dependency graph → topological sort → execution waves**. Since only the main holds teammate-spawn authority (§ Agent Teams mapping), the main is also the subject of scheduling and parallel orchestration.

**Scheduling decision-layer procedure** (always, when the lead enters Story Action execution):
1. **Collect dependencies**: each `A-NNN.md`'s `depends_on` (the source SSOT — `flow-procedure-action`). The Story table is a derived view.
2. **Topological sort → waves**: an Action with no dependencies (or whose predecessors are complete) = the same wave (concurrent candidate); a dependent Action = the next wave.
3. **Conflict check**: within the same wave, Actions modifying the **same target path** are excluded from concurrency → dropped to serial (best-effort, worktree isolation if needed — limits exist).
4. **Confirm & execute per wave**: user confirmation is per wave. Independent Actions in the same wave run in parallel — AT-on = peer-to-peer teammates / AT-off = parallel subagents (the Task tool); serial only where dependencies or conflicts force it.

```
        ┌─ Main: preceding Action done (e.g. Domain contract frozen) ─┐
        │                                                             │
        ▼                   (assign concurrently)                     ▼
  teammate A (e.g. Presentation)          teammate B (e.g. Data)
        │                                                             │
        └────────────────── both done ──────────────────┘
                             ▼
          Main: integration verify + review & evaluation (§3 finish)
```

**Parallel-assignment conditions** (all must hold):
- **No output dependency between Actions** (predecessor output = only a frozen contract/interface is shared; each other's output is not needed)
- **No concurrent modification of the same file** (0 file-conflict risk — if a conflict is possible, go serial or isolate with a worktree)
- Each Action has an explicit `delegate_to` (identify the parallel-target teammate)

**Judgment signal**: if, after one stage in the playbook procedure (e.g. Domain design) completes, **the rest depend only on that output**, it is a parallel candidate. The playbook may mark parallelizable stages in its `## Procedure` (e.g. "6·7 (Presentation · Data) — parallelizable once the Domain contract is frozen"). Even with a linear notation, if the dependency analysis shows independence, the main may assign in parallel.

> ⚠️ **The decision layer is first-class (always running) — parallelism is its output, not a mandate**. If there are dependencies/conflicts/AT-inactive, dropping even the same wave to serial is normal (safe). Wrong parallelism (concurrent work atop an unfrozen contract) invites rework. In other words, "scheduling always, parallelism conditionally".

### §3.1.2 Subagent system constraints (invocation invariants)

The following constraints are invocation invariants independent of project and work type. Playbooks, teammate bodies, and Action plans are written on the premise of these constraints.

| Constraint | Meaning | Correct handling |
|------|------|-------------|
| **No nested invocation** | A teammate/Subagent cannot directly spawn another teammate/Subagent. Even if a lead-style teammate's body contains an expression that invokes a specialist, an actual nested spawn is impossible. | Work that needs a new teammate is requested to the main via mailbox, and the main assigns it directly. Info sharing · review between already-active teammates is handled by peer-to-peer direct mailbox. |
| **Single-working-tree parallel constraint** | If multiple teammates change files in parallel in the same git working tree, checkout/reset/stage/same-file-modification states can conflict. | If parallel file changes are needed, first design a separate `git worktree` isolation strategy. Without an isolation strategy, drop to serial execution within the same working tree. |
| **Main-direct routing principle** | The main directly assigns an Action's executor based on `delegate_to`. Do not plan on the premise of a teammate re-delegating to another teammate. | `delegate_to` is a routing input the main reads. New teammate assignment goes through the main; collaboration between active teammates is separated into peer-to-peer direct mailbox. |

> Core: orchestration authority rests with a single subject, the main. Teammates perform the main work. New teammate assignment · plan approval · parallelization judgment are reclaimed by the main, and info sharing · review between already-active teammates is direct collaboration.

### §3.2 The 2 invocation interfaces

Delegation is implemented via 2 interfaces between the main (team lead) and specialist teammates. (No orchestration middle layer — the main assigns and manages directly.)

#### §3.2.1 Interface 1: main ↔ specialist (Action assignment)

- **When invoked**: at Action execution (the main assigns the specialist matching each stage of the playbook procedure)
- **Implementation**: the main spawns the specialist (teammate assignment). The main orchestrates the playbook procedure directly, handing each stage's work unit to the specialist.
- **Input** (main → specialist): the current playbook stage + output format + context (target path + AC + analysis result)
- **Output** (specialist → main): the outputs + a self-retrospective (the main accumulates it into the Action retrospective)

**Standard spawn-prompt checklist** (the 6 base items when the main writes the specialist input — recurred 5 times in external-project retrospectives):

- [ ] **(a) Dependency-direction (DIP) compliance** — specify that the output's dependency direction points toward the domain (no inversion)
- [ ] **(b) Preserve existing behavior · contract (semantic)** — specify the preservation scope so the change does not break existing callers' or interfaces' behavior
- [ ] **(c) Include adversarial review (Red)** — instruct the output to attack itself (boundary · failure · bypass cases) (RT intensity per `flow-procedure-action` §RT intensity matrix)
- [ ] **(d) Specify existing mechanisms to reuse** — before writing anew, present the paths of reuse targets (existing functions · regexes · utilities) (`verify-before-assert` — ground-truth inspection of behavior first)
- [ ] **(e) Specify the mechanism that will consume the output** — who/what takes this output as input (consumer-contract parity)
- [ ] **(f) Post-completion return · mailbox report format** — the outputs + a self-retrospective + "verify/commit stage notice" (§7 correct completion procedure)

> The 6 base items — for items irrelevant to the work type, mark "N/A" on one line (no silent omission).

#### §3.2.2 Interface 2: peer collaboration (peer-to-peer mailbox)

- **When invoked**: when a specialist needs the output · review · info of another **active teammate**
- **Implementation**: **already-active teammates use peer-to-peer direct mailbox** (no routing through the lead — the essence of Agent Teams). They share a shared task list and exchange messages · reviews directly. **Only when a new teammate is needed** do they request a spawn from the main (a teammate cannot spawn — "No nested teams"). → This is **real team collaboration**, different from "the main spawns N workers in parallel and just gathers the results".
- **Active-team patterns** (Claude Code AT-on — actively used during a Story):
  - **Multi-perspective investigation · review**: several teammates investigate concurrently from different angles → share and challenge each other's findings (not central gathering)
  - **competing hypotheses**: each teammate verifies a different hypothesis → teammates rebut each other (scientific debate)
  - **cross-layer independent ownership**: per-area teammates work independently + communicate directly at the boundaries
- **A tool with no spawn mechanism (e.g. Copilot)**: peer-to-peer · spawn unavailable → the main runs the wave order itself; on Claude with AT merely off, use parallel subagents instead (`ARCHITECTURE.md §5`)
- **Input/output**: direct mailbox between teammates (work unit + context). Request a main spawn only when a new teammate is needed + confirm 0 trespass into the caller's area

### §3.3 plan approval — working around the teammate's G-defect

**G-defect (important)**: a teammate (specialist) does not have the EnterPlanMode / ExitPlanMode tools. Therefore a specialist **cannot perform plan approval (Plan Mode plan approval) directly.** plan approval is possible only between the main ↔ the user.

**Workaround procedure** (when a specialist must propose a plan):

1. The specialist drafts the plan (within its own context).
2. Specialist → **sends a "plan proposal" message to the main via mailbox**.
3. The main reviews the proposal.
4. The main decides: **reject** (request changes via mailbox → specialist rewrites) or **approve** (instruct to proceed).
5. If it is a large decision requiring user approval, the main obtains user plan approval (the main holds the Plan Mode tools).

> In other words, because a specialist lacks EnterPlanMode/ExitPlanMode and cannot do plan approval directly, it is replaced by **mailbox "plan proposal" → main review · reject · approve**.

### §3.4 Deployment-timing principles (4 items)

Applied at every teammate assignment. No bypassing via the AI's own judgment.

| # | Principle | Meaning |
|:-:|------|------|
| (a) | **Epic Planning = the main's responsibility** | Epic analysis / Story **outline** decomposition / user confirmation are all centered on the main + user dialogue. No teammate assignment. (Epic-level) |
| (b) | **Story Planning (Action decomposition) + orchestration = the main's responsibility** | On entering each Story, the Action-decomposition draft · finalization · user confirmation are all the main's. Thereafter Action execution = the main assigns and orchestrates specialists per the playbook procedure. |
| (c) | **The main orchestrates through the PR of one cycle** | main = the Epic-level orchestrator. The main runs the procedure through every Story + every Action + retrospective + Squash Merge + PR creation (the specialist = performs the Action only). |
| (d) | **User confirmation is at important decision points** | Autonomous progress by default. Call the user at a large decision (merging a shared branch / changing a non-goal / deleting a directory / entering an Epic) or an undecidable one (ambiguous either/or / risky assumption). |

> **Bypass — only an explicit user expression is allowed**: (a)(b)(c) are absolute mandates. (d) is signal-based, so no separate bypass is needed — a large-decision / undecidable signal is itself the user-call signal. (consistent with `gate-enforcement-default-on` — plugin rules/)

> **Code work = specialist team recommended by default (not blocked)**: a code-writing Action is **by default** assigned to a specialist teammate rather than done by the main directly (`delegation_mode: auto`). Meta · analysis · docs are `(direct)`. To pull a code job out with `(direct)`/`direct`, give a one-line reason. Recommended, not a mandate (hook deny). Criteria SSOT: `flow-procedure-action` §delegate_to judgment criteria.

> **Pre-check teammate tool availability** (before assignment — recurred 4 times in external-project retrospectives): if an Action requires a specific tool (shell · external MCP, etc. that a teammate may not be able to use), confirm before assignment that the teammate can use that tool. If it cannot → mark that Action (or the tool-dependent follow-up stage) `(direct)` (main performs) or add a one-line "the main does the follow-up". This preempts the infinite wait (§Hard Gate 2) caused by no response · tool absence.

---

## §4 Responsibility separation (flow management vs implementation)

| Responsibility | Main (flow management) | teammate (implementation) |
|------|:--------------------:|:---------------:|
| A-NNN.md management | ✅ | ❌ |
| delegate_to detection + teammate assignment | ✅ | ❌ |
| Executing its own procedure | ❌ | ✅ |
| Loading guides | ❌ | ✅ |
| Creating/modifying outputs | ❌ | ✅ |
| Completion notice (verify/commit timing) | ❌ | ✅ |
| Verification | ✅ | ❌ |
| Commit | ✅ | ❌ |
| Updating A-NNN.md status | ✅ | ❌ |
| Updating _story.md | ✅ | ❌ |
| Retrospective | ✅ | ❌ |

> **Principle**: teammate = **only the main work (implementation)**. Flow management (verify / commit / status / retrospective) is the main's responsibility.

---

## §5 Gray zones (Primary/Secondary explicit)

For cases where routing responsibility is ambiguous, make Primary (main responsibility) / Secondary (auxiliary verification) explicit:

| Gray-zone case | Primary | Secondary | Decision signal |
|---------------|---------|-----------|----------|
| main ↔ teammate delegation (delegate_to explicit) | **this guide** (assignment mechanism) | teammate's own procedure | A-NNN.md `delegate_to` value |
| implementation ↔ test (TDD pairing) | test-owning teammate (TDD enforcement) | implementation-owning teammate (implementation + its own sanity) | testability = implementability (the test owner's veto) |
| meta work (modifying flow resources) ↔ management | **this guide** (`(direct)` notation) | meta-authoring procedure | target = the flow resource itself |
| delegation between flow procedures | `flow` skill (Mode Detection) | this guide (assignment mechanism) | invoking subject = main vs procedure |
| delegation failure (teammate unassigned / area trespass) | **this guide** (fallback procedure) | issue-handling procedure (classification decision table) | failure classification (area trespass / no response / unassigned) |

> **Goal: 0 gray zones** — when a missing case is found in the table, add it immediately.

---

## §6 Hard Gate (enforcement mechanism)

### Hard Gate 1: delegate_to value verification (static grep)

| Verification | Expected result | On violation |
|-----|---------|---------|
| **(Case A — non-standard notation)** a `delegate_to` value with an uppercase / undefined teammate name | 0 | update A-NNN.md immediately (lowercase-kebab) |
| **(Case B — value entirely missing)** `grep -rn "delegate_to:[[:space:]]*$" <workspace>/**/A-*.md` | 0 | update A-NNN.md immediately (teammate name or `(direct)`) |
| a "verify/commit stage" notice exists in the teammate's completion report | all teammates pass | add the notice |

> The criteria for verifying the valid teammate-name list depend on the teammate definitions the project defines (in .claude/agents/).

### Hard Gate 2: delegation-failure fallback procedure

| Failure case | Fallback order |
|----------|--------------|
| `delegate_to` missing | auto-match (path/work signal) → load the guide directly → A-NNN.md Step → user confirmation |
| teammate unassigned | auto-match fallback + warning + retrospective Problem |
| teammate area trespass (executing flow management) | responsibility-separation table (§4) violation found → block immediately + retrospective |
| no response after delegation | main returns → failure analysis → retry or self-handle (fallback 2) |

### Hard Gate 3: review activation (right before commit)

- At the review stage right before commit, apply this guide's responsibility separation + persona input + essence attack
- On a finding, block the commit + fix the body

---

## §7 teammate MUST NOT

A teammate is **absolutely forbidden** to do the following (implementation responsibility only, no trespass into flow management):

| Forbidden | Reason | Correct handling |
|------|------|-----------|
| ❌ Run verification commands | verification is the main's (flow management) responsibility | work done → "verify/commit stage notice" |
| ❌ Commit (`git add` / `git commit`) | committing is the main's responsibility | work only, no commit |
| ❌ Modify A-NNN.md | document management is the main's responsibility | do not change status |
| ❌ Modify _story.md | document management is the main's responsibility | do not change status |
| ❌ Change out-of-scope outputs | exceeds the work scope | handle after the main's judgment |

**Correct completion procedure**:
1. Work done (outputs created/modified)
2. Notice: "Work done. Please proceed with the verify/commit stage."

---

## §8 Auto-match table (fallback when `delegate_to` is unspecified)

When there is no `delegate_to`, the main auto-matches by work signal / target path. **The concrete matching rules (which work signal → which teammate) depend on the playbook + the project's (.claude/agents/) teammate definitions**, so this skill specifies only the matching **procedure**:

**Matching rules**:
1. If `delegate_to` exists → that teammate (priority)
2. If not → look up the playbook mapping by work signal / path → the matched teammate
3. If not in the mapping either → the main loads the guide procedure directly (fallback 1)
4. If there is no guide either → the main executes per the A-NNN.md Step (fallback 2)

> 💡 An explicit `delegate_to` is recommended. Auto-match is for the fallback.

---

## §9 Notice message (at teammate assignment)

```
🔄 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**teammate assignment**: {teammate-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **Action info**:
- **Title**: {A-NNN.md title}
- **delegate_to**: {teammate-name} (lowercase-kebab)
- **Target**: {target path}

👉 **Next steps**:
1. The teammate follows its own procedure (implementation)
2. After completion, verify + commit + retrospective (the main's responsibility)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## §10 Error handling

| Situation | Handling |
|------|------|
| `delegate_to` teammate unassigned | warning + auto-match fallback |
| teammate work failure | main returns → failure analysis → retry |
| teammate trespassing into the flow-management area | forbidden by §7 MUST NOT + record retrospective |
| area trespass (a different work type found) | apply the issue-handling procedure classification decision table |

---

## §11 Related SSOT

- `gate-enforcement-default-on` (meta rule — the upper enforcement of this guide / plugin rules/)
- **The project (.claude/agents/)**: the actual concrete teammate (specialist) definitions — name · responsibilities · model · effort. **"Who does what" is the project (.claude/agents/); "how to delegate" is this skill.**
- `flow` (Mode Detection — the delegation entry point)
- issue-handling procedure (area-trespass classification + handling path)
