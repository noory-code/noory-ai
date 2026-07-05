# Core Concepts (CONCEPTS)

> ⚠️ **Status: provisional skeleton**. This document reflects the understanding agreed so far. It **keeps evolving through real-world validation + deep discussion via `debate-protocol`** (a self-improvement procedure). Items that are "unverified / up for discussion" are listed in §4 below — do not assert them as settled until confirmed.

---

## 1. playbook vs. guide/agents — "the 3 tiers of guidance"

A playbook is **the way of working per work type**, used on both planning (work-item breakdown) and execution (step guidance). It does not, however, carry the "concrete implementation method" — that belongs to the lower tiers.

```
playbook (flow)          "what, in what order"     — per work type (feature/bug/refactor/docs)
   ↓ when running each step
agents (layer experts)   "who does that step"      — defined by the project (e.g. domain/data/presentation owners)
   ↓ references
guide skill (concrete)   "how, with the framework" — technical-element implementation (e.g. model serialization / state-management API)
```

| | **playbook** | **guide skill** |
|--|-------------|---------------|
| What | per-work-type **flow** | **concrete implementation** of a technical element |
| Abstraction | higher — "what, in what order" | lower — "how to do it with the framework" |
| When | flow **work-item breakdown** (planning) + step guidance | **referenced when executing** a playbook step |

- **When planning**: the flow breaks work into Initiative/Epic/Story/Action along the playbook flow.
- **When executing**: the playbook guides which agents/guide each step references.
- **Boundary**: "in what order to build the domain layer (flow)" = playbook / "how to build that layer with a specific serialization / state-management library (implementation)" = guide·agents. (`playbooks/README.md` §playbook boundary)

> It is fair that a playbook feels like it "plays a guide-skill role" — but it is a **higher-level flow guide**, and the concrete implementation guide is a separate tier (the guide skill).

## 2. Agent Teams vs. expert Subagents — "mechanism and material"

The two are on **different axes**, so they are not duplicative.

| | **Agent Teams** | **Expert Subagent definition** |
|--|-----------------|--------------------------|
| What | **how to run** a team (lead + teammates, parallelism, mailbox, plan approval) | **what roles** to put on the team (validated responsibilities · personas) |
| Analogy | the assembler | the parts |

- Even when Agent Teams composes a team **dynamically**, **what** to compose (role definitions) must exist for quality to be stable (ad-hoc generation differs every time).
- **Even with Agent Teams off**, Subagents are used for **parallel invocation** via the Task tool — the definitions are useful independently of the mechanism.

> ⚠️ The exact behavior of Agent Teams (the automatic teammate-generation mechanism) is **subject to ground-truth inspection** — this document provisionally settles only the logic that "role definitions are needed independently of the mechanism".

## 3. RT runs default-on · single-branch mode (settled — established in real use)

- **RT (Red Team) runs default-on**: to stop reviews from being papered over with "self-inspection (naked eye)", every playbook's review/evaluation point enforces **independent RT adversarial review** (persona input + the 4 essence attacks: validity / responsibility / consistency / methodology) default-on. Rigor and independence are SSOT in the matrix (`flow-procedure-action` §RT intensity matrix) and `flow-verify-commit` Step 2.5 — only 0 RT *runs* is forbidden (rigor is tuned to the nature of the work). **Key insight**: RT must fire **during the work**, not after, to catch defects a self-review cannot see.
- **Single-branch mode (T5)**: the work hierarchy (Initiative/Epic/Story) does not always have to fork a sub-branch. If everything is meta / small / single-domain, track boundaries on **one branch** with `[epic-N][US-N][A-N]` tag commits, and state the tier merge (Squash · `--no-ff`) as "not applicable" (no faking a merge that never happened). The integration *gate* (whether) = `flow-completion` / *strategy* (method) = `flow-branch`, a **two-axis split** — this blocks the defect where the same criterion, duplicated across procedures, gets "patched in only one place".

## 4. Unverified / up for discussion (stage B — settle after validation)

- **Definition granularity**: how far to pre-define expert Subagents vs. leave to on-the-fly generation (consistency vs. flexibility trade-off) → settle after real-use evidence.
- **Agent Teams real behavior**: how the auto-composition mechanism uses the definition pool → ground-truth verification.
- **playbook ↔ agents call path**: the concrete interface by which a playbook step calls agents → observe in real use.
- On settling, promote these §4 items into the §1/§2 body and clear the "provisional" marker.

## 5. The 7 verification/evaluation types — what is measured where (summary)

"Verification / evaluation / verify" is scattered across 7 things and is easily confused. This one table summarizes what is measured where and what is hook-enforced (ground-truth — cross-checked directly against `flow-verify-commit` · `verify-before-assert` · `quality_gate_cli` · `flow-completion` · `debate-redteam` · `flow-retrospective`).

| # | Concept | What it measures | Enforcement |
|---|------|------------|------|
| 1 | Action verification | Does the implementation match the AC (just before commit) | Procedure Hard Gate |
| 2 | Ground-truth inspection before asserting | The basis for an assertion (no guessing) | Text rule |
| 3 | Quality gate | Project test/lint pass | **The execution tool of #1** (not a standalone type) |
| 4 | Completion determination | Unit completion criteria met | **hook (auto-block)** |
| 5 | Adversarial review (R1/R2/R3) | Defects in plan / code / retrospective | Text procedure (cross-cuts planning / #1 / #6) |
| 6 | Retrospective | *How* the AI worked | **hook (enforced)** |
| 7 | Outcome evaluation | Whether the result was actually *good* / rule-compliance rate | **none (blank — unimplemented, §4-type)** |

**Summary points**:
- **Not overlaps**: the only real duplication is #1⊃#3 (the quality gate = the execution tool of action verification). #5 is not a duplicate but a cross-cut that *rides on* planning / #1 / #6.
- **Enforcement asymmetry**: the *existence* of docs and retrospectives is enforced by #4 and #6 via hooks, but result *quality* (#7) is not even measured.
- **#7 blank = the core of "evaluation is weak"**: there is no place to measure result quality or rule-compliance rate. Creating one is **follow-up work gated on measurement data** (same class as the §4 unverified items) — route it to the internal board queue (`retro-processing` backlog convention).
