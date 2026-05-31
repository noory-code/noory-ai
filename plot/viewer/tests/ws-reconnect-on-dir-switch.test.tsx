/**
 * The project WebSocket reconnects when the effective project path (dir)
 * changes, and does NOT when it stays the same — v0.33.0 (D-2026-05-31-M).
 */
import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../src/api";
import { useProjectSocket } from "../src/hooks/useProjectSocket";
import type { CanvasKey } from "../src/types";

vi.mock("../src/api");

function args(path: string) {
  return {
    projectPath: path,
    activeId: "p1",
    pendingWrites: { current: new Set<CanvasKey>() } as React.MutableRefObject<Set<CanvasKey>>,
    onListStale: vi.fn(),
    onExternalCanvas: vi.fn(),
    onTagsRefresh: vi.fn(),
    onExternalChange: vi.fn(),
    onError: vi.fn(),
  };
}

beforeEach(() => {
  vi.mocked(api.openProjectSocket).mockReset();
});

describe("WS reconnect on dir switch (D-2026-05-31-M)", () => {
  it("reconnects when the effective path changes, not when it stays the same", () => {
    const closes: Array<() => void> = [];
    vi.mocked(api.openProjectSocket).mockImplementation(() => {
      const close = vi.fn();
      closes.push(close);
      return { close } as never;
    });

    const { rerender } = renderHook((p: { path: string }) => useProjectSocket(args(p.path)), {
      initialProps: { path: "/repo/a" },
    });
    expect(api.openProjectSocket).toHaveBeenCalledTimes(1);

    // same dir (e.g. switching between two projects under /repo/a) → no reconnect
    rerender({ path: "/repo/a" });
    expect(api.openProjectSocket).toHaveBeenCalledTimes(1);

    // different dir → old socket closed + new socket opened
    rerender({ path: "/repo/b" });
    expect(closes[0]).toHaveBeenCalled();
    expect(api.openProjectSocket).toHaveBeenCalledTimes(2);
    expect(vi.mocked(api.openProjectSocket).mock.calls[1][0]).toBe("/repo/b");
  });
});
