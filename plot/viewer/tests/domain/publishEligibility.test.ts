/**
 * v0.18.0 Phase 3 (D-2026-05-16-E) — viewer-side publish eligibility
 * mirror of ``plot_mcp/md_publish.py::can_publish``.
 *
 * Parametric over all 15 kinds + the is_root flag.
 */
import { describe, expect, it } from "vitest";
import { canPublish } from "../../src/domain/publishEligibility";
import type { SketchNode } from "../../src/domain/SketchNode";

function makeNode(
  kind: SketchNode["kind"],
  overrides: Partial<SketchNode> = {},
): SketchNode {
  // Minimal SketchNode shape — the helper only reads ``kind`` +
  // ``is_root``. Cast as never to skirt the per-kind discriminator
  // (the helper is kind-agnostic by design).
  return {
    id: "test",
    label: "test",
    x: 0,
    y: 0,
    width: 180,
    height: 80,
    color: "#fff",
    shape: "rounded",
    icon: null,
    parent_id: null,
    collapsed: false,
    is_root: false,
    details_path: null,
    owner: null,
    version: "v1.0",
    kind,
    ...overrides,
  } as never;
}

describe("canPublish", () => {
  it("rejects the project anchor", () => {
    expect(canPublish(makeNode("project"))).toBe(false);
  });

  it("rejects is_root service (ServiceDetail mirror)", () => {
    expect(canPublish(makeNode("service", { is_root: true }))).toBe(false);
  });

  it("accepts is_root actor (master; D-2026-05-19-C)", () => {
    expect(canPublish(makeNode("actor", { is_root: true }))).toBe(true);
  });

  it("rejects the actor_ref kind (the only surviving standalone ref)", () => {
    expect(canPublish(makeNode("actor_ref"))).toBe(false);
  });

  it.each([
    "mission",
    "core_value",
    "identity",
    "category",
    "step",
    "rule",
  ] as const)("accepts typed kind '%s'", (kind) => {
    expect(canPublish(makeNode(kind))).toBe(true);
  });

  it.each(["actor", "service"] as const)(
    "accepts non-root kind '%s'",
    (kind) => {
      expect(canPublish(makeNode(kind, { is_root: false }))).toBe(true);
    },
  );
});
