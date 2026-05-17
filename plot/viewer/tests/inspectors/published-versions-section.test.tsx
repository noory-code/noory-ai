/**
 * v0.23.0 (D-2026-05-17-I) — PublishedVersionsSection tests.
 *
 * Verifies:
 *  - empty state when API returns no versions
 *  - non-empty list rendering (version + published_at + sha rows)
 *  - clicking a row opens the modal
 */
import "@testing-library/jest-dom/vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { PublishedVersionsSection } from "../../src/canvases/inspectors/shared/PublishedVersionsSection";

vi.mock("../../src/api", async () => {
  const actual = await vi.importActual<typeof import("../../src/api")>(
    "../../src/api",
  );
  return {
    ...actual,
    listPublishedVersions: vi.fn(),
    readFile: vi.fn(async () => "# Mock MD\n\nhello"),
  };
});

import { listPublishedVersions } from "../../src/api";

const listMock = vi.mocked(listPublishedVersions);

const baseProps = {
  projectPath: "/tmp/plot-test",
  projectId: "alpha",
  canvasKind: "foundation",
  nodeId: "id-1",
  refreshKey: "v1.0",
};

beforeEach(() => {
  listMock.mockReset();
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("PublishedVersionsSection", () => {
  it("renders the empty state when the API returns no versions", async () => {
    listMock.mockResolvedValueOnce([]);
    render(<PublishedVersionsSection {...baseProps} />);
    expect(
      await screen.findByText(/no published versions yet/i),
    ).toBeInTheDocument();
  });

  it("renders one row per version with the version label visible", async () => {
    listMock.mockResolvedValueOnce([
      {
        version: "v3.0",
        path: "foundation/published/mission/mission/v3.0.md",
        published_at: "2026-05-17T05:26:16+00:00",
        sha: "abc1234",
        size: 256,
      },
      {
        version: "v2.0",
        path: "foundation/published/mission/mission/v2.0.md",
        published_at: "2026-05-17T05:20:00+00:00",
        sha: "def5678",
        size: 200,
      },
    ]);
    render(<PublishedVersionsSection {...baseProps} />);
    expect(await screen.findByText("v3.0")).toBeInTheDocument();
    expect(screen.getByText("v2.0")).toBeInTheDocument();
    expect(screen.getByText("abc1234")).toBeInTheDocument();
  });

  it("opens the modal when a version row is clicked", async () => {
    const user = userEvent.setup();
    listMock.mockResolvedValueOnce([
      {
        version: "v2.0",
        path: "foundation/published/mission/mission/v2.0.md",
        published_at: null,
        sha: null,
        size: 42,
      },
    ]);
    render(<PublishedVersionsSection {...baseProps} />);
    const row = await screen.findByRole("button", { name: /v2\.0/i });
    await user.click(row);
    // Modal aria-label uses the version string.
    await waitFor(() => {
      expect(
        screen.getByRole("dialog", { name: /published v2\.0/i }),
      ).toBeInTheDocument();
    });
  });

  it("re-fetches when refreshKey changes (e.g. after a publish)", async () => {
    listMock.mockResolvedValue([]);
    const { rerender } = render(
      <PublishedVersionsSection {...baseProps} refreshKey="v1.0" />,
    );
    await waitFor(() => expect(listMock).toHaveBeenCalledTimes(1));
    rerender(<PublishedVersionsSection {...baseProps} refreshKey="v2.0" />);
    await waitFor(() => expect(listMock).toHaveBeenCalledTimes(2));
  });
});
