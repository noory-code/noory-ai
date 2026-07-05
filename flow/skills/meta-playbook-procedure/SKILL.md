---
name: meta-playbook-procedure
description: "Procedure for writing/modifying a playbook. Write a work-type (bug/feature/refactoring/docs/retro-processing, etc.) playbook to the README 7-element writing standard + absorb existing procedures (process-flow style) + apply the work-type-primary / methodology-variant principle. Reference when creating or improving a playbook."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.0
---

# playbook writing procedure

A procedure document for creating/modifying a playbook (the way of working per work type). Peer to the writing procedures (`meta-*-procedure`) for Skill/Rule/Prompt/Agent — it fills in the writing procedure for playbooks.

> **SSOT separation**: the 7-element writing-standard format = the responsibility of `playbooks/README.md` (cited by this procedure). playbook **selection** = `flow-playbook-selection`. This procedure = playbook **writing·modification** (when/how to build it).
> **SSOT standard-vocabulary parity**: persona/Layer/Phase/unit notation cites the plugin rules/ standard-vocabulary dictionary. No coinages.

## Scope (gray-area declaration)

| Gray-area case | Primary | Secondary |
|---------------|---------|-----------|
| playbook writing timing/order/absorption (when·how to build) | **meta-playbook-procedure** | `playbooks/README.md` (7-element standard) |
| 7-element notation format / verification method | `playbooks/README.md` | **meta-playbook-procedure** (confirm the writing procedure) |
| playbook selection (which playbook for the work) | `flow-playbook-selection` | — |

## Core principles (playbook writing)

1. **Primary work-type classification**: 1 playbook = 1 work type. Methodology is a variant (an option within the feature work type).
2. **7 elements (cite the README)**: frontmatter / procedure / AC format / Hard Gate / feedback-loop location / violation handling / review·assessment point.
3. **Absorb existing procedures**: if a work type has an existing process flow (e.g. 7-stage/9-stage, etc.) · checklist, absorb those stages into the playbook `## Procedure` (record the source).
4. **Placement**: general flow = plugin `playbooks/` / specialized = project `.flow/playbooks/` override.

> 🚩 **Official position (Q2 decision — work type vs layer)**: the primary classification axis for a playbook is **fixed as work type**. The layer (Domain/Presentation/Data) is not raised as a separate playbook axis; it is expressed as a **variant within the feature work type** (`layered-domain-first`).
> - **Rationale (orthogonal axes)**: work type ("what kind of work") and layer ("which code layer") are mutually orthogonal axes. Of two orthogonal axes only one can be primary, and **work type is more universal** — every task has a kind (bug · docs · deploy, etc.), whereas layers exist only for code work. If layer were made primary, bug · docs work would have no playbook to go to.
> - **Answer to the unease ("the layer becomes invisible")**: the unease that in Clean Arch, etc., development converges into a single `feature` is resolved by absorbing the layer into `feature`'s **standard variant menu** (layer-ordered development) instead of splitting it out as an axis.
> - **Rejected**: promoting layer to a playbook axis (orthogonal-axis confusion + the cost of reorganizing 12 playbooks). origin: Initiative `initiative-flow-hardening` Epic 2 US-001 (debate decision, 2026-06-05).

## Resolution procedure

### Step 1: Identify the work type (new vs modification)
- Confirm **which work type** the playbook to build/fix is (bug/feature/refactoring/docs/retro-processing, etc.).
- If it is a methodology (tdd/bdd/prototype), fold it into the (feature) work type as a variant; do not create a separate playbook.
- Existing playbook present → modify / absent → create.

### Step 2: Absorb existing procedures (block duplication)
- Identify that work type's existing procedure (process flow / checklist / guide) (`grep`/`ls`).
- Absorb those stages as input to the playbook `## Procedure` — do not rewrite the flow.
- Record the absorption source in a comment/note (which stage came from where).

### Step 3: Write the 7 elements (README standard)
- Apply `playbooks/README.md` § the 7-element writing standard as-is. Accompany each element with a verification method (grep/ls).
- **Explicitly state** the review·assessment / feedback-loop slots (beware of omission when compressing — README §7).

### Step 4: Decide placement (general vs specialized)
- Universal work-type flow → plugin `playbooks/{...}/` (adhere to the generality principle: no framework names in the body).
- Project-specialized (architecture/domain) → `.flow/playbooks/` override (specialization allowed).

### Step 5: Verification
```bash
# 7 elements present
grep -E "^name:|^## Procedure|## AC format|HARD GATE|## Feedback loop|## Violation handling|## Review·assessment point" {playbook}.md
# work-type-primary (no new playbook for a methodology as a work type) — confirm the work-type name in the frontmatter
grep -E "^name:|^description:" {playbook}.md
```

## Project override writing pattern (bundle → project derivative)

The standard pattern for when a project adapts (overrides / derives) a bundled playbook into its own. `feature.md` is the exemplar, but that pattern was not written down and had to be rediscovered each time — this blocks that. (origin: downstream dogfooding Epic `playbook-override` — verified writing of 9 overrides. The config-time procedure SSOT = `flow-config` §3-2-B)

1. **Preserve the bundled flow (no rewriting)**: leave the bundled playbook's procedure order · Hard Gates as-is. An override is not rewriting the flow but **wiring up project assets to each stage**. Rewriting the flow description at length causes duplication · drift.
2. **Wire up project skills/agents to each procedure stage after ground-truth inspection**: perform ground-truth inspection (exhaustively) of `.claude/skills` · `.claude/agents`, etc., and explicitly wire up `delegate / reference / artifact` to each stage (e.g. `① Domain design — delegate: agent-dev-domain / reference: guide-domain-design / artifact: …`).
   - **Ground-truth-inspection method branch (no guessing)**: **external assets** (CI flows/external systems/APIs — contracts outside the code) **require a user interview** (no SKILL.md → no guessing) / **internal skills** (`.claude/skills`) are **sufficiently covered by ground-truth inspection of SKILL.md · the directory**. Detail: `flow-config` §3-2-B.
3. **A code-generation playbook requires stage-0 cross-cutting wiring**: place a "0. Confirm structure·location·naming" stage ahead of all layers — wire up the structure/location/naming guides (`guide-architect-structure` · `-location` · `-conventions` style) + the app `CLAUDE.md`. Omitting it makes output locations · naming drift (an actually-occurring defect). Also wire up structure/location/naming violation checks into the review·assessment point.
4. **Preserve·state the work-type-specific Hard Gate**: each work type has its own gate — refactor = behavior preservation (characterization tests) / bug = reproduction · regression / docs = source · consistency / deploy = write the rollback first, etc. When overriding, don't drop this gate while compressing.

> Detailed config procedure (derivative scaffold / exhaustive skill discovery / 7-element draft) is `flow-config` §3-2-B. This section is the writing-procedure SSOT for that pattern.

## Verification
- The written playbook has all README 7 elements present (`grep` → 7 pattern hits)
- (when writing an override) adheres to the above 4-item pattern — bundled flow preserved / per-stage skill wiring / stage-0 cross-cutting (code generation) / work-type Hard Gate
- 1 playbook = 1 work type (0 separate methodology playbooks created)
- Existing process-flow absorption source recorded
- 0 framework-specific names in a general playbook body (code blocks excepted)

## Related SSOT
- `playbooks/README.md` (7-element writing standard + evolution mechanism)
- `flow-playbook-selection` (playbook selection — not writing)
- `meta-skill-procedure` / `meta-rule-procedure` / `meta-prompt-procedure` / `meta-agent-procedure` (peer writing procedures)
