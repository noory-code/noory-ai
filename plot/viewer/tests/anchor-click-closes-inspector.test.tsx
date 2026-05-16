/**
 * v0.17.1 (D-2026-05-16-B) — Clicking the synthetic project anchor
 * must close any currently-open Inspector. The v0.13 behaviour
 * (early-return no-op) left the previously-selected node's content
 * stale on screen after the user moved focus to the anchor.
 *
 * Regression guard for ``useInspectorRouting.onNodeClick`` —
 * `PROJECT_ANCHOR_ID` branch must set `inspectorNodeId` to null.
 */
import { act, renderHook } from "@testing-library/react";
import type { Node } from "reactflow";
import { describe, expect, it } from "vitest";
import { PROJECT_ANCHOR_ID } from "../src/canvases/sketch/constants";
import { useInspectorRouting } from "../src/canvases/sketch/useInspectorRouting";

const fakeFlowRef = { current: null } as never;

function fakeNode(id: string): Node {
  return { id, position: { x: 0, y: 0 }, data: {} } as unknown as Node;
}

describe("useInspectorRouting — anchor click closes Inspector (D-2026-05-16-B)", () => {
  it("clicking the project anchor while an inspector is open closes it", () => {
    const { result } = renderHook(() =>
      useInspectorRouting({
        nodes: [],
        flowRef: fakeFlowRef,
        selectNodeId: null,
        onSelectionConsumed: undefined,
        onNodeDrill: undefined,
      }),
    );

    // 1. open Inspector on a normal node
    act(() => {
      result.current.onNodeClick(null, fakeNode("regular-node-id"));
    });
    expect(result.current.inspectorNodeId).toBe("regular-node-id");

    // 2. click the synthetic anchor → Inspector closes
    act(() => {
      result.current.onNodeClick(null, fakeNode(PROJECT_ANCHOR_ID));
    });
    expect(result.current.inspectorNodeId).toBeNull();
  });

  it("clicking the project anchor while no inspector is open stays closed (no-op)", () => {
    const { result } = renderHook(() =>
      useInspectorRouting({
        nodes: [],
        flowRef: fakeFlowRef,
        selectNodeId: null,
        onSelectionConsumed: undefined,
        onNodeDrill: undefined,
      }),
    );

    expect(result.current.inspectorNodeId).toBeNull();
    act(() => {
      result.current.onNodeClick(null, fakeNode(PROJECT_ANCHOR_ID));
    });
    expect(result.current.inspectorNodeId).toBeNull();
  });
});
