/**
 * The sidebar shows the unified project list with a per-project dir label
 * ("." → localized root label) — v0.33.0 (D-2026-05-31-M).
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import i18n from "../src/i18n";
import { SketchSidebar } from "../src/canvases/SketchSidebar";
import { ThemeProvider } from "../src/theme/ThemeProvider";
import type { ProjectDoc } from "../src/types";

function project(id: string, name: string): ProjectDoc {
  return { id, name } as unknown as ProjectDoc;
}

function props() {
  return {
    projects: [project("p1", "Alpha"), project("p2", "Beta")],
    activeId: "p1",
    dirForId: (id: string) => (id === "p1" ? "plot" : "."),
    stencilCanvas: "foundation" as const,
    tags: [],
    onPick: vi.fn(),
    onCreate: vi.fn(),
    onRename: vi.fn(),
    onDelete: vi.fn(),
    onDeleteTag: vi.fn(),
    onViewTag: vi.fn(),
    viewingTag: null,
  };
}

describe("Sidebar unified list (D-2026-05-31-M)", () => {
  it("renders each project with its directory label", () => {
    render(<SketchSidebar {...props()} />, { wrapper: ThemeProvider });
    expect(screen.getByText("Alpha")).toBeInTheDocument();
    expect(screen.getByText("Beta")).toBeInTheDocument();
    expect(screen.getByText("plot")).toBeInTheDocument();
    // root-level project shows the localized root label, not "."
    expect(screen.getByText(i18n.t("sidebar.rootDir"))).toBeInTheDocument();
  });
});
