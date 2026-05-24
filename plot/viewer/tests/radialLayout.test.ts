// Unit tests for the pure ``computeRadialLayout`` algorithm. Pins the
// behaviour codified in SPEC.md §Auto-layout / DECISIONS.md
// D-2026-05-24-B. JSDOM-only — no React Flow / browser dependency.

import { describe, expect, it } from "vitest";
import {
  computeRadialLayout,
  type RadialLayoutHub,
} from "../src/canvases/sketch/radialLayout";
import type { SketchEdge, SketchNode } from "../src/types";

function mkNode(id: string, x = 0, y = 0, w = 80, h = 36): SketchNode {
  return {
    id,
    label: id,
    x,
    y,
    width: w,
    height: h,
    color: "#fff",
    shape: "rounded",
    icon: null,
    kind: null,
    parent_id: null,
    collapsed: false,
    is_root: false,
    mission: "",
    core_values: "",
    identity: "",
    what_we_do: "",
    why: "",
    direction: "",
    definition: "",
    description: "",
    do: "",
    dont: "",
    what: "",
    value_created: "",
    scope: "",
    trigger: "",
    how: "",
    outcome: "",
    target: "",
    measurement: "",
    order: null,
    policy: "",
    enforcement: "",
    actor_permissions: {},
    format: "",
    producer_actor_id: null,
    consumer_actor_id: null,
    motivation: "",
    pain: "",
    side: null,
    gives: "",
    receives: "",
    target_side: null,
    theme: "",
    ref_actor_id: null,
    ref_mission_id: null,
    ref_value_id: null,
    ref_identity_id: null,
  };
}

function mkEdge(id: string, source: string, target: string): SketchEdge {
  return {
    id,
    source,
    target,
    sourceHandle: null,
    targetHandle: null,
    label: "",
    style: "solid",
    action_verb: null,
    value_form: [],
  };
}

const HUB: RadialLayoutHub = {
  id: "__hub__",
  x: 0,
  y: 0,
  width: 80,
  height: 36,
};

describe("computeRadialLayout — ring assignment", () => {
  it("places a single neighbour directly above the hub centre", () => {
    const { positions } = computeRadialLayout({
      nodes: [mkNode("a")],
      edges: [mkEdge("e1", "__hub__", "a")],
      hub: HUB,
    });
    const p = positions.get("a")!;
    // Hub centre is (40, 18). Ring 1 angle starts at -π/2 (top).
    // Radius = hubSpan/2 + ringSpan/2 + gap = 40 + 40 + 40 = 120 (with
    // hubSpan = max(80, 36) = 80 and node span = 80).
    expect(Math.round(p.x)).toBe(0); // 40 - 80/2
    // y = hubCy + radius * sin(-π/2) - h/2 = 18 - 120 - 18 = -120
    expect(Math.round(p.y)).toBe(-120);
  });

  it("distributes 3 ring-1 neighbours at 120° intervals", () => {
    const { positions } = computeRadialLayout({
      nodes: [mkNode("a"), mkNode("b"), mkNode("c")],
      edges: [
        mkEdge("e1", "__hub__", "a"),
        mkEdge("e2", "__hub__", "b"),
        mkEdge("e3", "__hub__", "c"),
      ],
      hub: HUB,
    });
    expect(positions.size).toBe(3);
    // Determinism: sorted by id — a/b/c at angles -π/2, -π/2 + 2π/3,
    // -π/2 + 4π/3. Compare distances from hub centre — they must be
    // identical.
    const hubCx = 40;
    const hubCy = 18;
    const dist = (id: string) => {
      const p = positions.get(id)!;
      const cx = p.x + 40;
      const cy = p.y + 18;
      return Math.hypot(cx - hubCx, cy - hubCy);
    };
    const dA = dist("a");
    const dB = dist("b");
    const dC = dist("c");
    expect(Math.abs(dA - dB)).toBeLessThan(1e-6);
    expect(Math.abs(dA - dC)).toBeLessThan(1e-6);
  });

  it("assigns multi-hop neighbours to outer rings", () => {
    // hub - a - b   →   a on ring 1, b on ring 2
    const { positions } = computeRadialLayout({
      nodes: [mkNode("a"), mkNode("b")],
      edges: [mkEdge("e1", "__hub__", "a"), mkEdge("e2", "a", "b")],
      hub: HUB,
    });
    const hubCx = 40;
    const hubCy = 18;
    const dist = (id: string) => {
      const p = positions.get(id)!;
      const cx = p.x + 40;
      const cy = p.y + 18;
      return Math.hypot(cx - hubCx, cy - hubCy);
    };
    expect(dist("b")).toBeGreaterThan(dist("a"));
  });

  it("places orphan nodes (no edge to hub) in a grid below the rings", () => {
    const { positions } = computeRadialLayout({
      nodes: [mkNode("a"), mkNode("orphan1"), mkNode("orphan2")],
      edges: [mkEdge("e1", "__hub__", "a")],
      hub: HUB,
    });
    expect(positions.has("orphan1")).toBe(true);
    expect(positions.has("orphan2")).toBe(true);
    // Orphans must land below the ring-1 node a (greater y).
    const pa = positions.get("a")!;
    const po1 = positions.get("orphan1")!;
    const po2 = positions.get("orphan2")!;
    expect(po1.y).toBeGreaterThan(pa.y);
    expect(po2.y).toBeGreaterThan(pa.y);
  });

  it("never includes the hub itself in the positions map", () => {
    const { positions } = computeRadialLayout({
      nodes: [mkNode("a")],
      edges: [mkEdge("e1", "__hub__", "a")],
      hub: HUB,
    });
    expect(positions.has("__hub__")).toBe(false);
  });

  it("works when the hub also appears in nodes (hidden root-service case)", () => {
    // ServiceDetail's hub is the hidden root-service node, which lives
    // inside ``doc.nodes``. The algorithm must still skip it.
    const hub: RadialLayoutHub = {
      id: "svc-root",
      x: 100,
      y: 200,
      width: 80,
      height: 36,
    };
    const { positions } = computeRadialLayout({
      nodes: [mkNode("svc-root", 100, 200), mkNode("a")],
      edges: [mkEdge("e1", "svc-root", "a")],
      hub,
    });
    expect(positions.has("svc-root")).toBe(false);
    expect(positions.has("a")).toBe(true);
  });

  it("returns an empty positions map for an isolated hub (no edges)", () => {
    const { positions } = computeRadialLayout({
      nodes: [],
      edges: [],
      hub: HUB,
    });
    expect(positions.size).toBe(0);
  });

  it("is deterministic — same input produces same output", () => {
    const input = {
      nodes: [mkNode("z"), mkNode("a"), mkNode("m")],
      edges: [
        mkEdge("e1", "__hub__", "z"),
        mkEdge("e2", "__hub__", "a"),
        mkEdge("e3", "__hub__", "m"),
      ],
      hub: HUB,
    };
    const out1 = computeRadialLayout(input);
    const out2 = computeRadialLayout(input);
    for (const id of ["a", "m", "z"]) {
      expect(out1.positions.get(id)).toEqual(out2.positions.get(id));
    }
  });
});
