/**
 * D-2026-06-13-E — a nested drop (service into category, sub-actor into
 * actor, …) materialises a directed parent→child edge, but that edge carries
 * NO visible verb label. The old "decomposes" label was clutter (user
 * 2026-06-13). The directed edge + relation still carry the structure.
 */
import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useNodeCreation } from "../src/canvases/sketch/useNodeCreation";
import { createBlankNode } from "../src/domain";
import type { CanvasDoc } from "../src/types";

describe("nested drop edge (D-2026-06-13-E)", () => {
  it("creates a directed parent→child edge with no verb label", () => {
    const parent = createBlankNode("category", {
      id: "cat",
      label: "Cat",
      x: 0,
      y: 0,
      width: 140,
      height: 50,
      color: "#e2e8f0",
      shape: "rectangle",
      icon: null,
    });
    const doc: CanvasDoc = {
      canvas_id: "services",
      canvas_kind: "services",
      service_ref: null,
      nodes: [parent],
      edges: [],
    };
    const docRef = { current: doc };
    let next: CanvasDoc | undefined;
    const { result } = renderHook(() =>
      useNodeCreation({ docRef, onDocChange: (d) => { next = d; } }),
    );

    result.current.addNestedNodeAt({
      parentId: "cat",
      localX: 10,
      localY: 10,
      preset: { kind: "service", shape: "rectangle", color: "#bae6fd" },
    });

    expect(next).toBeDefined();
    const edge = next!.edges[next!.edges.length - 1];
    expect(edge.source).toBe("cat");
    expect(edge.directed).toBe(true);
    expect(edge.label).toBe("");
    expect(edge.action_verb).toBeNull();
  });
});
