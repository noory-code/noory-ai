/**
 * Engine auth seam — viewer-side wiring tests (D-2026-06-12-F).
 *
 * Pins three guarantees:
 *
 *   1. ``setEngineAuthToken`` is idempotent, accepts ``null`` to clear, and
 *      treats empty strings as "no token" so a Tauri command that returns
 *      ``""`` doesn't silently break enforcement.
 *   2. With a token set, every engine fetch grows an
 *      ``Authorization: Bearer <token>`` header (verified via the global
 *      ``fetch`` spy). With no token, the request goes through unmodified
 *      — the dev-parity guarantee.
 *   3. ``initEngineAuth`` resolves the token via the Tauri invoke command
 *      first, falls back to the dev env var, and falls through to ``null``
 *      when both are absent.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  _peekEngineAuthToken,
  listProjects,
  setEngineAuthToken,
} from "../src/api";

// ``__TAURI_INTERNALS__`` is declared as ``unknown`` in the viewer's
// existing globals (shell/ProjectPicker.tsx); we cast at assignment time so
// the test stays compatible with that declaration without redeclaring.
type TauriInternalsShape = {
  invoke?: (cmd: string, args?: Record<string, unknown>) => Promise<unknown>;
};

function setTauriInternals(value: TauriInternalsShape | undefined): void {
  (window as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ = value;
}

const fetchSpy = vi.fn();

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

beforeEach(() => {
  fetchSpy.mockReset();
  fetchSpy.mockResolvedValue(jsonResponse({ projects: [], migrated: [] }));
  vi.stubGlobal("fetch", fetchSpy);
  setEngineAuthToken(null);
});

afterEach(() => {
  vi.unstubAllGlobals();
  setEngineAuthToken(null);
});

describe("engineFetch (D-2026-06-12-F)", () => {
  it("sends no Authorization header when no token is set (dev parity)", async () => {
    await listProjects("/tmp/ws");
    expect(fetchSpy).toHaveBeenCalledOnce();
    const init = fetchSpy.mock.calls[0][1] as RequestInit | undefined;
    // init may be undefined (some sites pass nothing) — either way no auth.
    const headers = new Headers(init?.headers ?? {});
    expect(headers.has("authorization")).toBe(false);
  });

  it("sends Authorization: Bearer <token> on every fetch when a token is set", async () => {
    setEngineAuthToken("secret-tok");
    await listProjects("/tmp/ws");
    const init = fetchSpy.mock.calls[0][1] as RequestInit | undefined;
    const headers = new Headers(init?.headers ?? {});
    expect(headers.get("authorization")).toBe("Bearer secret-tok");
  });

  it("setEngineAuthToken treats empty string as null", async () => {
    setEngineAuthToken("");
    expect(_peekEngineAuthToken()).toBeNull();
    await listProjects("/tmp/ws");
    const init = fetchSpy.mock.calls[0][1] as RequestInit | undefined;
    const headers = new Headers(init?.headers ?? {});
    expect(headers.has("authorization")).toBe(false);
  });

  it("setEngineAuthToken(null) clears a previously-set token", async () => {
    setEngineAuthToken("first");
    setEngineAuthToken(null);
    expect(_peekEngineAuthToken()).toBeNull();
    await listProjects("/tmp/ws");
    const init = fetchSpy.mock.calls[0][1] as RequestInit | undefined;
    const headers = new Headers(init?.headers ?? {});
    expect(headers.has("authorization")).toBe(false);
  });
});

describe("initEngineAuth (D-2026-06-12-F)", () => {
  afterEach(() => {
    setTauriInternals(undefined);
  });

  it("uses the Tauri invoke command when present", async () => {
    const invoke = vi.fn().mockResolvedValue("tauri-token-xyz");
    setTauriInternals({ invoke });
    const { initEngineAuth } = await import("../src/app/auth");
    await initEngineAuth();
    expect(invoke).toHaveBeenCalledWith("plot_auth_token");
    expect(_peekEngineAuthToken()).toBe("tauri-token-xyz");
  });

  it("falls back to null when Tauri is absent and no VITE env var is set", async () => {
    // VITE_PLOT_AUTH_TOKEN is undefined in test env by default.
    const { initEngineAuth } = await import("../src/app/auth");
    await initEngineAuth();
    expect(_peekEngineAuthToken()).toBeNull();
  });

  it("swallows Tauri invoke errors and falls through to dev token / null", async () => {
    const invoke = vi.fn().mockRejectedValue(new Error("no such command"));
    setTauriInternals({ invoke });
    const { initEngineAuth } = await import("../src/app/auth");
    await initEngineAuth();
    // No dev env var either → null. The bundled engine's 401 is louder
    // than a thrown promise here would be.
    expect(_peekEngineAuthToken()).toBeNull();
  });
});
