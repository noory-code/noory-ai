/**
 * CanvasTabs shows the workspace root path centered in the tab bar
 * (v0.34.2, D-2026-05-31-P).
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CanvasTabs } from "../src/shell/CanvasTabs";

describe("CanvasTabs workspace root (D-2026-05-31-P)", () => {
  it("renders the workspace root path", () => {
    render(
      <CanvasTabs
        active="foundation"
        onSelect={vi.fn()}
        blueprintVersion="v0.1.0"
        onPublishBlueprint={vi.fn()}
        workspaceRoot="/Users/me/Workspace/repo"
      />,
    );
    const span = screen.getByText("/Users/me/Workspace/repo");
    expect(span).toBeInTheDocument();
    expect(span).toHaveAttribute("title", "/Users/me/Workspace/repo");
  });
});
