/**
 * Dev-only debug probe (D-2026-06-09-D).
 *
 * Collects on-screen state (theme, React Flow watermark presence, per-node
 * computed colour + layout rect) and POSTs it to the engine's `/api/debug`, so
 * an external agent (Claude Code) can introspect the Tauri **WKWebView** — CDP
 * tools (chrome-devtools, Playwright) cannot attach to it on macOS. Not part of
 * the product surface; runs only when `debugEnabled()`.
 *
 * Phase 2: in the Tauri shell the probe also captures a real PNG of the app
 * window (tauri-plugin-screenshots) and includes its file path in the
 * snapshot, so the agent can Read actual pixels. Throttled — capture is far
 * heavier than the DOM walk. macOS asks for Screen Recording permission on
 * first capture (one-time, per app signature).
 */
import {
  getScreenshotableWindows,
  getWindowScreenshot,
  type ScreenshotableWindow,
} from "tauri-plugin-screenshots-api";

export interface NodeProbe {
  id: string;
  text: string;
  /** computed `color` of the card (inherited on-card text colour) */
  fg: string;
  /** computed `background-color` (the user's node colour) */
  bg: string;
  rect: { w: number; h: number };
  /** className of the card root — diagnosis aid (e.g. is aspect-square on?) */
  classes: string;
  /** Sizing diagnosis: own inline style + computed aspect-ratio, and the
   *  React Flow wrapper (parent) box + inline style — to tell whether a size
   *  is imposed from outside (wrapper) or grown from inside (content). */
  inline: string;
  aspect: string;
  /** Computed `box-sizing` — N-1: distinguishes border-box (96×96 expected)
   *  from content-box (148×132). If WKWebView reports `border-box` and the
   *  rect is still 96×132, the box-sizing hypothesis is dead. */
  boxSizing: string;
  /** The first non-handle direct child of the card — the in-flow `h-full`
   *  flex column. A percentage-height vs aspect-ratio cycle would show as
   *  inner.h driving rect.h taller than the min-width square. */
  inner: { w: number; h: number } | null;
  parent: { w: number; h: number; inline: string } | null;
}

export interface ProbeSnapshot {
  ts: number;
  theme: "dark" | "light";
  watermark: boolean;
  nodeCount: number;
  nodes: NodeProbe[];
  /** React Flow viewport zoom — read from `.react-flow__viewport` transform.
   *  The earlier session assumed ×2 from the persisted anchor size; this
   *  ground-truths it. `null` outside a canvas (e.g. on ProjectPicker). */
  zoom: number | null;
  /** Absolute path of the latest window PNG (Tauri shell only). */
  screenshotPath?: string;
}

/** First child `<div>` that isn't a React Flow handle — the in-flow content
 *  wrapper. A `h-full` percentage height resolves against this box. */
function innerChildBox(card: HTMLElement): { w: number; h: number } | null {
  for (const child of Array.from(card.children)) {
    if (!(child instanceof HTMLElement)) continue;
    if (child.classList.contains("react-flow__handle")) continue;
    if (child.tagName !== "DIV") continue;
    const r = child.getBoundingClientRect();
    return { w: Math.round(r.width), h: Math.round(r.height) };
  }
  return null;
}

/** Parse `scale(n)` out of the React Flow viewport's transform. */
function readViewportZoom(): number | null {
  const vp = document.querySelector<HTMLElement>(".react-flow__viewport");
  if (!vp) return null;
  const m = vp.style.transform.match(/scale\(([-0-9.]+)\)/);
  return m ? Number(m[1]) : null;
}

/** Read the current screen state into a serialisable snapshot. */
export function collectProbe(): ProbeSnapshot {
  const dark = document.documentElement.classList.contains("dark");
  const watermark = !!document.querySelector(".react-flow__attribution");
  const cards = Array.from(document.querySelectorAll<HTMLElement>("[data-node-id]"));
  const nodes: NodeProbe[] = cards.map((el) => {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      id: el.getAttribute("data-node-id") ?? "",
      text: (el.textContent ?? "").trim().slice(0, 60),
      fg: cs.color,
      bg: cs.backgroundColor,
      rect: { w: Math.round(r.width), h: Math.round(r.height) },
      classes: el.className,
      inline: el.getAttribute("style") ?? "",
      aspect: cs.aspectRatio,
      boxSizing: cs.boxSizing,
      inner: innerChildBox(el),
      parent: el.parentElement
        ? {
            w: Math.round(el.parentElement.getBoundingClientRect().width),
            h: Math.round(el.parentElement.getBoundingClientRect().height),
            inline: el.parentElement.getAttribute("style") ?? "",
          }
        : null,
    };
  });
  return {
    ts: Date.now(),
    theme: dark ? "dark" : "light",
    watermark,
    nodeCount: nodes.length,
    nodes,
    zoom: readViewportZoom(),
  };
}

/** Pick the Plot app window out of the capturable-window list.
 *  appName match first (bundled .app, most stable), then a title containing
 *  "Plot" (dev builds report the binary name as appName). */
export function pickPlotWindow(windows: ScreenshotableWindow[]): number | null {
  const byApp = windows.find((w) => w.appName === "Plot");
  if (byApp) return byApp.id;
  const byTitle = windows.find((w) => w.title.includes("Plot"));
  return byTitle ? byTitle.id : null;
}

const inTauri = (): boolean =>
  typeof (window as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ !== "undefined";

const SCREENSHOT_MIN_INTERVAL_MS = 3_000;
let lastShotAt = 0;

/** Capture the app window as a PNG (Tauri only, throttled). Returns the
 *  saved file path, or null outside Tauri / inside the throttle window /
 *  on any capture error (e.g. Screen Recording permission not granted).
 *
 *  Time-boxed: without a TCC grant (fresh app identity) the plugin call can
 *  stall indefinitely — the race keeps the numeric probe flowing; the
 *  screenshot joins once permission is granted. */
export async function captureScreenshot(): Promise<string | null> {
  if (!inTauri()) return null;
  const now = Date.now();
  if (now - lastShotAt < SCREENSHOT_MIN_INTERVAL_MS) return null;
  lastShotAt = now;
  const timeout = new Promise<null>((resolve) => setTimeout(() => resolve(null), 1_500));
  try {
    const shot = (async () => {
      const id = pickPlotWindow(await getScreenshotableWindows());
      if (id === null) return null;
      return await getWindowScreenshot(id);
    })();
    return await Promise.race([shot, timeout]);
  } catch {
    return null; // permission denied / plugin absent — numeric probe still works
  }
}

/** POST a snapshot to the engine debug channel (fire-and-forget). */
export function postProbe(snap: ProbeSnapshot = collectProbe()): void {
  const base = import.meta.env.VITE_PLOT_ENGINE ?? "";
  void fetch(`${base}/api/debug`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(snap),
  }).catch(() => {
    /* dev-only; ignore when the engine isn't reachable */
  });
}

/** BUILD-TIME flavor gate: enabled only when the bundle was built with
 *  `VITE_PLOT_DEBUG=1` (the debug flavor). No runtime escape hatch — a
 *  release bundle must not expose the probe via URL params. */
export function debugEnabled(): boolean {
  return import.meta.env.VITE_PLOT_DEBUG === "1";
}

/**
 * Start auto-probing: post once now, on every debounced DOM mutation, and on
 * a 10s heartbeat. The heartbeat exists because the very first POST can race
 * the engine's startup (the sidecar takes ~1s; the probe fires at ~300ms) and
 * POSTs are fire-and-forget — without it a static screen (e.g. the
 * ProjectPicker) would never re-post and the channel would stay empty.
 * No-op (returns a no-op cleanup) when debug mode is off. Wire it once at the
 * app entry; the returned function disconnects observer + heartbeat.
 */
export function startDebugProbe(): () => void {
  if (!debugEnabled()) return () => {};
  let t: ReturnType<typeof setTimeout> | undefined;
  const fire = () => {
    t = undefined;
    void captureScreenshot().then((screenshotPath) => {
      const snap = collectProbe();
      postProbe(screenshotPath ? { ...snap, screenshotPath } : snap);
    });
  };
  const schedule = () => {
    if (t) clearTimeout(t);
    t = setTimeout(fire, 300);
  };
  const obs = new MutationObserver(schedule);
  obs.observe(document.body, { subtree: true, childList: true, attributes: true });
  const heartbeat = setInterval(schedule, 10_000);
  schedule();
  return () => {
    obs.disconnect();
    clearInterval(heartbeat);
    if (t) clearTimeout(t);
  };
}
