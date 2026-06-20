/**
 * Drill rewire (D-2026-06-17-D): on the Services overview the **feature** is
 * the sole drill target. Selecting a service shows its inspector (no drill);
 * clicking a feature drills into its detail. This pins the wrapper predicate
 * ``ServicesCanvas`` hands to ``useInspectorRouting`` via ``shouldDrill``.
 */
import { describe, expect, it } from "vitest";
import { shouldDrillFeature } from "../src/canvases/ServicesCanvas";
import type { SketchNode } from "../src/types";

const node = (kind: string, extra: Record<string, unknown> = {}): SketchNode =>
  ({ id: "n1", kind, ...extra }) as unknown as SketchNode;

describe("ServicesCanvas drill target = feature (D-2026-06-17-D)", () => {
  it("a feature node drills", () => {
    expect(shouldDrillFeature(node("feature"))).toBe(true);
  });

  it("a service node does NOT drill (it opens its inspector instead)", () => {
    expect(shouldDrillFeature(node("service"))).toBe(false);
    // even a non-root service must not drill
    expect(shouldDrillFeature(node("service", { is_root: false }))).toBe(false);
  });

  it("a category / actor_ref / project node does NOT drill", () => {
    expect(shouldDrillFeature(node("category"))).toBe(false);
    expect(shouldDrillFeature(node("actor_ref"))).toBe(false);
    expect(shouldDrillFeature(node("project", { is_root: true }))).toBe(false);
  });
});
