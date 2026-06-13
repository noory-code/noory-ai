/**
 * Sidebar stencil is gated on an active project — v0.31.3
 * (D-2026-05-31-K).
 *
 * With no project selected (empty workspace / "No projects yet"), the
 * left-sidebar stencil must be hidden — there is nothing to drop its
 * draggables onto. Once a project is active, the stencil renders.
 */
import "@testing-library/jest-dom/vitest";
import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SketchSidebar } from "../src/canvases/SketchSidebar";
import { ThemeProvider } from "../src/theme/ThemeProvider";
import type { ProjectDoc } from "../src/types";

function makeProps(over: Partial<React.ComponentProps<typeof SketchSidebar>> = {}) {
  return {
    projects: [] as ProjectDoc[],
    activeId: null as string | null,
    stencilCanvas: "foundation" as const,
    tags: [],
    onPick: vi.fn(),
    onCreate: vi.fn(),
    onRename: vi.fn(),
    onDelete: vi.fn(),
    onDeleteTag: vi.fn(),
    onViewTag: vi.fn(),
    viewingTag: null,
    ...over,
  };
}

const PROJECT = { id: "p1", name: "Demo" } as unknown as ProjectDoc;

describe("Sidebar stencil gating (D-2026-05-31-K)", () => {
  it("hides the stencil when no project is active", () => {
    const { container } = render(
      <SketchSidebar {...makeProps({ activeId: null, projects: [] })} />,
      { wrapper: ThemeProvider },
    );
    expect(container.querySelectorAll('[data-stencil-item]')).toHaveLength(0);
  });

  it("shows the stencil once a project is active", () => {
    const { container } = render(
      <SketchSidebar {...makeProps({ activeId: "p1", projects: [PROJECT] })} />,
      { wrapper: ThemeProvider },
    );
    expect(container.querySelectorAll('[data-stencil-item]').length).toBeGreaterThan(0);
  });
});
