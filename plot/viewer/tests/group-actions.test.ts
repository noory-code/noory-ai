/**
 * v0.29.0 (D-2026-05-30-I) — group / ungroup actions.
 */
import { describe, expect, it } from "vitest";
import { groupSelected, ungroup } from "../src/canvases/sketch/groupActions";
import type { CanvasDoc, SketchNode } from "../src/types";

function step(id: string, x: number, y: number): SketchNode {
  return {
    id, kind: "step", label: id, x, y, width: 150, height: 60,
    color: "#fff", shape: "rounded", icon: null, collapsed: false,
    is_root: false, details_path: null, owner: null, version: "v1.0",
    order: null, outcome: "", body: "", polarity: "neutral",
  } as unknown as SketchNode;
}

function doc(nodes: SketchNode[]): CanvasDoc {
  return {
    id: "d", name: "d", canvas_kind: "service_detail",
    service_ref: null, nodes, edges: [],
  } as unknown as CanvasDoc;
}

describe("groupSelected (D-2026-05-30-I)", () => {
  it("creates a group node with member_ids = the selection, above the members", () => {
    const d = doc([step("a", 100, 200), step("b", 400, 260)]);
    const out = groupSelected(d, ["a", "b"], "g1");
    const g = out.nodes.find((n) => n.id === "g1");
    expect(g).toBeTruthy();
    expect(g!.kind).toBe("group");
    expect((g as unknown as { member_ids: string[] }).member_ids.sort()).toEqual(["a", "b"]);
    // placed above the topmost member (minY 200) by height + gap.
    expect(g!.y).toBeLessThan(200);
    // members untouched.
    expect(out.nodes.find((n) => n.id === "a")!.x).toBe(100);
  });

  it("is a no-op for fewer than 2 members", () => {
    const d = doc([step("a", 0, 0)]);
    expect(groupSelected(d, ["a"], "g1")).toBe(d);
  });
});

describe("ungroup (D-2026-05-30-I)", () => {
  it("removes the group node and leaves members", () => {
    const d = doc([step("a", 0, 0), step("b", 0, 0)]);
    const grouped = groupSelected(d, ["a", "b"], "g1");
    const out = ungroup(grouped, "g1");
    expect(out.nodes.find((n) => n.id === "g1")).toBeUndefined();
    expect(out.nodes.find((n) => n.id === "a")).toBeTruthy();
    expect(out.nodes.find((n) => n.id === "b")).toBeTruthy();
  });
});
