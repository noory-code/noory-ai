/**
 * v0.28.1 (D-2026-05-30-D) — foundation-injection edge styling.
 *
 * An edge whose SOURCE node is a foundation ref (mission_ref /
 * value_ref / identity_ref) renders as an "injection" edge: animated
 * (marching dashes toward the target) + violet stroke. Derived from
 * the source node kind, not a stored flag.
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
    action_verb: null,
    value_form: [],
    ...over,
  };
}

function run(edge: SketchEdge, kindBySource: Record<string, string>) {
  return edgeTransform({
    edges: [edge],
    serviceRef: null,
    nearestCollapsedAncestor: () => null,
    valueFlowOn: false,
    hideRootServiceNode: false,
    nodeKindById: (id) => kindBySource[id],
  });
}

describe("edgeTransform — foundation-injection styling (D-2026-05-30-D)", () => {
  it.each(["value_ref", "mission_ref", "identity_ref"])(
    "marks an edge from a %s source as injection (animated + violet)",
    (refKind) => {
      const [out] = run(makeEdge(), { src: refKind });
      expect(out.animated).toBe(true);
      expect(out.style?.stroke).toBe(INJECTION_STROKE);
    },
  );

  it("does NOT mark an ordinary step→step edge as injection", () => {
    const [out] = run(makeEdge(), { src: "step", tgt: "step" });
    expect(out.animated).toBeFalsy();
    expect(out.style?.stroke).not.toBe(INJECTION_STROKE);
  });

  it("does NOT treat an actor_ref source as injection (it is the subject anchor)", () => {
    const [out] = run(makeEdge(), { src: "actor_ref" });
    expect(out.animated).toBeFalsy();
    expect(out.style?.stroke).not.toBe(INJECTION_STROKE);
  });
});
