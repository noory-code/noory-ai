/**
 * Shape encodes producer-vs-reference — v0.29.3 (D-2026-05-31-B).
 *
 * 원본/master kinds (mission / core_value / identity / actor) render
 * as a **rounded rectangle (네모 — soft corners)**; symbol-reference
 * (`*_ref`) kinds render as a **circle (동그라미)**. This supersedes
 * D-2026-05-28-D (which made every Symbol kind a circle): the user
 * clarified the shape should distinguish the original (rounded
 * rectangle) from the symbol pointer that stands in for it (circle).
 *
 * `decision` stays a diamond (the shape IS the semantic, D-2026-05-30-C).
 * `project` (synthetic anchor) is excluded — its shape is a user
 * toggle (defaults to circle). Every other kind honours its stored
 * shape.
 */
import { describe, expect, it } from "vitest";
import { effectiveShape } from "../src/canvases/sketch/nodeShape";

describe("effectiveShape — producer vs reference (D-2026-05-31-B)", () => {
  it("renders master kinds as a rounded rectangle (원본 = 네모, soft corners)", () => {
    for (const kind of ["mission", "core_value", "identity", "actor"]) {
      expect(effectiveShape(kind, "circle")).toBe("rounded");
    }
  });

  it("renders symbol-reference kinds as circle (심볼 = 동그라미)", () => {
    for (const kind of [
      "actor_ref",
      "mission_ref",
      "value_ref",
      "identity_ref",
    ]) {
      expect(effectiveShape(kind, "rectangle")).toBe("circle");
    }
  });

  it("keeps decision as a diamond", () => {
    expect(effectiveShape("decision", "rectangle")).toBe("diamond");
  });

  it("leaves the project anchor's stored shape untouched (user toggle)", () => {
    expect(effectiveShape("project", "circle")).toBe("circle");
    expect(effectiveShape("project", "rectangle")).toBe("rectangle");
  });

  it("honours the stored shape for every other kind", () => {
    expect(effectiveShape("service", "circle")).toBe("circle");
    expect(effectiveShape("step", "rounded")).toBe("rounded");
    expect(effectiveShape("category", "rounded")).toBe("rounded");
    expect(effectiveShape(undefined, "ellipse")).toBe("ellipse");
  });
});
