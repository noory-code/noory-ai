/**
 * Cursor baseline guard — D-2026-05-11-C.
 *
 * styles.css must contain ZERO cursor declarations. Pure RF default
 * + Tailwind preflight composes to the user's mental model per
 * D-2026-05-11-A. Adding any cursor rule requires a fresh
 * D-YYYY-MM-DD-X decision id and updating this test together.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("styles.css cursor baseline (D-2026-05-11-C)", () => {
  it("contains no cursor declaration outside comments", () => {
    const css = readFileSync(
      resolve(__dirname, "../src/styles.css"),
      "utf8",
    );
    const stripped = css.replace(/\/\*[\s\S]*?\*\//g, "");
    const matches = stripped.match(/cursor\s*:/gi) ?? [];
    expect(matches).toEqual([]);
  });
});
