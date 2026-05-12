/**
 * Per-kind inspector smoke tests.
 *
 * One test per kind that has been migrated out of the legacy
 * ``SketchInspector`` (Phase 2.1+ vertical slice). Each test:
 *
 *   - Renders ``KindInspector`` with a synthetic node of the kind.
 *   - Asserts that the per-kind body renders.
 *   - Asserts that the shared chrome (label input, kind tag) renders.
 *   - Asserts no ``console.error`` fires during render.
 *
 * The tests grow incrementally as Phase 2.X commits add kinds.
 * Phase 2.10 closes the loop with a "registry size === 15" assertion.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { KindInspector } from "../../src/canvases/inspectors/KindInspector";
import type { CanvasKind, SketchNode } from "../../src/types";

interface MakeNodeOverrides extends Partial<SketchNode> {
  kind: SketchNode["kind"];
}

function makeNode(overrides: MakeNodeOverrides): SketchNode {
  return {
    id: "n1",
    label: "Test",
    x: 0,
    y: 0,
    width: 180,
    height: 80,
    color: "#ffffff",
    shape: "rounded",
    icon: null,
    parent_id: null,
    collapsed: false,
    is_root: false,
    mission: "",
    core_values: "",
    identity: "",
    ref_actor_id: null,
    ref_mission_id: null,
    ref_value_id: null,
    ref_identity_id: null,
    what_we_do: "",
    why: "",
    direction: "",
    definition: "",
    description: "",
    do: "",
    dont: "",
    target_side: null,
    theme: "",
    what: "",
    value_created: "",
    scope: "",
    trigger: "",
    how: "",
    outcome: "",
    target: "",
    measurement: "",
    order: null,
    motivation: "",
    pain: "",
    gives: "",
    receives: "",
    side: null,
    policy: "",
    enforcement: "",
    actor_permissions: {},
    format: "",
    producer_actor_id: null,
    consumer_actor_id: null,
    details_path: null,
    ...overrides,
  };
}

function makeProps(node: SketchNode, canvasKind: CanvasKind = "service_detail") {
  return {
    node,
    onPatchNode: vi.fn(),
    onDeleteNode: vi.fn(),
    onClose: vi.fn(),
    projectPath: "/tmp/plot-test",
    projectId: "test-project",
    canvasKind,
  };
}

let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

beforeEach(() => {
  consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
});

afterEach(() => {
  consoleErrorSpy.mockRestore();
});

describe("MetricInspector (Phase 2.1)", () => {
  it("renders with shared chrome + metric typed fields", () => {
    const node = makeNode({
      id: "m1",
      kind: "metric",
      label: "Latency",
      target: ">99% under 200ms",
      measurement: "p95 from server timing-API",
    });
    render(<KindInspector {...makeProps(node)} />);

    // Shared chrome — label input populated from node.label
    const labelInput = screen.getByDisplayValue("Latency");
    expect(labelInput).toBeInTheDocument();

    // Metric typed fields — target + measurement values rendered
    expect(screen.getByDisplayValue(">99% under 200ms")).toBeInTheDocument();
    expect(screen.getByDisplayValue("p95 from server timing-API")).toBeInTheDocument();
  });

  it("renders without firing console.error", () => {
    const node = makeNode({ id: "m1", kind: "metric" });
    render(<KindInspector {...makeProps(node)} />);
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it("returns null for unmigrated kinds (KindInspector contract)", () => {
    const node = makeNode({ id: "a1", kind: "actor" });
    const { container } = render(<KindInspector {...makeProps(node, "actors")} />);
    expect(container.firstChild).toBeNull();
  });
});
