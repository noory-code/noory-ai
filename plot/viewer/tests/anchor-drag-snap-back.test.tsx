/**
 * Anchor drag snap-back regression — v0.16.15 (D-2026-05-12-Q).
 *
 * React Flow is a *controlled* component: ``nodes`` prop = SSOT for
 * positions. Anchor drag flow:
 *
 *   user drag → onNodesChange (RF) → handleNodesChange →
 *   applyAnchorChange → onAnchorChange(patch) →
 *   patchProjectAnchor (async, 100-500ms) → replaceSummary
 *
 * Before this fix, ``summaries`` state only updated *after* the PATCH
 * resolved, so during the round-trip the computed projectAnchor prop
 * carried the OLD position → RF snapped the anchor back. Fix: update
 * local state OPTIMISTICALLY (via ``applyOptimisticAnchorPatch``) before
 * the network call.
 *
 * This file tests the pure helper that drives the optimistic merge.
 * App.tsx wraps the network round-trip + error revert around it.
 */
import { describe, expect, it } from "vitest";
import {
  applyOptimisticAnchorPatch,
  resolveAnchorPlacement,
} from "../src/lib/anchorOptimistic";
import type { ProjectDoc } from "../src/types";

function makeProject(overrides: Partial<ProjectDoc> = {}): ProjectDoc {
  return {
    id: "p1",
    name: "Test",
    created: "2026-05-12",
    updated: "2026-05-12T00:00:00Z",
    version: 1,
    anchors: {
      foundation: {
        x: -75,
        y: -75,
        width: 150,
        height: 150,
        color: "#fef3c7",
        shape: "circle",
      },
    },
    tags: [],
    feature_details: [],
    ...overrides,
  } as ProjectDoc;
}

describe("anchorOptimistic — optimistic anchor update", () => {
  it("patches x/y on the foundation anchor without losing other fields", () => {
    const current = makeProject();
    const merged = applyOptimisticAnchorPatch(current, "foundation", {
      x: 200,
      y: 100,
    });
    expect(merged.anchors?.foundation).toEqual({
      x: 200,
      y: 100,
      width: 150,
      height: 150,
      color: "#fef3c7",
      shape: "circle",
    });
    expect(merged.id).toBe("p1");
    expect(merged.name).toBe("Test");
  });

  it("creates the foundation anchor when project has none yet", () => {
    const current = makeProject({ anchors: undefined });
    const merged = applyOptimisticAnchorPatch(current, "foundation", {
      x: 50,
      y: 50,
    });
    expect(merged.anchors?.foundation).toMatchObject({
      x: 50,
      y: 50,
      width: 150,
      height: 150,
    });
  });

  it("leaves other tab's anchor untouched when patching foundation", () => {
    const current = makeProject({
      anchors: {
        foundation: {
          x: 0,
          y: 0,
          width: 150,
          height: 150,
          color: "#fef3c7",
          shape: "circle",
        },
        actors: {
          x: 500,
          y: 500,
          width: 200,
          height: 100,
          color: "#dbeafe",
          shape: "rounded",
        },
      },
    });
    const merged = applyOptimisticAnchorPatch(current, "foundation", { x: 99 });
    expect(merged.anchors?.foundation?.x).toBe(99);
    expect(merged.anchors?.actors?.x).toBe(500);
    expect(merged.anchors?.actors?.shape).toBe("rounded");
  });

  it("merges dimension changes (width/height) without losing position", () => {
    const current = makeProject();
    const merged = applyOptimisticAnchorPatch(current, "foundation", {
      width: 250,
      height: 250,
    });
    expect(merged.anchors?.foundation).toMatchObject({
      x: -75,
      y: -75,
      width: 250,
      height: 250,
    });
  });

  it("revert path — the captured ``previous`` doc is unchanged by merge", () => {
    const previous = makeProject();
    const merged = applyOptimisticAnchorPatch(previous, "foundation", { x: 999 });
    expect(merged.anchors?.foundation?.x).toBe(999);
    // previous is the reference the catch branch in App.tsx restores.
    expect(previous.anchors?.foundation?.x).toBe(-75);
  });

  it("resolveAnchorPlacement returns default for null/missing project", () => {
    expect(resolveAnchorPlacement(undefined, "foundation")).toEqual({
      x: -75,
      y: -75,
      width: 150,
      height: 150,
      color: "#fef3c7",
      shape: "circle",
    });
  });

  it("resolveAnchorPlacement returns the stored placement when present", () => {
    const proj = makeProject({
      anchors: {
        foundation: {
          x: 100,
          y: 200,
          width: 180,
          height: 120,
          color: "#abcdef",
          shape: "rectangle",
        },
      },
    });
    expect(resolveAnchorPlacement(proj, "foundation")).toEqual({
      x: 100,
      y: 200,
      width: 180,
      height: 120,
      color: "#abcdef",
      shape: "rectangle",
    });
  });
});
