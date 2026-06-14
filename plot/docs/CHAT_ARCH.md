# Plot — in-app chat architecture (DRAFT for red-team)

> Status: **draft proposal**, 2026-06-14. Not yet pinned to SPEC/DECISIONS.
> Builds on D-2026-06-13-H (per-canvas scope) + D-2026-06-14-B (claude
> re-included). To be adversarially reviewed (plot-design-red-team) before
> any code. Pairs with VISION.md (3-phase cycle) and DOMAIN.md
> (AICollaboration is cross-cutting).

## The ask (user, 2026-06-14)

> "각 캔버스마다 있는 채팅창은 각 캔버스에 맞게 동작을 해야할 것 같아요."

Concretely:
1. Foundation and Actors each have **one chat**, with context matching that
   canvas.
2. Services: **one chat per service-detail canvas** (i.e. per service), with
   that service's context. The services overview canvas also gets its own
   chat (cross-service planning).
3. When a node is selected, the chat should **know the selection** — "everything
   selected in the app should be synced so it's natural to talk about it."

## Design: three independent layers

The ask decomposes into three layers that compose cleanly. They are NOT
either/or.

### Layer 1 — Thread partitioning (how many conversation histories)

**Thread = `CanvasKey` + a shared `project` scope.**

| Scope key | Thread |
|---|---|
| `foundation` | Foundation discovery |
| `actors` | Actors design |
| `services` | Services overview — cross-service planning |
| `service_detail:<service_id>` | One specific service's design/execution |
| `project` | Cross-canvas / workspace-wide |

This **refines D-2026-06-13-H**: today `service_detail` is a single shared
scope; here it becomes **per-service-instance**. The scope set then equals
`CanvasKey | "project"` — identical to the viewer's existing canvas-cache key
(`viewer/src/types.ts` `CanvasKey`), so chat threads and canvas state key the
same way (one mental model).

- Engine session registry key becomes `(workspace, provider, scope)` where
  `scope` is a `CanvasKey | "project"` string (already the shape, just widening
  the `service_detail` member to carry the id).
- Rationale for NOT collapsing to a single chat: a single thread mixes
  unrelated contexts (foundation discovery vs one service's flow), breaking the
  CLI's resumed-session continuity and confusing the agent. Per-area threads
  keep each conversation coherent.

### Layer 2 — Context injection (what the agent knows each turn)

Every chat turn carries a **context preamble** built from live viewer state:
- **Active canvas** (the scope).
- **Current selection** — ALL selected node ids + their kind + their data
  (user: "다 연동"). Multi-select supported.

The viewer already tracks selection (`SketchCanvas` `selectedIds`, App
`selectedNodeId`). On `POST /api/chat/send` the viewer includes
`{scope, selection: [{id, kind, ...fields}]}`; the engine prepends a short
preamble to the CLI prompt, e.g.:

> Context: canvas=`foundation`. Selected: `core_value "신뢰"` { … }.
> User message: …

So the user can say "이거 고쳐줘" and the agent resolves "이거" = the selected
node. A **selection chip** in the dock shows what the next message will
reference (Clear Feedback — the user sees what the chat "sees").

This layer is independent of threading and is the high-value, low-cost win.
**In-app first** (engine-side preamble). The MCP path (external agent knowing
selection) needs a viewer→engine selection bridge + an MCP resource/tool —
deferred.

### Layer 3 — Per-canvas system framing (canvas-appropriate behaviour)

Each scope maps to a VISION phase, which sets the agent's framing:

| Canvas | VISION phase | Chat framing |
|---|---|---|
| Foundation | Discovery | Help surface / sharpen the essence |
| Actors / Services | Planning | Design the value-creation machinery |
| Service-Detail | Execution | Break the plan into concrete steps |

How the framing is delivered (preamble text vs system prompt vs suggested
prompts) and **where it's configured** (code constants vs `.noory/plot/`
user-editable) is an open question for red-team — see below.

## Relation to other tracks

- **Settings / model selection (D-2026-06-14-B follow-up):** the per-scope
  thread + model choice live together. Model selection is a separate Settings
  surface (2-tier: global `~/.noory/plot/settings.json` + per-workspace). The
  chat structure here is orthogonal but should leave room for per-scope model
  override later.
- **MCP path (primary):** Layers 1–2 describe the **in-app** chat. The MCP
  path already gives the external agent canvas access via tools; selection
  awareness over MCP is the deferred extension of Layer 2.

## Open questions (for plot-design-red-team)

1. **Scope as a parametric string vs enum.** Widening `ChatScope` from a fixed
   5-member literal to `CanvasKey | "project"` (parametric `service_detail:<id>`)
   breaks the current parity test (`test_chat_scope_parity.py` asserts a fixed
   set). What's the new parity contract? (Likely: the prefix set + a
   `service_detail:` pattern.)
2. **Service-detail thread lifecycle.** A service can be renamed/deleted. Does
   its thread persist by `service_id` (stable) — yes — but what happens to the
   thread when the service is deleted? Orphan cleanup vs keep.
3. **Selection preamble size.** "All selected nodes + data" could be large
   (multi-select of N nodes). Cap? Summarise? Send ids + let the agent fetch
   via MCP?
4. **Layer 3 config location.** Per-canvas framing in code (YAGNI, ships now)
   vs `.noory/plot/` user-editable (flexible, more surface). Start where?
5. **Selection freshness.** Per-turn snapshot at send time (simple) vs live
   sync (the agent always has current selection even mid-conversation).
6. **project scope + selection.** On the `project` thread the active canvas is
   ambiguous — what canvas/selection context does it inject?
