/**
 * R7 chat provider panel (D-2026-06-11-E, Phase A).
 *
 * Pins:
 *   - on mount, the panel fetches and renders one row per provider
 *   - each row's badge reflects install + registration state
 *   - clicking "Register" calls registerMcpProvider, then refreshes
 *   - clicking "Unregister" calls unregisterMcpProvider, then refreshes
 *   - a fetch / register error bubbles up via onError (no throw, no
 *     unhandled rejection)
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { ChatProvidersPanel } from "../src/shell/ChatProvidersPanel";
import "../src/i18n";

const fetchSpy = vi.fn();

beforeEach(() => {
  fetchSpy.mockReset();
  vi.stubGlobal("fetch", fetchSpy);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

const PROVIDERS_ALL_FRESH = {
  providers: [
    { name: "claude-code", installed: true, registered: false, config_path: "~/.claude.json" },
    { name: "codex", installed: true, registered: false, config_path: "~/.codex/config.toml" },
    { name: "gemini", installed: false, registered: false, config_path: "~/.gemini/settings.json" },
  ],
};

const PROVIDERS_AFTER_REGISTER = {
  providers: [
    { name: "claude-code", installed: true, registered: true, config_path: "~/.claude.json" },
    { name: "codex", installed: true, registered: false, config_path: "~/.codex/config.toml" },
    { name: "gemini", installed: false, registered: false, config_path: "~/.gemini/settings.json" },
  ],
};

describe("ChatProvidersPanel (D-2026-06-11-E Phase A)", () => {
  it("renders one row per provider after the initial fetch", async () => {
    fetchSpy.mockResolvedValue(jsonResponse(PROVIDERS_ALL_FRESH));
    render(<ChatProvidersPanel onError={() => {}} />);
    await waitFor(() => screen.getByText("Claude Code"));
    expect(screen.getByText("Claude Code")).toBeTruthy();
    expect(screen.getByText("Codex")).toBeTruthy();
    expect(screen.getByText("Gemini")).toBeTruthy();
  });

  it("shows 'Not installed' on the Gemini row + no action button", async () => {
    fetchSpy.mockResolvedValue(jsonResponse(PROVIDERS_ALL_FRESH));
    render(<ChatProvidersPanel onError={() => {}} />);
    await waitFor(() => screen.getByText("Gemini"));
    expect(screen.getByText("Not installed")).toBeTruthy();
    // Two installed providers → two Register buttons; Gemini has none.
    expect(screen.getAllByRole("button", { name: "Register Plot" })).toHaveLength(2);
  });

  it("calls register endpoint when a Register button is clicked + refreshes", async () => {
    fetchSpy
      .mockResolvedValueOnce(jsonResponse(PROVIDERS_ALL_FRESH))
      .mockResolvedValueOnce(jsonResponse({ ok: true, provider: "claude-code" }, 201))
      .mockResolvedValueOnce(jsonResponse(PROVIDERS_AFTER_REGISTER));
    const user = userEvent.setup();
    render(<ChatProvidersPanel onError={() => {}} />);
    await waitFor(() => screen.getAllByRole("button", { name: "Register Plot" }));
    // The first Register button is on the Claude Code row (alphabetical order).
    const buttons = screen.getAllByRole("button", { name: "Register Plot" });
    await user.click(buttons[0]);
    await waitFor(() => screen.getByText("Registered"));
    const calls = fetchSpy.mock.calls.map((c) => String(c[0]));
    expect(calls.some((u) => u.includes("/api/mcp/providers/claude-code/register"))).toBe(true);
    // Final list refresh was issued.
    expect(calls.filter((u) => u.endsWith("/api/mcp/providers"))).toHaveLength(2);
  });

  it("surfaces a fetch error through onError instead of throwing", async () => {
    const onError = vi.fn();
    fetchSpy.mockResolvedValueOnce(
      jsonResponse({ error: "engine offline" }, 500),
    );
    render(<ChatProvidersPanel onError={onError} />);
    await waitFor(() => expect(onError).toHaveBeenCalled());
  });

  // ---- Phase B step B3: active-provider selection radio ----

  it("renders no selection radio when activeProvider / onSelectProvider are omitted", async () => {
    fetchSpy.mockResolvedValue(jsonResponse(PROVIDERS_ALL_FRESH));
    render(<ChatProvidersPanel onError={() => {}} />);
    await waitFor(() => screen.getByText("Claude Code"));
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
  });

  it("renders a radio for each selectable row + checks the active row (claude-code excluded)", async () => {
    // codex is the active chat provider; claude-code carries no radio.
    fetchSpy.mockResolvedValue(
      jsonResponse({
        providers: [
          { name: "claude-code", installed: true, registered: true, config_path: "~/.claude.json" },
          { name: "codex", installed: true, registered: true, config_path: "~/.codex/config.toml" },
          { name: "gemini", installed: true, registered: true, config_path: "~/.gemini/settings.json" },
        ],
      }),
    );
    render(
      <ChatProvidersPanel
        onError={() => {}}
        activeProvider="codex"
        onSelectProvider={() => {}}
      />,
    );
    await waitFor(() => screen.getByText("Codex"));
    const radios = screen.getAllByRole("radio") as HTMLInputElement[];
    // Two selectable CLIs (codex, gemini); claude-code is excluded.
    expect(radios).toHaveLength(2);
    const codex = radios.find((r) => r.value === "codex");
    expect(codex?.checked).toBe(true);
  });

  it("omits the selection radio on the claude-code row but keeps its row + register controls (D-2026-06-13-H)", async () => {
    fetchSpy.mockResolvedValue(jsonResponse(PROVIDERS_AFTER_REGISTER));
    render(
      <ChatProvidersPanel
        onError={() => {}}
        activeProvider={null}
        onSelectProvider={() => {}}
      />,
    );
    await waitFor(() => screen.getByText("Claude Code"));
    const radios = screen.getAllByRole("radio") as HTMLInputElement[];
    const values = radios.map((r) => r.value);
    // claude-code is excluded from in-app chat selection...
    expect(values).not.toContain("claude-code");
    expect(values).toEqual(expect.arrayContaining(["codex", "gemini"]));
    // ...but its row + MCP register/unregister controls stay.
    expect(screen.getByText("Claude Code")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Unregister" })).toBeTruthy();
  });

  it("disables the radio on a not-installed provider", async () => {
    fetchSpy.mockResolvedValue(jsonResponse(PROVIDERS_ALL_FRESH));
    render(
      <ChatProvidersPanel
        onError={() => {}}
        activeProvider={null}
        onSelectProvider={() => {}}
      />,
    );
    await waitFor(() => screen.getByText("Gemini"));
    const radios = screen.getAllByRole("radio") as HTMLInputElement[];
    const gemini = radios.find((r) => r.value === "gemini");
    expect(gemini?.disabled).toBe(true);
  });

  it("calls onSelectProvider when an enabled radio is clicked", async () => {
    fetchSpy.mockResolvedValue(
      jsonResponse({
        providers: [
          { name: "claude-code", installed: true, registered: true, config_path: "~/.claude.json" },
          { name: "codex", installed: true, registered: true, config_path: "~/.codex/config.toml" },
          { name: "gemini", installed: false, registered: false, config_path: "~/.gemini/settings.json" },
        ],
      }),
    );
    const onSelectProvider = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatProvidersPanel
        onError={() => {}}
        activeProvider={null}
        onSelectProvider={onSelectProvider}
      />,
    );
    await waitFor(() => screen.getByText("Codex"));
    const radios = screen.getAllByRole("radio") as HTMLInputElement[];
    const codex = radios.find((r) => r.value === "codex")!;
    await user.click(codex);
    expect(onSelectProvider).toHaveBeenCalledWith("codex");
  });

  it("clears the active selection when the active provider is unregistered", async () => {
    fetchSpy
      .mockResolvedValueOnce(jsonResponse(PROVIDERS_AFTER_REGISTER))
      .mockResolvedValueOnce(jsonResponse({ ok: true, provider: "claude-code" }))
      .mockResolvedValueOnce(jsonResponse(PROVIDERS_ALL_FRESH));
    const onSelectProvider = vi.fn();
    const user = userEvent.setup();
    render(
      <ChatProvidersPanel
        onError={() => {}}
        activeProvider="claude-code"
        onSelectProvider={onSelectProvider}
      />,
    );
    await waitFor(() => screen.getByText("Claude Code"));
    const unregister = screen.getByRole("button", { name: "Unregister" });
    await user.click(unregister);
    await waitFor(() => expect(onSelectProvider).toHaveBeenCalledWith(null));
  });
});
