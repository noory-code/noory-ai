/**
 * Edge "Flip direction" context-menu action — v0.29.2
 * (D-2026-05-31-A).
 *
 * The edge context menu (``useContextMenus.openEdgeMenu``) previously
 * only toggled ``directed`` on/off. The user asked for a way to
 * *flip* an edge's orientation ("서비스 캔버스에서 연결선 방향을 바꿀
 * 수 있는 기능"), resolving the open "Direction switch UI" thread.
 *
 * Flip swaps ``source`` ↔ ``target`` so the arrowhead points the
 * other way, via the regular ``onDocChange`` (Cmd+Z undoes it).
 * Handles are typed by side (BaseNode: t/l target-only, r/b
 * source-only), so the old handle ids can't carry over — they are
 * nulled and RF re-routes through each node's default valid handle.
 * All edges stay user-drawn — this just re-orients one the user drew.
 */
import { renderHook } from "@testing-library/react";
import { act } from "react";
import { describe, expect, it, vi } from "vitest";
import type { Edge } from "reactflow";
import { useContextMenus } from "../src/canvases/sketch/useContextMenus";
import type { ContextMenuItem } from "../src/canvases/SketchContextMenu";
import type { CanvasDoc, SketchEdge } from "../src/types";

function makeDoc(edge: SketchEdge): CanvasDoc {
  return {
    canvas_id: "c1",
    canvas_kind: "services",
    nodes: [],
    edges: [edge],
  } as unknown as CanvasDoc;
}

function makeEdge(): SketchEdge {
  return {
    id: "e1",
    source: "a",
    target: "b",
    sourceHandle: "a-right",
    targetHandle: "b-left",
    label: "",
    style: "solid",
    directed: true,
    action_verb: null,
    value_form: [],
  } as unknown as SketchEdge;
}

function renderMenus(doc: CanvasDoc, onDocChange: (d: CanvasDoc) => void) {
  const docRef = { current: doc };
  return renderHook(() =>
    useContextMenus({
      docRef,
      flowRef: { current: null },
      onDocChange,
      clipboard: { hasClip: () => false } as never,
      handleNodesDelete: vi.fn(),
      handleEdgesDelete: vi.fn(),
      addNodeAt: vi.fn(),
      selectedNodeIds: { current: [] },
    }),
  );
}

function fakeEvent() {
  return { preventDefault: vi.fn(), clientX: 0, clientY: 0 } as never;
}

describe("edge flip direction", () => {
  it("offers a Flip direction item on the edge menu", () => {
    const { result } = renderMenus(makeDoc(makeEdge()), vi.fn());
    act(() => result.current.openEdgeMenu(fakeEvent(), { id: "e1" } as Edge));
    const labels = (result.current.menu?.items ?? []).map(
      (i: ContextMenuItem) => i.label,
    );
    expect(labels.some((l) => l.toLowerCase().includes("flip"))).toBe(true);
  });

  it("swaps source<->target and nulls the handles on select", () => {
    const onDocChange = vi.fn();
    const { result } = renderMenus(makeDoc(makeEdge()), onDocChange);
    act(() => result.current.openEdgeMenu(fakeEvent(), { id: "e1" } as Edge));
    const flip = (result.current.menu?.items ?? []).find((i: ContextMenuItem) =>
      i.label.toLowerCase().includes("flip"),
    );
    expect(flip).toBeDefined();
    flip!.onSelect();

    expect(onDocChange).toHaveBeenCalledTimes(1);
    const next = onDocChange.mock.calls[0][0] as CanvasDoc;
    const e = next.edges[0];
    expect(e.source).toBe("b");
    expect(e.target).toBe("a");
    // typed handles can't carry over → nulled so RF re-routes validly.
    expect(e.sourceHandle).toBeNull();
    expect(e.targetHandle).toBeNull();
    // directed flag is preserved (flip is orientation only).
    expect(e.directed).toBe(true);
  });
});
