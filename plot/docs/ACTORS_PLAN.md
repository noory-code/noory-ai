# ACTORS_PLAN — implementing the 2026-06-17 Actors design

> **Status: PLAN (2026-06-17).** Implements `D-2026-06-17-A`
> ([DECISIONS.md](./DECISIONS.md)). Concept SSOT = D-A + the actor section of
> [FOUNDATION_CONCEPT.md](./FOUNDATION_CONCEPT.md). **The node/inspector already
> fits — the real work is the two edge types.** TDD per CLAUDE.md Gate 1.5.

## Already correct (no change)

- `actor` node/inspector = label (role name) + `side` (operator/user) + `body`
  + inheritance captions. Identity-only (D-2026-06-15-J). Keep.
- Hierarchy via inheritance edges + `side` propagated down the tree. Keep.
- Per-service stake (gives/receives, motivation/pain) on `actor_ref`
  (Service-Detail). Keep.

## The work — two distinct edge types on the Actors canvas

### 1. Hierarchy edge ("is-a-kind-of")
- Structure only, **no value**. This is the existing inheritance edge.
- Visual: a quiet / neutral line (thin or dashed) — clearly **not** a value arrow.

### 2. Relationship edge ("gives value to")
- A **directed, labelled arrow** carrying *what value* flows *from which role to
  which* (hero →expertise→ fan).
- A reciprocal relationship is **two arrows** (hero →expertise→ fan; fan
  →support→ hero) — so "what flows, from where to where" is explicit.
- This is the **general / role-defining** value flow. The **concrete per-service
  exchange** (specific value, steps, metrics) stays in Service-Detail (`actor_ref`).

### Hard rule
The two edge types must be **visually distinct** (shape / colour) so
"classification" (hierarchy) is never confused with "exchange" (relationship).

## Build scope (lock-step, TDD)

- **Edge model:** confirm/extend the edge type so a relationship edge carries
  *value + direction* (a verb/value label). (PHILOSOPHY: arrows carry
  verb + value + direction — check what the current edge model already supports
  before adding.)
- **Renderer:** distinct visuals for hierarchy vs relationship edges on the
  Actors canvas.
- **Affordance:** editing a relationship edge's value label.
- **Tests:** the two edge types are distinguishable; relationship edge carries
  value + direction; reciprocal = two arrows; structural guard that the two
  types stay distinct.
- **Doc-sync:** CONCEPTS.md / SPEC Actors section (two edge types; two-level
  value: general on Actors → concrete in Service-Detail).

## Out of scope (separate)

- Aggregate "who relates to whom across all services" view — a **Services-layer**
  design topic (not the Actors canvas; next session).
- Foundation work → [`FOUNDATION_PLAN.md`](./FOUNDATION_PLAN.md).

## Done when

The Actors canvas renders two visually-distinct edge types; relationship edges
carry value + direction (reciprocal = two arrows); node/inspector unchanged;
tests + doc-sync green.
