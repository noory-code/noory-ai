# playbooks/

Library of per-work-type ways-of-working playbooks (work-type first — 1 playbook = 1 work type).

> playbook = **the rulebook the AI must follow (a finished product)**. It defines the work flow + AC format + feedback loop + Hard Gate self-containedly. Usable as-is without any adaptation (`_initiative.md` confirmed design — completeness principle).

> 📋 **Reinforcement-candidate backlog + derivation menu**: `CANDIDATES.md` (per-work-type candidate methods). A project can also **derive** a playbook from its own way of working via `/flow-config` (Phase 3-2) (scaffolding a `.flow/playbooks/` draft).

## Structure (work-type first — flat)

| Element | Meaning | Definition location |
|------|------|----------|
| **playbook (per-work-type working method)** | Per-work-type way of working — feature / bug / refactor / docs, etc. | `playbooks/{playbook}.md` |

> ⚠️ One playbook is **selected per work item** — do not register playbooks as Claude Code rules (always-on loading would apply feature/bug at once → conflict).

## playbook boundary — what it holds / what it does not

A playbook holds the **flow** only. Per-layer concrete implementation is the job of agents/reference skills (to prevent confusion).

| Held in the playbook (flow) | Not held → agents / reference skills |
|--------------------------|----------------------------------|
| Step order / Hard Gate / feedback loop | Per-layer concrete implementation (model/state management/DB adapter) |
| "What, in what order" | "How, via the framework API" |
| Per-work-type way of working | Domain / language-specific procedures |

> Judgment question: "Is this content a work **flow**, or a specific **implementation method**?" → if implementation, take it out of the playbook and delegate to agents (project-defined) / reference skills.

### Floor (bundle) vs ceiling (override integration wiring)

A playbook operates at two levels depending on project maturity:

| Level | What | When |
|------|------|------|
| **Floor (bundle playbook)** | General flow + gates + **abstract delegation** ("delegate to project agents/skills") | Projects with no skills — works on its own (completeness principle) |
| **Ceiling (project override)** | Same flow + gates + **explicit wiring to project skills** (each step specifies the actual skill/agent via `delegate:`/`ref:`) | Projects that have skills — *integrates* existing skills to beat the bundle |

> **Key**: in a rich project (skill-abundant), the value of a playbook is **not adding a new flow but *integration-wiring* the already-present skills into one way of working**. Rewriting the flow alone would **duplicate** the project skills. An override is thin — "order + gates + skill pointers" — an integration recipe. (config Phase 3-2.5 generates this wiring — `commands/flow-config.md`)

## Directory structure

```
playbooks/{playbook}.md        # plugin default (finished product)
.flow/playbooks/{playbook}.md  # project override (optional — name clash = project wins)
```

Application: on entering Plan Mode, Read `.flow/settings.json` → **select a playbook by work type** (feature/bug/refactor/docs → the matching playbook). If nothing fits, **`general`** (general fallback). If an override (`.flow/playbooks/`) exists, it wins. Details: `flow-playbook-selection`.

> ⚠️ **No fixed `default`** (v0.3.1 — user insight): the AI selects a playbook each time by work type. The fallback for unclassified work is not a fixed specific playbook (default) but the general-purpose `general` playbook.

## Authoring standard

Every playbook includes the following 7 elements. **Each element comes with a notation format + a verification method (grep/ls)** — because prose alone leaves a later author unable to judge what to produce, breaking the completeness principle.

### 1. frontmatter

```yaml
---
name: feature                   # playbook name (same as filename = work type)
description: Feature development flow (test-first)   # 1-line summary
---
```

**Verify**: `grep -E "^name:|^description:" {playbook}.md` → 2 hits

### 2. Procedure (`## Procedure` section)

Define the work flow as steps. Each step = **number + action + deliverable (verifiable artifact)**. Step order = work order.

Notation format (example):

```markdown
## Procedure

1. **Design** — requirements → decide interface/structure / deliverable: design note (interface signatures)
2. **Test Case definition** — Given/When/Then / deliverable: AC list
3. **Test code (Red)** — write failing tests / deliverable: test file
...
```

> **Step wiring on override (ceiling)**: append `delegate: <agent>` / `ref: <skill>` pointers to the same step to integrate project skills (§floor/ceiling · config Phase 3-2.5). The bundle (floor) leaves it as abstract delegation — the flow format is identical, only the presence of pointers differs.

**Verify**: `grep -E "^## Procedure" {playbook}.md` hit + each step has a "deliverable:" notation (`grep -icE "(deliverable|output):" {playbook}.md` → matches the number of steps; `deliverable:` is the standard, `output:` is a legacy synonym still present in some bundled playbooks)

### 3. AC format (`## AC format` section — measurable)

Each AC has 5 fields: **Given** / **When** / **Then** / **Verification method** (grep·ls·test or manual observation) / **Pass/fail criteria** (quantitative or clearly qualitative).

> Immeasurable ACs like "works well / looks fine" are banned. Each playbook includes the 5-field definition + **one domain-agnostic example** so authors do not diverge.

**Verify**: `grep -E "Given|When|Then|Verification method|Pass/fail" {playbook}.md` → 5 patterns hit

### 4. Hard Gate (`## Hard Gate` section — notation format enforced)

Non-bypassable enforced points. Notation format:

```markdown
> **HARD GATE**: [condition]
> If unmet: [blocking action — block the next step]
> Bypass: only on the user's explicit expression (skip / move on / bypass / skip over)
```

**Verify**: `grep "HARD GATE" {playbook}.md` → ≥1 hit

### 5. Feedback-loop location (`## Feedback-loop location` section — required)

Each playbook specifies **which step it places** the "verify → feedback → fix → re-verify" loop at. (Core of the Initiative's evolution value — the point where the way of working self-checks.)

**Verify**: `grep -E "^## Feedback.?loop" {playbook}.md` → hit (missing section = violation; covers both the `Feedback-loop` and `Feedback loop` spellings present in bundled playbooks)

### 6. Violation handling (`## Violation handling` section)

- An artifact that does not follow the procedure = block or request rework
- A bypass is allowed only on the user's explicit expression + mandatory record in the retrospective Problem section

**Verify**: `grep "## Violation handling" {playbook}.md` → hit

### 7. Review/evaluation points (`## Review/evaluation points` section — required)

Specify **when the artifact is reviewed and by what it is evaluated**. Declare where in the flow you place review steps (design review / code review / PR review, etc.) and the artifact evaluation criteria (AC-satisfaction judgment). The review/evaluation Hard Gate in `flow-procedure-story` §7-2 **reads this declaration and enforces whether it runs** — without a declaration, the gate does not know what to enforce.

> ⚠️ **Omission warning**: when deriving (override), it is easy to drop review steps while compressing the procedure (Epic 5 third demonstration — the clean-arch derivation omitted `feature`'s (then tdd) design/PR reviews). This element is the explicit slot that blocks that omission.

#### RT run default-on (no naked-eye pass — CRITICAL)

The "review" in review/evaluation points must include **running the RT (Red Team) mechanism** (persona input + 4 essence-attack priorities validity/responsibility/consistency/methodology — `debate-redteam` §R1/R2 call-payload standard) default-on. **A naked-eye (casual) review that does not apply the RT payload does not satisfy this element.**

- **Intensity/independence SSOT (this section does not redefine — it only enforces that zero runs is banned)**: RT intensity (strong/medium/weak) and R1/R2/R3 on/off are SSOT'd by `flow-procedure-action` §RT intensity matrix. The self-review vs independent-agent boundary follows `flow-verify-commit` §Step 2.5 (R2 spec; its 5-case matrix SSOT is `flow-planning-action` §R1 spec — cases 1–3 self OK / cases 4–5 · code work mandate an independent agent / no independent-agent environment provided = same-payload self fallback). This section follows that matrix but only enforces **"zero RT runs banned"** (`gate-enforcement-default-on` consistent).
- **R1/R2 independence**: follows the `debate-redteam` R1/R2 matrix — **R1 Epic=main immersion**, Story/Action=independent agent / R2=independent agent (self only for the matrix-allowed cases).
- **Misclassification warning (Epic 7 origin)**: a change to plugin assets (skills/rules/playbooks/docs) is classified not as "docs/format (weak · R2 △)" but as **"architecture/meta (manager)" = R2 ✅ mandatory**. Epic 4·5·6 misclassified meta work as 'docs · weak' and skipped R2 → the RT found many stale/wrong-install-name issues right before PR (the cost of a naked-eye pass). Since classification decides whether RT runs, classify conservatively (strong).

**Verify**: `grep -E "^## Review" {playbook}.md` → hit (missing section = violation) · `grep "RT run" {playbook}.md` → hit (missing RT-run declaration = violation)

## Generality principle

A playbook holds **only project-agnostic universal flow**.

- Use only universal terms in the body ("test framework" / "implementation" / "interface")
- Framework/language-specific names (Flutter / Spring / React, etc.) **must not appear in the body procedure**. Unavoidable example/anti-pattern explanations are quoted only inside code blocks
- Concrete domain analysis (layer composition / state management, etc.) and language specialization are delegated to the analysis procedures the **project supplies** (project `.claude/agents/`)

**Verify**: 0 framework-specific names outside code blocks — `grep -nE "Flutter|Spring|React|Riverpod|Django" {playbook}.md`; PASS if the results are not outside a code block (```)

> **Application scope (bundle vs override)**: this generality principle is enforced on **plugin bundle** playbooks (for project-agnostic reuse). A **project override** (`.flow/playbooks/`) is specific to that project, so **framework/domain specialization is allowed** (e.g., a project override may use specific framework terms). But the override also keeps the § playbook boundary above (flow vs implementation).

## Completeness principle

A plugin-provided playbook is **usable as-is without any adaptation** (empty formats banned — the 7 elements above must have notation format + verification). A project customizes via a `.flow/playbooks/` override when needed.

## playbook evolution mechanism (Φ4 self-improvement)

A playbook is not a fixed asset but **an asset that evolves through accumulated retrospectives**. When the following signals accumulate in the retrospective (`flow-retrospective` Part 3), classify it as a playbook candidate:

| Candidate | Criterion (measurable) | Handling |
|------|----------------|------|
| **New candidate** | The same work pattern does not fit an existing playbook and repeats **≥3 times** | Review writing a new playbook (apply the 7-element authoring standard) |
| **Fix candidate** | Applying an existing playbook **fails ≥2 times** (procedure unfit / feedback loop missing, etc.) | Review fixing that playbook's procedure/Hard Gate |

> **Classification origin**: the **playbook candidate** classification in retrospective Try (`flow-retrospective` Part 3-1). This README is the evolution-procedure SSOT; retrospective is classification + cross-ref.
> **Actual new/fix timing**: Epic retrospective → asset-update step (operational accumulation). This mechanism is the criterion for "when it becomes a candidate."

## Procedure → Action decomposition guide

When decomposing a playbook's `## Procedure` steps into flow Actions:

- **Feedback-loop points become independent Actions** — the verification/review steps specified in the playbook's `## Feedback-loop location` are placed as separate Actions to secure visibility. (Bundling the whole procedure into one Action loses the feedback loop.)
- **Consecutive-output steps can be merged** — non-feedback-loop consecutive work steps (e.g., design → interface definition) may be merged into 1 Action (same artifact / sequential dependency / < 2 hours).
- Judgment criterion: "Is this step a verify → feedback → fix loop?" → if Yes, an independent Action.

> **origin (issue 3)**: in the early PoC, the 6 steps of `docs` (then interview-first) were merged into 1 Action → reduced feedback-loop visibility. This guide blocks that.

## Status

Work-type first — 1 playbook = 1 work type (flat). A methodology is a variation within a work type. (Q2 official stance — work type vs layer are orthogonal axes and work type is more universal: `skills/meta-playbook-procedure` §core principles. Layer is not a separate axis but is absorbed as a feature variation.)

- `feature` — feature development (test-first default + methodology variations: BDD/prototype/spec-first/contract-first/layer-first)
- `refactor` — refactoring (pin behavior with characterization tests → change incrementally)
- `bug` — bug fixing (reproduce → failing test → fix → regression, regardless of scale)
- `docs` — docs/spec authoring (material gathering → structuring → writing → review / requirement-and-planning spec variation)
- `retro-processing` — retrospective processing (collect retrospectives → repeated patterns → improvement plan → review → apply)
- `research` — investigation/research (gather sources → cross-verify ≥2 independent sources → structure → indexing/handoff)
- `usecase-extraction` — reverse documentation (analyze code/spec → extract use cases → verify code↔doc two-way consistency)
- `qa` — quality verification (risk-first allocation → exploratory test charter → defect logging → pass judgment)
- `security` — security (threat modeling → mitigation AC → implementation → security check → merge)
- `deploy` — deploy/infra (write runbook/rollback first → plan → review → incremental apply → observe → expand/rollback)
- `plugin-dev` — plugin self-development (rule/skill/hook/command changes + full-regression obligation + propagation obligation (rule sync / version bump) + dogfood — a single meta-work flow)
- `general` — general fallback (when the work type is unclassified. understand work→plan→execute→verify→retrospect)
