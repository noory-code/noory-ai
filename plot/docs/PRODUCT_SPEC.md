# Plot — Product Spec

> **Source:** user-provided product brief, 2026-05-11.
>
> **Position in the doc set:** this file captures **product-level
> decisions** (who Plot is for, what platforms, what business model,
> what's in MVP). It sits **above** [`VISION.md`](./VISION.md) — VISION
> is the essence; this file is how the essence becomes a shippable
> product.
>
> **Read order on session start:**
> 1. [`VISION.md`](./VISION.md) — the essence.
> 2. **This file** — product framing.
> 3. [`DOMAIN.md`](./DOMAIN.md) — bounded contexts.
> 4. [`SPEC.md`](./SPEC.md), [`CONCEPTS.md`](./CONCEPTS.md), etc.

---

## 1. Overview

A mindmap-based planning tool. Two-sided goal:

- **For humans:** keep direction visible so the user does not drift.
- **For agents:** define a paradigm so AI works inside known rails.

Plot is the surface where the two co-draw — the human anchors
direction, the agent fills in supported moves.

## 2. Platforms

| Phase | Host | MCP |
|---|---|---|
| **Now** | Claude Code plugin (`plot/`) | MCP server runs from the plugin (`plot_mcp/`). |
| **Next** | macOS desktop app | MCP server embedded in the app process. |

The desktop app is downstream; no new viewer / data model work is
required to enable it. The current React Flow viewer ships as a
webview; the Python MCP server ships as an embedded process.

## 3. Business model

- **Individuals:** free.
- **Enterprise:** paid. Surface = collaboration + permissions +
  security. Detailed design deferred (see §10 Future).
- **Growth model:** PLG — individual adoption → team / org spread.

## 4. Tech stack

| Layer | Tech | Owner doc |
|---|---|---|
| Canvas | React Flow | [`ARCHITECTURE.md`](./ARCHITECTURE.md) |
| Source of truth | JSON | [`CONCEPTS.md`](./CONCEPTS.md) |
| Free-text rendering | Markdown | [`SPEC.md`](./SPEC.md) §Foundation |
| Diagram rendering | Mermaid | (queued for Service-Detail visualisation) |
| Agent connection | MCP | [`DOMAIN.md`](./DOMAIN.md) AICollaboration |

## 5. Data structure principles

- **JSON is the source of truth.** Every persisted shape lives in
  JSON files under `.plot/{project}/`.
- **Free-text fields → Markdown.** Realised in v0.13 for Foundation
  (`foundation/{kind}-{slug}.md`).
- **Structured fields → arrays / objects.** Anything that needs
  validation or referential integrity stays in JSON.
- **Every node carries a unique id.** Referential tracking is a
  precondition for §6 Symbols.
- **Every node carries an `owner` field.** Currently unused; reserved
  for the multi-user expansion in §10. (See [`CONCEPTS.md`](./CONCEPTS.md)
  for the existing kind schemas — `owner` must be added before
  multi-user lands.)
- **Export targets:** Markdown, Mermaid, MCP. (MCP "export" = exposing
  the sketch as agent context, not file output.)

## 6. Symbol system

The Figma-symbol concept applied to a graph editor: a node defined
once is referenced everywhere; editing the master updates every
reference at render time.

| Concept | Definition |
|---|---|
| **Symbol** | The canonical node. Lives once. |
| **Instance** | A reference to a symbol. JSON stores only the master id; the renderer resolves the label / colour / typed-text at draw time. |

**Symbol kinds:**

- Mission, Core value, Identity (the Foundation triad).
- Actor.
- Service.

**Service-to-service edges = User journey.** A path
`Service A → Service B → Service C` IS the user journey. Rendered on
the main Services canvas as connection lines. (Today's `services`
canvas edge layer already supports this; the *interpretation* as a
journey is the product framing — see [`SPEC.md`](./SPEC.md) §Edges.)

## 7. Canvas layers (spatial)

Four canvases. Each has a defined audience.

| # | Canvas | Audience | Defines |
|---|---|---|---|
| 1 | **Mission / Core value** | Human | Why the project exists. |
| 2 | **Identity** | Agent | Tone and manner the agent must follow. |
| 3 | **Actor** | Both | Stakeholder map: actors, their relations, pain points. |
| 4 | **Service** | Both | Categorised services. Main canvas = service overview + user-journey edges. Double-click a service → modal canvas with: related actors (symbol references), actor relations / actions / constraints, diagram visualisation, agent-driven definition. |

The current viewer collapses (1) and (2) into a single Foundation
canvas with three kinds (`mission`, `core_value`, `identity`). The
product spec's distinction (human-facing vs agent-facing) is a
*layer concept inside Foundation*, not a separate canvas yet. Split
into two canvases is a separate decision before it can land.

## 8. Core UX pattern — canvas via conversation

Every canvas's first draft comes from an **agent interview**. This
is Plot's onboarding flow AND its primary interaction loop.

**Flow:**

```
empty canvas
  → agent interview
  → human answers
  → canvas draft proposal
  → human approves / edits
```

**Context flow between canvases:**

- Mission interview → results referenced in Actor interview.
- Actor interview → results referenced in Service interview.
- Each prior canvas becomes the input context of the next.

This is the operational form of the VISION cycle (Discovery →
Retention → Execution). See [`VISION.md`](./VISION.md).

## 9. Work-item layer (temporal)

Distinct from the canvases (which are spatial).

- Service canvas → user stories → tasks (derived).
- Each task carries **provenance metadata**: which actor relation it
  came from, which service generated it.
- **Snapshot model:** when work starts on a task, a canvas snapshot
  is taken. The task is then immune to subsequent canvas edits — it
  references a frozen view.

This layer does not exist in Plot today. It's a future addition;
the data-structure work needed: a `snapshots/` folder per project
+ a `tasks/` index + the provenance fields on each task.

## 10. Feedback loop

**Agents cannot mutate the source of truth directly.** Every
proposed canvas change from an agent goes through a PR-style flow:

- Agent proposes a change.
- Human approves or rejects.
- Only approved changes touch JSON.
- Interview results follow the same PR flow.

Implementation today: not yet enforced. The MCP tool surface
(`extend`, `reshape`) currently writes directly. The PR gate is a
required addition before any "self-improving agent" pattern is
safe.

## 11. Agent integration

- Embedded MCP server (current: `plot/plot_mcp/`).
- Snapshot-based context injection (per §9).
- Default skill set provided alongside the MCP server.

## 12. MVP scope

What ships in the first commercially complete version:

- Canvas (Foundation + Actor + Service + Service-Detail).
- Agent interview per canvas.
- JSON export (already exists — `.plot/{project}/`).
- Agent context injection.

MCP-as-protocol is **post-MVP** in the framing here, but Plot's
current implementation already ships MCP. Read this constraint as
"MCP is a value-add for adopters who use Claude Code; the MVP must
work for users who never touch MCP."

## 13. Future / out-of-scope-for-MVP

- Enterprise collaboration + permission management.
- Security model.
- Multi-user concurrent canvas editing.
- Symbol-level permissions (org / team scoped).
- Mermaid Service-Detail diagram rendering.
- Snapshot work-item layer (§9).
- PR-style feedback loop enforcement (§10).

## 14. Cross-references

| Topic | Source of truth |
|---|---|
| The essence (one sentence) | [`VISION.md`](./VISION.md) |
| Discovery / Retention / Execution cycle | [`VISION.md`](./VISION.md) |
| Bounded contexts + dependency direction | [`DOMAIN.md`](./DOMAIN.md) |
| 10 principles (relational value, services-as-hub, …) | [`PHILOSOPHY.md`](./PHILOSOPHY.md) |
| Node kinds and typed fields | [`CONCEPTS.md`](./CONCEPTS.md) |
| Per-canvas behaviour | [`SPEC.md`](./SPEC.md) |
| Decision log | [`DECISIONS.md`](./DECISIONS.md) |
| Release sequence | [`ROADMAP.md`](./ROADMAP.md) |
| Code shape and split plan | [`ARCHITECTURE.md`](./ARCHITECTURE.md) |
| Cursor visual contract | [`CURSOR.md`](./CURSOR.md) |
| Identity (older identity doc, v0.10 era) | [`IDENTITY.md`](./IDENTITY.md) |

## 15. When this file changes

This file changes only when the user explicitly re-defines a
product-level fact (platform target, business model, MVP scope,
symbol / canvas inventory). Each such change is a
`D-YYYY-MM-DD-X` entry in [`DECISIONS.md`](./DECISIONS.md). Drift in
tactical files (SPEC, DECISIONS) does not modify this file; it
modifies them to align with this file.

## 16. Open questions captured for follow-up

These items appear in the product spec but do not have implementation
clarity yet. Logged here so they don't get lost:

1. **`owner` field on every node** — required for multi-user. Today's
   `SketchNode` has no `owner`. When does this land? Likely before
   collaboration enters scope, not before MVP. Add to
   [`CONCEPTS.md`](./CONCEPTS.md) when the multi-user roadmap firms
   up.
2. **Mission/Core-value vs Identity canvas split** — product spec
   treats them as separate canvases (human-facing vs agent-facing).
   Today's Foundation is one canvas with three kinds. Decision: keep
   as one canvas with section grouping in the stencil, OR split into
   two canvases? Needs an explicit user call.
3. **PR-style feedback loop enforcement** (§10) — currently MCP
   tools write directly. Enforcing the PR loop changes the agent
   contract. Where does the diff queue live? Per-project file? Where
   does the approve / reject UI go? Plan needed.
4. **Snapshot work-item layer** (§9) — net-new subsystem. Schema for
   `tasks/`, `snapshots/`. Plan needed.
5. **Mermaid Service-Detail rendering** — Service-Detail canvas
   needs a diagram-export view. Decision: in-modal toggle? Separate
   panel?
6. **`canvas.tabs.foundation` Korean label** — currently "토대". The
   product spec uses "미션/코어밸류 + 아이덴티티" as the audience
   split. If Foundation stays one canvas, "토대" is acceptable; if
   split, two new tab labels required.
