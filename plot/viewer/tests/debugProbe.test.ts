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
import { afterEach, describe, expect, it } from "vitest";
import { collectProbe } from "../src/lib/debugProbe";

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
  });
});
