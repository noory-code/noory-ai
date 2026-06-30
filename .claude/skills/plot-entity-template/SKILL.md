---
name: plot-entity-template
description: Procedure for adding a new domain entity (a new ``kind``) to Novel. Walks through every file that must land in lock-step (viewer domain class, server Pydantic model, per-kind node renderer, per-kind inspector, i18n keys, registry updates, tests, schema-parity, structural guards). Triggers on phrases like "add a new kind", "엔티티 추가", "새 종류", "new entity", "kind 추가", "domain entity", "fromJson", "discriminated union extend". Prevents the v0.13 god ``SketchNode`` regression — every new kind must land as a class with ``fromJson`` boundary + per-kind UI files, never as a new field appended to the god union.
metadata:
  version: "1.0.0"
  category: dev-process
  type: unit
  style: procedure
  triggers:
    - "new kind"
    - "엔티티 추가"
    - "새 종류"
    - "new entity"
    - "kind 추가"
    - "domain entity"
    - "fromJson"
    - "discriminated union"
  uses: []
---

# plot-entity-template — adding a new ``kind`` end-to-end

> **Why this skill exists.** Novel has 15 entity kinds; each lives as a
> domain class (``viewer/src/domain/{Kind}.ts``) with ``fromJson`` /
> ``toJson`` invariants, a Pydantic server model
> (``plot_mcp/models/``), a per-kind node renderer, a per-kind
> inspector, i18n keys, and round-trip tests. Adding a 16th kind
> *correctly* means touching ~14 files in a single landing. Skipping
> any of them re-introduces god-object debt (see auto-memory
> ``feedback_no_god_object`` — *"kind 별 클래스 + Pydantic/TS
> discriminated union 비협상"*) and is blocked at multiple layers
> — structural-guards tests,
> schema-parity tests, no-god-import hook, entity-roundtrip test.
>
> This skill is the **single procedure SSOT** for that walk. Follow it
> in order. Skip nothing.

---

## When to invoke

User asks to add a new node kind, value-object, or discriminated
variant. Examples:

- *"a 'risk' kind for Foundation"*
- *"엔티티 추가하자 — 'budget'"*
- *"new entity: Decision"*

If the user wants to **modify** an existing kind (add a field, change a
validation), this skill does **not** apply — go directly to
[`plot-feature-tdd`](../plot-feature-tdd/SKILL.md). New kind = new
discriminator value = this skill.

---

## Pre-flight checks (before any file edit)

| Check | If yes | If no |
|---|---|---|
| Is the new kind already covered by an existing kind under a different name? | Stop. Reuse. Document the synonym in `DOMAIN.md`. | Continue. |
| Does the new kind belong to a different bounded context than the 4 current canvases (Foundation / Actors / Services / ServiceDetail) cover? | Stop. Open a `D-YYYY-MM-DD-X` entry first; canvas-inventory change is a product decision (PRODUCT_SPEC.md §canvas inventory), not a kind addition. | Continue. |
| Has the user explicitly approved the kind name + canvas placement? | Continue. | Ask. Append the answer as a `D-YYYY-MM-DD-X` entry before writing code. |
| Will the new kind be a value-object (no id, embedded in another entity) or an entity (own id, own node)? | Value-object → skip §3-§6 (no class, no inspector); only add a JSON sub-type. Entity → full walk. | Decide first. |

---

## The 14-step walk

Order matters. Each step has a **commit-ready unit**: tests pass after
each step (the previous steps are not yet wired in, so the new code is
*dormant* — exactly the property that keeps small ships landable).

### Step 1 — `docs/CONCEPTS.md`: register the kind

Add a row to the kind table. Fields:
- ``kind`` string
- one-sentence purpose
- bounded context (Foundation / Actors / Services)
- canvas(es) it appears on
- typed-text fields (if any) — these become the `foundation/{kind}-{id}.md` template lines
- relations (which other kinds it may parent / be parented by; which edge endpoints it accepts)

Format mirrors the existing 15 rows. Don't break alphabetical / context grouping.

### Step 2 — `docs/SPEC.md`: behaviour for the relevant canvas

For each canvas the new kind appears on, add bullets under that
canvas's "Nodes" subsection: render shape, palette, fold behaviour,
drill behaviour, edge endpoint legality. Use the existing 15 entries
as templates; banned phrases per `noory-ai/CLAUDE.md` apply.

### Step 3 — `viewer/src/domain/{Kind}.ts`: entity class

Pattern (from [`Mission.ts`](../../plot/viewer/src/domain/Mission.ts)):

```ts
// JSON wire shape
export interface {Kind}Json extends BaseFieldsJson {
  kind: "{kind}";
  // kind-specific JSON fields only — NO god union
}

// Domain class
export class {Kind} implements BaseFields {
  // BaseFields readonly fields (id, label, x, y, w, h, color, shape, …)
  readonly kind: "{kind}" = "{kind}";
  // kind-specific readonly fields

  private constructor(base: BaseFields, /* kind-specific args */) {
    Object.assign(this, base);
    // assign kind-specific
  }

  static fromJson(raw: unknown): {Kind} {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "{kind}") {
      throw new DomainParseError("expected kind '{kind}'", raw);
    }
    // parse + validate kind-specific fields
    return new {Kind}(base, /* args */);
  }

  toJson(): {Kind}Json {
    return {
      // base fields
      // kind-specific
      kind: "{kind}",
    };
  }
}

registerKindParser("{kind}", {Kind}.fromJson);
```

**Invariants** belong inside `fromJson` (throw `DomainParseError` on
violation) — not in setters, not in UI validation, not in toJson.
`fromJson` is the **JSON↔domain boundary** the v0.15 reset built; UI
imports the class, never the raw `{Kind}Json` interface.

### Step 4 — `viewer/src/domain/SketchNode.ts`: extend the union

```ts
export type SketchNode = Mission | CoreValue | … | {Kind};
export type SketchNodeJson = MissionJson | CoreValueJson | … | {Kind}Json;
```

Both lines, alphabetical order. The `parseEntity` registry already
picks up the new parser from Step 3's `registerKindParser` call.

### Step 5 — `viewer/src/domain/createBlankNode.ts`: factory case

Add a `case "{kind}":` branch with kind-specific defaults (typed-text
fields = `""`, container-shape defaults, palette colour from the
canvas's palette). Cross-check `viewer/src/canvases/sketch/palette.ts`.

### Step 6 — `viewer/src/domain/index.ts`: export

Add the class + JSON type to the barrel. Alphabetical.

### Step 7 — `plot_mcp/models/{kind}.py`: Pydantic model

Pydantic v2 model with the same fields as `{Kind}Json`. Discriminator
literal: `kind: Literal["{kind}"]`. Register in the union:
`plot_mcp/models/__init__.py::AnyNode = Annotated[Mission | … | {Kind}, Field(discriminator="kind")]`.

### Step 8 — `plot_mcp/tests/test_schema_parity.py`: parity case

`test_schema_parity.py` already iterates every kind and asserts
`{Kind}Json` (from `viewer/src/types.ts` generated schema) ≡ Pydantic
`{Kind}.model_json_schema()`. Adding the kind to both sides above
automatically lands here; run the test to confirm zero drift.

### Step 9 — `viewer/src/canvases/nodes/{kind}/index.tsx`: renderer

Wrap `BaseNode` with kind-specific chrome flags:

```tsx
export const {Kind}NodeRenderer = (props: NodeProps<{Kind}NodeData>) => (
  <BaseNode
    {...props}
    /* kind-specific flags */
  />
);
```

LOC ceiling 100 per `plot/CLAUDE.md` Gate 2.

### Step 10 — `viewer/src/canvases/inspectors/{kind}/index.tsx`: inspector

Renders inside `BaseInspector`'s slot. Typed-text fields use
`EditableText` with i18n keys from Step 12. LOC ceiling 250.

### Step 11 — Registry wiring

Two registries pick up the new files automatically *if* they follow
the directory convention:

```bash
# viewer/src/canvases/nodes/registry.ts auto-imports nodes/{kind}/index.tsx
# viewer/src/canvases/inspectors/registry.ts auto-imports inspectors/{kind}/index.tsx
```

Verify by running:

```bash
cd plot/viewer && npx vitest run -t "NODE_RENDERERS includes {kind}"
cd plot/viewer && npx vitest run -t "inspector registry includes {kind}"
```

### Step 12 — `viewer/src/i18n/locales/{en,ko}.json`: i18n keys

Every user-facing string for the new kind must land in **both**
locales. The `i18n-keys-parity.test.tsx` static guard fails the build
on drift. Per [D-2026-05-11-D](../../plot/docs/DECISIONS.md) — Novel is a
global service; no hardcoded strings.

Required keys (minimum):
- `kind.{kind}.label` — sidebar / stencil label
- `kind.{kind}.description` — tooltip
- `inspector.{kind}.field.{fieldName}` × N — per typed-text field
- `inspector.{kind}.field.{fieldName}.hint` × N — placeholder

### Step 13 — `viewer/tests/entity-roundtrip.test.tsx`: round-trip case

Per [Phase D of this batch](../../plot/docs/DECISIONS.md). The test
iterates every kind and asserts:

```ts
const json = /* sample {Kind}Json */;
const entity = {Kind}.fromJson(json);
expect(entity.toJson()).toEqual(json);
```

Add a `{kind}` row to the test's parameterised cases. If round-trip
fails, `toJson` is missing fields or `fromJson` is normalising —
either is a defect, fix in Step 3.

### Step 14 — `viewer/tests/structural-guards.test.tsx`: LOC ceiling

Add the new files to the LOC-ceiling table:
- `nodes/{kind}/index.tsx` — ceiling 100
- `inspectors/{kind}/index.tsx` — ceiling 250

Verify the test still passes after Steps 9-10.

---

## Verification (mandatory before claim "done")

```bash
cd plot/viewer && npx tsc --noEmit
cd plot/viewer && npx vitest run
cd plot && uv run pytest
cd plot && uv run mypy plot_mcp/
cd plot && uv run ruff check plot_mcp/ tests/
cd plot && uv run pytest tests/test_pre_commit_gate.py        # kill-switch
cd plot && uv run pytest tests/test_schema_parity.py          # schema-parity
```

Plus Gate 3 (hands-on browser) per `plot/CLAUDE.md` — the new kind
must be droppable from the stencil, draggable on the canvas, openable
in the inspector, and editable on every typed-text field.

---

## Documentation & decision pinning (Gate 4)

1. Bump `plot/.claude-plugin/plugin.json` patch / minor.
2. `plot/CHANGELOG.md` — Added section listing every file in the
   14-step walk.
3. `plot/docs/DECISIONS.md` — `D-YYYY-MM-DD-X` entry with:
   - **What:** the new kind + its bounded context + canvas placement.
   - **Why:** the product / spec / user need that justified it.
   - **Alternatives:** which existing kind was considered and rejected.
   - **Approval:** Accepted by user, date.
   - **Spec impact:** `CONCEPTS.md` row + `SPEC.md §{canvas} Nodes` bullet.
4. `plot/docs/SPEC.md` + `CONCEPTS.md` already updated in Steps 1-2.

---

## Anti-patterns this skill prevents

| Anti-pattern | Why blocked here |
|---|---|
| Adding a field to god `SketchNode` instead of new class | Step 3 forces a class with `fromJson` boundary; no-god-import hook (Phase C) blocks the alternative. |
| Adding a kind without per-kind UI files | Steps 9-10 mandatory; registries fail closed (registry test, structural-guards) if missing. |
| Skipping i18n for a "quick prototype" string | Step 12 mandatory; `i18n-keys-parity.test.tsx` fails the build. |
| Skipping the round-trip test | Step 13 mandatory; the test is the only proof `fromJson(toJson(x)) ≡ x`. |
| Skipping schema-parity update | Step 8 mandatory; `test_schema_parity.py` fails if `{Kind}Json` and Pydantic drift. |
| Bumping LOC ceilings silently | Step 14 explicit; ceiling-raise requires its own `D-YYYY-MM-DD-X` entry. |

---

## Companion skills

- [`plot-domain-design`](../plot-domain-design/SKILL.md) — *before*
  this skill: decide whether the new concept is an entity or a value
  object, which bounded context it lives in, and whether it really
  warrants a new kind at all.
- [`plot-feature-tdd`](../plot-feature-tdd/SKILL.md) — the upstream
  pipeline that calls into this skill when the feature is "a new
  kind".
- [`plot-design-red-team`](../plot-design-red-team/SKILL.md) — run
  *after* Step 14 but *before* committing; the adversarial attacks
  catch missing canvas-edge legality and palette collisions.
- [`plot-frontend-bug-diagnosis`](../plot-frontend-bug-diagnosis/SKILL.md)
  — if the new kind misbehaves after landing.
