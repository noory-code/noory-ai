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
