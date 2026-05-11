# Plot — VISION (project essence, single source of truth)

> **Read this file first, every session, before touching code.**
> One sentence at the top. Three phases below it. Everything else
> downstream.

---

## The essence — one sentence

**Plot 은 본질을 모르는 사람이 본질을 찾고, 그걸 놓치지 않으면서, 그
본질 아래에서 서비스를 쉽게 기획·개발할 수 있게 AI 와 협업하는
툴이다.**

(English mirror: Plot is a tool for people who don't know their essence to
discover it, retain it without drift, and plan + develop services under
that essence — with AI as a continuous collaborator.)

This is the only sentence that overrides every other priority. If a
proposed change does not serve this essence, it should not ship. When
this sentence and any other rule disagree, this sentence wins; fix
the other rule.

---

## The three-phase cycle

The essence resolves into a single workflow that loops as the project
matures. Every Plot canvas, every MCP tool, every Inspector field, every
auto-layout click, every cursor decision must trace back to one of these
three phases.

| # | Phase | What it does | Where it happens | AI collaboration mode |
|---|---|---|---|---|
| 1 | **Discovery** | Surfaces the user's not-yet-articulated essence. | Foundation canvas (mission / core_value / identity) | Claude *interviews* the user; the resulting language is captured in typed-text MD templates and rendered as nodes. |
| 2 | **Retention** | Keeps the discovered essence visible and load-bearing as the project moves. | Anchor (project node) injected on every primary canvas; Foundation references threaded through Actors / Services. | Claude *anchors* every later suggestion to the Discovery output — never proposes a service that contradicts the mission. |
| 3 | **Execution** | Plans and develops the services that realise the essence. | Actors → Services → Service-Detail; MCP tools (`read`, `extend`, `reshape`) drive code-level work. | Claude *participates* in planning (proposes actors, services, value flows) AND development (writes code that the user reviews against the essence). |

> **The cycle is not linear.** A user often discovers part of the essence
> only after attempting Execution and realising what's missing. Plot
> must support drilling back from Service-Detail to Foundation without
> losing context.

---

## Who Plot is for

- **Solo developers** building the first version of something.
- **Early-stage startups** before the team has a shared mental model.
- **Anyone working with AI as a thinking partner** who needs the AI
  to share the same picture of "what we're building and why."

Not for: large enterprises with established product specs (they have
other tools); pure documentation use cases (they have wikis); end-user
analytics dashboards (they're consumers, not builders).

---

## How a feature decision uses this file

Every feature, bug fix, or refactor must be checked against this
cycle. The check has two questions:

1. **Which of the three phases does this serve?** If none, ask the
   user before doing anything.
2. **Does it preserve the cycle's reversibility?** Drilling backward
   (e.g. Service-Detail → Foundation to fix a typo in mission) must
   keep working.

If either answer is unclear, **stop and re-read this file's first
sentence**.

---

## Anti-patterns (concrete examples of drift)

| Drift example | Why it violates this VISION |
|---|---|
| Spending six rounds on a cursor flicker without first asking *"is the cursor blocking the user from seeing their essence?"* | Reduced VISION to UI mechanics; missed that the canvas's job is to make the essence visible. |
| Auto-emitting edges between anchor and children (D-2026-05-04-A) | Removed user authorship from a graph that is supposed to capture the user's essence-language. |
| Treating Foundation as "form fields" rather than "interview output" | Lost Phase 1 (Discovery — interview-driven) and reduced it to data entry. |
| Removing the Auto-layout button (D-2026-05-04-D, since reverted) | Removed the "see your essence's shape" gesture entirely. |
| Deferring SPEC.md updates after a confirmed user decision | Broke Phase 2 Retention — the next session loses the just-discovered language. |

---

## Cross-references

- [`PRODUCT_SPEC.md`](./PRODUCT_SPEC.md) — **product-level decisions**
  (platforms, business model, MVP scope, symbol system, canvas
  inventory). Sits above this file in the doc set; this file is the
  essence, PRODUCT_SPEC is how the essence becomes a shippable
  product.
- [`PHILOSOPHY.md`](./PHILOSOPHY.md) — the **why** behind value relations
  (10 principles). VISION inherits from this; PHILOSOPHY is the
  conceptual foundation, VISION is the operational mission.
- [`DOMAIN.md`](./DOMAIN.md) — the **bounded contexts** that translate
  this VISION into code architecture.
- [`CONCEPTS.md`](./CONCEPTS.md) — the **data model** (kinds, fields,
  schemas) that the contexts manipulate.
- [`SPEC.md`](./SPEC.md) — the **canvas behaviour** that surfaces the
  essence visually.
- [`DECISIONS.md`](./DECISIONS.md) — the **change log** of every
  user-facing behaviour decision, anchored back to this VISION.
- [`CURSOR.md`](./CURSOR.md) — the **canvas-wide cursor SSOT** (the
  visual contract for "the user's surface to their essence").
- [`ROADMAP.md`](./ROADMAP.md) — the **release sequence** that grows
  this VISION over time.
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — the **code shape** and the
  refactor plan that aligns code with DOMAIN contexts.
- [`../CLAUDE.md`](../CLAUDE.md) — operational gates (Gate -1 reads
  this file; Gates 0-4 enforce the discipline that keeps it true).

---

## When this file changes

This file changes only when the user explicitly redefines the essence
or one of the three phases. Such a change is a `D-YYYY-MM-DD-X`
decision id with `Approval: Accepted by user`. Drift in tactical files
(SPEC, DECISIONS) does not modify this file; it modifies them to align
with this file.
