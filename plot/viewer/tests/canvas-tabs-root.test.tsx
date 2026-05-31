/**
 * CanvasTabs shows the active project NAME centered in the tab bar
 * (v0.34.3, D-2026-05-31-Q). The workspace root path lives in the header.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CanvasTabs } from "../src/shell/CanvasTabs";

describe("CanvasTabs project name (D-2026-05-31-Q)", () => {
  it("renders the active project name centered", () => {
    render(
      <CanvasTabs
        active="foundation"
        onSelect={vi.fn()}
        blueprintVersion="v0.1.0"
        onPublishBlueprint={vi.fn()}
        projectName="Banas"
      />,
    );
    expect(screen.getByText("Banas")).toBeInTheDocument();
  });
});
