# Principles

This document owns the index and core summary of this project's stable principles.

The detailed SSOT of each principle lives in `principles/`. Principles are not a checklist — they are the criteria that control decisions and behavior at every decision point (`operations/during.md`), in every decision record (`decisions/pending/`), and in every retrospective.

The Thinking, Behavior, and Completion sections are the harness core — fixed by the Stage plugin and verified by the audit; removing them breaks the harness's own premises. The Design and Methodology sections and the referenced rule owners are project-adjustable, and projects add their own principles as individual records in `principles/`.

## Thinking principles

Applied to every analysis, plan, implementation, document, and answer.

| Principle | Governs |
|---|---|
| SSOT (Single Source of Truth) | Ownership decisions — every durable fact, status, responsibility, and criterion has exactly one owning location. |
| MECE (Mutually Exclusive, Collectively Exhaustive) | Coverage decisions — task breakdown, case classification, failure handling, test scope, completion conditions. |
| Fail Fast | Early-exposure decisions — wrong premises and incomplete states never pass silently. |
| AHA (Avoid Hasty Abstractions) | Abstraction timing — no new abstraction, rule, category, or procedure before repetition is visible. |

## Design principles

Applied when deciding structure, responsibility, abstraction, and boundaries.

| Principle | Governs |
|---|---|
| DRY (Don't Repeat Yourself) | Duplication checks — repeated criteria and flows are candidates for consolidation, weighed against AHA. |
| KISS (Keep It Simple, Stupid) | Simplicity checks — excessive separation and procedure are treated as violations. |
| SoC (Separation of Concerns) | Responsibility boundaries between documents, code, and procedures. |
| SRP (Single Responsibility Principle) | One module, document, or procedure owns one responsibility. |
| LoD (Law of Demeter) | Coupling checks — do not depend on internals you do not need to know. |
| OCP (Open-Closed Principle) | Extension checks — add cases without breaking existing behavior. |
| LSP (Liskov Substitution Principle) | Contract checks — substitutes must not break existing contracts. |
| ISP (Interface Segregation Principle) | Surface checks — no oversized interfaces or unused dependencies. |
| DIP (Dependency Inversion Principle) | Dependency direction — high-level policy never follows low-level detail. |
| Postel's Law | Tolerance balance — how lenient to accept input, how strict to emit output, bounded by Fail Fast. |
| Clean Architecture | Boundary between domain logic and external detail. |
| DDD (Domain-Driven Design) | Domain terms, boundaries, and model alignment. |

Domain boundaries and SSOT are strict from the start. A wrong abstraction costs more than duplication. Excessive separation is a KISS violation.

## Methodology principles

Applied when verifying work of any kind — code, documents, designs, plans.

| Principle | Governs |
|---|---|
| TDD (Red → Green → Refactor) | Verification precedes implementation where an executable test exists. |
| BDD (Given / When / Then) | Expected outcomes are expressed from the user's behavior. |
| Test pyramid | Verification cost and placement decisions. |
| F.I.R.S.T | Verification quality — fast, independent, repeatable, self-validating, timely. |

## Behavior principles

Applied to how work itself is conducted.

| Principle | Governs |
|---|---|
| Honesty | No asserting unverified facts. Unknown is stated as unknown. Paths, commands, specs, and versions are verified before stated. |
| No temporary passes | A workaround that fakes a pass is never a pass. |
| No partial completion | Partially done is not done. |
| No silent substitution | The request is never silently replaced with something else. |
| Plan execution | A confirmed plan is completed; deviation only on physical impossibility, with the user informed. |
| Question protocol | Before asking, derive the answer from the higher purpose; ask only what the user alone can decide. |

## Completion principle

Work is complete only when external-perspective completion, internal-perspective completion, and the retrospective are all satisfied.

## Referenced rule owners

- Output rules: `operations/output.md`
- Documentation rules: `operations/documentation.md`
- Verification rules: `operations/verification.md`
- UX principles (user-facing work): user-centricity, don't make me think, consistency, clear feedback, visual hierarchy, accessibility — detailed records live in `principles/` when the project does user-facing work.

