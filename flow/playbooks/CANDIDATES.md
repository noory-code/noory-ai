# playbook enhancement candidates (CANDIDATES)

> Updated: work-type first reorg (Initiative agent-centric-flow)

A **candidate backlog for enhancing** the plugin-bundled playbook library + a **variant menu** that the `/flow-config` derivation stage references.

## Two uses

1. **Maintainer backlog** — tracks which variants/work types to enhance. Candidate → when adopted, add it to the `## Methodology variants` of the relevant work-type playbook, or if it is a new work type, author `playbooks/{worktype}.md` + register it in `playbooks.json`.
2. **Derivation starting menu** — when `/flow-config` interviews the project's way of working and scaffolds a `.flow/playbooks/` draft, it offers the nearest candidate as a starting point.

## Registration/authoring rules (mandatory)

- When **authoring a candidate as a finished product**, include all of the **7-element authoring standard** from `playbooks/README.md` (frontmatter / procedure / AC format / Hard Gate / feedback-loop location / violation handling / review/evaluation points). No empty forms (completeness principle).
- **Generality principle** — the body uses only project-agnostic universal terms. Names specific to a particular framework/library/language are banned in the body (if unavoidable, quote only inside a code block).
- **Work-type first** — methodologies (variants) are absorbed into the work-type playbook (no new standalone playbook — `meta-playbook-procedure`). Only new-work-type candidates warrant a new playbook.

---

## A. Existing-work-type variant candidates (enhance the relevant playbook's `## Methodology variants`)

> Columns: **Prio** authoring priority / **Status** ⬜ not adopted · ✅ adopted

### feature variant candidates

| Candidate | One line | Prio | Status |
|------|------|:---:|:---:|
| `tdd` (test-first) | Test first → implement toward passing | — | ✅ default flow |
| `bdd` (behavior scenario) | Agree on Given/When/Then scenario → implement | — | ✅ variant |
| `prototype-first` | Behavior first → add tests when stabilizing | — | ✅ variant |
| `spec-driven` (spec-first) | Fix interface/contract first → implement | — | ✅ variant |
| `api-first`/`contract-first` (contract-first) | API schema/contract → Mock → implement → integration verify | — | ✅ variant |
| `type-driven` | Express invariants via types/contracts → implementation satisfies the types | Low | ⬜ |
| `layered-domain-first` | Domain design first → implement layers in dependency-direction order | Mid | ✅ variant (feature.md — Epic 2 US-002, Q2 3rd option) |
| `event-first` | Event/message contract first → implement handlers | Mid | ⬜ |
| `component-catalog-first` | Component catalog (isolated) first → assemble screens | High | ⬜ |
| `design-system-first` | Fix design tokens/patterns → token-compliance gate | Mid | ⬜ |
| `a11y-first` | Pre-embed accessibility criteria (contrast/focus/keyboard) as AC/gates | Mid | ⬜ |
| `schema-contract-first` | Data schema/contract first → implement transforms → contract verify | Mid | ⬜ |
| `eval-driven` | Offline eval metrics/baseline first → change → eval gate | Mid | ⬜ |

### refactor variant candidates

| Candidate | One line | Prio | Status |
|------|------|:---:|:---:|
| `refactor-legacy` (characterization tests) | Pin behavior with characterization tests → change incrementally | — | ✅ default flow |
| `expand-contract` | Zero-downtime migration — expand (parallel) → migrate → contract gate | High | ⬜ |

### bug variant candidates

| Candidate | One line | Prio | Status |
|------|------|:---:|:---:|
| `defect-driven` (reproduce/regression) | Reproduce → failing test → fix → regression | — | ✅ default flow |

### docs (document/spec) variant candidates

| Candidate | One line | Prio | Status |
|------|------|:---:|:---:|
| `interview-first` (requirements/planning spec) | Interview → organize requirements → visualize flow → spec → review → handoff | — | ✅ variant |
| `spec-by-example` | Spec via concrete examples (scenarios) → the examples are the verification criteria | Mid | ⬜ |
| `design-doc-first` | Design doc (RFC) → review-agreement gate → execute | Mid | ⬜ |
| `outcome-first` | Define scope by outcome/impact, not output | Low | ⬜ |
| `runbook-first` | Operations procedure/rollback-path doc (runbook) first | Low | ⬜ |

---

## B. New-work-type candidates (new playbook targets)

> Universal work types that did not fit the original 5 bundled work types (feature/refactor/bug/docs/retro-processing). Author a new playbook when repeat demand (≥3 times) is confirmed. Adopted candidates (✅) have since shipped as bundled playbooks.

| Candidate work type | One line | Prio | Status |
|------|------|:---:|:---:|
| `research` (investigation/research) | Collect sources → cross-verify → structure → indexing/handoff. Unlike docs, collection/verification is the core gate | High | ✅ |
| `usecase-extraction` (reverse documentation) | Analyze code/spec → extract use cases → verify bidirectional code↔doc sync. Opposite of docs (authoring direction): code→doc parity is the gate | High | ✅ |
| `deploy` (deployment/infrastructure) | Separate plan→review→apply stages / incremental rollout (partial exposure→observe→expand/rollback) / runbook first | Mid | ✅ |
| `qa` (quality verification) | Risk-based test allocation / exploratory test charter (goal/scope/time) | Mid | ✅ |
| `security` | Threat modeling first → mitigation AC/gates / security review Hard Gate before merge | Mid | ✅ |
| `plugin-dev` (developing the plugin itself) | Rule/skill/hook/command changes + full regression obligation + propagation obligation (rule sync / version bump) + dogfood. A single meta-work flow (no methodology variants) | High | ✅ |
| `observability` | Include observability metrics/logs/traces in the deliverable definition, gate their verification | Mid | ⬜ |
| `data-quality` | Data-quality (completeness/consistency) Hard Gate at each pipeline stage | Mid | ⬜ |
| `experiment-tracking` | Enforce experiment config/metric recording as a deliverable → reproducibility | Low | ⬜ |

> **2026-06-05 update (based on repeat-demand signals)**: registered `research`/`usecase-extraction` as new + raised `qa`/`security` priority Low→Mid. Rationale — some projects already operate these 4 work types with **dedicated skill sets + dedicated agents** (a multi-stage flow per work type + a dedicated agent = a strong signal of ≥3-time repeat demand). research/usecase have a flow direction different from docs (collection/verification / code→doc parity), so absorbing them as variants is unsuitable → new-work-type targets.

> **2026-06-05 adoption complete (✅)**: the 5 new-work-type candidates above (`research`·`usecase-extraction`·`qa`·`security`·`deploy`) were **authored as bundled finished-product playbooks** (7-element authoring standard + generality principle) and registered in the `playbooks.json` catalog. The remaining Section B candidates (`observability`·`data-quality`·`experiment-tracking`) are follow-ups once demand is proven.

---

## Evolution linkage (Φ4 / retro-processing)

The criteria for candidate → adoption and existing → revision are consistent with `playbooks/README.md` §playbook evolution mechanism + the `retro-processing` work type:

- **New candidate**: the same work pattern does not fit an existing playbook and repeats **≥3 times** → register in this backlog or raise its priority.
- **Add variant**: a new methodology for an existing work type is useful **≥3 times** → add it to that playbook's `## Methodology variants`.
- **Revision candidate**: applying an existing playbook fails **≥2 times** → revise the procedure/Hard Gate.
- The repeat-pattern identification of retrospectives (`retro-processing` work type) is the input source for this backlog.
