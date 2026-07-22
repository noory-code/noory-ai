# Schema v4 — Official-Zone Topology

This document is the canonical design for Stage schema v4. Implementation cards C2-C9
(W-00000018 lineage) implement against the interfaces declared here. Rulings trace to the
2026-07-12 dual-debate verdict (Codex thread `019f5637-2372-7d51-9727-a470c4b5b533`; the
debates used the working moniker PAST-ANCHORED) and the post-verdict zone-rename amendment
(owner-ruled, Codex-approved).

Governing principles: SSOT, MECE, Fail Fast, AHA (see `official/canon/principles.md` in the
project harness).

## Design axioms

1. The lifecycle triad is a **semantic MECE classification** — every artifact is always in
   exactly one of three states: planned, current, official. It governs behavior through gates
   and vocabulary, not through directory nesting.
2. Directories group by **responsibility** (space axis). Physical movement is retained only
   where it has operational force: execution artifacts whose location controls authorization
   or whose transition must be legible as a git move.
3. `official/` is the sole **authorization zone**: containment under `.stage/official/` is the
   single predicate behind the promotion-intent gate. The predicate mechanism survives v4
   verbatim; only its root constant renames (v3: `past/`).

## Root topology

```
.stage/
├── index.md, settings.json     ungoverned meta (unchanged)
├── operations/                 project-owned operating rules (unchanged)
├── official/                   authorization zone (was past/, contents unchanged):
│   ├── canon/  model/          official structure and rules
│   ├── decisions/records/      official decision records
│   └── work/archive/           archived items/ and retrospectives/
├── work/
│   ├── planned/                planned W cards + backlog index (was future/backlog/items)
│   ├── current/                open W cards: active, blocked, review, completed, rejected
│   ├── retrospectives/         current-cycle retrospectives
│   ├── views/                  auxiliary views (was future/backlog/views)
│   ├── active.md  review.md    phase index surfaces (kept separate; no unified board file)
├── decisions/
│   ├── pending/                DE records under consideration
│   └── index.md                pending index
├── state/                      observations/ questions/ assumptions/ risks/ (unchanged inside)
├── proposals/                  P records (was future/proposals)
├── roadmap/
│   ├── themes/                 TH records (fixed residence)
│   ├── milestones/             M records (fixed residence)
│   └── index.md
└── .runtime/                   untracked machine state: intents, sessions, question-ack
```

Removed: top-level `past/`, `present/`, and `future/`. The wrappers `present/` and `future/`
carried no gate semantics; `past/` carried the authorization semantics and renames to
`official/` so the zone name equals the lifecycle state name — canon and model are living
official truth, not history, and one word now serves vocabulary, gate, and folder alike.
`work/current/` is named for its residents: all five open statuses live there.

## Lifecycle model

Canonical vocabulary (registry-owned; canon vocabulary gains these three terms):

| State | Meaning | Storage projection |
|---|---|---|
| `planned` | intended, not yet real | `work/planned/`, `proposals/`, roadmap records without pursuit decision |
| `current` | becoming real | `work/current/`, `decisions/pending/`, `state/*`, roadmap records with open pursuit |
| `official` | promoted, settled truth | everything under `official/` |

Rules:
- Single-classification: every artifact maps to exactly one lifecycle state; the audit
  verifies the mapping and fails on contradiction (e.g. a W ID present in two zones, or a
  location disagreeing with the card's own status enum).
- Transitions are performed by the existing mechanisms: `start_work.py` (planned → current),
  the promotion-intent gate (current → official), archive flow (record-keeping within
  official). Gates and movers are the time axis; validation gates (hierarchy, enum, venue,
  commit, review) check admissibility, not lifecycle.

Pedagogy surfaces (replace time-as-directories teaching):
- Root `index.md`: one table declaring the root MECE frame (official zone / mutable families /
  direction / rules / machine state) and the three-state lifecycle.
- Session-start context (`stage_context.py`): teaches the triad and renders derived lifecycle
  views (see Roadmap).
- `operations/before|during|after.md`: rewritten to route by lifecycle state and gate, not by
  directory tense.
- Derived cross-family lifecycle views restore ambient visibility (what is planned / current /
  official across families) lost with the wrappers.

## Topology registry (`stage/hooks/stage_topology.py`)

Single tooling SSOT for topology. Importable by hooks and scripts (same pattern as
`stage_paths`). Owns:

- Family table — one entry per family (`canon`, `model`, `decisions`, `work`, `state`,
  `proposals`, `roadmap`, `operations`), each declaring its zones. Authorization class is
  **per zone**, not per family (`work` and `decisions` span mutable and official zones).
- Zone record: canonical path, lifecycle state, allowed status enums, record roots, index/view
  surfaces, template source, transition destination, reference-resolver policy, v3 relocation
  origin.
- Artifact prefixes: `W` (work), `DE` (decisions; `D` legacy-resolve-only), `TH` (themes),
  `M` (milestones), `O Q A K` (state), `P` (proposals). Counters are family-local, 8-digit
  zero-padded (widths of 3+ remain valid).
- Cross-family facts: lifecycle vocabulary, single-classification rule, `schema_version`
  ownership (stamped in `.stage/settings.json`; audit and migration read the same constant),
  the v3 → v4 relocation map, migration maintenance-marker location (under `.runtime/`).
- Derivation helpers: card location by status, retrospective locations, scan roots for
  records/audit/context, legacy detection.

Boundary: **authorization stays in `stage_paths`** (official-containment predicate; the root
constant renames from `past/`). The registry records the zone classification; a parity test
guards drift between the two.

Conformance tests: (a) no `past/`, `present/`, or `future/` topology literals in production
Python outside `stage_topology` and `stage_paths` (exempt: templates, migration fixtures,
historical docs); (b) registry-to-template parity.

## Decision identity — Contract X

- A decision record's identity is its `DE-` id, **permanent for life**. Promotion moves the
  file from `decisions/pending/` into `official/decisions/records/` without renaming the id;
  `status` becomes `promoted`.
- `D-` ids are legacy: existing archives stay untouched; resolvers accept both prefixes and
  route by registry policy. New records never mint `D-` ids.
- Rationale (SSOT): stable identity keeps `decision_refs`, predecessor/supersession chains,
  and closure snapshots valid across promotion with no alias table to synchronize.

Decision-chain integrity (v1-blocking, from debate 1): every transition decision names its
predecessor or the decision it supersedes; the audit rejects forks, cycles, dangling
references, and multiple effective heads. Effective state = the latest non-superseded decision
in the chain; ordering is chain-structural, never numeric or timestamp.

## Work family contracts

W frontmatter includes these execution fields:

- `autonomous:` — boolean eligibility signal. It defaults to `false` when absent. An item with
  `autonomous: true` must carry at least one `acceptance` command; `register_work.py` and
  `start_work.py` refuse the transition otherwise.
- `acceptance:` — YAML list of shell-command strings that deterministically verify completion.
  `close_work.py` runs each entry through its existing check runner using the shared per-check
  `--timeout`, then runs any additional repeatable `--check` arguments. Every stored and CLI
  check must exit zero. Non-autonomous items may omit the list or leave it empty.
- Independent review of autonomous work: an item with `autonomous: true` must, at close, pass an
  independent reviewer whose venue differs from the item's `venue` — an executor must not grade its
  own work. `review.reviewers` in settings.json maps each venue to a reviewer command;
  `close_work.py` resolves the sole reviewer whose venue differs from the item's and runs it,
  blocking on a nonzero exit or a `BLOCK:` verdict line. If no differing-venue reviewer is
  configured, or the map is ambiguous, the autonomous item cannot close (fail closed) — the
  escalation path. Non-autonomous items keep the opt-in per-stage `review` behavior.

- `milestone:` — optional, cardinality 0..1. **Attribution**: names the single milestone that
  claims this card's completion credit. Evidence citations elsewhere are unrestricted and
  many-to-many; attribution and evidence are distinct relations. Genuinely mixed work splits
  (existing split contract) rather than double-attributing. `parent:` remains execution
  decomposition (W→W); `milestone:` is portfolio membership (W→M); they never substitute for
  each other.
- `terminal_disposition:` — SSOT for a closed card's outcome (`accepted` / `rejected`),
  card-owned. The archive index disposition column derives from it.

Registration flows are unchanged: direct registration into `work/current/`, `--backlog`
capture into `work/planned/`, `start_work.py` as the only mover.

## Roadmap family

- Themes (`TH-`) and milestones (`M-`) reside in `roadmap/` for life; they span lifecycle
  states, so movement is meaningless for them. Both carry frontmatter (theme: `id`,
  `decision_refs`; milestone: `id`, `theme`, `decision_refs`) and index files.
- **No authored or cached status field.** Current status is computed solely from the record's
  decision chain: no pursuit decision = planned; open pursuit = current; effective closure =
  closed. Milestone `Linked backlog` and theme `Linked milestones` sections are derived views.
- Pursuit and closure are decision records (in `decisions/pending/`, promoted like any DE).
- Closure basis: the closure decision freezes the exact W ids with their `terminal_disposition`
  values and the completion-criteria attestation. Closure is valid only when every linked W is
  terminal (archived, accepted or explicitly rejected); planned/current cards are nonterminal
  and must first be rejected (with reason) or re-linked. Theme closure requires all its
  milestones closed or explicitly re-parented/rejected.
- Promotion of a closure revalidates the frozen basis against live state through the registry,
  fail-closed with the diff shown. Reopening requires a superseding decision. A W id in any
  effective closure snapshot cannot change its `milestone:` field without a decision
  superseding that closure — enforced preventively by the write gate, not audit-only.
- Discovery: the stage-work skill asks the milestone question iff at least one open milestone
  exists; roadmap creation is user-initiated via the stage-roadmap skill; session context
  renders the active-milestone table (without open-card counts in v1; an empty table renders
  honestly).

## Migration contract (v3 → v4)

Real projects run Stage (this repo's own `.stage`, and sibling workspaces), so the migration
is a first-class, user-facing deliverable — not an internal script an operator has to know to
find.

- **Delivered as a skill.** The migration is invoked through a `stage-migrate` skill (the CLI
  it wraps stays `migrate_stage.py`), so an end user runs it like any other lifecycle skill
  (`stage-work`, `stage-archive`). The fail-closed banner below names this skill, not a raw
  script path. The skill is transitional by nature — it exists to move v3 projects to v4 and
  carries no ongoing role after a project is on v4.
- **No version strands a v3 user (release-ordering invariant).** No shipped plugin version may
  enforce schema v4 — activate v4-only hook/scanner behavior, or reject a v3 project — unless
  that same version also ships the `stage-migrate` skill and a completed migration path. The
  consumer-adoption cards (C3–C6) therefore stay v3-compatible and dormant (the registry and
  new templates ship inert); the v4 cutover (C4/C7) and the migration skill land in the SAME
  release. A user who pulls any intermediate version keeps a working v3 project; the first
  version that speaks v4 is also the first that can migrate them to it.
- Marker: `schema_version` in `.stage/settings.json`. The v4-enforcing release supports v4
  only; on a v3 project, mutating gates deny with a banner naming the `stage-migrate` skill;
  the migration itself and read-only audit remain callable on v3.
- One command (extends `migrate_stage.py`, surfaced by the `stage-migrate` skill), driven
  entirely by the registry relocation map (which includes `past/` → `official/`):
  1. Preflight: refuse dirty tree (`.runtime/` exempt), symlinked `.stage` roots,
     case-insensitive destination collisions, and any pending promotion machinery —
     `.runtime/intents/` must hold zero pending intent and claim files and no legacy
     `promote-intent.json` may exist (the command reports blocking intents with instructions
     to complete or discard them). Mixed populated topology is a hard error with manual
     instructions.
  2. Write the maintenance marker (under `.runtime/`); v4 hooks deny writes while it exists.
     The command instructs the operator to close other agent windows first.
  3. Relocate via `git mv`, recording every relocation in a journal; content moves verbatim.
     Durable machine-readable path fields (`promotes:`, decision/retrospective references,
     scope entries) and exact recognized topology references inside moved markdown are
     rewritten through the relocation map; ambiguous customized sections fail the run. The
     project `index.md` topology section is patched only when structurally recognizable;
     otherwise the command fails and emits a proposed merge file (a competing permanent index
     file would violate SSOT).
  4. Stage changes only — never auto-commit; the operator commits with a provided message.
     Pre-commit rollback = restore staged/working tree; post-commit rollback = revert.
  5. Post-relocation verification: no machine-readable field or live doc link still targets
     `.stage/past/`, `.stage/present/`, or `.stage/future/`. Stamp `schema_version: 4` only
     after this passes; then run strict audit and fail loudly (restoring the v3 marker) if not
     clean.
  6. Abort mode restores migration-owned staged changes deterministically. Resume mode is
     deferred (restart-after-abort is sufficient at current migration sizes).
- Empty legacy roadmap dirs (the common case) migrate as directory renames.
- Long-lived branches with `.stage` changes under old paths must rebase onto the migration
  commit and translate paths through the relocation map; strict audit before merge.

## Defenses: shipped vs deferred

| Defense | v4 | Trigger to revisit |
|---|---|---|
| Legacy-root denial gate (deny writes under recreated `past/`/`present/`/`future/`) | shipped | — |
| Dogfood release sequence doc (fixtures first; migrate own `.stage` only after v4 install) | shipped | — |
| Branch-merge guidance | shipped | — |
| Migration journal + abort | shipped (minimal) | resume mode after first real interruption |
| `stage-migrate` user-facing skill + no-stranding release ordering | shipped (with C7) | — |
| Bridge release (v3 hook recognizing v4 and denying) | deferred | first stale-plugin incident or multi-host support |
| Lifecycle claims protocol (closure race) | deferred | multiple concurrent operators, or observed closure drift |

## Implementation cards

| Card | Kind | Venue | Scope | Depends on |
|---|---|---|---|---|
| C1 | design | claude | this document | — |
| C2 | development | codex | `stage_topology` registry, schema marker, maps, resolvers, D-legacy compat, official-zone predicate rename in `stage_paths` | C1 |
| C3 | development | codex | v4 template tree; TH/M templates and indexes | C2 |
| C4 | development | codex | hooks, scanners, audit, context on registry; legacy-root denial; lifecycle views. **Stays v3-compatible/dormant — gated on `schema_version`; does NOT enforce v4 until the C7 release.** | C3 |
| C5 | development | codex | register/start/close/archive CLIs; stage-work milestone question (dormant until cutover) | C4 |
| C6 | development | codex | stage-roadmap skill, decision chains, closure snapshot/revalidation, re-attribution gate, roadmap audits, session table | C4, C5 |
| C7 | development | codex | migration command + **`stage-migrate` skill** (preflight incl. zero-pending-intents, maintenance marker, journal/abort, durable-field and link rewrite, post-relocation verification, marker-last audit). **This is the release that activates v4 enforcement — it and the migration skill ship together (no-stranding invariant).** | C3-C6 |
| C8 | qa | codex | end-to-end fixtures: v3 migration, customized files, abort, stale roots, Contract X, closure, dogfood rehearsal | C7 |
| C9 | documentation | claude | concept-layer rewrites (index, operations trio, skills, READMEs, BLUEPRINT), migration/branch/dogfood guidance | C8 |

One release carries schema v4 and roadmap semantics together: they form one schema contract,
and users migrate once. Intermediate cards (C3–C6) may ship to main as dormant, v3-compatible
increments, but no shipped version enforces v4 before the C7 release that carries the
`stage-migrate` skill.

## Residual risks

- Cached v3 hosts can recreate legacy topology — revisit with the bridge release on first
  incident.
- Interrupted migrations lack resume — revisit after a real interruption.
- Closure revalidation retains a concurrency window — revisit with lifecycle claims when
  multiple writers are supported.
- Roadmap process may outweigh solo-scale value — revisit if the next 20 W cards produce
  fewer than two milestones.
- Derived scans may slow at scale — revisit with a rebuildable index (stdlib sqlite) at
  hundreds of cards.
