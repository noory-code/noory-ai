/**
 * Cursor baseline guard — D-2026-05-11-C (styles.css) + D-2026-05-12-D
 * (extended to wrappers / nodes / inspectors / sketch hooks).
 *
 * Two contracts, both verified statically:
 *
 *   1. ``viewer/src/styles.css`` contains ZERO raw ``cursor:``
 *      declarations. The cursor SSOT is the React Flow vendor CSS +
 *      ``@reactflow/node-resizer`` vendor CSS + Tailwind preflight
 *      (``button, [role="button"] { cursor: pointer }``) — see
 *      ``docs/CURSOR.md``. Adding any rule to ``styles.css`` requires
 *      a fresh ``D-YYYY-MM-DD-X`` decision (per D-2026-05-11-A).
 *
 *   2. Every canvas-internal source file (wrappers, BaseNode, the
 *      15 per-kind node renderers, BaseInspector, KindInspector, the
 *      15 per-kind inspectors, inspectors/shared/*, all sketch hooks)
 *      contains ZERO raw ``cursor:`` declarations and ZERO JS-side
 *      ``style.cursor`` assignments. Combined with contract #1, this
 *      guarantees per-canvas cursor drift is structurally impossible:
 *      all 4 wrappers compose the same shared CSS stack (RF vendor +
 *      Tailwind preflight) and add nothing of their own.
 *
 * Note on Tailwind utility classes (``cursor-grab``,
 * ``cursor-not-allowed``, ``cursor-pointer``, ``cursor-grabbing``):
 * these are *class strings* (``cursor-X`` with a hyphen, not a colon)
 * and intentionally appear on chrome surfaces (SketchStencil drag
 * tray, SketchContextMenu items, SketchToolbar buttons, modal forms,
 * DetailsSection chrome). They are not canvas/node/edge surfaces and
 * are shared identically across all 4 wrappers. The regex below
 * matches ``cursor:`` (colon-suffixed) so utility classes pass.
 */
import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const SRC = resolve(__dirname, "../src");

function read(rel: string): string {
  return readFileSync(resolve(SRC, rel), "utf8");
}

function stripComments(s: string): string {
  // /* ... */
  let out = s.replace(/\/\*[\s\S]*?\*\//g, "");
  // // ... (line comments — strip only outside string literals; the
  // simple form below is good enough for these source files because
  // we know they don't embed ``//`` inside strings on the same line
  // as a real ``cursor:`` token).
  out = out
    .split("\n")
    .map((line) => line.replace(/\/\/.*$/, ""))
    .join("\n");
  return out;
}

function rawCursorMatches(src: string): string[] {
  return stripComments(src).match(/cursor\s*:/gi) ?? [];
}

function styleCursorAssignMatches(src: string): string[] {
  // ``el.style.cursor =`` / ``.style.cursor=`` / ``style.cursor =``
  return stripComments(src).match(/\bstyle\s*\.\s*cursor\s*=/g) ?? [];
}

/** Per-kind directory names. The 15-way structural reset
 *  (D-2026-05-12-B) pins these as the SSOT for node-kind enumeration;
 *  any drift is caught by the count assertion below. */
const KIND_DIRS = [
  "actor",
  "actor_ref",
  "category",
  "content",
  "core_value",
  "identity",
  "identity_ref",
  "metric",
  "mission",
  "mission_ref",
  "project",
  "rule",
  "service",
  "step",
  "value_ref",
] as const;

function listKindIndexFiles(parent: string): string[] {
  // Verify each expected kind directory exists; ignore non-kind sibling
  // directories (e.g. ``inspectors/shared/`` which holds composition
  // helpers, not a per-kind inspector).
  const entries = new Set(
    readdirSync(resolve(SRC, parent), { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name),
  );
  return KIND_DIRS.filter((k) => entries.has(k))
    .map((k) => `${parent}/${k}/index.tsx`)
    .sort();
}

function listSketchHookFiles(): string[] {
  const dir = "canvases/sketch";
  const entries = readdirSync(resolve(SRC, dir), { withFileTypes: true });
  const out: string[] = [];
  for (const e of entries) {
    if (e.isFile() && (e.name.endsWith(".ts") || e.name.endsWith(".tsx"))) {
      out.push(`${dir}/${e.name}`);
    }
  }
  return out.sort();
}

function listInspectorSharedFiles(): string[] {
  const dir = "canvases/inspectors/shared";
  const entries = readdirSync(resolve(SRC, dir), { withFileTypes: true });
  const out: string[] = [];
  for (const e of entries) {
    if (e.isFile() && (e.name.endsWith(".ts") || e.name.endsWith(".tsx"))) {
      out.push(`${dir}/${e.name}`);
    }
  }
  return out.sort();
}

// ---- Contract #1: styles.css ---------------------------------------

describe("styles.css cursor baseline (D-2026-05-11-C)", () => {
  it("contains no cursor declaration outside comments", () => {
    expect(rawCursorMatches(read("styles.css"))).toEqual([]);
  });
});

// ---- Contract #2: canvas-internal source files ---------------------

const WRAPPER_FILES = [
  "canvases/FoundationCanvas.tsx",
  "canvases/ActorsCanvas.tsx",
  "canvases/ServicesCanvas.tsx",
  "canvases/ServiceDetailCanvas.tsx",
] as const;

const SHARED_SHELL_FILES = [
  "canvases/SketchCanvas.tsx",
  "canvases/nodes/BaseNode.tsx",
  "canvases/nodes/registry.ts",
  "canvases/inspectors/BaseInspector.tsx",
  "canvases/inspectors/KindInspector.tsx",
  "canvases/inspectors/DetailsSection.tsx",
  "canvases/inspectors/registry.ts",
  "canvases/inspectors/types.ts",
] as const;

const PER_KIND_NODE_FILES = listKindIndexFiles("canvases/nodes");
const PER_KIND_INSPECTOR_FILES = listKindIndexFiles("canvases/inspectors");
const SKETCH_HOOK_FILES = listSketchHookFiles();
const INSPECTOR_SHARED_FILES = listInspectorSharedFiles();

const ALL_CANVAS_FILES: readonly string[] = [
  ...WRAPPER_FILES,
  ...SHARED_SHELL_FILES,
  ...PER_KIND_NODE_FILES,
  ...PER_KIND_INSPECTOR_FILES,
  ...INSPECTOR_SHARED_FILES,
  ...SKETCH_HOOK_FILES,
];

describe("Canvas-internal cursor baseline (D-2026-05-12-D)", () => {
  it("the registry covers all 15 per-kind node and 15 per-kind inspector files", () => {
    expect(PER_KIND_NODE_FILES.length).toBe(15);
    expect(PER_KIND_INSPECTOR_FILES.length).toBe(15);
  });

  it("no canvas-internal file is empty (sanity)", () => {
    for (const rel of ALL_CANVAS_FILES) {
      expect(read(rel).length, `empty file: ${rel}`).toBeGreaterThan(0);
    }
  });

  it.each(ALL_CANVAS_FILES)(
    "contains no raw `cursor:` declaration outside comments — %s",
    (rel) => {
      expect(rawCursorMatches(read(rel))).toEqual([]);
    },
  );

  it.each(ALL_CANVAS_FILES)(
    "contains no `style.cursor =` JS assignment — %s",
    (rel) => {
      expect(styleCursorAssignMatches(read(rel))).toEqual([]);
    },
  );
});
