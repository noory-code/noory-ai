/**
 * Viewport stability regression — v0.16.18 (D-2026-05-12-T).
 *
 * ``ReactFlow`` exposes a ``fitView`` boolean prop that re-fits the
 * viewport whenever the ``nodes`` array reference changes. In Plot's
 * setup ``useNodesMemo`` returns a fresh array every render (the
 * synthetic anchor is re-injected), so the ``fitView`` prop firing
 * on every render resets the user's manual zoom/pan mid-session.
 *
 * Fix: drop the ``fitView`` prop; call ``inst.fitView({ padding: 0.2 })``
 * once inside ``onInit``. Tab changes naturally re-fit because the
 * wrapper has ``key={activeCanvasKey}`` in App.tsx → remount → onInit
 * fires again.
 *
 * Static guard: regex-grep the ``SketchCanvas.tsx`` source to ensure
 * the antipattern doesn't return. Runtime testing of viewport
 * transforms in JSDOM is unreliable; the static structural check is
 * the cheaper, sharper signal.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const SKETCH_CANVAS_SRC = readFileSync(
  resolve(__dirname, "../src/canvases/SketchCanvas.tsx"),
  "utf8",
);

describe("ReactFlow fitView gating — v0.16.18", () => {
  it("the ReactFlow element does NOT carry a top-level ``fitView`` prop", () => {
    // Reject: ``fitView`` as a JSX boolean prop (with or without
    // explicit ``={true}``) directly on the ``<ReactFlow ...>`` element.
    // Match the lines between ``<ReactFlow`` and the first ``>`` that
    // closes the opening tag.
    const openMatch = SKETCH_CANVAS_SRC.match(/<ReactFlow\b[\s\S]*?>/);
    expect(openMatch, "ReactFlow opening tag not found").toBeTruthy();
    const opening = openMatch![0];
    // ``fitView`` as a standalone attribute name (not ``fitViewOptions``
    // and not inside string / curly-brace expressions on the SAME line).
    const standaloneFitView = /\bfitView\b(?!Options)(?!\s*[:.=])/g;
    const matches = opening.match(standaloneFitView) ?? [];
    expect(
      matches,
      "ReactFlow top-level ``fitView`` prop reintroduced — instead call " +
        "``inst.fitView()`` inside ``onInit`` so viewport doesn't reset on every render",
    ).toEqual([]);
  });

  it("``onInit`` invokes ``inst.fitView`` so initial mount + tab switches still fit", () => {
    // The replacement pattern: onInit should call fitView on the
    // ReactFlow instance once at init. We accept either
    // ``inst.fitView()`` or ``inst.fitView({ ... })``.
    // JSX form: ``onInit={(inst) => { ... }}``.
    expect(SKETCH_CANVAS_SRC).toMatch(/onInit=\{\s*\(\s*\w+\s*\)\s*=>/);
    expect(SKETCH_CANVAS_SRC).toMatch(/\b\w+\.fitView\s*\(/);
  });
});
