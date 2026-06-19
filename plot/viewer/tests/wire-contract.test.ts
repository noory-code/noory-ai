/**
 * Wire-contract guard, viewer side (D-2026-06-10-E).
 *
 * `src/schema/wire-contract.json` is the committed snapshot of the engine's
 * Pydantic wire contract (regenerate: `uv run python -m plot_mcp.schema_export
 * --wire`). This test parses every `domain/{Kind}.ts` `XxxJson` interface and
 * asserts its field set equals the snapshot — the viewer-side half of the
 * parity loop. Because it reads ONLY viewer-repo files, it survives the repo
 * split (unlike the Python `test_schema_parity.py`, which reads both sides).
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import contract from "../src/schema/wire-contract.json";

const DOMAIN = resolve(__dirname, "../src/domain");

const pascal = (kind: string) =>
  kind.split("_").map((p) => p[0].toUpperCase() + p.slice(1)).join("");

const FIELD_RE = /^\s*([A-Za-z_][A-Za-z_0-9]*)\??\s*:/gm;

function stripComments(s: string): string {
  return s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
}

function interfaceFields(src: string, re: RegExp, where: string): Set<string> {
  const m = src.match(re);
  if (!m) throw new Error(`interface not found in ${where}`);
  return new Set([...stripComments(m[1]).matchAll(FIELD_RE)].map((x) => x[1]));
}

const baseSrc = readFileSync(resolve(DOMAIN, "BaseFields.ts"), "utf8");
const baseFields = interfaceFields(
  baseSrc,
  /export\s+interface\s+BaseFieldsJson\s*\{([^}]*)\}/s,
  "BaseFields.ts",
);

describe("wire contract — viewer side (D-2026-06-10-E)", () => {
  it("BaseFieldsJson equals the snapshot base_fields", () => {
    expect([...baseFields].sort()).toEqual(contract.base_fields);
  });

  for (const [kind, fields] of Object.entries(contract.kinds)) {
    it(`${kind}: XxxJson interface equals the snapshot`, () => {
      const src = readFileSync(resolve(DOMAIN, `${pascal(kind)}.ts`), "utf8");
      const specific = interfaceFields(
        src,
        /export\s+interface\s+\w+Json\s+extends\s+BaseFieldsJson\s*\{([^}]*)\}/s,
        `${pascal(kind)}.ts`,
      );
      const full = new Set([...specific, ...baseFields]);
      expect([...full].sort()).toEqual(fields);
    });
  }

  it("covers exactly the 17-kind union", () => {
    expect(Object.keys(contract.kinds)).toHaveLength(17);
  });

  it("self-check: the parser would catch a drifted contract", () => {
    // simulate the engine adding a field the TS side lacks
    const drifted = [...(contract.kinds as Record<string, string[]>).mission, "zzz_new"];
    const src = readFileSync(resolve(DOMAIN, "Mission.ts"), "utf8");
    const specific = interfaceFields(
      src,
      /export\s+interface\s+\w+Json\s+extends\s+BaseFieldsJson\s*\{([^}]*)\}/s,
      "Mission.ts",
    );
    const full = [...new Set([...specific, ...baseFields])].sort();
    expect(full).not.toEqual([...drifted].sort());
  });
});
