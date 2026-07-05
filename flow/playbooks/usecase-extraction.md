---
name: usecase-extraction
description: Reverse-documentation work type — analyze code/specs → extract use cases → verify code↔document bidirectional parity. The direction is code→document (opposite of docs, which writes forward), and parity verification is the core gate
---

# usecase-extraction (reverse documentation — code→document)

A work type that reads the actual behavior from existing code/specs to **extract use cases**, then **verifies bidirectionally** that the extracted output does not diverge from the code. Unlike `docs`, which *writes* a document from intent/planning (direction: person→document), this type **derives a document in reverse from already-implemented behavior** (direction: code→document). Therefore the value of the output is judged not by "reads well" but by **parity with the code**.

## Applies to

- When you must recover use cases (actor, trigger, flow, outcome) from code/specs that have rolled along without documentation
- When you must document the actual current behavior before a migration/handover/audit
- When there is a suspicion that code and existing documents have diverged, and parity must be re-confirmed
- Not applicable:
  - *Writing* a new document from intent/planning (direction is person→document) → `docs`. This type differs from docs in that its direction is **code→document** and its gate is **parity verification**.
  - Work that creates new behavior → `feature` / defect fixes → `bug` / behavior-preserving structural improvement → `refactor`

## Procedure

1. **Identify scope and sources** — fix the boundary of the target code/spec to extract from and the entry points (actors, external interfaces) / Output: target source list + entry-point inventory
2. **Trace behavior** — follow the flow from each entry point and read the actual branches, state changes, and external effects to collect behavior / Output: per-entry-point behavior-trace notes (input → branch → outcome)
3. **Extract use cases** — structure the trace notes into actor, trigger, main flow, alternative/exception flows, and outcome / Output: use-case draft (per UC, including cited code-evidence locations)
4. **Evidence back-trace verification (document→code)** — confirm in reverse that each UC item reduces to an actual code location (a statement without evidence = a guess) / Output: UC↔code evidence mapping table (source location per UC item)
5. **Coverage verification (code→document)** — confirm that none of the code's entry points/major branches are missed by every UC / Output: coverage checklist (uncovered branches = 0, or an explicit reason for intentional exclusion)
6. **Discrepancy reconciliation iteration** — resolve the divergences (over-statement/omission/contradiction) surfaced in 4/5 by re-checking the code, repeating until bidirectional parity / Output: reconciled use cases + a record of 0 residual discrepancies
7. **Handover** — hand over the parity-passed use-case document together with a review request / Output: finalized use-case document + attached evidence mapping

> Language/framework-specific code-reading methods (deriving call graphs, state-flow analysis, etc.) and domain-model interpretation are delegated to the analysis procedure **supplied by the project** (the project's `.claude/agents/`). This playbook defines only the generic reverse-documentation flow.

## AC format

Each use-case item (or parity judgment) is written with 5 fields.

- **Given** — premise (target source scope / entry point / trace starting state)
- **When** — action (run that flow, or verify the extracted item)
- **Then** — expected result (the extracted UC matches the code behavior / evidence location exists)
- **Verification method** — code back-trace (document→code) + coverage check (code→document). Where possible, cross-check by reproducing the behavior (run/observe)
- **Pass/fail criteria** — every flow of the UC reduces to code evidence + uncovered branches 0 = PASS / a statement without evidence, or an uncovered branch exists = FAIL

> No unmeasurable "roughly this kind of feature" extraction. Every UC item is accompanied by its code-evidence location.

Example (domain-agnostic — extracting a credential-verification flow):

- **Given** — authentication module source scope + verification entry point
- **When** — back-trace the extracted UC "valid credential → returns success state" to the code
- **Then** — that branch/return exists at an actual code location, and every verification branch of the code is covered by some UC
- **Verification method** — compare against the UC↔code evidence mapping table + coverage checklist + where possible, reproduce the input
- **Pass/fail criteria** — evidence mapping 100% + uncovered branches 0 = PASS / missing evidence or uncovered branches ≥1 = FAIL

## Hard Gate

> **HARD GATE**: Handover forbidden when code↔document bidirectional parity verification has not passed
> On failure: procedure 7 (handover) is blocked — if an extracted UC does not match the actual code behavior (statement without evidence / uncovered branch / contradiction), roll back to procedures 4/5/6 and secure parity (mandatory)
> Bypass: only on the user's explicit expression (skip / move on / bypass / skip over)

> **HARD GATE**: Writing a UC item without code evidence is forbidden
> On failure: block items without cited evidence in the procedure 3 (extraction) output — a speculative statement is not recognized as a UC (it must reduce via procedure 4 back-trace)
> Bypass: only on the user's explicit expression

## Feedback loop location

The "verify → feedback → fix → re-verify" loop of this playbook:

1. **Procedure 6 (discrepancy reconciliation iteration)** — the core loop. Back-trace/coverage verification (verify) → divergence analysis (feedback) → code re-check/UC fix → re-verify. Repeat until bidirectional parity
2. **Procedure 4 (evidence back-trace)** — early feedback in the document→code direction (early blocking of guesses)
3. **Procedure 5 (coverage check)** — omission feedback in the code→document direction
4. **Procedure 7 (handover review)** — reviewer feedback → fix → re-review

> The feedback of this type is **bidirectional** — whereas docs is a one-directional (material→document) verification, here both document→code (evidence) and code→document (coverage) must be closed for the loop to complete.
> The loop above is a verification loop **within the work flow**. Improving the playbook itself is the responsibility of retrospective-based evolution (the `retro-processing` work type) — outside this playbook's scope.

## Review/evaluation points

- **Review**: procedures 4/5 (evidence back-trace / coverage check — verifying the essence of parity) + procedure 7 (handover review request). Prioritize speculative statements, omitted branches, and contradictions. Delegate when the project supplies a review teammate. **RT running default-on** (strength/independence = README §7 + RT strength matrix). RT essence attack: evidence-free speculative UCs, coverage omissions, code↔document contradictions.
- **Evaluation**: the procedure 3 UC 5 fields (Given/When/Then) satisfied + evidence mapping 100% + uncovered branches 0 = output evaluation criteria. Bidirectional parity passed = satisfied.
- `flow-procedure-story` §7-2 Review/Evaluation Hard Gate enforces execution of the above points.

## Violation handling

- An evidence-free speculative UC / a residual uncovered branch / a statement that contradicts the code = block or request supplementation
- A bypass is allowed only on the user's explicit expression (skip / move on / bypass / skip over)
- A bypass fact = mandatory record in the retrospective Problem section (in particular, a parity-unverified handover must be noted as a downstream risk)
