/**
 * The socket indicator is prefixed "MCP:" so it's clear the dot reflects
 * the MCP server connection (v0.34.2, D-2026-05-31-P).
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Header } from "../src/shell/Header";

function props(over: Partial<React.ComponentProps<typeof Header>> = {}) {
  return {
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

describe("Header socket label (D-2026-05-31-P)", () => {
  it("shows 'MCP: live' when connected", () => {
    render(<Header {...props({ socketStatus: "connected" })} />);
    expect(screen.getByText("MCP: live")).toBeInTheDocument();
  });

  it("shows 'MCP: offline' when disconnected", () => {
    render(<Header {...props({ socketStatus: "disconnected" })} />);
    expect(screen.getByText("MCP: offline")).toBeInTheDocument();
  });
});
