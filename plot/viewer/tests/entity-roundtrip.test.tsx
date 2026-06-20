/**
 * v0.16.28 — entity round-trip static guard (4 of 5 D-2026-05-12-B
 * catch-up artefacts, D-2026-05-13-E).
 *
 * For every ``NodeKind`` value, verifies that
 *
 *   parseEntity(createBlankNode(kind, base)).toJson() ===
 *     createBlankNode(kind, base)
 *
 * — i.e. ``fromJson`` (via ``parseEntity``) and ``toJson`` are
 * inverse operations on a canonical wire-shape input. If a kind's
 * entity class adds, drops, renames, or reorders fields between
 * fromJson and toJson, this guard catches it before the regression
 * reaches the React Flow render path.
 *
 * Companion to:
 *   - ``no-god-import.test.tsx`` (Phase C) — domain-layer integrity.
 *   - ``test_schema_parity.py`` (server side) — Pydantic ↔ JSON.
 *
 * Together the three guards keep the discriminated-union pattern
 * intact and protect against silent field drift between the wire
 * shape and the entity class.
 */
import { describe, expect, test } from "vitest";
import { createBlankNode } from "../src/domain/createBlankNode";
import { parseEntity } from "../src/domain/parseEntity";
import type { SketchNode } from "../src/domain/SketchNode";

const NODE_KINDS = [
  "project",
  "mission",
  "core_value",
  "identity",
  "actor",
  "actor_ref",
  "service",
  "feature",
  "rule",
  "content",
  "mission_ref",
  "value_ref",
  "identity_ref",
  "metric",
  "step",
  "decision",
  "category",
] as const satisfies readonly SketchNode["kind"][];

const BASE_BLANK = {
  id: "test-node-1",
  label: "Test Label",
  x: 100,
  y: 200,
  width: 240,
  height: 120,
  color: "#fff7ed",
  shape: "rectangle" as const,
  icon: null,
  parent_id: null,
};

// Per-kind overrides for the ref-family kinds, which require a
// non-null ``ref_*_id`` to land valid. Other kinds use the empty
// overrides (defaults inside the entity class).
const REF_OVERRIDES: Partial<Record<SketchNode["kind"], Record<string, string>>> = {
  actor_ref: { ref_actor_id: "actor-target-id" },
  mission_ref: { ref_mission_id: "mission-target-id" },
  value_ref: { ref_value_id: "value-target-id" },
  identity_ref: { ref_identity_id: "identity-target-id" },
};

describe("entity round-trip: fromJson(toJson(x)) === x", () => {
  test.each(NODE_KINDS)(
    "kind '%s' round-trips through parseEntity / toJson",
    (kind) => {
      const overrides = REF_OVERRIDES[kind] ?? {};
      const wireShape = createBlankNode(kind, BASE_BLANK, overrides);
      const entity = parseEntity(wireShape);
      const roundTripped = entity.toJson();
      expect(
        roundTripped,
        `kind '${kind}' lost fidelity through fromJson → toJson. ` +
          `Field-level diff between input and round-trip output indicates ` +
          `the entity class's fromJson normalises a field that toJson does ` +
          `not (or vice versa). See plot-entity-template SKILL.md Step 3.`,
      ).toEqual(wireShape);
    },
  );

  test("parseEntity dispatch covers every NodeKind", () => {
    for (const kind of NODE_KINDS) {
      const overrides = REF_OVERRIDES[kind] ?? {};
      const wireShape = createBlankNode(kind, BASE_BLANK, overrides);
      expect(
        () => parseEntity(wireShape),
        `parseEntity must accept kind '${kind}' — registerKindParser ` +
          `call missing from domain/${kind}.ts? See no-god-import.test.tsx ` +
          `for the per-kind file guard.`,
      ).not.toThrow();
    }
  });
});
