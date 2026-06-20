/**
 * v0.16.27 — no-god-import static guard (3 of 5 D-2026-05-12-B catch-up
 * artefacts, D-2026-05-13-D).
 *
 * Blocks regression to the v0.13–v0.14 god ``SketchNode`` interface
 * pattern. Four invariants:
 *   1. ``viewer/src/types.ts`` does not declare a god ``SketchNode``
 *      interface (must be a re-export from ``domain/``).
 *   2. Every ``NodeKind`` discriminator value has a corresponding
 *      ``domain/{Kind}.ts`` entity class file.
 *   3. The GENERATED ``domain/wire.gen.ts`` declares each ``{Kind}Json``
 *      wire interface, the class file CONSUMES it from ``./wire.gen``,
 *      and the class file does NOT re-declare an inline ``{Kind}Json``
 *      (codegen Phase A, D-2026-06-20-A — inline interfaces retired;
 *      re-introducing one is the new shape of the god regression).
 *   4. Every domain class registers its parser via
 *      ``registerKindParser("{kind}", {Kind}.fromJson)``.
 *
 * pre_commit_gate.py runs vitest on every viewer commit; a failure here
 * blocks the commit. Together with ``test_ts_codegen.py`` (server-side
 * codegen drift) + ``wire-contract.test.ts`` (viewer snapshot) and
 * ``entity-roundtrip.test.tsx`` (Phase D), these guards keep the
 * discriminated-union pattern intact.
 */
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, test } from "vitest";

const __dirname = dirname(fileURLToPath(import.meta.url));
const VIEWER_SRC = resolve(__dirname, "..", "src");

const NODE_KINDS = [
  "project",
  "mission",
  "core_value",
  "identity",
  "actor",
  "actor_ref",
  "service",
  "feature",
  "rule",
  "content",
  "mission_ref",
  "value_ref",
  "identity_ref",
  "metric",
  "step",
  "decision",
  "note",
  "category",
] as const;

const WIRE_GEN = readFileSync(
  resolve(VIEWER_SRC, "domain", "wire.gen.ts"),
  "utf8",
);

// kebab / snake_case → PascalCase. ``actor_ref`` → ``ActorRef``.
const toClassName = (kind: string): string =>
  kind
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join("");

describe("no-god-import: domain layer integrity", () => {
  test("types.ts does not declare a god SketchNode interface", () => {
    const src = readFileSync(resolve(VIEWER_SRC, "types.ts"), "utf8");
    // The v0.13-v0.14 god pattern was:
    //   export interface SketchNode { ...every typed field flat... }
    // After v0.15 Phase 2.10 (D-2026-05-12-B), SketchNode is a
    // re-export of the discriminated union in ``domain/SketchNode.ts``.
    expect(
      src,
      "types.ts must not declare `export interface SketchNode { ... }` — " +
        "the discriminated union lives in domain/SketchNode.ts and is " +
        "re-exported here. Re-introducing the god interface is the " +
        "D-2026-05-12-B regression.",
    ).not.toMatch(/^\s*export\s+interface\s+SketchNode\b/m);
  });

  test.each(NODE_KINDS)(
    "domain/%s.ts entity class file exists",
    (kind) => {
      const className = toClassName(kind);
      const file = resolve(VIEWER_SRC, "domain", `${className}.ts`);
      expect(
        existsSync(file),
        `domain/${className}.ts is missing for NodeKind '${kind}'. ` +
          `Every kind in viewer/src/types.ts::NodeKind must have a ` +
          `corresponding entity class per plot-entity-template skill.`,
      ).toBe(true);
    },
  );

  test.each(NODE_KINDS)(
    "%s: wire.gen.ts declares {Kind}Json, the class consumes it, no inline god interface",
    (kind) => {
      const className = toClassName(kind);
      // 3a — the GENERATED wire interface exists (the JSON↔domain boundary).
      expect(
        WIRE_GEN,
        `wire.gen.ts must declare 'interface ${className}Json' — the generated ` +
          `wire-shape interface mirroring the Pydantic model ` +
          `(regenerate: uv run python -m plot_mcp.ts_codegen).`,
      ).toMatch(new RegExp(`export\\s+interface\\s+${className}Json\\b`));

      const file = resolve(VIEWER_SRC, "domain", `${className}.ts`);
      if (!existsSync(file)) {
        return; // already reported by the file-exists test
      }
      const src = readFileSync(file, "utf8");

      // 3b — the hand-written class file CONSUMES the generated wire shape
      // (so toJson() is typed by it), importing from ./wire.gen.
      expect(
        src,
        `domain/${className}.ts must import '${className}Json' from './wire.gen' ` +
          `— the generated wire shape (inline interfaces were retired in Phase A).`,
      ).toMatch(
        new RegExp(
          `import\\s+type\\s*\\{[^}]*\\b${className}Json\\b[^}]*\\}\\s*from\\s*["']\\./wire\\.gen["']`,
        ),
      );

      // 3c — the class file must NOT re-declare an inline interface (that is
      // the new shape of the god regression: a hand-edited wire type that
      // drifts from the Pydantic SSOT, bypassing the codegen guard).
      expect(
        src,
        `domain/${className}.ts must NOT declare 'export interface ${className}Json' ` +
          `inline — the wire shape is generated in wire.gen.ts (single SSOT).`,
      ).not.toMatch(new RegExp(`export\\s+interface\\s+${className}Json\\b`));
    },
  );

  test.each(NODE_KINDS)(
    "domain/%s.ts registers its parser via registerKindParser",
    (kind) => {
      const className = toClassName(kind);
      const file = resolve(VIEWER_SRC, "domain", `${className}.ts`);
      if (!existsSync(file)) {
        return;
      }
      const src = readFileSync(file, "utf8");
      const registerRe = new RegExp(
        `registerKindParser\\s*\\(\\s*["']${kind}["']`,
      );
      expect(
        src,
        `domain/${className}.ts must call ` +
          `\`registerKindParser("${kind}", ${className}.fromJson)\` ` +
          `at module load so parseEntity() dispatches correctly.`,
      ).toMatch(registerRe);
    },
  );
});
