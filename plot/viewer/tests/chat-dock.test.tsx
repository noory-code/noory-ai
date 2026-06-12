/**
 * R7 chat dock (D-2026-06-11-E, Phase B step B1).
 *
 * The dock is the right-side collapsible container that holds the chat
 * surface (provider list now; message frame + input in B2; CLI streaming
 * in Phase C). Behaviour pinned here:
 *
 *   - Expanded by default; the provider panel renders inside.
 *   - A toggle button collapses / expands the dock.
 *   - Collapse state persists across reloads via
 *     `localStorage["plot:chatDockCollapsed"]` ("1" = collapsed).
 *   - `onError` is forwarded to the embedded `ChatProvidersPanel`.
 *   - When collapsed, the provider list is removed from the DOM (we hide
 *     by unmount, not by CSS — keeps the screen-reader tree honest).
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ChatDock } from "../src/shell/ChatDock";
import "../src/i18n";

const fetchSpy = vi.fn();

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

const PROVIDERS_FRESH = {
  providers: [
    { name: "claude-code", installed: true, registered: false, config_path: "~/.claude.json" },
    { name: "codex", installed: true, registered: false, config_path: "~/.codex/config.toml" },
    { name: "gemini", installed: false, registered: false, config_path: "~/.gemini/settings.json" },
  ],
};

beforeEach(() => {
  fetchSpy.mockReset();
  fetchSpy.mockResolvedValue(jsonResponse(PROVIDERS_FRESH));
  vi.stubGlobal("fetch", fetchSpy);
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe("ChatDock (D-2026-06-11-E Phase B step B1)", () => {
  it("renders the provider panel inside when expanded by default", async () => {
    render(<ChatDock onError={() => {}} />);
    await waitFor(() => screen.getByText("Claude Code"));
    expect(screen.getByText("Claude Code")).toBeTruthy();
    expect(screen.getByText("Codex")).toBeTruthy();
  });

  it("collapses on toggle click and removes the provider panel from the DOM", async () => {
    const user = userEvent.setup();
    render(<ChatDock onError={() => {}} />);
    await waitFor(() => screen.getByText("Claude Code"));

    const toggle = screen.getByRole("button", { name: /collapse chat/i });
    await user.click(toggle);

    expect(screen.queryByText("Claude Code")).toBeNull();
    expect(localStorage.getItem("plot:chatDockCollapsed")).toBe("1");
  });

  it("expands again on a second toggle click and clears persisted collapsed flag", async () => {
    const user = userEvent.setup();
    localStorage.setItem("plot:chatDockCollapsed", "1");
    render(<ChatDock onError={() => {}} />);

    // Starts collapsed → provider panel never rendered, so no fetch yet.
    expect(screen.queryByText("Claude Code")).toBeNull();

    const expand = screen.getByRole("button", { name: /expand chat/i });
    await user.click(expand);

    await waitFor(() => screen.getByText("Claude Code"));
    expect(localStorage.getItem("plot:chatDockCollapsed")).toBe("0");
  });

  it("starts collapsed when localStorage says so", () => {
    localStorage.setItem("plot:chatDockCollapsed", "1");
    render(<ChatDock onError={() => {}} />);
    expect(screen.queryByText("Claude Code")).toBeNull();
    // The provider fetch must NOT have fired — panel was never mounted.
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("forwards onError to the embedded ChatProvidersPanel", async () => {
    const onError = vi.fn();
    fetchSpy.mockReset();
    fetchSpy.mockResolvedValueOnce(jsonResponse({ error: "engine offline" }, 500));
    render(<ChatDock onError={onError} />);
    await waitFor(() => expect(onError).toHaveBeenCalled());
  });
});
