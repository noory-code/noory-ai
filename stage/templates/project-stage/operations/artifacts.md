# Artifact Operation

This document owns the artifact structure rules.

## Principles

- A single document only holds an index, a map, or policy.
- Every durable individual artifact has its own file.
- The same body is never duplicated between an index and an individual record.
- Derived views are not SSOT; they link to the original items.
- A new artifact family ships with an `index` plus `items` or `records`.
- Status judgments follow the frontmatter of individual artifact files.

## Base structure

```text
family/
  index.md
  items/ or records/
    README.md
    _template.md
  views/
```

## Work status values

| Field | Values |
|---|---|
| `status` | `active`, `review`, `blocked`, `completed`, `archived`, `rejected` |
| `verification` | `pending`, `passed`, `not_required` |
| `retrospective` | `pending`, `completed` |
| `retrospective_ref` | ID or path of the linked retrospective file |
| `promotion` | `pending`, `approved`, `promoted`, `deferred`, `not_applicable`, `rejected` |
| `promotes` | list of `.stage/past/` paths this item may promote |
| `decision_refs` | optional IDs or paths of linked decision records |
| `source` | optional backlog item ID (`B-*`) this work realizes |

`active.md` and `review.md` are current views. Hooks judge from the frontmatter of `present/work/items/*.md`.

`scope` is fail-closed. An empty value or `.` owns no source path. Declare `*` only when a global scope is truly needed.

Governance is broad by default: nearly every workspace file is governed (registration required before modification), excluding `.stage/`, `.git/`, and `.discuss/`. Projects widen the exclusions via `settings.json` `governance.exclude_paths`/`exclude_extensions`; the audit warns about every narrowing so it stays visible. Legacy allowlist keys (`extensions`/`paths`) are still honored but also reported as narrower than the default.

Lineage is bidirectional: a work item's `source` names the backlog item it realizes, and that backlog item's `realized_by` names the work item. A `selected` backlog item without `realized_by` is an audit warning. State records (Q/A/K/O) may link affected work through their `work_items` field.

`promotes` is also fail-closed. A regular promotion intent may only modify paths declared in the work item's `promotes`. `promotes` entries are exact file paths, not directory prefixes.

`retrospective: completed` is valid only when `retrospective_ref` points to an existing retrospective file whose `work_item` matches the work item ID.

`decision_refs` is optional — not every task has a decision point. When present, each ref must point to an existing decision record in `present/work/decisions/` whose `work_item` matches the work item ID.

## Work status locations

| Status | Location |
|---|---|
| `active`, `blocked` | `present/work/items/` + `present/work/active.md` |
| `review`, `completed`, `rejected` | `present/work/items/` + `present/work/review.md` |
| `archived` | `past/work/archive/items/` |

`completed` means verification, retrospective, and the promotion decision are all closed. Archive a `completed` or `rejected` item once BOTH hold: no active/review/blocked work item names it as `parent`, and no open question, assumption, or risk lists it in `work_items`. Then set `status: archived` and move it to `past/work/archive/items/`.

Moving to `archived` is record keeping, not promotion. A `completed` or `rejected` work item can be archived with an archive intent to `past/work/archive/items/`. The item's retrospective file moves with it to `past/work/archive/retrospectives/` in the same archive intent.

## Artifact catalog

One table to recognize every artifact family fast. Read this before creating any artifact; routing lives in `index.md`.

| Prefix | Artifact | Location | Use when |
|---|---|---|---|
| `W-` | Work item | `present/work/items/` | Any accountable unit of work starts. |
| `R-` | Retrospective | `present/work/retrospectives/` | A work item reaches completion candidate. |
| `DE-` | Working decision | `present/work/decisions/` | A decision point occurs during work. |
| `D-` | Approved decision | `past/decisions/records/` | A decision is approved and promoted. |
| `O-` | Observation | `present/state/observations/` | A fact is observed but not yet official. |
| `Q-` | Question | `present/state/questions/` | An open question blocks or shapes work. |
| `A-` | Assumption | `present/state/assumptions/` | Work proceeds on an unverified premise. |
| `K-` | Risk | `present/state/risks/` | A known risk needs tracking. |
| `B-` | Backlog item | `future/backlog/items/` | Future work is captured. |
| `P-` | Proposal | `future/proposals/` | A direction needs a decision. |
| `M-` | Milestone | `future/roadmap/milestones/` | Backlog items group toward a goal. |
| — | Theme | `future/roadmap/themes/` | Milestones group toward a direction. |
| — | Principle / Term / Invariant | `past/canon/*/` | A rule of the project itself stabilizes. |
| — | Component / Boundary / Interface | `past/model/*/` | Stable structure is recorded. |

Every family follows the same shape — `index` (view) + individual records + `_template.md`. Copy the family's `_template.md` to create a record; never invent a new frontmatter shape.

IDs are zero-padded to 8 digits (`W-00000001`) so lexical order matches creation order at long-project scale. Hooks and the audit accept any width of 3 or more digits, so existing shorter IDs stay valid.

## Audit

The Stage structure audit is performed by:

```bash
python3 stage/scripts/audit_stage.py --project-root .
```
