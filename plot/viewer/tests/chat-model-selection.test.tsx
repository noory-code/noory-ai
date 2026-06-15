/**
 * Chat model display + selection (D-2026-06-16-C).
 *
 *   ① the active model is shown (on the provider bar + in the model field);
 *   ② the user can set a model, which PUTs {provider, model} to the engine;
 *   switching provider clears the model.
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
      return Promise.resolve(jsonResponse({ providers: [] }));
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

describe("ChatDock — model display + selection (D-2026-06-16-C)", () => {
  it("shows the active model on the provider bar", async () => {
    selectionValue = { provider: "codex", model: "o3" };
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const bar = await screen.findByRole("button", { name: /ai agent/i });
    await waitFor(() => expect(bar.textContent).toContain("o3"));
    expect(bar.textContent).toContain("Codex");
  });

  it("renders a model field that reflects the persisted model", async () => {
    selectionValue = { provider: "codex", model: "o3" };
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const field = (await screen.findByLabelText(/model/i)) as HTMLInputElement;
    await waitFor(() => expect(field.value).toBe("o3"));
  });

  it("PUTs {provider, model} when the user sets a model", async () => {
    selectionValue = { provider: "codex", model: null };
    const user = userEvent.setup();
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const field = (await screen.findByLabelText(/model/i)) as HTMLInputElement;
    await user.click(field);
    await user.type(field, "o3");
    await user.tab(); // blur → commit
    await waitFor(() => {
      const put = fetchSpy.mock.calls.find(
        (c) =>
          String(c[0]).includes("/api/chat/provider") &&
          c[1] &&
          (c[1] as RequestInit).method === "PUT",
      );
      expect(put).toBeDefined();
      expect(JSON.parse(String((put![1] as RequestInit).body))).toEqual({
        provider: "codex",
        model: "o3",
      });
    });
  });

  it("does not show a model field when no provider is selected", async () => {
    selectionValue = { provider: null, model: null };
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    await screen.findByRole("button", { name: /ai agent/i });
    expect(screen.queryByLabelText(/model/i)).toBeNull();
  });
});
