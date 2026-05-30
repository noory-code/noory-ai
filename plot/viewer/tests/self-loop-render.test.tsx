/**
 * Self-loop rendering — v0.16.10 (D-2026-05-12-M).
 *
 * Three contracts:
 *   1. ``edgeTransform`` emits ``type: "selfLoop"`` for an edge with
 *      ``source === target`` whose endpoints don't collapse to a
 *      different ancestor.
 *   2. The pure ``selfLoopPath`` helper produces a non-degenerate
 *      cubic Bezier path (visible arc) even at zero-length input.
 *   3. Collapsed-ancestor "fake self-loop" case still gets filtered
 *      (cross-subtree edge that now resolves to the same parent must
 *      not render as a self-loop).
 */
import { describe, expect, it } from "vitest";
import { edgeTransform } from "../src/canvases/sketch/edgeTransform";
import { selfLoopPath } from "../src/canvases/edges/SelfLoopEdge";
import type { SketchEdge } from "../src/types";

function makeEdge(overrides: Partial<SketchEdge>): SketchEdge {
  return {
    id: "e1",
    source: "a",
    target: "b",
    sourceHandle: null,
    targetHandle: null,
    label: "",
    style: "solid",
    value_form: [],
    ...overrides,
  };
}

describe("edgeTransform — real self-loop (D-2026-05-12-M)", () => {
  it("emits type=selfLoop for source===target with no collapsed ancestor", () => {
    const out = edgeTransform({
      edges: [makeEdge({ id: "loop", source: "a", target: "a", label: "feedback" })],
      serviceRef: null,
      nearestCollapsedAncestor: () => null,
      valueFlowOn: false,
      hideRootServiceNode: false,
    });
    expect(out).toHaveLength(1);
    expect(out[0]).toMatchObject({
      id: "loop",
      source: "a",
      target: "a",
      type: "selfLoop",
      label: "feedback",
    });
  });

  it("preserves value-flow recolouring on self-loop", () => {
    const out = edgeTransform({
      edges: [
        makeEdge({
          id: "loop",
          source: "a",
          target: "a",
          value_form: ["economic"],
        }),
      ],
      serviceRef: null,
      nearestCollapsedAncestor: () => null,
      valueFlowOn: true,
      hideRootServiceNode: false,
    });
    expect(out).toHaveLength(1);
    expect(out[0].type).toBe("selfLoop");
    expect(out[0].style).toBeDefined();
  });
});

describe("edgeTransform — collapsed-ancestor fake self-loop (regression)", () => {
  it("filters edge whose endpoints collapse into the same ancestor", () => {
    // a and b are different nodes; both collapse into parent "P".
    // After collapse-tree resolution, src === tgt = "P" — but the
    // *original* edge was a real cross-node edge, not a self-loop.
    const out = edgeTransform({
      edges: [makeEdge({ source: "a", target: "b" })],
      serviceRef: null,
      nearestCollapsedAncestor: () => "P",
      valueFlowOn: false,
      hideRootServiceNode: false,
    });
    expect(out).toEqual([]);
  });

  it("filters edge where only one side collapses to the other endpoint", () => {
    // a is independent, b collapses to a. Cross-subtree edge that
    // now looks like a self-loop on "a" — must NOT render as self-loop.
    const out = edgeTransform({
      edges: [makeEdge({ source: "a", target: "b" })],
      serviceRef: null,
      nearestCollapsedAncestor: (id) => (id === "b" ? "a" : null),
      valueFlowOn: false,
      hideRootServiceNode: false,
    });
    expect(out).toEqual([]);
  });
});

describe("edgeTransform — regular non-self-loop is a floating edge", () => {
  it("emits a floating-type edge for a → b (v0.30.3, D-2026-05-31-F)", () => {
    const out = edgeTransform({
      edges: [makeEdge({ source: "a", target: "b" })],
      serviceRef: null,
      nearestCollapsedAncestor: () => null,
      valueFlowOn: false,
      hideRootServiceNode: false,
    });
    expect(out).toHaveLength(1);
    expect(out[0].source).toBe("a");
    expect(out[0].target).toBe("b");
    expect(out[0].type).toBe("floating");
  });
});

describe("selfLoopPath — non-degenerate arc", () => {
  it("produces a cubic Bezier from a zero-distance input", () => {
    const { path, labelX, labelY } = selfLoopPath(100, 100, 100, 100);
    expect(path).toMatch(/^M 100,100 C /);
    // The two control points are bulged 100 above/aside the source,
    // so the curve's apex sits visibly off the source point.
    expect(labelY).toBeLessThan(100); // above the source
  });

  it("produces an arc when source and target differ (handle-to-handle)", () => {
    const { path } = selfLoopPath(0, 0, 100, 0);
    expect(path).toMatch(/^M 0,0 C /);
    expect(path).toContain("100,0");
  });
});
