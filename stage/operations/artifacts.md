# Artifact Operation

This document owns the artifact structure rules.

## Principles

- A single document only holds an index, a map, or policy.
- Every durable individual artifact has its own file.
- The same body is never duplicated between an index and an individual record.
- Derived views are not SSOT; they link to the original items.
- A new artifact family ships with an `index` plus `items` or `records`.
- Status judgments follow the frontmatter of individual artifact files.

## Lifecycle model

Every artifact is always in exactly one lifecycle state — `planned` (intended, not yet real),
`current` (becoming real), or `official` (promoted, settled truth). Directories group by
RESPONSIBILITY, not by tense; the lifecycle is carried by each artifact and enforced by the
gates (registration into current, promotion into official, archival within official). The three
states are MECE: no overlap, no gap.

## Base structure

Each family declares its own record roots and index surfaces in the topology registry
(`hooks/stage_topology.py`); there is no single universal subdirectory shape. Most families keep
individual records under a named subdirectory (e.g. `work/current/`, `official/decisions/records/`),
while others hold records and their `_template.md` directly in the zone (e.g. `proposals/`,
`roadmap/themes/`, `roadmap/milestones/`). What every family shares is: an `index` (view), the
individual records as their own files, and a `_template.md` to copy.

## Work status values

| Field | Values |
|---|---|
| `status` | planned: `captured`, `triaged`, `ready`, `selected`, `deferred`, `rejected`; current: `active`, `blocked`, `review`, `completed`, `rejected`; official: `archived` |
| `verification` | `pending`, `passed`, `not_required` |
| `retrospective` | `pending`, `completed` |
| `retrospective_ref` | ID or path of the linked retrospective file |
| `promotion` | `pending`, `approved`, `promoted`, `deferred`, `not_applicable`, `rejected` |
| `promotes` | list of `.stage/official/` paths this item may promote |
| `terminal_disposition` | on a closed card: `accepted` or `rejected` (the archive index derives from it) |
| `decision_refs` | optional IDs or paths of linked decision records |
| `milestone` | optional roadmap attribution, `0..1`: the single milestone that claims this card's completion credit |
| `priority` | optional, planned cards only: ordering hint shown in the planned index |
| `venue` | optional execution-surface routing; project-defined values, derived from `settings.json` `venue_routing` when declared |

`work/active.md` and `work/review.md` are current views. Hooks judge from the frontmatter of `work/current/*.md`.

`venue` names the execution surface that should carry out the work item — the routing signal a human reads to open the right window when more than one agent or session works the project. No hook gates on it. The machine-readable `kind -> venue` role policy is project-declared in `settings.json` `venue_routing` (registration derives from it; the audit checks consistency); what each venue means belongs to the project's canon. A policy-contradicting venue is valid only with a linked decision record that is decided/promoted and declares `authorizes: venue_exception`; the reserved routing value `split` marks a kind as mixed by definition — it registers as separate design/implementation items with `parent` lineage. The harness fixes no venue names.

`scope` is fail-closed. An empty value or `.` owns no source path. Declare `*` only when a global scope is truly needed.

Governance is broad by default: nearly every workspace file is governed (registration required before modification), excluding `.stage/`, `.git/`, and `.discuss/`. Projects widen the exclusions via `settings.json` `governance.exclude_paths`/`exclude_extensions`; the audit warns about every narrowing so it stays visible. Legacy allowlist keys (`extensions`/`paths`) are still honored but also reported as narrower than the default.

Hierarchy is the only work lineage: `parent` names the parent work card (e.g. an implementation item under its design item). `milestone` is a distinct, upward roadmap attribution (portfolio membership), never a substitute for `parent`. A card keeps one identity from planned to archive, so no realization links exist; a legacy `source:` field on an old record is inert history. State records (Q/A/K/O) may link affected work through their `work_items` field.

`promotes` is also fail-closed. A regular promotion intent may only modify paths declared in the work item's `promotes`. `promotes` entries are exact file paths, not directory prefixes.

`retrospective: completed` is valid only when `retrospective_ref` points to an existing retrospective file whose `work_item` matches the work item ID.

`decision_refs` is optional — not every task has a decision point. When present, each ref must point to an existing decision record in `decisions/pending/` (or, once promoted, `official/decisions/records/`) whose `work_item` matches the work item ID.

## Work status locations

| Status | Location |
|---|---|
| `captured`, `triaged`, `ready`, `selected`, `deferred`, `rejected` (planned) | `work/planned/` + `work/planned/index.md` |
| `active`, `blocked` | `work/current/` + `work/active.md` |
| `review`, `completed`, `rejected` | `work/current/` + `work/review.md` |
| `archived` | `official/work/archive/items/` |

`rejected` appears in two lifecycle states: a planned card declined before any work started
stays in `work/planned/`; a card rejected during execution sits in `work/current/`. Both carry a
completed retrospective before archiving.

A work card is ONE artifact across its whole life (DE-00000007): captured as a planned card in
`work/planned/`, physically moved to `work/current/` when work starts (`scripts/start_work.py`
sets `active`, requires `scope`, and enforces the venue/split contract at that moment), and
archived to `official/work/archive/items/` when closed. `rejected` may also appear on a planned
card that was declined before any work started. Registering directly into `work/current/`
remains valid for work that never sat in the planned column.

`completed` means verification, retrospective, and the promotion decision are all closed. A `rejected` item also records its completed retrospective (`retrospective_ref`) before archiving — rejection reasons are learning assets. Archive a `completed` or `rejected` item once BOTH hold: no active/review/blocked work item names it as `parent`, and no open question, assumption, or risk lists it in `work_items`. Then set `status: archived` and move it to `official/work/archive/items/`.

Moving to `archived` is record keeping, not promotion. A `completed` or `rejected` work item can be archived with an archive intent to `official/work/archive/items/`. The item's retrospective file moves with it to `official/work/archive/retrospectives/`, and its `official/work/archive/index.md` row — whose `Final status` cell records `completed` or `rejected`, the transition evidence the `archived` overwrite erases — lands in the same archive intent.

## Artifact catalog

One table to recognize every artifact family fast. Read this before creating any artifact; routing lives in `index.md`.

| Prefix | Artifact | Location | Use when |
|---|---|---|---|
| `W-` | Work card | `work/current/` | Any accountable unit of work; planned cards wait in `work/planned/`, archived cards rest in `official/work/archive/items/`. |
| `R-` | Retrospective | `work/retrospectives/` | A work item reaches completion candidate. |
| `DE-` | Working decision | `decisions/pending/` | A decision point occurs during work. Its `DE-` id is permanent; promotion moves the record into `official/decisions/records/` without renaming it. |
| `D-` | Legacy approved decision | `official/decisions/records/` | Historical promoted decisions; new promotions keep their `DE-` id. |
| `O-` | Observation | `state/observations/` | A fact is observed but not yet official. |
| `Q-` | Question | `state/questions/` | An open question blocks or shapes work. |
| `A-` | Assumption | `state/assumptions/` | Work proceeds on an unverified premise. |
| `K-` | Risk | `state/risks/` | A known risk needs tracking. |
| `P-` | Proposal | `proposals/` | A direction needs a decision. |
| `M-` | Milestone | `roadmap/milestones/` | Work cards group toward a goal; status is computed from its decision chain. |
| `TH-` | Theme | `roadmap/themes/` | Milestones group toward a direction; status is computed from its decision chain. |
| — | Principle / Term / Invariant | `official/canon/*/` | A rule of the project itself stabilizes. |
| — | Component / Boundary / Interface | `official/model/*/` | Stable structure is recorded. |

Every family follows the same shape — `index` (view) + individual records + `_template.md`. Copy the family's `_template.md` to create a record; never invent a new frontmatter shape.

IDs are zero-padded to 8 digits (`W-00000001`) and counted PER TYPE (the first theme is `TH-00000001`, the first milestone `M-00000001`), so lexical order matches creation order within each type at long-project scale. Hooks and the audit accept any width of 3 or more digits, so existing shorter IDs stay valid.

The roadmap family (`TH-`/`M-`) is fixed in `roadmap/`: themes and milestones span lifecycle states, so they do not move. Their status is computed solely from their decision chain (no authored status field). A milestone closes through a decision that freezes an immutable basis of its terminal work cards; promoting that closure revalidates the basis fail-closed, and a work card frozen by an effective closure cannot change its `milestone` without a superseding decision.

## Audit

The Stage structure audit is performed by:

```bash
python3 stage/scripts/audit_stage.py --project-root .
```
