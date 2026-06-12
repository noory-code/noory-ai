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

  // ---- Phase B step B2: message-area frame (visual only — Phase C streams) ----

  it("renders a message log frame with the no-workspace caption when no workspace is given", async () => {
    render(<ChatDock onError={() => {}} />);
    await waitFor(() => screen.getByText("Claude Code"));
    const log = screen.getByRole("log", { name: /chat messages/i });
    expect(log).toBeTruthy();
    // Phase C: without a workspace there is no chat session — the empty-state
    // caption prompts the user to open one, not "no messages yet".
    expect(screen.getByText(/open a workspace/i)).toBeTruthy();
  });

  it("keeps the input disabled until a workspace + active CLI are both present (Phase C)", async () => {
    render(<ChatDock onError={() => {}} />);
    await waitFor(() => screen.getByText("Claude Code"));
    const input = screen.getByRole("textbox", { name: /message input/i }) as HTMLTextAreaElement;
    // No workspace → input stays disabled + placeholder prompts the user to pick a CLI.
    expect(input.disabled).toBe(true);
    expect(input.placeholder.toLowerCase()).toContain("pick a chat cli");
    const send = screen.getByRole("button", { name: /^send$/i }) as HTMLButtonElement;
    expect(send.disabled).toBe(true);
  });

  it("does not render the message frame when collapsed", () => {
    localStorage.setItem("plot:chatDockCollapsed", "1");
    render(<ChatDock onError={() => {}} />);
    expect(screen.queryByRole("log", { name: /chat messages/i })).toBeNull();
    expect(screen.queryByRole("textbox", { name: /message input/i })).toBeNull();
  });

  // ---- Phase B step B3: workspace-scoped active-provider persistence ----

  it("does not call /api/chat/provider when workspaceRoot is not provided", async () => {
    render(<ChatDock onError={() => {}} />);
    await waitFor(() => screen.getByText("Claude Code"));
    const calls = fetchSpy.mock.calls.map((c) => String(c[0]));
    expect(calls.some((u) => u.includes("/api/chat/provider"))).toBe(false);
  });

  it("loads the persisted chat provider from the server on mount when workspaceRoot is given", async () => {
    fetchSpy.mockReset();
    fetchSpy
      .mockResolvedValueOnce(jsonResponse(PROVIDERS_FRESH))
      .mockResolvedValueOnce(jsonResponse({ provider: "claude-code" }));
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    await waitFor(() => {
      const calls = fetchSpy.mock.calls.map((c) => String(c[0]));
      expect(
        calls.some((u) => u.includes("/api/chat/provider") && u.includes("project_path=")),
      ).toBe(true);
    });
  });

  it("PUTs the new selection to the server when a radio is clicked", async () => {
    fetchSpy.mockReset();
    fetchSpy
      .mockResolvedValueOnce(jsonResponse(PROVIDERS_FRESH_REGISTERED))
      .mockResolvedValueOnce(jsonResponse({ provider: null }))
      .mockResolvedValueOnce(jsonResponse({ provider: "claude-code" }));
    const user = userEvent.setup();
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    await waitFor(() => screen.getByText("Claude Code"));
    const radios = await screen.findAllByRole("radio");
    const claude = (radios as HTMLInputElement[]).find((r) => r.value === "claude-code")!;
    await user.click(claude);
    await waitFor(() => {
      const calls = fetchSpy.mock.calls;
      const put = calls.find(
        (c) =>
          String(c[0]).includes("/api/chat/provider") &&
          c[1] &&
          (c[1] as RequestInit).method === "PUT",
      );
      expect(put).toBeDefined();
      const body = JSON.parse(String((put![1] as RequestInit).body));
      expect(body).toEqual({ provider: "claude-code" });
    });
  });
});

const PROVIDERS_FRESH_REGISTERED = {
  providers: [
    { name: "claude-code", installed: true, registered: true, config_path: "~/.claude.json" },
    { name: "codex", installed: true, registered: true, config_path: "~/.codex/config.toml" },
    { name: "gemini", installed: false, registered: false, config_path: "~/.gemini/settings.json" },
  ],
};
