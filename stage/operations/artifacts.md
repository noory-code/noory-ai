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

`work/active.md` and `work/review.md` are current views. Hooks judge from the frontmatter of work
records anywhere in the hierarchy below `work/current/`.

`venue` names the execution surface that should carry out the work item — the routing signal a human reads to open the right window when more than one agent or session works the project. No hook gates on it. The machine-readable `kind -> venue` role policy is project-declared in `settings.json` `venue_routing` (registration derives from it; the audit checks consistency); what each venue means belongs to the project's canon. A policy-contradicting venue is valid only with a linked decision record that is decided/promoted and declares `authorizes: venue_exception`; the reserved routing value `split` marks a kind as mixed by definition and places its separate design and implementation actions under one story. The harness fixes no venue names.

`scope` is fail-closed. An empty value or `.` owns no source path. Declare `*` only when a global scope is truly needed.

Governance is broad by default: nearly every workspace file is governed (registration required before modification), excluding `.stage/`, `.git/`, and `.discuss/`. Projects widen the exclusions via `settings.json` `governance.exclude_paths`/`exclude_extensions`; the audit warns about every narrowing so it stays visible. Legacy allowlist keys (`extensions`/`paths`) are still honored but also reported as narrower than the default.

Folder placement is the only work hierarchy truth. An epic directory owns `_epic.md` and story
directories; a story directory owns `_story.md` and action cards. A story may be top-level or
inside an epic, while an action must be inside a story. Work records have no `parent` field.
`milestone` is a distinct, upward roadmap attribution carried only by a top-level epic or
independent story. State records (Q/A/K/O) may link affected work through `work_items`.

`promotes` is also fail-closed. A regular promotion intent may only modify paths declared in the work item's `promotes`. `promotes` entries are exact file paths, not directory prefixes.

A current `completed` item with `promotion: approved` has chosen promotion but has not recorded
that it happened, so the audit reports it even when every `promotes` path already existed. After
writing every declared path, set `promotion: promoted`; the audit then requires at least one
declared path and checks that every path exists as a file. This contract applies while the item
remains in `work/current/`; archived cards that predate it are not rejected retroactively.

`retrospective: completed` is valid only when `retrospective_ref` points to an existing retrospective file whose `work_item` matches the work item ID.

`decision_refs` is optional — not every task has a decision point. When present, each ref must point to an existing decision record in `decisions/pending/` (or, once promoted, `official/decisions/records/`) whose `work_item` matches the work item ID.

## Work status locations

| Status | Location |
|---|---|
| `captured`, `triaged`, `ready`, `selected`, `deferred`, `rejected` (planned) | hierarchy below `work/planned/` + `work/planned/index.md` |
| `active`, `blocked` | hierarchy below `work/current/` + `work/active.md` |
| `review`, `completed`, `rejected` | hierarchy below `work/current/` + `work/review.md` |
| `archived` | hierarchy below `official/work/archive/items/` |

`rejected` appears in two lifecycle states: a planned card declined before any work started
stays in `work/planned/`; a card rejected during execution sits in `work/current/`. Both carry a
completed retrospective before archiving.

A top-level work hierarchy is ONE lifecycle move unit (DE-00000007, DE-00000035): an epic or
independent story directory is captured below `work/planned/`, physically moved with all nested
stories and actions to `work/current/` when work starts, and archived as a whole below
`official/work/archive/items/` when closed. Inner stories and actions stay inside that directory
while their own status changes.

`completed` means verification, retrospective, and the promotion decision are all closed. A
`rejected` item also records its completed retrospective (`retrospective_ref`) before archiving —
rejection reasons are learning assets. Archive a top-level epic or independent story once every
nested work record is terminal and no open question, assumption, or risk lists one of its work
records in `work_items`. Then set the records to `archived` and move the top-level directory to
`official/work/archive/items/`.

Moving to `archived` is record keeping, not promotion. A `completed` or `rejected` work item can be archived with an archive intent to `official/work/archive/items/`. The item's retrospective file moves with it to `official/work/archive/retrospectives/`, and its `official/work/archive/index.md` row — whose `Final status` cell records `completed` or `rejected`, the transition evidence the `archived` overwrite erases — lands in the same archive intent.

## Artifact catalog

One table to recognize every artifact family fast. Read this before creating any artifact; routing lives in `index.md`.

| Prefix | Artifact | Location | Use when |
|---|---|---|---|
| `W-` | Epic, story, or action work record | `work/current/` | Any accountable unit of work; records live in the hierarchy below this root, planned hierarchies wait below `work/planned/`, and archived hierarchies rest below `official/work/archive/items/`. |
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

The pending-decision index is a derived view. Refresh it after decision or linked-work lifecycle
changes; the command preserves prose outside its recognized table and refuses an unfamiliar table
instead of overwriting it:

```bash
python3 stage/scripts/refresh_decision_index.py --project-root .
```

IDs are zero-padded to 8 digits (`W-00000001`) and counted PER TYPE (the first theme is `TH-00000001`, the first milestone `M-00000001`), so lexical order matches creation order within each type at long-project scale. Hooks and the audit accept any width of 3 or more digits, so existing shorter IDs stay valid.

The roadmap family (`TH-`/`M-`) is fixed in `roadmap/`: themes and milestones span lifecycle states, so they do not move. Their status is computed solely from their decision chain (no authored status field). A milestone closes through a decision that freezes an immutable basis of its terminal work cards; promoting that closure revalidates the basis fail-closed, and a work card frozen by an effective closure cannot change its `milestone` without a superseding decision.

## Audit

The Stage structure audit is performed by:

```bash
python3 stage/scripts/audit_stage.py --project-root .
```
