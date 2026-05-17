// Unit tests for the pure ``computeAutoLayout`` algorithm. Pins the
// behaviour codified in SPEC.md §Auto-layout / DECISIONS.md
// D-2026-05-10-E. JSDOM-only — no React Flow / browser dependency.

import { describe, expect, it } from "vitest";
import {
  computeAutoLayout,
  handleToDirection,
  inferDirection,
} from "../src/canvases/sketch/autoLayout";
import type { SketchEdge, SketchNode } from "../src/types";

function mkNode(id: string, x = 0, y = 0, w = 200, h = 80): SketchNode {
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

function mkEdge(
  id: string,
  source: string,
  target: string,
  sourceHandle: string | null = null,
  targetHandle: string | null = null,
): SketchEdge {
  return {
    id,
    source,
    target,
    sourceHandle,
    targetHandle,
    label: "",
    style: "solid",
    action_verb: null,
    value_form: [],
  };
}

const ANCHOR = { id: "__anchor__", x: 0, y: 0, width: 200, height: 200 };

describe("computeAutoLayout — direction grouping", () => {
  it("places R-handle child to the right of anchor", () => {
    const nodes = [mkNode("m1")];
    const edges = [mkEdge("e1", ANCHOR.id, "m1", "r", "l")];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    const m1 = positions.get("m1")!;
    expect(m1.x).toBeGreaterThan(ANCHOR.x + ANCHOR.width / 2);
    // Vertically centred on anchor → m1.y center == anchor.y center
    const m1Cy = m1.y + 80 / 2;
    const anchorCy = ANCHOR.y + ANCHOR.height / 2;
    expect(m1Cy).toBeCloseTo(anchorCy, 5);
  });

  it("places T-handle child above anchor", () => {
    const nodes = [mkNode("i1")];
    const edges = [mkEdge("e1", ANCHOR.id, "i1", "t", "b")];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    const i1 = positions.get("i1")!;
    expect(i1.y + 80).toBeLessThanOrEqual(ANCHOR.y); // entire i1 above anchor
  });

  it("multiple R children stack in a vertical column on the right (no overlap)", () => {
    const nodes = [mkNode("m1"), mkNode("m2"), mkNode("m3")];
    const edges = [
      mkEdge("e1", ANCHOR.id, "m1", "r", "l"),
      mkEdge("e2", ANCHOR.id, "m2", "r", "l"),
      mkEdge("e3", ANCHOR.id, "m3", "r", "l"),
    ];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    const ps = ["m1", "m2", "m3"].map((id) => positions.get(id)!);
    // All to the right of anchor
    for (const p of ps) expect(p.x).toBeGreaterThan(ANCHOR.x + ANCHOR.width / 2);
    // Same x (column)
    expect(ps[0].x).toBe(ps[1].x);
    expect(ps[1].x).toBe(ps[2].x);
    // No vertical overlap (sorted by id since all Rs)
    const sortedByY = [...ps].sort((a, b) => a.y - b.y);
    for (let i = 1; i < sortedByY.length; i++) {
      expect(sortedByY[i].y).toBeGreaterThanOrEqual(sortedByY[i - 1].y + 80);
    }
  });

  it("R-connected nodes do NOT migrate downward (handle direction is strict)", () => {
    // Five children all on R; classical mistake would push some to B
    // when right gets crowded. Spec forbids that.
    const nodes = ["a", "b", "c", "d", "e"].map((id) => mkNode(id));
    const edges = nodes.map((n, i) => mkEdge(`e${i}`, ANCHOR.id, n.id, "r", "l"));
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    for (const n of nodes) {
      const p = positions.get(n.id)!;
      expect(p.x).toBeGreaterThan(ANCHOR.x + ANCHOR.width / 2);
    }
  });

  it("groups by direction independently — R + T + L children each in own region", () => {
    const nodes = [mkNode("r1"), mkNode("t1"), mkNode("l1")];
    const edges = [
      mkEdge("e1", ANCHOR.id, "r1", "r", "l"),
      mkEdge("e2", ANCHOR.id, "t1", "t", "b"),
      mkEdge("e3", ANCHOR.id, "l1", "l", "r"),
    ];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    expect(positions.get("r1")!.x).toBeGreaterThan(ANCHOR.x + ANCHOR.width / 2);
    expect(positions.get("l1")!.x + 200).toBeLessThanOrEqual(ANCHOR.x);
    expect(positions.get("t1")!.y + 80).toBeLessThanOrEqual(ANCHOR.y);
  });
});

describe("computeAutoLayout — recursion + no overlap", () => {
  it("grandchild attaches in its own incoming-handle direction", () => {
    // Anchor -R-> mission, mission -B-> sub
    const nodes = [mkNode("mission"), mkNode("sub")];
    const edges = [
      mkEdge("e1", ANCHOR.id, "mission", "r", "l"),
      mkEdge("e2", "mission", "sub", "b", "t"),
    ];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    const mission = positions.get("mission")!;
    const sub = positions.get("sub")!;
    // sub is below mission (entirely below)
    expect(sub.y).toBeGreaterThanOrEqual(mission.y + 80);
    // mission is to the right of anchor
    expect(mission.x).toBeGreaterThan(ANCHOR.x + ANCHOR.width / 2);
  });

  it("subtree extent expands to fit grandchildren without overlapping siblings", () => {
    // Anchor -R-> M1 with 3 R-grandchildren
    // Anchor -R-> M2 (no grandchildren)
    // Both M1 and M2 are R children of anchor; M1's grandchildren must
    // not overlap M2.
    const nodes = [
      mkNode("m1"),
      mkNode("m2"),
      mkNode("g1"),
      mkNode("g2"),
      mkNode("g3"),
    ];
    const edges = [
      mkEdge("e1", ANCHOR.id, "m1", "r", "l"),
      mkEdge("e2", ANCHOR.id, "m2", "r", "l"),
      mkEdge("e3", "m1", "g1", "r", "l"),
      mkEdge("e4", "m1", "g2", "r", "l"),
      mkEdge("e5", "m1", "g3", "r", "l"),
    ];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    // No two nodes overlap pairwise
    const ids = ["m1", "m2", "g1", "g2", "g3"];
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        const a = positions.get(ids[i])!;
        const b = positions.get(ids[j])!;
        const aRight = a.x + 200;
        const aBottom = a.y + 80;
        const bRight = b.x + 200;
        const bBottom = b.y + 80;
        const xOverlap = a.x < bRight && b.x < aRight;
        const yOverlap = a.y < bBottom && b.y < aBottom;
        expect(xOverlap && yOverlap).toBe(false);
      }
    }
  });
});

describe("computeAutoLayout — determinism + cycle handling", () => {
  it("same input produces same output across runs", () => {
    const nodes = [mkNode("a"), mkNode("b"), mkNode("c")];
    const edges = [
      mkEdge("e1", ANCHOR.id, "a", "r", "l"),
      mkEdge("e2", ANCHOR.id, "b", "r", "l"),
      mkEdge("e3", ANCHOR.id, "c", "r", "l"),
    ];
    const r1 = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    const r2 = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    for (const id of ["a", "b", "c"]) {
      expect(r1.positions.get(id)).toEqual(r2.positions.get(id));
    }
  });

  it("handles cycles via BFS spanning tree (no infinite loop)", () => {
    // Anchor -R-> a, a -R-> b, b -R-> a (cycle back)
    const nodes = [mkNode("a"), mkNode("b")];
    const edges = [
      mkEdge("e1", ANCHOR.id, "a", "r", "l"),
      mkEdge("e2", "a", "b", "r", "l"),
      mkEdge("e3", "b", "a", "r", "l"), // cycle
    ];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    expect(positions.has("a")).toBe(true);
    expect(positions.has("b")).toBe(true);
  });
});

describe("computeAutoLayout — isolated nodes", () => {
  it("places nodes not reachable from anchor in a lower-right grid (no overlap)", () => {
    // v0.24.2 (D-2026-05-17-N) — isolated nodes pack into a square-ish
    // grid (not a single column). 2 orphans = 2 columns × 1 row so they
    // share the same y, differ in x; cells never collide because the
    // grid step = max(width)+padding / max(height)+padding.
    const nodes = [mkNode("connected"), mkNode("orphan1"), mkNode("orphan2")];
    const edges = [mkEdge("e1", ANCHOR.id, "connected", "r", "l")];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    expect(positions.has("orphan1")).toBe(true);
    expect(positions.has("orphan2")).toBe(true);
    const o1 = positions.get("orphan1")!;
    const o2 = positions.get("orphan2")!;
    // Grid: 2 nodes → 2 columns × 1 row → same y, different x.
    expect(o1.y).toBe(o2.y);
    expect(o1.x).not.toBe(o2.x);
  });
});

describe("computeAutoLayout — handle inference fallback", () => {
  it("infers direction from current position when sourceHandle is null", () => {
    // Place "right" node already to the right of anchor; null handles
    // should infer R direction.
    const right = mkNode("right", 500, 0);
    const nodes = [right];
    const edges = [mkEdge("e1", ANCHOR.id, "right", null, null)];
    const { positions } = computeAutoLayout({ nodes, edges, anchor: ANCHOR });
    const p = positions.get("right")!;
    expect(p.x).toBeGreaterThan(ANCHOR.x + ANCHOR.width / 2);
  });
});

describe("handleToDirection / inferDirection helpers", () => {
  it("maps handle keys to canonical directions", () => {
    expect(handleToDirection("t")).toBe("T");
    expect(handleToDirection("top")).toBe("T");
    expect(handleToDirection("R")).toBe("R");
    expect(handleToDirection("bottom")).toBe("B");
    expect(handleToDirection("l")).toBe("L");
    expect(handleToDirection("xyz")).toBe("R"); // fallback
  });

  it("infers direction from positional delta", () => {
    expect(inferDirection({ x: 0, y: 0 }, { x: 100, y: 5 })).toBe("R");
    expect(inferDirection({ x: 0, y: 0 }, { x: -100, y: 5 })).toBe("L");
    expect(inferDirection({ x: 0, y: 0 }, { x: 5, y: 100 })).toBe("B");
    expect(inferDirection({ x: 0, y: 0 }, { x: 5, y: -100 })).toBe("T");
  });
});
