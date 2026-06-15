/**
 * Viewer→engine context bridge (D-2026-06-15-D).
 *
 * Pins ``useViewerContextBridge``: it POSTs the active scope + selection to the
 * engine (debounced) whenever they change, sends a periodic heartbeat so an
 * idle-but-open viewer stays "live", and stays silent without a workspace.
 */
import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const reportSpy = vi.fn(async () => {});
vi.mock("../src/app/viewer", () => ({
  reportViewerContext: (...args: unknown[]) => reportSpy(...args),
}));

import { useViewerContextBridge } from "../src/hooks/useViewerContextBridge";
import type { ChatSelectionNode } from "../src/types";

const SEL: ChatSelectionNode[] = [{ id: "n1", kind: "core_value", label: "Trust" }];

beforeEach(() => {
  vi.useFakeTimers();
  reportSpy.mockClear();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("useViewerContextBridge (D-2026-06-15-D)", () => {
  it("posts the scope + selection after the debounce", () => {
    renderHook(() => useViewerContextBridge("/ws", "foundation", SEL));
    expect(reportSpy).not.toHaveBeenCalled(); // debounced, not immediate
    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(reportSpy).toHaveBeenCalledWith("/ws", "foundation", SEL);
  });

  it("coalesces rapid changes into a single post", () => {
    const { rerender } = renderHook(
      ({ scope }) => useViewerContextBridge("/ws", scope, SEL),
      { initialProps: { scope: "foundation" as const } },
    );
    act(() => {
      vi.advanceTimersByTime(50);
    });
    rerender({ scope: "actors" as never });
    act(() => {
      vi.advanceTimersByTime(50);
    });
    rerender({ scope: "services" as never });
    act(() => {
      vi.advanceTimersByTime(200);
    });
    // Only the final settled value is posted (plus none mid-flight).
    expect(reportSpy).toHaveBeenCalledTimes(1);
    expect(reportSpy).toHaveBeenLastCalledWith("/ws", "services", SEL);
  });

  it("sends a heartbeat while mounted so an idle viewer stays live", () => {
    renderHook(() => useViewerContextBridge("/ws", "foundation", SEL));
    act(() => {
      vi.advanceTimersByTime(200); // initial debounced post
    });
    reportSpy.mockClear();
    act(() => {
      vi.advanceTimersByTime(30_000); // one heartbeat interval
    });
    expect(reportSpy).toHaveBeenCalledWith("/ws", "foundation", SEL);
  });

  it("stays silent without a workspace", () => {
    renderHook(() => useViewerContextBridge(undefined, "foundation", SEL));
    act(() => {
      vi.advanceTimersByTime(60_000);
    });
    expect(reportSpy).not.toHaveBeenCalled();
  });
});
