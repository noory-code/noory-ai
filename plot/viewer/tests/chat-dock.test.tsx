/**
 * R7 chat dock (D-2026-06-11-E … D-2026-06-14-D).
 *
 * The dock is the right-side collapsible container that holds the chat
 * surface. Behaviour pinned here:
 *
 *   - Dock collapses/expands; collapse persists in localStorage.
 *   - Provider connection lives behind a COMPACT BAR, collapsed by default
 *     (D-2026-06-14-D) — clicking it reveals the full ChatProvidersPanel.
 *   - The compact bar shows the active CLI label.
 *   - claude-code is selectable with a billing warning (D-2026-06-14-B).
 *   - Per-canvas scope switcher (D-2026-06-13-H).
 *
 * Fetch is mocked by URL (not call order) so it's robust to which surface
 * fetches first.
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

const PROVIDERS_FRESH_REGISTERED = {
  providers: [
    { name: "claude-code", installed: true, registered: true, config_path: "~/.claude.json" },
    { name: "codex", installed: true, registered: true, config_path: "~/.codex/config.toml" },
    { name: "gemini", installed: false, registered: false, config_path: "~/.gemini/settings.json" },
  ],
};

// Mutable per-test fixtures the URL router serves.
let selectionValue: { provider: string | null };
let providersValue: unknown;

beforeEach(() => {
  fetchSpy.mockReset();
  selectionValue = { provider: null };
  providersValue = PROVIDERS_FRESH;
  fetchSpy.mockImplementation((url: unknown, init?: RequestInit) => {
    const u = String(url);
    if (u.includes("/api/chat/provider")) {
      if (init && init.method === "PUT") {
        return Promise.resolve(jsonResponse({ ok: true }));
      }
      return Promise.resolve(jsonResponse(selectionValue));
    }
    if (u.includes("/api/mcp/providers")) {
      return Promise.resolve(jsonResponse(providersValue));
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

async function expandProviders(user: ReturnType<typeof userEvent.setup>) {
  const bar = await screen.findByRole("button", { name: /ai agent/i });
  await user.click(bar);
  return bar;
}

describe("ChatDock — dock + compact provider bar", () => {
  it("keeps the provider panel collapsed behind a compact bar by default", async () => {
    selectionValue = { provider: "codex" };
    providersValue = PROVIDERS_FRESH_REGISTERED;
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const bar = await screen.findByRole("button", { name: /ai agent/i });
    expect(bar.getAttribute("aria-expanded")).toBe("false");
    // Full provider list (register buttons / radios) is NOT mounted.
    expect(screen.queryByRole("button", { name: /register plot/i })).toBeNull();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
  });

  it("reveals the provider panel when the compact bar is clicked", async () => {
    providersValue = PROVIDERS_FRESH_REGISTERED;
    const user = userEvent.setup();
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const bar = await expandProviders(user);
    await waitFor(() => screen.getByText("Codex"));
    expect(bar.getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByText("Claude Code")).toBeTruthy();
  });

  it("shows the active provider label on the compact bar", async () => {
    selectionValue = { provider: "codex" };
    providersValue = PROVIDERS_FRESH_REGISTERED;
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const bar = await screen.findByRole("button", { name: /ai agent/i });
    await waitFor(() => expect(bar.textContent).toContain("Codex"));
  });

  it("marks the bar connected (status indicator) when an agent is active, without expanding", async () => {
    selectionValue = { provider: "codex" };
    providersValue = PROVIDERS_FRESH_REGISTERED;
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const bar = await screen.findByRole("button", { name: /ai agent/i });
    await waitFor(() => expect(bar.getAttribute("data-connected")).toBe("1"));
    expect(bar.getAttribute("aria-expanded")).toBe("false"); // not expanded
    expect(bar.textContent).toContain("Codex");
  });

  it("marks the bar disconnected when no agent is selected", async () => {
    selectionValue = { provider: null };
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const bar = await screen.findByRole("button", { name: /ai agent/i });
    await waitFor(() => expect(bar.getAttribute("data-connected")).toBe("0"));
  });

  it("forwards a provider-fetch error to onError when the panel is opened", async () => {
    const onError = vi.fn();
    fetchSpy.mockImplementation((url: unknown) => {
      if (String(url).includes("/api/mcp/providers")) {
        return Promise.resolve(jsonResponse({ error: "engine offline" }, 500));
      }
      return Promise.resolve(jsonResponse({ provider: null }));
    });
    const user = userEvent.setup();
    render(<ChatDock onError={onError} />);
    await expandProviders(user);
    await waitFor(() => expect(onError).toHaveBeenCalled());
  });
});

describe("ChatDock — message frame", () => {
  it("renders the message log frame with the no-workspace caption", async () => {
    render(<ChatDock onError={() => {}} />);
    const log = await screen.findByRole("log", { name: /chat messages/i });
    expect(log).toBeTruthy();
    expect(screen.getByText(/open a workspace/i)).toBeTruthy();
  });

  it("keeps the input disabled until a workspace + active CLI are present", async () => {
    render(<ChatDock onError={() => {}} />);
    const input = (await screen.findByRole("textbox", {
      name: /message input/i,
    })) as HTMLTextAreaElement;
    expect(input.disabled).toBe(true);
    expect(input.placeholder.toLowerCase()).toContain("pick a chat cli");
    expect(
      (screen.getByRole("button", { name: /^send$/i }) as HTMLButtonElement).disabled,
    ).toBe(true);
  });

});

describe("ChatDock — provider selection", () => {
  it("does not call /api/chat/provider when workspaceRoot is not provided", async () => {
    const user = userEvent.setup();
    render(<ChatDock onError={() => {}} />);
    await expandProviders(user);
    await waitFor(() => screen.getByText("Codex"));
    const calls = fetchSpy.mock.calls.map((c) => String(c[0]));
    expect(calls.some((u) => u.includes("/api/chat/provider"))).toBe(false);
  });

  it("loads the persisted chat provider on mount when workspaceRoot is given", async () => {
    selectionValue = { provider: "claude-code" };
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    await waitFor(() => {
      const calls = fetchSpy.mock.calls.map((c) => String(c[0]));
      expect(
        calls.some((u) => u.includes("/api/chat/provider") && u.includes("project_path=")),
      ).toBe(true);
    });
  });

  it("PUTs the new selection to the server when a radio is clicked", async () => {
    // claude-code carries a radio (D-2026-06-14-B), but exercise codex here.
    providersValue = PROVIDERS_FRESH_REGISTERED;
    const user = userEvent.setup();
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    await expandProviders(user);
    const radios = await screen.findAllByRole("radio");
    const codex = (radios as HTMLInputElement[]).find((r) => r.value === "codex")!;
    await user.click(codex);
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
      });
    });
  });

  it("enables input + shows the billing warning for a claude-code selection", async () => {
    selectionValue = { provider: "claude-code" };
    providersValue = PROVIDERS_FRESH_REGISTERED;
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const input = (await screen.findByRole("textbox", {
      name: /message input/i,
    })) as HTMLTextAreaElement;
    await waitFor(() => expect(input.disabled).toBe(false));
    const warning = await screen.findByRole("note");
    expect(warning.getAttribute("data-warning")).toBe("claude-billing");
    expect(warning.textContent?.toLowerCase()).toContain("claude -p");
  });

  it("shows no billing warning for a codex selection", async () => {
    selectionValue = { provider: "codex" };
    providersValue = PROVIDERS_FRESH_REGISTERED;
    render(<ChatDock onError={() => {}} workspaceRoot="/tmp/ws" />);
    const bar = await screen.findByRole("button", { name: /ai agent/i });
    await waitFor(() => expect(bar.textContent).toContain("Codex"));
    expect(screen.queryByRole("note")).toBeNull();
  });
});

describe("ChatDock — scope switcher (D-2026-06-13-H; 2-tab, D-2026-06-15-H)", () => {
  it("shows the [active canvas | project] two segments", async () => {
    selectionValue = { provider: "codex" };
    render(
      <ChatDock onError={() => {}} workspaceRoot="/tmp/ws" activeScope="foundation" />,
    );
    await screen.findByRole("tablist", { name: /conversation/i });
    const labels = screen.getAllByRole("tab").map((t) => t.textContent);
    expect(labels).toContain("Foundation");
    expect(labels).toContain("Project");
    // Exactly two tabs — the full F/A/S picker was reverted (v0.78.0).
    expect(labels).not.toContain("Actors");
    expect(
      screen.getByRole("tab", { name: "Foundation" }).getAttribute("aria-selected"),
    ).toBe("true");
  });

  it("labels a service-detail canvas tab with the service NAME", async () => {
    selectionValue = { provider: "codex" };
    render(
      <ChatDock
        onError={() => {}}
        workspaceRoot="/tmp/ws"
        activeScope="service_detail:svc_one"
        activeScopeLabel="Login service"
      />,
    );
    await screen.findByRole("tablist", { name: /conversation/i });
    const labels = screen.getAllByRole("tab").map((t) => t.textContent);
    expect(labels).toContain("Login service"); // the service name, not "Service detail"
    expect(labels).not.toContain("Service detail");
    expect(labels).not.toContain("service_detail:svc_one");
  });

  it("falls back to the base label when no service name is given", async () => {
    selectionValue = { provider: "codex" };
    render(
      <ChatDock
        onError={() => {}}
        workspaceRoot="/tmp/ws"
        activeScope="service_detail:svc_one"
      />,
    );
    await screen.findByRole("tablist", { name: /conversation/i });
    const labels = screen.getAllByRole("tab").map((t) => t.textContent);
    expect(labels).toContain("Service detail");
    expect(labels).not.toContain("service_detail:svc_one");
  });

  it("switches the selected segment to project on click", async () => {
    selectionValue = { provider: "codex" };
    const user = userEvent.setup();
    render(
      <ChatDock onError={() => {}} workspaceRoot="/tmp/ws" activeScope="actors" />,
    );
    const projectTab = await screen.findByRole("tab", { name: "Project" });
    await user.click(projectTab);
    expect(projectTab.getAttribute("aria-selected")).toBe("true");
    expect(
      screen.getByRole("tab", { name: "Actors" }).getAttribute("aria-selected"),
    ).toBe("false");
  });

  it("omits the scope switcher when the active scope is already project", async () => {
    selectionValue = { provider: "codex" };
    render(
      <ChatDock onError={() => {}} workspaceRoot="/tmp/ws" activeScope="project" />,
    );
    const bar = await screen.findByRole("button", { name: /ai agent/i });
    await waitFor(() => expect(bar.textContent).toContain("Codex"));
    expect(screen.queryByRole("tablist", { name: /conversation/i })).toBeNull();
  });
});
