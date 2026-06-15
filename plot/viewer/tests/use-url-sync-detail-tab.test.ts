/**
 * useUrlSync — service-detail dynamic-tab state (D-2026-06-15-H).
 *
 * The service-detail opens as a tab (was a modal): ``drillIntoService`` adds
 * the tab and makes it active; switching to an F/A/S tab deactivates it but
 * KEEPS the tab; ``closeDetail`` removes it.
 */
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { useUrlSync } from "../src/hooks/useUrlSync";

beforeEach(() => {
  window.history.replaceState(null, "", "/");
});

describe("useUrlSync — service-detail tab (D-2026-06-15-H)", () => {
  it("drillIntoService adds the tab and makes it the active view", () => {
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoService("svc_1"));
    expect(result.current.detailServiceId).toBe("svc_1");
    expect(result.current.detailActive).toBe(true);
  });

  it("selecting an F/A/S tab deactivates but keeps the detail tab", () => {
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoService("svc_1"));
    act(() => result.current.selectTab("actors"));
    expect(result.current.activeTab).toBe("actors");
    expect(result.current.detailActive).toBe(false);
    expect(result.current.detailServiceId).toBe("svc_1"); // tab persists
  });

  it("activateDetail re-activates the existing detail tab", () => {
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoService("svc_1"));
    act(() => result.current.selectTab("foundation"));
    act(() => result.current.activateDetail());
    expect(result.current.detailActive).toBe(true);
    expect(result.current.detailServiceId).toBe("svc_1");
  });

  it("closeDetail removes the tab entirely", () => {
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoService("svc_1"));
    act(() => result.current.closeDetail());
    expect(result.current.detailServiceId).toBeNull();
    expect(result.current.detailActive).toBe(false);
  });

  it("jumpToActor deactivates the detail tab (no stale detailActive on the actors canvas)", () => {
    // Bug (workflow diagnosis 2026-06-15): jumpToActor switched to the actors
    // canvas but left detailActive=true → stencil/chat/tab desynced. Leaving a
    // service-detail for the actor master must deactivate the detail tab, like
    // selectTab does.
    const { result } = renderHook(() => useUrlSync());
    act(() => result.current.drillIntoService("svc_1"));
    act(() => result.current.jumpToActor("actor_9"));
    expect(result.current.activeTab).toBe("actors");
    expect(result.current.detailActive).toBe(false);
  });
});
