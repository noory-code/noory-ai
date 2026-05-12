# Plot — NEXT SESSION queue

> **Surfaced automatically by the SessionStart hook
> (`plot/hooks/session_start.py`) at every new session start.**
> When the user invokes a queued item by its trigger keyword, that
> item becomes the active task for the session.

---

## Active queue

### `검증` — v0.15 reset Phases 4 + 5 (cursor sweep + verification gates)

> **Trigger:** user says **"검증"** or **"verification"** or
> **"phase 4"** or **"phase 5"** or **"커서 sweep"** as the first /
> near-first message of a Plot session.
>
> **Filed:** 2026-05-12 by user — Phase 1+2+3 of the v0.15 reset
> shipped this session (D-2026-05-12-B); Phases 4–5 deferred to a
> dedicated next session because they have a different shape (test
> infra + acceptance gates rather than per-kind work).
>
> **Reference:** [D-2026-05-12-B](./DECISIONS.md), the full plan
> in `~/.claude/plans/dazzling-greeting-diffie.md`, and the
> per-phase changelog from v0.14.15 → v0.15.5.

#### Phase 4 — Per-canvas cursor sweep

The user's complaint that fired the v0.15 reset (*"파운데이션에서
사용되는 커서 컨트롤하고 액터나 서비스에서 사용되는 커서 컨트롤이
다릅니다"*) needs an empirical answer now that the reset's structural
half is done. Phase 4 work:

1. **Audit** — file `D-2026-05-13-X` in `DECISIONS.md` listing
   the `getComputedStyle(...).cursor` returns of every meaningful
   target on each of the 4 canvases (Foundation / Actors /
   Services / ServiceDetail). Compare against `docs/CURSOR.md`
   contract (which says all 4 share one cursor table).
2. **Author Playwright sweep** — `viewer/tests/cursor-sweep.spec.ts`
   that mounts each wrapper, hovers (i) empty pane (ii) regular
   node body (iii) anchor body (iv) connection handle (v) edge
   (vi) resize handle, snapshots cursor inventory per canvas, and
   asserts the 4 inventories are identical (modulo the v0.11.4
   anchor-vs-button asymmetry per D-2026-05-11-A).
3. **Extend the static cursor-baseline guard** — `viewer/tests/
   styles-cursor-baseline.test.tsx` should also verify the 4
   wrapper files contain zero `cursor:` strings.
4. Fixture project under `viewer/tests/fixtures/cursor-sweep-project/`
   with `.plot/` seeded via `domain/createBlankNode` so schema
   drift breaks fixture build before the sweep runs.

Expected output: 2 commits (`v0.15.6` author sweep + `v0.15.7`
extend baseline guard + DECISIONS pin).

#### Phase 5 — Verification gates + kill-switch

5 acceptance gates + 2 static guards + 1 kill-switch. All planned
in detail in the plan file's "Phase 5" section. Highlights:

1. **Per-kind Inspector smoke** — extend
   `viewer/tests/inspectors/inspectors.smoke.test.tsx` to exercise
   every one of the 15 kinds with a synthetic node and assert
   chrome + per-kind body render without `console.error`.
2. **Entity round-trip** — already mostly there in
   `viewer/tests/domain/round-trip.test.ts` and
   `plot/tests/test_node_models.py`; consolidate.
3. **Per-canvas cursor sweep** — Phase 4's spec.
4. **Static guard: `no-god-union-import.test.ts`** — fail the
   build if any `viewer/src/canvases/` `.tsx` matches
   `node.kind === "X"` god dispatch outside the
   `inspectors/` registry's allowlist.
5. **LOC budget guard** — `viewer/tests/loc-budget.test.ts`
   asserting `App.tsx ≤ 400`, wrapper canvases ≤ 150, per-kind
   inspector ≤ 250, per-kind node renderer ≤ 100,
   `BaseInspector ≤ 200`, `BaseNode ≤ 250`.
6. **Kill-switch** — `plot/hooks/pre_commit_gate.py` adds
   `reset_complete_check` that verifies (a) Pydantic
   ``SketchNode`` is the 15-way union, (b) viewer
   ``SketchNode.tsx`` absent, (c) `SketchInspector.tsx` absent,
   (d) zero `doc.canvas_kind` in `viewer/src/canvases/sketch/`,
   (e) all five Phase 5 acceptance gates green. Active for
   v0.15.x; removed at v0.16.0.

Expected output: 3 commits (`v0.15.8` smoke + round-trip
consolidation, `v0.15.9` static guards, `v0.16.0` kill-switch +
final DECISIONS pin + SPEC update + ARCHITECTURE Domain section).

#### What "v0.15 reset complete" means at v0.16.0

- Server: 15-way Pydantic union, no god class, schema_export for
  all 15 kinds, parity test pinning TS↔Pydantic field names.
- Viewer: 15 entity classes, 15 per-kind inspectors, 15 per-kind
  node renderers, 4 canvas wrappers, no god ``SketchInspector.tsx``
  or ``SketchNode.tsx`` on disk, no canvas_kind switches in
  transforms, no ``"sketch"`` god type.
- Tests: 100+ viewer + 200+ server, all green.
- ``pre_commit_gate.reset_complete_check`` returning OK on every
  commit (then retired).

---

### `구조 리셋` (COMPLETED Phase 1+2+3 in this session)

> **Completed Phases 1–3:** 2026-05-12 across v0.14.15 → v0.15.5
> (23 commits). Phases 4–5 → see active `검증` queue above.
>
> **Reference:** [D-2026-05-12-B](./DECISIONS.md).
>
> **What landed in Phase 1+2+3 this session:**
>
> - **Phase 0** v0.14.15 — pre-existing 17 ruff/mypy debts → 0.
> - **Phase 1.1–1.3** v0.14.16–18 — server-side Pydantic 15-way
>   discriminated union, schema_export extended to all 15 kinds,
>   god ``SketchNode`` class deleted server-side.
> - **Phase 2.0–2.10** v0.14.19–v0.15.0 — viewer domain layer
>   (15 entity classes + Canvas + parseEntity + DomainParseError
>   + createBlankNode factory), per-kind Inspector framework
>   (15 inspectors + BaseInspector + KindInspector + 4 shared
>   pieces in `inspectors/shared/`), atomic flip of
>   ``viewer/src/types.ts`` god ``SketchNode`` interface to
>   discriminated union, ``SketchInspector.tsx`` (1491 LOC)
>   deleted from disk.
> - **Phase 3.1–3.5** v0.15.1–5 — 15 per-kind React Flow node
>   renderers (BaseNode + per-kind wrappers + NODE_RENDERERS
>   registry), 4 canvas wrappers (FoundationCanvas / ActorsCanvas
>   / ServicesCanvas / ServiceDetailCanvas), 4 ``canvas_kind``
>   switches stripped from transforms (replaced by 4
>   wrapper-supplied props), ``SketchNode.tsx`` (245 LOC)
>   deleted from disk.
>
> **Verification status:** server 214/214 tests + ruff/mypy clean;
> viewer 106/106 tests + tsc clean. No user-visible behaviour
> change. The "no god object" rule is now enforced end-to-end.

(Original "구조 리셋" trigger text — problem statement, code
evidence, Phase A–F plan, done criteria, skills shortlist — is
preserved in git history at v0.14.14 and in the plan file
`~/.claude/plans/dazzling-greeting-diffie.md`.)

---

## How this file works

- The `SessionStart` hook (`plot/hooks/session_start.py`) reads
  this file at every session start and prepends each `### TRIGGER`
  heading to the assistant's context.
- The assistant then watches for the user's next message. If it
  contains a trigger keyword, the assistant executes the matching
  item.
- After completion, the assistant **moves the item to the
  "Completed" section below** with the date + commit hash, instead
  of deleting it. This preserves the audit trail.

---

## Completed

### `다음` — Architectural review: cursor / auto-layout coupling

> **Completed:** 2026-05-10 in v0.14.3.
> **Outcome:** [D-2026-05-11-C](./DECISIONS.md).
> Pre-commit gate + static guard + plot-verifier default sweep
> shipped. (Full diagnosis preserved in the file's prior revision
> and the D-entry.)
