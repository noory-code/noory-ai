/**
 * Engine-base seam (VITE_PLOT_ENGINE) — characterization guard for the
 * EngineClient seed in ``src/api.ts``.
 *
 * Pins how the HTTP base and WebSocket base are derived from the engine
 * origin so a future edit can't silently break a bundled-desktop (Tauri)
 * build, where the frontend is served from ``tauri://`` and must call the
 * sidecar engine at an explicit ``http://127.0.0.1:5190`` origin.
 *
 * Contract:
 *   - VITE_PLOT_ENGINE set   → HTTP URLs are prefixed with it; WS derives
 *     ``ws(s)://`` by swapping the ``http`` scheme.
 *   - VITE_PLOT_ENGINE unset → HTTP URLs are same-origin relative; WS uses
 *     the document host.
 *
 * NOTE: this guards pre-existing seam code committed alongside it, so it is
 * a characterization test (green from the start), not Red-first TDD — the
 * behaviour predates this commit. ``API_BASE`` is captured at module load
 * from ``import.meta.env``, so each case re-imports the module after stubbing
 * the env (``vi.resetModules`` + dynamic import).
 */
import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.resetModules();
});

async function loadApi(engine: string) {
  vi.resetModules();
  vi.stubEnv("VITE_PLOT_ENGINE", engine);
  return import("../src/api");
}

function stubFetchOk() {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ projects: [] }),
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function stubWebSocket(): () => string {
  let url = "";
  vi.stubGlobal(
    "WebSocket",
    class {
      constructor(u: string) {
        url = u;
      }
      close() {}
    } as unknown as typeof WebSocket,
  );
  return () => url;
}

describe("engine-base seam (VITE_PLOT_ENGINE)", () => {
  it("HTTP base: prefixes fetch URLs with the engine origin when set", async () => {
    const api = await loadApi("http://127.0.0.1:5190");
    const fetchMock = stubFetchOk();
    await api.listProjects("/p");
    expect(fetchMock.mock.calls[0][0]).toBe(
      "http://127.0.0.1:5190/api/projects?project_path=%2Fp",
    );
  });

  it("HTTP base: same-origin relative when unset (empty)", async () => {
    const api = await loadApi("");
    const fetchMock = stubFetchOk();
    await api.listProjects("/p");
    expect(fetchMock.mock.calls[0][0]).toBe("/api/projects?project_path=%2Fp");
  });

  it("WS base: derives ws:// from the engine origin when set", async () => {
    const api = await loadApi("http://127.0.0.1:5190");
    const wsUrl = stubWebSocket();
    const sock = api.openProjectSocket("/p", { onEvent: () => {} });
    expect(wsUrl()).toBe("ws://127.0.0.1:5190/ws?project_path=%2Fp");
    sock.close();
  });

  it("WS base: same-origin host when unset (empty)", async () => {
    const api = await loadApi("");
    const wsUrl = stubWebSocket();
    const sock = api.openProjectSocket("/p", { onEvent: () => {} });
    // same-origin: ws://<document host>/ws?... (host varies by JSDOM config)
    expect(wsUrl()).toMatch(/^ws:\/\/[^/]+\/ws\?project_path=%2Fp$/);
    sock.close();
  });
});
