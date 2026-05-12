/**
 * Static guard: every NodeKind has a registered React Flow renderer.
 * Failure means a per-kind canvas would crash with "no component for
 * type X" when a node of the unmigrated kind appears.
 */
import { describe, expect, it } from "vitest";
import { NODE_RENDERERS } from "../../src/canvases/nodes/registry";
import { shouldShowKindTag } from "../../src/canvases/nodes/BaseNode";

describe("nodes/registry", () => {
  it("registers all 15 NodeKind entries", () => {
    expect(Object.keys(NODE_RENDERERS).sort()).toEqual(
      [
        "actor",
        "actor_ref",
        "category",
        "content",
        "core_value",
        "identity",
        "identity_ref",
        "metric",
        "mission",
        "mission_ref",
        "project",
        "rule",
        "service",
        "step",
        "value_ref",
      ].sort(),
    );
  });

  it("every entry is a callable component", () => {
    for (const [kind, Component] of Object.entries(NODE_RENDERERS)) {
      expect(typeof Component).toBe("function");
      expect(Component, `no renderer for kind ${kind}`).toBeTruthy();
    }
  });
});

describe("BaseNode.shouldShowKindTag", () => {
  it("returns true only for rectangle / rounded shapes", () => {
    expect(shouldShowKindTag("rectangle")).toBe(true);
    expect(shouldShowKindTag("rounded")).toBe(true);
    expect(shouldShowKindTag("circle")).toBe(false);
    expect(shouldShowKindTag("ellipse")).toBe(false);
    expect(shouldShowKindTag("diamond")).toBe(false);
    expect(shouldShowKindTag("hexagon")).toBe(false);
    expect(shouldShowKindTag("octagon")).toBe(false);
  });
});
