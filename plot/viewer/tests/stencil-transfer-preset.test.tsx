/**
 * Regression: the stencil → dataTransfer serialization must preserve
 * ``preset.id``. ``resolveDropTarget`` keys the sub-actor /
 * service-in-category NESTING rules off ``id``; an earlier ``onDragStart``
 * stripped it, so every service-in-category / sub-actor drop silently fell
 * through to a TOP-LEVEL node — bypassing the already-pinned
 * D-2026-05-28-A contract (pinned by service-detail-composition-drop.test,
 * which passes the preset to resolveDropTarget directly and so never
 * exercised the lossy wire round-trip). This test pins the round-trip.
 */
import { describe, expect, it } from "vitest";
import {
  resolveDropTarget,
  STENCIL_PRESETS,
  toTransferPreset,
  type StencilPreset,
} from "../src/canvases/SketchStencil";

function preset(id: string): StencilPreset {
  const p = STENCIL_PRESETS.find((x) => x.id === id);
  if (!p) throw new Error(`no stencil preset ${id}`);
  return p;
}

/** Exactly what the drop handler reconstructs from dataTransfer. */
function overTheWire(p: StencilPreset): StencilPreset {
  return JSON.parse(JSON.stringify(toTransferPreset(p))) as StencilPreset;
}

describe("stencil dataTransfer payload keeps preset.id (nesting rule key)", () => {
  it("toTransferPreset retains id but drops display-only fields", () => {
    const wire = toTransferPreset(preset("service-in-category"));
    expect(wire.id).toBe("service-in-category");
    expect("labelHint" in wire).toBe(false);
    expect("dropHint" in wire).toBe(false);
  });

  it("service-in-category over the wire still requires a Category parent", () => {
    const wire = overTheWire(preset("service-in-category"));
    expect(resolveDropTarget(wire, null, "services")).toHaveProperty("error");
    expect(
      resolveDropTarget(wire, { id: "n_cat", kind: "category" }, "services"),
    ).toEqual({ parentId: "n_cat" });
  });

  it("sub-actor over the wire still requires an Actor parent", () => {
    const wire = overTheWire(preset("sub-actor"));
    expect(resolveDropTarget(wire, null, "actors")).toHaveProperty("error");
    expect(
      resolveDropTarget(wire, { id: "n_actor", kind: "actor" }, "actors"),
    ).toEqual({ parentId: "n_actor" });
  });
});
