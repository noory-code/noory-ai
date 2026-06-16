/**
 * Chat model display + selection (D-2026-06-16-C; top dropdown D-2026-06-16-D).
 *
 *   ① the active model is shown (the top dropdown reflects it);
 *   ② the user selects a model from the dropdown, which PUTs {provider, model};
 *   the selector is absent until an agent is connected.
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

const PROVIDERS_REGISTERED = {
  providers: [
    { name: "claude-code", installed: true, registered: true, config_path: "~/.claude.json" },
    { name: "codex", installed: true, registered: true, config_path: "~/.codex/config.toml" },
    { name: "gemini", installed: false, registered: false, config_path: "~/.gemini/settings.json" },
  ],
};

let selectionValue: { provider: string | null; model: string | null };

beforeEach(() => {
  fetchSpy.mockReset();
  selectionValue = { provider: "codex", model: null };
  fetchSpy.mockImplementation((url: unknown, init?: RequestInit) => {
    const u = String(url);
    if (u.includes("/api/chat/provider")) {
      if (init && init.method === "PUT") {
        return Promise.resolve(jsonResponse({ ok: true }));
      }
      return Promise.resolve(jsonResponse(selectionValue));
    }
    if (u.includes("/api/mcp/providers")) {
      return Promise.resolve(jsonResponse(PROVIDERS_REGISTERED));
    }
    return Promise.resolve(jsonResponse({}));
  });
  vi.stubGlobal("fetch", fetchSpy);
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe("ChatDock — model display + selection (D-2026-06-16-C/D)", () => {
  it("shows the active model in the top dropdown", async () => {
    selectionValue = { provider: "codex", model: "o3" };
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const select = (await screen.findByLabelText(/model/i)) as HTMLSelectElement;
    await waitFor(() => expect(select.value).toBe("o3"));
  });

  it("shows 'default' selected when no model override is set", async () => {
    selectionValue = { provider: "codex", model: null };
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const select = (await screen.findByLabelText(/model/i)) as HTMLSelectElement;
    await waitFor(() => expect(select.value).toBe("")); // "" = default option
  });

  it("PUTs {provider, model} when the user picks a model from the dropdown", async () => {
    selectionValue = { provider: "claude-code", model: null };
    const user = userEvent.setup();
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const select = (await screen.findByLabelText(/model/i)) as HTMLSelectElement;
    await user.selectOptions(select, "opus");
    await waitFor(() => {
      const put = fetchSpy.mock.calls.find(
        (c) =>
          String(c[0]).includes("/api/chat/provider") &&
          c[1] &&
          (c[1] as RequestInit).method === "PUT",
      );
      expect(put).toBeDefined();
      expect(JSON.parse(String((put![1] as RequestInit).body))).toEqual({
        provider: "claude-code",
        model: "opus",
      });
    });
  });

  it("does not show a model selector when no provider is connected", async () => {
    selectionValue = { provider: null, model: null };
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    await screen.findByRole("button", { name: /ai agent/i });
    expect(screen.queryByLabelText(/model/i)).toBeNull();
  });
});
