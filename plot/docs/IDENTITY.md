# Plot — What Plot Is (and Is Not)

> **Established: 2026-04-28** (v0.11 prerequisite)
>
> The product identity, as articulated by the user (domain owner). Every
> feature, model, and UX decision must be evaluated against this. If a
> design pulls Plot toward "general mindmap tool," it's the wrong direction.

---

## Plot is NOT

- ❌ A simple mindmap / brainstorming tool
- ❌ A diagram-only canvas (we don't compete with draw.io / Excalidraw)
- ❌ A prose document (Notion / Google Docs already do that)

## Plot IS

✅ **A strategic operations design + alignment tool.**

Plot is where a team draws the picture of *who participates*, *what
services produce value*, *how those services answer to identity and
mission*, and (eventually) *what work is happening on the time axis*.
The drawing is the deliverable, not a side artefact.

Korean original (user, 2026-04-28):

> "두번째층을 운영해야합니다. 액터와 서비스 정의 과정을 디테일을
> 잡아가는거에요. 플롯은 마인드맵 사고정리 도구가 아니에요. 단순하지
> 않아요. 서비스를 구체적으로 기획하면서 모두가 같은 방향으로 가게
> 만들고 큰그림 안에서 구성원들이 무엇을 하고 있는지 정확하게
> 이해시키기 위한 목적도 있어요. 그리고 넓게 봐야 서로간의 관계가
> 보이기 때문에 일단 그림을 그리는 겁니다. 플롯은 그렇게 그림을
> 그리는 부분과 실질적 시간축 일감을 관리하는 기능도 들어가게
> 될겁니다."

---

## The 4 Use Purposes

Every Plot feature should serve one or more of these:

1. **Concrete service planning** — drawing the details of a service.
   Not "what would be cool to build" but "what value does this service
   create, who exchanges what with whom, what's enforced, what's
   produced."
2. **Direction alignment** — making sure everyone sees the same target.
   Mission / values / identity exist so a team and an AI can act
   coherently. Plot is the surface where that alignment is captured
   *and* checked.
3. **Position in the big picture** — letting any contributor locate
   their work inside the whole. "What I'm doing today" → "this
   feature" → "this service" → "this category" → "this mission."
   (category → service → feature is the Services-overview hierarchy
   per [D-2026-06-17-D](DECISIONS.md); sub-services are gone.)
4. **Relationship visualisation** — seeing the interactions only
   visible at a wide zoom. Actors and services rarely make sense in
   isolation; the wider view is the diagnostic.

---

## The Two Modes (current and future)

Plot is becoming two things in one product:

### Mode 1: The Picture (today)

Strategic visualisation. Foundation / Actors / Services / Feature /
Entities canvases. (The old "Service Detail" canvas is now the
**Feature** canvas — a behaviour flowchart a feature drills into per
[D-2026-06-17-G](DECISIONS.md); **Entities** is a new AI-maintained
project-level canvas of data objects per [D-2026-06-17-I](DECISIONS.md).)
Typed fields, Symbol/Component refs, AI-friendly structure. Static in
the sense that it captures *how things are intended to work* — not
*what's happening this week*.

### Mode 2: The Time Axis (future)

Actual task / work management. Each service can host concrete delivery
items along a timeline; the picture's structure (categories, services,
features, owners as actor refs) becomes the **reporting structure**
for the time axis.

Comparable products (rough analogy):

- Wardley Map (strategic positioning)
- Service Blueprint (process + actor view)
- RACI (responsibility assignment)
- Project Plan (time-axis delivery)

Plot collapses these into one continuous surface.

---

## What This Means for v0.11+ Decisions

Implications when evaluating any new design proposal:

1. **Actor / Service models must survive the time-axis transition.**
   Anything we add to those kinds in v0.11 has to make sense both in
   the picture and (eventually) in the schedule. Don't add a field
   that only makes sense in one mode.
2. **AI-first stays paramount.** The picture exists so an AI can read
   it and act consistently. Typed, structured fields over free prose.
   Structure over decoration. (Do/Don't pairs are no longer a model
   shape — core_value collapsed to name + body per
   [D-2026-06-16-M](DECISIONS.md), and the service inspector's `do`/`dont`
   fields were deleted per [D-2026-06-17-B](DECISIONS.md).)
3. **Required fields enforce alignment, not friction.** A few hard
   requirements raise the quality floor; many requirements break flow.
   A service answers to identity and value through its inspector's
   selectable `core_value` and `identity` references (the 5-field
   inspector, [D-2026-06-17-B](DECISIONS.md)), not a free-prose anchor.
   Default: **rich fields, minimal required**.
4. **Wide before deep.** Encourage the user to draw the full picture
   first (every actor, every top-level service). Detail comes after
   the relationships are visible.
5. **Drawing is the artefact.** Don't treat the canvas as a means to
   produce a doc. The canvas IS the doc, and it's the source the AI
   reads. `details.md` per node is for human prose only.

---

## Actor & Service — the Core Philosophy

These are the load-bearing definitions. Confirmed with the domain
owner during v0.11 planning (2026-04-28). Every other model decision
about actors and services must be consistent with these.

### Actor

> An **actor** is a *relational role* — a class of participant in this
> project's value economy, defined by position and resources, **not a
> person / persona**. Every actor both gives and receives value.

- **Role, not person**: "User" / "Operator", not "Kim Cheol-su" — and
  not a demographic persona. One person can occupy several actor-roles,
  and roles can switch. ([D-2026-06-17-A](DECISIONS.md).)
- **Relational + hierarchical**: a role alone is meaningless, so actors
  form a **hierarchy (tree)** — the top split is operator vs user
  (`side`), inherited down to child roles (user → hero, fan; operator →
  super-admin, manager). Inheritance is **core, not optional**. The
  Actors canvas carries **two distinct edge types**: a **hierarchy edge**
  ("is-a-kind-of", structure only, no value) and a **relationship edge**
  ("gives value to", a directed labelled arrow carrying which value flows
  from which role to which; a reciprocal relationship = two arrows).
  ([D-2026-06-17-A](DECISIONS.md).)
- **People only**: external APIs, systems, bots, and infrastructure
  are *not* actors. They belong to the **infrastructure** layer, which
  is out of scope for Mode 1 (the picture) — they re-enter when Mode 2
  (the time-axis / task layer) is built.
- **Project minimum**: a project naturally has at least an operator
  side and a user side — but this is **emergent** from the role
  hierarchy (operator/user at the top, [D-2026-06-17-A](DECISIONS.md)),
  not a hard ≥2 validator (the old floor was dropped,
  [D-2026-06-18-A](DECISIONS.md)).

### Service

> A **service** is a *playground* where stakeholders **produce and
> exchange value** while building relationships with each other.

The exact phrasing matters: not "exchange" alone but "**produce and
exchange**." Many services produce *new* value through actor
participation (a content platform's posts, a community's culture);
they are not pure distribution markets. The model must accommodate
both directions.

On the Services overview, a service is captured by a **5-field
question-titled inspector** — 누가 참여하나? (actor refs) · 왜 필요한가? ·
뭐가 좋아지나? · 뭘 양보 못 하나? (core_value refs) · 어떤 결로 다가가나?
(identity refs) — and **selecting a service shows that inspector; it no
longer drills.** Drilling happens on its **`feature`** children
(글쓰기 / 글편집 / 이모지 반응 …): clicking a feature opens the Feature
canvas (its behaviour flowchart). Hierarchy: 카테고리 → 서비스 → 기능 →
행동 / 룰. ([D-2026-06-17-B](DECISIONS.md), [D-2026-06-17-D](DECISIONS.md).)

### Service Participants

> A service needs **at least one** participating actor reference
> (`actor_ref`); the operator is the **default participant**.

The old hard "≥ 2 with an explicit operator" floor was relaxed
([D-2026-05-28-K](DECISIONS.md) → ≥ 1; [D-2026-06-18-A](DECISIONS.md)
dropped the ≥2 / explicit-operator gate). The intent survives as
**guidance**, not a gate:

- A playground with one person isn't much of a playground.
- "Produce + exchange" usually needs more than one party — a
  single-participant service is a smell worth questioning, not a
  blocked state.

This sits alongside the wider **rich fields, minimal required**
default — most service fields stay optional.

### The Operator as Default Participant

> The operator is the **default participant** of every service
> ([D-2026-06-17-B](DECISIONS.md)) — so it need not be forced as a
> separate explicit-operator validator (the old "always explicit" gate
> was dropped, [D-2026-06-18-A](DECISIONS.md)).

The reasoning is **moderation responsibility**, and it still holds —
now as the rationale for the default, not as a hard gate:

- Services are playgrounds where actors freely produce and exchange.
  Freedom requires alignment-keepers — that role is moderation.
- Moderation = keeping what happens in this service consistent with
  the project's mission, values, and identity.
- Because the operator is the default participant, alignment ownership
  stays visible without forcing a separate explicit-operator
  `actor_ref` on every service (see "Direction alignment" in the four
  use purposes above).

### Why these are philosophy, not just rules

These were once hard validators (≥ 2 actors, explicit operator); the
hard floors were **relaxed** ([D-2026-06-18-A](DECISIONS.md)) because
they fall out of the role hierarchy (operator/user) and the operator
being the default participant — the model no longer needs them
enforced. What survives is the *claim* they encoded: Plot is a picture
where **alignment ownership is legible at every level**. The intent is
philosophy; it now lives as guidance and defaults, not as gates.

---

## Concepts the picture now carries (2026-06-17 marathon)

The big-picture marathon ([D-2026-06-17-D..K](DECISIONS.md)) added
load-bearing concepts that an IDENTITY-level reader must know exist:

- **`feature`** — a capability a service offers (글쓰기 / 글편집 …),
  nested under a service on the Services overview. It is the **drill
  target**: clicking a feature opens its detail canvas.
  ([D-2026-06-17-D](DECISIONS.md).)
- **Feature canvas** (the old "Service Detail") — a feature's behaviour
  as a **flowchart** (행동 → 분기 → 결과), at **action-altitude only**.
  It does NOT descend into implementation logic (storage / queries /
  rendering) — that is the user's AI agent's job, outside Plot. The
  flow is actor-anchored and value-oriented, so it stays continuous
  with the service above it and does not turn Plot into a flowchart
  tool. ([D-2026-06-17-G](DECISIONS.md), [D-2026-06-17-H](DECISIONS.md).)
- **`rule`** — a per-feature operational constraint (policy / SLA).
  This is **not** identity: policy ≠ identity.
  ([D-2026-06-17-E](DECISIONS.md).)
- **`note`** — an edgeless, canvas-global memo on the feature canvas:
  ambient context a human reads and the AI always takes into account.
  ([D-2026-06-17-F](DECISIONS.md).)
- **Entities canvas + `entity`** — a project-level, **AI-maintained**
  canvas of the product's data objects (글 · 댓글 · 사용자). 액터 = 누가
  / 엔티티 = 무엇. Entities **emerge from designing features/services**
  (the AI surfaces and registers them; the user never starts from a
  blank canvas) and Plot holds only **name + a one-line "무엇을 담나"** —
  detailed schema / field types / relations are the AI agent's job,
  **outside Plot** (else Plot becomes an ERD / DB-modelling tool — an
  identity violation). ([D-2026-06-17-I](DECISIONS.md), [D-2026-06-17-K](DECISIONS.md).)
- **Edges are governed by their definition, not by who draws them.**
  The former "all edges are user-drawn" global ban is gone: the AI may
  propose / draw edges (especially on AI-maintained canvases like
  Entities), the user may edit or delete any edge, and what must hold
  is each edge's *definition* — never a meaningless line. A canvas may
  still be user-draw-only by its own spec.
  ([D-2026-06-17-J](DECISIONS.md).)

---

## Relationship to Other Docs

- [`PHILOSOPHY.md`](PHILOSOPHY.md) — the value-theory foundation
  (relational value, plural forms, asymmetric participation, etc.).
  Established 2026-04-20. Still valid; this document layers the
  product-identity statement on top.
- [`CONCEPTS.md`](CONCEPTS.md) — the canvas / kind / typed-field
  reference. The "what" of the model.
- [`ROADMAP.md`](ROADMAP.md) — the implementation order for the
  current release line.

This document is the **"why and for whom."** When CONCEPTS or ROADMAP
suggest a change, check it against IDENTITY first.
