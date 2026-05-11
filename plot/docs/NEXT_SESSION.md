# Plot — NEXT SESSION queue

> **Surfaced automatically by the SessionStart hook
> (`plot/hooks/session_start.py`) at every new session start.**
> When the user invokes a queued item by its trigger keyword, that
> item becomes the active task for the session.

---

## Active queue

### `구조 리셋` — v0.15.0 domain layer + entity classes + componentisation

> **Trigger:** user says **"구조 리셋"** or **"v0.15"** or
> **"도메인"** or **"엔티티"** as the first / near-first message
> of a Plot session.
>
> **Filed:** 2026-05-12 by user (multiple messages).
>
> **Reference:** [D-2026-05-12-B](./DECISIONS.md) (this entry +
> its plan) and full backlog detail in
> [`memory/project_plot_next_session.md`](../../.claude/projects/-Users-woogis-Workspace-repo-noory-ai/memory/project_plot_next_session.md).

#### The problem (user direct quotes 2026-05-12)

- *"파운데이션에서 사용되는 커서 컨트롤하고 액터나 서비스에서
  사용되는 커서 컨트롤이 다릅니다. 코어 원칙이 지켜지고
  있지않아요."*
- *"엔티티 정의도 안되어 있구요."*
- *"기본을 못하고 있는겁니다."*
- *"코드 재활용 할 수도 없게 해뒀어요. JSON을 직접 건드리고
  있는게 아닌지 모르겠네요. fromJson, toJson 같은걸 쓰고
  클래스를 코드로 만들어서 개념화해야 했다."*
- *"도메인 레이어 설계가 제대로 되어 있는지도 모르겠구요."*

#### Code evidence (collected 2026-05-12)

| Evidence | Status |
|---|---|
| `viewer/src/types.ts:174` comment | Self-admits god interface |
| `grep -rE "fromJson\|toJson\|parse(\|serialize("` viewer/src | 0 hits |
| `grep -rE "^class \|^export class "` viewer/src | 0 hits |
| `find viewer/src -type d \| grep -iE "domain\|entit\|model"` | No domain dir |
| `types.ts` 305 LOC | 100% `type` / `interface`, zero methods |
| `SketchInspector.tsx` | 1422 LOC; branches on `kind` for every typed field |
| `SketchCanvas.tsx` | 359 LOC; one god component for 3 canvases |

#### Plan (do all phases in order; each phase = its own
multi-commit plan; viewer green at every phase boundary)

**Phase A — Domain entity classes.** New
`viewer/src/domain/{Mission,CoreValue,Identity,Actor,ActorRef,
Service,Category,MissionRef,ValueRef,IdentityRef,Metric,Step,
Rule,Content,Project}.ts`. Each is a real `class` with
fromJson / toJson / invariants / kind-specific fields only.
`domain/SketchNode.ts` = discriminated union of the 15 classes.
`domain/CanvasDoc.ts` = `Canvas` class with `findById` etc.

**Phase B — Server alignment.** Verify
`plot_mcp/models.py` Pydantic discriminated union matches 1:1.
Decide manual vs generated TS types.

**Phase C — Inspector kind fan-out.** Split
`SketchInspector.tsx` (1422 LOC) into per-kind files
(`inspectors/MissionInspector.tsx` etc.) on top of domain
classes.

**Phase D — Canvas componentisation.**
`FoundationCanvas.tsx`, `ActorsCanvas.tsx`,
`ServicesCanvas.tsx`, `ServiceDetailCanvas.tsx` as separate
top-level components. No more runtime `canvas_kind` switch.

**Phase E — Cursor / interaction contracts per canvas.**
Per-canvas Playwright cursor sweep returns identical
inventories.

**Phase F — Verification.** Per-canvas cursor sweep + per-kind
Inspector smoke + entity-shape round-trip test.

#### Skills / rules to consider (user-allowed 2026-05-12)

Discuss at session start, create only those that prove their
weight during the work:

1. `plot/skills/plot-entity-template/` — per-kind entity class
   boilerplate.
2. `plot/skills/plot-domain-design/` — Plot-specific DDD
   guidance.
3. Pre-commit hook `no-god-import` — block god `SketchNode`
   import in new viewer files once Phase A lands.
4. Vitest entity-shape round-trip test.
5. `plot/CLAUDE.md` anti-pattern row — *"Treating raw JSON as
   domain entity (no fromJson boundary)."*

#### Done criteria

Session-by-session: each phase boundary leaves Plot green +
tests passing. The whole reset is done when:

- `viewer/src/domain/` exists with 15 per-kind entity classes
  + Canvas / SketchNode union.
- `grep -rE "^class \|^export class "` in `viewer/src/domain` →
  ≥ 15 hits (one per kind).
- All UI components import per-kind classes, not god
  `SketchNode`.
- Per-canvas cursor sweeps return identical, allow-listed
  inventories.
- `SketchInspector.tsx` ≤ 300 LOC (chrome + dispatch only) or
  removed entirely.
- `SketchCanvas.tsx` removed or reduced to a shared shell used
  by the 4 per-canvas components.

#### What this reset does NOT do

- Does not change Plot UI / behaviour from the user's seat.
  Same canvases, same nodes, same i18n. Internal structure
  only.
- Does not re-open the old backlog items (i18n audit, owner
  field, Mermaid, …). Those wait until the reset lands.

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
