/**
 * Dev-only debug probe (D-2026-06-09-D).
 *
 * Collects on-screen state (theme, React Flow watermark presence, per-node
 * computed colour + layout rect) and POSTs it to the engine's `/api/debug`, so
 * an external agent (Claude Code) can introspect the Tauri **WKWebView** — CDP
 * tools (chrome-devtools, Playwright) cannot attach to it on macOS. Not part of
 * the product surface; runs only when `debugEnabled()`.
 */

export interface NodeProbe {
  id: string;
  text: string;
  /** computed `color` of the card (inherited on-card text colour) */
  fg: string;
  /** computed `background-color` (the user's node colour) */
  bg: string;
  rect: { w: number; h: number };
}

export interface ProbeSnapshot {
  ts: number;
  theme: "dark" | "light";
  watermark: boolean;
  nodeCount: number;
  nodes: NodeProbe[];
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
    };
  });
  return {
    ts: Date.now(),
    theme: dark ? "dark" : "light",
    watermark,
    nodeCount: nodes.length,
    nodes,
  };
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

/** Enabled by a build flag (`VITE_PLOT_DEBUG=1`) or a `?debug` URL param. */
export function debugEnabled(): boolean {
  if (import.meta.env.VITE_PLOT_DEBUG === "1") return true;
  try {
    return new URLSearchParams(location.search).has("debug");
  } catch {
    return false;
  }
}

/**
 * Start auto-probing: post once now, then on every debounced DOM mutation.
 * No-op (returns a no-op cleanup) when debug mode is off. Wire it once at the
 * app entry; the returned function disconnects the observer.
 */
export function startDebugProbe(): () => void {
  if (!debugEnabled()) return () => {};
  let t: ReturnType<typeof setTimeout> | undefined;
  const fire = () => {
    t = undefined;
    postProbe();
  };
  const schedule = () => {
    if (t) clearTimeout(t);
    t = setTimeout(fire, 300);
  };
  const obs = new MutationObserver(schedule);
  obs.observe(document.body, { subtree: true, childList: true, attributes: true });
  schedule();
  return () => {
    obs.disconnect();
    if (t) clearTimeout(t);
  };
}
