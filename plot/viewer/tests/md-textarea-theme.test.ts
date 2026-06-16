/**
 * Regression (D-2026-06-16-E): the Inspector's MD editor (CodeMirror) must
 * follow the app theme. Its ``baseTheme`` previously hardcoded
 * ``backgroundColor: "white"`` + slate/indigo literals, so in dark mode the
 * editor was a white island with the wrong border/caret colours (user-visible
 * on every typed-text field — service problem/what/…, decision, etc.).
 *
 * Static guard: the theme must reference Plot's CSS tokens (``rgb(var(--…))``)
 * and must NOT hardcode raw colours. JSDOM can't resolve CSS-var colours, so
 * we pin the structural cause at the source.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const SRC = resolve(__dirname, "../src/canvases/inspectors/shared/MdTextarea.tsx");
const src = readFileSync(SRC, "utf8");

describe("MdTextarea CodeMirror theme follows app tokens (D-2026-06-16-E)", () => {
  it("does not hardcode a white background", () => {
    expect(src).not.toMatch(/backgroundColor:\s*["']white["']/);
  });

  it("does not hardcode the old slate/indigo literals", () => {
    expect(src).not.toContain("rgb(203 213 225)"); // slate-300 border
    expect(src).not.toContain("rgb(79 70 229)"); // indigo-600 focus
  });

  it("references the theme tokens for surface, fg, and accent", () => {
    expect(src).toContain("var(--surface)");
    expect(src).toContain("var(--fg)");
    expect(src).toContain("var(--accent)");
  });
});
