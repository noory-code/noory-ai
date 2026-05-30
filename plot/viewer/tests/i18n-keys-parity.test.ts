/**
 * i18n keys parity guard — D-2026-05-11-D.
 *
 * Every locale JSON in `src/i18n/locales/` must contain the exact
 * same key set as the primary locale `en.json`. Missing or extra
 * keys in `ko.json` (and any future locale) fail this test.
 *
 * Adding a new key:
 * 1. Add to `en.json`.
 * 2. Add the translated value at the same path in `ko.json`.
 * 3. This test passes.
 *
 * Per `feedback_plot_global_service.md` — Plot is a global service;
 * locale drift is a release blocker.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import en from "../src/i18n/locales/en.json";
import ko from "../src/i18n/locales/ko.json";

type Tree = { [key: string]: string | Tree };

function flatKeys(obj: Tree, prefix = ""): string[] {
  const out: string[] = [];
  for (const [k, v] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${k}` : k;
    if (typeof v === "string") {
      out.push(path);
    } else {
      out.push(...flatKeys(v as Tree, path));
    }
  }
  return out.sort();
}

describe("i18n locale parity (D-2026-05-11-D)", () => {
  const enKeys = flatKeys(en as unknown as Tree);
  const koKeys = flatKeys(ko as unknown as Tree);

  it("ko.json has the same key set as en.json", () => {
    expect(koKeys).toEqual(enKeys);
  });

  it("every value is a non-empty string", () => {
    for (const [locale, tree] of [
      ["en", en],
      ["ko", ko],
    ] as const) {
      const flat = flatKeys(tree as unknown as Tree);
      for (const key of flat) {
        const value = key
          .split(".")
          .reduce<unknown>(
            (acc, part) =>
              acc && typeof acc === "object" && part in (acc as object)
                ? (acc as Record<string, unknown>)[part]
                : undefined,
            tree,
          );
        expect(typeof value, `${locale}:${key}`).toBe("string");
        expect((value as string).length, `${locale}:${key}`).toBeGreaterThan(0);
      }
    }
  });
});

// D-2026-05-30-J — the parity test above imports the JSON, which the
// JS engine has ALREADY de-duplicated (a duplicate key silently keeps
// only the LAST occurrence). That hid the v0.28.3 bug where a second
// top-level "canvas" block overwrote the first, wiping `canvas.tabs.*`
// so the canvas tab labels rendered as raw keys ("변수명처럼"). This
// guard reads the RAW text so a duplicate top-level key is caught.
describe("i18n locales — no duplicate top-level keys (D-2026-05-30-J)", () => {
  function topLevelKeys(locale: string): string[] {
    const text = readFileSync(
      resolve(__dirname, `../src/i18n/locales/${locale}.json`),
      "utf8",
    );
    const keys: string[] = [];
    // Pretty-printed, 2-space indent, single-line values → a line that
    // starts with exactly two spaces + a quoted key is a top-level key.
    for (const line of text.split("\n")) {
      const m = /^ {2}"([^"]+)":/.exec(line);
      if (m) keys.push(m[1]);
    }
    return keys;
  }

  it.each(["en", "ko"])("%s.json: each top-level key appears exactly once", (loc) => {
    const keys = topLevelKeys(loc);
    const seen = new Set<string>();
    const dups = new Set<string>();
    for (const k of keys) {
      if (seen.has(k)) dups.add(k);
      seen.add(k);
    }
    expect(
      [...dups],
      `duplicate top-level key(s) in ${loc}.json — JSON keeps only the LAST, ` +
        `silently dropping the earlier block: ${[...dups].join(", ")}`,
    ).toEqual([]);
  });
});
