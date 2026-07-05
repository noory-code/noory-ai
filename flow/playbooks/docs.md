---
name: docs
description: Documentation/spec authoring task type — gather sources (material) → structure → write → review. Includes the requirement/planning spec variant
---

# docs (documentation/spec)

The task type for producing documents/specs (README / manual / usage guide / USECASE / design/requirement spec). Start from **sourced material**, structure and write it, and confirm consistency through review. Work with no change to code behavior.

## Applies to

- Authoring/updating documents, manuals, guides, specs
- Requirement/planning specs (→ `## Variant: requirement/planning spec`)
- Not applicable: code-behavior changes (→ `feature`/`bug`/`refactor`)

## Procedure

Base flow (documentation/spec authoring):

1. **Define scope and audience** — what / for whom you write it + completion criteria / Output: document goal (scope + audience + completion criteria)
2. **Gather material (sources)** — gather supporting material together with its source (code / existing docs / interviews, etc.) / Output: list of sourced material
3. **Structure** — design the table of contents and flow (the order the reader follows) / Output: structure (TOC)
4. **Write** — write the body per the structure (link each assertion to its source) / Output: draft
5. **Review** — check accuracy, completeness, consistency → apply feedback → re-review / Output: reviewed document
6. **Apply/publish** — apply the finalized document to its target location / Output: published document

> Documentation tools, notation conventions, and publish location are delegated to the procedure **the project supplies**. This playbook defines only the universal documentation/spec flow.

## Variant: requirement/planning spec

**Planning** work where requirements are unclear or stakeholder agreement is needed follows the variant below (the interview/handoff gates apply only to this variant — not needed for ordinary documents).

| Stage | Difference (vs base) |
|------|------------------|
| ① Interview | Instead of scope definition, gather requirements/pain points via stakeholder interviews (material source = interviews) |
| ② Organize requirements | Prioritized requirement list |
| ③ Visualize flow | Low-fidelity expression of the core flow (wireframe/flow — the expression method is project-supplied) |
| ④ Write spec | Flow-based feature spec (including ACs) |
| ⑤ Review | Iterate until stakeholder agreement |
| ⑥ Handoff | Pass the finalized spec + acceptance criteria to the implementation task type (`feature`) |

> Variant-added gates — **no spec authoring without requirement gathering (interview)** / **no handoff without stakeholder agreement**. (Other spec methods like spec-by-example / design-doc-first also follow this variant's gather-material→structure→review skeleton.)

## AC format

Write each document/spec item with 5 fields.

- **Given** — reader context/premise (or requirement context)
- **When** — the situation in which the reader uses the document (or the requirement-fulfillment scenario)
- **Then** — expected result (the reader achieves the goal / the requirement is met)
- **Verification method** — review agreement or usability observation (a spec is checked against acceptance criteria)
- **Success/fail criteria** — completion criteria met + review agreement PASS / unsourced assertion or no agreement FAIL

> No unmeasurable ACs like "works well / looks fine".

Example (domain-agnostic — a setup guide):

- **Given** — a reader using the feature for the first time
- **When** — they perform the setup following the guide
- **Then** — setup completes with no extra guidance
- **Verification method** — review agreement + (if possible) observing a new user follow along
- **Success/fail criteria** — completes with no sticking point PASS / unsourced description or a sticking point occurs FAIL

## Hard Gate

> **HARD GATE**: No unsourced assertions (no writing body assertions without material gathering ②)
> On failure: procedure ④ (write) is blocked — link each assertion to a source (code/doc/interview). No speculative descriptions
> Bypass: only on the user's explicit expression (skip / move on / bypass / skip over)

> **HARD GATE**: No apply/publish/handoff without review (procedure ⑤)
> On failure: procedure ⑥ is blocked — accuracy/consistency review must come first (the planning variant requires stakeholder agreement)
> Bypass: only on the user's explicit expression

> **HARD GATE**: Do not close ground-truth-inspectable document consistency with a "split off later" placeholder
> On failure: stale references, versions, and link consistency are ground-truth-inspected with `grep` and corrected within that task. Defer only when ground-truth inspection is impossible (`no-defer-blockers` consistency)
> Bypass: only on the user's explicit expression

## Feedback loop locations

1. **Procedure ⑤ (review)** — the core loop. Present draft (check) → feedback → revise → re-review. Iterate until agreement
2. **Procedure ② (material gathering)** — an early loop for confirming sources (re-gather when evidence is insufficient)

> These are verification loops within the work flow. Improving the playbook itself is the responsibility of retrospective-based evolution (`retro-processing`) (out of scope).

## Review/evaluation points

- **Review**: procedure ⑤ (accuracy/completeness/consistency review / stakeholder agreement in the planning variant). Delegate when the project supplies a review teammate. **RT active default-on** (strength/independence = README §7 + RT strength matrix). RT essence attacks: source consistency · stale figures · name/path accuracy · omissions.
- **Evaluation**: completion criteria (defined in ①) met + source consistency + review agreement = the output evaluation criteria.
- `flow-procedure-story` §7-2 review/evaluation Hard Gate enforces execution of the points above.

## Violation handling

- Unsourced assertion / unreviewed publish / unagreed handoff = block or request remediation
- Bypass allowed only on the user's explicit expression + obligation to record it in the retrospective Problem section
