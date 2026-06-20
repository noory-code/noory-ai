/**
 * Exhaustive 13-kind entity round-trip — Phase 5.1 (D-2026-05-12-B).
 *
 * Companion to ``round-trip.test.ts`` (per-kind hand-written asserts
 * built up Phase 2.1 → 2.10). This file is the structural sweep:
 *
 *   For every NodeKind in the 13-way discriminated union:
 *
 *     1. ``parseEntity(raw)`` dispatches to a class instance.
 *     2. ``Class.fromJson(entity.toJson()).toJson()`` is deeply
 *        equal to ``entity.toJson()`` (idempotent round-trip).
 *     3. ``parseEntity(entity.toJson())`` returns a same-kind class
 *        instance.
 *
 * Drift detection: a new kind without ``parseEntity`` dispatch fails
 * step 1; a typed-field default mismatch fails step 2; a misregistered
 * class fails step 3.
 */
import { describe, expect, it } from "vitest";
import { parseEntity } from "../../src/domain";
import { createBlankNode } from "../../src/domain/createBlankNode";
import type { NodeKind } from "../../src/types";

const ALL_KINDS: NodeKind[] = [
  "project",
  "mission",
  "core_value",
  "identity",
  "actor",
  "actor_ref",
  "service",
  "feature",
  "category",
  "step",
  "decision",
  "note",
  "rule",
];

function defaultRaw(kind: NodeKind) {
  return createBlankNode(kind, {
    id: `${kind}-1`,
    label: kind,
    x: 0,
    y: 0,
    width: 180,
    height: 80,
    color: "#ffffff",
    shape: "rounded",
    icon: null,
    parent_id: null,
  });
}

describe("parseEntity → 13-kind dispatch (Phase 5.1)", () => {
  it.each(ALL_KINDS)("returns a class instance for kind=%s", (kind) => {
    const raw = defaultRaw(kind);
    const node = parseEntity(raw);
    expect(node, `parseEntity returned null/undefined for kind=${kind}`).toBeTruthy();
    expect(node.kind).toBe(kind);
  });
});

describe("Entity round-trip — 13-kind idempotence (Phase 5.1)", () => {
  it.each(ALL_KINDS)(
    "fromJson(toJson()) is deeply equal to toJson() for kind=%s",
    (kind) => {
      const raw = defaultRaw(kind);
      const first = parseEntity(raw);
      const firstJson = first.toJson();
      const second = parseEntity(firstJson);
      const secondJson = second.toJson();
      expect(secondJson, `round-trip drift for kind=${kind}`).toEqual(firstJson);
    },
  );

  it.each(ALL_KINDS)(
    "round-tripped instance has the same kind as the source for kind=%s",
    (kind) => {
      const raw = defaultRaw(kind);
      const first = parseEntity(raw);
      const second = parseEntity(first.toJson());
      expect(second.kind, `kind drift for ${kind}`).toBe(first.kind);
    },
  );
});
