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
    anchorArrowMode: "none",
  });
}

const ANCHOR = "__project_anchor__";

function runConstrained(edges: SketchEdge[]) {
  return edgeTransform({
    edges,
    serviceRef: null,
    nearestCollapsedAncestor: () => null,
    valueFlowOn: false,
    hideRootServiceNode: false,
    anchorArrowMode: "converge",
  });
}

function runDiverged(edges: SketchEdge[]) {
  return edgeTransform({
    edges,
    serviceRef: null,
    nearestCollapsedAncestor: () => null,
    valueFlowOn: false,
    hideRootServiceNode: false,
    anchorArrowMode: "diverge",
  });
}

describe("edgeTransform — anchor-ward arrow (D-2026-05-31-R)", () => {
  it("flips an edge drawn anchor→element so the arrow points at the anchor", () => {
    const [out] = runConstrained([makeEdge({ source: ANCHOR, target: "voice" })]);
    expect(out.source).toBe("voice");
    expect(out.target).toBe(ANCHOR);
  });

  it("keeps an element→anchor edge as-is", () => {
    const [out] = runConstrained([makeEdge({ source: "voice", target: ANCHOR })]);
    expect(out.source).toBe("voice");
    expect(out.target).toBe(ANCHOR);
  });

  it("actor tree: child→parent keeps the arrow at the parent (anchor-ward)", () => {
    const out = runConstrained([
      makeEdge({ id: "e_user_anchor", source: "user", target: ANCHOR }),
      makeEdge({ id: "e_bana_user", source: "bana", target: "user" }),
    ]);
    const e = out.find((x) => x.id === "e_bana_user")!;
    expect(e.source).toBe("bana");
    expect(e.target).toBe("user");
  });

  it("actor tree: a backwards parent→child edge is flipped toward the parent", () => {
    const out = runConstrained([
      makeEdge({ id: "e_user_anchor", source: "user", target: ANCHOR }),
      makeEdge({ id: "e_user_bana", source: "user", target: "bana" }),
    ]);
    const e = out.find((x) => x.id === "e_user_bana")!;
    expect(e.source).toBe("bana");
    expect(e.target).toBe("user");
  });

  it("does NOT reorient under anchorArrowMode 'none'", () => {
    const [out] = run(makeEdge({ source: ANCHOR, target: "voice" }));
    expect(out.source).toBe(ANCHOR);
    expect(out.target).toBe("voice");
  });
});

describe("edgeTransform — divergence (Services, D-2026-06-14-C)", () => {
  it("keeps an anchor→element edge pointing outward (arrow away from anchor)", () => {
    const [out] = runDiverged([makeEdge({ source: ANCHOR, target: "shop" })]);
    // markerEnd lands on rfTarget; for divergence it must be the non-anchor
    // node, so the arrow points away from the anchor.
    expect(out.source).toBe(ANCHOR);
    expect(out.target).toBe("shop");
  });

  it("flips an element→anchor edge so the arrow points outward", () => {
    const [out] = runDiverged([makeEdge({ source: "shop", target: ANCHOR })]);
    expect(out.source).toBe(ANCHOR);
    expect(out.target).toBe("shop");
  });

  it("service tree: a backwards service→category edge is flipped outward", () => {
    // anchor → category → service is the canonical divergence chain. An edge
    // drawn service→category (inward) must render category→service (outward).
    const out = runDiverged([
      makeEdge({ id: "e_anchor_cat", source: ANCHOR, target: "cat" }),
      makeEdge({ id: "e_svc_cat", source: "svc", target: "cat" }),
    ]);
    const e = out.find((x) => x.id === "e_svc_cat")!;
    expect(e.source).toBe("cat"); // anchor-ward end becomes the source
    expect(e.target).toBe("svc"); // arrow points outward at the service
  });
});

describe("edgeTransform — edge selection hit area (D-2026-06-14-C)", () => {
  it("widens the interaction band so edges are easy to click", () => {
    const [out] = run(makeEdge());
    expect(out.interactionWidth ?? 0).toBeGreaterThanOrEqual(24);
  });
});

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
