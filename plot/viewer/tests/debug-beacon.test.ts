/**
 * D-2026-06-10-B — debug-flavor boot beacon in index.html.
 *
 * The module-graph probe (debugProbe.ts) cannot report a failure of the
 * module graph itself: if any import in main.tsx's graph throws at load, the
 * probe never starts and the debug channel stays silent — indistinguishable
 * from "engine down". The beacon is an INLINE index.html script (independent
 * of the bundle) that posts a boot marker immediately and wires
 * error/unhandledrejection reporters, all gated on the build-time
 * %VITE_PLOT_DEBUG% HTML env replacement so release bundles carry a dead
 * guard, no live reporter.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const HTML = readFileSync(resolve(__dirname, "../index.html"), "utf8");

describe("debug boot beacon (D-2026-06-10-B)", () => {
  it("index.html carries an inline beacon gated on %VITE_PLOT_DEBUG%", () => {
    expect(HTML).toContain('if ("%VITE_PLOT_DEBUG%" !== "1") return;');
  });

  it("posts boot + error reports to the engine debug channel", () => {
    expect(HTML).toContain("/api/debug");
    expect(HTML).toContain("unhandledrejection");
    // window error hook for module-graph load failures
    expect(HTML).toMatch(/addEventListener\("error"/);
  });
});
