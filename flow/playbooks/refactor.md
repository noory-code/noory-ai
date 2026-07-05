---
name: refactor
description: Refactor work type — pin behavior with characterization tests, then change incrementally in small units (behavior preserved)
---

# refactor (refactoring)

A work type that improves internal structure while preserving behavior. Before changing, pin the current behavior with tests (characterization), then change incrementally in small units.

## Applies to

- Structural improvement of existing code that has no or insufficient tests
- Cases that change only internal structure while preserving behavior
- Not suitable for: new features (→ `feature`) / changes that alter behavior itself (→ `feature`) / defect fixes (→ `bug`)

## Procedure

1. **Analyze current code** — grasp the target's current behavior, dependencies, and impact scope / Deliverable: analysis notes (impact scope)
2. **Add characterization tests** — write tests that pin the current behavior as-is (pre-improvement behavior = baseline) / Deliverable: characterization tests (passing)
3. **Break into change units** — decompose the large improvement into small, safe units / Deliverable: list of change units
4. **Incremental change + re-verify** — change one unit → rerun characterization tests (confirm behavior preserved) → next unit. Repeat / Deliverable: changed code + tests kept passing
5. **Tidy the structure** — remove duplication, clean up naming (behavior unchanged) / Deliverable: tidied structure
6. **PR** — change units + evidence of behavior preservation (tests) + review / Deliverable: Pull Request

> Concrete domain analysis and language-specific test authoring are delegated to the analysis procedure **supplied by the project**. This playbook defines only the general refactoring flow. If the project defines refactoring levels (pattern fix / directory migration / structural migration, etc.), follow that stage's criteria.

## AC format

Specify each change unit's "behavior preservation" in 5 fields.

- **Given** — input/state before the change
- **When** — run the same behavior after the change
- **Then** — the same result as before the change (behavior preserved)
- **Verification method** — rerun the characterization tests (same pass before and after)
- **Pass/fail criteria** — all characterization tests keep passing = PASS / any break = FAIL (behavior changed)

> No unmeasurable AC such as "works / looks fine".

Example (domain-agnostic — a price-calculation function):

- **Given** — identical input (quantity + unit price)
- **When** — run the calculation after refactoring
- **Then** — the same total as before refactoring
- **Verification method** — characterization test (compare outputs over a representative input set)
- **Pass/fail criteria** — identical output for all inputs = PASS / any difference = FAIL

## Hard Gate

> **HARD GATE**: do not start changes without characterization tests (procedure ②)
> If unmet: procedure ④ (incremental change) is blocked — pinning current behavior first is required
> Bypass: only on explicit user phrasing (skip / move on / bypass / skip over)

> **HARD GATE**: no PR while characterization tests are broken (behavior change = not refactoring)
> If unmet: procedure ⑥ is blocked — broken behavior is a feature change (→ `feature`), not refactoring
> Bypass: only on explicit user phrasing

## Feedback-loop locations

1. **Procedure ④ (incremental change + re-verify)** — the core loop. change one unit → characterization tests (verify) → confirm behavior preserved (feedback) → next unit
2. **Procedure ① (analyze current code)** — a loop for grasping impact scope early
3. **Procedure ⑥ (PR)** — reviewer feedback → fix → re-review

> This is the verification loop within the work flow. Improving the playbook itself is the responsibility of retrospective-based evolution (`retro-processing`) (out of scope).

## Review/evaluation points

- **Review**: procedure ⑥ (PR review — examine the evidence of behavior preservation) + procedure ① impact-scope review. Delegate when the project supplies a review teammate. **RT runs default-on** (rigor/independence = README §7 + the RT-rigor matrix). RT essence attacks: behavior preservation (characterization tests) / broken references / consistency.
- **Evaluation**: characterization tests passing (behavior preserved) = the deliverable's evaluation criterion. Re-verify at every change unit.
- `flow-procedure-story` §7-2's review/evaluation Hard Gate enforces execution of the points above.

## Handling violations

- A change without characterization tests / a PR with broken behavior = blocked or sent back for completion
- Bypass is allowed only on explicit user phrasing + must be recorded in the retrospective's Problem section
