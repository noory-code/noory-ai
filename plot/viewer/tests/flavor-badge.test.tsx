/**
 * Build-flavor badge. The debug flavor (VITE_PLOT_DEBUG=1) shows a
 * "DEBUG" badge in the header so a non-release build is visually obvious;
 * the release flavor renders nothing (no runtime escape hatch — same
 * BUILD-TIME gate as the debug probe, D-2026-06-09-D / debugEnabled()).
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { FlavorBadge } from "../src/shell/FlavorBadge";

describe("FlavorBadge (debug-flavor only)", () => {
  afterEach(() => vi.unstubAllEnvs());

  it("renders a DEBUG badge in the debug flavor (VITE_PLOT_DEBUG=1)", () => {
    vi.stubEnv("VITE_PLOT_DEBUG", "1");
    render(<FlavorBadge />);
    expect(screen.getByText("DEBUG")).toBeInTheDocument();
  });

  it("renders nothing in the release flavor (VITE_PLOT_DEBUG unset)", () => {
    vi.stubEnv("VITE_PLOT_DEBUG", "");
    const { container } = render(<FlavorBadge />);
    expect(container).toBeEmptyDOMElement();
  });
});
