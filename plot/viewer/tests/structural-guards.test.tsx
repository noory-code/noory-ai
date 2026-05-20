/**
 * Structural guards — Phase 5.2 (D-2026-05-12-F).
 *
 * Three contracts pin the v0.15 reset's structural shape so a future
 * commit cannot regress to a god component without the build failing
 * with a pointer to the relevant decision:
 *
 *   1. ``no-god-union-import``: the deleted god components
 *      (``SketchInspector.tsx``, ``SketchNode.tsx``) must remain
 *      absent from disk, and no canvas file (wrappers + sketch hooks
 *      + App.tsx) may use a ``switch (X.kind)`` god dispatch outside
 *      the allowlisted registries / domain layer / per-kind factory.
 *      Per-kind narrowing guards (``if (node.kind !== "X") return null``)
 *      inside ``inspectors/{kind}/`` or ``nodes/{kind}/`` files
 *      remain allowed — they are the *consumers* of the union, not
 *      god dispatchers.
 *
 *   2. ``loc-budget``: each canvas-internal file fits inside a
 *      ceiling proportional to its responsibility. The ceiling is
 *      tight enough that bloat triggers a decision before review;
 *      lowering a ceiling requires a fresh ``D-YYYY-MM-DD-X`` entry.
 *      *Raise* via decision (the file outgrew its single responsibility
 *      and needs a split), never via test edit.
 *
 *   3. ``registry-completeness``: the 15 per-kind directories
 *      (``canvases/nodes/{kind}/`` + ``canvases/inspectors/{kind}/``)
 *      must each exist, and the runtime registries must enumerate
 *      all 15. Catches a kind drop / addition during refactor.
 *
 * Adding a 16th kind requires touching the registries and the
 * ``KIND_DIRS`` SSOTs in both this file and
 * ``styles-cursor-baseline.test.tsx`` — the friction is intentional.
 */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { NODE_RENDERERS } from "../src/canvases/nodes/registry";

const SRC = resolve(__dirname, "../src");

function loc(rel: string): number {
  return readFileSync(resolve(SRC, rel), "utf8").split("\n").length;
}

function stripComments(s: string): string {
  let out = s.replace(/\/\*[\s\S]*?\*\//g, "");
  out = out
    .split("\n")
    .map((line) => line.replace(/\/\/.*$/, ""))
    .join("\n");
  return out;
}

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

// ---------------------------------------------------------------------
// Contract 1: no-god-union-import
// ---------------------------------------------------------------------

const GOD_FILES_ABSENT = [
  "canvases/SketchInspector.tsx",
  "canvases/SketchNode.tsx",
] as const;

/** Files where a ``switch (X.kind)`` god-dispatch would re-introduce
 *  the v0.14 anti-pattern. Per-kind files (`inspectors/{kind}/`,
 *  `nodes/{kind}/`, registries, and the domain factory in
 *  `domain/createBlankNode.ts`) are explicitly excluded. */
function listForbiddenSwitchFiles(): string[] {
  const out: string[] = [];

  // 4 canvas wrappers + shared shell
  out.push(
    "canvases/FoundationCanvas.tsx",
    "canvases/ActorsCanvas.tsx",
    "canvases/ServicesCanvas.tsx",
    "canvases/ServiceDetailCanvas.tsx",
    "canvases/SketchCanvas.tsx",
    "canvases/nodes/BaseNode.tsx",
    "canvases/inspectors/BaseInspector.tsx",
    "canvases/inspectors/KindInspector.tsx",
    "canvases/inspectors/DetailsSection.tsx",
    "App.tsx",
  );

  // All sketch hooks
  for (const e of readdirSync(resolve(SRC, "canvases/sketch"), { withFileTypes: true })) {
    if (e.isFile() && (e.name.endsWith(".ts") || e.name.endsWith(".tsx"))) {
      out.push(`canvases/sketch/${e.name}`);
    }
  }

  return out.sort();
}

const FORBIDDEN_SWITCH_FILES = listForbiddenSwitchFiles();

describe("no-god-union-import (Phase 5.2)", () => {
  it.each(GOD_FILES_ABSENT)(
    "the god file %s must remain absent from disk",
    (rel) => {
      expect(existsSync(resolve(SRC, rel)), `god file present: ${rel}`).toBe(false);
    },
  );

  it.each(FORBIDDEN_SWITCH_FILES)(
    "no `switch (X.kind)` god dispatch in %s",
    (rel) => {
      const src = stripComments(readFileSync(resolve(SRC, rel), "utf8"));
      const matches = src.match(/switch\s*\(\s*[\w.]*\.?kind\s*\)/g) ?? [];
      expect(matches, `god dispatch in ${rel}`).toEqual([]);
    },
  );
});

// ---------------------------------------------------------------------
// Contract 2: loc-budget
// ---------------------------------------------------------------------

/**
 * LOC ceilings — see plan ``dazzling-greeting-diffie.md`` Phase 5.2
 * + D-2026-05-12-F (the no-growth ceiling at 830) + D-2026-05-12-H
 * (the App.tsx split that landed the plan target ≤ 400 over five
 * commits v0.16.1 → v0.16.5). Raise via decision (file outgrew its
 * single responsibility and needs a split), never via test edit.
 *
 * App.tsx: the plan target ``≤ 400`` is now live as of v0.16.5
 * (App.tsx 381 LOC). Header / CanvasTabs / HelpCheatsheet /
 * ServiceDetailModal / states moved to ``viewer/src/shell/``;
 * useUrlSync / useAvailableNodes / useAppKeyboard moved to
 * ``viewer/src/hooks/``.
 */
const LOC_BUDGETS: Record<string, { ceiling: number; note?: string }> = {
  "App.tsx": {
    ceiling: 425,
    note: "Plan target locked in v0.16.5 (D-2026-05-12-H). v0.23.x (D-2026-05-17-J) raised 400 → 410 to wire onUnpublishNode on both SketchCanvas slots. v0.24.14 (D-2026-05-21-C) raised 410 → 425 to wire snapshot-view state (viewingTag / enterTagView / exitTagView + applyEdit guard + cache swap) into Header / Sidebar.",
  },
  "canvases/SketchCanvas.tsx": {
    ceiling: 450,
    note: "v0.18.0 Phase 3 (D-2026-05-16-E) raised 420 → 440 to absorb the onPublishNode prop wiring through to SketchInspectorBindings. v0.23.x (D-2026-05-17-J) raised 440 → 450 to add the onUnpublishNode prop wiring (same pattern).",
  },
  "canvases/nodes/BaseNode.tsx": { ceiling: 250 },
  "canvases/inspectors/BaseInspector.tsx": {
    ceiling: 380,
    note: "v0.18.0 Phase 3 (D-2026-05-16-E) raised 220 → 270 (publish button + confirm-dialog handler). v0.22.0 (D-2026-05-17-H) raised 270 → 285 to wrap the button in a dirty-aware IIFE. v0.23.0 (D-2026-05-17-I) raised 285 → 295 (PublishedVersionsSection insertion). v0.23.1 (D-2026-05-17-J) raised 295 → 340 (Unpublish button). v0.23.2 (D-2026-05-17-K) raised 340 → 380 to move publish + unpublish from the header cluster into a sticky footer (primary CTA layout, user-picked via ASCII-mockup AskUserQuestion).",
  },
  "canvases/FoundationCanvas.tsx": { ceiling: 150 },
  "canvases/ActorsCanvas.tsx": { ceiling: 150 },
  "canvases/ServicesCanvas.tsx": { ceiling: 150 },
  "canvases/ServiceDetailCanvas.tsx": { ceiling: 150 },
};

function perKindFiles(parent: string): string[] {
  return KIND_DIRS.map((k) => `${parent}/${k}/index.tsx`).filter((p) =>
    existsSync(resolve(SRC, p)),
  );
}

describe("loc-budget (Phase 5.2)", () => {
  it.each(Object.entries(LOC_BUDGETS))(
    "%s fits inside its ceiling",
    (rel, { ceiling }) => {
      const actual = loc(rel);
      expect(actual, `${rel} LOC budget`).toBeLessThanOrEqual(ceiling);
    },
  );

  it("every per-kind node renderer ≤ 100 LOC", () => {
    for (const rel of perKindFiles("canvases/nodes")) {
      const actual = loc(rel);
      expect(actual, `${rel} per-kind node LOC`).toBeLessThanOrEqual(100);
    }
  });

  it("every per-kind inspector ≤ 250 LOC", () => {
    for (const rel of perKindFiles("canvases/inspectors")) {
      const actual = loc(rel);
      expect(actual, `${rel} per-kind inspector LOC`).toBeLessThanOrEqual(250);
    }
  });
});

// ---------------------------------------------------------------------
// Contract 3: registry-completeness
// ---------------------------------------------------------------------

describe("registry-completeness (Phase 5.2)", () => {
  it("every kind has a per-kind node renderer file", () => {
    for (const kind of KIND_DIRS) {
      const path = `canvases/nodes/${kind}/index.tsx`;
      expect(existsSync(resolve(SRC, path)), `missing: ${path}`).toBe(true);
      // Sanity: file is non-empty.
      expect(statSync(resolve(SRC, path)).size, `empty: ${path}`).toBeGreaterThan(0);
    }
  });

  it("every kind has a per-kind inspector file", () => {
    for (const kind of KIND_DIRS) {
      const path = `canvases/inspectors/${kind}/index.tsx`;
      expect(existsSync(resolve(SRC, path)), `missing: ${path}`).toBe(true);
      expect(statSync(resolve(SRC, path)).size, `empty: ${path}`).toBeGreaterThan(0);
    }
  });

  it("NODE_RENDERERS registry contains exactly the 15 kinds", () => {
    expect(Object.keys(NODE_RENDERERS).sort()).toEqual(
      KIND_DIRS.slice().sort() as unknown as string[],
    );
  });
});
