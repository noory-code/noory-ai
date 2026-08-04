# Stage Index

This document routes project context to the correct Stage location.

## Lifecycle

- `planned`: intended work in `work/planned/`, `proposals/`, and roadmap records without a pursuit decision.
- `current`: work becoming real in `work/current/`, `decisions/pending/`, `state/`, and roadmap records with open pursuit.
- `official`: promoted, settled truth under `official/`.

## Authority

- `official/`: the sole authorization zone for official artifacts and approved truth.
- `work/`, `decisions/`, `state/`, `proposals/`, and `roadmap/`: mutable responsibility families.
- `operations/`: project-owned Stage policy. Common behavior rules are plugin-owned and live in
  the installed Stage plugin's `operations/` directory.

## Routing rules

| Information | Location |
|---|---|
| Principle index and summary | `official/canon/principles.md` |
| Individual principles | `official/canon/principles/` |
| Vocabulary index and summary | `official/canon/vocabulary.md` |
| Individual terms | `official/canon/vocabulary/` |
| Invariant index and summary | `official/canon/invariants.md` |
| Individual invariants | `official/canon/invariants/` |
| System structure | `official/model/` |
| Model components | `official/model/components/` |
| Model boundaries | `official/model/boundaries/` |
| Model interfaces | `official/model/interfaces/` |
| Official decisions | `official/decisions/index.md` |
| Official decision records | `official/decisions/records/` |
| Archived decisions | `official/decisions/archive/` |
| Archived proposals | `official/proposals/archive/` |
| Archived state records | `official/state/archive/` |
| Archived work index | `official/work/archive/index.md` |
| Archived work items | `official/work/archive/items/` |
| Archived retrospectives | `official/work/archive/retrospectives/` |
| Active work | `work/active.md` |
| Current work cards | `work/current/` |
| Review candidates | `work/review.md` |
| Work retrospectives | `work/retrospectives/` |
| Planned work index | `work/planned/index.md` |
| Planned work cards | `work/planned/` |
| Work views | `work/views/` |
| Pending decision index | `decisions/index.md` |
| Pending decision records | `decisions/pending/` |
| Current observations | `state/current.md` |
| Observation records | `state/observations/` |
| Open questions | `state/questions.md` |
| Question records | `state/questions/` |
| Assumptions | `state/assumptions.md` |
| Assumption records | `state/assumptions/` |
| Risks | `state/risks.md` |
| Risk records | `state/risks/` |
| Proposal index | `proposals/index.md` |
| Proposal bodies | `proposals/` |
| Roadmap index | `roadmap/index.md` |
| Roadmap milestones | `roadmap/milestones/` |
| Roadmap themes | `roadmap/themes/` |
| Work-kind verification criteria | `operations/verification.md` |
| Common operation rules | plugin-owned `operations/` in the installed Stage plugin |

## Core rule

Planned artifacts are not truth. Current artifacts are not truth. Only official artifacts are truth.
