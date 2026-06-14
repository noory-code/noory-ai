/**
 * Selected-edge highlight guard — D-2026-06-14-C.
 *
 * ``edgeTransform`` sets each edge's stroke INLINE (value-flow recolour),
 * which beats React Flow's default ``.selected`` class styling — so without
 * an ``!important`` override a selected edge shows no visual change. This
 * static guard pins the styles.css rule that restores selection feedback.
 *
 * CSS rendering can't be observed in JSDOM (no layout / computed cascade for
 * RF's vendor classes), so per the Plot Gate 1.5 "static guard for behaviour
 * JSDOM can't observe" rule this asserts the rule's presence structurally.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const STYLES = readFileSync(
  resolve(__dirname, "../src/styles.css"),
  "utf-8",
);

describe("selected-edge highlight (D-2026-06-14-C)", () => {
  it("styles.css highlights a selected edge path with !important stroke", () => {
    expect(STYLES).toMatch(/\.react-flow__edge\.selected/);
    // Must override the inline stroke → requires !important on stroke.
    const block = STYLES.slice(STYLES.indexOf(".react-flow__edge.selected"));
    expect(block).toMatch(/stroke:[^;]*!important/);
  });
});
