/**
 * Foundation stencil concept info (ⓘ popover) — D-2026-06-06-A.
 *
 * Each Foundation stencil section (Mission / Core values / Identity) shows
 * an always-visible ⓘ button; clicking it opens a popover with that
 * concept's definition (FOUNDATION_CONCEPT.md). Foundation-only.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SketchStencil } from "../src/canvases/SketchStencil";

describe("Foundation stencil concept info (D-2026-06-06-A)", () => {
  it("renders an always-visible ⓘ button on each of the 3 foundation sections", () => {
    render(<SketchStencil canvas="foundation" />);
    const infoButtons = screen.getAllByRole("button", { name: /concept info/i });
    expect(infoButtons).toHaveLength(3); // mission, core values, identity
  });

  it("opens a popover with the concept definition on click", () => {
    render(<SketchStencil canvas="foundation" />);
    // popover content not visible before click
    expect(screen.queryByText(/why it exists/i)).not.toBeInTheDocument();
    // first ⓘ = mission section
    fireEvent.click(screen.getAllByRole("button", { name: /concept info/i })[0]);
    expect(screen.getByText(/why it exists/i)).toBeInTheDocument();
  });

  it("portals the popover to body so the stencil's overflow container can't clip it", () => {
    const { container } = render(<SketchStencil canvas="foundation" />);
    fireEvent.click(screen.getAllByRole("button", { name: /concept info/i })[0]);
    const dialog = screen.getByRole("dialog");
    // portaled out of the rendered stencil tree (which sits in an
    // overflow-y-auto scroll container) → not a descendant of it.
    expect(container.contains(dialog)).toBe(false);
  });

  it("shows no ⓘ on non-foundation canvases (foundation-only)", () => {
    render(<SketchStencil canvas="actors" />);
    expect(screen.queryAllByRole("button", { name: /concept info/i })).toHaveLength(0);
  });
});
