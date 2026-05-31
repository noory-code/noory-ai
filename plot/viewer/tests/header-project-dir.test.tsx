/**
 * Header shows the active project's relative dir, not the absolute root
 * (v0.34.1, D-2026-05-31-O). The absolute root stays as the hover title.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import i18n from "../src/i18n";
import { Header } from "../src/shell/Header";

function props(over: Partial<React.ComponentProps<typeof Header>> = {}) {
  return {
    projectPath: "/repo",
    projectDir: "apps/web" as string | null,
    error: null,
    socketStatus: "connected" as const,
    saveState: "idle" as const,
    projectName: "Web",
    blueprintVersion: "v0.1.0",
    viewingTag: null,
    onExitTagView: vi.fn(),
    migratedToast: null,
    onDismissToast: vi.fn(),
    ...over,
  };
}

describe("Header project dir (D-2026-05-31-O)", () => {
  it("shows the relative dir, with the absolute root as the title", () => {
    render(<Header {...props({ projectDir: "apps/web" })} />);
    const span = screen.getByText("apps/web");
    expect(span).toBeInTheDocument();
    expect(span).toHaveAttribute("title", "/repo");
  });

  it("shows the localized root label for a root-level project", () => {
    render(<Header {...props({ projectDir: "." })} />);
    expect(screen.getByText(i18n.t("sidebar.rootDir"))).toBeInTheDocument();
  });

  it("shows the root label when no project is active", () => {
    render(<Header {...props({ projectDir: null })} />);
    expect(screen.getByText(i18n.t("sidebar.rootDir"))).toBeInTheDocument();
  });
});
