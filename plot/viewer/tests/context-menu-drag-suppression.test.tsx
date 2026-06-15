/**
 * Regression: a node drag that ends on a macOS trackpad emits a trailing
 * ``contextmenu`` event AFTER pointerup. React Flow's d3-drag only
 * suppresses ``contextmenu`` WHILE a drag is active, so the trailing event
 * leaks to ``onNodeContextMenu`` / ``onPaneContextMenu`` and the sketch
 * context menu pops up at the release point — the "drag a node, let go, it
 * acts like a right-click" bug (user report 2026-06-15).
 *
 * The fix (D-2026-06-15-N): ``useContextMenus`` arms a one-shot suppression
 * flag on ``onNodeDragStop``; the next ``contextmenu`` that arrives is
 * swallowed. A genuine right-click first fires ``pointerdown`` (button 2),
 * which disarms the flag, so deliberate right-clicks after a drag still open
 * the menu.
 */
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { MouseEvent as ReactMouseEvent } from "react";
import type { Edge, Node, ReactFlowInstance } from "reactflow";
import { useContextMenus } from "../src/canvases/sketch/useContextMenus";
import type { CanvasDoc } from "../src/types";

function makeArgs() {
  const docRef = {
    current: { canvas_kind: "services", nodes: [], edges: [] } as unknown as CanvasDoc,
  };
  const flowRef = {
    current: {
      screenToFlowPosition: (p: { x: number; y: number }) => p,
    } as unknown as ReactFlowInstance,
  };
  return {
    docRef,
    flowRef,
    onDocChange: vi.fn(),
    clipboard: {
      hasClip: () => false,
      copy: vi.fn(),
      duplicate: vi.fn(),
      paste: vi.fn(),
    } as never,
    handleNodesDelete: vi.fn(),
    handleEdgesDelete: vi.fn(),
    addNodeAt: vi.fn(),
    selectedNodeIds: { current: [] as string[] },
  };
}

function fakeEvent() {
  return {
    preventDefault: vi.fn(),
    clientX: 12,
    clientY: 34,
  } as unknown as ReactMouseEvent;
}

const NODE = { id: "n1" } as Node;
const EDGE = { id: "e1" } as Edge;

describe("context-menu drag suppression (D-2026-06-15-N)", () => {
  it("opens the node menu on a plain right-click (no preceding drag)", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => result.current.openNodeMenu(fakeEvent(), NODE));
    expect(result.current.menu).not.toBeNull();
  });

  it("suppresses the trailing contextmenu fired right after a node drag", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    const evt = fakeEvent();
    act(() => result.current.onNodeDragStop());
    act(() => result.current.openNodeMenu(evt, NODE));
    expect(evt.preventDefault).toHaveBeenCalled();
    expect(result.current.menu).toBeNull();
  });

  it("suppresses a trailing pane contextmenu after a drag too", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => result.current.onNodeDragStop());
    act(() => result.current.openPaneMenu(fakeEvent()));
    expect(result.current.menu).toBeNull();
  });

  it("only swallows ONE contextmenu — a second attempt opens normally", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => result.current.onNodeDragStop());
    act(() => result.current.openNodeMenu(fakeEvent(), NODE)); // swallowed
    act(() => result.current.openNodeMenu(fakeEvent(), NODE)); // opens
    expect(result.current.menu).not.toBeNull();
  });

  it("a deliberate right-click after a drag opens (pointerdown disarms)", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => result.current.onNodeDragStop());
    // A real right-click fires pointerdown before contextmenu — this disarms
    // the one-shot suppression.
    act(() => {
      window.dispatchEvent(new Event("pointerdown"));
    });
    act(() => result.current.openNodeMenu(fakeEvent(), NODE));
    expect(result.current.menu).not.toBeNull();
  });

  it("does not suppress the edge menu after a drag-unrelated open", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => result.current.openEdgeMenu(fakeEvent(), EDGE));
    expect(result.current.menu).not.toBeNull();
  });
});
