/**
 * Light-token fidelity (D-2026-06-07-C). The dark/light migration replaced
 * raw Tailwind palette classes with semantic tokens. SPEC §"Appearance"
 * promises the LIGHT UI is preserved 1:1 — that only holds if each token's
 * `:root` (light) value equals the original palette colour it replaced.
 *
 * This test parses the `:root` block of `styles.css` and asserts the core
 * neutral tokens still equal their original slate / white RGB channels, so a
 * future edit can't silently shift the light theme.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const CSS = readFileSync(resolve(__dirname, "../src/styles.css"), "utf8");

function rootVars(): Record<string, string> {
  const block = CSS.match(/:root\s*\{([^}]*)\}/);
  if (!block) throw new Error(":root block not found in styles.css");
  const out: Record<string, string> = {};
  for (const m of block[1].matchAll(/(--[\w-]+):\s*([^;]+);/g)) {
    out[m[1]] = m[2].trim();
  }
  return out;
}

describe("theme light-token fidelity (D-2026-06-07-C)", () => {
  const vars = rootVars();

  // token -> original Tailwind palette colour (RGB channels) it replaced.
  const EXPECTED: Record<string, string> = {
    "--surface": "255 255 255", // white
    "--surface-muted": "248 250 252", // slate-50
    "--surface-subtle": "241 245 249", // slate-100
    "--surface-inverse": "15 23 42", // slate-900
    "--fg": "51 65 85", // slate-700
    "--fg-strong": "15 23 42", // slate-900
    "--fg-secondary": "71 85 105", // slate-600
    "--fg-muted": "100 116 139", // slate-500
    "--fg-faint": "148 163 184", // slate-400
    "--fg-inverse": "255 255 255", // white
    "--line": "226 232 240", // slate-200
    "--line-strong": "203 213 225", // slate-300
  };

  for (const [token, rgb] of Object.entries(EXPECTED)) {
    it(`${token} light value = ${rgb}`, () => {
      expect(vars[token]).toBe(rgb);
    });
  }

  it("defines a matching .dark override for every :root token", () => {
    const darkBlock = CSS.match(/\.dark\s*\{([^}]*)\}/);
    expect(darkBlock, ".dark block not found").toBeTruthy();
    const darkVars = new Set(
      [...darkBlock![1].matchAll(/(--[\w-]+):/g)].map((m) => m[1]),
    );
    const missing = Object.keys(vars).filter((t) => !darkVars.has(t));
    expect(missing, `tokens missing a .dark value: ${missing.join(", ")}`).toEqual([]);
  });
});
