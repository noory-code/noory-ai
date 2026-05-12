/**
 * Stable-handlers regression — v0.16.16 (D-2026-05-12-R).
 *
 * Refetch storm root cause: App.tsx's inline arrow callbacks passed
 * to useProject / useCanvasPersist / useProjectSocket were recreated
 * on every render. That cascaded into useProject's loadList being
 * rebuilt every render (it deps on onError), which under specific
 * WS event timings caused infinite fetch loops.
 *
 * Fix: ``useStableHandlers`` returns useCallback-wrapped handlers so
 * the downstream hooks see stable callback references. This test
 * asserts the identity stability across renders.
 */
import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useStableHandlers } from "../src/hooks/useStableHandlers";
import type { CanvasDoc, CanvasKey, ProjectTag } from "../src/types";

function makeDeps() {
  const setCanvasCache = ((updater: unknown) => {
    void updater;
  }) as React.Dispatch<React.SetStateAction<Map<CanvasKey, CanvasDoc>>>;
  const setTags = ((updater: unknown) => {
    void updater;
  }) as React.Dispatch<React.SetStateAction<ProjectTag[]>>;
  const loadList = () => Promise.resolve();
  const historyClear = () => {};
  return { setCanvasCache, setTags, loadList, historyClear };
}

describe("useStableHandlers — identity stability", () => {
  it("returns identically-referenced handlers across re-renders when deps are stable", () => {
    const deps = makeDeps();
    const { result, rerender } = renderHook(() => useStableHandlers(deps));
    const first = { ...result.current };
    rerender();
    expect(result.current.handleListStale).toBe(first.handleListStale);
    expect(result.current.handleExternalCanvas).toBe(first.handleExternalCanvas);
    expect(result.current.handleTagsRefresh).toBe(first.handleTagsRefresh);
    expect(result.current.handleExternalChange).toBe(first.handleExternalChange);
  });

  it("returns a new handleListStale only when loadList ref changes", () => {
    const deps = makeDeps();
    const { result, rerender } = renderHook(
      ({ d }: { d: ReturnType<typeof makeDeps> }) => useStableHandlers(d),
      { initialProps: { d: deps } },
    );
    const firstHandleListStale = result.current.handleListStale;
    // Re-render with the SAME deps → identity stable.
    rerender({ d: deps });
    expect(result.current.handleListStale).toBe(firstHandleListStale);
    // Re-render with a NEW loadList → identity changes.
    const newDeps = { ...deps, loadList: () => Promise.resolve() };
    rerender({ d: newDeps });
    expect(result.current.handleListStale).not.toBe(firstHandleListStale);
  });

  it("handleExternalCanvas calls setCanvasCache with the produced Map updater", () => {
    let captured: unknown = null;
    const setCanvasCache = ((updater: unknown) => {
      captured = updater;
    }) as React.Dispatch<React.SetStateAction<Map<CanvasKey, CanvasDoc>>>;
    const deps = { ...makeDeps(), setCanvasCache };
    const { result } = renderHook(() => useStableHandlers(deps));
    const fakeDoc = {
      id: "x",
      name: "X",
      created: "",
      updated: "",
      version: 1,
      nodes: [],
      edges: [],
    } as unknown as CanvasDoc;
    result.current.handleExternalCanvas("foundation" as CanvasKey, fakeDoc);
    expect(typeof captured).toBe("function");
    // Apply the captured updater to a sample previous Map; expect the
    // canvas to be added.
    const prev = new Map<CanvasKey, CanvasDoc>();
    const next = (captured as (m: Map<CanvasKey, CanvasDoc>) => Map<CanvasKey, CanvasDoc>)(
      prev,
    );
    expect(next.get("foundation" as CanvasKey)).toBe(fakeDoc);
  });

  it("handleExternalChange calls historyClear", () => {
    let cleared = 0;
    const deps = { ...makeDeps(), historyClear: () => (cleared += 1) };
    const { result } = renderHook(() => useStableHandlers(deps));
    result.current.handleExternalChange();
    expect(cleared).toBe(1);
  });

  it("handleListStale invokes loadList", () => {
    let called = 0;
    const deps = {
      ...makeDeps(),
      loadList: () => {
        called += 1;
        return Promise.resolve();
      },
    };
    const { result } = renderHook(() => useStableHandlers(deps));
    result.current.handleListStale();
    expect(called).toBe(1);
  });
});
