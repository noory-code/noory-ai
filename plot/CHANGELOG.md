# Changelog

All notable changes to Plot are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.16.34] — 2026-05-13

Fix page-load refetch storm. After user reported "Foundation nodes
appear briefly then disappear; need to reload to see them again",
server log showed the GET 3-call set (`/projects` →
`/projects/{id}` → `/projects/{id}/canvases/foundation`) repeating
dozens of times per page load — an infinite refetch loop.

Root cause: ``upgrade_foundation_canvas_if_needed`` step 4
(``migrate.py:834``) — a pre-v0.13 migration that synthesises a
``kind=project`` anchor node when ``canvas.json`` has none — fires
on *every* read for v0.13+ projects. The synthesised node is then
immediately removed by ``_evict_legacy_project_anchor``
(``folder_io.py:478``) on the same read because v0.13 Phase 0
moved the anchor to ``ProjectDoc.anchors``. Both functions write
the file, the watcher fires, the broadcast triggers a viewer
refetch, the next read repeats the cycle.

The two functions are running in opposing directions every read
because the v0.13 Phase 0 migration left step 4 in place without
gating it on the new anchor location.

Fix: guard step 4 on ``ProjectDoc.anchors[canvas_kind]``. When
``project.json`` already carries an anchor for foundation, step 4
short-circuits — no node synthesis, no write, no watcher fire.
Pre-v0.13 projects (no ``anchors`` field) still get the original
synthesis behaviour, preserving backward compatibility.
(D-2026-05-13-K)

### Fixed

- ``plot/plot_mcp/migrate.py:upgrade_foundation_canvas_if_needed``
  step 4 — added ``_project_doc_has_anchor`` guard so the legacy
  pre-v0.13 anchor synthesis no-ops when v0.13 Phase 0 has already
  migrated the anchor to ``ProjectDoc.anchors``.

### Added

- ``plot/tests/test_migrate.py`` — two regression tests:
  - ``test_upgrade_foundation_is_idempotent_when_anchor_in_project_doc``
    pins the new guard (no write on idempotent re-call when the
    anchor lives in project.json).
  - ``test_upgrade_foundation_still_synthesises_anchor_for_pre_v013_project``
    pins backward compat — pre-v0.13 projects still get synthesis.

### Verification

- plot_mcp pytest — 276 / 276 (274 → 276, +2 new tests).
- plot_mcp mypy — clean.
- plot_mcp ruff — clean.
- viewer tsc — clean.
- kill-switch (pre_commit_gate) — 11 / 11.

### Hands-on (Gate 3 — pending user verification)

User to verify in real Chrome after MCP HTTP server restart:
- page hard reload (Cmd+Shift+R)
- server log: GET 3-call set fires *once* on page load + idle
  silence afterward (no storm).
- Foundation nodes appear and stay visible.
- No console 422 storm.

## [0.16.33] — 2026-05-13

Vision pin for PRODUCT_SPEC §15 #2 Phase 2 (D-2026-05-12-A
deferral) reopening. User pinned a 4-point design vision during
Foundation hands-on testing:

1. JSON = SSOT (co-equal storage abolished).
2. JSON value = MD-formatted string (typed-text fields inside
   JSON, viewer edits via MD editor).
3. MD extraction = explicit button (no auto-sync).
4. Extraction unit = canvas (per-node MD files abolished, single
   MD file per canvas).

User direction 2026-05-13: *"이건 내일 논의해봅시다"* — today
ships vision pin only (docs); detail discussion (editor UX /
line-break handling / per-canvas layout / migration path / button
placement / idempotence / regression guard) and implementation
deferred to next session under the ``JSON SSOT 논의`` trigger.
(D-2026-05-13-J)

### Changed

- ``plot/docs/PRODUCT_SPEC.md`` §15 #2 — 4-point vision inlined;
  status transitioned from "deferred" to "in-discussion 2026-05-13".
- ``plot/docs/DECISIONS.md`` — D-2026-05-13-J entry (Pending —
  vision locked, detail decisions deferred to next session).
- ``plot/docs/NEXT_SESSION.md`` — new ``JSON SSOT 논의`` Active
  queue entry at the top, with the 7 open detail questions.

### Out of scope

- No code changes (no folder_io / models / api_endpoints / viewer
  edits). Phase 2 implementation deferred to next session.

## [0.16.32] — 2026-05-13

End-of-session bookkeeping. Pin user hands-on confirmation of
v0.16.24 anchor visual restoration + RF interaction working
correctly (D-2026-05-13-H). File two silent state inconsistencies
surfaced by automated page probe as a new lower-priority NEXT_SESSION
queue entry (D-2026-05-13-I): (1) console 422 storm with
``e_``-prefixed unknown node ids, (2) ``services/canvas.json`` orphan
edge with ``None`` endpoints. User interaction confirmed working —
neither of these surface visibly in the user's session, but both are
real data-integrity issues that should be fixed before next major
release.

### Changed

- ``plot/docs/NEXT_SESSION.md`` — RF 움직임 entry archived to
  Completed; new `잔여 silent state` entry added at top of Active
  queue for the 422 storm + orphan edge.
- ``plot/docs/DECISIONS.md`` — D-2026-05-13-H (hands-on confirm)
  and D-2026-05-13-I (silent state filing) entries.

## [0.16.31] — 2026-05-13

Skill classification correction. Plot's plugin-skill directory
``plot/skills/`` is meant for **end-user** skills that trigger in
the *consumer's* project after installing the Plot plugin. Seven
of the eight skills there were actually **dev-facing** — they
trigger during Plot's *own* development and have no meaning to a
plugin consumer. Moving them to the monorepo-level
``noory-ai/.claude/skills/`` aligns the boundary: the plugin
manifest exposes only what a consumer actually needs; the dev-tool
procedures live in the monorepo's Claude Code workspace where they
trigger when working *on* Plot. (D-2026-05-13-G)

### Removed (moved out of plot/skills/)

The following moved to ``noory-ai/.claude/skills/`` via
``git mv`` (audit-trail preserved):

- ``plot-entity-template/`` (was v0.16.25 D-2026-05-13-B)
- ``plot-domain-design/`` (was v0.16.26 D-2026-05-13-C)
- ``plot-feature-tdd/``
- ``plot-frontend-bug-diagnosis/``
- ``plot-i18n-audit/`` (was v0.16.9 D-2026-05-12-L)
- ``plot-code-red-team/`` (was v0.16.7 D-2026-05-12-J)
- ``plot-design-red-team/`` (was v0.16.8 D-2026-05-12-K)

### Retained in plot/skills/ (end-user facing)

- ``plot-help/`` — Plot usage explanation.
- ``plot-new-sketch/`` — consumer creates a new sketch.
- ``plot-read-sketch/`` — consumer reads an existing sketch.

### Changed

- All cross-references inside the 7 moved SKILL.md files updated:
  ``(../../X)`` → ``(../../plot/X)`` to point from the new location
  back into the plot/ subdirectory.
- ``plot-entity-template/SKILL.md`` ``feedback_no_god_object``
  cross-reference converted from a broken cross-home filesystem
  link to plain-text reference (auto-memory paths are user-home
  specific and cannot be relative-linked from a monorepo file).

## [0.16.30] — 2026-05-13

Docs follow-up to v0.16.24-29 catch-up batch. Update
``NEXT_SESSION.md`` "RF 움직임" trigger entry to reflect:
- Anchor visual is now **restored** (v0.16.24, D-2026-05-13-A) —
  Open Question 3 is closed.
- Baseline for next-session diagnosis is **v0.16.29** with 461 / 461
  viewer tests + all 5 D-2026-05-12-B catch-up artefacts shipped.
- Reference plan switched from
  ``~/.claude/plans/dazzling-inventing-boole.md`` (historical
  rollback plan, now an over-reach reference) to
  ``~/.claude/plans/sparkling-discovering-blanket.md`` (current
  plan, Step 3 layer kill-switch bisect is the diagnosis entry).
- Recovery-commit list trimmed to currently-live commits.

### Changed

- ``plot/docs/NEXT_SESSION.md`` — RF 움직임 entry refreshed for the
  post-v0.16.24 baseline.

## [0.16.29] — 2026-05-13

Fifth and final of 5 deferred D-2026-05-12-B catch-up artefacts. Add
a row to ``plot/CLAUDE.md`` §Anti-patterns: *"Treating raw JSON as a
domain entity (no fromJson boundary)"*. Cross-references the
``plot-entity-template`` skill (Phase A), ``no-god-import.test.tsx``
(Phase C), ``entity-roundtrip.test.tsx`` (Phase D), and server-side
``test_schema_parity.py``. Closes the D-2026-05-12-B candidate list.
(D-2026-05-13-F)

### Added

- ``plot/CLAUDE.md`` — anti-pattern table row 11 ("Treating raw JSON
  as a domain entity").

## [0.16.28] — 2026-05-13

Fourth of 5 deferred D-2026-05-12-B catch-up artefacts. Add
``viewer/tests/entity-roundtrip.test.tsx`` — vitest static guard
verifying ``parseEntity(createBlankNode(kind, base)).toJson() ===
createBlankNode(kind, base)`` for every NodeKind. Catches silent
field drift between ``fromJson`` and ``toJson`` (a field added in
one and missed in the other) before the regression reaches the
React Flow render path. Companion to no-god-import (Phase C) and
test_schema_parity (server side). (D-2026-05-13-E)

### Added

- ``viewer/tests/entity-roundtrip.test.tsx`` — 16 sub-tests:
  - 15 per-kind round-trip (parseEntity ∘ toJson is identity).
  - 1 dispatch coverage (parseEntity accepts every NodeKind).

### Verification

- viewer vitest — 461 / 461 (445 → 461, +16).

## [0.16.27] — 2026-05-13

Third of 5 deferred D-2026-05-12-B catch-up artefacts. Add
``viewer/tests/no-god-import.test.tsx`` — static guard enforcing the
v0.15 Phase 2.10 invariant that ``viewer/src/types.ts`` re-exports
``SketchNode`` from the discriminated union rather than declaring a
god interface. Plus per-kind file existence + ``{Kind}Json`` export +
``registerKindParser`` call. Together with ``test_schema_parity.py``
(server side) and the upcoming ``entity-roundtrip.test.tsx`` (Phase D),
keeps the domain layer intact. Hook semantics realised via existing
``pre_commit_gate.py`` running vitest on every viewer commit.
(D-2026-05-13-D)

### Added

- ``viewer/tests/no-god-import.test.tsx`` — 46 sub-tests (1 anti-god
  + 15 file-exists + 15 Json-export + 15 registerKindParser).

### Verification

- viewer vitest — 445 / 445 (399 → 445, +46).
- New guard fails cleanly on regression (verified by inspection of
  assertion messages).

## [0.16.26] — 2026-05-13

Second of 5 deferred D-2026-05-12-B catch-up artefacts. Add
``plot/skills/plot-domain-design/SKILL.md`` — the **gate** that forces
the placement decision *before* any code lands. Five-decision walk
(thing-vs-rule / entity-vs-value / existing-kind-reuse / bounded-context
home / SSOT location) writes a Decision summary into DECISIONS.md
*before* implementation begins. The v0.13.3-v0.13.10 cursor saga was
caused by no domain map; this skill is the framework that saga lacked.
(D-2026-05-13-C)

### Added

- ``plot/skills/plot-domain-design/SKILL.md`` — procedure skill.

## [0.16.25] — 2026-05-13

First of 5 deferred D-2026-05-12-B candidate artefacts. Add
``plot/skills/plot-entity-template/SKILL.md`` — the single procedure
SSOT for adding a new domain entity (a new ``kind``) end-to-end.
14-step walk covers CONCEPTS / SPEC / domain class with ``fromJson`` /
union extend / factory / Pydantic model / schema-parity / per-kind
renderer / per-kind inspector / registry / i18n / round-trip test /
structural-guards. User direction 2026-05-12: *"필요하다면 스킬이나
룰을 만들구요"* (D-2026-05-12-B), surfaced as overdue 2026-05-13.
(D-2026-05-13-B)

### Added

- ``plot/skills/plot-entity-template/SKILL.md`` — procedure skill.

## [0.16.24] — 2026-05-13

Restore the v0.16.20-23 "RF 기본 동작 rollback" batch as a single
``git revert`` of all four commits (``ac35021`` v0.16.23, ``32f3dc5``
v0.16.22, ``7edbbf8`` v0.16.21, ``75ee0b0`` v0.16.20). User direct
correction "다 복구 하라" after the prior batch was identified as
over-reach (NEXT_SESSION.md:22-24). The original triggering message
"그냥 RF 기본 동작으로 동작하게 해주세요" had been interpreted as
"remove the synthetic anchor and all its visual layers"; the user's
actual intent was "keep the anchor + make *interaction* feel like
stock React Flow". (D-2026-05-13-A)

### Added (restored)

- ``viewer/src/canvases/edges/SelfLoopEdge.tsx`` — custom edge for
  ``source === target`` (arc rendering).
- ``viewer/src/canvases/edges/registry.ts`` — edge type registry.
- ``viewer/src/canvases/sketch/anchorRadialLayout.ts`` — 120°
  auto-radial slot computation for Foundation new nodes.
- ``viewer/src/canvases/sketch/applyAnchorChange.ts`` — anchor PATCH
  diff helper.
- ``viewer/src/lib/anchorOptimistic.ts`` — optimistic local update on
  anchor drag / resize.
- ``viewer/tests/anchor-drag-snap-back.test.tsx`` — 7 tests.
- ``viewer/tests/foundation-radial-layout.test.tsx``.
- ``viewer/tests/self-loop-render.test.tsx``.

### Changed (restored to v0.16.19 state)

- ``viewer/src/canvases/sketch/useNodesMemo.ts`` — synthetic anchor
  injection block + ``projectAnchor`` / ``projectName`` /
  ``onAnchorChange`` props restored.
- ``viewer/src/canvases/SketchCanvas.tsx`` — ``edgeTypes`` prop +
  anchor props + ``applyAnchorRadialLayout`` prop restored.
- ``viewer/src/canvases/FoundationCanvas.tsx`` /
  ``ActorsCanvas.tsx`` / ``ServicesCanvas.tsx`` — ``injectAnchor={true}``
  restored.
- ``viewer/src/canvases/ServiceDetailCanvas.tsx`` —
  ``injectAnchor={false}`` restored.
- ``viewer/src/canvases/sketch/useNodeCreation.ts`` —
  ``applyAnchorRadialLayout`` argument restored.
- ``viewer/src/canvases/sketch/edgeTransform.ts`` — ``isRealSelfLoop``
  branch restored.
- ``viewer/src/App.tsx`` — ``handleAnchorChange`` useCallback +
  ``onAnchorChange`` prop wiring restored.
- ``docs/SPEC.md`` — §Anchor / §Edges Self-loops / §Foundation
  Anchor-radial sections restored.
- ``docs/DECISIONS.md`` — D-2026-05-13-A entry; D-2026-05-12-V/W/X/Y
  removed by revert (their decisions are now Rejected as documented
  in D-2026-05-13-A).
- ``docs/ROADMAP.md`` — anchor / self-loop / radial archived entries
  removed by revert.

### Removed (the previous batch's removals undone)

- v0.16.20-23 removals (anchor injection, radial layout, self-loop,
  PATCH path) are no longer in effect. See "Added (restored)" above.

### Known unresolved

- Interaction "엉망" — the *actual* user complaint that originally
  triggered both v0.16.15-19 and v0.16.20-23 — is **not** addressed
  by this revert. v0.16.19 (anchor present) and v0.16.23 (anchor
  absent) both exhibited the issue. Diagnosis happens in the next
  session under the ``RF 움직임`` trigger (NEXT_SESSION.md).

## [0.16.19] — 2026-05-12

Minor stability — ``handleAnchorChange`` extracted from inline JSX
to a top-level ``useCallback``. ``useNodesMemo`` 's synthetic anchor
node carries an inline ``data.onResize`` that delegates to
``onAnchorChange``; by stabilising the source ref, the memo's
``data`` object now only rebuilds when anchor-relevant state
actually changes (projectPath / activeId / activeTab / summaries /
project), not on every App render. Closes the 5-commit React Flow
regression-fix batch (v0.16.15-19). (D-2026-05-12-U)

### Changed — viewer/src/App.tsx

- Inline ``onAnchorChange`` JSX arrow (17 lines) extracted into
  top-level ``handleAnchorChange = useCallback(...)``.
- JSX site uses the stable reference: ``onAnchorChange={handleAnchorChange}``.
- LOC: 380 → 385 (within 400 ceiling).

### Tests

No new dedicated test; existing ``anchor-drag-snap-back.test.tsx``
(7) + ``stable-handlers.test.tsx`` (5) cover both behaviour and
identity-stability patterns this commit applies.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 399 / 399 passed (no test count change).
- ``uv run pytest`` — 274 / 274.

### Batch closure (v0.16.15-19)

Five commits ship the React Flow regression-fix batch surfaced by
user hands-on review of v0.16.14:

| # | Fix | Decision | Tests |
|---|---|---|---:|
| 1 | Anchor drag snap-back | D-2026-05-12-Q | 7 |
| 2 | Refetch storm | D-2026-05-12-R | 5 |
| 3 | Cmd+A controlled contract | D-2026-05-12-S | 2 |
| 4 | fitView mid-session reset | D-2026-05-12-T | 2 |
| 5 | Anchor data.onResize stability | D-2026-05-12-U | (covered) |

Viewer tests: 383 → 399 (+16). Server: 274 / 274 unchanged.

Plugin patch bump 0.16.18 → 0.16.19.

## [0.16.18] — 2026-05-12

Bug fix — fitView gating. ReactFlow's ``fitView`` prop re-fits
whenever the ``nodes`` reference changes; Plot's ``useNodesMemo``
returns a fresh array every render, so the user's manual zoom/pan
was reset mid-session by every unrelated state update. Fix: drop
the prop, call ``inst.fitView({ padding: 0.2 })`` once inside
``onInit``. Canvas tab switches still re-fit because the wrapper
has ``key={activeCanvasKey}`` → remount → onInit fires.
(D-2026-05-12-T)

### Changed — viewer/src/canvases/SketchCanvas.tsx

- Remove ``fitView`` + ``fitViewOptions`` props from
  ``<ReactFlow>``.
- ``onInit`` now invokes ``inst.fitView({ padding: 0.2 })`` once.

### Added — viewer/tests/viewport-stability.test.tsx

2 static-grep guards:
- No top-level ``fitView`` prop on ``<ReactFlow ...>``.
- ``onInit`` JSX form present and contains an
  ``inst.fitView(...)`` call.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 399 / 399 passed (397 prior + 2 new).
- ``uv run pytest`` — 274 / 274.

Plugin patch bump 0.16.17 → 0.16.18.

## [0.16.17] — 2026-05-12

Bug fix — Cmd+A respects controlled-component contract. Previously
Cmd+A flipped RF's internal ``selected`` flag via ``setNodes`` /
``setEdges``, but never synced ``selectedNodeIds.current`` (the
SketchCanvas ref the clipboard reads). Cmd+C / Cmd+D following
Cmd+A copied / duplicated the *previous* selection, not "all nodes".
Fix: write ``selectedNodeIds.current = inst.getNodes().map(n => n.id)``
after the store mutation. (D-2026-05-12-S)

### Changed — viewer/src/canvases/sketch/useKeyboardShortcuts.ts

- Cmd+A branch: after ``setNodes``/``setEdges``, sync
  ``selectedNodeIds.current`` from the RF store.

### Added — viewer/tests/select-all-sync.test.tsx

2 tests:
- Cmd+A populates ``selectedNodeIds.current`` with all rendered
  node ids + RF store ``selected`` flag flips for all nodes.
- Cmd+C after Cmd+A copies the full set (via clipboard mock).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 397 / 397 passed (395 prior + 2 new).
- ``uv run pytest`` — 274 / 274.

Plugin patch bump 0.16.16 → 0.16.17.

## [0.16.16] — 2026-05-12

Bug fix — refetch storm. Playwright session recording showed 404 GETs
to the same 3 endpoints in a single idle browser session. Cause:
App.tsx passed inline arrow closures to ``useProject`` / ``useCanvasPersist``
/ ``useProjectSocket``; those closures were recreated every render,
which under specific WS event timings produced a fetch chain that
re-triggered on each iteration. Fix: ``useStableHandlers`` hook returns
``useCallback``-wrapped post-project handlers; pre-project handlers
(``handleError`` / ``handleActiveIdChange``) are inlined as direct
``useCallback`` in App.tsx. (D-2026-05-12-R)

### Added — viewer/src/hooks/useStableHandlers.ts

Returns ``useCallback``-wrapped:
- ``handleListStale`` — calls ``loadList``.
- ``handleExternalCanvas`` — Map-set into ``setCanvasCache``.
- ``handleTagsRefresh`` — passes through to ``setTags``.
- ``handleExternalChange`` — calls ``historyClear``.

### Changed — viewer/src/App.tsx

- Pre-project handlers (``handleError``, ``handleActiveIdChange``)
  defined as ``useCallback`` before ``useProject`` is invoked.
- Post-project handlers come from ``useStableHandlers`` (single
  destructure).
- ``useProject`` destructure compacted onto fewer lines.
- LOC: 393 → 380.

### Added — viewer/tests/stable-handlers.test.tsx

5 tests:
- Identity stability across re-renders when deps are stable.
- Identity change when ``loadList`` reference changes (correct
  recompute behaviour).
- ``handleExternalCanvas`` produces the right Map-updater.
- ``handleExternalChange`` calls ``historyClear``.
- ``handleListStale`` invokes ``loadList``.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 395 / 395 passed (390 prior + 5 new).
- ``uv run pytest`` — 274 / 274 (no server change).

### Why this wasn't caught by v0.15 structural guards

The structural-guards test (D-2026-05-12-F) is *static* — it checks
file shape, LOC ceilings, registry completeness, no-god-dispatch.
Callback identity stability is a *runtime* concern that no static
guard can detect; it surfaces only under hands-on use. The lesson
will go into the future v0.17+ "RF integration test layer" (filed
in ROADMAP) — runtime regression tests via Playwright.

Plugin patch bump 0.16.15 → 0.16.16.

## [0.16.15] — 2026-05-12

Bug fix — anchor drag snap-back. User dragging the synthetic project
anchor on Foundation / Actors / Services canvases would briefly snap
back to its pre-drag position during the 100-500ms server PATCH
round-trip. Cause: ``summaries`` state only updated *after* the PATCH
resolved, so React Flow's controlled ``nodes`` prop rendered the OLD
anchor placement during the gap. Fix: optimistic local update before
the network call, with revert on PATCH failure. (D-2026-05-12-Q)

### Added — viewer/src/lib/anchorOptimistic.ts

- ``applyOptimisticAnchorPatch(current, tab, patch): ProjectDoc`` —
  pure helper that merges an anchor patch into a ProjectDoc.
- ``resolveAnchorPlacement(proj, tab): AnchorPlacement`` — same
  fallback logic as App.tsx's resolveProjectAnchor, extracted for
  helper-internal use.

### Changed — viewer/src/App.tsx

- ``onAnchorChange`` handler:
  - Captures the previous ProjectDoc before mutation.
  - Calls ``replaceSummary(applyOptimisticAnchorPatch(...))`` *before*
    ``patchProjectAnchor``.
  - On PATCH success, ``replaceSummary(refreshed)`` with server doc.
  - On PATCH failure, ``replaceSummary(previous)`` to revert.
- LOC: 381 → 393 (under 400 ceiling per structural-guards).

### Added — viewer/tests/anchor-drag-snap-back.test.tsx

7 tests covering:
- x/y patch preserves other anchor fields.
- Missing-anchors project gets a default-fallback patch.
- Patching foundation leaves actors anchor untouched.
- Dimension-only patch preserves position.
- Revert path (``previous`` reference unchanged by merge).
- ``resolveAnchorPlacement`` default + stored variants.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 390 / 390 passed (383 prior + 7 new).
- ``uv run pytest`` — 274 / 274 (no server change).

### Series context

First of a 5-commit React Flow regression-fix batch (v0.16.15-19)
prompted by user hands-on review of v0.16.14. The batch addresses
multiple React Flow misuse patterns surfaced when the user dragged
the anchor: snap-back here, refetch storm (v0.16.16), Cmd+A
controlled-contract violation (v0.16.17), fitView mid-session resets
(v0.16.18), anchor data.onResize stability (v0.16.19).

Plugin patch bump 0.16.14 → 0.16.15.

## [0.16.14] — 2026-05-12

Docs-only — end-of-session wrap-up. Three remaining parked-backlog
items (isomorphic-git / work-item layer / repo split) are filed
in ``ROADMAP.md`` §"v0.17+" **with the ``plot-design-red-team``
8-attack findings inlined per item** so the next implementer
walks into pinned design questions instead of fresh discovery.
``NEXT_SESSION.md`` queue is empty pending user hands-on review
of the v0.16 ship.

### Changed — plot/docs/ROADMAP.md

- New top section "v0.17+ — Roadmap items (queued, design
  red-team findings inline)" listing:
  - **A) isomorphic-git source-data version control** — 6 Major
    findings need DECISIONS answers (UI vocab / .git location /
    agent commit identity / conflict resolution UX / commit
    granularity / MVP scope cut). Spec mandate quoted. 2-4 weeks
    estimated, 8-12 commits.
  - **B) Work-item layer (userstory + task)** — hard dep on A.
    4 Major findings (file locations / origin-metadata schema /
    orphan handling / MVP schema cut). 1-2 weeks after A.
  - **C) Plot repository split** — product decision the user
    owns. Technical side: 🟢 READY (one-time ``git filter-repo``).

### Changed — plot/docs/NEXT_SESSION.md

- Active queue empty; entry text points at ROADMAP §"v0.17+".
- Trigger phrases listed for each ROADMAP item so re-entry is
  one phrase away.
- First-priority next-session task = user-driven hands-on review
  of v0.16 ship.

### This session scorecard (v0.15.7 → v0.16.13, 19 commits)

| Track | Commits | Outcome |
|---|---:|---|
| v0.15 Phase 4-5 (검증) | 5 | reset COMPLETE; 8 acceptance gates + kill-switch |
| App.tsx split | 5 | 811 → 381 LOC, ceiling locked at 400 |
| Schema parity test | 1 | 15-kind Pydantic ↔ TS pinned |
| Red-team skills | 2 | code + design SKILL.md |
| First red-team dogfood (i18n-audit) | 1 | 6 findings → revised before code |
| Self-loop visual | 1 | SelfLoopEdge custom edge type |
| Foundation anchor-radial | 1 | Mission/CV/Id radial slots |
| Kill-switch cleanup | 1 | canvas_kind → wrapper prop |
| Owner field | 1 | BaseNodeFields multi-user prep |
| End-of-session wrap | 1 | this commit |

viewer 383/383 + server 274/274 + kill-switch 11/11. tsc / mypy /
ruff all clean.

Plugin patch bump 0.16.13 → 0.16.14.

## [0.16.13] — 2026-05-12

Multi-user prep — ``owner: str | None`` (default ``null``) added
to ``BaseNodeFields`` (Pydantic) and ``BaseFieldsJson`` / ``BaseFields``
(TS). Inherited by all 15 entity classes. Wire-format only — no UI,
no permission logic, no migration. Single-user sessions write
``null``; server will fill from session context once multi-user
ships. Canonical Plot spec §"데이터 구조 원칙":
> "owner 필드 포함 (멀티유저 확장 대비)."
(D-2026-05-12-P)

### Changed — plot_mcp/models.py

- ``BaseNodeFields.owner: str | None = None`` after ``details_path``.

### Changed — viewer/src/domain/BaseFields.ts

- ``BaseFieldsJson`` + ``BaseFields`` interfaces gain
  ``owner: string | null``.
- ``parseBaseFields`` reads ``obj.owner`` with null default
  (using existing ``asNullableString`` helper).

### Changed — viewer/src/domain/{15 entity files}

Each entity class adds:
- ``readonly owner!: string | null;`` declaration after
  ``readonly details_path!: string | null;``.
- ``owner: this.owner,`` line in ``toJson`` after ``details_path``.

(``Object.assign(this, base)`` in each constructor already copies
the new field through from ``parseBaseFields``; no per-class
fromJson change needed.)

### Changed — tests/test_schema_parity.py

- ``_EXPECTED_BASE_FIELDS`` gains ``"owner"`` so the 2-anchor +
  15-per-kind parity tests assert agreement on the new field.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 383 / 383 passed.
- ``uv run pytest`` — 274 / 274 (schema parity now asserts the
  14-field BaseFields canonical set on both sides).
- ``uv run mypy plot_mcp/`` — clean.
- ``uv run ruff check`` — clean.
- ``test_pre_commit_gate.py`` — 11 / 11 (kill-switch happy).

Plugin patch bump 0.16.12 → 0.16.13.

## [0.16.12] — 2026-05-12

Kill-switch cleanup — v0.16.11 (D-2026-05-12-N) introduced a
``doc.canvas_kind === "foundation"`` check in
``useNodeCreation.ts`` which the v0.15 reset's
``reset_complete_check`` kill-switch (D-2026-05-12-G) correctly
rejected on the next commit attempt. Same observable behaviour
reshipped via a wrapper-supplied prop ``applyAnchorRadialLayout``
(5th sibling to ``hideRootServiceNode`` / ``shouldDrill`` /
``showFoldButton`` / ``injectAnchor``). FoundationCanvas opts in;
other wrappers default ``false``. (D-2026-05-12-O)

### Changed — viewer/src/canvases/sketch/useNodeCreation.ts

- ``UseNodeCreationArgs`` gains optional
  ``applyAnchorRadialLayout?: boolean``.
- Inline ``current.canvas_kind === "foundation"`` removed.
- ``addNodeAt`` useCallback dep array adds the new flag.

### Changed — viewer/src/canvases/SketchCanvas.tsx

- ``SketchCanvasProps`` adds ``applyAnchorRadialLayout?: boolean``.
- Threaded into ``useNodeCreation`` call.

### Changed — viewer/src/canvases/FoundationCanvas.tsx

- Passes ``applyAnchorRadialLayout={true}``.

### Honest note

The design red-team that ran on the v0.16.11 proposal missed the
``D-2026-05-12-F structural-guards`` invariant about sketch hooks
not reading ``doc.canvas_kind``. The kill-switch caught it within
one commit; the fix is small (one prop, three line edits). The
lesson goes into ``plot-design-red-team`` Attack 2 (Unstated
invariants) as a calibration anchor.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 383 / 383 passed (no test changes).
- ``uv run pytest`` — 274 / 274.
- ``uv run pytest tests/test_pre_commit_gate.py`` — 11 / 11
  passed (kill-switch recovered).

Plugin patch bump 0.16.11 → 0.16.12.

## [0.16.11] — 2026-05-12

Foundation anchor-radial initial placement — when the user creates
a Mission / CoreValue / Identity node on the Foundation canvas, the
new node snaps to a slot on a circle of radius 320 px around the
anchor centre. Slots 120° apart for visual balance. No narrative
ordering. **Positional hint, not a constraint** — user can drag
afterward. D-2026-05-12-N.

### Added — viewer/src/canvases/sketch/anchorRadialLayout.ts

Pure helper module (~95 LOC). Exports:

- ``FOUNDATION_RADIAL_KINDS`` SSOT (the three radial kinds).
- ``isFoundationRadialKind`` type guard.
- ``anchorRadialSlot(kind, existing)`` — slot centre on the
  320 px circle.
- ``anchorRadialPosition(kind, existing, w, h)`` — top-left
  position so the node centre lands on the slot.
- ``countFoundationKinds(nodes)`` — counts of each radial kind
  in the current canvas (drives the +30° same-kind offset).

Clock-face mapping:

- Mission   →  9 o'clock (270°) — left of anchor.
- CoreValue →  1 o'clock (30°)  — upper-right of anchor.
- Identity  →  5 o'clock (150°) — lower-right of anchor.

### Changed — viewer/src/canvases/sketch/useNodeCreation.ts

- ``addNodeAt`` checks ``doc.canvas_kind === "foundation"`` AND
  ``isFoundationRadialKind(kind)``. If both true, ``x``/``y`` are
  overridden by ``anchorRadialPosition``. All other cases keep
  the caller-supplied position.

### Added — viewer/tests/foundation-radial-layout.test.tsx

15 tests covering: SSOT membership, kind-discrimination guard,
slot positions for first node of each kind, on-radius invariant
across all slots, +30° collision offset for repeat kinds,
top-left centring math, ``countFoundationKinds`` ignoring
non-radial kinds.

### Changed — docs/SPEC.md §Foundation

- New "Anchor-radial initial placement" subsection at the top
  of the Foundation section, citing the canonical spec mandate
  + D-2026-05-12-N + the D-2026-05-04-A relationship (auto-position
  is fine because user can drag; auto-edges still banned).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 383 / 383 passed (368 prior + 15 new).
- ``uv run pytest`` — 274 / 274 (no server change).

Plugin patch bump 0.16.10 → 0.16.11. Second of the 3-item
parked-backlog batch.

### Note on v0.16.12 (originally planned)

The third batch item (Service-Detail Mermaid panel) was **dropped**.
User clarification 2026-05-12: Service-Detail's
*"다이어그램 시각화"* is the existing React Flow canvas itself
(actor refs + their relationships + rule/content composition).
Not a separate Mermaid chart. ``ServiceDetailCanvas`` already
serves that role; no panel work needed.

## [0.16.10] — 2026-05-12

Self-loop visual rendering — user-drawn edges with
``source === target`` now render as a curved Bezier arc instead of
being silently dropped. The canonical Plot spec
(*"셀프 피드백 루프 표현 가능 (서비스 A → 서비스 A)"*) explicitly
permitted them; the previous ``edgeTransform.ts:40`` filter was a
spec violation. Plan ``~/.claude/plans/dazzling-inventing-boole.md``,
decision **D-2026-05-12-M**.

### Added — viewer/src/canvases/edges/SelfLoopEdge.tsx

- React Flow custom edge component. Cubic Bezier arc from source
  to target with two control points bulged 100 px above. Click-able,
  selectable, deletable like any edge. Label renders at the arc's apex.
- Exports ``selfLoopPath`` pure helper (the math is the
  worth-protecting part) for unit testing.

### Added — viewer/src/canvases/edges/registry.ts

- ``EDGE_TYPES`` SSOT (mirrors ``nodes/registry.ts`` pattern).
  Single entry today (``selfLoop``); future edge types extend here.

### Changed — viewer/src/canvases/sketch/edgeTransform.ts

- Filter at line 40 split into two cases:
  - **Real self-loop** (``e.source === e.target``) → emit with
    ``type: "selfLoop"``. Renders via ``SelfLoopEdge``.
  - **Pseudo self-loop** (``e.source !== e.target`` but both
    collapse to the same id) → filter (preserves pre-v0.16.10
    behaviour for collapsed subtrees).
- Collapsed-ancestor filter (line 39) unchanged.

### Changed — viewer/src/canvases/SketchCanvas.tsx

- ``ReactFlow`` now receives ``edgeTypes={EDGE_TYPES}``.

### Added — viewer/tests/self-loop-render.test.tsx

7 tests:
- Real self-loop → ``type: "selfLoop"`` emitted with label + value-flow.
- Pseudo self-loop (collapsed) → filtered (2 cases: both-collapse,
  one-side-collapse-to-other).
- Regular cross-node edge → no ``type`` (default Bezier).
- ``selfLoopPath`` → non-degenerate arc from zero-distance input;
  cubic Bezier shape preserved with different source/target.

### Changed — docs/SPEC.md §Edges

- New "Self-loops (source === target)" subsection citing the canonical
  Plot spec mandate + D-2026-05-12-M.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 368 / 368 passed (361 prior + 7 new).
- ``uv run pytest`` — 274 / 274 (no server change).

Plugin patch bump 0.16.9 → 0.16.10. First commit in the 3-item
parked-backlog batch (v0.16.10 — self-loop / v0.16.11 — Foundation
anchor-radial / v0.16.12 — Service-Detail Mermaid panel).

## [0.16.9] — 2026-05-12

New skill — ``plot-i18n-audit`` runs 4 static audits on the viewer
codebase for i18n compliance per ``feedback_plot_global_service`` +
D-2026-05-11-D. **First dogfood of the v0.16.8 ``plot-design-red-team``
skill** — the v1 proposal was design-reviewed before implementation;
6 findings (3 Major + 3 Minor) forced revisions before ship.
(D-2026-05-12-L)

### Added — plot/skills/plot-i18n-audit/SKILL.md

The 4 audits:
1. **Hardcoded user-facing strings** — JSX text + named attribute
   allowlist (aria-* / title / alt / placeholder / label); exemption
   rules for length ≤ 3 / NodeKind literals / brand regex
   ``^[A-Z]{2,8}$`` / MIME type / adjacent ``// i18n-skip`` comment.
2. **Undefined ``t()`` keys** — static + dynamic
   (``t(\`prefix.${var}\`)`` template-literal prefix expansion).
3. **Stale en.json keys** — zero static or dynamic-prefix references.
4. **Untranslated ko.json values** — ``ko[k] === en[k]`` AND length
   > 3 AND value ≠ key tail AND not in brand / MIME allowlist.

Output verdict: ✅ CLEAN / 🟡 FIX / 🔴 BLOCK. Audits 3-4 are
Minor; alone they never escalate verdict.

### Why now

Memory ``feedback_plot_global_service.md``
(*"이건 글로벌 서비스가 될거거든요"*, 2026-05-10) pinned i18n as
non-negotiable. ``i18n-keys-parity.test.ts`` enforces locale parity
but cannot see hardcoded strings, undefined ``t()`` calls, stale keys,
or untranslated values. This skill closes those four gaps without
TS-compiler infra.

### Process note — first red-team dogfood

The v1 proposal was reviewed via ``plot-design-red-team`` (v0.16.8)
before any SKILL.md was written. The skill returned 🟡 REVISE FIRST
with 3 Major + 3 Minor findings: fuzzy "user-facing" definition,
unhandled dynamic-key composition, over-fit untranslated check,
missing WIP escape hatch, undefined audit scope. **Every Major
finding was addressed in the revised proposal that shipped here.**
The dogfood loop was the value-add of v0.16.7 + v0.16.8: catch
proposal weaknesses before code.

### Evolution path (documented inside the skill)

- Phase 1 (now): manual invocation, manual scan, manual report.
- Phase 2: wire Audit 1 + 2 into a vitest static guard so missing
  keys / hardcoded strings fail the build.
- Phase 3: PreCommit hook gating FIX / BLOCK verdicts.
- Per ``project_red_team_review_skill.md`` philosophy: don't
  pre-build Phase 2-3; let usage shape them.

Plugin patch bump 0.16.8 → 0.16.9.

## [0.16.8] — 2026-05-12

New skill — ``plot-design-red-team`` runs 8 adversarial attacks
against a Plot proposal BEFORE implementation. Sister skill to
``plot-code-red-team`` (v0.16.7). Reads a SPEC change draft, a
DECISIONS entry draft, a plan file, or a verbal proposal and
attacks the *idea*, not the code. (D-2026-05-12-K)

### Added — plot/skills/plot-design-red-team/SKILL.md

The 8 attacks:
1. VISION re-anchor (off-essence / phase-leakage).
2. Unstated invariants (service / actor / anchor / edge
   assumptions pinned by DECISIONS).
3. Failure modes (worst-case input / timing / browser).
4. Reversibility (one-way write / user-state contamination /
   migration trap).
5. VISION / PRODUCT_SPEC alignment (canvas inventory, kind
   out-of-scope, global service).
6. Over-fit / under-fit (YAGNI vs AHA tension).
7. Hidden tradeoffs (every benefit must name what it makes harder).
8. Scope drift (implicit "and also…" additions).

Output verdict: ✅ READY TO IMPLEMENT / 🟡 REVISE FIRST /
🔴 REDESIGN.

### Why the two-skill split

Code reviews catch bad code; they don't catch bad ideas. Plot's
v0.13.2 auto-edges were good code that the user rolled back
same-day — the idea was wrong. D-2026-05-10-E auto-layout shipped
twice and was rejected twice. Catching these at the *proposal*
stage is cheaper than catching them at the diff.

The two skills together close the review loop end-to-end (proposal
→ code). Together with the v0.16.0 reset's structural guards +
v0.16.6 schema parity test, Plot now has:

- **Structural** review (8 acceptance gates + kill-switch from
  v0.16.0).
- **Schema** review (parity test from v0.16.6).
- **Code** red-team (v0.16.7).
- **Design** red-team (this commit).

### Evolution path (documented inside the skill)

Per the user's 2026-05-12 direction
(``memory/project_red_team_review_skill.md``):
*"이런 것들이 만들어지면 차차 정형화된 워크플로우로
진화되어야합니다."*

Phase 1 (now): manual invocation via trigger phrases.
Phase 2 (after several uses): hook on PR creation that nudges
"should this have run on the underlying decision?"
Phase 3 (mature): composed slash command ``/plot-propose <text>``.

Phases 2-3 are explicitly *not* pre-built; let usage shape them.

Plugin patch bump 0.16.7 → 0.16.8.

## [0.16.7] — 2026-05-12

New skill — ``plot-code-red-team`` runs 9 adversarial attacks
against a Plot branch / commit set / PR. Triggers on Korean (리뷰 /
코드리뷰 / 공격적으로 / 비판적으로) and English (review / red-team)
phrases. Output: structured report with evidence (file:line) → rule
violated → severity → suggested fix → verdict. (D-2026-05-12-J)

### Added — plot/skills/plot-code-red-team/SKILL.md

The 9 attacks, in order:
1. Diff-vs-claim (scope creep / behaviour-disguised-as-refactor).
2. Bad-faith input (null / wrong-type / path-traversal / PII).
3. Code-as-spec violations (un-specced behaviour, comments-as-spec).
4. Hidden coupling (closure state, prop-semantic drift).
5. God dispatch (micro-god in per-kind files; ``switch (node.kind)``
   regression).
6. Cross-cutting visual bundle (cognitive scapegoat).
7. LOC budget creep (file absorbing responsibility without
   admitting it).
8. Rotted comments (TODO additions, stale module references).
9. Test coverage (regression-bait, brittle tests).

Output verdict: ✅ MERGE OK / 🟡 MERGE WITH FIXES / 🔴 DO NOT MERGE.

### Why now

Memory ``project_red_team_review_skill.md`` filed the user's
direction during the v0.15 Phase 2 session: *"코드 리뷰나 설계
리뷰를 하는 스킬도 필요할 것 같구요. 이건 레드팀 처럼 비판적
시각으로 바라 볼 수 있게."* Deferred until after the v0.15 reset.
The reset shipped at v0.16.0; this is the first follow-up skill.

Sister skill ``plot-design-red-team`` (pre-implementation review)
lands in v0.16.8.

Plugin patch bump 0.16.6 → 0.16.7.

## [0.16.6] — 2026-05-12

Schema parity test — Pydantic ↔ TS XxxJson field sets pinned for
all 15 kinds. The v0.15 reset's parallel union is now machine-checked
end-to-end; field-name drift between server and viewer fails at CI
time with the offending kind named. (D-2026-05-12-I)

### Added — plot/tests/test_schema_parity.py

- 18 tests across three describe-equivalent groups:
  - 2 anchor tests pinning ``BaseNodeFields`` (Pydantic) and
    ``BaseFieldsJson`` (TS) against the canonical 13-field set
    (id / label / x / y / width / height / color / shape / icon /
    parent_id / collapsed / is_root / details_path).
  - 15 parametrised per-kind parity assertions
    (``Pydantic.model_fields.keys() == TS XxxJson field set``).
  - 1 sanity assertion that the discriminated union has exactly
    15 entries.

### Verification

- ``uv run pytest`` — 274 / 274 passed (256 prior + 18 new).
- ``uv run mypy plot_mcp/`` — clean.
- ``uv run ruff check plot_mcp/ tests/`` — clean.

Plugin patch bump 0.16.5 → 0.16.6.

## [0.16.5] — 2026-05-12

v0.16.0 follow-up — App.tsx split commit 5 of 5, **DONE**. The
plan target ``≤ 400`` LOC for App.tsx (deferred from Phase 5.2,
filed in D-2026-05-12-F) is now locked in. App.tsx 423 → 381 LOC;
``structural-guards.test.tsx`` ceiling lowered from **830 → 400**.
(D-2026-05-12-H)

### Added — viewer/src/hooks/useAvailableNodes.ts

- Derives the four cross-canvas "available master" lists from the
  canvas cache: ``availableActors`` (actors canvas, kind="actor") +
  ``availableMissions`` / ``availableValues`` / ``availableIdentities``
  (foundation canvas, kind="mission" / "core_value" / "identity").
- Replaces 4 inline ``useMemo`` blocks in App.tsx.

### Added — viewer/src/hooks/useAppKeyboard.ts

- Owns the App-shell keyboard shortcuts: ⌘/Ctrl+Z (undo), ⌘/Ctrl+
  Shift+Z / ⌘/Ctrl+Y (redo), ``?`` (toggle help), Esc (close help
  when open).
- Skips when focus is in an editable field (INPUT / TEXTAREA /
  contentEditable).

### Changed — viewer/src/App.tsx

- 423 → 381 LOC (-42).
- 4 inline ``availableX`` ``useMemo`` blocks replaced by one
  ``useAvailableNodes(canvasCache)`` call.
- 33-LOC inline keyboard ``useEffect`` replaced by ``useAppKeyboard({
  onUndo, onRedo, helpOpen, setHelpOpen })``.
- ``useEffect`` import dropped (no longer used in App).
- ``SketchNode`` type import dropped (now scoped inside
  ``useAvailableNodes``).

### Changed — viewer/tests/structural-guards.test.tsx

- ``App.tsx`` ceiling **830 → 400**. The plan target from
  D-2026-05-12-F is now enforced. Raising the ceiling requires a
  fresh ``D-YYYY-MM-DD-X`` entry that names the new responsibility
  App.tsx legitimately absorbed.

### Changed — plot/CLAUDE.md §Gate 2

- App.tsx row updated: 811 / 830 → 381 / 400.
- New rows for ``shell/*`` and ``hooks/use*`` outlining the
  per-concern split pattern.

### Changed — plot/docs/ARCHITECTURE.md

- "What's still pending" section: App.tsx ≤ 400 marked **DONE**.
  Pointer to the v0.16.1–v0.16.5 commit sequence.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 361 / 361 passed.
- ``uv run pytest`` — 256 / 256 passed (no server-side changes).
- App.tsx LOC budget assertion: 381 ≤ 400 ✓.

### App.tsx split scorecard (v0.16.1 → v0.16.5)

| Commit | App.tsx LOC | Δ | Extracted |
|---|---:|---:|---|
| v0.16.0 (baseline) | 811 | — | — |
| v0.16.1 | 715 | -96 | ``shell/Header.tsx`` |
| v0.16.2 | 564 | -151 | ``shell/CanvasTabs.tsx``, ``HelpCheatsheet.tsx``, ``states.tsx`` |
| v0.16.3 | 496 | -68 | ``shell/ServiceDetailModal.tsx`` |
| v0.16.4 | 423 | -73 | ``hooks/useUrlSync.ts`` |
| v0.16.5 | 381 | -42 | ``hooks/useAvailableNodes.ts``, ``useAppKeyboard.ts`` + ceiling lock |

Plugin patch bump 0.16.4 → 0.16.5. App.tsx no longer owns chrome
or glue — only project-level state + canvas wiring.

## [0.16.4] — 2026-05-12

v0.16.0 follow-up — App.tsx split commit 4 of 5. URL ⟷ tab /
drill / selection state pulled out of App into a new
``useUrlSync`` hook. App owns only project-level state +
canvas wiring now; tab/drill/selection live in the hook.
(D-2026-05-12-H)

### Added — viewer/src/hooks/useUrlSync.ts

A hook that owns the three browser-URL query params Plot keeps in
sync (``?canvas`` / ``?detail`` / ``?select``) and exposes:

- State: ``activeTab`` / ``detailServiceId`` / ``selectedNodeId``.
- Action: ``syncUrl`` — generic URL writer (also used by App.tsx
  to sync ``?project=<id>`` when useProject changes activeId).
- Navigation callbacks: ``selectTab`` / ``drillIntoService`` /
  ``backToOverview`` / ``jumpToActor`` / ``consumeSelection`` /
  ``focusCanvas`` (the last consumed by ``handleUndo`` / ``handleRedo``
  in App to refocus the right tab after a cross-tab undo).

### Changed — viewer/src/App.tsx

- 496 → 423 LOC (-73).
- Three ``useState`` blocks for tab/drill/selection removed.
- Six navigation callbacks (selectTab / drillIntoService /
  backToOverview / jumpToActor / consumeSelection / focusCanvas)
  removed.
- ``syncUrl`` callback removed.
- ``CANVAS_TAB_IDS`` import dropped (only used inside the hook now;
  ``CanvasTab`` type still imported for the local ``tabToKind`` helper).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 361 / 361 passed.

Plugin patch bump 0.16.3 → 0.16.4. One more extraction
(``useAvailableNodes`` + ``useAppKeyboard``) lands in v0.16.5,
followed by lowering the structural-guards ceiling from 830 to 400.

## [0.16.3] — 2026-05-12

v0.16.0 follow-up — App.tsx split commit 3 of 5. ServiceDetailModal
extracted; ``useTranslation`` import dropped from App.tsx (only
consumer was the modal). Pure JSX move, no behaviour change.
(D-2026-05-12-H)

### Added — viewer/src/shell/ServiceDetailModal.tsx

- ``ServiceDetailModal`` — overlay that mounts ServiceDetailCanvas
  on top of the still-mounted services canvas (v0.12 drill-in
  pattern). Esc / backdrop click / × button all call ``onClose``.

### Changed — viewer/src/App.tsx

- 564 → 496 LOC (-68).
- Inline ``ServiceDetailModal`` definition removed.
- ``useTranslation`` import dropped (App.tsx no longer renders any
  i18n-aware JSX directly — every i18n string lives inside an
  extracted shell or canvas component).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 361 / 361 passed.

Plugin patch bump 0.16.2 → 0.16.3. Two more extractions (URL sync +
filters/keyboard hooks) land through v0.16.5; the final commit
lowers the structural-guards ceiling from 830 to 400.

## [0.16.2] — 2026-05-12

v0.16.0 follow-up — App.tsx split commit 2 of 5. Tab strip, help
overlay, and the three placeholder states extracted to
``viewer/src/shell/``. Pure JSX move, no behaviour change.
(D-2026-05-12-H)

### Added — viewer/src/shell/

- ``CanvasTabs.tsx`` — Foundation / Actors / Services tab strip +
  Mark-session button. **Also exports the ``CanvasTab`` discriminator
  + ``CANVAS_TAB_IDS`` SSOT** (the type now lives next to its only
  visual consumer; App.tsx imports both).
- ``HelpCheatsheet.tsx`` — keyboard-shortcut cheat sheet overlay.
- ``states.tsx`` — ``Loading`` + ``ErrorPanel`` + ``EmptyState``
  (each < 15 LOC; grouped per file).

### Changed — viewer/src/App.tsx

- 715 → 564 LOC (-151).
- ``CanvasTab`` type + ``CANVAS_TAB_IDS`` const moved out (now
  imported from ``./shell/CanvasTabs``).
- ``CanvasTabs`` / ``Loading`` / ``ErrorPanel`` / ``EmptyState`` /
  ``HelpCheatsheet`` inline definitions removed.
- ``// Small UI bits`` divider comment removed.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 361 / 361 passed.

Plugin patch bump 0.16.1 → 0.16.2. Three more extractions land
through v0.16.5; the final commit lowers the structural-guards
ceiling from 830 to 400.

## [0.16.1] — 2026-05-12

v0.16.0 follow-up — App.tsx split commit 1 of 5. Header +
SocketIndicator + ``truncateMiddle`` extracted to
``viewer/src/shell/Header.tsx``. Pure JSX move, no behaviour
change. (D-2026-05-12-H)

### Added — viewer/src/shell/Header.tsx

- ``Header`` component (project path + name + socket + error +
  migration toast).
- Internal ``SocketIndicator`` + ``truncateMiddle`` helpers,
  scoped to this file.

### Changed — viewer/src/App.tsx

- 811 → 715 LOC (-96).
- ``SocketStatus`` type import dropped (now scoped inside the new
  shell module).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 361 / 361 passed (no test changes; same
  component tree, just imported from a new path).
- ``uv run pytest`` — 245 / 245 passed (no server-side changes).

Plugin patch bump 0.16.0 → 0.16.1. Four more extractions land
through v0.16.5; the final commit lowers the structural-guards
ceiling from 830 to 400.

## [0.16.0] — 2026-05-12

**v0.15 structural reset COMPLETE.** Domain layer + per-kind
inspectors + per-kind node renderers + 4 thin wrappers + 8 acceptance
gates + 1 kill-switch land at v0.16.0. (D-2026-05-12-G)

### Added — hooks/pre_commit_gate.py::reset_complete_check

A single-boolean kill-switch that fires on every commit touching
viewer or server code. Verifies four structural invariants the
existing acceptance-gate suite cannot detect:

1. ``plot_mcp/models.py`` exposes ``SketchNode`` as a 15-way
   discriminated union (not a god class).
2. ``viewer/src/canvases/SketchInspector.tsx`` stays absent from disk.
3. ``viewer/src/canvases/SketchNode.tsx`` stays absent from disk.
4. Zero ``canvas_kind`` branching in ``viewer/src/canvases/sketch/``
   source files (comments-only references ignored).

Docs-only / non-viewer / non-server commits skip the check entirely.

### Added — tests/test_pre_commit_gate.py (11 tests)

- Pass-case against the real repo (verifies the current tree
  satisfies all four invariants).
- Docs-only skip-case (3 parametrised non-viewer / non-server paths).
- Each invariant has an isolated failure-mode test using a
  ``tmp_path`` scaffold so the deny path is exercised without
  mutating the real working tree.
- Comment-stripping test (``canvas_kind`` inside ``//`` and ``/* */``
  comments does NOT trip the gate).

### Changed — docs/ARCHITECTURE.md

- New "Post-v0.15 shape" section at the top documenting the
  Domain → UI dependency direction, a contracts table linking
  each invariant to its test + decision id, and a "how to add a
  16th kind" recipe.
- Legacy pre-reset section preserved below with a "historical only"
  banner; LOC numbers in that section no longer reflect reality.

### Changed — docs/NEXT_SESSION.md

- ``검증`` queue item moved to Completed with a per-commit summary
  (v0.15.7 → v0.16.0). Active queue now empty.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 361 / 361 passed.
- ``uv run pytest`` — 256 / 256 passed (245 prior + 11 new from
  ``test_pre_commit_gate.py``).
- ``uv run mypy plot_mcp/`` — clean.
- ``uv run ruff check plot_mcp/ tests/ hooks/pre_commit_gate.py`` —
  clean.
- ``reset_complete_check`` returns ``None`` (= reset COMPLETE)
  against the current tree.

### Reset scorecard (v0.14.15 → v0.16.0, 28 commits)

| Phase | Commits | Versions | Outcome |
|---|---:|---|---|
| 0 — Pre-existing ruff/mypy debt | 1 | v0.14.15 | 17 → 0 |
| 1 — Server SSOT (Pydantic 15-class union) | 3 | v0.14.16-18 | god ``SketchNode`` class → ``Annotated[Union[15]]`` |
| 2 — Viewer entities + per-kind Inspector fan-out | 12 | v0.14.19-v0.15.0 | god ``SketchInspector.tsx`` (1491 LOC) deleted; ``SketchNode`` (TS) is now a 15-way union |
| 3 — Canvas wrappers + per-kind node renderers | 5 | v0.15.1-5 | 4 thin wrappers + 15 per-kind nodes + god ``SketchNode.tsx`` (245 LOC) deleted |
| 4 — Cursor uniformity sweep + extended guard | 2 | v0.15.7-8 | 8 + 128 new cursor tests; ``cursor_kind`` drift structurally impossible |
| 5.1 — Exhaustive 15-kind sweeps | 1 | v0.15.9 | 75 viewer + 31 server tests, parametrised across all kinds |
| 5.2 — Structural guards (god + LOC + registry) | 1 | v0.15.10 | 44 tests; CLAUDE.md Gate 2 LOC table updated |
| 5.3 — Kill-switch + docs + complete pin | 1 | v0.16.0 | This commit. Reset DONE. |

- viewer tests: 106 → 361.
- server tests: 214 → 256.
- god files removed: 2 (1491 + 245 = 1736 LOC).
- god switches removed: 4 (3 in transforms + 1 in App.tsx tabToKind).
- structural invariants pinned: 8 acceptance gates + 1 kill-switch.

Plugin minor bump 0.15.10 → 0.16.0 — the only minor bump in the
entire reset sequence. Subsequent work (App.tsx split, schema
parity, Actors v0.15 migration, …) starts from this baseline.

## [0.15.10] — 2026-05-12

v0.15 reset Phase 5.2 — three structural guards protect the post-reset
shape against regression: no-god-union-import (the deleted
``SketchInspector.tsx`` / ``SketchNode.tsx`` must stay absent + no
``switch (X.kind)`` god dispatch in wrappers, App.tsx, SketchCanvas,
BaseNode, BaseInspector, KindInspector, DetailsSection, or any sketch
hook), loc-budget (per-file ceilings — raise via decision, never via
test edit), and registry-completeness (every kind has a per-kind
node + inspector file + registry entry). (D-2026-05-12-F)

### Added — viewer/tests/structural-guards.test.tsx

- 44 tests across three describe blocks:
  - ``no-god-union-import``: 2 god-files-absent + 17 no-switch-dispatch
    across wrappers / shared shell / App.tsx / 14 sketch hooks.
  - ``loc-budget``: 8 named-file ceilings + 2 per-kind sweeps
    (every per-kind node ≤ 100 LOC, every per-kind inspector ≤ 250 LOC).
  - ``registry-completeness``: per-kind file existence + non-empty +
    ``NODE_RENDERERS`` registry contains the 15 kinds and only those.

### Changed — plot/CLAUDE.md §Gate 2

- LOC table replaced. Stale 1476 / 1422 / 791 / 523 entries removed;
  new 8-row post-reset table added with current LOC + runtime-enforced
  ceiling for each canvas-internal file.
- Two "deleted-file" rows pin ``SketchInspector.tsx`` and
  ``SketchNode.tsx`` as absent (re-creating fails the test).
- Documentation pin: "raise a ceiling via decision id; never via
  test edit". App.tsx no-growth deviation (current 811 vs plan target
  ≤ 400) explicitly documented.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 361 / 361 passed (317 prior + 44 new).
- ``uv run pytest`` — 245 / 245 passed (no server-side changes).

### App.tsx refactor follow-up (deferred)

The original Phase 5.2 plan targets ``App.tsx ≤ 400`` LOC. Current
811 reflects URL sync + filter callbacks + handler glue that has not
been extracted into hooks. The split is filed for the v0.16 cycle;
doing it inside this commit would have bundled structural rules +
a behavioural refactor (cross-cutting bundle violation). The
no-growth ceiling (830) catches any further bloat in the meantime.

Plugin patch bump 0.15.9 → 0.15.10.

## [0.15.9] — 2026-05-12

v0.15 reset Phase 5.1 — exhaustive 15-kind smoke + round-trip
sweeps across viewer and server. Each parametric suite iterates
over the 15-way node-kind union and asserts the structural
contract; a future drop / addition / mis-registration in any of
{ Pydantic class, parseEntity dispatch, KindInspector registry }
fails the suite immediately with the offending kind in the test
name. (D-2026-05-12-E)

### Added — viewer/tests/inspectors/inspectors.exhaustive.test.tsx

- 30 tests = 15 kinds × { ``KindInspector`` returns a non-null
  tree, no ``console.error`` during render }.
- Uses ``createBlankNode`` (domain SSOT) to build each synthetic
  node from canonical defaults.

### Added — viewer/tests/domain/round-trip.exhaustive.test.ts

- 45 tests = 15 kinds × { ``parseEntity`` dispatches to a class
  instance, ``fromJson(toJson())`` is idempotent, kind is
  preserved across the round-trip }.

### Added — plot/tests/test_node_models.py (exhaustive section)

- 31 new tests = 15 kinds × { adapter dispatches to right class,
  ``model_validate(instance.model_dump())`` is idempotent } +
  1 union-size sanity. Pins the server-side 15-way discriminated
  union as the source of truth for kind enumeration.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 317 / 317 passed (242 prior + 75 new).
- ``uv run pytest`` — 245 / 245 passed (214 prior + 31 new).
- ``uv run mypy plot_mcp/`` — clean.
- ``uv run ruff check plot_mcp/ tests/`` — clean.

Phase 5.1 leaves the hand-written per-kind tests in place (they
cover kind-specific edge cases the structural sweep can't
enumerate — e.g. ``CategoryInspector`` empty-warning,
``ActorRefInspector`` orphan rendering, Service composition lists).
The sweep is additive, not a replacement.

Plugin patch bump 0.15.8 → 0.15.9.

## [0.15.8] — 2026-05-12

v0.15 reset Phase 4.2 — extended cursor-baseline static guard.
The existing 1-test ``styles.css`` guard (D-2026-05-11-C) is
broadened into a 129-test sweep that asserts ZERO raw ``cursor:``
declarations and ZERO ``style.cursor =`` JS assignments across
every canvas-internal source file: 4 wrappers, shared shell (SketchCanvas
/ BaseNode / BaseInspector / KindInspector / DetailsSection /
registries / types), 15 per-kind node renderers, 15 per-kind
inspectors, inspectors/shared, and all 17 sketch hooks. With
``cursor-sweep.test.tsx`` (D-2026-05-12-C, ships in 0.15.7) and
this guard, per-canvas cursor drift is structurally impossible.
(D-2026-05-12-D)

### Added — guards inside viewer/tests/styles-cursor-baseline.test.tsx

- ``KIND_DIRS`` SSOT for the 15 node-kind names (assertion: every
  expected per-kind directory exists under both
  ``canvases/nodes/`` and ``canvases/inspectors/``).
- ``it.each`` raw ``cursor:`` guard across all 60-ish canvas-internal
  source files (regex ``cursor\s*:`` — colon-suffixed; intentionally
  ignores Tailwind ``cursor-X`` utility class names by design).
- ``it.each`` ``style.cursor =`` JS assignment guard (regex
  ``\bstyle\s*\.\s*cursor\s*=``).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 242 / 242 passed (114 prior + 128 new from this
  file).
- ``uv run pytest`` — 214 / 214 passed (no server-side changes).

### Note on Tailwind utility classes

``cursor-grab`` (SketchStencil), ``active:cursor-grabbing``
(SketchStencil), ``cursor-not-allowed`` (SketchContextMenu,
SketchToolbar), ``cursor-pointer`` (SketchEdgeModal),
``disabled:cursor-not-allowed`` (DetailsSection): each is a class
string with a hyphen after ``cursor``, not a colon, and lives on
chrome surfaces shared identically across all 4 wrappers. The
regex above intentionally does not match these; their per-file
addition is allowed and tracked by the cursor-sweep DOM-equivalence
test instead (which would notice class-set drift across wrappers).
See D-2026-05-12-D §"What the guard does not match" for the full
rationale.

Plugin patch bump 0.15.7 → 0.15.8.

## [0.15.7] — 2026-05-12

v0.15 reset Phase 4.1 — cursor uniformity audit + JSDOM sweep.
The user's complaint that fired the v0.15 reset
(*"파운데이션에서 사용되는 커서 컨트롤하고 액터나 서비스에서
사용되는 커서 컨트롤이 다릅니다"*) is now answered empirically:
all 4 wrappers (Foundation / Actors / Services / ServiceDetail)
route through a single SketchCanvas + NODE_RENDERERS + BaseNode
pipeline, with **zero** per-canvas cursor declarations anywhere
in the wrapper / per-kind node / per-kind inspector / sketch hook
files, and **identical** ``react-flow__*`` class skeletons under
DOM sweep. Cursor inventory is fully determined by the shared RF
vendor CSS + Tailwind preflight stack; per-canvas drift is now
structurally impossible. (D-2026-05-12-C)

### Added — viewer/tests/cursor-sweep.test.tsx

- 8 tests across 3 describe blocks:
  1. Zero inline ``style.cursor`` assignments on any element rendered
     by FoundationCanvas / ActorsCanvas / ServicesCanvas /
     ServiceDetailCanvas (empty doc).
  2. Zero inline ``style.cursor`` when each wrapper is seeded with
     all 15 node kinds (via ``createBlankNode`` from the domain layer).
  3. ``react-flow__*`` class-skeleton equivalence across the 4
     wrappers — same set of fragments (``react-flow__pane``,
     ``react-flow__renderer``, ``react-flow__viewport``, …) on each.
- Per-kind node renderer probes: Foundation seed (project + mission +
  core_value + identity) and Services seed (category + service) each
  render with zero inline cursor on any descendant.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 114 / 114 passed (106 prior + 8 new from this
  file).
- ``uv run pytest`` — 214 / 214 passed (no server-side changes).

### Audit evidence (pinned via D-2026-05-12-C)

| Probe | Result |
|---|---|
| ``grep -rn "cursor:" viewer/src/canvases/`` | 0 raw CSS hits |
| Tailwind ``cursor-*`` utility usage | Only in chrome (Stencil / ContextMenu / Toolbar / EdgeModal / DetailsSection) — shared across all wrappers |
| ``grep -rEn "style\.cursor\|cursor\s*="`` viewer/src/ | 0 hits |
| ``styles.css`` cursor declarations | 0 (guarded by ``styles-cursor-baseline.test.tsx`` since D-2026-05-11-C) |
| Wrapper LOC (Foundation / Actors / Services / ServiceDetail) | 22 / 16 / 22 / 23 — props-only thin shells |

### Deviation from the original Phase 4.1 plan

The plan called for a Playwright spec that probes
``getComputedStyle()`` in a real browser. The audit above proves
cursor uniformity structurally — every per-canvas cursor source
has been eliminated — and the JSDOM sweep pins the DOM-shape
equivalence. Adding Playwright would re-derive the same conclusion
at the cost of ~300 MB browser binaries + a separate test runner.
The user-runnable DevTools recipe in ``docs/CURSOR.md`` §"How to
verify the cursor state in the browser" (lines 197-215) remains
the canonical sensory confirmation when the user wants one. See
D-2026-05-12-C §Alternatives for the reversal path if a future
drift report needs live evidence.

Plugin patch bump 0.15.6 → 0.15.7.

## [0.15.6] — 2026-05-12

Docs-only — handoff for the next session. v0.15 reset Phases 4–5
queued in NEXT_SESSION.md under the new ``검증`` trigger; the
original ``구조 리셋`` queue entry is moved to Completed with the
per-phase summary of what shipped this session (v0.14.15 → v0.15.5,
23 commits). (D-2026-05-12-B)

### Changed — plot/docs/NEXT_SESSION.md

- New active queue item: ``검증`` (triggers: 검증 / verification /
  phase 4 / phase 5 / 커서 sweep). Carries the Phase 4 (cursor
  sweep + drift audit) and Phase 5 (verification gates +
  kill-switch → v0.16.0) per-phase plan.
- Old ``구조 리셋`` entry moved to "Completed Phase 1+2+3 in this
  session" with a per-phase summary. The original problem statement,
  code evidence, and Phase A–F plan blocks were removed (preserved
  in git history at v0.14.14 + the plan file
  ``~/.claude/plans/dazzling-greeting-diffie.md``).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 106 / 106 passed (no test changes).
- ``uv run pytest`` — 214 / 214 passed (no test changes).

Plugin patch bump 0.15.5 → 0.15.6.

## [0.15.5] — 2026-05-12

v0.15 structural reset Phase 3.5 — legacy ``SketchNode.tsx`` (245
LOC) DELETED. ``NODE_RENDERERS`` is now wired into SketchCanvas's
React Flow ``nodeTypes`` map; each node carries its kind as the
React Flow ``type`` discriminator instead of the v0.14 ``"sketch"``
god type. Phase 3 complete. (D-2026-05-12-B)

### Removed (BREAKING within viewer/src/canvases/)

- ``viewer/src/canvases/SketchNode.tsx`` — the 245-LOC god renderer
  that branched on ``data.kind`` for every cosmetic choice. Now
  zero LOC on disk.

### Changed — SketchCanvas

- ``NODE_TYPES = NODE_RENDERERS`` (was ``{ sketch: SketchNode }``).
  React Flow now dispatches by kind; each per-kind component from
  ``nodes/{kind}/`` handles its own node rendering.

### Changed — useNodesMemo

- Each rendered node's ``type`` field is now ``n.kind`` (was the
  hardcoded ``"sketch"`` god type).
- Synthetic project anchor's ``type`` is ``"project"``.
- ``SketchNodeData`` import replaced by ``BaseNodeData`` from
  ``../nodes/BaseNode`` (the per-kind data shape).

### Verification

- ``find viewer/src -name "SketchNode.tsx"`` — absent.
- ``grep '"sketch"' viewer/src/canvases/sketch/`` — only inside
  a comment, no live code reference.
- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 106 / 106 passed.

### Phase 3 complete

15 per-kind React Flow node renderers + 4 canvas wrappers
(Foundation / Actors / Services / ServiceDetail) + zero
``canvas_kind`` switches in transforms + zero ``"sketch"`` god
type. The viewer canvas layer now mirrors Phase 2's Inspector
layer's per-kind discipline end-to-end.

Plugin patch bump 0.15.4 → 0.15.5. Phase 4 (per-canvas cursor
sweep) is the natural next ship.

## [0.15.4] — 2026-05-12

v0.15 structural reset Phase 3.4 — canvas_kind switches stripped
from useNodesMemo + useEdgesMemo + edgeTransform; each per-canvas
wrapper now supplies its own behaviour via 4 explicit props.
(D-2026-05-12-B)

### Changed — useNodesMemo

The 4 ``doc.canvas_kind`` switches inside the transform are gone.
``useNodesMemo`` now takes 4 new wrapper-supplied args:

- ``hideRootServiceNode: boolean`` — drop the canvas's root-service
  node from the rendered list. Was: ``canvas_kind === "service_detail"``.
- ``shouldDrill: ((node) => boolean) | undefined`` — predicate that
  opts nodes into double-click drill. Was: inline kind-specific
  conditions on services / service_detail.
- ``showFoldButton: boolean`` — render the fold (▾/▸) button on
  container nodes. Was: ``canvas_kind !== "foundation"``.
- ``injectAnchor: boolean`` — inject the synthetic project anchor
  at the top of the node list. Was: ``ANCHOR_KINDS.has(canvas_kind)``.

### Changed — useEdgesMemo + edgeTransform

The ``canvasKind`` parameter is gone; ``hideRootServiceNode`` flows
in instead. ``edgeTransform`` is still pure + unit-testable in
isolation; the change just renamed the input flag.

### Changed — SketchCanvas

Forwards the 4 new props to the transforms with safe defaults
(``hideRootServiceNode=false``, ``showFoldButton=true``,
``injectAnchor=true``, ``shouldDrill=undefined``) so any direct call
without a wrapper still works (none today; the default just means
"normal main-canvas behaviour").

### Changed — wrappers

- ``FoundationCanvas``: ``hideRootServiceNode=false``,
  ``shouldDrill=undefined``, ``showFoldButton=false``,
  ``injectAnchor=true``.
- ``ActorsCanvas``: ``showFoldButton=true``, others as Foundation.
- ``ServicesCanvas``: ``shouldDrill=(n => n.kind === "service" && !n.is_root)``,
  others as Foundation but ``showFoldButton=true``.
- ``ServiceDetailCanvas``: ``hideRootServiceNode=true``,
  ``shouldDrill=(n => n.kind === "actor_ref")``, ``injectAnchor=false``,
  ``showFoldButton=true``.

### Verification

- ``grep -nE "canvas_kind\s*===" useNodesMemo useEdgesMemo edgeTransform App.tsx`` — 0 hits.
- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 106 / 106 passed.

Plugin patch bump 0.15.3 → 0.15.4.

## [0.15.3] — 2026-05-12

v0.15 structural reset Phase 3.3 — ServicesCanvas + ServiceDetailCanvas
wrappers added; ``App.tsx`` no longer calls ``SketchCanvas`` directly.
(D-2026-05-12-B)

### Added

- ``viewer/src/canvases/ServicesCanvas.tsx`` — services-overview
  wrapper. Pass-through; Phase 3.4 absorbs canvas-kind-specific
  behaviour.
- ``viewer/src/canvases/ServiceDetailCanvas.tsx`` — service-detail
  modal wrapper. Pass-through; Phase 3.4 absorbs the service-detail-
  specific anchor + edge filter rules; Phase 3.5 wires NODE_RENDERERS.

### Changed

- ``viewer/src/App.tsx`` — the ``SketchCanvas`` import is gone.
  Both call sites (main canvas + service-detail modal) now mount
  the named wrapper. The activeTab dispatch picks
  Foundation / Actors / Services per tab.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 106 / 106 passed.

Plugin patch bump 0.15.2 → 0.15.3.

## [0.15.2] — 2026-05-12

v0.15 structural reset Phase 3.2 — FoundationCanvas + ActorsCanvas
wrappers introduced as named pass-throughs; App.tsx routes by
``activeTab``. (D-2026-05-12-B)

### Added

- ``viewer/src/canvases/FoundationCanvas.tsx`` — pure pass-through
  to ``SketchCanvas``. Phase 3.4 absorbs canvas-kind-specific
  behaviour; Phase 3.5 wires ``NODE_RENDERERS`` so this wrapper
  supplies a Foundation-only ``nodeTypes`` map.
- ``viewer/src/canvases/ActorsCanvas.tsx`` — same pattern.

### Changed

- ``viewer/src/App.tsx`` — the main canvas mount now picks
  ``FoundationCanvas`` / ``ActorsCanvas`` / (legacy)
  ``SketchCanvas`` based on ``activeTab``. The component identity
  is now named per tab; behaviour unchanged.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 106 / 106 passed.

Plugin patch bump 0.15.1 → 0.15.2.

## [0.15.1] — 2026-05-12

v0.15 structural reset Phase 3.1 — BaseNode shell + 15-kind React
Flow node renderer registry. Mirrors the Phase 2 Inspector pattern
(BaseInspector + KIND_INSPECTORS + per-kind wrappers) at the node
layer. (D-2026-05-12-B)

The legacy ``SketchNode.tsx`` (245 LOC) is unchanged and still in
use by ``SketchCanvas`` until Phase 3.5 wires the registry.
Phase 3.2–3.4 introduces canvas wrappers that consume the registry.

### Added — viewer/src/canvases/nodes/

- ``BaseNode.tsx`` — chrome SSOT: NodeResizer, the outer
  shape-styled div, the 4 React Flow Handles, the MD-warnings
  badge, the label / icon / fold / body area. Per-kind callers
  pass a small ``chrome`` prop with ``showKindTag`` /
  ``isAnchor`` / ``labelAlignLeft`` / ``bodyOverride`` overrides.
- ``shouldShowKindTag(shape)`` helper — returns true for
  ``rectangle`` / ``rounded`` shapes (where the top-left corner
  is inside the visible silhouette).
- ``{kind}/index.tsx`` × 15 — minimal per-kind wrappers (avg
  ~12 LOC each). Currently same chrome as today; the per-file
  structure is the hook point for future per-kind visual variations.
  ``ProjectNode`` carries ``isAnchor: true``; ``CategoryNode``
  carries ``labelAlignLeft: true``; Foundation + composition kinds
  enable ``showKindTag`` for rectangle / rounded shapes.
- ``registry.ts`` — ``NODE_RENDERERS: Record<NodeKind,
  NodeRendererComponent>`` covering all 15 kinds.

### Added — tests

- ``viewer/tests/nodes/registry.test.tsx`` — 3 tests: registry
  has all 15 NodeKind entries, every entry is a callable
  component, and ``shouldShowKindTag`` returns true only for
  rectangle / rounded shapes.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 106 / 106 passed (103 prior + 3 new).

Plugin patch bump 0.15.0 → 0.15.1.

## [0.15.0] — 2026-05-12

v0.15 structural reset Phase 2.10 — viewer-side god ``SketchNode``
interface RETIRED. The TypeScript wire shape is now a discriminated
union of 15 per-kind ``XxxJson`` interfaces (mirroring the server-side
Pydantic union landed in v0.14.17). This is the version-bump moment
the entire reset has been climbing toward. (D-2026-05-12-B)

### Atomic flip — types.ts

- ``viewer/src/types.ts`` no longer defines an ``interface SketchNode``
  with all 47 typed fields collapsed. The 130-LOC god block (and the
  4 ``*FoundationNode`` cosmetic-narrowing types) are gone.
- ``viewer/src/types.ts`` re-exports ``SketchNode`` from ``./domain``;
  the dozen+ files that already import from ``../types`` keep working
  without any import path changes.
- New ``viewer/src/domain/SketchNode.ts`` defines:
  - ``SketchEntity`` — class-instance union (used by parseEntity +
    tests; rare in viewer code).
  - ``SketchNode`` — JSON-shape union (used by React Flow state,
    Inspector props, api.ts response casts, undo/redo). Class
    instances satisfy this structurally; plain objects from
    ``{...node, x: newX}`` spread also satisfy it (no method
    requirement on the union).

### Per-kind ``XxxJson`` interfaces tightened to required

The wire shape from the server (Pydantic ``model_dump()``) always
populates every field with its default, so each ``XxxJson`` is now
"required everywhere". This eliminates ``?? ""`` / ``?? null``
fallbacks throughout the Inspector code and matches reality.

### Per-kind Inspector narrowing

Every ``inspectors/{kind}/index.tsx`` now opens with:

```ts
if (props.node.kind !== "<kind>") return null;
const node = props.node;
```

so TypeScript narrows ``node`` to the per-kind ``XxxJson`` shape
inside the body. The matching ``XxxFields`` component declares
``node: XxxJson`` (was ``node: SketchNode`` god). Per-kind components
now type-check the kind-specific field accesses they always relied
on (``node.target`` for Metric, ``node.target_side`` for Service,
etc.).

### Added — viewer/src/domain/createBlankNode.ts

Factory that builds a wire-shape node for a given kind by running
the per-kind entity class's ``fromJson`` + ``toJson``. Replaces the
v0.14 god-style 47-field inline initialiser in
``useNodeCreation.ts``. Each blank node now carries exactly the
canonical defaults its kind owns — no foreign fields.

### Added — narrowed shared components

- ``inspectors/shared/DoDontFields.tsx`` accepts a structural
  ``DoDontCarrier`` (``{ do?: string; dont?: string }``) instead
  of a god-typed ``SketchNode``.
- ``inspectors/shared/FoundationRefBlock.tsx`` accepts the
  ``MissionRefJson | ValueRefJson | IdentityRefJson`` narrowed
  union.

### Removed

- God ``SketchNode`` interface (130 LOC) from ``viewer/src/types.ts``.
- ``BaseFoundationNode`` + ``ProjectFoundationNode`` +
  ``MissionFoundationNode`` + ``CoreValueFoundationNode`` +
  ``IdentityFoundationNode`` (the v0.13 cosmetic-narrowing aliases
  superseded by the real per-kind entity classes).
- The "kind: NodeKind | null" path in node-creation. Every node now
  has a non-null kind discriminator at construction time.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 103 / 103 passed.
- All 15 per-kind inspectors narrow correctly; no ``as any`` /
  no untyped accesses on the union.

Plugin minor bump 0.14.27 → 0.15.0 — the v0.15 reset's central
promise (no god object on either server or viewer; per-kind
discriminated union end-to-end) is now LIVE.

## [0.14.27] — 2026-05-12

v0.15 structural reset Phase 2.9 — final per-kind vertical slice
(Service + Rule + Content) AND deletion of the legacy
``SketchInspector.tsx`` (was 1491 LOC at v0.14.18; this commit
removes the last remnants and cuts the file from disk).
(D-2026-05-12-B)

### Decision — phase merge

The plan had Phase 2.10 do "delete SketchInspector + retire god
types.ts" as one step. This commit pulls the SketchInspector
deletion forward because by the time service migrated, every kind
was in the registry — the legacy fallback path was unreachable
dead code. Phase 2.10 (next commit) now does ONLY the types.ts
atomic flip (god interface → 15-way discriminated union).

### Added — viewer/src/domain/ (3 final entity classes)

- ``Service.ts`` — target_side + 6 typed fields (what /
  value_created / scope / trigger / how / outcome) + do/dont.
- ``Rule.ts`` — policy + enforcement + actor_permissions
  (Record<string,string> with strict value typing).
- ``Content.ts`` — format + producer_actor_id + consumer_actor_id.

### Added — viewer/src/canvases/inspectors/ (3 per-kind + 3 shared)

- ``service/index.tsx`` — ServiceInspector wraps ServiceFields +
  two CompositionList panels (rules + contents).
- ``service/CompositionList.tsx`` — extracted CompositionList +
  CompositionRow.
- ``service/RuleFields.tsx`` — extracted RuleFields with the
  per-actor-permissions editor.
- ``service/ContentFields.tsx`` — extracted ContentFields +
  ContentActorPicker.
- ``rule/index.tsx`` — direct-selection variant of RuleFields
  inside BaseInspector chrome.
- ``content/index.tsx`` — direct-selection variant of ContentFields.
- KindInspectorProps grows ``onAddChild?`` + ``onPatchChild?`` +
  ``onRemoveChild?`` (all optional — only ServiceInspector uses
  them; other kinds receive undefined).

### Removed

- ``viewer/src/canvases/SketchInspector.tsx`` — the 1491-LOC
  god component is now ZERO LOC on disk.
- All local fields helpers and composition components that lived
  inside it (CompositionList, CompositionRow, ServiceFields,
  ServiceTextarea, RuleFields, ContentFields, ContentActorPicker).

### Changed

- ``viewer/src/canvases/sketch/SketchInspectorBindings.tsx`` now
  calls ``KindInspector`` directly, with an inline null-guard for
  the no-selection case. The bindings file is the same external
  contract — it's the ONLY consumer of the inspector framework
  outside ``inspectors/`` itself.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 103 / 103 passed (90 prior + 13 new
  covering Service / Rule / Content round-trip + dispatch + smoke).

### Registry status — all 15 kinds migrated

```
metric, step, core_value, identity, mission, project, category,
actor_ref, mission_ref, value_ref, identity_ref, actor,
service, rule, content
```

Plugin patch bump 0.14.26 → 0.14.27.

## [0.14.26] — 2026-05-12

v0.15 structural reset Phase 2.8 — ``actor`` kind vertical slice
(D-2026-05-12-B). Includes the v0.3 actor-composition placeholder
that fires for non-root actors.

### Added

- ``viewer/src/domain/Actor.ts`` (motivation + pain + side validator).
- ``viewer/src/canvases/inspectors/actor/index.tsx`` — renders the
  side select + motivation + pain + the placeholder for non-root.
- registry: ``actor: ActorInspector``.
- 4 round-trip + 3 smoke tests.

### Removed

- Local ``ActorFields`` (~58 LOC) + the actor-placeholder branch
  from ``SketchInspector.tsx``.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 90 / 90 passed (83 prior + 7 new).

Plugin patch bump 0.14.25 → 0.14.26.

## [0.14.25] — 2026-05-12

v0.15 structural reset Phase 2.7 — bundled vertical slice for the 4
reference kinds: ``actor_ref`` + ``mission_ref`` / ``value_ref`` /
``identity_ref``. (D-2026-05-12-B)

### Added — KindInspectorProps grew ref-related optional fields

- ``availableActors?: SketchNode[]`` (ActorRef master lookup).
- ``availableMissions?`` / ``availableValues?`` / ``availableIdentities?``
  (FoundationRef master lookups).
- ``onRepickActorRef?`` + ``onRepickFoundationRef?`` callbacks for
  re-pick UI on orphaned refs.

### Added — viewer/src/domain/

- ``ActorRef.ts`` (ref_actor_id + gives + receives + side validator).
- ``MissionRef.ts``, ``ValueRef.ts``, ``IdentityRef.ts`` (each with
  the corresponding ref_*_id field).

### Added — viewer/src/canvases/inspectors/

- ``shared/FoundationRefBlock.tsx`` — extracted from the legacy
  inspector. Resolves master from available-list; surfaces orphan
  state with re-pick + delete actions.
- ``actor_ref/index.tsx`` — gives/receives form + actor-master
  display + orphan handling.
- ``mission_ref/`` + ``value_ref/`` + ``identity_ref/`` — each wraps
  the shared FoundationRefBlock inside BaseInspector.
- registry: all 4 ref kinds registered.

### Removed — SketchInspector.tsx

- All 4 ref-kind branches (~85 LOC of inline JSX).
- Local ``ActorRefFields`` (~40 LOC) + ``FoundationRefBlock``
  (~85 LOC). Now in ``inspectors/`` per-kind + shared paths.
- Stale ``refTarget`` / ``isOrphanActorRef`` locals (used only by the
  removed branches).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 83 / 83 passed (71 prior + 12 new).

Plugin patch bump 0.14.24 → 0.14.25.

## [0.14.24] — 2026-05-12

v0.15 structural reset Phase 2.5 + 2.6 — bundled vertical slice for
the two simplest remaining kinds: ``project`` (Foundation anchor,
no typed body) and ``category`` (one-line ``theme`` + ``childCount``
empty-warning). (D-2026-05-12-B)

### Added — KindInspectorProps grew an `allNodes` field

Category needs to count nested services for its empty-warning. Rather
than build a context-provider for one prop, the existing
``SketchInspector`` already passes ``allNodes`` and the registry now
forwards it through ``KindInspector`` to every per-kind component.
Most kinds ignore it; Category uses it.

### Added

- ``viewer/src/domain/Project.ts`` (no typed fields beyond BaseFields).
- ``viewer/src/domain/Category.ts`` (theme).
- ``viewer/src/canvases/inspectors/project/index.tsx`` —
  ``ProjectInspector`` is just ``BaseInspector`` (chrome only).
- ``viewer/src/canvases/inspectors/category/index.tsx`` — computes
  ``childCount`` from ``allNodes`` and renders the empty-warning when
  zero.
- registry: ``project`` + ``category``.
- 7 round-trip tests + 3 smoke tests.

### Removed

- Local ``CategoryFields`` (~38 LOC) from ``SketchInspector.tsx``.
- Stale "returns null for unmigrated kinds" smoke test (used
  ``category`` as the unmigrated example; now category IS migrated).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 71 / 71 passed (62 prior + 9 new).

Plugin patch bump 0.14.23 → 0.14.24.

## [0.14.23] — 2026-05-12

v0.15 structural reset Phase 2.4 — ``mission`` Foundation kind
vertical slice. (D-2026-05-12-B)

### Added

- ``viewer/src/domain/Mission.ts`` (what_we_do + why + direction).
- ``viewer/src/canvases/inspectors/mission/index.tsx``.
- registry: ``mission: MissionInspector``.
- 4 round-trip tests + 1 smoke test.

### Removed

- Local ``MissionFields`` (~55 LOC) from ``SketchInspector.tsx``.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 62 / 62 passed (57 prior + 5 new).

Plugin patch bump 0.14.22 → 0.14.23.

## [0.14.22] — 2026-05-12

v0.15 structural reset Phase 2.3 — bundled vertical slice for the
two Foundation kinds that share the do / dont AI-first pair:
``core_value`` and ``identity``. (D-2026-05-12-B)

### Added

- ``viewer/src/domain/CoreValue.ts`` — definition + do + dont.
- ``viewer/src/domain/Identity.ts`` — description + do + dont.
- ``viewer/src/canvases/inspectors/shared/DoDontFields.tsx`` —
  shared do/dont pair extracted from ``SketchInspector.tsx``.
  CoreValue + Identity per-kind inspectors consume it; the legacy
  ``Service`` branch (still on the legacy code path until Phase 2.9)
  imports it from the new shared location.
- ``inspectors/core_value/index.tsx`` + ``inspectors/identity/index.tsx``.
- registry: ``core_value: CoreValueInspector`` + ``identity: IdentityInspector``.
- 8 round-trip tests + 2 dispatch tests + 3 smoke tests.

### Removed

- Local ``CoreValueFields`` / ``IdentityFields`` / ``DoDontFields``
  (~95 LOC) from ``SketchInspector.tsx``.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 57 / 57 passed (47 prior + 10 new).

Plugin patch bump 0.14.21 → 0.14.22.

## [0.14.21] — 2026-05-12

v0.15 structural reset Phase 2.2 — ``step`` kind vertical slice
(D-2026-05-12-B). Repeats the Phase 2.1 pattern.

### Added

- ``viewer/src/domain/Step.ts`` — ``class Step`` with ``order: int |
  null`` (null for parallel branches) + ``outcome``. Self-registers
  with ``parseEntity``.
- ``viewer/src/canvases/inspectors/step/index.tsx`` — ``StepInspector``
  wraps the per-kind body inside ``BaseInspector``.
- ``inspectors/registry.ts`` registers ``step: StepInspector``.
- 5 round-trip tests for Step (defaults / ordered / fractional-rejection
  / wrong-kind rejection / null-order round-trip).
- 1 dispatch test (parseEntity → Step).
- 2 smoke tests (StepInspector renders ordered + unordered nodes
  without console.error).

### Removed

- Local ``StepFields`` (47 LOC) from ``SketchInspector.tsx``.

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 47 / 47 passed (39 prior + 8 new).

Plugin patch bump 0.14.20 → 0.14.21 per the Plot plugin rule.

## [0.14.20] — 2026-05-12

v0.15 structural reset Phase 2.1 — first vertical slice.
``metric`` kind migrates out of the legacy god ``SketchInspector``
into ``viewer/src/domain/Metric.ts`` + ``viewer/src/canvases/inspectors/metric/``.
The pattern this commit establishes is the template Phase 2.2+
will repeat for every remaining kind. (D-2026-05-12-B)

### Decision — types.ts atomic flip stays in Phase 2.10

Considered: trim god ``SketchNode`` interface kind-by-kind in each
Phase 2.X. Rejected: leaves transient type holes mid-migration and
contradicts the Phase 1.2 atomic-flip principle. Per-kind RENDERING
moves out incrementally; the god TYPE shape stays intact until
Phase 2.10 retires it atomically (mirrors v0.14.17's god-class flip).

### Added — viewer/src/domain/

- ``Metric.ts`` — ``class Metric`` with BaseFields slice + ``target`` +
  ``measurement`` + ``kind: "metric"`` literal. Static
  ``fromJson(raw)`` validates via ``parseBaseFields`` then per-kind
  invariants. Self-registers with ``parseEntity`` on module load.
- ``index.ts`` re-exports ``Metric`` + ``MetricJson``.

### Added — viewer/src/canvases/inspectors/metric/

- ``index.tsx`` — ``MetricInspector`` wraps the per-kind
  ``MetricFields`` body (``target`` text input + ``measurement``
  textarea, identical i18n keys to the legacy ``MetricFields``)
  inside the shared ``BaseInspector`` chrome.

### Added — registry + short-circuit wiring

- ``inspectors/registry.ts`` registers ``metric: MetricInspector``.
- ``SketchInspector.tsx`` — top of the function (after the
  ``if (!node)`` guard) checks ``lookupKindInspector(node.kind)`` and
  delegates to ``KindInspector`` when the kind is migrated. Unmigrated
  kinds fall through to the legacy ``aside`` body unchanged.

### Added — tests

- ``viewer/tests/domain/round-trip.test.ts`` — 9 tests covering
  ``Metric.fromJson`` defaults / overrides / kind validation /
  type coercion / round-trip / spread-safety (React Flow
  ``applyNodeChanges`` compatibility) + ``parseEntity`` dispatch.
- ``viewer/tests/inspectors/inspectors.smoke.test.tsx`` — 3 tests:
  MetricInspector renders shared chrome + typed fields, no
  ``console.error`` fires, ``KindInspector`` returns ``null`` for
  unmigrated kinds (the resolver contract).

### Removed

- ``viewer/src/canvases/SketchInspector.tsx`` — local ``MetricFields``
  function + its props interface (43 LOC). Now lives in
  ``inspectors/metric/index.tsx``. SketchInspector LOC drops
  1413 → 1394 (Gate 2 ✓).

### Verification

- ``npx tsc --noEmit`` — clean.
- ``npx vitest run`` — 39 / 39 passed (27 prior + 12 new).

Plugin patch bump 0.14.19 → 0.14.20 per the Plot plugin rule.

## [0.14.19] — 2026-05-12

v0.15 structural reset Phase 2.0 — viewer-side scaffolding for the
domain entity layer + per-kind Inspector framework. Pure additive +
one mechanical refactor (extract `DetailsSection` so the new
`BaseInspector` shell and the legacy `SketchInspector` share one
implementation). No user-visible behaviour change. (D-2026-05-12-B)

### Added — `viewer/src/domain/`

- `DomainParseError.ts` — custom error subclass thrown by every
  per-kind `fromJson` parser; carries the offending raw input on
  the error so callers can surface it without re-deriving.
- `BaseFields.ts` — `BaseFieldsJson` (wire shape) + `BaseFields`
  (in-memory shape with defaults filled) + `parseBaseFields(raw)`
  validator that throws `DomainParseError` on any invariant
  violation. Mirrors `plot_mcp/models.py::BaseNodeFields` 1:1.
- `parseEntity.ts` — discriminator dispatch on `raw.kind`. Each
  per-kind class registers its parser via `registerKindParser`
  during module load; `parseEntity` looks up at runtime. Throws
  `DomainParseError` for missing / unknown kinds.
- `index.ts` — barrel re-export.

### Added — `viewer/src/canvases/inspectors/`

- `types.ts` — `KindInspectorProps` (the prop slice every per-kind
  inspector consumes; kind-specific extras live on per-kind prop
  interfaces inside `inspectors/{kind}/index.tsx`).
- `BaseInspector.tsx` — chrome SSOT for every per-kind inspector.
  Wraps the per-kind body as `children` and renders the shared
  header (kind tag, delete, width toggle, close), MD-warnings
  banner, label input, long-form details section, and actor-root
  toggle. Width preference (narrow / wide) persists across reloads
  via the same localStorage key the legacy inspector uses.
- `DetailsSection.tsx` — extracted from `SketchInspector.tsx`
  (was a local function). Now a standalone shared chrome piece
  consumed by both the legacy inspector and `BaseInspector`.
- `registry.ts` — `KIND_INSPECTORS: Partial<Record<NodeKind,
  KindInspectorComponent>>` (intentionally `Partial` during the
  migration so a kind without a registered inspector returns
  `undefined` and the caller can fall back). Phase 2.1+ populates
  one entry per commit.
- `KindInspector.tsx` — resolver. Looks up the registered
  per-kind inspector for the current node and renders it; returns
  `null` when the kind isn't migrated yet so the legacy inspector
  stays in charge.

### Added — tests

- `viewer/tests/domain/base-fields.test.ts` — 13 tests covering
  `parseBaseFields` (defaults / overrides / id-required /
  type-required / shape-validation / `DomainParseError.raw`
  attachment) and `parseEntity` (empty registry / missing kind /
  non-string kind / unknown kind / dispatch wiring with a
  test-only registered parser).

### Changed

- `viewer/src/canvases/SketchInspector.tsx` — removed local
  `DetailsSection` function (71 LOC) and the unused
  `createFolder` / `MDFileEditor` / `folderSlug` imports it
  needed; now imports `DetailsSection` from
  `./inspectors/DetailsSection`. SketchInspector LOC drops
  1491 → 1413 (Gate 2 ✓ — file shrinks, no new responsibilities).

### Why

Phase 2.0 puts the rails in place so each Phase 2.1+ commit can
land one kind at a time (vertical slice — entity class +
per-kind inspector + types.ts cleanup) without inventing new
infrastructure on every ship. The `Partial<Record<...>>`
registry typing lets the legacy `SketchInspector` keep handling
unmigrated kinds while migrated ones flow through `KindInspector`,
so the user sees no UI change at any commit boundary.

### Verification

- `npx tsc --noEmit` — clean.
- `npx vitest run` — 27 / 27 passed (14 prior + 13 new).
- Existing `i18n-keys-parity.test.ts` and
  `styles-cursor-baseline.test.tsx` static guards still pass.

Plugin patch bump 0.14.18 → 0.14.19 per the Plot plugin rule.

## [0.14.18] — 2026-05-12

v0.15 structural reset Phase 1.3 — extend `schema_export` to all 15
kinds. Server SSOT now publishes per-kind JSON Schemas + Foundation
MD templates for the full discriminated union introduced in v0.14.17
(D-2026-05-12-B).

### Added

- `plot_mcp/schema_export.py` — `_ALL_KIND_CLASSES` map covering all
  15 per-kind Pydantic classes (replaces Foundation-only
  `_FOUNDATION_KIND_CLASSES`). `SCHEMA_VERSION` bumped 1 → 2 to flag
  the expansion to downstream consumers.
- `plot_mcp/schema_export.py` — `export_all_schemas(project_root,
  project_id)` (renamed from `export_foundation_schemas`). Emits 15
  `{kind}.json` JSON Schema files + 3 `{kind}.md.template` heading
  templates (Foundation typed-text kinds only). Idempotent — files
  with unchanged content keep their mtime.
- `plot/tests/test_schema_export.py` — 7 tests covering the export
  surface:
  - all 15 `{kind}.json` files emitted
  - only Foundation typed-text kinds emit `{kind}.md.template`
  - Foundation JSON strips typed-text fields
  - non-Foundation JSON includes typed fields
    (Actor.motivation, Service.target_side, Metric.target, …)
  - `_meta.json` lists every kind with the right schema/plot version
  - idempotent — second call preserves mtime
  - each schema parses with `id` in required props (smoke)

### Changed

- `plot_mcp/folder_io.py:724` — `create_project` now calls
  `export_all_schemas` instead of `export_foundation_schemas`.

### Why

Phase 2 (viewer-side domain entity classes) needs a server SSOT that
publishes the full per-kind shape, not just the Foundation subset.
The schema files under `.plot/{project_id}/schema/` will back the
TS↔Pydantic field-name parity test introduced when
`viewer/src/domain/` lands in Phase 2.0.

### Verification

- `uv run pytest` — 214 / 214 passed (207 prior + 7 new).
- `uv run mypy plot_mcp/` — Success: no issues found in 17 files.
- `uv run ruff check plot_mcp/ tests/` — All checks passed.

## [0.14.17] — 2026-05-12

v0.15 structural reset Phase 1.2 — atomic flip. God `SketchNode`
class retired; `SketchNode` is now a 15-way Pydantic discriminated
union dispatched on the `kind` literal. The 4 composition kinds
(metric / step / rule / content) join the per-class family. No
behaviour change; round-trip and migration paths preserved
(D-2026-05-12-B).

### Added

- `plot_mcp/models.py` — four composition Pydantic classes:
  - `MetricNode` (target / measurement)
  - `StepNode` (order: int | None / outcome)
  - `RuleNode` (policy / enforcement / actor_permissions)
  - `ContentNode` (format / producer_actor_id / consumer_actor_id)
- `plot_mcp/models.py` — `SketchNode` is now
  `Annotated[Union[15 per-kind classes], Field(discriminator="kind")]`.
  Pydantic dispatches construction / validation on the `kind` literal;
  `CanvasDoc.nodes: list[SketchNode]` automatically narrows.
- `plot_mcp/models.py` — `SketchNodeAdapter: TypeAdapter[SketchNode]`
  exposed for raw-dict validation outside a `CanvasDoc` wrapper
  (e.g. WebSocket payloads in v0.15 Phase 2).
- `plot_mcp/models.py` — `BaseNodeFields._details_path_is_safe`
  validator (hoisted from the retired god class) so every per-kind
  class enforces the path-traversal check at construction time.
- `plot_mcp/models.py` — `ActorRefNode.side` field. Mirrors the
  referenced actor's side so canvases can colour-code without
  dereferencing the master each render.
- `plot_mcp/migrate.py` — `_V01SketchNode` legacy class. Permissive
  superset that accepts v0.1 raw JSON (including the legacy
  `mission` / `core_values` / `identity` god string fields). Owned by
  the migration module; `models.py` stays clean of legacy concerns.
- `plot_mcp/migrate.py` — `_v01_to_service` / `_v01_to_composition`
  converters. Translate `_V01SketchNode` instances into current
  per-kind classes at the canvas-build boundary.
- `plot/tests/test_node_models.py` — 10 new tests:
  - 5 round-trip per composition kind (metric / step ordered + unordered
    / rule / content).
  - 5 discriminated-union dispatch via `SketchNodeAdapter`
    (actor / metric / actor_ref-with-validator / unknown-kind /
    missing-kind rejections).

### Removed

- `plot_mcp/models.py` — god `SketchNode` class (203 LOC, lines
  102-305 in v0.14.16). Every kind's typed-text fields no longer
  pool together as defaults on a single class.
- `plot_mcp/models.py` — `_REF_KIND_TO_ID_FIELD` map and the god
  `_ref_kind_requires_ref_id` validator. Each ref kind class now
  owns its own validator (added in v0.14.16).
- Tests — `test_typed_fields_default_to_empty` (god polymorphism
  check; replaced by `test_actor_does_not_carry_foreign_typed_fields`
  which now asserts the OPPOSITE: that ActorNode does NOT carry
  Mission's typed fields).

### Changed

- 134 call sites across `plot_mcp/migrate.py`, `plot_mcp/folder_io.py`,
  `tests/test_canvas_doc.py`, `tests/test_folder_io.py`, and
  `tests/test_sync.py` migrated from `SketchNode(id=..., kind="X", ...)`
  to the per-kind constructor `XNode(id=..., ...)`. One-shot codemod
  written + applied + deleted (no committed migration scaffolding).
- `plot_mcp/migrate.py` — `_build_actors_canvas`, `_split_services`,
  `_backfill_actor_sides`, `_ensure_minimum_actors` now consume
  `_V01SketchNode` (legacy) and emit per-kind class instances
  (current). Conversion happens at the function boundary; downstream
  helpers operate on current per-kind classes.
- `tests/test_canvas_doc.py::test_actor_permissions_default_empty`
  rewritten to validate via `SketchNodeAdapter.validate_python(...)`
  (the union exposed by Pydantic) instead of the retired
  `SketchNode.model_validate(...)`.

### Why

The god `SketchNode` was the load-bearing piece of the v0.14
god-object pattern (D-2026-05-12-B, user direct quote: "엔티티 정의도
안되어 있구요... fromJson, toJson 같은걸 쓰고 클래스를 코드로 만들어서
개념화해야 했다"). v0.14.17 ships the principled atomic flip with
zero remaining ruff / mypy debt and zero behavioural regressions
(207 / 207 tests green, up from 197 in v0.14.16 thanks to the new
composition + adapter coverage).

## [0.14.16] — 2026-05-12

v0.15 structural reset Phase 1.1 — server-side per-class Pydantic
models for 7 of the 11 non-Foundation node kinds (D-2026-05-12-B).
Additive only; god `SketchNode` is untouched and remains the type
backing `CanvasDoc.nodes` until v0.14.17 promotes the union.

### Added

- `plot_mcp/models.py` — seven per-kind Pydantic classes extending
  `BaseNodeFields`:
  - `ActorNode` (motivation / pain / side)
  - `ActorRefNode` (ref_actor_id required + gives / receives)
  - `ServiceNode` (target_side + 6 service-typed fields + do / dont)
  - `CategoryNode` (theme)
  - `MissionRefNode` (ref_mission_id required)
  - `ValueRefNode` (ref_value_id required)
  - `IdentityRefNode` (ref_identity_id required)
- Each ref class carries its own `@model_validator` mirroring the
  dispatch `_ref_kind_requires_ref_id` on god `SketchNode`.
- `plot/tests/test_node_models.py` — 15 tests covering per-class
  round-trip (`Cls.model_validate(Cls(...).model_dump()) == original`),
  ref-id required invariants, and default-field wire parity with the
  god `SketchNode` defaults.

### Why

Per the v0.15 plan (B → A order, no-shim policy), Phase 1 ships
the server SSOT first so viewer entity classes in Phase 2 can mirror
a fully-disciplined Pydantic discriminated union. v0.14.16 is the
additive prep; v0.14.17 promotes `SketchNode` to a 15-way
`Annotated[..., Field(discriminator="kind")]` and retires the god
class.

## [0.14.15] — 2026-05-12

v0.15 structural reset Phase 0 — pre-existing lint / type-check
debt cleared to zero so subsequent phases land on a green baseline
(D-2026-05-12-B). No behaviour change.

### Fixed — `ruff check` → 0 errors

- `plot_mcp/http_app.py` — import block sorted.
- `plot_mcp/md_template.py` — extracted `tail` local variable to fit
  the typed-area / free-prose split under the 100-char line limit.
- `plot_mcp/models.py` — `FoundationNode` discriminated union now
  uses the PEP 604 `X | Y` form instead of `typing.Union[...]`;
  unused `Union` import removed. `_foundation_canvas_rules` error
  message split across two lines.

### Fixed — `mypy plot_mcp/` → 0 errors

Root causes addressed (not suppressed):

- `plot_mcp/schema_export.py` — `_FOUNDATION_KIND_CLASSES` now
  declares `dict[str, type[BaseNodeFields]]` so `cls.model_json_schema()`
  resolves against the Pydantic `BaseModel` API instead of the bare
  `ModelMetaclass`. `_node_canvas_schema` return value gets an
  explicit `dict[str, Any]` annotation.
- `plot_mcp/folder_io.py` — three Foundation-MD helpers
  (`_evict_typed_text_to_md`, `_merge_md_typed_text_into_nodes`,
  `_split_foundation_typed_text_to_md`) narrow `kind = n.get("kind")`
  with an `isinstance(kind, str)` guard before passing to
  `_foundation_md_path` / `parse_md_template` / `render_md_template`
  (which all require `str`, not `Any | None`).
- `plot_mcp/folder_io.py` — removed an unused
  `# type: ignore[arg-type]` on the legacy project-anchor `shape`
  read; renamed the second `edges` local in
  `_evict_legacy_project_anchor` to `all_edges` to satisfy the
  `no-redef` rule.

### Fixed — formatting

`ruff format` applied across `plot_mcp/` + `tests/`. 10 files
reformatted; no semantic changes.

### Why

The v0.15 structural reset requires every phase to leave the tree
green at the commit boundary. Inheriting a pre-existing baseline
of 5 ruff + 12 mypy errors would have made each Phase 1.x ship
fight the noise. Zero-debt cleanup commits first, structural
changes afterward.

## [0.14.14] — 2026-05-12

### Changed — Backlog re-prioritised: v0.15.0 structural reset is now next-session top priority (D-2026-05-12-B)

End-of-session user critique surfaced a fundamental
architectural debt the v0.14.x cleanup commits did not touch:

- No domain layer in `viewer/src/`.
- `SketchNode` is a god TypeScript interface holding every
  kind's flat fields (self-admitted at `types.ts:174`).
- No JSON↔domain boundary (`fromJson` / `toJson` patterns
  return 0 hits across `viewer/src`).
- No real classes (`class` / `export class` returns 0 hits).
- `SketchCanvas.tsx` is one god component serving 3 canvases
  via runtime `canvas_kind` discrimination.
- `SketchInspector.tsx` is 1422 LOC branching on `kind` for
  every typed field.

User direct quotes (recorded in D-2026-05-12-B):

- *"엔티티 정의도 안되어 있구요."*
- *"기본을 못하고 있는겁니다."*
- *"코드 재활용 할 수도 없게 해뒀어요. fromJson, toJson
  같은걸 쓰고 클래스를 코드로 만들어서 개념화해야 했다."*
- *"도메인 레이어 설계가 제대로 되어 있는지도 모르겠구요."*

The v0.14.3–v0.14.12 i18n + cleanup commits delivered correct
surface polish but did not address the god object. Honest
correction logged: the assistant should have surfaced the debt
*before* adding more surface work, not after the user flagged it.

### Added — NEXT_SESSION.md trigger entry

`구조 리셋` / `v0.15` / `도메인` / `엔티티` — any of these as
the first session message fires the v0.15.0 structural reset
plan:

- **Phase A — Domain entity classes** (`viewer/src/domain/` with
  15 per-kind classes + fromJson/toJson + invariants +
  discriminated union).
- **Phase B — Server alignment** with `plot_mcp/models.py`.
- **Phase C — Inspector kind fan-out** (per-kind files).
- **Phase D — Canvas componentisation** (FoundationCanvas /
  ActorsCanvas / ServicesCanvas / ServiceDetailCanvas).
- **Phase E — Cursor / interaction contracts per canvas.**
- **Phase F — Verification.**

### Added — Skills / rules candidate list (user-allowed)

User permission 2026-05-12: *"필요하다면 스킬이나 룰을
만들구요."* Candidates to evaluate at structural-reset session
start (create only those that prove their weight):

- `plot/skills/plot-entity-template/`
- `plot/skills/plot-domain-design/`
- Pre-commit hook `no-god-import` (post-Phase-A)
- Vitest entity-shape round-trip test
- `plot/CLAUDE.md` anti-pattern row: *"Treating raw JSON as
  domain entity (no fromJson boundary)."*

### Parked — old backlog (until structural reset lands)

The 10-item backlog pinned in v0.14.13 is paused. These items
remain valid but should not be picked up before Phase A above:

- i18n audit skill, owner field on SketchNode, Mermaid
  Service-Detail rendering, self-loop visual, Foundation flow
  visual, Plot repository split, isomorphic-git integration,
  MD-as-export migration (user-deferred regardless), snapshot
  work-item layer, v0.15 Actors model migration.

### Not changed

- No code changes. Docs + backlog re-prioritisation only.

### Verification

- Pre-commit gate self-trip → PASS.

## [0.14.13] — 2026-05-12

### Changed — NEXT_SESSION.md backlog pinned (session wrap)

User flagged 2026-05-12 *"이거 다 할일로 지정해두고요"* —
capture every queued item (small wins, meta decisions, mid-size
plans) so the backlog persists into the next session.

Backlog now spelled out across three layers (each layer is a
mirror; pick any one as the source of truth when planning):

- `plot/docs/NEXT_SESSION.md` — three sections (small wins / meta
  decisions / mid-size). 10 items. User picks the next item
  explicitly each session.
- `~/.claude/projects/.../memory/project_plot_next_session.md`
  — full prose with AI's prioritisation analysis +
  repository-split 7-step plan + closed-this-session log.
- TodoWrite (this assistant's session-scoped checklist) — same
  10 items.

### Backlog items recorded (cross-link)

Small wins:
1. i18n audit skill (`plot/skills/plot-i18n-audit/`)
2. `owner` field on `SketchNode`
3. Mermaid Service-Detail rendering UI location
4. Self-loop visual verification (`Service A → Service A`)
5. Foundation single-canvas flow visual check

Meta decisions:
6. Plot repository split (extract `plot/` from noory-ai
   monorepo — AI recommends; user decision)

Mid-size:
7. isomorphic-git integration (PRODUCT_SPEC §6)
8. MD-as-export migration (user-deferred)
9. Snapshot work-item layer
10. v0.15 Actors → v0.13 model (re-evaluate after #8)

### Verification

- Pre-commit gate self-trip → PASS (no code changes; docs +
  plugin.json + CHANGELOG only).

## [0.14.12] — 2026-05-12

### Changed — PRODUCT_SPEC.md revision 2 (D-2026-05-12-A)

User delivered a substantially revised product spec. The new
material:

- **Language split:** Plot is a "mindmap" to users, "graph"
  internally. Cycles + self-loops are part of the model.
- **`isomorphic-git`** added to the tech stack.
- **Source-data version control** is now an explicit subsystem
  (§6 of PRODUCT_SPEC). Canvas JSON / user stories / tasks are
  git-versioned independent of any source-code repo. Snapshot ≡
  commit; agent proposal ≡ branch; user approve ≡ merge.
- **Foundation = one canvas** (Mission + Core value + Identity).
  Resolves the v0.14.7 open question. Audience distinction is
  visual, not structural.
- **Service-Detail starts empty,** fills bottom-up through
  agent-interview + user-story loop. Living document.
- **Service interview produces two artefacts** — Service-Detail
  content + user-story draft, shared provenance.
- **Feedback loop is git-branch shaped** per the new §6.
- **GitHub integration** added to future items.
- **MVP scope section removed** — rev-1 framing dropped.

### Queued — open questions

PRODUCT_SPEC §15 reorganised. Closed: Mission/Identity canvas
split. Added:

- MD-as-export migration (today's co-equal MD becomes derived
  from JSON). Deferred per user direction *"이 부분은 나중에
  다시 다듬어 봅시다."*
- isomorphic-git integration timing.
- i18n string lifecycle skill (delete unused keys) — user
  flagged *"사용되지 않는 것들 삭제하고 하는 거 관리되어야해요."*
- Plot repository split (move out of noory-ai monorepo) — user
  flagged for analysis.

### Not changed (deliberate)

- No code changes — spec-only update.
- SPEC.md / CONCEPTS.md / ROADMAP.md unchanged. Each will get
  its own update when the queued items (MD-as-export, git,
  Foundation merger if not already that way) land.

## [0.14.11] — 2026-05-12

### Added — i18n: Stencil draggable preset labels

Final stencil-side i18n step. Migrates the labels that appear
inside each draggable preset card in `SketchStencil` (visible in
every per-canvas stencil), plus the tooltip / drop-hint text on
the same cards.

**New `stencil.*` keys:**

- `subActor` (Sub-Actor / 서브 액터)
- `dragOntoCanvas` (interpolated `{{name}}`)
- `dropHintIntoCategory` / `dropHintIntoService` /
  `dropHintIntoActor` — replace the three hardcoded English
  drop-hints.

### Changed

- `plot/viewer/src/canvases/SketchStencil.tsx`:
  - `StencilPreset` interface gains optional `labelI18nKey` and
    `dropHintI18nKey` fields.
  - Sub-Actor preset declares `labelI18nKey: "stencil.subActor"`
    (its kind is "actor" so the default `kind.${kind}` fallback
    would conflict with `TOP_LEVEL_ACTOR`).
  - SERVICE_INSIDE_CATEGORY / metric / step / sub-actor declare
    their `dropHintI18nKey`.
  - `StencilItem` renders with `useTranslation()`; resolves the
    label via (preset.labelI18nKey ?? `kind.${preset.kind}` ??
    preset.labelHint). Resolves the drop-hint title similarly.
    The drag-onto-canvas fallback tooltip uses the interpolated
    `stencil.dragOntoCanvas` key.
  - `onDragStart` data-transfer payload strips the new i18n key
    fields (alongside `id` / `labelHint` / `dropHint`) before
    serialising the preset.

### Verification

- `npx tsc --noEmit` clean.
- `npx vitest run` → 14/14 (parity active).
- Browser smoke (Playwright KO on Services): stencil reads
  최상위 / 카테고리 / 서비스 + "카테고리 안에 놓으세요" drop
  hint. Confirmed via direct screenshot.
- Pre-commit gate self-trip → PASS.

### Out of scope

The *initial label of the dropped node* (`preset.label`) stays
language-pinned (English by default). Rationale: as soon as the
drop lands, that string is user data — the user will edit it.
Localising the drop time would create asymmetric data (KO user's
node "미션", EN user's node "Mission") which is wrong: it's the
same project, viewed in different locales. The stencil-side
label (visible only while dragging) follows locale; the dropped
node's label is data and stays as-is.

### Queued — separate diagnosis

- "❀ ❀ ❀" Inspector MD preview font fallback investigation.
- "1 validation error for CanvasDoc Val…" toast briefly during
  Inspector load — verify whether it persists.

## [0.14.10] — 2026-05-12

### Added — i18n: composition lists + Long-form details + Actor placeholder (Phase C)

Final Inspector i18n phase. Migrates the remaining Service
composition lists (Rules / Contents), the Long-form details
section, and the Actor v0.3 placeholder.

**New `composition.*` keys:**

- `add` (+ Add / + 추가)
- `expand` / `collapse` (펼치기 / 접기)
- `namePlaceholder` (Name / 이름)
- `remove` (Remove / 삭제)
- `confirmRemove` (interpolated `{{name}}`)
- `untitled` ((untitled) / (이름 없음))
- `rules` (Rules / 규칙)
- `rulesSubtitle` ("정책 · 제약 · SLA · 권한" — user-approved)
- `contents` (Contents / 콘텐츠)
- `contentsSubtitle` ("아티팩트 · 결과물 · 자산" — user-approved)

**New `inspector.*` keys:**

- `actorCompositionDeferred` ("v0.3 에서 액터 구성(권한 · 기능 ·
  목표 · 상태)을 지원할 예정입니다." — user-approved)
- `longFormDetailsHeader` (장문 상세)
- `longFormDetailsIntro` (Korean retained verbatim; English
  translation user-approved)
- `createDetails` (📁 상세 만들기)
- `creating` (생성 중…)

All new hint sentences in this commit went through the
`AskUserQuestion` review workflow per `I18N_KO_GLOSSARY.md` §3.

### Changed

- `plot/viewer/src/canvases/SketchInspector.tsx`:
  - `CompositionList` migrated (title / subtitle pass-through;
    `+ Add` button; empty-state placeholder).
  - `CompositionRow` migrated (expand / collapse aria + title;
    Name placeholder; Remove confirm dialog with `{{name}}` +
    `(untitled)` fallback; Remove aria-label).
  - `DetailsSection` migrated (header; intro paragraph; busy
    label; idle label).
  - Actor v0.3 placeholder migrated.
- `plot/viewer/src/i18n/locales/{en,ko}.json` — ~15 new keys.

### Verification

- `npx tsc --noEmit` clean.
- `npx vitest run` → 14/14 (parity active).
- Browser smoke (Playwright KO on Services → Login Inspector):
  서비스 / 라벨 / ✕ 삭제 / 장문 상세 / 📁 상세 만들기 / 대상
  측 운영자측 / 무엇 / 만드는 가치 / 범위 / 트리거 / 방법 /
  결과 / 할 것 / 하지 말 것. Category node badge reads 카테고리.
- Pre-commit gate self-trip → PASS.

### Queued — v0.14.11 (Stencil draggable labels)

The labels INSIDE each draggable preset in `SketchStencil`
("Mission" / "Core Value" / "Identity" / "Actor" / "Sub-Actor" /
"Category" / "Service" / "Metric" / "Step" / "Rule" / "Content")
are still English. They render via `StencilPreset.label`
hardcoded in TS module-level constants. Migration needs a
runtime t() call at the StencilItem render site (since module-
level constants can't call hooks). Small follow-up commit.

### Queued — separate diagnosis (deferred)

- "❀ ❀ ❀" Inspector MD preview font fallback investigation.
- "1 validation error for CanvasDoc Val…" toast briefly visible
  during Inspector load — not regression (pre-existing, surfaced
  by Playwright nav timing). Worth a closer look if it persists.

## [0.14.9] — 2026-05-12

### Added — i18n: Inspector typed-field labels per kind (Phase B)

Continues v0.14.8. Migrates every Inspector typed-field section
across all node kinds (Mission / Category / Service / actor_ref /
Actor / Metric / Step / FoundationRef / CoreValue / Identity /
DoDont / Rule / Content). All section headers reuse the
`kind.*` SSOT from v0.14.8.

**New `inspector.field.*` keys** (label per field):

- theme / whatWeDo / why / direction / targetSide / what /
  valueCreated / scope / trigger / how / outcome / policy /
  enforcement / actorPermissions / format / producer / consumer /
  definition / description / side / motivation / pain / target /
  measurement / order / gives / receives / do / dont /
  longFormDetails.

**New `inspector.fieldHint.*` keys** (italic hint per field).
Translated to natural Korean per the new
[`I18N_KO_GLOSSARY.md`](docs/I18N_KO_GLOSSARY.md) workflow.

**Misc new `inspector.*` keys** (modal flow + select options):

- `valueFlowHeader` (이 서비스 ↔ 이 액터 가치 흐름 헤더)
- `referencesHeader` (interpolated `{{label}}`)
- `rePick` / `unset` / `empty` /
  `operatorOption` / `userOption` / `operatorSideOption` /
  `userSideOption` / `bothSideOption` /
  `addActorPermission` / `permissionRemove` / `masterNotFound`.

### Added — `plot/docs/I18N_KO_GLOSSARY.md`

New doc capturing:

1. Canonical Plot vocabulary (Korean spellings the project
   commits to — 미션 / 코어밸류 / 아이덴티티 / 액터 / 서비스 /
   파운데이션 / 등).
2. UI-context fragments (Undo / Redo / Delete / etc.).
3. **Hint-sentence review process** — before committing new
   `inspector.fieldHint.*` strings, surface them via
   `AskUserQuestion` for review. The AI-translated-Korean
   failure mode (e.g. 측면별로 → 속성별로) is structural, not
   one-off, so the workflow needs a gate.
4. Correction log — every user-driven Korean fix gets a row so
   the same mistake does not repeat across sessions.

### Fixed — Korean translation drift caught by user 2026-05-12

- `stencil.note.identityOnePerAspect`: 측면별로 하나씩 →
  **속성별로 하나씩** (user direction; 측면 is unnatural in this
  register).
- `IdentityFields` description placeholder: 이 측면이 어떻게
  드러나는가 → **이 속성이 어떻게 드러나는가** (same rule).
- `ActorFields` motivation placeholder: "이 actor 가 …" →
  **"이 액터가 …"** (canonical naming consistency).

### Changed

- `plot/viewer/src/canvases/SketchInspector.tsx` — every
  `<Fields>` subcomponent (10 of them) gained `useTranslation()`;
  ~50 hardcoded label / hint strings replaced with `t()`
  lookups; per-kind section headers now read from `kind.*`.
- `plot/viewer/src/i18n/locales/{en,ko}.json` — net ~40 new keys.

### Verification

- `npx tsc --noEmit` clean.
- `npx vitest run` → 14/14 passed (parity test active; en/ko
  remain in sync).
- Browser smoke (Playwright KO on Foundation): Mission node →
  Inspector header shows 미션 + 라벨 + ✕ 삭제; Mission section
  reads 미션 / 하는 일 — 현재형으로 표현한 매일의 활동 / 이유
  — 존재 이유 / 방향 — 포지셔닝 (공간이지 시간이 아님). Stencil
  reads 속성별로 하나씩 — 목소리, 에너지, 말투, …
- Pre-commit gate self-trip → PASS.

### Queued — Phase C (v0.14.10)

- Composition items (Name placeholder, Remove, Expand / Collapse,
  Rules / Contents tab labels).
- "Creating…" / "📁 Create details" button.
- Foundation-ref label prefix (already handled in Phase B
  references header; verify no straggler).
- `body` placeholder / Edge modal headers.

### Queued — separate

- "❀ ❀ ❀" Inspector MD preview font fallback investigation.

## [0.14.8] — 2026-05-12

### Added — i18n: kind labels SSOT + Inspector header / actions / Label

Continues the v0.14.4 → v0.14.6 i18n rollout. This is **Phase A**
of the Inspector migration. Two more phases follow (typed-field
section labels per kind, then composition items / modals / misc).

**New `kind.*` namespace** — canonical Plot kind names per
locale. Korean follows the user-provided product spec's canonical
vocabulary (2026-05-11):

- project / actorRoot / node / mission / core_value / identity /
  actor / actor_ref / mission_ref / value_ref / identity_ref /
  service / category / metric / step / rule / content.

Korean values: 프로젝트 / 액터 루트 / 노드 / 미션 / 코어밸류 /
아이덴티티 / 액터 / 액터 (참조) / 미션 (참조) / 코어밸류 (참조)
/ 아이덴티티 (참조) / 서비스 / 카테고리 / 지표 / 단계 / 규칙 /
콘텐츠.

**New `kindTag.*` namespace** — the small UPPERCASE label
painted top-left of each node (`SketchNode`). Subset of kinds
that get the visual badge per `KIND_TAG_KINDS`: project / mission
/ core_value / identity / metric / step / category.

**New `inspector.*` keys** — header bar + actions + Label field:

- label / deleteNode / deleteShort / confirmDelete (interpolated
  `{{name}}`).
- narrow / widen / narrowInspector / widenInspector /
  closeInspector.
- mdWarnings / mdWarningsFixHint (HTML-interpolated `{{path}}`,
  rendered via `dangerouslySetInnerHTML` for the `<code>` tag).

### Changed

- `plot/viewer/src/canvases/SketchNode.tsx` — replaced the
  hardcoded `KIND_TAG_LABELS` lookup with a membership-only
  `KIND_TAG_KINDS` set + `t(\`kindTag.${kind}\`)` lookup. The
  badge text now follows the user's locale.
- `plot/viewer/src/canvases/SketchInspector.tsx` — `useTranslation()`
  in `SketchInspector`; kind badge in header reads from `kind.*`
  with the `project` / `actorRoot` fallback chain; delete button
  text + tooltip + confirm dialog use `inspector.*`; narrow/widen
  + close labels + tooltips use `inspector.*`; MD warnings panel
  header + fix hint (with `<code>{{path}}</code>` interpolation)
  use `inspector.mdWarnings*`; Label field heading uses
  `inspector.label`.
- `plot/viewer/src/i18n/locales/ko.json` — retroactive label fix
  per user direction: `canvas.tabs.foundation` 토대 → **파운데이션**.
  (v0.14.5 shipped 토대; v0.14.6 corrected actors 행위자 → 액터;
  this commit completes the canonical-naming pass on the tabs.)

### Verification

- `npx tsc --noEmit` clean.
- `npx vitest run` → 14/14 passed (parity test still passes;
  `kind` + `kindTag` + `inspector` keys present in both locales).
- Browser smoke (Playwright KO sweep on Foundation): node badges
  read 미션 / 코어밸류 / 아이덴티티; Inspector top-bar reads 미션
  + ✕ 삭제 + 라벨; tabs read 파운데이션 / 액터 / 서비스.
- Pre-commit gate self-trip → PASS (styles.css not touched).

### Queued — Phase B (v0.14.9)

- Inspector typed-field section labels per kind:
  - Mission: What we do / Why / Direction.
  - Core value: Definition / Do / Don't.
  - Identity: Description / Do / Don't.
  - Actor: Side / Motivation / Pain / Target side.
  - Service: What / Value created / Scope / Trigger / Outcome /
    Theme.
  - actor_ref: Gives / Receives.
  - step: Order / Outcome.
  - metric: Target / Measurement.
  - rule: Policy / Enforcement / Actor permissions.
  - content: Format / Producer / Consumer.
  - Long-form details.

### Queued — Phase C (v0.14.10)

- Composition items (Name placeholder, Remove, Expand/Collapse).
- Inspector edit / split / preview tabs.
- Foundation refs label ("Actor:" prefix).
- Inspector "Create details" button.
- ⚠ MD preview "❀ ❀ ❀" font fallback investigation.

## [0.14.7] — 2026-05-11

### Added — `plot/docs/PRODUCT_SPEC.md` (D-2026-05-11-E)

User delivered a Plot product spec mid-session covering platforms,
business model, tech stack, data principles, Figma-style symbol
system, four canvas layers, agent-interview UX, snapshot work-item
layer, PR-style feedback loop, MVP scope, future items. Per user
direction *"이건 잘 정리해두세요"* the spec is pinned as a new
canonical document.

**Position:** PRODUCT_SPEC sits *above* VISION.md in the doc set.
VISION = the essence; PRODUCT_SPEC = how the essence becomes a
shippable product (platforms, business model, MVP scope).

**Translation:** Korean source → English per noory-ai CLAUDE.md
"Language" rule. Korean vocabulary preserved where it's a Plot
term (Mission / Core value / Identity / Actor / Service / User
journey / Snapshot).

**Open questions captured in §16** (not decided in this commit):

1. `owner` field on every node — multi-user prerequisite. Land
   date unset.
2. Mission-Core-value vs Identity canvas split (audience: humans
   vs agents). Today both live in Foundation.
3. PR-style feedback loop enforcement — MCP tools today write
   directly.
4. Snapshot work-item layer — net-new subsystem.
5. Mermaid Service-Detail rendering — UI location unset.
6. `canvas.tabs.foundation` Korean label review if Mission /
   Identity canvases split.

### Changed

- `plot/docs/VISION.md` — Cross-references now point at
  PRODUCT_SPEC first.
- `plot/CLAUDE.md` — reading order updated; PRODUCT_SPEC is step
  2 (right after VISION, before DOMAIN).
- `plot/docs/DECISIONS.md` — new D-2026-05-11-E entry pinning the
  decision.

### Not changed (deliberate)

- No code changes.
- No canvas / kind / Inspector behaviour changes.
- SPEC.md / CONCEPTS.md / ROADMAP.md / DOMAIN.md left as-is — each
  remains the source of truth for its own concern. PRODUCT_SPEC
  cross-links into them.

## [0.14.6] — 2026-05-11

### Added — i18n migration: Stencil section headers + helper notes

Continues v0.14.5. Migrates the SketchStencil's per-canvas section
labels and helper notes across all four canvases (Foundation /
Actors / Services / Service-Detail).

Korean translations align with the canonical Plot vocabulary
provided by the user 2026-05-11:

> 심볼 종류: 미션, 코어밸류, 아이덴티티 / 액터 / 서비스

So Korean reads as 미션 / 코어밸류 / 아이덴티티 / 액터 / 서비스 —
NOT a literal "정체성" / "행위자" / "핵심 가치" translation.

### Translated keys added

`stencil.section.*`:
- mission / coreValues / identity / topLevel / actorHierarchy /
  service / composition / actors / missions / identityAspects

`stencil.note.*`:
- addAsManyAsYouNeed (필요한 만큼 추가하세요)
- identityOnePerAspect (측면별로 하나씩 — 목소리, 에너지, 말투, …)
- dropOnActor (액터 위에 놓으세요)
- dropInsideCategory (카테고리 안에 놓으세요)
- compositionInsideService (이 서비스 안의 지표 + 단계)
- dragActorOntoService (이 서비스에 액터를 끌어 놓으세요)
- dragMissionThisServiceAnswersTo
- dragValueThisServiceEmbodies
- dragIdentityAspectThisServiceExpresses

### Changed

- `plot/viewer/src/canvases/SketchStencil.tsx` — `useTranslation()`
  in `SketchStencil`; replaced 10 hardcoded `title=` props and 8
  hardcoded `note=` props with `t()` lookups across the four
  per-canvas branches.
- `plot/viewer/src/i18n/locales/ko.json` — `canvas.tabs.actors`
  corrected from "행위자" to "액터" per the user-provided product
  spec's canonical naming. (Was set in v0.14.5; before that locale
  reached any user, so retroactive fix in the same i18n rollout.)

### Verification

- `npx tsc --noEmit` → clean.
- `npx vitest run` → 14/14 passed (parity test catches en/ko
  drift).
- Browser smoke (Playwright KO sweep): Foundation stencil shows
  미션 / 코어밸류 / 아이덴티티 with the new notes. Tabs read
  토대 / 액터 / 서비스 as expected.
- Pre-commit gate self-trip → PASS (styles.css not touched).

### Queued for v0.14.7+

- Inspector form labels (largest single migration surface; will
  land as its own commit / session).
- Plot product spec → `plot/docs/PRODUCT_SPEC.md` consolidation
  per user direction 2026-05-11 ("이건 잘 정리해두세요. 작업 다
  끝나고").
- "❀ ❀ ❀" MD preview font fallback investigation.

## [0.14.5] — 2026-05-11

### Added — i18n migration: canvas tabs + Mark session + Service-Detail modal header

Continues the v0.14.4 i18n rollout. Migrates the next-most-visible
surface: the three canvas tab labels at the top of the viewer, the
"Mark session…" button + its hint, and the Service-Detail modal's
header / aria-label / close-button.

**Translated keys added to `en.json` + `ko.json`:**

- `canvas.tabs.foundation` / `canvas.tabs.actors` / `canvas.tabs.services`
  — 토대 / 행위자 / 서비스.
- `header.markSession` / `header.markSessionHint` — 세션 기록… /
  현재 프로젝트 상태에 git 태그를 찍습니다.
- `serviceDetail.label` — 서비스 상세.
- `serviceDetail.ariaWithCategory` / `serviceDetail.ariaWithoutCategory`
  — interpolation-driven aria-label so screen readers see the
  Korean "서비스 상세 — {category} › {service}" form.

**Changed:**

- `plot/viewer/src/App.tsx` — replaced hardcoded `CANVAS_TABS`
  label table with `CANVAS_TAB_IDS` + `t("canvas.tabs.{id}")`,
  switched `aria-label="Canvas"` to `t("canvas.aria")`, swapped
  the `Mark session…` button text + hint, and rewrote
  `ServiceDetailModal` to read all visible / aria text from i18n
  (including the close-button label/title via the existing
  `shell.closeEsc` key).

### Out of scope this release (queued for v0.14.6+)

- Stencil section headers (TOP-LEVEL, MISSION, CORE VALUES,
  IDENTITY, ACTOR HIERARCHY, COMPOSITION, ACTORS, IDENTITY
  ASPECTS) and helper hints ("add as many as you need", "drop
  inside a Category", "drop on an Actor").
- Inspector form labels and section headers (largest single
  migration surface; will land as its own commit / session).
- Investigation: Inspector MD preview renders `* * *` separators
  as "❀ ❀ ❀" — looks like a font fallback issue, queued for
  separate diagnosis.
- Decision: Plot kind labels (Mission, Core Value, Identity,
  Actor, Service, Category, …) shown inside nodes — stay English
  as canonical kind names vs. localise? Will surface as an
  AskUserQuestion before the v0.14.6 Stencil migration lands.

## [0.14.4] — 2026-05-10

### Added — i18n infrastructure (English primary, Korean locale) — D-2026-05-11-D

Plot is being positioned as a global service (user direction
2026-05-10: *"이건 글로벌 서비스가 될거거든요"*). This release
boots the i18n stack and migrates the most visible UI strings.
Remaining hardcoded text (Inspector forms, Stencil, modals,
context menus, App-level toasts) is queued for follow-up commits;
the new anti-pattern row + parity test prevent NEW hardcoded text
from leaking in.

**New module — `plot/viewer/src/i18n/`:**

- `index.ts` — bootstraps `i18next` + `react-i18next` +
  `i18next-browser-languagedetector`. Detection order
  `localStorage["plot:lang"] → navigator.language → en`. Fallback
  `en`. Imported for side effects from `main.tsx`.
- `locales/en.json` — primary resource bundle.
- `locales/ko.json` — Korean locale.
- `LanguageToggle.tsx` — compact EN / KO pill rendered at the
  bottom of `SketchSidebar`. Choice persists via localStorage.

**Migrated strings (this commit):**

- `SketchToolbar.tsx` — Undo / Redo button labels + tooltip
  shortcuts.
- `SketchSidebar.tsx` — collapse / expand controls, "Projects"
  header, "+ New project" button, "(none yet)" placeholder,
  per-project Rename / Delete buttons + confirm dialogs, "Session
  tags" section + per-tag confirm dialogs + delete tooltips.

**Guards:**

- `plot/viewer/tests/i18n-keys-parity.test.ts` — Vitest static
  guard asserting `ko.json` has the identical key set as `en.json`
  and every value is a non-empty string. Locale drift is a build
  failure.
- `plot/CLAUDE.md` anti-patterns table — new row "Hardcoding
  user-facing UI text in a viewer component", pointing to
  D-2026-05-11-D.

**Dependencies added:** `react-i18next ^15`, `i18next ^23`,
`i18next-browser-languagedetector ^8`. ~30KB cost (production
build) is acceptable for a viewer that already ships Mermaid +
React Flow + React Markdown.

**Out of scope this release** (queued for follow-up):

- Inspector typed-field labels per kind (largest single migration
  surface).
- Stencil draggable labels.
- Modal headings and confirm dialogs in `SketchModals`.
- App-level toast / error messages.
- Context-menu items.

## [0.14.3] — 2026-05-10

### Added — Cursor ⊥ auto-layout structural gate (D-2026-05-11-C)

Concludes the architectural review queued via the `NEXT_SESSION.md`
"다음" trigger filed in D-2026-05-11-B.

**Diagnosis:** the perceived cursor ↔ auto-layout coupling was
*cognitive (commit bundling in v0.13.10)*, not *mechanical (shared
files)*. Empirical verification of v0.13.7..v0.14.2 git history:
`viewer/src/styles.css` was never modified by any auto-layout
commit, and `autoLayout.ts` was never modified by any cursor
commit. The cursor flicker root cause (RF v11 `role="button"` +
Tailwind preflight) had existed since v0.13.0; the auto-layout
work merely surfaced it during browser verification.

**Three orthogonal enforcement mechanisms ship in this release:**

- `plot/hooks/pre_commit_gate.py` — new
  `cross_cutting_bundle_check()` denies commits that stage
  `viewer/src/styles.css` (cross-cutting visual SSOT) alongside
  feature code under `viewer/` or `plot_mcp/`. Tests excluded from
  the "feature" category.
- `plot/viewer/tests/styles-cursor-baseline.test.tsx` — static
  Vitest guard asserting `styles.css` contains zero cursor
  declarations outside comments. Adding a cursor rule requires a
  fresh `D-YYYY-MM-DD-X` decision id and updating the test
  together — the audit trail becomes mechanical.
- `plot/agents/plot-verifier.md` — Step 4 default now runs the
  cursor DOM probe sweep FIRST on every viewer change, regardless
  of declared change kind. Latent cross-cutting visual regressions
  cannot hide behind unrelated feature commits.
- `plot/CLAUDE.md` anti-patterns table — new row "Bundling a
  cross-cutting visual change with a feature change in one
  commit", pointing to D-2026-05-11-C.

**No viewer behaviour change. No DOMAIN.md change** — DOMAIN.md
line 205 already correctly characterises cursor as cross-cutting
with no natural domain home. The right enforcement layer is
commit hygiene + static guard + verification default, not domain
re-modelling.

Code-level alternatives (extract `cursorContract.ts` module,
refactor `useNodesMemo` / `useEdgesMemo`) considered and rejected
as YAGNI — `styles.css` is 27 LOC with zero cursor rules
post-v0.14.2, and the ghost-edge symptom from v0.13.9 was already
resolved by D-2026-05-10-G.

## [0.14.2] — 2026-05-11

### Removed — All cursor cancellation rules; pure RF default + Tailwind preflight

User direction: *"일단 RF 기본으로 돌리라구요. 이해를 못하지?"* The
v0.13.6 (D-2026-05-10-C) and v0.13.10 (D-2026-05-10-F) Tailwind
preflight cancellation rules were the assistant repeatedly forcing
`node = grab` to match RF's nominal default — but the user's
mental model was always "node = pointer (clickable), pane = grab
(pannable), handle = crosshair (drawable)" which is **exactly what
pure RF default + Tailwind preflight composes to** with zero
overrides.

`viewer/src/styles.css` now contains only `@tailwind` imports and
`html/body/#root` sizing. Resulting cursors:

| Region | Cursor | Source |
|---|---|---|
| `.react-flow__pane` | `grab` / `grabbing` | RF default |
| `.react-flow__node` (RF v11 sets `role="button"`) | `pointer` | Tailwind preflight `[role="button"]` |
| `.react-flow__node.dragging` | `grabbing` | RF default beats preflight via specificity |
| EditableText label span (`role="button"`) | `pointer` | Tailwind preflight |
| Fold `<button>` | `pointer` | Tailwind preflight |
| `.react-flow__handle.connectionindicator` | `crosshair` | RF default |
| Resize controls | `ew/ns/nwse/nesw-resize` | `@reactflow/node-resizer` default |

Anchor body shows `grab` because the anchor uses a static `<span>`
(no EditableText, no `role="button"`); the inner divs inherit the
parent's cursor without preflight matching them. Acceptable
asymmetry per D-2026-05-11-A.

### Removed — MiniMap (bottom-right overview)

User: *"오른쪽 아래에 있는 오버뷰? 이거 없애요."* Drop the
`<MiniMap zoomable pannable />` and its import from
`viewer/src/canvases/SketchCanvas.tsx`. The lower-right corner is
now empty.

### Added — `plot/docs/NEXT_SESSION.md` queue + SessionStart hook integration

User: *"다음세션에서 심층적으로 검토하고 개선할 수 있게 해두세요.
다음세선서 '다음' 이라고 하면 이거 해야해요."*

A new `plot/docs/NEXT_SESSION.md` file holds keyword-triggered tasks
that the assistant should pick up at the next Plot session start.
The first queued item: **`다음`** ⇒ architectural review of how
auto-layout work bled into cursor code (see D-2026-05-11-B for
context, NEXT_SESSION.md for full scope).

`plot/hooks/session_start.py` reads `NEXT_SESSION.md`'s "Active
queue" section and surfaces each `### \`<TRIGGER>\` — <title>`
heading in the SessionStart `additionalContext`. The assistant
watches the user's first message; if it contains a trigger keyword,
that item becomes the active task.

### Added — DECISIONS.md entries

- **D-2026-05-11-A** — Pure RF default cursors + MiniMap removal,
  with the lesson "default to NO cursor rules in `styles.css`".
- **D-2026-05-11-B** — Architectural concern: auto-layout work
  affected cursor code; review queued for next session via the
  `다음` trigger.

### Updated — SPEC.md / CURSOR.md

Both rewritten to reflect "no overrides" and the resulting cursor
table. CURSOR.md change-history extended with the v0.14.2 entry.

### Verification

- `tsc --noEmit`: clean.
- `vitest run`: 11/11 passing.
- Playwright probe: pane=`grab`, mission body span=`pointer`,
  handle=`crosshair`, anchor body=`grab` (asymmetry as documented),
  MiniMap absent.
- SessionStart hook smoke test: VISION + 5 DECISIONS + `다음`
  trigger all surfaced in `additionalContext`.

## [0.14.1] — 2026-05-10

### Removed — Auto-layout (again)

User cost/benefit call: *"근데 auto layout 빼야겠네 문제가 너무 많다.
넣고 나서 커서 들에 문제 너무 많고."*

The feature added across v0.13.8 (spec) → v0.13.9 (impl) → v0.13.10
(button placement) carried more debugging / verification load than
its current value justified. Plot has no users with complex
multi-actor / multi-service graphs yet; the layout-readability
benefit is theoretical at this stage. Re-introduction in the future
needs a fresh decision id with concrete user workflows in evidence.

### Honest correction — cursor problems were not caused by auto-layout

The user temporally associated cursor flicker with auto-layout
(*"넣고 나서 커서 들에 문제 너무 많고"*). The actual root cause was
unrelated and was diagnosed + fixed in v0.13.10 (D-2026-05-10-F):
RF v11 sets `role="button"` on `.react-flow__node`; Tailwind preflight
matches that selector and overrides the RF default `cursor: grab`.
The Tailwind preflight cancellation rule in `viewer/src/styles.css`
fixes the flicker independently of auto-layout's existence. This
removal therefore does not undo any cursor fix — Plot v0.14.1 still
has uniform `grab` on pane and nodes, no flicker.

### Files removed

- `viewer/src/canvases/sketch/autoLayout.ts` (297 LOC pure algorithm).
- `viewer/src/canvases/sketch/useAutoLayout.ts` (43 LOC React bridge).
- `viewer/tests/autoLayout.test.ts` (11 unit tests).

### Files reverted

- `viewer/src/canvases/SketchCanvas.tsx`:
  - Drop `ControlButton` from the React Flow imports.
  - Drop `useAutoLayout` import.
  - Drop the `applyAutoLayout` hook call and the `<ControlButton>`
    block inside `<Controls>`.
  - LOC 366 → 360 (back to the v0.13.7 baseline).
- `viewer/tests/SketchCanvas.regression.test.tsx`:
  - The `'toolbar does not render an Auto layout button'` test from
    v0.13.8 is restored (with a new comment block referencing the
    full lineage D-2026-05-04-D → -10-E → -10-G).

### Documentation

- `docs/SPEC.md` §Auto-layout — rewritten to "Removed" with a single
  history paragraph linking the four-decision lineage.
- `docs/DECISIONS.md`:
  - **D-2026-05-10-E** marked **Rejected (rolled back v0.14.1)** with
    a forward pointer to D-2026-05-10-G.
  - **D-2026-05-10-G** new entry, Accepted, with the cost/benefit
    reasoning + the cursor-causation correction + the
    re-introduction policy (must cite real-user workflows and
    cost/benefit comparison).

### Verification

- `tsc --noEmit`: clean.
- `vitest run`: 11/11 passing (24 → 11 because the 11 auto-layout
  tests were deleted with their source; the remaining 11 cover
  every other regression and pass after the inverted auto-layout
  test was re-inverted).

## [0.14.0] — 2026-05-10

### Added — Plot dev infrastructure (the "AI develops Plot reliably" milestone)

After two weeks of tactical fixes (six rounds on cursor; auto-layout
misattributed; SPEC drift across sessions), the user's diagnosis cut
through: *"플러그인 설치가 되어 있는데? 왜? 그러지? ... 진짜 큰일이네
... 필요한 스킬, 룰, 서브 에이전트들, 다 만들면서 해야 제대로 빠르고
효율적으로 일 할 수 있습니까? 그럼 그렇게 하구요."*

The fix is structural: replace human-memory-dependent rules with
deterministic infrastructure that fires automatically. This release
ships the full set so the next session inherits a workable AI dev
environment instead of starting from "be careful next time."

#### `docs/VISION.md` (new) — single-source-of-truth essence

The one sentence that overrides every other priority:

> **Plot 은 본질을 모르는 사람이 본질을 찾고, 그걸 놓치지 않으면서, 그
> 본질 아래에서 서비스를 쉽게 기획·개발할 수 있게 AI 와 협업하는
> 툴이다.**

Plus the three-phase cycle (Discovery / Retention / Execution with
AICollaboration cross-cutting), who Plot is for, the feature-decision
checklist, and a banned-pattern table calibrated to past drift
(cursor 6 rounds; auto-edges D-2026-05-04-A; auto-layout removal
D-2026-05-04-D).

#### `docs/DOMAIN.md` (new) — bounded contexts + ubiquitous language

Translates VISION into 5 bounded contexts:

- **EssenceDiscovery** — Foundation canvas, Inspector typed text
- **EssenceRetention** — anchor injection, cross-canvas refs
- **EssencePlanning** — Actors / Services, value-flow, auto-layout
- **EssenceExecution** — Service-Detail, MCP tools
- **AICollaboration** — cross-cutting (skills, hooks, agents, MCP)

Each context names its surfaces, what it owns vs not, current code
home (with file paths), and where current code violates the model
(refactor candidates with severity).

Plus the ubiquitous language table that disambiguates Plot terms
("Node" vs "rf-node" vs DOM node, "Service" vs REST service, etc.),
the entity-vs-VO classification, and the dependency-direction
mermaid that codifies "EssenceExecution may read EssenceDiscovery
but not the reverse."

#### `skills/plot-frontend-bug-diagnosis` (new) — Playwright probe-first

The deterministic procedure that v0.13.10 finally stumbled on after
six failed cursor rounds. Triggers on `cursor / hover / pointer /
hit-test / flicker / 깜빡` keywords. 10 mandatory steps:

1. Verify Playwright + dev server.
2. Navigate to affected canvas.
3. Baseline screenshot.
4. Cursor / hit-test probe at suspect coordinates (templates included).
5. Walk parent chain to find the cursor source.
6. Identify source rule (CSS file + selector + line).
7. Propose fix anchored to probe.
8. Apply fix, re-probe.
9. Confirmation screenshot.
10. Update SPEC + CURSOR + DECISIONS per Gate 0.

Banned shortcuts table (5 patterns) + quick-reference for common Plot
cursor bug patterns.

#### `skills/plot-feature-tdd` (new) — essence-anchored test-first

Triggers on `feature / 기능 추가 / 만들어줘 / add / implement`. 10
mandatory steps:

1. Re-read VISION.md first sentence.
2. Identify VISION phase.
3. Look up bounded context in DOMAIN.md.
4. Sketch entity / VO touched.
5. Check SPEC.md for existing coverage.
6. Write regression test FIRST (Red).
7. Implement minimally (Green).
8. Browser-verify with `plot-verifier` agent.
9. Update SPEC + DECISIONS + CHANGELOG (Gate 0).
10. Commit + push (Gate 4).

Non-negotiables table (test first; one context per change; no SPEC
drift; browser-verify all UI changes; never grow oversize files;
never auto-emit user-visible state).

#### `hooks/session_start.py` (new) — surface VISION + recent DECISIONS

Runs on every Claude Code session start when the Plot plugin is
loaded. Emits an `additionalContext` payload that prepends to the
assistant's system prompt:

- VISION.md essence sentence verbatim.
- Last 5 DECISIONS.md headings.
- Pre-action gate list (Gate -1 → Gate 4).
- Available skills.

This is the deterministic answer to "the assistant forgets what we
agreed last session." Output verified via direct invocation.

#### `hooks/pre_commit_gate.py` (new) — block bad commits

Fires on PreToolUse when the assistant runs `git commit` or `git
push`. Reads the staged file list:

- If `plot/viewer/` changed → run `npx tsc --noEmit` + `npx vitest run`.
- If `plot/plot_mcp/` changed → run `uv run pytest`.

Failures return `permissionDecision: deny` with the failure output,
so the assistant must fix and retry. No more "tests broke after
commit" surprises.

#### `agents/plot-verifier.md` (new) — Playwright sub-agent

A read-only browser verifier. Parent assistant invokes it after any
UI change in `viewer/`. Sub-agent navigates, screenshots,
DOM-probes, and returns one of three verdicts:

- **MATCHES SPEC** — with evidence (paths + probe data).
- **DIVERGES** — with the specific element / cursor / position that
  differs and the most likely cause.
- **CANNOT VERIFY** — environment broken; exact obstacle named.

Sole tools: Playwright MCP browser_* + Bash + Read. Cannot mutate
the canvas (mutations belong to the parent assistant).

#### `CLAUDE.md` updates

- New **Gate -1** (re-anchor to essence) added at the top of
  Pre-action gates. Gate 0-4 now follow.
- "Pairs with" list updated to read VISION → DOMAIN → SPEC →
  DECISIONS → ARCHITECTURE → CONCEPTS → CURSOR → PHILOSOPHY →
  ROADMAP, in that order, every session.
- Gate 3 rewritten to delegate to the `plot-verifier` sub-agent
  (with the manual fallback path retained for offline cases).

#### `plot/.claude-plugin/plugin.json` updates

- Registered `agents` and `hooks` paths.
- Version bump to **0.14.0** (minor bump because the assistant's
  effective behaviour changed — new gates, new procedures, new
  automation — without breaking any product API).

### Verification

- `tsc --noEmit`: clean.
- `vitest run`: 24/24 passing.
- `session_start.py`: produces VISION + last 5 DECISIONS as
  `additionalContext`, 600+ chars.
- `pre_commit_gate.py`: passes through non-gating commands; runs
  checks on `git commit`; returns `deny` with output on failure.
- Skills + agent: SKILL.md / agent.md frontmatter validates;
  triggers and tools listed explicitly.

### Why minor bump (0.13 → 0.14)

The product UX is unchanged. What changed is the assistant's
operating environment — the rules / tools / procedures by which
future Plot work happens. By the user's framing, this is the
"AI develops Plot reliably" milestone, which conceptually opens a
new release line. v0.14.x will iterate on this infrastructure as
real sessions surface gaps.

## [0.13.10] — 2026-05-10

### Fixed — Cursor flicker root cause: `[role="button"]` on `.react-flow__node`

After six rounds across v0.13.3 → v0.13.6 with every diagnosis
proven wrong by the user reporting the same flicker, **the actual
cause was finally identified via Playwright DOM probe**:

> React Flow v11 sets `role="button"` on the
> `.react-flow__node` element itself for accessibility. Tailwind
> preflight ships `[role="button"] { cursor: pointer }`, which
> matches that element directly and overrides RF's intended
> `cursor: grab` *before any descendant rule runs*.

The v0.13.6 reset's premise ("RF default is grab; remove our
overrides and grab will work") was correct in theory but Tailwind
preflight had been silently shadowing it the whole time. None of
the prior six rounds walked the actual DOM parent chain to find
this — they all theorised from CSS files instead.

#### Fix

`viewer/src/styles.css` — add a second cursor rule (the first one
from v0.13.6 still applies to descendants):

```css
.react-flow__node[role="button"] {
  cursor: grab;
}
.react-flow__node[role="button"].dragging {
  cursor: grabbing;
}
```

#### Verification

Playwright DOM probe sweep across the entire post-layout canvas
(50 px grid sample × 22 cols × 21 rows) returned only three
distinct cursors anywhere:

- `grab` — `.react-flow__pane` AND every node body (uniform).
- `auto` — SVG inside MiniMap (never user-interactive).
- `not-allowed` — disabled toolbar buttons.

Zero `pointer` on any node body. Zero cursor changes when crossing
between pane and node. The flicker is structurally impossible now.

#### Process change

- **First step on any cursor / hit-test bug = Playwright DOM probe**,
  not code reading.
- Tailwind preflight is a hidden source of cursor regressions —
  it interacts silently with vendor library accessibility attributes.

### Changed — Auto layout button moved from top-right toolbar to lower-left Controls panel

Per user direction (*"정렬은 그리고 왼쪽 아래에 핏하는거하고 같은
곳에 넣어도 되요. 오른쪽 상단에 둘 필요 없음."*) the v0.13.9 Auto
layout button moves from `<SketchToolbar>` (top-right) into the
React Flow `<Controls>` panel at lower-left, rendered as a
`<ControlButton>` below zoom / fit / lock.

Rationale: the user grouped auto-layout mentally with view-state
controls (zoom / fit) rather than mutation actions (undo / redo).
Lower-left is also where the user's eye already goes for
camera-related operations. Algorithm itself is unchanged from
D-2026-05-10-E.

#### Files

- `viewer/src/canvases/SketchCanvas.tsx` — adds `ControlButton` to
  the `<Controls>` panel; removes the auto-layout props from the
  `<SketchToolbar>` instantiation.
- `viewer/src/canvases/SketchToolbar.tsx` — reverts to its v0.13.8
  shape (no `canAutoLayout` / `onAutoLayout` props, no Auto layout
  button).
- `viewer/tests/SketchCanvas.regression.test.tsx` — the
  v0.13.9-inverted regression test still asserts "auto layout
  button exists" via `aria-label="Auto layout"`, which still
  matches because the button kept the same accessible name when
  it moved into Controls.

### Documentation

- `docs/SPEC.md` §Cursor states — explicitly mentions BOTH
  Tailwind preflight cancellation rules (descendants from v0.13.6
  + `.react-flow__node[role="button"]` from v0.13.10).
- `docs/SPEC.md` §Auto-layout — Trigger and undo section updated
  with the new lower-left location and rationale.
- `docs/CURSOR.md` — Tailwind cancellation section expanded to
  cover the `.react-flow__node` element itself (in addition to
  descendants); change-history entry for v0.13.10.
- `docs/DECISIONS.md` — D-2026-05-10-F new entry, Accepted, with
  the full diagnosis story and the implied process change ("probe
  the DOM first, theorise second").

## [0.13.9] — 2026-05-10

### Added — Auto-layout button (mindmap directional tree implementation)

Implements the spec shipped in v0.13.8. Single click on the new
"Auto layout" button on `<SketchToolbar>` runs the directional-tree
algorithm against the active canvas, repositions every non-anchor
node, and dispatches one `onDocChange` so `Cmd+Z` reverses the
layout in one step.

#### New files

- `viewer/src/canvases/sketch/autoLayout.ts` (297 LOC) — pure
  module, no React imports. Exports `computeAutoLayout(input):
  { positions: Map<id, {x, y}> }`. Implements:
  - BFS spanning tree from the anchor.
  - Per-child direction from the parent-side handle (R / L / T / B).
    Falls back to positional inference when the edge has null
    `sourceHandle` / `targetHandle`.
  - R / L children → vertical column on the parent's right / left.
  - T / B children → horizontal row above / below the parent.
  - Recursive: grandchildren follow the same rule using *their*
    incoming handle.
  - Reingold-Tilford-style subtree-extent tracking → no node
    footprint overlaps (verified by unit test on a mixed-depth
    grandchild case).
  - Determinism: ties broken by node id at every level.
  - Isolated nodes (not reachable from anchor) → vertical column
    in the anchor's lower-right empty quadrant, sorted by id.
  - Cycles handled by BFS spanning tree (no infinite loop;
    cycle-closing edges are not used for placement).
- `viewer/src/canvases/sketch/useAutoLayout.ts` (43 LOC) — thin
  React hook bridging `computeAutoLayout` to `onDocChange`. Reads
  `docRef.current` + `projectAnchor`, computes positions, builds
  the next `CanvasDoc` with updated `nodes[]`, fires `onDocChange`
  once.
- `viewer/tests/autoLayout.test.ts` — 11 new unit tests pinning:
  per-direction grouping (R children stay right, T children above,
  …), strict no-migration-downward when right is crowded, recursion
  into grandchildren in their own direction, no overlap on a mixed
  R + grandchildren case, determinism across runs, cycle handling,
  isolated nodes, handle-direction inference fallback, and helper
  contracts.

#### Wired changes

- `viewer/src/canvases/SketchToolbar.tsx` — new `canAutoLayout`
  + `onAutoLayout` props; new `IconBtn` rendered between Redo and
  end of toolbar (glyph: `⊞`).
- `viewer/src/canvases/SketchCanvas.tsx` — imports `useAutoLayout`,
  calls it, passes the result to `<SketchToolbar>`. Six lines of
  glue; no new responsibility (the algorithm and the React bridge
  both live in `sketch/`). LOC 360 → 366.
- `viewer/tests/SketchCanvas.regression.test.tsx` — the
  D-2026-05-04-D regression test (`'toolbar does not render an
  Auto layout button'`) was updated to assert the **opposite** per
  D-2026-05-10-E: button MUST render and is enabled when the
  canvas has an anchor + at least one non-anchor node.

#### What stayed the same

- The anchor is never moved by auto-layout.
- Edges keep their `sourceHandle` / `targetHandle` after layout.
- No animation, no preview, no confirmation dialog — single click
  ⇒ instant re-layout per spec.

## [0.13.8] — 2026-05-10

### Spec — Auto-layout restored as a mindmap-style directional tree

D-2026-05-04-D (auto-layout removed) was based on a misread of the
user's v0.11.6 toolbar-cleanup request. The user wanted only
download / upload buttons removed; auto-layout was meant to stay.
The 2026-05-10 Foundation re-verification surfaced this — direct
user quote: *"내가 없애라는건 다운로드 업로드 이런거였는데.
오토레이아웃만 남기라는거였는데."*

This release ships the **spec** for the corrected behaviour. The
implementation lands in v0.13.9.

#### Algorithm shape (full table in `docs/SPEC.md` §Auto-layout)

- **Root:** the canvas anchor, kept fixed in place. Surrounding
  nodes arrange around the anchor's current position.
- **Spanning tree:** BFS from the anchor over `doc.edges`. Tree
  edges drive layout; cycle-closing edges are drawn but ignored.
- **Direction per child:** the **parent-side handle** of each tree
  edge picks the child's direction relative to its parent — `R`
  handle ⇒ child to the right, `T` handle ⇒ child above, etc.
- **R / L children:** stacked in a vertical column on the right /
  left of the parent.
- **T / B children:** placed in a horizontal row above / below the
  parent.
- **Recursive:** grandchildren follow the same rule, using *their*
  incoming-edge parent-side handle. Direction is absolute.
- **No overlap:** Reingold-Tilford-style subtree-extent tracking
  guarantees node footprints never collide. `padding` defaults to
  32 px; node footprint = its `data.width × data.height`.
- **Determinism:** node-id sort order breaks every tie. Same input
  ⇒ same output, every time.
- **Isolated nodes:** placed in the anchor's lower-right empty
  quadrant in a separate vertical column.

#### Trigger

- A single "Auto layout" button on `<SketchToolbar>` (next to
  undo / redo). Click ⇒ instant execution, no confirmation.
- Result is applied via `onDocChange`, so `Cmd / Ctrl + Z` reverses
  it in one step.

#### What auto-layout does NOT do

- Does not move the anchor.
- Does not change which nodes are connected (edges stay).
- Does not re-balance handles after layout.
- Does not animate or preview — single-click determinism is the
  product feature.

### Documentation

- `docs/SPEC.md` §Auto-layout — fully rewritten from "Removed" to
  the directional-tree spec above.
- `docs/DECISIONS.md`:
  - **D-2026-05-04-D** marked **Rejected** with a misattribution
    note explaining the 2026-05-04 / 2026-05-10 timeline.
  - **D-2026-05-10-E** new entry, Accepted: full algorithm rationale
    (why directional, why not radial, why not force-directed, why
    no library, why anchor stays fixed, why no animation).

### First Gate 0 application

This entire release exists because Gate 0 (added in v0.13.7) fired
on the user's *"네 일단 해봐요"* during the spec discussion. SPEC +
DECISIONS were updated in the same commit cycle as the version
bump, exactly as Gate 0 prescribes.

## [0.13.7] — 2026-05-10

### Added — Gate 0: user confirmation pins the spec immediately

`plot/CLAUDE.md` adds a new pre-action gate at position 0 (before the
existing Gate 1). Trigger: any user message containing one of a fixed
keyword set (`승인합니다 / 좋아요 / 네 좋아요 / 됐다 / 이제 됐다 /
맞아요`, English equivalents). When the trigger fires, the assistant
must, before any other tool call:

1. State the confirmed behaviour in one declarative sentence.
2. Verify or add the matching line to `docs/SPEC.md`.
3. Append a `D-YYYY-MM-DD-X` entry to `docs/DECISIONS.md` with
   `Approval: Accepted by user, YYYY-MM-DD`.
4. Stage SPEC + DECISIONS changes into the current commit cycle (or
   a docs-only follow-up if the implementing commit already shipped).

Banned shortcuts: deferring to "next session", assuming the SPEC was
already updated without verifying the diff, batching multiple
confirmations into one update, treating an unclear confirmation as
implicit (must ask the user).

This is a structural fix for the "work doesn't accumulate across
sessions" problem the user has flagged repeatedly. Without it, each
session re-asks questions the previous session already answered.
The v0.13.3 → v0.13.6 cursor saga is the canonical motivating
example — six rounds of cursor work because confirmed behaviour
never made it into the spec until v0.13.6 reset.

Authored as the first application of Gate 0 itself (user said *"네
좋아요"* on 2026-05-10 in the same conversation that drafted the
gate). See [D-2026-05-10-D](./docs/DECISIONS.md).

## [0.13.6] — 2026-05-10

### Changed — Reset to React Flow vendor cursor / handle defaults

Six rounds of cursor / handle interventions across v0.13.3 → v0.13.5
shipped overrides on top of overrides. Each round fixed one
localised symptom and revealed or introduced another. After the
user's *"정리한게 이상하지 않아요?"* / *"RF 디폴트로 일단 가세요.
거기서부터 다시 시작하죠. 코드 정리 제대로 하구요."* feedback,
v0.13.6 removes the entire override stack and restarts from the
React Flow vendor baseline.

The structural reasoning (D-2026-05-10-C):

- **One known state** to reason from. Vendor CSS in
  `node_modules/reactflow/dist/style.css` is now the single source
  of truth — no mental model lives in our `styles.css`.
- **No flicker by construction.** RF baseline puts `cursor: grab`
  on both `.react-flow__pane` and `.react-flow__node` — the cursor
  literally cannot change when the mouse crosses the boundary, so
  the "arrow ↔ pointer flicker" the user kept reporting is gone
  not because we patched it but because the conditions for it no
  longer exist.
- **The RF mental model is uniform:** anything draggable shows
  `grab`; active drag shows `grabbing`; drawing a connection shows
  `crosshair`; resizing shows the directional resize cursor. This
  is the standard React Flow contract that ships in every other
  React Flow product.

#### Two changes that did not need rolling back

- **Pan re-enable** (`SketchCanvas.tsx`: `panOnDrag={false}` →
  `panOnDrag`) shipped earlier in this release per D-2026-05-10-A
  and matches RF default. Stays.
- **Border-replaces-outline** on the inner node decoration (v0.13.5,
  D-2026-05-08-G) is about visual extent matching the click target
  — clicks on the visible decoration must select the node, not
  pass through to the pane. Independent of cursor, stays.

### Removed — The full v0.13.3 → v0.13.5 cursor / handle override stack

`viewer/src/styles.css` — removed:

- `.react-flow__node { cursor: pointer }` (was D-2026-05-08-C —
  unified node cursor). RF default `grab` restored.
- `.react-flow__node.dragging { cursor: grabbing }` (was redundant
  with RF default).
- `.react-flow__pane / .react-flow__viewport / .react-flow__renderer { cursor: default !important }` (was v0.13.4 — already removed earlier in this release per D-2026-05-10-A).
- `.react-flow__handle { width 10px / height 10px / 1.5px slate-400 border / white background / opacity 0 / cursor: pointer !important }` (was D-2026-05-08-F + earlier). RF default 6×6 dark-fill always-visible dot restored.
- `.react-flow__node.selected .react-flow__handle { opacity 1 / indigo border + bg }` (was D-2026-05-08-F — handles-on-select). Handles now always visible per RF default.
- `.react-flow__handle.connecting / .connectingfrom { cursor: crosshair !important / opacity 1 / indigo border }` (was D-2026-05-08-C). RF's native `.connectionindicator` selector covers crosshair-while-connecting.

`viewer/src/edit/EditableText.tsx` — removed:

- `cursor-pointer` Tailwind class on the display span (was
  D-2026-05-08-E — label cursor unification). The label inherits
  from the node, which under RF default is `grab`.

`viewer/src/canvases/SketchNode.tsx` — simplified the v0.13.5 border
comment block from a six-line cursor-flicker rationale to a single
sentence about hit-box matching the visual extent (the cursor part
of the rationale was disproven by D-2026-05-10-C anyway).

### Added — One single retained CSS rule (Tailwind preflight cancellation)

After the reset, the user reported flicker still present on node
hover. Investigation found the source: **Tailwind preflight** ships
`button, [role="button"] { cursor: pointer }`, which inside our
nodes matches:

- The fold `<button>` on container nodes.
- The EditableText label span (has `role="button"` for keyboard
  accessibility — needed for screen readers).

These elements flipped the cursor from RF's `grab` to Tailwind's
`pointer` — re-introducing the very flicker the reset was meant to
kill, with no override of ours involved.

The fix is one CSS rule that cancels the Tailwind preflight effect
inside `.react-flow__node`, restoring RF's inheritance chain:

```css
.react-flow__node *:not(.react-flow__handle):not(.react-flow__resize-control) {
  cursor: inherit;
}
```

The :not() exclusions preserve RF's own semantic cursors on
connection handles (crosshair) and resize controls (directional
resize). This is the **only** cursor rule in `styles.css` after the
reset; it does not change RF, only stops Tailwind from contradicting
it. (D-2026-05-10-C.)

### Documentation

`docs/SPEC.md`:

- §Pan and select rewritten — the pan-off paragraph from v0.13.4 is
  gone; the new prose codifies "drag empty pane = pan; Shift+drag =
  selection box; node drag = node move".
- §Hover behaviour rewritten — was "handles only when selected,
  cursor pointer everywhere"; now "RF defaults, handles always
  visible".
- §Cursor states rewritten — table mirrors the React Flow vendor
  CSS exactly + the one Tailwind cancellation rule so future
  sessions can verify against the spec without re-reading vendor
  CSS. Includes the "RF mental model in one sentence" summary.

`docs/CURSOR.md` — **new file**, dedicated cursor SSOT:

- TL;DR table for the five cursor regions a user actually sees.
- Full table with selectors mirroring React Flow vendor CSS.
- Detailed write-up of the Tailwind preflight cancellation rule:
  what it is, why it's not "just another override", why we don't
  fix the problem upstream by removing `role="button"` from the
  label.
- Anti-patterns derived from v0.13.3 → v0.13.5 mistakes.
- "How to deviate" workflow for any future cursor change — must
  open a `D-YYYY-MM-DD-X` decision id, get user approval, add a
  CSS comment naming the id, update SPEC + CURSOR + add a
  regression test.
- DevTools probe script for verifying cursor state in the browser.

`plot/CLAUDE.md`:

- "Pairs with" list — `docs/CURSOR.md` added.
- Anti-patterns table updated: replaced the four cursor-related
  rows with one general rule about not adding cursor / handle
  overrides without a decision id.

`docs/DECISIONS.md` — three new entries:

- **D-2026-05-10-A** Pan re-enable (Accepted, shipped earlier in
  this release).
- **D-2026-05-10-B** Force-pointer on every node descendant
  (Rejected, rolled back in same session before commit).
- **D-2026-05-10-C** Reset to RF defaults + Tailwind preflight
  cancellation (Accepted, this release).

## [0.13.5] — 2026-05-08

### Fixed — **Cursor flicker root cause: outline paints outside hit-box**

After three previous rounds of cursor fixes (v0.13.3 → v0.13.4) the
user still reported `default ↔ pointer` flicker on a slow mouse-move
across one node ("커서 검지 커서 검지 이렇게 되요"). DOM probing
returned a single cursor (`pointer`) for every descendant of the
node, which ruled out competing cursor declarations and left only
one possible cause: the cursor was crossing the **node's actual
hit-box boundary** while the user thought they were still inside
the visual node.

The decoration `outline outline-2 outline-slate-600 outline-offset-2
ring-1 ring-slate-300` on the synthetic project anchor paints the
visual ring **8–10 px outside** the `.react-flow__node` bounding box.
Pixels in that ring zone — though they look like part of the node —
hit-test to `.react-flow__pane` (cursor: default). Slow movement
across the ring zone flicked the cursor `pointer ↔ default`.

Fix: replace `outline` (paints outside the box, excluded from
hit-testing) with `border` (part of the border-box, included in
hit-testing). After the change the hit-box and the visual box are
pixel-identical (verified via `getBoundingClientRect`); the cursor
is `pointer` everywhere on the node region with no flicker zone.

Per-state class change in `viewer/src/canvases/SketchNode.tsx`:

| State | Before | After |
|---|---|---|
| Selected | `outline outline-2 outline-indigo-500` | `border-2 border-indigo-500` |
| Anchor (idle) | `outline outline-2 outline-slate-600 outline-offset-2 ring-1 ring-slate-300` | `border-2 border-slate-600` |
| Regular (idle) | `outline outline-1 outline-slate-300` | `border border-slate-300` |

The anchor loses its 8 px breathing-room visual + thin slate-300
inner ring (those were the source of the flicker zone). The new
2 px slate-600 border keeps the anchor visually distinct from the
1 px slate-300 of regular nodes and the 2 px indigo-500 of selected
nodes. If the original "double ring" look matters, an `inset
box-shadow` is the right tool for a follow-up — it paints inside
the box and doesn't touch hit-testing.

[D-2026-05-08-G](./docs/DECISIONS.md) records the diagnosis and the
general rule that follows: **node decoration must coincide with the
hit-box; never use `outline` / `outline-offset` / `ring` /
`shadow-[…]` rules that paint outside the box for any pointer-
significant element.**

## [0.13.4] — 2026-05-08

### Fixed — **Cursor / handle visual flicker on node hover (final)**

The user reported "커서였다가 검지였다가 큰 검지였다가 작은
검지였다가 등등" — the cursor itself appearing to vary in size /
shape as it moved across a node, even after the v0.13.3 cursor
unification. DOM probing showed the cursor was never actually
varying; the perceived variation was the four handle dots
pulsing in opacity (0 → 0.55 on node-hover) and the one near
the pointer scaling to 1.25× on direct handle-hover. The dots
near the pointer were reading as "cursor".

- **Handles now appear only when the node is selected.** Hovering
  a node no longer reveals or animates anything. Click to select
  the node → handles appear at full opacity with indigo styling
  → drag from a handle to draw an edge. One extra click compared
  to the prior hover-to-reveal flow, but the canvas reads still
  on hover.
- **All transition / scale animations on handles removed** —
  they were the actual flicker source.
- SPEC §Hover behaviour rewritten: three visibility states (idle
  / hover / direct-handle-hover) collapse to two (hidden /
  selected). DECISIONS [D-2026-05-08-F](./docs/DECISIONS.md)
  records the user direction and the diagnosis trail.

## [0.13.3] — 2026-05-08

### Changed — **SketchCanvas refactor: test baseline + extraction in progress**

The viewer's central component (`canvases/SketchCanvas.tsx`, 1476
LOC, 16 concerns in one closure) is being split down to a thin React
Flow shell (target ≈ 150 LOC) per
[D-2026-05-08-A](./docs/DECISIONS.md). Approach: Candidate A
(modified) — surgical responsibility split with pure transforms
(nodes / edges / overlap math) extracted as `.ts` modules, hooks for
the rest, React Flow prop wiring stays in the shell.

This release ships the **test baseline** that gates the extraction:

- **JSDOM `localStorage` mock added** to `viewer/tests/setup.ts`.
  JSDOM previously shipped a placeholder without `getItem` /
  `setItem` methods, which crashed any test that mounted a component
  calling `window.localStorage.getItem(...)` (notably `SketchInspector`'s
  width-toggle persistence). The previously-broken
  `SketchCanvas.smoke.test.tsx` is green again.
- **`viewer/tests/useSketchHistory.test.ts` deleted.** It imported a
  hook that was never implemented (orphan from a planned-but-skipped
  feature). The actual undo/redo lives in
  `viewer/src/canvases/useProjectHistory.ts`; if dedicated coverage is
  wanted there, that's a new feature task.
- **Regression test set added** at
  `viewer/tests/SketchCanvas.regression.test.tsx` — four pinning
  assertions for invariants the v0.13.2 bugs flipped: 0 auto-edges
  on Foundation when `doc.edges` is empty (D-2026-05-04-A);
  anchor renders 4 React Flow handles (D-2026-05-04-B); no "Auto
  layout" button in the toolbar (D-2026-05-04-D); Inspector aside
  appears after a node click. All four match real-browser state
  (verified at the v0.13.3 baseline). Test suite now: 4 files /
  13 tests, all passing.
- **Step 1 + 2 of the SketchCanvas split** — extracted the
  value-flow toggle state (`canvases/sketch/useValueFlow.ts`) and
  the orphan actor_ref detection memo
  (`canvases/sketch/useOrphanActorRefs.ts`). New folder:
  `viewer/src/canvases/sketch/`. SketchCanvas.tsx: 1476 → 1466 LOC
  (−10).
- **Step 3 — collapsed-tree state**
  (`canvases/sketch/useCollapsedTree.ts`). One hook now owns
  `childIdsByParent`, `nodeById`, `nearestCollapsedAncestor`,
  `toggleCollapsed` (reads `docRef` for mid-drag freshness per the
  coupling map), and `subtreeSize`. The lookup map is also used by
  drag/drop and keyboard, so the hook is the single source. SC:
  1466 → 1409 LOC (−57).
- **Step 4 — Inspector routing**
  (`canvases/sketch/useInspectorRouting.ts`) plus
  `canvases/sketch/constants.ts` for the shared
  `PROJECT_ANCHOR_ID`. The hook owns `inspectorNodeId` state, the
  `selectNodeId` jump-and-fit effect, and the three React Flow
  callbacks (`onNodeClick`, `onNodeDoubleClick`, `onPaneClick`),
  including the anchor read-only guard. SC: 1409 → 1394 LOC
  (−15). Browser verified: clicking Mission opens Inspector;
  clicking the anchor does not.
- **Step 5 — Doc-to-node transform**
  (`canvases/sketch/useNodesMemo.ts`). One hook owns the
  parents-before-children sort, the hide rules
  (collapsed-ancestor / rule&content / service-detail
  service-root), the orphan-actor_ref visual override, the
  master-derived ref label sync, the service.target_side body
  tint, drill routing, and synthetic project anchor injection.
  Plan called for a separate pure `nodeTransform.ts` + thin
  wrapper, but the transform reads ten-plus callbacks; a "pure"
  form would be cosmetic. Documented as
  [D-2026-05-08-B](./docs/DECISIONS.md). SPEC §Anchor and SPEC
  §Rendering order updated with the implementation invariants
  this hook preserves. SC: 1394 → 1246 LOC (−148). Browser
  verified: Foundation renders 4 nodes (anchor + Mission +
  CoreValue + Identity), 0 edges, 3 ⚠ badges intact.
- **Step 6 — Doc-to-edge transform**
  (`canvases/sketch/edgeTransform.ts` pure +
  `canvases/sketch/useEdgesMemo.ts` thin wrapper). The pure
  module survives here because edges have far fewer callback
  dependencies than nodes — only data + collapse hide rule +
  value-flow recolour. Genuinely unit-testable in isolation if
  someone later wants snapshot tests over thousands of edge
  shapes. SC: 1246 → 1212 LOC (−34). Browser sanity (Foundation,
  banas-v013): 0 edges (regression test still pinned), 0
  console errors. Recolour path not exercised against this
  fixture (no user-drawn edges); the pure code is byte-equal to
  the prior inline so the recolour invariant is preserved by
  construction.
- **Step 7 — Anchor mutation branch**
  (`canvases/sketch/applyAnchorChange.ts`, pure helper).
  `handleNodesChange` stays in the shell (React Flow's
  `onNodesChange` prop must dispatch atomically per the coupling
  map) but the anchor-vs-regular-node split now reads as one
  helper call, surfacing SPEC §Anchor "Mutation routing". SC:
  1212 → 1199 LOC (−13). Browser sanity: anchor present, 4
  handles, 0 console errors. Mid-drag persistence path cannot be
  exercised through Playwright synthetic clicks (they bypass
  d3-zoom's drag pipeline); the helper is a byte-equal
  extraction of the prior inline so the persistence invariant is
  preserved by construction.

- **Step 8 — Three context menus**
  (`canvases/sketch/useContextMenus.ts`). One hook owns
  `menu` state, `openPaneMenu`, `openNodeMenu`, `openEdgeMenu`,
  `closeMenu`. `MenuState` type lives in the hook; `DEFAULT_WIDTH`
  / `DEFAULT_HEIGHT` / `DEFAULT_COLOR` lifted to
  `sketch/constants.ts` so the future `useNodeCreation` (Step 10)
  can reuse them without circular imports. Color palette also
  lifted to a const inside the hook (was a per-call inline
  array). SC: 1199 → 1073 LOC (−126). Browser verified: right-click
  on a Mission node renders the Duplicate / Copy / Color × 7 /
  Delete menu items.
- **Step 14 — Shell consolidation; split complete.** Three
  more reductions land:
  - `addCompositionChild(parentId, kind)` factored into
    `useNodeCreation`. The Inspector's `onAddChild` (60 lines
    of inline default-everything DocNode boilerplate) becomes
    a one-line callback.
  - `SketchInspectorBindings.tsx` (new) wraps the SketchInspector
    with all the SC-side glue (which node is selected, repick /
    delete / patch / add-child routing). SC's render block goes
    from ~100 lines of inline JSX to one
    `<SketchInspectorBindings ... />` element.
  - `nodeChanges.ts` (new pure module) exposes
    `collectNodeChanges(changes)` and
    `applyNodeChangesToDoc(doc, posById, dimById)`.
    `handleNodesChange` shrinks to 10 lines while still living
    in the shell (React Flow's `onNodesChange` requires
    atomic dispatch per the coupling map).
  Final SC LOC: **1476 → 360 (75.6 % reduction).** 16 hook
  modules + 5 pure helpers under `viewer/src/canvases/sketch/`
  each carry a single responsibility. The 360-LOC floor
  (instead of the plan's 150 design target) is recorded in
  [D-2026-05-08-D](./docs/DECISIONS.md): pushing further would
  reintroduce the controller-hook god scope that
  D-2026-05-08-A explicitly rejected.

- **Step 13 — Small flow handlers**
  (`canvases/sketch/useFlowHandlers.ts`). One hook bundles
  `handleConnect` (new edge), `handleEdgesChange` (no-op stub
  React Flow still requires), `handleNodesDelete` (with anchor
  + legacy project-kind protection per SPEC §Anchor),
  `handleEdgesDelete`, `handlePaneDoubleClick` (add node where
  the user double-clicked, only on the React Flow pane), and
  `handleSelectionChange` (selection ref sync). `handleNodesChange`
  stays in the SC shell — its mid-drag `docRef.current` read is
  load-bearing per the coupling map and would regress if the
  React Flow event were dispatched through a longer call chain.
  Cleanup: SC drops six unused reactflow type imports
  (`Connection`, `Edge`, `EdgeChange`, `OnSelectionChangeParams`,
  the `SketchEdge` type, the constants block), and the
  `applyEdgeChanges` / `applyNodeChanges` re-export at the
  bottom of the file (dead code — nothing imports them from SC).
  **SC LOC: 546 → 472 (−74) — under the 500-LOC threshold for
  the first time since the file was born.** Gate 2 satisfied;
  one-step-from-final-shell remains.
- **Step 12 — Modal / picker renders**
  (`canvases/sketch/SketchModals.tsx`). One component renders the
  four conditional modal blocks: SketchBodyModal (long-form node
  body editor), SketchEdgeModal (edge label + dashed + value-form),
  FoundationRefPicker (mission/value/identity ref picker), and
  ActorRefPicker (actor ref picker, both create + rewire flows).
  Inspector stays in the SC shell. Side-cleanup: extracted a
  `parentAbsolute()` helper that the two picker callbacks both
  used to walk the parent chain (was duplicated inline). SC drops
  six imports (ActorRefPicker, FoundationRefPicker family,
  SketchBodyModal, SketchEdgeModal, NodePreset). SC: 673 → 546
  LOC (−127). One step under the 500-LOC threshold mark.
- **Step 11 — Drag-and-drop + overlap nudging**
  (`canvases/sketch/useDragAndDrop.ts` hook +
  `canvases/sketch/overlapNudge.ts` pure module). The pure
  module owns `containerAtFlowPoint` and `findFreeSpot` — both
  pure functions of (nodes, point) / (rect, siblings); React-
  free, unit-testable. The hook owns the drop orchestration:
  preset parse, hit-test, hierarchy edge creation,
  reference-kind picker dispatch, and the two `pendingActorRef`
  / `pendingFoundationRef` states. `PendingActorRef` and
  `PendingFoundationRef` types lifted to `sketch/types.ts` so
  the modal render block (Step 12 next) can read them. SPEC
  §Drag-and-drop section added with the canonical hit-test /
  nudge / hierarchy-edge / picker rules. SC: 857 → 673 LOC
  (−184). Browser sanity (Foundation, banas-v013): nodes still
  render, no console errors. Real drag-from-stencil cannot be
  exercised via Playwright (synthetic dataTransfer doesn't
  round-trip the way the browser's native drag does); the hook
  body is byte-equal to the prior inline so the drop pipeline
  is preserved by construction.
- **Step 10 — Node creation helpers**
  (`canvases/sketch/useNodeCreation.ts`).  `addNodeAt` (top-level)
  and `addNestedNodeAt` (drop onto an existing container, with
  decomposition edge for actor / service kinds) move out of the
  shell. Side-extraction: `NodePreset` interface lifted to
  `canvases/sketch/types.ts` so multiple sketch hooks (and
  `SketchStencil`) can import without circular deps. The
  default-everything DocNode boilerplate is duplicated across
  `addNodeAt` and `addNestedNodeAt` — intentionally preserved
  byte-equally during this extraction; a `makeBlankNode()`
  follow-up is worth doing once Step 11 is also out of the way.
  Cleanup: SC drops `NodeKind` and `DEFAULT_COLOR` imports (only
  the new hook needs them). SC: 1030 → 857 LOC (−173). Browser
  sanity: Foundation renders (4 nodes incl. anchor).
- **Step 9 — Window keyboard shortcuts**
  (`canvases/sketch/useKeyboardShortcuts.ts`). One hook owns the
  `window.addEventListener("keydown")` effect and the canonical
  combo set (Cmd+Z / Cmd+Shift+Z / Cmd+Y / Cmd+C / Cmd+V /
  Cmd+D / Cmd+A). The editable-target guard
  (`INPUT` / `TEXTAREA` / `contentEditable`) is preserved
  byte-equally — typing in Inspector text fields still does NOT
  trigger canvas undo. SPEC §Keyboard shortcuts added with the
  full combo table and the load-bearing guard note. SC: 1073 →
  1030 LOC (−43). Browser verified: synthetic `keydown` reaches
  the listener and `preventDefault` fires for Cmd+A; the
  imperative `setNodes` selection path doesn't survive a
  Playwright synthetic dispatch (React Flow re-renders from our
  `useNodesMemo` and overwrites the imperative state) — that's a
  pre-existing limitation of synthetic testing, not a regression
  of this refactor.

### Changed — **Canvas pan-on-drag removed; node cursor invariant tightened**

Per [D-2026-05-08-E](./docs/DECISIONS.md):

- **`panOnDrag={false}` on `<ReactFlow>`.** Grabbing an empty
  canvas region and dragging no longer pans the viewport. Use the
  zoom controls (bottom-left) or the minimap (bottom-right) to
  move the view. Users were accidentally panning while reaching
  for nodes; removing the affordance lets the canvas read as a
  fixed page.
- **Pane / viewport cursor forced to `default`** with a CSS
  override on `.react-flow__pane` / `.react-flow__viewport` /
  `.react-flow__renderer`. React Flow's baseline CSS keeps the
  `cursor: grab` rule on those elements even after `panOnDrag` is
  disabled — that reintroduced the cursor flicker the user had
  reported (`grab` over empty canvas ↔ `pointer` over a node).
  After the override the canvas region reads "default" (page) and
  only the node region reads "pointer" (clickable).
- **Cursor on a node is now `pointer` everywhere, in every state**
  (idle, hover, mousedown). The `.react-flow__node:active {
  cursor: grabbing }` rule is gone — clicking a node no longer
  flashes the grabbing cursor, only an actual drag does (via
  `.react-flow__node.dragging`).
- **`EditableText` display span uses `cursor-pointer`**, not
  `cursor-text`. The display span is `role="button"` (click to
  edit), so the I-beam cursor was misleading and was the
  remaining flicker source the v0.13.3 cursor fix didn't catch.

SPEC §Pan and select (new) and §Hover behaviour (clarified)
codify the cursor invariant.

### Fixed — **Cursor flicker on node hover**

`.react-flow__handle` now uses `cursor: pointer` (matching the node
body); `cursor: crosshair` is restored only while a connection is
actively being drawn (`.connecting` / `.connectingfrom`). Previously
React Flow's default crosshair on handles fought our pointer rule on
the node body — moving the mouse across a node would flip the cursor
back and forth (described by the user as "보자기 / 가위 계속 바뀌는",
paper / scissors swapping). The v0.13.2 hover tone-down made handles
visually quieter but left the cursor invariant ambiguous; this fix
addresses the root cause. (D-2026-05-08-C, SPEC §Hover behaviour
updated.)

The extraction commits land incrementally over subsequent versions
under this same v0.13.x line; each commit is a single concern moved
out, browser-verified per the plan's matrix.

## [0.13.2] — 2026-05-05

### Added — **Foundation SPEC + decision log**
- ``plot/docs/SPEC.md`` — first canonical behaviour spec (Foundation
  canvas only). Codifies anchor / edges / auto-layout / ⚠ badge /
  hover / Inspector / viewport behaviour with explicit user approval.
- ``plot/docs/DECISIONS.md`` — append-only UX / behaviour decision
  log. Today's seven decisions are logged with status (accepted /
  rejected / pending). Future UI changes must add an entry here
  before / alongside the code change.
- Reason: prior to this release, behavioural decisions lived only in
  code comments (not agreed) or in session memory (didn't survive).
  Cross-session work didn't accumulate. The two new files are the
  fix.

### Changed — **Foundation canvas: smaller, agreed-upon polish**
- **Anchor visually distinct from Service circles.** The project
  anchor now wears a slate-600 outline + offset + slate-300 inner
  ring so it reads as "this is the project itself, not a peer", even
  when it appears on Actors / Services where same-coloured Service
  circles also exist. (Decision D-2026-05-04-C.)
- **⚠ MD-warning badge contrast.** Was amber-100 fill on amber-100 /
  amber-50 cards — nearly invisible. Now white fill, amber-700
  glyph, amber-500 ring + shadow; legible on every Foundation card
  colour. (Decision D-2026-05-04-F.)
- **Quieter hover.** Connection handles stay hidden at rest; fade to
  opacity 0.55 while the cursor is on the node body; only become
  fully opaque + scaled on direct handle hover. The previous "all
  four handles pop the moment the cursor approaches" felt noisy.
  (Decision D-2026-05-04-E.)
- **Defensive viewport sizing.** Outermost shell uses ``h-screen
  min-h-screen``; ``html, body, #root`` add ``min-height: 100dvh``
  fallback. Belt-and-braces against cascading quirks so the canvas
  always reaches the bottom of the window. (Decision D-2026-05-04-G,
  approval pending user confirmation.)

### Removed — **Auto-layout button + auto-edges (rolled back same day)**
- **"Auto layout" button gone** from the canvas toolbar and the pane
  context menu. ``handleAutoLayout`` callback and ``autoLayout`` /
  ``radialLayout`` imports dropped from ``SketchCanvas``. Layout is
  fully manual — node positions encode user intent and shouldn't be
  silently rewritten. (Decision D-2026-05-04-D.)
- **Synthetic anchor → child auto-edges removed** before reaching a
  release. Briefly added during this session as dashed slate-400
  lines connecting the anchor to Mission / CoreValue / Identity, but
  the user rejected the approach: edges that the user can't edit or
  delete break the "every line on the canvas is mine to control"
  expectation. All edges on Foundation are user-drawn. (Decision
  D-2026-05-04-A.)
- **Anchor handle suppression rolled back.** Briefly hid the anchor's
  four React Flow handles on the assumption that "synthetic =
  read-only" (a stale code comment, not an agreed decision). Handles
  restored — the user may draw edges from / to the anchor like any
  other node. (Decision D-2026-05-04-B.)

## [0.13.1] — 2026-05-04

### Fixed — **Radial auto-layout under v0.13's derived project anchor**
- ``radialLayout`` was still looking for the project node inside
  ``doc.nodes`` (legacy v0.12 path). v0.13 moved the anchor out to
  ``ProjectDoc.anchors``; the lookup returned nothing on Foundation /
  Actors and silently fell back to dagre LR, collapsing the canvas
  into a horizontal row.
- New ``options.anchorOverride`` parameter; SketchCanvas passes the
  derived anchor in. Legacy in-doc.nodes lookup preserved as a
  fallback.

### Fixed — **Peer overlap on radial rings**
- The "minimum angular separation" between adjacent peers was a fixed
  15°. With node widths > 120 px on a 220 px ring, two peers could
  end up visibly overlapping. Now derives the gap from
  ``(maxNodeDim + 24px padding) / radius`` so it scales with actual
  footprint. Caps at π/2.
- If the spread chain wraps past 2π (user's nodes were so clustered
  that respecting angles couldn't yield separation), fall back to
  even distribution around the full circle.

## [0.13.0] — 2026-05-04

A foundational rework of how a project's data is laid out on disk —
**graph in JSON, typed content in Markdown, schema in its own folder**.
Foundation canvas is the v1 surface; Actors / Services / Service
Detail keep the v0.12 layout for now and join the new model in v0.14+.

### BREAKING — file layout

The first time Plot reads a v0.12 project, it migrates Foundation in
place:

  .plot/{project}/
    project.json                 ← + new ``anchors`` field
    schema/                      ← ✨ NEW (auto-generated, git-tracked)
      _meta.json                 schema_version=1, plot_version, kinds
      project.json               JSON Schema for project node entry
      mission.json               + core_value.json, identity.json
      mission.md.template        + core_value.md.template, identity.md.template
    foundation/
      canvas.json                ← graph only (no project node, no typed text)
      mission-mission.md         ← ✨ per-node typed text + free prose
      core_value-{slug}.md
      identity-voice.md
    actors/canvas.json           ← v0.12 layout, project node evicted
    services/                    ← v0.12 layout, project node evicted

### Phase 0 — Project SSOT
- New ``ProjectDoc.anchors: dict[CanvasKind, AnchorPlacement]``. Each
  AnchorPlacement carries x/y/w/h/color/shape for the project anchor
  on a given canvas. Default-seeded; old projects fall back cleanly.
- Per-canvas seeds (foundation/actors/services) no longer create a
  ``project`` kind node — the anchor is no longer canvas data.
- Eviction migrator on canvas read: legacy ``project`` node →
  ``ProjectDoc.anchors[canvas]`` + node removed + orphan edges stripped.
- Frontend: SketchCanvas injects a synthetic project anchor (id
  ``__project_anchor__``) derived from ProjectDoc.anchors. Drag /
  resize routes through a new ``PATCH /api/projects/{id}/anchors/{canvas}``;
  the canvas .json never carries a project node again.
- ``ProjectDoc.version`` bumped 2 → 3.

### Phase 1 — Pydantic discriminated union (Foundation)
- ``BaseNodeFields`` carries the 13 graph fields. Per-kind subclasses
  ``ProjectNode`` / ``MissionNode`` / ``CoreValueNode`` /
  ``IdentityNode`` declare a ``Literal`` discriminator on ``kind`` and
  their own typed-text fields. ``FoundationNode = Annotated[Union[...],
  Field(discriminator="kind")]``.
- The legacy god ``SketchNode`` stays in place — Foundation just gains
  type-safer per-kind constructors.

### Phase 2 — Schema auto-export
- New module ``schema_export.py``. ``create_project`` writes
  ``.plot/{project}/schema/`` with one JSON Schema per kind (graph
  fields only) plus per-kind MD templates. Idempotent.

### Phase 3 — Markdown template I/O
- New module ``md_template.py``. ``parse_md_template`` is **lenient**
  (missing sections → empty + warning, unknown headings preserved in
  warnings, case-insensitive headings, HTML comments stripped, free
  prose below the ``---`` rule preserved verbatim).
  ``render_md_template`` is **strict** (canonical section order per
  kind, free prose round-trips).
- 18 round-trip + lenient + strict tests.

### Phase 6 — Migration v0.12 → v0.13 (Foundation)
- ``_evict_typed_text_to_md`` runs on first foundation read: per-kind
  typed text in canvas.json → ``foundation/{kind}-{slug}.md`` template
  (preserving any existing free prose), then stripped from JSON.
- ``_merge_md_typed_text_into_nodes`` re-attaches typed text from the
  canonical MD path into the in-memory node so Inspector / API
  continue to see populated fields.
- ``_split_foundation_typed_text_to_md`` runs on every foundation
  write so Inspector edits land in MD, not back in canvas.json.

### Phase 4 — File watcher
- Watcher recognises ``foundation/*.md`` (any .md directly under
  ``foundation/``) as v0.13 per-node templates. External Obsidian /
  VS Code edits trigger ``project_changed`` with ``canvas_kind:
  "foundation"`` so any open viewer reloads.

### Phase 5 — TypeScript Foundation discriminated union
- ``BaseFoundationNode`` + ``MissionFoundationNode`` /
  ``CoreValueFoundationNode`` / ``IdentityFoundationNode`` /
  ``ProjectFoundationNode`` per-kind types.
  ``FoundationNode = ...`` discriminated on ``kind``. Ready for
  Foundation-aware code paths to narrow safely.

### Phase 7 — Resilience UX
- New helper ``collect_foundation_md_warnings`` runs alongside
  canvas read; ``canvas_get_endpoint`` injects per-node
  ``_md_warnings`` into the response without polluting the model.
- Frontend: ``SketchNode`` shows a yellow ⚠ badge when warnings
  present. Inspector displays the warning list with a hint pointing
  at the file the user should fix.

### Compatibility
- v0.12 projects auto-migrate on first read. Eviction is idempotent:
  re-running on v0.13 data is a no-op. The legacy v0.7
  ``{slug}/details.md`` per-node folders are left in place for
  backward compatibility but no longer used by Foundation reads;
  ``details_path`` may continue to point at them for the user's
  reference.
- 182 tests pass (164 prior + 18 new for md_template).

## [0.12.6] — 2026-05-03

Code-level audit cleared the v0.10/v0.11 residue still leaking into
the v0.12 Services surfaces.

### Changed — **`is_root` UI no longer applies to service**
- Inspector still surfaced a "Mark as Service Root" checkbox and a
  "Service Root" header for any parentless service. v0.12 made
  `service` a category leaf — there is no service-root concept any
  more. The toggle and the header branch now apply only to `actor`.
  The `is_root` field stays on the data model (still meaningful for
  actor); only the service UI path is removed.

### Changed — **Service Detail modal shows the parent category**
- The header used to read just "SERVICE DETAIL — Login". Inside the
  modal users had no way to see which category the service belonged
  to; drill context was lost. Header now reads
  "SERVICE DETAIL  {Category} › {Service}", with the category label
  derived from the service's `parent_id` lookup against the cached
  Services canvas.

### Added — **Soft warning on empty categories**
- A `category` with zero child services is structurally legal but
  semantically noise (categories exist to group services). Inspector
  now surfaces an amber hint inside `CategoryFields` when child
  count = 0, suggesting the user either drop a service in or delete
  the category. Not a hard validator — autosave-friendly.

### Changed — **Stale "sub-service" wording removed**
- Comments and JSDoc across `types.ts`, `SketchStencil.tsx`, and
  `SketchCanvas.tsx` still described the v0.10/v0.11 sub-service
  decomposition. Updated to v0.12 phrasing
  ("category → service leaf"; "service detail = modal").

### Changed — **Auto-layout button tooltip drops "(dagre LR)"**
- v0.12.4 made auto-layout dispatch by canvas (radial for
  Foundation/Actors, dagre for Services/Detail), so the literal
  "(dagre LR)" tooltip was a lie on half the canvases. Tooltip is
  now just "Auto layout".

## [0.12.5] — 2026-05-03

### Fixed — **Radial auto-layout preserves the user's angle**
- v0.12.4's radial placed peers around the project in `doc.nodes`
  declaration order (top → clockwise), so a node the user had
  dragged to the right could end up on the left after auto-layout.
  The placement felt arbitrary because it ignored where the user
  put things.
- New behaviour: each peer keeps its **current angle** from the
  project anchor; auto-layout only normalises distance (snap onto
  the same ring) and nudges any pair that would sit within 15° of
  each other so they don't visually overlap. If the user dragged
  Identity to the right, it stays on the right.

## [0.12.4] — 2026-05-03

Three corrections from continued usage.

### Changed — **Auto-layout dispatches by canvas shape**
- `dagre LR` lays a graph out as a left→right tree, which only fits
  the canvases that *are* trees (Services, Service Detail). On
  Foundation and Actors — both "project anchor at the centre, peers
  around it" — it collapsed everything into a single horizontal row
  and broke the radial mental model.
- New `radialLayout` keeps the `project` anchor where it sits and
  spreads the other connected nodes on a circle around it (top-down
  start, equal angular steps, ring sized to the largest peer node).
  `SketchCanvas.handleAutoLayout` dispatches by `canvas_kind` —
  Foundation / Actors radial; Services / Service Detail stay dagre.

### Changed — **Label alignment: category left, service centre**
- v0.12.2 left-aligned service titles to read them as "headers", but
  in v0.12 the actual *header* role belongs to `category` (the
  container). Service nodes are leaves and read better centred like
  every other kind. So the conditional flips: only `category` uses
  `justify-start`; everything else (including `service`) stays
  centred.

### Changed — **Collapse button: lose the circle, grow the arrow**
- The 32×32 white-circle-with-shadow control read as a UI chrome
  blob detached from the label. Replaced with a borderless inline
  arrow at `text-xl` (`▸` / `▾`) that hugs the label, hover
  darkens. Same hit area, much less visual noise.

## [0.12.3] — 2026-05-03

Docs only — sync `CONCEPTS.md` to v0.12 reality.

### Changed — **CONCEPTS.md**
- Canvas table: Services row now `project / category / service`;
  Service Detail row drops `service (sub via parent_id)` (sub-service
  was eliminated in v0.12) and is labelled "(modal, per-service)".
- `service` kind: the "Top-level service" / "Sub-service" sub-sections
  are merged into a single v0.12 service definition with one typed
  field block (`target_side`, `what`, `value_created`, `scope`,
  `trigger`, `how`, `outcome`, `do`, `dont`).
- Design principles: the validator floor for the Services canvas is
  rewritten — `service` must sit under a `category`, no nested
  categories. The v0.11.2 "≥ 1 Foundation anchor on the Services
  canvas" rule is removed (anchors now live inside the per-service
  modal, not on the top view).
- Stylistic phrasings updated from "Service Detail canvas" to
  "Service Detail modal" wherever the old surface was named.

## [0.12.2] — 2026-05-03

Visual polish on the v0.12 surfaces, driven by direct usage feedback.

### Changed — **Collapse button is a clear circle, not a tiny chevron**
- The fold/unfold control on container nodes (categories on the
  Services canvas, sub-actor parents on Actors) was a 24×24 square
  with no border that visually disappeared. Now 32×32, `rounded-full`,
  white background with a slate border and shadow. Same arrow glyph,
  much higher discoverability.

### Changed — **Service titles align left**
- Service node labels were centered like every other kind. With the
  v0.12 service-as-leaf model the label reads better as a header,
  so service nodes now `justify-start`. Other kinds still center.

### Fixed — **Service-detail modal hides the redundant root node**
- The modal's inner canvas seeded a copy of the service itself as a
  visible node, even though the modal header already names it
  ("SERVICE DETAIL — Login"). The modal now filters the root
  (matched by `doc.service_ref === node.id`) from both the nodes
  and edges memos, so refs and composition read against an empty
  background.

## [0.12.1] — 2026-05-03

Two decisive bugs from the v0.12.0 cleanup pass.

### Fixed — **Service double-click now opens the detail modal**
- The intended v0.12 gesture (double-click a service → modal overlay)
  silently failed: `SketchNode`'s inner `dblclick` handler called
  `e.stopPropagation()` and opened the generic Edit Node modal,
  shadowing React Flow's `onNodeDoubleClick → onNodeDrill`. The
  `ServiceDetailModal` was unreachable via the documented gesture.
- `SketchNodeData` now carries an optional `onDrill`. `SketchCanvas`
  wires it for kinds where drill is the intended dblclick gesture
  (services-canvas service → detail modal; service_detail actor_ref →
  jump to actor master). `SketchNode` prefers `onDrill` over
  `onOpenBody` when both could fire, so the Edit Node modal stops
  hijacking drill-eligible nodes.

### Changed — **Inspector says "Service", not "Sub-service"**
- v0.12 eliminated sub-service, but `SketchInspector.ServiceFields`
  still branched on `isTopLevel` and rendered "Sub-service" as the
  section header for any service with a `parent_id` (i.e. all
  services on the v0.12 services canvas, plus the service_detail
  root). Header is now always "Service".
- The dead "top-level vs sub" branch is gone: every service surfaces
  the same six typed fields (`what` / `value_created` / `scope` /
  `trigger` / `how` / `outcome`) plus Do/Don't, matching v0.12's
  "service is one kind" model.

## [0.12.0] — 2026-05-03

A larger refactor — the **Service vs Category split**. v0.10.3's
choice to keep top-level service and sub-service in a single `service`
kind never matched the user's mental model: top-level was always a
*grouping* (Admin / App / Backend), and the actual unit of value
production+exchange was the sub-service. v0.12 splits them.

### Added — **`category` kind**
- New top-level kind on the Services canvas. Categories are pure
  containers — they don't carry actor_refs, foundation refs, or any
  composition. Services nest inside them.
- One typed field: `theme` (one-line common thread).
- Stencil: a Category preset (top-level) and a Service preset that
  drops *inside* a category container.
- Validator: services on the Services canvas must have a category
  parent; categories must be top-level (no nested categories).

### Changed — **Service is now a leaf**
- The "service hierarchy depth = unlimited" rule from v0.10.3 is
  retired. A service has no sub-service. The Services canvas reads
  exactly two levels: `category → service`.
- All the previous sub-service typed fields (`value_created` /
  `trigger` / `how` / `outcome` / `do` / `dont`) and the v0.11.4
  `target_side` field stay on `service` exactly as before.

### Changed — **Service detail is now a modal overlay**
- Double-clicking a service no longer swaps the main canvas. The
  Services canvas stays mounted; the detail content opens in a
  modal overlay (Esc / backdrop click closes).
- The on-disk `service_detail/{id}/detail.json` file structure is
  unchanged. The change is purely UI — modal instead of canvas-swap.
- The drill-in breadcrumb is removed.

### Migration
- v0.1 → v0.2 split now seeds a single default `Category` ("Services",
  with `theme = "Migrated services"`) and parents the migrated
  top-level services under it.
- On read of the Services canvas, any orphan top-level services left
  by v0.11.x projects are silently re-parented under a seeded
  `default-category`. Idempotent.

### Notes
- 164 Python tests passing. Test fixtures updated to wrap services
  in a category. ruff / mypy / tsc all clean.
- `category` brings the kind count from 14 to 15.
- The "user can keep building deep service hierarchies" claim from
  v0.11.4 is rescinded for v0.12 — that's no longer the model. Depth
  in the picture maxes at category → service.

## [0.11.6] — 2026-05-03

Three small UX fixes from continued use.

### Removed — **Toolbar Download / Upload / save-state indicator**
- Save is automatic and silent already; the persistent indicator was
  noise. Errors still surface via the App-level error toast.
- `SketchToolbar` now only carries Undo / Redo / Auto layout.
- `SketchCanvasProps` no longer takes `saveState` / `onDownload` /
  `onUpload`; App.tsx drops `handleDownload` / `handleUpload`. JSON
  import/export, if it ever returns, will be a dedicated flow.

### Changed — **Top-level service default size shrinks**
- Was 300×200, now 180×100. Users still resize after drop; the
  smaller default keeps the Services canvas tidy when many top-level
  services are added (the previous size felt overscale next to the
  project anchor).

### Notes
- This release is viewer-only. Python schema unchanged.
- Pairs naturally with the user's flow after v0.11.5: drop a top-
  level service, drill in, and use the per-master stencil for refs.

## [0.11.5] — 2026-05-03

Two paired user-experience changes triggered by hands-on use.

### Changed — **Services top view only carries Project + Services**
- `_ALLOWED_KINDS_BY_CANVAS["services"]` is now `{"service", "project"}`
  (was `{"service", "project"} | _FOUNDATION_REFS`).
- All Foundation references (`mission_ref` / `value_ref` /
  `identity_ref`), participant references (`actor_ref`), and
  composition kinds (`metric` / `step`) are **service-detail-only**
  from now on. Sub-service decomposition already lives there, so the
  whole "rich detail" lives in one place.
- The v0.11.2 anchor hard validator on the Services canvas is dropped
  along with this change. Alignment ownership now lives inside each
  Service-Detail canvas.
- Migrator: read of an older Services canvas silently drops any
  Foundation ref nodes (idempotent) so existing projects open clean.

### Changed — **Stencil generates one draggable per master**
- The Service-Detail stencil no longer shows a generic "Mission ref"
  preset. Instead it renders **one draggable per master**, labelled
  with that master's real label and tinted with its colour. Ten
  missions on the Foundation canvas → ten mission entries on the
  Service-Detail stencil. Same for `value_ref`, `identity_ref`, and
  `actor_ref`.
- Drops are now **direct**: the preset already carries the target
  master id, so the picker no longer opens for the create flow. The
  picker is reserved for the Inspector's rewire button on orphans.
- `StencilCanvas` type gains a `service_detail` value; `App.tsx`
  passes `"service_detail"` whenever the user is drilled into a
  service detail (was always `"services"` before).

### Notes
- 162 Python tests passing. Existing fixtures padded to match the
  new allowed-kinds set.
- The Inspector's existing actor_ref / foundation_ref orphan UX
  (Re-pick / Delete) still works — the rewire flow keeps the picker.
- "Product as a kind" remains rejected from the v0.11.4 discussion.

## [0.11.4] — 2026-05-03

First user-experience-driven patch on the v0.11 model. Two paired
changes triggered by hands-on use:

- "Where's the project? Each canvas feels like it floats on its own."
  → Project anchor visible on every primary canvas.
- "Operator-facing services and user-facing services need to read
  differently at a glance."
  → New `target_side` typed field on `service`, mirror of `actor.side`.

### Added — **Project anchor on Actors / Services canvases**
- `_ALLOWED_KINDS_BY_CANVAS` admits `project` on Actors and Services
  in addition to Foundation.
- New `_seed_project_anchor()` factory; `_seed_actors_canvas()` and
  the new `_seed_services_canvas()` both seed it at the centre.
- `rename_project()` now propagates the rename to Actors / Services
  copies in addition to Foundation. All three labels stay in sync.
- `read_canvas` quietly backfills the anchor for projects created
  before v0.11.4 (idempotent).

### Added — **`service.target_side` typed field**
- `SketchNode.target_side: Literal["operator", "user", "both"] | None
  = None`. Mirror of `actor.side`.
- Inspector ServiceFields gains a Target side selector
  (운영자측 / 사용자측 / 둘 다 / 미지정).
- Canvas tints the service body by `target_side`:
  - `operator` → blue (`#dbeafe`)
  - `user` → red (`#fee2e2`)
  - `both` → violet (`#ede9fe`)
- No new kind. The two-axis classification (actor side ↔ service
  target_side) keeps the model's mental shape consistent.

### Notes
- Tests: 162 passing. Two existing fixtures updated for the new
  Actors / Services seeds.
- "Product" is intentionally **not** a new kind — operator-facing
  services and user-facing services are distinct service instances
  with different `target_side`, not a separate kind. This decision
  was confirmed during the discussion (see plan file).
- Users can keep building deep service hierarchies (sub-sub-service
  is fine — depth stays unlimited).

## [0.11.3] — 2026-04-30

Closes the v0.11 release line. Phase D (Mode 2 time-axis layer
compatibility) was verified without code changes — every Phase A/B/C
decision extends non-destructively when the time-axis kinds (Task,
schedule, etc.) are eventually added. The infrastructure layer joins
Mode 2 as already documented in IDENTITY.md.

### Changed — `docs/ROADMAP.md`
- Reorganised to cover both v0.10 and v0.11 release lines with a
  per-phase ship table for v0.11.

### Notes — what's next
- v0.11 model is now intentionally stable. The next round is
  **user-experience polish** — known follow-ups (e.g. node click
  going to label-edit instead of opening the Inspector) and anything
  surfaced by hands-on use of the new actor/service model.
- Mode 2 (time-axis task layer) waits until that polish round
  generates concrete requirements.
- No code or schema changes in this release.

## [0.11.2] — 2026-04-30

Phase C of v0.11. Two long-standing soft rules graduate to hard
validators, and `actor_ref` joins the typed-field family with a
per-actor-per-service value-flow pair.

### Added — **`actor_ref` typed fields (Phase C3)**
- `SketchNode.gives: str = ""` — what this actor gives to the service.
- `SketchNode.receives: str = ""` — what this actor receives back.
- Inspector renders an "Value flow" form on `actor_ref` selection
  with the two fields side by side. Both optional.
- Rationale: PHILOSOPHY.md P6 ("arrows carry action + value") in its
  weakened form. The flow lives on the ref node rather than on an
  explicit edge, so the value economy is captured per-pair without
  forcing the user to draw and label dozens of arrows.
- `service.value_created` (aggregate) and `actor_ref.gives` /
  `receives` (per-pair) are deliberately orthogonal.

### Changed — **Top-level service Foundation anchor is now a hard
validator (Phase C2)**
- A `services` canvas containing at least one top-level service must
  also contain at least one Foundation reference (`mission_ref` /
  `value_ref` / `identity_ref`). An empty services canvas is fine.
- The same rule was already in IDENTITY.md and CONCEPTS.md as docs;
  this release wires it into Pydantic.
- Mapping is **canvas-level, not per-service**: the visual layout
  (which anchor sits next to which service) carries the 1:1 nuance.
  This keeps the model schema free of new fields and matches the
  existing `mission_ref` placement pattern from v0.10.2.
- Migrator: legacy v0.1 sketches whose split overview canvas had no
  anchor get a single `mission_ref → "mission"` seeded automatically
  so the canvas validates after open. Idempotent.

### Notes
- Tests: 162 passing. New test `test_overview_services_without_anchor_rejected`
  asserts the new floor; existing fixtures padded with anchors.
- Phase D (time-axis compatibility + v0.11 vs v0.12+ scoping) remains
  the last v0.11 step.

## [0.11.1] — 2026-04-30

Phase B of v0.11. The `actor_ref` orphan UX (re-pick, delete) now
extends to all four ref kinds, and ref labels stay in sync with their
masters automatically.

### Added — **Foundation ref orphan UX**
- `mission_ref` / `value_ref` / `identity_ref` Inspector blocks now
  show a **Re-pick…** + **Delete** button pair when the master is
  missing from the Foundation canvas. Mirrors the existing
  `actor_ref` orphan UI.
- `FoundationRefPicker` already supported a `rewire` mode (since
  v0.10.2); this release wires it through `SketchCanvas` so the
  Inspector's Re-pick button opens the picker and the user-selected
  master replaces the orphan's `ref_*_id`.

### Added — **Ref label auto-sync**
- The displayed label for any ref kind (`actor_ref`, `mission_ref`,
  `value_ref`, `identity_ref`) is now **derived from the master at
  render time** — `→ {master.label}`. The stored label remains as a
  fallback for the orphan case (master missing).
- This means: rename the master `Mission` to `우리의 사명`, and every
  `mission_ref` on every canvas updates instantly with no propagation
  step. No more stale denormalised labels.

### Notes
- Implementation: the label transform happens in `SketchCanvas`'s
  React Flow node mapping (`useMemo`), via lookups against the
  `availableActors` / `availableMissions` / `availableValues` /
  `availableIdentities` props the App already passes through. No
  backend / migration change needed.
- Phase C (Service field polish) and Phase D (time-axis
  compatibility) remain.

## [0.11.0] — 2026-04-28

The Actor model promised by v0.10.6 / v0.10.7 lands as code. Phase A
of the v0.11 redefinition (A1–A5) is fully implemented; B/C/D follow
in later releases.

### Added — **Actor typed fields**
- `SketchNode.motivation: str = ""` — why this actor participates.
- `SketchNode.pain: str = ""` — frictions / frustrations they face.
- `SketchNode.side: Literal["operator", "user"] | None = None` —
  flat category; partitions actors by which side of the value
  exchange they occupy. Set on every actor; mirrored onto every
  `actor_ref` so service-detail canvases can validate operator/user
  mixes without cross-canvas lookups.
- Inspector renders an `Actor` form (Side selector + Motivation +
  Pain textareas) when `kind === "actor"`.

### Changed — **Hard validators**
- `actors` canvas now requires **≥ 2 actor classes**.
  IDENTITY.md baseline: a project without two sides can't host value
  exchange. New projects seed two placeholders (Operator + User) so
  this floor is satisfied out of the box.
- `service_detail` canvas now requires **≥ 2 `actor_ref` nodes**.
  Auto-creation paths (`sync_details_with_overview`, the v0.10
  migrator) seed two stub refs (operator + user) for every new or
  migrated detail canvas.

### Added — **Project + migration seeding**
- `_seed_actors_canvas()` (folder_io.py) seeds two actor classes
  ("Operator" + "User", with `side` set) on project creation.
- Migration path (`_backfill_actor_sides` + `_ensure_minimum_actors`
  + `_detail_actor_ref_seeds`) heals legacy v0.10.x projects on open:
  defaults missing `side` to `"user"`, pads under-populated actors
  canvases, and seeds operator/user actor_refs for any service_detail
  that doesn't already have them. Idempotent.

### Changed — **`docs/CONCEPTS.md` actor section**
- Adds the "two orthogonal mechanisms" subsection (`side` flat
  category + `parent_id` is-a tree) — the central insight from Phase
  A3 of the discussion.
- Documents the v0.11 typed fields (`motivation`, `pain`) and notes
  the deliberate exclusion of Do/Don't and permissions from the
  actor.

### Notes
- Phase A discussion log lives at
  `~/.claude/plans/ancient-pondering-petal.md`.
- Phase B (actor_ref Symbol justification + orphan UX), Phase C
  (Service field polish), and Phase D (time-axis compatibility) are
  the remaining v0.11.x work.
- This release re-asserts every IDENTITY.md floor as Pydantic
  validation, not just doc text. Existing projects migrate cleanly;
  no data loss is expected.

## [0.10.7] — 2026-04-28

Docs-only patch capturing the load-bearing Actor / Service decisions
made in v0.11 Phase A1 + A2 planning. The code changes (validators,
seed actors) ship later as v0.11.0; this release is the philosophy
front-load so the docs are accurate before any model moves.

### Added — `IDENTITY.md` "Actor & Service — the Core Philosophy" section
- **Actor definition**: a *class of people* who participate in the
  project's value economy. Class, not individual; people only — APIs,
  systems, bots, and infrastructure are out of scope until Mode 2.
- **Service definition**: a *playground* where stakeholders **produce
  and exchange** value (the dual phrasing is deliberate — services
  produce new value through actor participation, not just route
  pre-existing value).
- **Service minimum baseline**: every service must include **≥ 2**
  participating `actor_ref` nodes — non-negotiable.
- **Operator-explicit rule**: the operator/developer must always be
  one of those `actor_ref`s. The reasoning is moderation: services
  are playgrounds, freedom needs alignment-keepers, and *which*
  operator owns alignment for *which* service must be visible —
  exactly Plot's stated purpose.
- A "Why these are philosophy, not just rules" subsection explains
  that loosening any of these floors changes the product, not just
  the schema.

### Changed — `CONCEPTS.md`
- `actor` kind: redefined as "a class of people," with the people-only
  scope and the project-level `≥ 2` floor stated. Previous "person /
  system / organisation" wording retired.
- `service` kind: re-introduced with the playground metaphor,
  "produce + exchange" phrasing, and a new explicit subsection
  documenting the service minimum baseline (≥ 2 actor_refs, explicit
  operator).
- "Design principles" #2 ("templates rich, requirements minimal") now
  enumerates the current set of hard floors and cross-references
  IDENTITY.md.

### Notes
- This is **not** a behaviour change. The validators and the seed
  actors (User / Operator placeholders) land in v0.11.0 once the rest
  of Phase A — A3 (sub-actor semantics), A4 (typed fields), A5
  (naming) — and Phase B / C / D are decided. Doing docs first means
  the model changes can be evaluated against a stable spec.
- Plan-file framework with the running discussion log lives at
  `~/.claude/plans/ancient-pondering-petal.md`.

## [0.10.6] — 2026-04-28

Docs-only patch ahead of v0.11. Captures Plot's product identity in
permanent storage so future sessions (human or AI) can ground their
decisions in what Plot actually is — and is not.

### Added — **`docs/IDENTITY.md`**
- New canonical document stating what Plot is (a strategic operations
  design + alignment tool) and what it is not (a simple mindmap or
  brainstorming tool).
- The four use purposes: concrete service planning, direction alignment,
  position in the big picture, relationship visualisation.
- The two modes — today's picture mode and the future time-axis task
  mode — and the implication that v0.11+ models must survive the
  transition.
- Korean original quote from the user (2026-04-28) preserved so the
  source intent is auditable.

### Changed — `docs/CONCEPTS.md`
- Header now points to `IDENTITY.md` first. CONCEPTS remains the
  technical reference (kinds, canvases, fields); IDENTITY is the
  "why and for whom" check applied before any new concept lands.

### Notes
- This release contains no code changes. It exists to fix a gap caught
  during v0.11 planning: the user-stated identity from 2026-04-28 was
  living only in the in-progress plan file, which is volatile across
  sessions.

## [0.10.5] — 2026-04-28

Step 6 of the v0.10 kind-redefinition program — and the **final** step.
The two pre-existing composition kinds (`rule`, `content`) gain typed
fields so the Inspector can drive them as deterministically as the
kinds added earlier in v0.10.

### Added — **`rule` typed fields**
- `SketchNode.policy: str = ""` — the rule statement.
- `SketchNode.enforcement: str = ""` — how it's enforced.
- `SketchNode.actor_permissions: dict[str, str] = {}` — actor-id →
  permission-string map. Free-form value; suggested vocabulary is
  C/R/U/D shorthand (`"RUD"`, `"CRUD"`, etc.).

### Added — **`content` typed fields**
- `SketchNode.format: str = ""` — artifact shape (JSON, MD, image, …).
- `SketchNode.producer_actor_id: str | None = None` — actor master id
  that creates the content.
- `SketchNode.consumer_actor_id: str | None = None` — actor master id
  that consumes it.

### Added — **Expandable Inspector rows**
- The `CompositionList` rows for Rules and Contents are now expandable
  via a chevron toggle. Collapsed: just the label input. Expanded:
  the kind-specific typed form.
- Rule form includes a **permission editor**: a dropdown of actor
  masters not yet assigned + a per-row permission text input + a
  remove button.
- Content form includes producer/consumer **actor pickers** populated
  from the same `availableActors` list the Inspector already uses.

### Notes
- `actor_permissions` is keyed by actor master id (matching the
  `actor_ref` semantic from Step 3); the editor surfaces the actor's
  label for readability.
- The permission string is intentionally free-form for v0.10. A future
  release may switch to a richer schema (e.g. `{create, read, update,
  delete}` booleans) once the convention settles.
- This release closes out the v0.10 kind-redefinition program: every
  kind now has a clear semantic purpose, typed fields where the
  domain has separable facets, and Inspector rendering. The next
  release line can focus on edge utilisation or the time-axis layer.

## [0.10.4] — 2026-04-28

Step 5 of the v0.10 kind-redefinition program. Two new composition
kinds for the Service-Detail canvas — explicit success indicators
(metrics) and ordered procedural flow (steps).

### Added — **`metric` kind**
- New node kind admitted only on the **service_detail** canvas, with
  the same parent-must-be-a-service rule that already governs
  `rule` / `content`.
- Typed fields:
  - `target: str = ""` — goal value or threshold (e.g. `>99%`).
  - `measurement: str = ""` — how the metric is measured.
- Stencil entry on the Services-tab stencil under "Composition"
  (drop on a Service container).

### Added — **`step` kind**
- New node kind admitted only on the **service_detail** canvas, same
  parent constraint as the other composition kinds.
- Typed fields:
  - `order: int | None = None` — ordinal position in the sequence;
    `None` leaves the step unordered (e.g. parallel branches).
  - `outcome: str = ""` — observable end state. Shared with `service`
    (declared once on the model in v0.10 Step 4).
- Stencil entry on the Services-tab stencil under "Composition".

### Changed — **`_COMPOSITION_KINDS`**
- Now `{rule, content, metric, step}`. Inside a `service_detail`
  canvas all four kinds must have a service parent.

### Notes
- `metric` and `step` are canvas-first composition (visible on the
  Service-Detail canvas), unlike `rule` / `content` which remain
  Inspector-only `+ Add` items. The model accepts both kinds in either
  position; the editorial choice is a UI policy.
- Inspector forms render the typed fields per-kind. Drop validator
  rejects metric/step placed at top level with the standard
  "Drop inside a Service container" message.

## [0.10.3] — 2026-04-28

Step 4 of the v0.10 kind-redefinition program. Service nodes gain typed
fields differentiated by canvas — top-level services (the strategic
view) and sub-services (the operational view) get different forms while
sharing one model.

### Added — **Service typed fields**
- `SketchNode` gains six optional `str` fields (default `""`):
  - Top-level focus: `what`, `value_created`, `scope`.
  - Sub-service focus: `value_created`, `trigger`, `how`, `outcome`.
  - The shared Do/Don't pair from Step 2 (`do`, `dont`) is reused.
- One model carries all six on every service node; the **Inspector**
  surfaces them per branch:
  - `kind === "service"` on the **services** canvas with no parent →
    Label · What · Value created · Scope · Do · Don't.
  - `kind === "service"` on a **service_detail** canvas →
    Label · Value created · Trigger · How · Outcome · Do · Don't.

### Notes — **No hard validator gating**
- The ROADMAP suggested gating top-level services on either a
  Foundation ref or non-empty `value_created`. Per the v0.10 design
  philosophy ("rich fields, minimal required"), this is **not** a
  hard validator: writes succeed regardless. The Inspector's typed
  form makes the missing fields visible without blocking drafting.
- Round-trip and per-branch tests added in `tests/test_canvas_doc.py`.

## [0.10.2] — 2026-04-28

Step 3 of the v0.10 kind-redefinition program. Generalises the existing
`actor_ref` Symbol/Component pattern to the three Foundation masters
(Mission / Core Value / Identity), so a Service can declare which
Foundation commitment it answers to without leaving its canvas.

### Added — **Foundation reference kinds**
- New node kinds: `mission_ref`, `value_ref`, `identity_ref`. Together
  with the pre-existing `actor_ref` they form a uniform four-member
  family of "instance points at master" symbols.
- New `SketchNode` fields: `ref_mission_id`, `ref_value_id`,
  `ref_identity_id` (each `str | None = None`). Validator rule: every
  `*_ref` kind requires its corresponding `ref_*_id` to be set.
- `_ALLOWED_KINDS_BY_CANVAS`: the three new ref kinds are admitted on
  the **Services** overview canvas and on **Service-Detail** canvases.
  They stay forbidden on Foundation (would be a self-loop) and on
  Actors (out of place there).

### Added — **Stencil presets + picker UI**
- New stencil entries on the Services-side stencil: Mission ref, Value
  ref, Identity ref (under a "Foundation refs" section). Each gets a
  distinct hue and Lucide icon (flag / star / heart) so the canvas reads
  at a glance.
- New `FoundationRefPicker` modal — drop a ref onto the canvas, the
  picker lists candidates pulled from the Foundation canvas (Mission /
  Core Value / Identity, depending on the kind dropped). Clicking one
  spawns the ref node with the right `ref_*_id` set and a `→ {label}`
  display label.
- `App` derives the three master lists (`availableMissions`,
  `availableValues`, `availableIdentities`) from the Foundation canvas
  cache and passes them down to the canvas/inspector.

### Added — **Inspector ref display**
- The Inspector shows a "References — {kind}" block for each ref node,
  listing the resolved master label or a "⚠ master not found" warning
  when the target doesn't exist (orphan).

### Notes
- The orphan re-pick UX from `actor_ref` is **not** generalised in this
  step — for now users can drop a fresh ref preset and delete the
  broken one. Re-pick is on the list for a follow-up patch.
- The validator does not (yet) cross-check that `ref_mission_id` etc.
  point at an actual master in the project's Foundation canvas: writes
  succeed even with stale ids so drafting stays cheap; the Inspector's
  orphan warning surfaces the issue interactively.

## [0.10.1] — 2026-04-28

Step 2 of the v0.10 kind-redefinition program (see
[`docs/ROADMAP.md`](docs/ROADMAP.md)). Re-introduces typed fields on
the remaining two Foundation kinds, with the AI-first **Do / Don't**
pair shared between them.

### Added — **Core Value typed fields**
- `SketchNode.definition` (`str`, default `""`) — what the value means.
- Inspector renders a typed form when `kind === "core_value"`:
  Label · Definition · Do · Don't.

### Added — **Identity typed fields**
- `SketchNode.description` (`str`, default `""`) — how the aspect is
  expressed (Voice / Energy / Speech style / …).
- Inspector renders a typed form when `kind === "identity"`:
  Label · Description · Do · Don't.

### Added — **Shared Do / Don't pair**
- `SketchNode.do`, `SketchNode.dont` (`str`, default `""`). Both fields
  exist on every node so the schema stays uniform; only the Inspector
  forms for `core_value` and `identity` surface them today. Future kinds
  (Mission, Service) may opt in without a schema migration.

### Notes
- All four new fields are optional and default to `""` — none of them
  introduce a validator that could reject a legacy canvas. Mirroring
  v0.10 Step 1's principle: "rich fields, minimal required".
- Long-form prose still belongs in `details.md` per node. Typed fields
  are for short, structured facets that an LLM (or human reader) can
  consume deterministically.

## [0.10.0] — 2026-04-28

This release kicks off the v0.10 kind-redefinition program (see
[`docs/CONCEPTS.md`](docs/CONCEPTS.md) and [`docs/ROADMAP.md`](docs/ROADMAP.md)).
Step 1 ships the rename of the identity canvas and the first AI-first typed
fields on `mission`. Subsequent steps will re-introduce typed fields on the
remaining kinds where the domain has clearly distinct facets.

### Changed — **`core` canvas → `foundation` canvas**
- Canvas kind/id rename: `"core"` → `"foundation"`. The folder is now
  `.plot/{project_id}/foundation/canvas.json`. Existing v0.5–v0.9 projects
  are migrated transparently on open: the `core/` directory is renamed to
  `foundation/` and the `canvas_kind` field is rewritten. Legacy alias
  `migrate.upgrade_core_canvas_if_needed` still works.
  ([`plot_mcp/folder_io.py`](plot_mcp/folder_io.py),
   [`plot_mcp/migrate.py`](plot_mcp/migrate.py),
   [`plot_mcp/models.py`](plot_mcp/models.py))
- Viewer tab label is now **Foundation** (not Core); `CanvasKind` /
  `CanvasKey` types match. Default folder slug is `foundation/…`.
  ([`viewer/src/types.ts`](viewer/src/types.ts),
   [`viewer/src/App.tsx`](viewer/src/App.tsx),
   [`viewer/src/lib/slug.ts`](viewer/src/lib/slug.ts))

### Added — **Mission typed fields** (AI-first)
- `SketchNode.what_we_do`, `SketchNode.why`, `SketchNode.direction` (all `str`,
  default `""`). These three facets are stored directly on the `mission` node
  in `canvas.json` — Plot is the sole editor. Long-form prose still lives in
  `details.md`. Other kinds also carry the fields as empty strings; only the
  Inspector for `kind === "mission"` exposes a typed form.
  ([`plot_mcp/models.py`](plot_mcp/models.py),
   [`viewer/src/types.ts`](viewer/src/types.ts),
   [`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))

### Added — **Concept docs**
- [`docs/CONCEPTS.md`](docs/CONCEPTS.md) — the full glossary
  (4 canvases × 13 kinds + design principles). SSOT for human and AI tooling.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — six-step v0.10 implementation
  plan. Step 1 is this release.

### Notes
- Mission is **0..N** (was effectively 1..N). Validator unchanged; the doc
  surface now matches what the model already allowed since v0.5.
- Foundation rename is backward-compatible at the file-system layer — opening
  a v0.9 project rewrites it in place to the new layout.

## [0.9.1] — 2026-04-28

### Removed
- **Typed fields on `SketchNode`** (`tagline`, `audience`, `method`, `goal`, `summary`, `criteria`). For most kinds the typed `summary` was just a worse copy of `label`. The viewer's `TypedFieldsForm` and the per-kind `TYPED_FIELDS` map go with them. Long-form structure (Tagline / Audience / Method / Goal sections) now lives wherever the user wants it inside `details.md`.
- **`details.md` legacy text bridge from v0.1 migration** — the old core-root `mission` / `identity` text used to land in `tagline` / `summary`. With those fields gone the text is dropped on migration. The structural mission / identity nodes still get created so the user can paste the text into the new node's `details.md` if they care. (Practically nobody ever ran v0.1 → v0.9 on real data.)
- **`leftover bodySections.ts` viewer file** — finally tracked the deletion that should have ridden along with v0.9.0.

### Notes
- Inspector layout per node is now: **Label** input + per-node **`details.md` editor** (or "Create details" button). That's it. No middle tier.
- On-canvas node preview is just the label — the body block is hidden when `data.body` is empty (which it always is now).
- `details.md` is still SSOT for prose; external editors (Obsidian, VS Code) can still edit it freely with watcher-driven sync.

## [0.9.0] — 2026-04-26

### Changed — **typed JSON fields + per-node `details.md`** (no more sync conflicts)
- **JSON and MD now hold different data.** Typed short fields live on the node in `canvas.json` and are written/read only by Plot; long prose lives in a per-node `details.md` and Plot reads/writes that file just like any other editor (Obsidian, VS Code) can. Same content is never duplicated, so the sync question that haunted v0.7 / v0.8 disappears entirely. ([`plot_mcp/models.py`](plot_mcp/models.py))
- **`SketchNode` typed fields**: `tagline`, `audience`, `method`, `goal`, `summary`, `criteria`. All optional; Inspector renders kind-specific subsets (Mission → Tagline/Audience/Method/Goal, CoreValue → Summary/Criteria, Identity / Project → Summary).
- **`SketchNode.body` is gone.** Its preview-cache role is moot (typed fields are direct), and its long-form-edit role moves to `details.md`. v0.1 migration drops legacy `mission` text into `tagline`, `identity` text into `summary`.
- **`SketchNode.folder_path` → `SketchNode.details_path`.** Same path-traversal validator, clearer name (it points at the node's `details.md`, not a generic folder).
- **Inspector**: dropped the H3-section `KindTemplate` and the `ConnectToFolderButton` flow. Replaced with `TypedFieldsForm` (binds directly to typed fields) + `DetailsSection` (opens `MDFileEditor` if `details_path` is set, otherwise shows "Create details"). ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))
- **External MD editing is now safe.** The watcher tracks `details.md` files too — edits in Obsidian, VS Code, or any other editor raise a `project_changed` event and the open viewer reloads. There's nothing to drift because the JSON has no mirror of the MD content. ([`plot_mcp/watcher.py`](plot_mcp/watcher.py), [`plot_mcp/broadcast.py`](plot_mcp/broadcast.py))
- **On-canvas node preview** now picks from typed fields directly: Mission shows `tagline` (falling back to `summary`); everything else shows `summary`. No more H3 parsing on the client.

### Removed
- `plot_mcp/body_sections.py`, `viewer/src/lib/bodySections.ts`, `tests/test_body_sections_py.py` — no callers.
- `_sync_node_body_cache_on_md_write` and the `preview` field on `PUT /api/files` — typed fields are direct, no cache to sync.
- `ConnectToFolderButton`, `KindTemplate`, `REFERENCES_FIELD`, `TEMPLATES` (Inspector).
- `body` field on `SketchNode` (Python and TypeScript).
- Long-form textarea in `SketchBodyModal` (visual properties only now).

### Notes
- **No automatic migration from v0.8.** User confirmed no production data; v0.9 is a clean break.
- `details.md` is intentionally never parsed by Plot. Use whatever Markdown layout you like — `# Heading`, tables, Mermaid blocks, etc.

## [0.8.0] — 2026-04-23

### Changed — **breaking disk-layout refactor**
- **`.plot/` is wrapper-less and canvas-grouped.** Every project now owns a single folder under `.plot/` containing one subfolder per canvas kind; each canvas folder holds its structure (`canvas.json`) alongside its nodes' content folders. The former sibling `workspace/` tree is gone — long-form content lives inside the project's own folder.
  ```
  .plot/{project_id}/
    project.json
    core/
      canvas.json
      {slug}/index.md
    actors/
      canvas.json
      {slug}/index.md
    services/
      canvas.json                 ← top-view
      {service_id}/
        index.md
        detail.json               ← per-service drill-down
  ```
  - `.plot/sketches/` intermediate removed.
  - `core.json` / `actors.json` / `services-overview.json` → `{canvas}/canvas.json`.
  - `services-detail/{sid}.json` → `services/{sid}/detail.json` (co-located with the service's `index.md`).
- **`CanvasKind` literal `services_overview` → `services`.** Tab label is already "Services" — the canvas key now matches.
- **`/api/files`, `/api/folders` are project-scoped.** `project_id` is required; `path` is relative to `.plot/{project_id}/`. Client can no longer accidentally address another project's tree via `..`.
- **`folderSlug` drops the `workspace/` prefix.** Returns `{canvas}/{kind}-{label}` on both server (`plot_mcp/slug.py`) and client (`viewer/src/lib/slug.ts`).
- **`sync_details_with_overview`** archives a service's whole folder (including `index.md`) to `services/_archive/{sid}/` when it disappears from the top-view — the previous `.json`-only archive would have orphaned any long-form notes.

### Removed
- `workspace/` wrapper folder (everything moved inside `.plot/{project_id}/`).
- `services-detail/` dedicated folder.
- `.plot/sketches/` intermediate directory for new projects (legacy v0.1 migration still reads from it when it exists).

### Notes
- **No automatic migration from v0.7.** The user confirmed no production data — BANAS is a dev-only artifact. Opening an old v0.7 project in v0.8 will look empty; re-create or run a manual port.
- v0.1 → v0.4 auto-migration path still works and lands new projects in the v0.8 layout.

## [0.7.1] — 2026-04-23

### Added
- **Inspector width toggle** (`⇤` / `⇥`). Narrow stays at 320px; wide expands to `min(720px, 60vw)`. Choice persists in `localStorage` so the next node opens at the user's preferred size. ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))
- **MDPreview component + Edit / Split / Preview tabs in the MD editor.** Rendered view is powered by `react-markdown` + `remark-gfm` (tables, task lists) plus a custom code renderer that pipes `` ```mermaid `` blocks through `mermaid.render`. Diagrams appear inline; parse errors fall back to the raw source instead of crashing the Inspector. Split mode pairs well with the wide Inspector for drafting diagrams next to the source. ([`viewer/src/edit/MDPreview.tsx`](viewer/src/edit/MDPreview.tsx), [`viewer/src/edit/MDFileEditor.tsx`](viewer/src/edit/MDFileEditor.tsx))

## [0.7.0] — 2026-04-23

### Added
- **Folder-backed node content — Inspector becomes an MD editor.** Click a node with a `folder_path`, the right panel turns into a full Markdown editor for that folder's `index.md`. Free-form text, structured ### H3 sections, wiki links — all round-trip to disk via a 600 ms debounced save. Mirrors the Claude-skill pattern the user asked for ("each node = folder, each folder has an `index.md`"). ([`viewer/src/edit/MDFileEditor.tsx`](viewer/src/edit/MDFileEditor.tsx))
- **`SketchNode.folder_path` field.** Optional relative path (under `project_path`) that binds a node to a folder on disk. When set, `body` holds only a short summary cache for the canvas preview; the long-form lives in the MD file. Validator rejects absolute paths, `..` segments, and blanks. ([`plot_mcp/models.py`](plot_mcp/models.py))
- **`/api/files` and `/api/folders` endpoints.** `GET /api/files`, `PUT /api/files`, `POST /api/folders`. Path-traversal, absolute paths, and symlink-escapes are all rejected; writes go through a tmp-rename so readers never see half a file. Folder POST uniquifies on collision (`-2`, `-3`, …). ([`plot_mcp/file_io.py`](plot_mcp/file_io.py), [`plot_mcp/api_endpoints.py`](plot_mcp/api_endpoints.py))
- **Server-side preview cache sync.** `PUT /api/files` with `project_id` + `node_id` query hints parses the saved `index.md`, picks the `### Tagline` (Mission) or `### Summary` (everything else), and mirrors it into the node's `body`. The on-canvas preview stays current without a separate fetch per node.
- **"Connect to folder" button in Inspector.** Legacy body-backed nodes (BANAS and everything shipped before 0.7) can opt into the folder model one click at a time: the button asks the server for a fresh folder based on `kind + label`, seeds `index.md` with whatever `body` already had, and attaches `folder_path`. No big-bang migration. ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))
- **Shared slug convention.** `plot_mcp/slug.py` + `viewer/src/lib/slug.ts` compute the same default folder path — `workspace/{canvas}/{kind}-{label-slug}/` — so the client doesn't need a round-trip just to guess a name. Korean and CJK characters are preserved; server uniquifies on collision.

### Notes
- BANAS (and any pre-0.7 project) keeps working exactly as before until the user presses "Connect to folder" on a node. Migration is opt-in, not automatic.
- `index.md` is free-form. Use whatever headings you like — `### Tagline` and `### Summary` are the only ones the canvas preview reads.

## [0.6.0] — 2026-04-22

### Added
- **Markdown body rendering.** `SketchNode` now renders its body through `react-markdown`, so Inspector template fields (`### Tagline`, `### Summary`, …) appear as small uppercase section labels inside the node, and bold / italic / lists / links stay readable. Left-aligned body text reads naturally once multiple sections are stacked; the label keeps its centred treatment. ([`viewer/src/canvases/SketchNode.tsx`](viewer/src/canvases/SketchNode.tsx))
- **References field in Inspector templates.** Mission / Core Value / Identity / Project each pick up a `References` field for wiki-style links (e.g. `[[workspace/identity/mission.md]]`) pointing at long-form narrative docs. Plot stays the structural SSOT; MD files stay the narrative SSOT — no auto-sync. ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))

## [0.5.1] — 2026-04-22

### Fixed
- **Legacy Core children no longer trap inside the Project anchor.** Pre-v0.5 projects (like BANAS) stored Mission / Identity nested under a `core`-kind octagon. The v0.5 upgrade now un-parents every node whose `parent_id` pointed at a legacy core anchor, so after opening the pillars land as peers around the small circular Project — not inside it. ([`plot_mcp/migrate.py`](plot_mcp/migrate.py))

### Changed
- **Top-left kind tag on Core nodes.** Mission / Core Value / Identity / Project nodes carry a small uppercase "MISSION" / "CORE VALUE" / … label in the top-left so the kind is legible at a glance, before opening the Inspector. ([`viewer/src/canvases/SketchNode.tsx`](viewer/src/canvases/SketchNode.tsx))
- **Star icon retired from Core kinds.** Mission / Core Value / Identity / Project no longer seed with a `star` icon (every Core kind had the same star, so it couldn't tell them apart). The new kind tag carries the identity signal. Legacy disk files carrying `icon: "star"` on Core kinds get cleaned up on the next open.
- **Fold button shifted to 24×24** (was 16×16) so it's no longer easy to miss. The Core canvas suppresses it entirely — Core is a peer layout, fold has no meaning there. Other canvases (actors / services) keep it.

## [0.5.0] — 2026-04-22

### Added
- **Project anchor on the Core canvas.** Every project now carries a central, circular **Project** node — auto-seeded on create / on the first open of a legacy project, protected from deletion (keyboard Delete, right-click Delete, Inspector Delete all refuse to touch it), and label-synced with `ProjectDoc.name` in both directions. Rename from the sidebar updates the node; editing the node label renames the project (the server reconciles on `PUT /canvases/core`). ([`plot_mcp/folder_io.py`](plot_mcp/folder_io.py), [`plot_mcp/migrate.py`](plot_mcp/migrate.py), [`viewer/src/canvases/SketchCanvas.tsx`](viewer/src/canvases/SketchCanvas.tsx))
- **Multi-Mission and multi-Identity on the Core canvas.** Mission is now 1..N (was exactly 1); Identity is now 1..N peers (was 1 + N Facet children). Each Identity node represents one aspect (Voice / Energy / Speech style / Visual tone / …) — drag the preset for every aspect you need. ([`plot_mcp/models.py`](plot_mcp/models.py))
- **Kind-aware Inspector templates.** Selecting a Mission / Core Value / Identity / Project node now surfaces the right fields instead of a bare Description textarea:
  - Mission → Tagline, Audience, Method, Goal, Story
  - Core Value → Summary, Decision criteria
  - Identity → Summary, Details
  - Project → Summary
  Fields persist as `### H3` Markdown sections inside `SketchNode.body` — no schema change, unknown sections and free-form notes round-trip untouched. ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx), [`viewer/src/lib/bodySections.ts`](viewer/src/lib/bodySections.ts))
- **Automatic v0.4 → v0.5 Core-canvas migration.** Opening a project with legacy `core`-kind octagons or `identity_facet` children heals itself lazily — the `read_canvas` path calls `upgrade_core_canvas_if_needed`, which rewrites kinds in-place and persists the result. No manual step. ([`plot_mcp/migrate.py`](plot_mcp/migrate.py))

### Changed
- **`NodeKind` shrinks.** Removed `core` (was the legacy octagon anchor) and `identity_facet` (absorbed into `identity`). Added `project`. Disk files carrying the retired kinds are rewritten on open.
- **`_core_canvas_rules`** relaxes Mission / Identity from "exactly 1" to "≥ 1" and adds "exactly 1 Project, top-level".
- **Stencil copy.** Mission / Core values / Identity sections now read "add as many as you need". Identity adds a hint listing example aspects. Identity Facet preset disappears.

### Fixed
- Right-click context menus no longer show their items with text pre-highlighted. The residual text selection the browser leaves behind on right-click is now suppressed with `select-none` + a `mousedown` preventDefault on the menu container. ([`viewer/src/canvases/SketchContextMenu.tsx`](viewer/src/canvases/SketchContextMenu.tsx))
- The Inspector no longer shows an empty "Select a node to see details" placeholder — it renders `null` when nothing is selected, reclaiming canvas width.

## [0.4.1] — 2026-04-21

### Added
- **Drop-overlap nudge.** Dragging a preset onto a spot already occupied by a sibling node no longer buries the new node behind the old one — the drop position slides diagonally by 32px until it finds a free slot (max 24 tries). Works for both top-level drops and container-nested drops. ([`viewer/src/canvases/SketchCanvas.tsx`](viewer/src/canvases/SketchCanvas.tsx))
- **Keyboard cheatsheet.** Press `?` anywhere to toggle a modal listing every shortcut; `Esc` or click-outside closes it. ([`viewer/src/App.tsx`](viewer/src/App.tsx))
- **Inspector delete button.** Every non-root, non-core node gets a `✕ delete` button in the Inspector header (with a confirmation prompt). The actor_ref orphan banner still has its own Delete button.
- **Inspector color swatch.** Small square next to the kind label shows the node's current fill colour at a glance.
- **Auto-layout now arranges Core / Actors / Detail canvases.** `autoLayout` treats `parent_id` relationships as implicit dagre edges, so the toolbar "Auto layout" button finally does something useful on canvases whose semantic links live in the hierarchy rather than in explicit edges. ([`viewer/src/flow/autoLayout.ts`](viewer/src/flow/autoLayout.ts))

### Fixed
- Tab-switch fit-view is now reliable: the canvas key includes the active canvas, so React Flow remounts and its `fitView` runs fresh on every tab change.

## [0.4.0] — 2026-04-21

### Added
- **Full viewer / HTTP cutover to the v0.2 folder layout.** New REST surface: `GET/POST /api/projects`, `GET/PATCH/DELETE /api/projects/{id}`, `GET/PUT /api/projects/{id}/canvases/{kind}[?service_id=]`. The viewer now loads one canvas at a time — no more in-memory tab-filtering. ([`plot_mcp/api_endpoints.py`](plot_mcp/api_endpoints.py), [`plot/viewer/src/api.ts`](viewer/src/api.ts))
- **Per-project git repo for session bookmarks.** Each project folder gets its own `.git/` at creation time, but editing never auto-commits. The user plants named tags at meaningful moments via the new **Mark session…** button or the `tag_project` MCP tool. `GET/POST /api/projects/{id}/tags` + `DELETE .../tags/{name}` expose the tag surface. ([`plot_mcp/git_store.py`](plot_mcp/git_store.py))
- **Project-level unified undo/redo.** New `useProjectHistory` hook holds one in-memory stack per loaded project with `{canvasKey, prev, next}` entries — `Ctrl+Z`/`Ctrl+Z+Shift`/`Ctrl+Y` rewinds any canvas's last edit and auto-switches tabs to where the change landed. 50-entry cap, cleared on project switch or external WebSocket write. ([`viewer/src/canvases/useProjectHistory.ts`](viewer/src/canvases/useProjectHistory.ts))
- WebSocket event shape: `sketch_changed` → **`project_changed`** with `{project_id, canvas_kind?, service_id?}` so the viewer only reloads the affected canvas.
- Sidebar has a **Session tags** collapsible panel listing the project's `git tag` entries with a hover × to delete (commit stays reachable via reflog).
- Silent v0.1 → v0.2 auto-migration on the first `GET /api/projects` call; banner toast reports what was migrated.
- New MCP tools: `tag_project`, `list_project_tags`, `delete_project_tag`. Canvas-level tools from v0.3 (`list_projects`, `get_project`, `get_canvas`, `update_canvas`, etc.) stay.

### Changed
- Sidebar "Sketches" → "Projects", "+ New sketch" → "+ New project". Summary's `node_count`/`edge_count` columns are dropped (canvases are loaded lazily now).
- `create_project` (Python + MCP) calls `git_store.ensure_repo` on the new folder.
- `plot_mcp/sketches.py` is now an internal module; only `migrate.py` imports it.

### Removed (breaking)
- `/api/sketches/*` REST endpoints — any external script that hit them needs to move to `/api/projects/*`.
- v0.1 MCP tool wrappers (`list_sketches_tool`, `get_sketch`, `create_sketch_tool`, `update_sketch`, `delete_sketch_tool`). Use the canvas-level equivalents.
- `useSketchHistory` viewer hook.

### Notes
- **Nested git repo.** `.plot/sketches/{id}/.git/` sits inside whatever project directory you're pointing Plot at. git naturally stops at inner `.git/` boundaries, so the parent repo sees `.plot/` as untracked. Recommended: add `.plot/` to your project's top-level `.gitignore`.
- Identity configured per-repo as `user.name=Plot`, `user.email=plot@noory-ai.local` so Plot commits don't inherit your global git identity.
- Undo/redo is in-memory only; tags are the durable history mechanism.

## [0.3.0] — 2026-04-21

### Added
- **Folder-per-project storage** — `.plot/sketches/{id}/` with one JSON file per canvas (`core.json`, `actors.json`, `services-overview.json`, `services-detail/{service_id}.json`). Writing one canvas no longer touches any other. ([`plot_mcp/folder_io.py`](plot_mcp/folder_io.py))
- **v0.1 → v0.2 migration** — `plot_mcp.migrate.migrate_v01_to_v02` (also exposed as the `migrate_v01_sketches` MCP tool). Idempotent; promotes `mission` / `core_values` / `identity` text fields on the core-root into their own nodes; multi-line core-values split into one node per line. Originals rename to `{id}.json.v01.bak`.
- **Canvas-level MCP tools** — `list_projects`, `get_project`, `create_project_tool`, `delete_project_tool`, `rename_project`, `get_canvas`, `update_canvas`, `list_detail_canvases`, `migrate_v01_sketches`. The legacy sketch tools stay available during the transition.
- **Overview ↔ Detail auto-sync** — writing the `services_overview` via `update_canvas` auto-creates a Detail canvas for any new service and archives (does not delete) the Detail of a removed service.
- **Actor_ref picker UI** — dragging "Actor ref" onto the Services canvas opens a modal listing every actor from the Actor canvas; picking one creates a reference node with `ref_actor_id` and a "→ {label}" prefix.
- Inspector shows a read-only `References` pill for `actor_ref` nodes.

### Changed
- Inspector no longer renders `mission` / `core_values` / `identity` text fields on root nodes — those are first-class node kinds now.

### Notes
- The v0.1 viewer (single-file `SketchDoc` + tab-filter) still works. Switching the HTTP layer and viewer to the new canvas-level API is a follow-up; until then, the new tools and folder layout are opt-in via MCP.

## [0.2.0] — 2026-04-21

### Added
- Multi-canvas split — the sketch is now viewed through three tabs (**Core**, **Actors**, **Services**) so each cognitive layer has its own canvas. The underlying `SketchDoc` stays single-file for v0.2; separate canvas storage arrives in a later release.
- **Core canvas** — drops for Mission, Core Value, Identity, and Identity Facet promote what used to be Inspector text fields into structural child nodes of the Core octagon.
- **Services drill-down** — double-click any non-root service in the Overview to enter its Detail view; a breadcrumb at the top navigates back. `?canvas=services&detail=<id>` makes the view deep-linkable.
- **Canvas-aware stencil** — each tab surfaces only the presets it can accept, and `resolveDropTarget` knows the new core-child / identity-facet parenting rules.
- `CanvasDoc` + `CanvasKind` in `plot_mcp/models.py` with per-canvas-kind validators (core: 1 mission + 1 identity; actors: actor-only; services-overview: top-level only; service-detail: requires service_ref matching canvas_id).
- Expanded `NodeKind`: `mission`, `core_value`, `identity`, `identity_facet`, `actor_ref`. `SketchNode.ref_actor_id` carries the pointer for Actor→Service references.
- 26 new tests in `tests/test_canvas_doc.py`.

### Changed
- `?canvas=` URL param now carries the active tab; refreshing lands back on the same canvas.
- `SketchSidebar.stencilCanvas` prop switches the presets shown in the stencil.

### Notes
- Backward compatible: existing v0.1 `.plot/sketches/{id}.json` files keep loading; legacy untyped nodes default to the Services tab.
- `SketchDoc`'s old `mission` / `core_values` / `identity` text fields on root nodes remain for round-tripping until the v0.1→v0.2 migration script lands.

## [0.1.0] — 2026-04-20

### Added
- Initial release.
- Schema-free sketch store at `.plot/sketches/{id}.json`.
- Starlette HTTP server on port 5190 with 5 endpoints (list / get / create / put / delete) + WebSocket push.
- FastMCP tool surface: `list_sketches`, `get_sketch`, `create_sketch`, `update_sketch`, `delete_sketch`.
- React Flow 11 viewer with full editing: multi-select, copy/paste, undo/redo, auto-layout (dagre), context menu, MiniMap, Controls, resize, color picker, body markdown modal.
- Claude Code plugin manifest + initial skills (`plot-help`, `plot-new-sketch`, `plot-read-sketch`).
