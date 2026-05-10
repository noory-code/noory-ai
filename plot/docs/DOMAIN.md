# Plot — DOMAIN model (bounded contexts, ubiquitous language, dependency direction)

> **Read after [`VISION.md`](./VISION.md).** This file translates the
> three-phase essence cycle (Discovery / Retention / Execution) into
> bounded contexts that the code is organised around. When in doubt
> about *where* a piece of behaviour belongs, this file decides.

---

## Why this file exists

Cursor took six rounds across v0.13.3 → v0.13.10 because every fix had
to pick "where does this rule live?" without a domain map. Each round
chose a different ad-hoc location — CSS file / component / hook — and
the next bug surfaced in a slightly different ad-hoc location. The
override stack itself became the regression engine (see
[D-2026-05-10-C](./DECISIONS.md), [D-2026-05-10-F](./DECISIONS.md)).

DOMAIN.md prevents the recurrence by giving every concern an explicit
home. Before adding new behaviour, the implementer reads this file,
identifies the bounded context, and places the code there — not where
it's most convenient at the moment.

---

## Bounded contexts (5)

Each context corresponds to a phase of the [`VISION.md`](./VISION.md)
cycle plus one cross-cutting context for the AI collaboration that
threads through every phase.

```mermaid
flowchart LR
  EssenceDiscovery --> EssenceRetention
  EssenceRetention --> EssencePlanning
  EssencePlanning --> EssenceExecution
  EssenceExecution -.feedback / drill-back.-> EssenceDiscovery
  AICollaboration -.cross-cutting.-> EssenceDiscovery
  AICollaboration -.cross-cutting.-> EssenceRetention
  AICollaboration -.cross-cutting.-> EssencePlanning
  AICollaboration -.cross-cutting.-> EssenceExecution
```

### 1. EssenceDiscovery — finding the essence
- **VISION phase:** Discovery (#1)
- **Surfaces:** Foundation canvas (mission / core_value / identity nodes),
  the Inspector's typed-text fields, the per-node `foundation/{kind}-{id}.md`
  templates.
- **Owns:** prompts that elicit the user's essence-language, the section
  schemas that ensure each typed field is captured, the ⚠ badge that
  flags missing sections.
- **Does NOT own:** how the discovered essence is rendered on later
  canvases (that's Retention) or how services derived from it are
  designed (that's Planning).
- **Code home (current):** `plot_mcp/foundation/`,
  `viewer/src/canvases/SketchInspector.tsx` (Foundation sections),
  `plot_mcp/templates/foundation/`.

### 2. EssenceRetention — keeping it visible
- **VISION phase:** Retention (#2)
- **Surfaces:** the synthetic project anchor injected on every primary
  canvas (Foundation / Actors / Services), the Foundation refs
  (`mission_ref`, `value_ref`, `identity_ref`) that point back from
  Actors / Services nodes, the cross-canvas link semantics.
- **Owns:** anchor placement (`ProjectDoc.anchors[canvasKind]`), anchor
  visual differentiation (border, never outline — see D-2026-05-08-G),
  the anchor mutation routing through `onAnchorChange` (never through
  `onDocChange`), the read-side `*_ref` resolution.
- **Does NOT own:** anchor's edit Inspector (that's Discovery's typed
  text), anchor click behaviour (open question per SPEC).
- **Code home (current):** `viewer/src/canvases/sketch/useNodesMemo.ts`
  (anchor injection), `viewer/src/canvases/sketch/applyAnchorChange.ts`,
  `plot_mcp/projects/anchors.py`.

### 3. EssencePlanning — designing the value-creation machinery
- **VISION phase:** Execution (#3, planning portion)
- **Surfaces:** Actors canvas (who participates), Services canvas
  (which value-creation hubs exist), the value-flow toggle that
  colours edges by `value_form`.
- **Owns:** actor / service / category kinds, the `gives` / `receives`
  fields, the `target_side` classification, the value-flow visual,
  the auto-layout algorithm (the "see the structure of the planned
  essence" gesture).
- **Does NOT own:** how individual services are decomposed (that's
  Execution / Service-Detail), how the user's free-form connections
  become formal exchange relationships (that's a future skill).
- **Code home (current):** `viewer/src/canvases/sketch/autoLayout.ts`,
  `viewer/src/canvases/sketch/useEdgesMemo.ts`,
  `plot_mcp/canvases/actors/`, `plot_mcp/canvases/services/`.

### 4. EssenceExecution — turning plans into reality
- **VISION phase:** Execution (#3, build portion)
- **Surfaces:** Service-Detail (modal canvas per service), the steps /
  metrics / rules / contents primitives, the MCP tools (`read`,
  `extend`, `reshape`) that let Claude operate on sketches as a
  collaborator while writing actual code.
- **Owns:** Service-Detail canvas, composition primitives (step,
  metric, rule, content), `actor_ref` decomposition, the MCP tool
  surface that exposes sketch graphs to Claude Code agents.
- **Does NOT own:** the actual application code being built (that
  lives outside Plot). Plot's job ends at "Claude has the right
  context to write the code."
- **Code home (current):** `plot_mcp/canvases/service_detail/`,
  `plot_mcp/server.py` (MCP tool registration),
  `viewer/src/canvases/sketch/SketchModals.tsx` (drill modal).

### 5. AICollaboration — cross-cutting (interview / suggest / verify)
- **VISION phase:** all of them (cross-cutting)
- **Surfaces:** the MCP server entry points, the Sampling-driven
  interview flows (future), the auto-suggest features (future), the
  Plot-side skill manifests in `plot/skills/` and the agent
  definitions in `plot/agents/`.
- **Owns:** the *patterns* by which Claude participates — when to
  interview, when to anchor, when to propose, when to verify — and
  the Plot-side enforcement of those patterns (skills + hooks +
  sub-agents in `plot/`).
- **Does NOT own:** the user's choice of model, the conversation
  transcript (that's Claude Code's), the canvas data itself
  (that's owned by the other four contexts).
- **Code home (current):** `plot/skills/`, `plot/.claude-plugin/plugin.json`,
  `plot_mcp/server.py` (tool surface). Adds `plot/hooks/` and
  `plot/agents/` in v0.14.0.

---

## Ubiquitous language

Words mean **exactly one thing** across Plot code, docs, commits, and
conversation. When the same word means different things in different
contexts, rename the loser.

| Word | Meaning in Plot | Common confusion to avoid |
|---|---|---|
| **Node** | A graph entity in `CanvasDoc.nodes[]` (`SketchNode`). | Not a DOM node, not a React Flow internal node, not a `ReactFlow.Node` (which we call **rf-node** if it must be referenced). |
| **rf-node** | The React Flow runtime representation (`{ id, position, data }`). | Distinct from our `SketchNode`. The `useNodesMemo` hook is the boundary that converts one to the other. |
| **Anchor** | The synthetic project node injected by `useNodesMemo`, identified by `PROJECT_ANCHOR_ID` (`__project_anchor__`). | Not stored in `canvas.json`. Position lives in `ProjectDoc.anchors[canvasKind]`. |
| **Canvas** | One of the four canvas kinds (`foundation`, `actors`, `services`, `service_detail`). | Not the HTML canvas element. |
| **Edge** | A connection in `CanvasDoc.edges[]` (`SketchEdge`). | Not the React Flow `rf-edge` (the runtime form). |
| **Service** | A `kind: "service"` node — the value-creation hub. | Not "REST service" or "microservice." |
| **Actor** | A `kind: "actor"` node — a participant in services. | Not a software actor (Akka-style). |
| **Essence** | The user's articulated mission / core_value / identity, captured on Foundation. | Not a generic "vision" or "purpose." Specifically what Foundation surfaces. |
| **Hub** | A service node, per PHILOSOPHY P5. | Synonym for "service node," not for "anchor." |
| **Discovery / Retention / Execution** | The three phases of the VISION cycle. | Not generic software-development phases. |
| **Drill** | Drill into a service to open its Service-Detail canvas. | Not "drill down" in a generic UI sense. |

---

## Entities vs value objects

| Concept | Entity / VO | Lives in | Identity by |
|---|---|---|---|
| `Project` | Entity | `ProjectDoc` | `id` (uuid) |
| `Canvas` | Entity | `CanvasDoc` | `(project_id, canvas_kind)` |
| `Node` (`SketchNode`) | Entity | `CanvasDoc.nodes[]` | `(canvas_id, id)` |
| `Edge` (`SketchEdge`) | Entity | `CanvasDoc.edges[]` | `(canvas_id, id)` |
| `AnchorPlacement` | Value Object | `ProjectDoc.anchors[canvasKind]` | by-value (no identity) |
| `Shape` | Value Object | enum on `SketchNode.shape` | by-value |
| `ValueForm` | Value Object | enum array on `SketchEdge.value_form` | by-value |
| `MdWarning` (string) | Value Object | `SketchNode._md_warnings[]` | by-value |
| `Direction` (T/R/B/L) | Value Object | `autoLayout.ts` runtime only | by-value |

---

## Dependency direction

Code in any context may depend on code in **lower-numbered** contexts
only. This keeps the cycle's drill-back semantics correct (Execution can
read Discovery; Discovery cannot reach into Execution).

```mermaid
flowchart LR
  EssenceDiscovery -->|read by| EssenceRetention
  EssenceDiscovery -->|read by| EssencePlanning
  EssenceDiscovery -->|read by| EssenceExecution
  EssenceRetention -->|read by| EssencePlanning
  EssenceRetention -->|read by| EssenceExecution
  EssencePlanning -->|read by| EssenceExecution
  AICollaboration -->|may import any| EssenceDiscovery
  AICollaboration -->|may import any| EssenceRetention
  AICollaboration -->|may import any| EssencePlanning
  AICollaboration -->|may import any| EssenceExecution
```

**Forbidden imports (compile-time / review-time):**
- `EssenceExecution` files importing from a sibling `EssenceExecution`
  feature without going through `EssencePlanning` or
  `EssenceRetention` first — this would couple two execution paths
  through the wrong layer.
- `EssenceDiscovery` reading `EssencePlanning` data — Foundation must
  not depend on what services exist; if it must, route through
  Retention.

---

## Current code-to-domain map (gap list)

This is where today's code violates the model. Each row is a refactor
candidate with explicit cost and benefit. Refactors here are
prioritised in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

| Where | Concern | Currently lives in | Belongs in | Severity |
|---|---|---|---|---|
| Anchor render | EssenceRetention | `viewer/src/canvases/sketch/useNodesMemo.ts` (mixed with regular node transform) | `EssenceRetention` (own module) | Med — works today; separation would clarify |
| Auto-layout algorithm | EssencePlanning | `viewer/src/canvases/sketch/autoLayout.ts` | `EssencePlanning` ✓ | None — already correct |
| Cursor SSOT | Cross-cutting (visual contract for the Discovery / Retention surface) | `viewer/src/styles.css` + `docs/CURSOR.md` | OK as-is — visual contract has no natural domain home | None |
| MCP tool registration | EssenceExecution + AICollaboration | `plot_mcp/server.py` | OK — tool surface IS the boundary | None |
| Inspector typed-text forms (Foundation) | EssenceDiscovery | `viewer/src/canvases/SketchInspector.tsx` (1422 LOC, mixed kinds) | `EssenceDiscovery` (Foundation slice) + `EssencePlanning` (Actors/Services slice) | High — the SI split is on the architecture roadmap |
| Service-Detail modal | EssenceExecution | `viewer/src/canvases/sketch/SketchModals.tsx` | `EssenceExecution` ✓ | Low — colocated with other modals; acceptable |
| Foundation refs (`mission_ref`, etc.) | EssenceRetention (read side) | scattered across `useNodesMemo`, picker components | `EssenceRetention` (own module) | Med — scattered references are fragile |

---

## Process — using this file

When implementing a feature or fixing a bug, apply this checklist:

1. **Re-read [VISION.md](./VISION.md)'s first sentence.**
2. **Identify the phase** (Discovery / Retention / Planning / Execution
   / cross-cutting AICollaboration).
3. **Look up the bounded context** in this file's "Bounded contexts" section.
4. **Check the Code home** for that context. Add to existing files
   there; create a new file in that context's directory if no fit
   exists.
5. **Avoid forbidden imports** (per the dependency direction rules).
6. **Update this file's "Current code-to-domain map"** if the change
   moves an existing concern into its proper context (or moves it
   away from one — note as a regression to be paid back).

---

## When this file changes

DOMAIN.md changes when:
- A new bounded context is needed (rare; should be tied to a major
  VISION update).
- An existing context's responsibility is genuinely re-scoped (also
  rare; record as a `D-YYYY-MM-DD-X` decision).
- The current code-to-domain map gains or loses entries (frequent;
  bookkeeping).

A typo / clarification edit does not need a decision id, but it does
need to keep the dependency-direction diagram and the ubiquitous
language table internally consistent.
