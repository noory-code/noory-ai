---
name: mashbill-domain-design
description: Procedure for placing a new domain concept into Novel's bounded-context map *before* writing code. Forces a decision tree — is this a new entity (own id, own kind) or a value-object (embedded in another)? Which bounded context owns it (Discovery / Retention / Planning / Execution / AICollaboration)? Does the existing 15-kind palette already cover it? Triggers on "design", "도메인 설계", "어디다 둘까", "where does this go", "bounded context", "DDD", "entity vs value", "domain layer", "도메인 레이어". Prevents the v0.13.3-v0.13.10 cursor saga's root cause (no domain map → every fix picks an ad-hoc location → next bug surfaces elsewhere).
metadata:
  version: "1.0.0"
  category: dev-process
  type: unit
  style: procedure
  triggers:
    - "design"
    - "도메인 설계"
    - "어디다 둘까"
    - "where does this go"
    - "bounded context"
    - "DDD"
    - "entity vs value"
    - "domain layer"
    - "도메인 레이어"
    - "domain design"
    - "어디에 두지"
  uses: []
---

# mashbill-domain-design — placing a new concept before writing code

> **Why this skill exists.** Novel's v0.13.3 → v0.13.10 cursor saga
> (six rounds, see [D-2026-05-10-C](../../mashbill/docs/DECISIONS.md),
> [D-2026-05-10-F](../../mashbill/docs/DECISIONS.md)) was caused by no domain
> map: every fix picked "where does this rule live?" without a
> framework, and the next bug surfaced in a different ad-hoc location.
> [DOMAIN.md](../../mashbill/docs/DOMAIN.md) ended that by giving every concern
> a bounded-context home. **This skill is the gate** that forces the
> placement decision *before* any code lands.
>
> Without it, the next session's new concept will repeat the v0.13.3
> mistake.

---

## When to invoke

Run this skill **before** [`mashbill-entity-template`](../mashbill-entity-template/SKILL.md)
or [`mashbill-feature-tdd`](../mashbill-feature-tdd/SKILL.md) when:

- The user proposes a *new* concept Novel doesn't yet model.
  Examples: *"budget"*, *"decision log"*, *"risk"*, *"timeline"*.
- The user proposes a rule whose location isn't obvious. Examples:
  *"selection should follow drag direction"*, *"the badge should mean
  X on Foundation and Y on Services"*.
- Implementation is ambiguous between two bounded contexts. Example:
  *"value-flow recolour"* — does it belong to Retention (visual link
  metadata) or Planning (value-creation machinery)?

If the proposed concept is already a known kind or already has a clear
home, skip this skill — go directly to the implementation pipeline.

---

## The 5 decisions (no skipping)

### Decision 1 — Is it a *thing* or a *rule*?

| Type | Definition | Example | Next step |
|---|---|---|---|
| **Thing** | Has identity (an id), can be created / deleted / referenced. | A new `risk` kind. | Continue to Decision 2. |
| **Rule** | Constraint / behaviour, no id, no instance count. | "Drag selection follows cursor direction". | Skip to Decision 4 (bounded context only). |

### Decision 2 — Entity or value-object?

For *things* only. Both end up as classes in `viewer/src/domain/`; the
distinction is whether the user can address it directly.

| Type | Has its own id? | Can be a node on a canvas? | Example in Novel |
|---|:---:|:---:|---|
| **Entity** | Yes | Yes (rendered as a `BaseNode`) | `Mission`, `Service`, `Actor` |
| **Value-object** | No | No (embedded inside an entity) | `BaseFields` (shared shape), the `MissionJson["why"]` typed text |

If **entity** → run [`mashbill-entity-template`](../mashbill-entity-template/SKILL.md)
14-step walk *after* finishing this skill. If **value-object** → just
add a TypeScript type + Pydantic field; no new class, no new UI files,
no new kind discriminator.

### Decision 3 — Does an existing kind already cover it?

Open `docs/CONCEPTS.md` and read all 15 rows. For each candidate
existing kind, ask:

- Does the existing kind's *purpose* (column 2) overlap ≥ 70 % with
  the proposed concept?
- Would the proposed concept be a *specialisation* of the existing
  one (e.g. *"funded-project"* is just `Project` with one extra field)?
- Would the new fields the proposed concept needs fit into an existing
  kind without bloating its purpose statement?

| If any answer is YES | If all answers are NO |
|---|---|
| Reuse the existing kind. Add the new fields to its `{Kind}.ts` class + Pydantic model. Document the extension in `DECISIONS.md`. **No new kind discriminator.** | Continue to Decision 4. |

The MECE rule (`noory-ai/CLAUDE.md`): new kinds must not overlap
with existing ones. The v0.14 `Category` vs `Service` confusion (which
took 3 iterations to resolve, see [D-2026-04-28-X](../../mashbill/docs/DECISIONS.md))
is the canonical "should have reused" case.

### Decision 4 — Which bounded context owns it?

Open [`DOMAIN.md`](../../mashbill/docs/DOMAIN.md) §"Bounded contexts (5)" and
match the new concept against each context's **Owns** / **Does NOT
own** lists:

| Bounded context | Owns | Code home |
|---|---|---|
| **EssenceDiscovery** | Foundation typed text (mission / core_value / identity), section schemas, ⚠ badge | `plot_mcp/foundation/`, Foundation inspectors |
| **EssenceRetention** | Synthetic project anchor, cross-canvas refs (`*_ref`), anchor mutation routing | `viewer/src/canvases/sketch/useNodesMemo.ts` (inject), `applyAnchorChange.ts`, `plot_mcp/projects/anchors.py` |
| **EssencePlanning** | Actors / Services / Categories / value-flow toggle, edge `value_form` semantics | `viewer/src/canvases/Actors/Services`, `plot_mcp/services/` |
| **EssenceExecution** | Work-item layer (future — v0.17+ per ROADMAP) | (none yet) |
| **AICollaboration** | Cross-cutting agent prompts, MCP tool surface, skills | `mashbill/agents/`, `mashbill/skills/`, `plot_mcp/tools/` |

A concept that fits **two** contexts is a flag — the concept is
probably *two* concepts that should split. Don't ship as one.

A concept that fits **none** is also a flag — open a
`D-YYYY-MM-DD-X` entry first asking whether DOMAIN.md needs a sixth
bounded context. Don't quietly create one.

### Decision 5 — SSOT location

Within the chosen bounded context, identify the single source of
truth:

| Concept shape | SSOT location |
|---|---|
| User-typed text | `foundation/{kind}-{id}.md` (per node) |
| Node position / size | `ProjectDoc.canvases[canvasKind].nodes[id]` (JSON) |
| Anchor position | `ProjectDoc.anchors[canvasKind]` (NOT in nodes — see D-2026-05-04-X) |
| Edge | `ProjectDoc.canvases[canvasKind].edges[]` (user-drawn only — D-2026-05-04-A) |
| Per-canvas behaviour flag | Canvas wrapper prop (`hideRootServiceNode`, `shouldDrill`, etc.) |
| Per-kind UI behaviour | `BaseNode` flag set by `nodes/{kind}/index.tsx` |
| Cross-kind invariant | `viewer/src/domain/{Kind}.ts::fromJson` |
| Cursor / pan / zoom rule | `viewer/src/styles.css` with `!important` + D-id comment (per [D-2026-05-11-A](../../mashbill/docs/DECISIONS.md)) |

If the SSOT location doesn't yet exist for the proposed concept,
**that's the design decision** — name where it goes *before* writing
code. Reading from two places later means refactoring; choosing the
right home now means linear future evolution.

---

## Output (the design document)

After running this skill, write a short Decision summary to be pasted
into `DECISIONS.md` *before* implementation begins:

```markdown
### D-YYYY-MM-DD-X — Add {concept name}

- **What:** {concept} as a {entity | value-object | rule}
  in {bounded context}.
- **Why:** {user need / spec line / VISION-phase fit}.
- **SSOT location:** {file path or schema location}.
- **Alternatives considered:** {existing kind X | sibling context Y};
  rejected because {reason}.
- **Spec impact:** CONCEPTS.md row {N}; SPEC.md §{canvas} Nodes bullet.
- **Approval:** Pending — user, YYYY-MM-DD.
```

Get user approval on this summary **before** invoking
`mashbill-entity-template` or any code edit. Approval pins the placement
so the next session sees the decision and doesn't re-litigate.

---

## Anti-patterns this skill prevents

| Anti-pattern | Why blocked here |
|---|---|
| Inventing a new kind for what was really a field on an existing one | Decision 3 forces the overlap check; the 15-row scan happens before any code. |
| Putting AI-collaboration logic into a canvas component | Decision 4 forces the bounded-context placement against DOMAIN.md's explicit "Does NOT own" lists. |
| Mixing two bounded contexts in one entity | Decision 4 flags two-context concepts as split candidates. |
| Implementing a rule with no SSOT (so it lives implicitly in three places) | Decision 5 forces an explicit SSOT pick *before* code lands. |
| Quietly growing DOMAIN.md beyond 5 bounded contexts | Decision 4's "fits none" branch forces a `D-` entry first. |
| Repeating the cursor-saga ad-hoc location pick | The whole skill is the framework the cursor saga lacked. |

---

## Companion skills

- [`mashbill-entity-template`](../mashbill-entity-template/SKILL.md) —
  runs *after* this skill when the new concept is an entity. This
  skill picks the home; the entity-template skill walks the 14 files
  to land it.
- [`mashbill-feature-tdd`](../mashbill-feature-tdd/SKILL.md) — runs *after*
  this skill for non-entity changes (rules, behaviour, refactors).
- [`mashbill-design-red-team`](../mashbill-design-red-team/SKILL.md) —
  optional sanity check: feed this skill's design document through
  the 8 adversarial attacks before pinning the decision.
