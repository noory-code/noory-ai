/**
 * useProject.create(targetDir) — create in the chosen dir, or land in an
 * existing project there instead of duplicating (D-2026-05-31-N).
 */
import { renderHook, waitFor, act } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../src/api";
import { useProject } from "../src/hooks/useProject";
import type { ProjectHistoryApi } from "../src/canvases/useProjectHistory";

vi.mock("../src/api");

// v0.36.0 (D-2026-05-31-Y) — create() now prompts for a name. Stub the
// dialog so this dir-routing test resolves a name without UI.
const promptMock = vi.fn().mockResolvedValue("New Service");
vi.mock("../src/shell/dialog/DialogProvider", () => ({
  useDialog: () => ({ prompt: promptMock, confirm: vi.fn(), alert: vi.fn() }),
}));

const ROOT = "/repo";

function historyStub(): ProjectHistoryApi {
  return { init: vi.fn(), clear: vi.fn() } as unknown as ProjectHistoryApi;
}
function proj(id: string) {
  return { id, name: id, service_details: [], tags: [], blueprint_version: "v0.1.0" };
}

beforeEach(() => {
  vi.mocked(api.discoverWorkspace).mockResolvedValue({
    projects: [{ project: proj("p1") as never, dir: "a" }],
    migrated: [],
  });
  vi.mocked(api.getProject).mockImplementation(async (_p: string, id: string) => proj(id) as never);
  vi.mocked(api.getAllCanvases).mockResolvedValue(new Map() as never);
  vi.mocked(api.createProject).mockResolvedValue(proj("proj-new") as never);
});

function mountProject() {
  return renderHook(() =>
    useProject({
      workspaceRoot: ROOT,
      history: historyStub(),
      initialActiveId: null,
      onActiveIdChange: vi.fn(),
      onError: vi.fn(),
    }),
  );
}

describe("useProject.create(targetDir) (D-2026-05-31-N)", () => {
  it("creates a project in the chosen (empty) directory", async () => {
    const { result } = mountProject();
    await waitFor(() => expect(result.current.summaries).toHaveLength(1));
    await waitFor(() => expect(api.getProject).toHaveBeenCalledWith("/repo/a", "p1"));

    await act(async () => {
      await result.current.create("services/new-svc");
    });
    expect(api.createProject).toHaveBeenCalledWith(
      "/repo/services/new-svc",
      expect.stringMatching(/^proj-/),
      "New Service",
    );
  });

  it("lands in the existing project when the chosen dir already has one", async () => {
    const { result } = mountProject();
    await waitFor(() => expect(result.current.summaries).toHaveLength(1));
    await waitFor(() => expect(api.getProject).toHaveBeenCalledWith("/repo/a", "p1"));
    vi.mocked(api.createProject).mockClear();

    await act(async () => {
      await result.current.create("a"); // dir "a" already holds p1
    });
    expect(api.createProject).not.toHaveBeenCalled();
    // re-opened the existing project at its dir
    expect(api.getProject).toHaveBeenCalledWith("/repo/a", "p1");
  });
});
