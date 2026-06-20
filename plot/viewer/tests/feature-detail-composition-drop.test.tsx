// D-2026-05-28-A — FeatureDetail = user-authored interaction graph
// (relations + value flow, NOT a service-container hierarchy).  User's
// own design intent (transcribed 2026-05-28):
//
//   - Actor nodes (Hero, Fan, …) — actor_ref
//   - Interaction nodes (액터 간 접점) — step / metric / free node;
//     positioned BETWEEN actors, not nested under a service
//   - Value nodes (인터랙션에서 교환되는 것) — same; between
//     interactions, not nested under a service
//   - Upper-link nodes (mission / core value) — mission_ref / value_ref
//
// The pre-D-2026-05-28-A behaviour of ``resolveDropTarget`` was a
// holdover from a prior "composition lives inside a service container"
// model and forced step/metric/rule/content drops to require a
// ``service`` parent.  That conflicts directly with the
// D-2026-05-26-C FeatureDetail = self-authored interaction graph
// decision: the user must be able to drop an interaction (step) or a
// branch point (decision) on empty space and wire it up themselves.
//
// This file pins the new contract.  The test uses ``resolveDropTarget``
// directly because that single pure function is the gate that decides
// every drop on every canvas.
import { describe, it, expect } from "vitest";
import { resolveDropTarget, STENCIL_PRESETS, type StencilPreset } from "../src/canvases/SketchStencil";

function findPreset(id: string): StencilPreset {
  const p = STENCIL_PRESETS.find((x) => x.id === id);
  if (!p) throw new Error(`stencil preset not found: ${id}`);
  return p;
}

describe("resolveDropTarget — FeatureDetail composition is free-form (D-2026-05-28-A)", () => {
  // rule is not in STENCIL_PRESETS (inspector-only kind —
  // SPEC §Foundation typed-text storage); only step + decision are the
  // canvas-droppable composition presets (metric / content retired
  // 2026-06-20, D-2026-06-20-H).
  const COMPOSITION_IDS = ["step", "decision"];

  it.each(COMPOSITION_IDS)(
    "FeatureDetail: %s drop on empty space resolves to top-level (no service parent required)",
    (id) => {
      const preset = findPreset(id);
      const resolved = resolveDropTarget(preset, null, "feature");
      expect(resolved, `${id} drop on empty in feature`).toEqual({ parentId: null });
    },
  );

  it.each(COMPOSITION_IDS)(
    "FeatureDetail: %s drop inside a service container still nests (backwards-compat)",
    (id) => {
      const preset = findPreset(id);
      const resolved = resolveDropTarget(
        preset,
        { id: "n_svc", kind: "service" },
        "feature",
      );
      expect(resolved).toEqual({ parentId: "n_svc" });
    },
  );

  it("Services canvas: category is OPTIONAL — service nests if dropped on one, else top-level (D-2026-06-13-D)", () => {
    const preset = findPreset("service-in-category");
    // Empty space → top-level (no error; supersedes D-2026-05-28-A).
    expect(resolveDropTarget(preset, null, "services")).toEqual({ parentId: null });
    // Dropped on a non-category container → still top-level.
    expect(
      resolveDropTarget(preset, { id: "n_svc", kind: "service" }, "services"),
    ).toEqual({ parentId: null });
    // Dropped on a category → nests under it.
    expect(
      resolveDropTarget(preset, { id: "n_cat", kind: "category" }, "services"),
    ).toEqual({ parentId: "n_cat" });
  });

  it("Services canvas: a feature nests under a service when dropped on one, else top-level (D-2026-06-17-D)", () => {
    const preset = findPreset("feature-in-service");
    // Empty space → top-level (optional nesting).
    expect(resolveDropTarget(preset, null, "services")).toEqual({ parentId: null });
    // Dropped on a non-service container → top-level.
    expect(
      resolveDropTarget(preset, { id: "n_cat", kind: "category" }, "services"),
    ).toEqual({ parentId: null });
    // Dropped on a service → nests under it (directed edge service→feature).
    expect(
      resolveDropTarget(preset, { id: "n_svc", kind: "service" }, "services"),
    ).toEqual({ parentId: "n_svc" });
  });

  it("Actors canvas: sub-actor still requires an Actor parent (unchanged)", () => {
    const preset = findPreset("sub-actor");
    const onEmpty = resolveDropTarget(preset, null, "actors");
    expect(onEmpty).toHaveProperty("error");
    const onActor = resolveDropTarget(
      preset,
      { id: "n_actor", kind: "actor" },
      "actors",
    );
    expect(onActor).toEqual({ parentId: "n_actor" });
  });
});
