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
   sub-service" → "this top-level service" → "this mission."
4. **Relationship visualisation** — seeing the interactions only
   visible at a wide zoom. Actors and services rarely make sense in
   isolation; the wider view is the diagnostic.

---

## The Two Modes (current and future)

Plot is becoming two things in one product:

### Mode 1: The Picture (today)

Strategic visualisation. Foundation / Actors / Services / Service
Detail canvases. Typed fields, Symbol/Component refs, AI-friendly
structure. Static in the sense that it captures *how things are
intended to work* — not *what's happening this week*.

### Mode 2: The Time Axis (future)

Actual task / work management. Each service can host concrete delivery
items along a timeline; the picture's structure (top-level services,
sub-services, owners as actor refs) becomes the **reporting structure**
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
   it and act consistently. Typed fields and Do/Don't pairs over free
   prose. Structure over decoration.
3. **Required fields enforce alignment, not friction.** A few hard
   requirements (top-level service must anchor to identity or value)
   are good — they raise quality floor. Many requirements break flow.
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

> An **actor** is a *class of people* who participate in this project's
> value economy — making, exchanging, and relating to each other.

- **Class, not individual**: "User" / "Operator", not "Kim Cheol-su".
- **People only**: external APIs, systems, bots, and infrastructure
  are *not* actors. They belong to the **infrastructure** layer, which
  is out of scope for Mode 1 (the picture) — they re-enter when Mode 2
  (the time-axis / task layer) is built.
- **Project minimum**: at least **two** actor classes per project
  (typically: an operator/developer side and a user side). A project
  with fewer is structurally incomplete — value exchange requires
  both sides.

### Service

> A **service** is a *playground* where stakeholders **produce and
> exchange value** while building relationships with each other.

The exact phrasing matters: not "exchange" alone but "**produce and
exchange**." Many services produce *new* value through actor
participation (a content platform's posts, a community's culture);
they are not pure distribution markets. The model must accommodate
both directions.

### Service Minimum Baseline

> Every service must have **at least two** participating actor
> references (`actor_ref`).

This is the only hard validator on `service` and is non-negotiable:

- A playground with one person isn't a playground.
- "Produce + exchange" requires at least two parties.

This sits alongside the wider **rich fields, minimal required**
default — most service fields stay optional, but the floor is real.

### The Operator Must Always Be Explicit

> The operator/developer is **never implicit**. Every service must
> include an explicit operator `actor_ref` in addition to the user(s).

The reasoning is **moderation responsibility**:

- Services are playgrounds where actors freely produce and exchange.
  Freedom requires alignment-keepers — that role is moderation.
- Moderation = keeping what happens in this service consistent with
  the project's mission, values, and identity.
- If the operator's involvement is left implicit ("of course they're
  in every service"), it becomes invisible *which* operator owns
  alignment for *which* service. Alignment ownership is precisely
  what Plot is meant to make visible (see "Direction alignment" in
  the four use purposes above).

### Why these are philosophy, not just rules

These look like validators (≥ 2 actors, explicit operator), but each
one encodes a claim about what Plot *is*: a picture where alignment
ownership is legible at every level. Loosening any of them would
change the product, not just the schema.

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
