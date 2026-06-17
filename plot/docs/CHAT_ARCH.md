# Plot — in-app chat architecture

> Status: **red-teamed + decisions committed**, 2026-06-15 (verdict was
> revise-first; revised below). Builds on D-2026-06-13-H (per-canvas scope) +
> D-2026-06-14-B (claude re-included). Implementation proceeds by the sequence
> below (Layer 2 first); each layer pins to SPEC/DECISIONS as it lands. Pairs
> with VISION.md (3-phase cycle) and DOMAIN.md (AICollaboration cross-cut).

## The ask (user, 2026-06-14)

> "각 캔버스마다 있는 채팅창은 각 캔버스에 맞게 동작을 해야할 것 같아요."

Concretely:
1. Foundation and Actors each have **one chat**, with context matching that
   canvas.
2. Services: **one chat per feature detail canvas**, with that detail's context.
   (As of `D-2026-06-17-D` the detail canvas drills from a **feature**, not a
   service — so this is per-**feature** detail; the service itself shows an
   inspector and no longer drills.) The services overview canvas also gets its
   own chat (cross-service planning).
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

> **⚠ Pending (2026-06-18, doc-sync).** `D-2026-06-17-D/G` rewired the drill: the
> detail canvas now opens from a **feature**, not a service (the service shows an
> inspector and no longer drills). Whether the per-instance detail **thread** therefore
> keys per-**feature** instead of per-**service** (`service_detail:<service_id>`) is
> **not yet pinned** — the scope/wire identifiers in this Layer 1 (and in the Decisions
> + Implementation-sequence sections below) still use the service-keyed form. **Resolve
> with the AI-chat playbook work (ROADMAP 5.10);** do not treat the service-keyed keys
> as final.

- Engine session registry key becomes `(plot_root, provider, scope)` where
  `scope` is a `CanvasKey | "project"` string (already the shape, just widening
  the `service_detail` member to carry the id). **D-2026-06-16-G:** `plot_root`
  is resolved from the **active project's** path (the viewer keys `ChatDock` on
  `activeProjectPath`), so the chat is per **(project × canvas)** — in a
  monorepo workspace each project owns its own threads + provider/model in its
  `.noory/plot`. (Originally workspace-wide; refined to per-project.)
- Rationale for NOT collapsing to a single chat: a single thread mixes
  unrelated contexts (foundation discovery vs one service's flow), breaking the
  CLI's resumed-session continuity and confusing the agent. Per-area threads
  keep each conversation coherent.

### Layer 2 — Context injection (what the agent knows each turn)

Every chat turn carries a **context preamble** built from live viewer state:
- **Active canvas** (the scope).
- **Current selection** — ALL selected node ids + their kind + their data
  (user: "다 연동"). Multi-select supported.

> **Extended by `D-2026-06-17-L` (2026-06-17).** The envelope also carries (3) an
> **upstream-canvas SUMMARY** (essence + key nodes of canvases earlier in the
> Foundation→Actors→Services→Feature→Entities order — not a full dump) and (4) the
> **entity registry** (names + one-line, for strong dedup + references); deeper
> detail is fetched on demand. **Delivery = CAG-first:** the stable project skeleton
> is a **prompt-cached prefix**; active-canvas detail + selection + message are the
> dynamic suffix. **RAG only at scale** (skeleton exceeds budget / deep content /
> cross-project). Core of the AI chat playbook (ROADMAP 5.10).

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

### Layer 3 — Per-canvas system framing (canvas-appropriate behaviour) — IN-APP ONLY

Each scope maps to a VISION phase, which sets the agent's framing:

| Canvas | VISION phase | Chat framing |
|---|---|---|
| Foundation | Discovery | Help surface / sharpen the essence |
| Actors / Services | Planning | Design the value-creation machinery (the Services overview is the category→service→feature drill layer per `D-2026-06-17-D`; the feature drill target is the Feature canvas below) |
| Feature (feature detail) | Execution | Break the plan into concrete steps |

> **D-2026-06-16-H — active coach, not topic-setter.** The phase mapping above is
> the *minimum* (which phase). The per-canvas guide is **active**: it makes the
> user's own AI a high-level discussion partner that (1) organises that canvas's
> concepts + their relationships and (2) proposes higher-order concepts /
> methodologies the user has not considered — not a passive blank-form filler.
> Rationale: Plot's purpose (2026-06-16 big-picture discussion) is to build good
> **context for the AI to work** and **accelerate the human's thinking**; the
> canvas (structured concepts + definitions) serves both, which requires an active
> partner per canvas. **Not yet implemented** — current Layer 3 ships only the weak
> topic-setter preamble.

**Scope honesty (red-team A1):** Layers 2–3 make the **in-app** chat
canvas-aware. The *primary* path is MCP (the user's own agent), which does NOT
receive this framing/selection yet — that's a named follow-up (a viewer→engine
selection bridge + an MCP resource). This doc does not claim the primary path
is covered.

Framing is delivered as a **preamble prepended to the CLI message**, configured
in **code constants** (committed below — `.noory/`-editable framing is YAGNI
until asked).

## Relation to other tracks

- **Settings / model selection (D-2026-06-14-B follow-up):** the per-scope
  thread + model choice live together. Model selection is a separate Settings
  surface (2-tier: global `~/.noory/plot/settings.json` + per-workspace). The
  chat structure here is orthogonal but should leave room for per-scope model
  override later.
- **MCP path (primary):** Layers 1–2 describe the **in-app** chat. The MCP
  path already gives the external agent canvas access via tools; selection
  awareness over MCP is the deferred extension of Layer 2.

## Decisions (committed 2026-06-15, post red-team)

1. **Scope parity contract.** `ChatScope` widens to `CanvasKind ∪ {project}`,
   with `service_detail` the one parametric member (`service_detail:<id>`).
   `test_chat_scope_parity.py` asserts the **base member set** = Python
   `ChatScope` prefixes == TS `CanvasKind ∪ {project}`, and that
   `service_detail` accepts an id suffix.
2. **Service-detail thread lifecycle.** Keyed by `service_id` (stable across
   rename). On delete, the thread is **left orphaned** (in-memory only; cleared
   on engine restart) — no eager cleanup. An unresolved id falls back to the
   `services` scope (see 6).
3. **Selection preamble cap.** Send up to **20** selected nodes as
   `{id, kind, label}`; beyond that, send the count + ids only. Full node data
   is the agent's to fetch via MCP if needed (keeps the prompt bounded).
4. **Layer 3 config = code constants.** No `.noory/`-editable framing yet.
5. **Selection freshness = per-turn snapshot** at send time. No live sync.
6. **project scope context.** The `project` thread injects **no canvas/selection
   context** (it's explicitly cross-canvas). An unresolved `service_detail:<id>`
   degrades to `services`.

## Implementation sequence (red-team A8 — three steps, not one)

1. **Layer 2 — context injection (do FIRST; cheapest high-value).** Viewer
   lifts the active canvas's selection → sends `{scope, selection}` on
   `/api/chat/send`; engine prepends a preamble (canvas + selected nodes, cap
   20) to the CLI message. In-app only.
2. **Layer 1 — per-instance scope.** Widen `service_detail` to
   `service_detail:<id>`; engine session key + viewer routing + parity (1).
3. **Layer 3 — per-canvas framing.** Code-constant preamble per scope.

## Tradeoff named (red-team A7)

Per-area threads keep each conversation coherent but **fragment continuity** —
a fresh `service_detail:<id>` thread has no memory of the foundation discussion
that motivated the service. Layer 2 selection injection partly mitigates (the
agent knows *what* is selected, not *why*). A future cross-thread "essence
summary" preamble could close the gap; not built now.
