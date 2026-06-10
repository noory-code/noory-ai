/**
 * D-2026-06-09-D — the viewer's debug probe collects on-screen state (theme,
 * watermark presence, per-node computed colour + rect) so it can be POSTed to
 * the engine's /api/debug and read by an external agent (which cannot attach
 * CDP tools to the Tauri WKWebView on macOS).
 *
 * JSDOM does not resolve Tailwind classes → computed colours, so `fg` here is
 * whatever JSDOM returns; the value is verified for *shape* (a string), while
 * the real colour check happens against a live .app snapshot. Theme, watermark,
 * node id/text, and rect collection are fully testable here.
 */
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  collectProbe,
  debugEnabled,
  pickPlotWindow,
  startDebugProbe,
} from "../src/lib/debugProbe";

// Hanging-capture double: without Screen Recording permission (fresh TCC
// identity) the plugin call can stall forever — the numeric probe must not
// be held hostage by it.
vi.mock("tauri-plugin-screenshots-api", () => ({
  getScreenshotableWindows: vi.fn(() => new Promise(() => {})),
  getWindowScreenshot: vi.fn(),
}));

afterEach(() => {
  document.documentElement.classList.remove("dark");
  document.body.innerHTML = "";
});

describe("collectProbe", () => {
  it("reports theme from the <html> dark class", () => {
    expect(collectProbe().theme).toBe("light");
    document.documentElement.classList.add("dark");
    expect(collectProbe().theme).toBe("dark");
  });

  it("reports React Flow watermark presence", () => {
    expect(collectProbe().watermark).toBe(false);
    const a = document.createElement("a");
    a.className = "react-flow__attribution";
    document.body.appendChild(a);
    expect(collectProbe().watermark).toBe(true);
  });

  it("collects nodes by data-node-id with text, fg, and rect", () => {
    const card = document.createElement("div");
    card.setAttribute("data-node-id", "n1");
    card.textContent = "Hello";
    document.body.appendChild(card);
    const snap = collectProbe();
    expect(snap.nodeCount).toBe(1);
    expect(snap.nodes[0].id).toBe("n1");
    expect(snap.nodes[0].text).toContain("Hello");
    expect(typeof snap.nodes[0].fg).toBe("string");
    expect(snap.nodes[0].rect).toHaveProperty("w");
    expect(snap.nodes[0].rect).toHaveProperty("h");
    // sizing-diagnosis fields (inline style / aspect-ratio / RF wrapper box)
    expect(typeof snap.nodes[0].inline).toBe("string");
    expect(typeof snap.nodes[0].aspect).toBe("string");
    expect(snap.nodes[0].parent).toHaveProperty("w");
  });
});

describe("debugEnabled (flavor gating)", () => {
  // The probe is BUILD-TIME gated only (debug flavor sets VITE_PLOT_DEBUG=1).
  // A release bundle must not expose a runtime escape hatch — `?debug` in the
  // URL must NOT enable the probe.
  afterEach(() => vi.unstubAllEnvs());

  it("?debug URL param does NOT enable the probe", () => {
    vi.stubEnv("VITE_PLOT_DEBUG", "");
    window.history.replaceState(null, "", "/?debug");
    expect(debugEnabled()).toBe(false);
  });

  it("VITE_PLOT_DEBUG=1 enables it", () => {
    vi.stubEnv("VITE_PLOT_DEBUG", "1");
    expect(debugEnabled()).toBe(true);
  });
});

describe("startDebugProbe heartbeat", () => {
  // The very first POST can race the engine's startup (sidecar takes ~1s;
  // the probe fires at ~300ms) and the POST is fire-and-forget — without a
  // heartbeat a static screen (e.g. the ProjectPicker) would never re-post
  // and the channel would stay empty. A 10s heartbeat re-posts regardless
  // of DOM mutations.
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("re-posts on the heartbeat even with zero DOM mutations", async () => {
    vi.useFakeTimers();
    vi.stubEnv("VITE_PLOT_DEBUG", "1");
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}"));
    vi.stubGlobal("fetch", fetchMock);
    const stop = startDebugProbe();
    await vi.advanceTimersByTimeAsync(500); // initial debounced post
    const initial = fetchMock.mock.calls.length;
    expect(initial).toBeGreaterThanOrEqual(1);
    await vi.advanceTimersByTimeAsync(25_000); // two heartbeat ticks later
    expect(fetchMock.mock.calls.length).toBeGreaterThan(initial);
    stop();
  });
});

describe("startDebugProbe — capture must not block the numeric probe", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("posts the snapshot even when the screenshot call hangs (no TCC grant)", async () => {
    vi.useFakeTimers();
    vi.stubEnv("VITE_PLOT_DEBUG", "1");
    // simulate Tauri so captureScreenshot actually calls the (hanging) plugin
    vi.stubGlobal("__TAURI_INTERNALS__", {});
    (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ = {};
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}"));
    vi.stubGlobal("fetch", fetchMock);
    const stop = startDebugProbe();
    await vi.advanceTimersByTimeAsync(5_000); // debounce + capture timeout
    expect(fetchMock).toHaveBeenCalled();
    stop();
    delete (window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__;
  });
});

describe("pickPlotWindow (screenshot target selection)", () => {
  // tauri.conf.json: productName "Plot", window title "Plot". The bundled app
  // window is matched by appName first (most stable), then by title.
  it("prefers the window whose appName is Plot", () => {
    const id = pickPlotWindow([
      { id: 1, name: "x", title: "Other", appName: "Finder" },
      { id: 2, name: "y", title: "Plot", appName: "Plot" },
    ]);
    expect(id).toBe(2);
  });

  it("falls back to a title containing Plot (dev builds)", () => {
    const id = pickPlotWindow([
      { id: 1, name: "x", title: "Other", appName: "Finder" },
      { id: 3, name: "y", title: "Plot", appName: "app" },
    ]);
    expect(id).toBe(3);
  });

  it("returns null when no window matches", () => {
    expect(pickPlotWindow([{ id: 1, name: "x", title: "T", appName: "A" }])).toBeNull();
  });
});
