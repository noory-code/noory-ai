import { describe, it, expect } from "vitest";
import { computeMindmapLayout } from "../src/canvases/sketch/mindmapLayout";
import type { SketchNode, SketchEdge } from "../src/types";

function node(id: string, x: number, y: number, width = 160, height = 80): SketchNode {
  return { id, kind: "service", label: id, x, y, width, height } as SketchNode;
}

function edge(source: string, target: string): SketchEdge {
  return { id: `${source}-${target}`, source, target, directed: true } as SketchEdge;
}

const HUB = { id: "hub", x: 0, y: 0, width: 120, height: 120 };

interface Box {
  x: number;
  y: number;
  w: number;
  h: number;
}

function boxesOf(
  positions: Map<string, { x: number; y: number }>,
  sizeById: Map<string, { w: number; h: number }>,
): Box[] {
  const out: Box[] = [];
  for (const [id, p] of positions) {
    const s = sizeById.get(id)!;
    out.push({ x: p.x, y: p.y, w: s.w, h: s.h });
  }
  return out;
}

function overlaps(a: Box, b: Box): boolean {
  // strict overlap with a tiny epsilon tolerance for touching edges
  const eps = 0.5;
  return (
    a.x < b.x + b.w - eps &&
    a.x + a.w - eps > b.x &&
    a.y < b.y + b.h - eps &&
    a.y + a.h - eps > b.y
  );
}

function dist(p: { x: number; y: number }, q: { x: number; y: number }): number {
  return Math.hypot(p.x - q.x, p.y - q.y);
}

function centerOf(
  positions: Map<string, { x: number; y: number }>,
  sizeById: Map<string, { w: number; h: number }>,
  id: string,
): { x: number; y: number } {
  const p = positions.get(id)!;
  const s = sizeById.get(id)!;
  return { x: p.x + s.w / 2, y: p.y + s.h / 2 };
}

/** A realistic BANAS-shaped graph: hub → 7 categories → 1-4 services each. */
function banasGraph(): { nodes: SketchNode[]; edges: SketchEdge[] } {
  const nodes: SketchNode[] = [node("hub", 0, 0, 120, 120)];
  const edges: SketchEdge[] = [];
  const cats: Record<string, number> = {
    auth: 1,
    onboard: 1,
    profile: 4,
    community: 2,
    noti: 1,
    landing: 1,
    ops: 1,
  };
  let i = 0;
  for (const [cat, nSvc] of Object.entries(cats)) {
    const cid = `c-${cat}`;
    // seed positions in a rough circle so any position-reading code has data
    const ang = (2 * Math.PI * i) / 7;
    nodes.push(node(cid, 300 * Math.cos(ang), 300 * Math.sin(ang)));
    edges.push(edge("hub", cid));
    for (let s = 0; s < nSvc; s++) {
      const sid = `s-${cat}-${s}`;
      nodes.push(node(sid, 500 * Math.cos(ang), 500 * Math.sin(ang)));
      edges.push(edge(cid, sid));
    }
    i++;
  }
  return { nodes, edges };
}

function sizes(nodes: SketchNode[]): Map<string, { w: number; h: number }> {
  const m = new Map<string, { w: number; h: number }>();
  for (const n of nodes) m.set(n.id, { w: n.width ?? 160, h: n.height ?? 80 });
  return m;
}

describe("computeMindmapLayout", () => {
  it("returns a position for every non-hub node", () => {
    const { nodes, edges } = banasGraph();
    const { positions } = computeMindmapLayout({ nodes, edges, hub: HUB });
    for (const n of nodes) {
      expect(positions.has(n.id)).toBe(true);
    }
  });

  it("places no two nodes overlapping (criterion 1)", () => {
    const { nodes, edges } = banasGraph();
    const { positions } = computeMindmapLayout({ nodes, edges, hub: HUB });
    const sz = sizes(nodes);
    const boxes = boxesOf(positions, sz);
    for (let a = 0; a < boxes.length; a++) {
      for (let b = a + 1; b < boxes.length; b++) {
        expect(
          overlaps(boxes[a], boxes[b]),
          `boxes ${a} and ${b} overlap`,
        ).toBe(false);
      }
    }
  });

  it("places each child nearer its parent than the hub (criterion 3: grouped)", () => {
    const { nodes, edges } = banasGraph();
    const { positions } = computeMindmapLayout({ nodes, edges, hub: HUB });
    const sz = sizes(nodes);
    const hubC = centerOf(positions, sz, "hub");
    // services should sit closer to their category than to the hub
    for (const e of edges) {
      if (!e.source.startsWith("c-")) continue; // only category→service edges
      const parentC = centerOf(positions, sz, e.source);
      const childC = centerOf(positions, sz, e.target);
      expect(
        dist(childC, parentC),
        `${e.target} should be nearer ${e.source} than hub`,
      ).toBeLessThan(dist(childC, hubC));
    }
  });

  it("spreads top-level branches across more than one direction (上下左右)", () => {
    const { nodes, edges } = banasGraph();
    const { positions } = computeMindmapLayout({ nodes, edges, hub: HUB });
    const sz = sizes(nodes);
    const hubC = centerOf(positions, sz, "hub");
    const cats = edges.filter((e) => e.source === "hub").map((e) => e.target);
    const dirs = new Set(
      cats.map((id) => {
        const c = centerOf(positions, sz, id);
        const dx = c.x - hubC.x;
        const dy = c.y - hubC.y;
        return Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? "R" : "L") : dy > 0 ? "D" : "U";
      }),
    );
    // 7 categories must not all pile onto one axis.
    expect(dirs.size).toBeGreaterThanOrEqual(3);
  });

  it("places each child on the outward side of its parent (tidy tree, no back-cross)", () => {
    const { nodes, edges } = banasGraph();
    const { positions } = computeMindmapLayout({ nodes, edges, hub: HUB });
    const sz = sizes(nodes);
    const hubC = centerOf(positions, sz, "hub");
    // every service is farther from the hub along its branch axis than its category
    for (const e of edges) {
      if (!e.source.startsWith("c-")) continue;
      const pc = centerOf(positions, sz, e.source);
      const cc = centerOf(positions, sz, e.target);
      const parentReach = Math.max(Math.abs(pc.x - hubC.x), Math.abs(pc.y - hubC.y));
      const childReach = Math.max(Math.abs(cc.x - hubC.x), Math.abs(cc.y - hubC.y));
      expect(childReach, `${e.target} must sit beyond ${e.source}`).toBeGreaterThan(parentReach);
    }
  });

  it("keeps user-grouped columns on their side (mission↑ / values← / identities→)", () => {
    // The user groups by PLACING: mission up, 5 core_value left, 14
    // identity right. Auto-layout respects each node's side — no per-kind
    // rule. Every node stays in the half-plane it was placed in.
    const nodes: SketchNode[] = [node("hub", 0, 0, 120, 120)];
    const edges: SketchEdge[] = [];
    const add = (id: string, kind: string, cx: number, cy: number) => {
      nodes.push({ id, kind, label: id, x: cx - 80, y: cy - 30, width: 160, height: 60 } as SketchNode);
      edges.push(edge("hub", id));
    };
    add("m", "mission", 60, -600); // up (hub centre is (60,60))
    for (let i = 0; i < 5; i++) add(`v-${i}`, "core_value", -600, 60 + i * 90); // left column
    for (let i = 0; i < 14; i++) add(`id-${i}`, "identity", 700, -500 + i * 90); // right column
    const { positions } = computeMindmapLayout({ nodes, edges, hub: HUB });
    const sz = sizes(nodes);
    const hubC = centerOf(positions, sz, "hub");
    const cxOf = (id: string) => centerOf(positions, sz, id).x;
    const cyOf = (id: string) => centerOf(positions, sz, id).y;
    const all = (prefix: string, pred: (id: string) => boolean) =>
      nodes.filter((n) => n.id.startsWith(prefix)).every((n) => pred(n.id));
    expect(all("id-", (id) => cxOf(id) > hubC.x), "identities all right").toBe(true);
    expect(all("v-", (id) => cxOf(id) < hubC.x), "values all left").toBe(true);
    expect(cyOf("m") < hubC.y, "mission above").toBe(true);
  });

  it("respects each branch's current side (D-2026-06-01-F)", () => {
    // hub + 4 leaves, each pre-placed on a distinct side of the hub.
    const nodes: SketchNode[] = [node("hub", 0, 0, 120, 120)];
    const edges: SketchEdge[] = [];
    // hub centre = (60,60). Place each branch clearly on one side.
    const place = (id: string, cx: number, cy: number) => {
      nodes.push({ id, kind: "category", label: id, x: cx - 80, y: cy - 30, width: 160, height: 60 } as SketchNode);
      edges.push(edge("hub", id));
    };
    place("up", 60, -400);
    place("down", 60, 520);
    place("left", -500, 60);
    place("right", 620, 60);
    const { positions } = computeMindmapLayout({ nodes, edges, hub: HUB });
    const sz = sizes(nodes);
    const hubC = centerOf(positions, sz, "hub");
    const arm = (id: string) => {
      const c = centerOf(positions, sz, id);
      const dx = c.x - hubC.x;
      const dy = c.y - hubC.y;
      return Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? "R" : "L") : dy > 0 ? "D" : "U";
    };
    expect(arm("up")).toBe("U");
    expect(arm("down")).toBe("D");
    expect(arm("left")).toBe("L");
    expect(arm("right")).toBe("R");
  });

  it("is deterministic (same input → identical output)", () => {
    const { nodes, edges } = banasGraph();
    const a = computeMindmapLayout({ nodes, edges, hub: HUB });
    const b = computeMindmapLayout({ nodes, edges, hub: HUB });
    for (const [id, p] of a.positions) {
      expect(b.positions.get(id)).toEqual(p);
    }
  });
});
