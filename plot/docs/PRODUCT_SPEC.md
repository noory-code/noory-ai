# Plot — Product Spec

> **Source:** user-provided product brief, last updated
> 2026-05-12 (revision 2).
>
> **Position in the doc set:** this file captures **product-level
> decisions** (who Plot is for, what platforms, what business
> model, what's in scope). It sits **above** [`VISION.md`](./VISION.md)
> — VISION is the essence; this file is how the essence becomes a
> shippable product.
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

### Language split — mindmap vs graph

- **To the user, Plot is a "mindmap."** Friendly, approachable
  vocabulary.
- **Internally, the structure is a "graph."** Supports cycles,
  self-loops, and arbitrary cross-references — relationships a
  strict tree cannot express.

Use *mindmap* in UI text, marketing, onboarding. Use *graph* in
code identifiers, data model, internal docs.

## 2. Platforms

| Phase | Host | MCP |
|---|---|---|
| **Now** | Claude Code plugin (`plot/`) | MCP server runs from the plugin (`plot_mcp/`). |
| **Next** | macOS desktop app | MCP server embedded in the app process. |

The desktop app is downstream; no new viewer / data model work is
required to enable it.

## 3. Business model

- **Individuals:** free.
- **Enterprise:** paid. Surface = collaboration + permissions +
  security. Detailed design deferred (see §13 Future).
- **Growth model:** PLG — individual adoption → team / org spread.

## 4. Tech stack

| Layer | Tech | Owner doc |
|---|---|---|
| Canvas + graph engine | React Flow | [`ARCHITECTURE.md`](./ARCHITECTURE.md) |
| Source of truth | JSON | [`CONCEPTS.md`](./CONCEPTS.md) |
| Source-data version control | **isomorphic-git** | §5 below |
| Free-text rendering | Markdown | [`SPEC.md`](./SPEC.md) §Foundation |
| Diagram rendering | Mermaid | (queued for feature-canvas visualisation, D-2026-06-17-G) |
| Agent connection | MCP | [`DOMAIN.md`](./DOMAIN.md) AICollaboration |

## 5. Data structure principles

- **JSON is the source of truth.** Every persisted shape lives in
  JSON files under `.plot/{project}/`.
- **Free-text fields → Markdown.** Realised in v0.13 for Foundation
  (`foundation/{kind}-{slug}.md`).

  > **Note (2026-05-12, deferred refactor):** The user has flagged
  > that the long-term direction is "JSON is SSOT, MD is generated
  > from JSON" — i.e. MD becomes a *derived export*, not a
  > co-equal storage layer. Today's v0.13 model is a stepping
  > stone; the move from co-equal MD to derived MD is queued.
  > Tracked in §15 Open questions.
- **Structured fields → arrays / objects.** Anything that needs
  validation or referential integrity stays in JSON.
- **Every node carries a unique id.** Referential tracking is a
  precondition for §7 Symbols.
- **Every node carries an `owner` field.** Currently unused;
  reserved for the multi-user expansion in §13.
- **Cycles allowed.** Plot's data model is a graph, not a tree.
  Self-loops (`Node A → Node A`) and cycles (`A → B → A`) are
  legal. (This is a graph-engine property only — there is **no**
  first-class service→service edge concept; that "user journey"
  edge was dropped, D-2026-06-17-C.)
- **Export targets:** Markdown, Mermaid, MCP. (MCP "export" =
  exposing the sketch as agent context, not file output.)

## 6. Source-data version control (git)

Plot's *content* (canvas JSON, user stories, tasks) is version-
controlled with git, **independent of any application source-
code git repo the user happens to be inside**. The user does not
need to know git exists; the trail accumulates internally.

| User action | Internal git event |
|---|---|
| Edit a canvas | Auto-commit *(aspirational — see note below)* |
| Snapshot a workflow state | Same commit (snapshot ≡ commit) |
| **Publish a node** *(v0.18.0+)* | **Explicit commit with `Publish-*` trailers** |
| **Session-tag the project** *(v0.16+)* | **Explicit commit + annotated tag** |
| Agent proposes a canvas change | Create a branch |
| User approves agent's proposal | Merge the branch |
| User rejects agent's proposal | Delete the branch |
| (future) Sync with remote | Optional GitHub link |

> **v0.17 / v0.18 reality vs aspiration.** The "Edit a canvas →
> Auto-commit" row is **aspirational**; it lands with the
> isomorphic-git in-viewer integration (ROADMAP §"v0.17+" item A).
> Through v0.17 and v0.18 the canvas stays *uncommitted* between
> explicit user actions — only **publish** (D-2026-05-16-D, v0.18.0)
> and **session-tag** (v0.16+) trigger a commit. The other rows
> (branch on agent proposal, sync with remote) are also gated on
> the isomorphic-git integration. Until then the implementation uses
> subprocess `git` and only fires on the two explicit-action rows.

Implementation: `isomorphic-git` so the version-control loop runs
inside the viewer / MCP server without requiring system `git`.
*(Currently subprocess `git` is used for the two explicit-commit
triggers; isomorphic-git swap-in is ROADMAP-A.)*

### Why this matters for the agent loop

- The snapshot model in §9 is literally a commit reference. When
  a long-running task starts, the agent's context is pinned to
  the commit SHA at task start; subsequent canvas edits do not
  invalidate the agent's working state.
- The PR-style feedback loop in §10 is git-branch shaped: agents
  cannot mutate the trunk directly; their proposals are branches
  pending human merge.

## 7. Symbol system

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
- Feature (a capability nested under a service; D-2026-06-17-D).
- Entity (a project-wide data object; D-2026-06-17-I).

Core value and Identity are also **referenced from a service's
inspector** (the 누가/왜/뭐가 좋아지나 + 코어밸류/아이덴티티
question fields, D-2026-06-17-B) — picked from the Foundation
canvas as chips, exactly like actors.

**No first-class service→service edge (D-2026-06-17-C).** The
previously-specced "Service-to-service edges = User journey" is
**dropped** — Plot does not build journey / value-flow edge
semantics between services. Value flow is already captured at the
role level (Actors relationship edges, D-2026-06-17-A) and
per-participant (`actor_ref` on the feature canvas). Generic
user-drawn edges remain technically possible but carry no special
inter-service meaning and are not a provided feature.

## 8. Canvas layers (spatial)

Project-level canvases. The audience (human / agent) is encoded
*inside* the canvases rather than as canvas boundaries.

| # | Canvas | Defines |
|---|---|---|
| 1 | **Mission / Core value / Identity** (one canvas) | All three on a single Foundation canvas. Mission = *why we exist*. Core value = *the value that wins when decisions conflict* (D-2026-06-16-L). Identity = the service's **consistent execution / expression action-rules** ("we design / speak / behave like ~"), AI-derived from mission + core value and human-confirmed (D-2026-06-16-N/O). The visual composition of the three around the project anchor *is* the essence (D-2026-06-16-Q). |
| 2 | **Actor** | Roles in the service's value economy — **relational roles, not people / personas** (D-2026-06-17-A). Actors form a hierarchy (operator vs user at the top, inherited down). The canvas carries **two edge types**: a quiet hierarchy edge ("is-a-kind-of", no value) and a directed, labelled relationship arrow ("gives value to"; reciprocal = two arrows). |
| 3 | **Entity** | A project-wide map of the product's **data objects** (글 · 댓글 · 사용자), **AI-maintained**, born as a byproduct of designing features / services (D-2026-06-17-I). A conceptual entity map (rough relationships OK), **not a physical ERD** — name + one-line "무엇을 담나" only; schema / field types / normalisation are the user's AI agent's job, outside Plot. |
| 4 | **Service** | Categorised services. The overview holds **카테고리 → 서비스 → 기능** (D-2026-06-17-D): a `category` is visual grouping only; a `service` shows its **5-field inspector** (누가 참여하나 / 왜 필요한가 / 뭐가 좋아지나 + 코어밸류·아이덴티티 references, D-2026-06-17-B) **and does not drill**; a `feature` (a capability nested under a service) **drills to the feature canvas.** |
| 5 | **Feature** (per-feature detail) | The behaviour flowchart for one feature (the former Service-Detail canvas), at action-altitude, inheriting the service philosophy (actor-anchored, value-oriented) (D-2026-06-17-G). Nodes: 행동(`step`) + 분기(`decision`) + flow edges + 노트(`note`, D-2026-06-17-F) + 룰(`rule`, per-feature, D-2026-06-17-E) + 액터 참조(`actor_ref`). It is a *living* document, filled bottom-up through AI discussion (D-2026-06-16-P). |

**Resolution of the earlier "split Mission/Core-value vs Identity"
open question (v0.14.7 §16):** the user decided 2026-05-12 to
keep them on a single canvas, reaffirmed 2026-06-16
(D-2026-06-16-R). The decisive reason is no longer "audience" but
that the essence is the **emergent composition** of the three
concepts around the anchor (D-2026-06-16-Q) — splitting them
would break that single visual statement of what the service is.

## 9. Core UX pattern — canvas via conversation

Every canvas's first draft comes from an **agent interview**.
This is Plot's onboarding flow AND its primary interaction loop.

**Flow:**

```
empty canvas
  → agent interview
  → human answers
  → canvas draft proposal
  → human approves / edits
```

**The feature interview produces two artefacts at once:**

- **Feature-canvas content** (the behaviour flowchart: actions /
  branches / rules, D-2026-06-17-G) → goes onto the canvas.
- **User-story draft** → goes into the work-item layer (§10).

The interview covers the feature's actions, branches, and
constraints AND the concrete user scenarios that motivate it. The
two artefacts share provenance from the same interview transcript.
The upstream foundation references (core value / identity) are
**not** re-collected here — they are inherited from the service's
inspector chips (D-2026-06-17-B/H).

**Context flow between canvases:**

- Foundation interview (Mission / Core value / Identity) →
  results referenced in the Actor interview.
- Actor interview → results referenced in the Service interview.
- Each prior canvas becomes the input context of the next.

This is the operational form of the VISION cycle (Discovery →
Retention → Execution). See [`VISION.md`](./VISION.md).

## 10. Work-item layer (temporal)

Distinct from the canvases (which are spatial).

- The feature interview generates the user-story draft alongside
  the feature-canvas content (§9).
- User stories → tasks (derived).
- Each task carries **provenance metadata**: which feature +
  which actor relation it came from.
- **During execution, discoveries flow back as PRs.** When a
  user-story task reveals new design constraints, the agent
  proposes those as canvas-change branches against the feature
  canvas.
- **Snapshot model:** snapshot ≡ git commit (§6). When work
  starts on a task, the agent's context pins to the commit SHA
  at task start; subsequent canvas edits do not invalidate the
  agent's working state.

## 11. Feedback loop (PR-style on canvases)

**Agents cannot mutate the source of truth directly.** Every
proposed canvas change from an agent goes through a branch:

- Agent proposes → creates a git branch (§6).
- Human approves → merge.
- Human rejects → delete the branch.
- Only merged branches touch the canvas's main view.
- Interview results follow the same branch flow.

Implementation today: not yet enforced. The MCP tool surface
(`extend`, `reshape`) currently writes directly. The branch-
based gate ships when §6 (isomorphic-git) lands.

## 12. Agent integration

- Embedded MCP server (current: `plot/plot_mcp/`).
- Snapshot-based (= commit-SHA-based) context injection per §10.
- Default skill set provided alongside the MCP server.

## 13. Future / out-of-scope

- Enterprise collaboration + permission management.
- Security model.
- Multi-user concurrent canvas editing.
- Symbol-level permissions (org / team scoped).
- **GitHub integration** — surface the internal git history (§6)
  to an external GitHub remote when the user wants public /
  collaborative version control.
- Mermaid feature-canvas diagram rendering (D-2026-06-17-G).

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
| Korean translation glossary | [`I18N_KO_GLOSSARY.md`](./I18N_KO_GLOSSARY.md) |
| Identity (older identity doc, v0.10 era) | [`IDENTITY.md`](./IDENTITY.md) |

## 15. Open questions captured for follow-up

These items appear in the product spec but do not yet have
implementation clarity. Logged here so they don't get lost.

1. **`owner` field on every node** — required for multi-user.
   Today's `SketchNode` has no `owner`. Add to
   [`CONCEPTS.md`](./CONCEPTS.md) when the multi-user roadmap
   firms up.
2. **JSON SSOT + per-node MD + per-node versioning + folder hierarchy**
   — 6-phase migration in progress per
   [D-2026-05-13-O](./DECISIONS.md). User stated the 7 canonical
   principles verbatim during the 2026-05-13 design session:

     1. **JSON = SSOT.** v0.13's JSON+MD co-equal storage abolished.
     2. **JSON value = MD-formatted string.** Typed-text fields
        are stored inside JSON as MD-formatted strings; viewer
        edits via MD-aware editor.
     3. **MD extraction = "발행" (publish) button.** No automatic
        sync.
     4. **Per-node MD file.** *Supersedes D-2026-05-13-J point #4*
        ("per-canvas single MD") — user explicit clarification.
     5. **Per-node versioning.** File-level git history = node
        history.
     6. **Version format `vMAJOR.MINOR`:**
        - MAJOR + 1 on the node's own content publish.
        - MINOR + 1 when any descendant publishes
          (chain-propagated to all ancestors).
        - Leaf nodes: MAJOR only (`v1.0` → `v2.0` → …).
     7. **MD folder hierarchy = node hierarchy 1:1.** Container
        nodes become folders; leaves become files inside.

   6-phase ship sequence (each phase its own plan-mode + user
   approval, see D-2026-05-13-O):

   - **Phase 0** (shipped v0.16.40, 2026-05-13) — Vision pin docs.
   - **Phase 1** (shipped v0.17.0, 2026-05-16) — MD → JSON
     absorption: typed-text fields + new `body` live in JSON as
     MD-syntax strings; legacy MD quarantined to `_legacy/`;
     viewer's MD-editor surface hidden for the 3 typed-text kinds.
     See D-2026-05-16-A.
   - **Phase 2** — `version: str = "v1.0"` in BaseFields.
   - **Phase 3** — "Publish" button + per-node MD export + MAJOR.
   - **Phase 4** — MINOR propagation (ancestor chain).
   - **Phase 5** — Folder hierarchy + container-publish.
   - **Phase 6** — Legacy purge + final docs sync.

   Original user direction (D-2026-05-12-A): *"이 부분은 나중에
   다시 다듬어 봅시다."* — discussion reopened 2026-05-13.
   First vision pin (D-2026-05-13-J): per-canvas MD. Today's pin
   (D-2026-05-13-O): per-node MD with versioning + folder
   hierarchy — supersedes D-2026-05-13-J point #4.
3. **isomorphic-git integration timing** — §6 / §11 hinge on git
   being live inside the viewer / MCP. Currently no git is
   integrated. Land before any "self-improving agent" pattern.
4. **Snapshot work-item layer** (§10) — net-new subsystem. Schema
   for `tasks/`, `user_stories/`, provenance links to commit
   SHAs.
5. **Mermaid feature-canvas rendering** (D-2026-06-17-G) — the
   feature canvas needs a diagram-export view. Decision: in-modal
   toggle? Separate panel?
6. **i18n string lifecycle skill** — adding new translations is
   handled (Glossary §3 workflow); **removing unused keys** is
   not. User flagged 2026-05-12 *"사용되지 않는 것들 삭제하고
   하는 거 관리되어야해요."* Need a tool / skill that scans
   `viewer/src/` for `t("...")` calls and reports keys present in
   `locales/*.json` that no source file references. Likely a
   `plot/skills/plot-i18n-audit/` skill.
7. **Plot repository split** — should `plot/` migrate out of the
   `noory-ai` monorepo into its own repo? User flagged
   2026-05-12 *"plot 이라는 프로젝트가 커지는데 리포지토리
   분리를 해야하나… 아니면 그냥 둬야하나…"* Decision deferred;
   trade-off analysis is in the assistant's session reply.

## 16. When this file changes

This file changes only when the user explicitly re-defines a
product-level fact (platform target, business model, scope, canvas
inventory, …). Each such change is a `D-YYYY-MM-DD-X` entry in
[`DECISIONS.md`](./DECISIONS.md). Drift in tactical files (SPEC,
DECISIONS) does not modify this file; it modifies them to align
with this file.

## 17. Revision history

- **2026-05-11 (rev 1, v0.14.7, D-2026-05-11-E):** initial pin.
- **2026-05-12 (rev 2, v0.14.12, D-2026-05-12-A):**
  - Added §1 mindmap / graph language split.
  - Added `isomorphic-git` to §4.
  - Added §5 "cycles allowed" principle.
  - **New §6** source-data version control.
  - §7 Symbol system clarified self-loops in user journey.
  - §8 collapsed "Mission/Core-value + Identity" into one
    Foundation canvas (resolves v0.14.7 open question #2).
  - §8 Service-Detail explicitly "starts empty, fills bottom-up."
  - §9 Service interview produces TWO artefacts (service-detail +
    user-story draft).
  - §10 work-item layer now references commit-SHA snapshots from
    §6.
  - §11 feedback loop is git-branch shaped.
  - §13 GitHub integration added.
  - **MVP scope section removed** — was §12 in rev 1, dropped
    deliberately. User has moved past "what's in MVP" framing.
  - §15 Open questions: removed resolved item #2 (Mission/Identity
    canvas split); added #2 (MD-as-export migration), #6 (i18n
    string lifecycle skill), #7 (repo split).
