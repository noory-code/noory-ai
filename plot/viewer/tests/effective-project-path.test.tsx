/**
 * useProject routes per-project I/O through the EFFECTIVE project path
 * (workspace root + the project's dir) — v0.33.0 (D-2026-05-31-M).
 *
 * Two projects live in different dirs; switching to one must address the
 * server at its dir, not the bare workspace root.
 */
import { renderHook, waitFor, act } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../src/api";
import { useProject } from "../src/hooks/useProject";
import type { ProjectHistoryApi } from "../src/canvases/useProjectHistory";

vi.mock("../src/api");

const ROOT = "/repo";

function historyStub(): ProjectHistoryApi {
  return { init: vi.fn(), clear: vi.fn() } as unknown as ProjectHistoryApi;
}

function proj(id: string) {
  return { id, name: id, service_details: [], tags: [], blueprint_version: "v0.1.0" };
}

beforeEach(() => {
  vi.mocked(api.discoverWorkspace).mockResolvedValue({
    projects: [
      { project: proj("p1") as never, dir: "a" },
      { project: proj("p2") as never, dir: "b" },
    ],
    migrated: [],
  });
  vi.mocked(api.getProject).mockImplementation(
    async (_path: string, id: string) => proj(id) as never,
  );
  vi.mocked(api.getAllCanvases).mockResolvedValue(new Map() as never);
});

describe("useProject effective project path (D-2026-05-31-M)", () => {
  it("opens the first project at its own dir on load", async () => {
    renderHook(() =>
      useProject({
        workspaceRoot: ROOT,
        history: historyStub(),
        initialActiveId: null,
        onActiveIdChange: vi.fn(),
        onError: vi.fn(),
      }),
    );
    await waitFor(() => expect(api.getProject).toHaveBeenCalled());
    expect(api.getProject).toHaveBeenCalledWith("/repo/a", "p1");
  });

  it("retargets I/O to the picked project's dir", async () => {
    const { result } = renderHook(() =>
      useProject({
        workspaceRoot: ROOT,
        history: historyStub(),
        initialActiveId: null,
        onActiveIdChange: vi.fn(),
        onError: vi.fn(),
      }),
    );
    await waitFor(() => expect(api.getProject).toHaveBeenCalledWith("/repo/a", "p1"));

    await act(async () => {
      result.current.pick("p2");
    });
    await waitFor(() => expect(api.getProject).toHaveBeenCalledWith("/repo/b", "p2"));
    // and the active effective path reflects dir "b"
    expect(result.current.activeProjectPath).toBe("/repo/b");
    expect(result.current.dirForId("p2")).toBe("b");
  });
});
