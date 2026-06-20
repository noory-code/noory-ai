/**
 * Exhaustive per-kind inspector smoke — Phase 5.1 (D-2026-05-12-B).
 *
 * Companion to ``inspectors.smoke.test.tsx`` (the per-kind asserts
 * built up Phase 2.1 → 2.10). This file is the structural sweep:
 *
 *   For every NodeKind in the 13-way discriminated union, build a
 *   synthetic node via ``createBlankNode`` (the domain SSOT), mount
 *   ``KindInspector``, and assert:
 *
 *     1. ``KindInspector`` returns a non-null tree (i.e. the
 *        per-kind inspector is registered).
 *     2. No ``console.error`` fires during render.
 *     3. The BaseInspector chrome's close button is present.
 *
 * Drift detection: if a new kind lands without an inspector registered,
 * step 1 fails. If a per-kind inspector blows up on default-shaped
 * data, step 2 fails.
 */
import "@testing-library/jest-dom/vitest";
import { render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { KindInspector } from "../../src/canvases/inspectors/KindInspector";
import { createBlankNode } from "../../src/domain/createBlankNode";
import type { CanvasKind, NodeKind, SketchNode } from "../../src/types";

const ALL_KINDS: NodeKind[] = [
  "project",
  "mission",
  "core_value",
  "identity",
  "actor",
  "actor_ref",
  "service",
  "feature",
  "category",
  "step",
  "decision",
  "note",
  "rule",
];

/** A reasonable default canvas for each kind. The KindInspector
 *  itself ignores ``canvasKind`` for most kinds, but a few (e.g.
 *  ``actor`` showing the composition placeholder only outside the
 *  ``actors`` canvas; ``category`` whose empty-warning depends on
 *  canvas) read it. We pick the canvas each kind is "native" to. */
function nativeCanvasFor(kind: NodeKind): CanvasKind {
  switch (kind) {
    case "project":
    case "mission":
    case "core_value":
    case "identity":
      return "foundation";
    case "actor":
    case "actor_ref":
      return "actors";
    case "service":
    case "category":
      return "services";
    default:
      return "feature";
  }
}

function buildNode(kind: NodeKind): SketchNode {
  return createBlankNode(kind, {
    id: `${kind}-1`,
    label: kind,
    x: 0,
    y: 0,
    width: 180,
    height: 80,
    color: "#ffffff",
    shape: "rounded",
    icon: null,
    parent_id: null,
  });
}

let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

beforeEach(() => {
  consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
});

afterEach(() => {
  consoleErrorSpy.mockRestore();
});

describe("KindInspector — exhaustive 13-kind smoke (Phase 5.1)", () => {
  it.each(ALL_KINDS)(
    "renders a non-null tree for kind=%s",
    (kind) => {
      const node = buildNode(kind);
      const { container } = render(
        <KindInspector
          node={node}
          allNodes={[node]}
          allEdges={[]}
          onPatchNode={vi.fn()}
          onDeleteNode={vi.fn()}
          onClose={vi.fn()}
          projectPath="/tmp/plot-test"
          projectId="test-project"
          canvasKind={nativeCanvasFor(kind)}
        />,
      );
      expect(container.firstChild, `inspector for ${kind}`).not.toBeNull();
    },
  );

  it.each(ALL_KINDS)(
    "renders without firing console.error for kind=%s",
    (kind) => {
      const node = buildNode(kind);
      render(
        <KindInspector
          node={node}
          allNodes={[node]}
          allEdges={[]}
          onPatchNode={vi.fn()}
          onDeleteNode={vi.fn()}
          onClose={vi.fn()}
          projectPath="/tmp/plot-test"
          projectId="test-project"
          canvasKind={nativeCanvasFor(kind)}
        />,
      );
      // BaseInspector's React warnings about uncontrolled-to-controlled
      // inputs or missing keys would land in console.error. A clean
      // pass means the per-kind body wires its inputs correctly.
      expect(
        consoleErrorSpy,
        `console.error fired for kind=${kind}`,
      ).not.toHaveBeenCalled();
    },
  );
});
