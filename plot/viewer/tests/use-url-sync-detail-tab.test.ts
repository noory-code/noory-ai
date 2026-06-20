/**
 * useUrlSync — feature dynamic-tab state (D-2026-06-15-H).
 *
 * The feature opens as a tab (was a modal): ``drillIntoFeature`` adds
 * the tab and makes it active; switching to an F/A/S tab deactivates it but
 * KEEPS the tab; ``closeDetail`` removes it.
 */
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { useUrlSync } from "../src/hooks/useUrlSync";

beforeEach(() => {
  window.history.replaceState(null, "", "/");
});

describe("useUrlSync — feature tab (D-2026-06-15-H)", () => {
  it("drillIntoFeature adds the tab and makes it the active view", () => {
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoFeature("svc_1"));
    expect(result.current.detailFeatureId).toBe("svc_1");
    expect(result.current.detailActive).toBe(true);
  });

  it("selecting an F/A/S tab deactivates but keeps the detail tab", () => {
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoFeature("svc_1"));
    act(() => result.current.selectTab("actors"));
    expect(result.current.activeTab).toBe("actors");
    expect(result.current.detailActive).toBe(false);
    expect(result.current.detailFeatureId).toBe("svc_1"); // tab persists
  });

  it("activateDetail re-activates the existing detail tab", () => {
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoFeature("svc_1"));
    act(() => result.current.selectTab("foundation"));
    act(() => result.current.activateDetail());
    expect(result.current.detailActive).toBe(true);
    expect(result.current.detailFeatureId).toBe("svc_1");
  });

  it("closeDetail removes the tab entirely", () => {
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoFeature("svc_1"));
    act(() => result.current.closeDetail());
    expect(result.current.detailFeatureId).toBeNull();
    expect(result.current.detailActive).toBe(false);
  });

  it("jumpToActor deactivates the detail tab (no stale detailActive on the actors canvas)", () => {
    // Bug (workflow diagnosis 2026-06-15): jumpToActor switched to the actors
    // canvas but left detailActive=true → stencil/chat/tab desynced. Leaving a
    // feature for the actor master must deactivate the detail tab, like
    // selectTab does.
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoFeature("svc_1"));
    act(() => result.current.jumpToActor("actor_9"));
    expect(result.current.activeTab).toBe("actors");
    expect(result.current.detailActive).toBe(false);
  });
});
