# FOUNDATION_PLAN — implementing the 2026-06-16 Foundation redesign

> **Status: PLAN (2026-06-16).** Build order for the pinned design decisions
> from the big-picture Foundation discussion
> (`D-2026-06-16-J/K/L/M/N/O/P` in [DECISIONS.md](./DECISIONS.md)). **Code is
> currently UNCHANGED** — the decisions live in docs only; this file is the
> implementation queue. Concept SSOT = [FOUNDATION_CONCEPT.md](./FOUNDATION_CONCEPT.md).

## Goal

Bring the three Foundation node kinds into line with their pinned definitions:
each inspector shows only the fields that earn their place (define the concept),
legacy fields folded into `body` with **no data loss**.

## Per-change scope (lands in lock-step)

Every kind change touches all of these together (schema parity is enforced):

- viewer domain class `viewer/src/domain/{Kind}.ts` (field set + `fromJson` migration)
- server pydantic model (parity guard `plot/tests/test_schema_parity.py`)
- per-kind inspector `viewer/src/canvases/inspectors/{kind}/index.tsx`
- i18n keys en/ko for any renamed field / placeholder
- tests: `entity-roundtrip`, inspector behaviour, schema parity, structural guards

**Procedure:** TDD (Red→Green→Refactor, CLAUDE.md Gate 1.5) via the
`plot-entity-template` / `plot-feature-tdd` skills.

## Build order (smallest-first)

### 1. mission — declaration + body  (`D-2026-06-16-J`)
- Drop `statement`; the single **declaration = `label`**. Inspector body = the
  `label` (declaration) input + `body` only.
- `Mission.fromJson` migration: if `label` empty, fill from legacy `statement`;
  otherwise fold `statement` into `body`. Loss-free.
- Remove the `statement` field from `MissionInspector`.
- Tests: roundtrip; migration folds legacy `statement`; inspector renders 2 fields.

### 2. core_value — name + body  (`D-2026-06-16-M`)
- Drop `definition`; fold into `body` on read (extend the existing
  `foldLegacy*`). `label` stays the value **name**.
- Remove the `definition` field from `CoreValueInspector` (body only).
- Tests: roundtrip; legacy `definition` folds into body; inspector renders name+body.

### 3. identity — name + action-rule list  (`D-2026-06-16-O`)
- Drop `description` (fold into `body`). `body` = the **action-rule list**
  (markdown bullets for now; a structured per-rule list is a Phase-2 enhancement
  that arrives with the AI-derive flow).
- Remove `status` + `provenance` **inputs** from `IdentityInspector`. **Keep the
  JSON fields dormant** (default-parsed) — they return with the derive flow
  (ROADMAP 5.7). Do NOT delete the schema, to avoid a re-migration later.
- Tests: roundtrip (status/provenance still parse + default); inspector renders
  name + rules; no status/provenance UI.

### 4. CONCEPTS.md doc-sync (Foundation slice only)
- Update the mission / core_value / identity rows to the new field sets. (The
  full CONCEPTS refresh — the expanded kind palette, actor as a relational role
  / identity-only (`D-2026-06-17-A`), and the Services-overview 5-field
  question-titled service inspector (`D-2026-06-17-B`) — is the wider T3 task;
  here only the Foundation fields.)

## Out of scope (separate, already tracked)

- Interview question sets → skill / MCP prompt — **ROADMAP 5.7**.
- AI-derive flow for identity (auto status/provenance) — **ROADMAP 5.7**.
- Foundation canvas visual / chips / layout — next design topic (not yet pinned).
- PHILOSOPHY.md S-D Logic grounding — **ROADMAP 5.8**.

## Done when

mission / core_value / identity inspectors match J / M / O; every migration is
loss-free; schema parity + structural guards green; CONCEPTS Foundation rows current.
