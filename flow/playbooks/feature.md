---
name: feature
description: Feature-development work type — design → test (Red) → implementation iteration (Green) → PR. Default is test-first, with selectable methodology variants (behavior scenario · prototype · spec-first · contract-first)
---

# feature (feature development)

A work type for building new features. **The default flow is test-first** (write tests first and implement toward making them pass), and depending on the nature of the work, the flow is changed via `## Methodology variants` (behavior scenario / prototype / spec-first / contract-first).

## Applies to

- New feature development where inputs/outputs and behavior can be defined
- Code where regression prevention matters
- Not suitable for: structural improvement that preserves existing behavior (→ `refactor`) / defect fixes (→ `bug`) / producing docs/specs (→ `docs`)

## Procedure

Default flow (test-first):

1. **Design** — requirements → decide interface/structure / deliverable: design note (interface signatures, responsibility separation)
2. **Design review** — check whether the design is consistent with requirements and the existing structure / deliverable: review-incorporated design
3. **Test Case definition** — specify each behavior as Given/When/Then (normal + boundary + exception) / deliverable: AC list
4. **Write test code (Red)** — turn Test Cases into runnable tests. They fail at this point (Red) / deliverable: test files (failure confirmed)
5. **Implementation + verification iteration (Green → Refactor)** — minimal implementation to pass the tests → pass (Green) → refactor → rerun. Repeat until all pass / deliverable: implementation code + all tests passing
6. **PR** — change bundle + test results + review request / deliverable: Pull Request

> Concrete domain analysis (layer composition / state management / data flow) and language-specific test-writing methods are delegated to the analysis procedure **supplied by the project** (project `.claude/agents/`). This playbook defines only the general-purpose feature-development flow.
>
> **Branch (when design is unclear)**: if the domain is new and it is hard to fix the design in advance, do not finalize the design first; instead run an exploratory cycle that derives the design via ③④ (Test Case → test code) first (write tests → derive design → ② review → enter ⑤). If more exploratory, use `## Methodology variants — prototype-first`.

## Methodology variants

Depending on the nature of the work, select one of the variants below instead of the default (test-first). **The variants differ only in flow; the AC 5 fields · Hard Gate · feedback loop · review principles are identical.**

| Variant | When | Flow (difference from default) | Key gate |
|------|------|---------------------|------------|
| **Behavior-scenario-first (BDD)** | a behavior spec stakeholders can understand matters / scenario agreement precedes implementation | ① define scenarios (Given/When/Then) → ② scenario review (agreement) → ③ scenario→runnable tests (fail) → ④ implement → ⑤ verification iteration → ⑥ PR. scenario = AC | no implementation without agreed scenarios |
| **Prototype-first** | requirements/design unclear — direction only emerges after building / fast feedback first | ① sketch the goal (hypothesis) → ② minimal implementation → ③ confirm behavior → ④ feedback loop → ⑤ stabilization decision (formalize/discard) → ⑥ reinforce tests (if formalized) | no merging of shared code before direction is fixed · no formal merge without a stabilization decision |
| **Spec-first (spec-driven)** | when the interface/contract must be fixed first | fix the interface/contract first in the design stage → turn that contract into tests → implement. Strengthens the default flow's ① design into "contract fixing" | no implementation without a fixed contract |
| **Contract-first (API/backend)** | agreeing an API contract with consumers (frontend/external) comes first / parallel development (consumer Mock) needed | ① design API spec (schema · error contract) → ② spec review (consumer agreement) → ③ provide Mock → ④ implement → ⑤ integration-test iteration (verify against spec) → ⑥ PR | no implementation without an agreed spec · no PR that fails integration tests (spec mismatch) |
| **Layer-first (layered-domain-first)** | architectures with strong layer separation (Clean Arch, etc.) — fix the domain contract first, then implement layers in dependency-direction order | ① domain design (fix entities · contracts) → ② domain review → ③ domain tests (fail) → ④ implement layers in dependency-direction order (Domain → Presentation · Data; layers can run in parallel once the contract is fixed) → ⑤ per-layer verification iteration → ⑥ PR | no upper-layer implementation without a fixed domain contract · no parallel work across layers while the contract is unfixed |

> Choose the variant when entering the work and record it in `_epic.md` (e.g., `feature (BDD variant)`). If no variant fits, use the default (test-first).
> The **layer-first variant** implements the Q2 official position (work type is primary + layers are a feature variant — `meta-playbook-procedure` §core principles). Rather than promoting layers to a separate playbook axis, it absorbs them into this variant. ④ parallel layer implementation is wired up as waves of the lead's scheduling decision layer (`handoff-protocol` §3.1.1).

## AC format

Each Test Case (or a variant's scenario/contract) is written with 5 fields.

- **Given** — preconditions (input / state / prior work)
- **When** — action (call / run)
- **Then** — expected result (output / state change / side effect)
- **Verification method** — automated tests (unit / integration) or an observation procedure
- **Pass/fail criteria** — pass condition (quantitative) / fail condition

> No unmeasurable ACs like "works fine / looks okay".

Example (domain-agnostic — authentication feature):

- **Given** — valid credentials (identifier + correct password)
- **When** — run authentication
- **Then** — return an authentication-success state
- **Verification method** — automated unit test (assert the returned state)
- **Pass/fail criteria** — test PASS / FAIL if not an authentication-success state

## Hard Gate

> **HARD GATE**: no starting implementation without tests (Red)
> If unmet: step ⑤ (implementation) is blocked — step ④ (test code) must come first. (The prototype variant substitutes test reinforcement at the stabilization decision — see the variant gate table.)
> Bypass: only on explicit user phrasing (skip / move on / bypass / skip it)

> **HARD GATE**: no PR unless all tests pass
> If unmet: step ⑥ (PR) is blocked — every test added/modified by this change plus the related existing regression tests must all pass
> Bypass: only on explicit user phrasing

## Feedback-loop location

This playbook's "verify → feedback → fix → re-verify" loop:

1. **Step ⑤ (implementation + verification iteration)** — the core loop. Run tests (verify) → analyze failures (feedback) → fix implementation → rerun. Repeat until all pass
2. **Step ② (design review)** — an early feedback loop at the design stage
3. **Step ⑥ (PR)** — reviewer feedback → fix → re-review

> Core loop per variant: BDD/contract = verification iteration / prototype = feedback loop (④) + stabilization decision (⑤).
> The loop above is a verification loop **within the work flow**. Improving the playbook itself ("is this flow correct?") is the responsibility of retrospective-based evolution (`retro-processing` work type) — outside this playbook's scope.

## Review/evaluation points

- **Review**: step ② (design/scenario/spec review) + step ⑥ (PR review request). Prioritize essential defects (design consistency / responsibility separation / regression risk / contract agreement). Delegate when the project supplies a review teammate. **RT runs default-on** (strength/independence = README §7 + RT strength matrix). RT essential attacks: design consistency · responsibility separation · contract agreement · regression risk.
- **Evaluation**: meeting the step ③ AC (Given/When/Then) = the deliverable evaluation criterion. All tests (or scenario/integration tests) passing = met.
- The `flow-procedure-story` §7-2 review/evaluation Hard Gate enforces execution of the points above.

## Violation handling

- Implementation without tests / a PR that does not pass / implementing an unagreed contract = block or request remediation
- Bypass is allowed only on explicit user phrasing (skip / move on / bypass / skip it)
- A bypass is a mandatory record in the retrospective Problem section
