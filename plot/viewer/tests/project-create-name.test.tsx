/**
 * v0.36.0 (D-2026-05-31-Y) — creating a project prompts for its name via the
 * in-app dialog instead of silently naming it "Untitled". Opening an existing
 * project (the dir already holds one) must NOT prompt.
 */
import { renderHook, waitFor, act } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../src/api";
import { useProject } from "../src/hooks/useProject";
import { makeQueryWrapper } from "./test-utils";
import type { ProjectHistoryApi } from "../src/canvases/useProjectHistory";

vi.mock("../src/api");

const promptMock = vi.fn();
vi.mock("../src/shell/dialog/DialogProvider", () => ({
  useDialog: () => ({ prompt: promptMock, confirm: vi.fn(), alert: vi.fn() }),
}));

const ROOT = "/repo";

function historyStub(): ProjectHistoryApi {
  return { init: vi.fn(), clear: vi.fn() } as unknown as ProjectHistoryApi;
}

function proj(id: string, name = id) {
  return { id, name, feature_details: [], tags: [], blueprint_version: "v0.1.0" };
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.discoverWorkspace).mockResolvedValue({
    projects: [{ project: proj("p1") as never, dir: "a" }],
    migrated: [],
  });
  vi.mocked(api.getProject).mockImplementation(
    async (_path: string, id: string) => proj(id) as never,
  );
  vi.mocked(api.getAllCanvases).mockResolvedValue(new Map() as never);
  vi.mocked(api.createProject).mockResolvedValue(proj("proj-new", "Banana") as never);
});

function mount() {
  return renderHook(() =>
    useProject({
      workspaceRoot: ROOT,
      history: historyStub(),
      initialActiveId: null,
      onActiveIdChange: vi.fn(),
      onError: vi.fn(),
    }),
    { wrapper: makeQueryWrapper() },
  );
}

describe("useProject — create prompts for a name (D-2026-05-31-Y)", () => {
  it("prompts and creates with the entered name in the picked dir", async () => {
    promptMock.mockResolvedValue("Banana");
    const { result } = mount();
    await waitFor(() => expect(api.getProject).toHaveBeenCalledWith("/repo/a", "p1"));

    await act(async () => {
      await result.current.create("banana"); // dir with no existing project
    });

    expect(promptMock).toHaveBeenCalled();
    expect(api.createProject).toHaveBeenCalledWith("/repo/banana", expect.any(String), "Banana");
  });

  it("aborts creation when the name prompt is cancelled", async () => {
    promptMock.mockResolvedValue(null);
    const { result } = mount();
    await waitFor(() => expect(api.getProject).toHaveBeenCalledWith("/repo/a", "p1"));

    await act(async () => {
      await result.current.create("banana");
    });

    expect(api.createProject).not.toHaveBeenCalled();
  });

  it("opening an existing project (dir already has one) does not prompt", async () => {
    promptMock.mockResolvedValue("X");
    const { result } = mount();
    await waitFor(() => expect(api.getProject).toHaveBeenCalledWith("/repo/a", "p1"));

    await act(async () => {
      await result.current.create("a"); // dir "a" already holds p1
    });

    expect(promptMock).not.toHaveBeenCalled();
    expect(api.createProject).not.toHaveBeenCalled();
  });
});
