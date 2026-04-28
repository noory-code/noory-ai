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
