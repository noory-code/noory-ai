/**
 * FOUC pre-paint parity (D-2026-06-08-A). The inline `<head>` script in
 * index.html applies `.dark` before React mounts, to avoid a flash of the
 * wrong theme. It CANNOT import the ESM theme module that early, so it
 * duplicates three literals: the storage key, the media query, and the `dark`
 * class. This test pins those duplicates against the real source of truth
 * (`theme/theme.ts` + `theme/ThemeProvider.tsx`) so they cannot drift.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { THEME_STORAGE_KEY } from "../src/theme/theme";

const INDEX = readFileSync(resolve(__dirname, "../index.html"), "utf8");
const PROVIDER = readFileSync(resolve(__dirname, "../src/theme/ThemeProvider.tsx"), "utf8");
const MEDIA_QUERY = "(prefers-color-scheme: dark)";

describe("FOUC pre-paint parity (D-2026-06-08-A)", () => {
  it("index.html has a pre-paint script that runs before the module entry", () => {
    const headScript = INDEX.indexOf("<script>");
    const moduleEntry = INDEX.indexOf('type="module"');
    expect(headScript).toBeGreaterThan(-1);
    expect(headScript).toBeLessThan(moduleEntry); // pre-paint runs first
  });

  it("pre-paint uses the same storage key as theme.ts", () => {
    expect(THEME_STORAGE_KEY).toBe("plot:theme");
    expect(INDEX).toContain(`"${THEME_STORAGE_KEY}"`);
  });

  it("pre-paint uses the same prefers-color-scheme query as ThemeProvider", () => {
    expect(INDEX).toContain(MEDIA_QUERY);
    expect(PROVIDER).toContain(MEDIA_QUERY); // both sides agree
  });

  it("pre-paint adds the dark class to documentElement", () => {
    expect(INDEX).toMatch(/document\.documentElement\.classList\.add\(\s*["']dark["']\s*\)/);
  });
});
