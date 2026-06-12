/**
 * D-2026-06-12-C / ROADMAP Track 1.4 final — keep three artefacts in
 * lock-step on every semantic theme token:
 *
 *   1. `src/theme/tokens.ts` exports `SEMANTIC_TOKENS` (the SSOT).
 *   2. `src/theme/tokens.css` `:root` + `.dark` declare `--name` CSS vars.
 *   3. `tailwind.config.js` `colors: { name: "rgb(var(--name) / ...)" }`.
 *
 * If a developer adds a token to one place and forgets the others, the
 * UI silently breaks (a class compiles but the var is undefined → falls
 * back to inherited / 0 / rgba(0 0 0 / 0)). This guard catches that at
 * test time instead of at runtime.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { SEMANTIC_TOKENS } from "../src/theme/tokens";

const TOKENS_CSS = readFileSync(
  resolve(__dirname, "../src/theme/tokens.css"),
  "utf8",
);
const TAILWIND_CONFIG = readFileSync(
  resolve(__dirname, "../tailwind.config.js"),
  "utf8",
);

function cssVarsIn(block: string): Set<string> {
  const out = new Set<string>();
  for (const m of block.matchAll(/--([\w-]+):\s*/g)) {
    out.add(m[1]);
  }
  return out;
}

function rootBlock(): string {
  const m = TOKENS_CSS.match(/:root\s*\{([^}]*)\}/);
  if (!m) throw new Error(":root block not found in tokens.css");
  return m[1];
}

function darkBlock(): string {
  const m = TOKENS_CSS.match(/\.dark\s*\{([^}]*)\}/);
  if (!m) throw new Error(".dark block not found in tokens.css");
  return m[1];
}

function tailwindColorKeys(): Set<string> {
  const out = new Set<string>();
  // Pull every `name: "rgb(var(--name) ..."` mapping. Match both quoted
  // ("foo-bar") and unquoted (foo) JS object keys; the regex anchors on
  // the `rgb(var(--…))` value so non-token entries are skipped.
  for (const m of TAILWIND_CONFIG.matchAll(
    /(?:"([\w-]+)"|([a-z][\w-]*)):\s*"rgb\(var\(--([\w-]+)\)\s*\/\s*<alpha-value>\)"/g,
  )) {
    const key = m[1] ?? m[2];
    const varName = m[3];
    // Sanity: tailwind key should equal the var name.
    out.add(key ?? varName);
  }
  return out;
}

const TOKEN_SET = new Set(SEMANTIC_TOKENS);

describe("semantic theme tokens (D-2026-06-12-C, SSOT in src/theme/tokens.ts)", () => {
  it(":root in tokens.css declares exactly the tokens in SEMANTIC_TOKENS", () => {
    const declared = cssVarsIn(rootBlock());
    const missing = [...TOKEN_SET].filter((t) => !declared.has(t)).sort();
    const extra = [...declared].filter((t) => !TOKEN_SET.has(t)).sort();
    expect(
      { missing, extra },
      `:root in tokens.css must declare each token in SEMANTIC_TOKENS ` +
        `exactly once (and no others). Missing = declared in TS but ` +
        `not in :root. Extra = declared in :root but not in TS. ` +
        `Adjust src/theme/tokens.ts OR src/theme/tokens.css until both ` +
        `lists are empty.`,
    ).toEqual({ missing: [], extra: [] });
  });

  it(".dark in tokens.css declares exactly the same tokens", () => {
    const declared = cssVarsIn(darkBlock());
    const missing = [...TOKEN_SET].filter((t) => !declared.has(t)).sort();
    const extra = [...declared].filter((t) => !TOKEN_SET.has(t)).sort();
    expect(
      { missing, extra },
      `.dark in tokens.css must declare each token in SEMANTIC_TOKENS ` +
        `exactly once. A token present in :root but missing from .dark ` +
        `would inherit the light value into dark mode — silently broken. ` +
        `Adjust src/theme/tokens.ts OR src/theme/tokens.css.`,
    ).toEqual({ missing: [], extra: [] });
  });

  it("tailwind.config.js exposes exactly the tokens in SEMANTIC_TOKENS", () => {
    const keys = tailwindColorKeys();
    const missing = [...TOKEN_SET].filter((t) => !keys.has(t)).sort();
    const extra = [...keys].filter((t) => !TOKEN_SET.has(t)).sort();
    expect(
      { missing, extra },
      `tailwind.config.js \`colors\` must map each token in ` +
        `SEMANTIC_TOKENS to \`rgb(var(--token) / <alpha-value>)\` ` +
        `exactly once. Missing = token in TS but no tailwind class can ` +
        `be generated for it. Extra = tailwind has a class but no TS / ` +
        `CSS backing.`,
    ).toEqual({ missing: [], extra: [] });
  });
});
