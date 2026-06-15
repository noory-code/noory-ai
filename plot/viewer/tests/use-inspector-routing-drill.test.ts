/**
 * useInspectorRouting — select-opens-drill scoping (D-2026-06-15-H).
 *
 * Single-clicking a drillable node opens its detail tab ONLY when the canvas
 * sets ``selectOpensDrill`` (Services). Otherwise (Service-Detail canvas, where
 * actor_ref is drillable on DOUBLE-click) a single click opens the inspector,
 * so actor_ref clicks don't navigate away.
 */
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { MutableRefObject } from "react";
import type { ReactFlowInstance, Node } from "reactflow";

import { useInspectorRouting } from "../src/canvases/sketch/useInspectorRouting";
import type { SketchNode } from "../src/types";

const flowRef = { current: null } as MutableRefObject<ReactFlowInstance | null>;
const svc = { id: "s1", kind: "service" } as unknown as SketchNode;
const actorRef = { id: "a1", kind: "actor_ref" } as unknown as SketchNode;
const isService = (n: SketchNode) => n.kind === "service";

function clickNode(id: string): Node {
  return { id } as Node;
}

describe("useInspectorRouting — selectOpensDrill (D-2026-06-15-H)", () => {
  it("single-click drills when selectOpensDrill + shouldDrill match", () => {
    const onNodeDrill = vi.fn();
    const { result } = renderHook(() =>
      useInspectorRouting({
        nodes: [svc],
        flowRef,
        selectNodeId: null,
        onSelectionConsumed: undefined,
        onNodeDrill,
        shouldDrill: isService,
        selectOpensDrill: true,
      }),
    );
    act(() => result.current.onNodeClick({}, clickNode("s1")));
    expect(onNodeDrill).toHaveBeenCalledWith("s1");
    expect(result.current.inspectorNodeId).toBeNull(); // no inspector
  });

  it("single-click opens the inspector (no drill) when selectOpensDrill is false", () => {
    const onNodeDrill = vi.fn();
    const { result } = renderHook(() =>
      useInspectorRouting({
        nodes: [actorRef],
        flowRef,
        selectNodeId: null,
        onSelectionConsumed: undefined,
        onNodeDrill,
        shouldDrill: (n) => n.kind === "actor_ref",
        selectOpensDrill: false, // Service-Detail canvas
      }),
    );
    act(() => result.current.onNodeClick({}, clickNode("a1")));
    expect(onNodeDrill).not.toHaveBeenCalled(); // no jump-to-actor on single click
    expect(result.current.inspectorNodeId).toBe("a1");
  });

  it("single-click opens the inspector for non-drillable nodes even with selectOpensDrill", () => {
    const onNodeDrill = vi.fn();
    const { result } = renderHook(() =>
      useInspectorRouting({
        nodes: [actorRef],
        flowRef,
        selectNodeId: null,
        onSelectionConsumed: undefined,
        onNodeDrill,
        shouldDrill: isService, // actor_ref is NOT drillable here
        selectOpensDrill: true,
      }),
    );
    act(() => result.current.onNodeClick({}, clickNode("a1")));
    expect(onNodeDrill).not.toHaveBeenCalled();
    expect(result.current.inspectorNodeId).toBe("a1");
  });

  it("double-click still drills regardless of selectOpensDrill", () => {
    const onNodeDrill = vi.fn();
    const { result } = renderHook(() =>
      useInspectorRouting({
        nodes: [actorRef],
        flowRef,
        selectNodeId: null,
        onSelectionConsumed: undefined,
        onNodeDrill,
        shouldDrill: (n) => n.kind === "actor_ref",
        selectOpensDrill: false,
      }),
    );
    act(() => result.current.onNodeDoubleClick({}, clickNode("a1")));
    expect(onNodeDrill).toHaveBeenCalledWith("a1");
  });
});
