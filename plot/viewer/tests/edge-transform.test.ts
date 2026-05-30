/**
 * Injection edge styling — v0.28.1 (D-2026-05-30-D), reworked
 * v0.30.1 (D-2026-05-31-D).
 *
 * An edge whose stored ``relation`` is ``injection`` renders animated
 * (marching dashes toward the target) + violet stroke. The styling is
 * now driven by the stored ``relation`` SSOT, not re-derived from the
 * source node kind (the kind→relation mapping is covered by
 * ``edge-semantics.test.ts``).
 */
import { describe, expect, it } from "vitest";
import { edgeTransform } from "../src/canvases/sketch/edgeTransform";
import type { SketchEdge } from "../src/types";

const INJECTION_STROKE = "#8b5cf6";

function makeEdge(over: Partial<SketchEdge> = {}): SketchEdge {
  return {
    id: "e1",
    source: "src",
    target: "tgt",
    sourceHandle: null,
    targetHandle: null,
    label: "",
    style: "solid",
    directed: true,
    relation: "flow",
    action_verb: null,
    value_form: [],
    ...over,
  };
}

function run(edge: SketchEdge) {
  return edgeTransform({
    edges: [edge],
    serviceRef: null,
    nearestCollapsedAncestor: () => null,
    valueFlowOn: false,
    hideRootServiceNode: false,
  });
}

describe("edgeTransform — injection styling (D-2026-05-31-D)", () => {
  it("marks an injection-relation edge as animated + violet", () => {
    const [out] = run(makeEdge({ relation: "injection" }));
    expect(out.animated).toBe(true);
    expect(out.style?.stroke).toBe(INJECTION_STROKE);
  });

  it("does NOT mark a flow edge as injection", () => {
    const [out] = run(makeEdge({ relation: "flow" }));
    expect(out.animated).toBeFalsy();
    expect(out.style?.stroke).not.toBe(INJECTION_STROKE);
  });

  it("does NOT mark an inheritance edge as injection", () => {
    const [out] = run(makeEdge({ relation: "inheritance" }));
    expect(out.animated).toBeFalsy();
    expect(out.style?.stroke).not.toBe(INJECTION_STROKE);
  });
});
