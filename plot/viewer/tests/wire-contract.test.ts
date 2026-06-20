/**
 * Wire-contract guard, viewer side (D-2026-06-10-E; codegen Phase A
 * D-2026-06-20-A).
 *
 * `src/schema/wire-contract.json` is the committed snapshot of the engine's
 * Pydantic wire contract; `src/domain/wire.gen.ts` is the GENERATED TS wire
 * types. Regenerate both after a model change:
 *   uv run python -m plot_mcp.schema_export --wire
 *   uv run python -m plot_mcp.ts_codegen
 *
 * This test parses the generated interfaces and asserts each field set equals
 * the snapshot — the viewer-side half of the parity loop. It reads ONLY
 * viewer-repo files (the generated `wire.gen.ts` + the committed snapshot), so
 * it survives the repo split (unlike the Python `test_schema_parity.py`, which
 * used to read both sides).
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import contract from "../src/schema/wire-contract.json";

const WIRE = readFileSync(resolve(__dirname, "../src/domain/wire.gen.ts"), "utf8");

const pascal = (kind: string) =>
  kind.split("_").map((p) => p[0].toUpperCase() + p.slice(1)).join("");

const FIELD_RE = /^\s*([A-Za-z_][A-Za-z_0-9]*)\??\s*:/gm;

function stripComments(s: string): string {
  return s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
}

/** Extract the field names declared on a named interface inside wire.gen.ts.
 *  `${name}\b[^{]*\{` spans the optional ` extends BaseFieldsJson` head; the
 *  exact name + `\b` keep `MissionJson` from matching `MissionRefJson`. */
function namedInterfaceFields(name: string): Set<string> {
  const re = new RegExp(`export\\s+interface\\s+${name}\\b[^{]*\\{([^}]*)\\}`, "s");
  const m = WIRE.match(re);
  if (!m) throw new Error(`interface ${name} not found in wire.gen.ts`);
  return new Set([...stripComments(m[1]).matchAll(FIELD_RE)].map((x) => x[1]));
}

const baseFields = namedInterfaceFields("BaseFieldsJson");

describe("wire contract — viewer side (generated, D-2026-06-10-E / D-2026-06-20-A)", () => {
  it("BaseFieldsJson equals the snapshot base_fields", () => {
    expect([...baseFields].sort()).toEqual(contract.base_fields);
  });

  for (const [kind, fields] of Object.entries(contract.kinds)) {
    it(`${kind}: XxxJson interface equals the snapshot`, () => {
      const specific = namedInterfaceFields(`${pascal(kind)}Json`);
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
    const specific = namedInterfaceFields("MissionJson");
    const full = [...new Set([...specific, ...baseFields])].sort();
    expect(full).not.toEqual([...drifted].sort());
  });
});
