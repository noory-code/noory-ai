// Regression tests pinning behaviour the v0.13.2 session bugs flipped.
// Each test corresponds to a SPEC.md invariant the assistant is allowed
// to refactor against, but never re-violate. See plan
// /Users/woogis/.claude/plans/wiggly-herding-pixel.md Pre-Step 0c.
import { fireEvent, render } from "@testing-library/react";
import { ReactFlowProvider } from "reactflow";
import { describe, expect, it } from "vitest";
import { SketchCanvas } from "../src/canvases/SketchCanvas";
import type {
  AnchorPlacement,
  CanvasDoc,
  CanvasKind,
  SketchNode,
} from "../src/types";

// Default-everything node helper. Plot's node type carries dozens of
// per-kind typed fields; tests only set what they're asserting on.
function makeNode(overrides: Partial<SketchNode> & Pick<SketchNode, "id" | "label">): SketchNode {
  return {
    label: overrides.label,
    id: overrides.id,
    x: 0,
    y: 0,
    width: 200,
    height: 90,
    color: "#fef3c7",
    shape: "rounded",
    icon: null,
    kind: null,
    parent_id: null,
    collapsed: false,
    is_root: false,
    mission: "",
    core_values: "",
    identity: "",
    what_we_do: "",
    why: "",
    direction: "",
    definition: "",
    description: "",
    do: "",
    dont: "",
    what: "",
    value_created: "",
    scope: "",
    trigger: "",
    how: "",
    outcome: "",
    target: "",
    measurement: "",
    order: null,
    policy: "",
    enforcement: "",
    actor_permissions: {},
    format: "",
    producer_actor_id: null,
    consumer_actor_id: null,
    motivation: "",
    pain: "",
    side: null,
    gives: "",
    receives: "",
    target_side: null,
    theme: "",
    ref_actor_id: null,
    ref_mission_id: null,
    ref_value_id: null,
    ref_identity_id: null,
    ...overrides,
  };
}

function makeCanvas(
  kind: CanvasKind,
  nodes: SketchNode[] = [],
  edges: CanvasDoc["edges"] = [],
): CanvasDoc {
  return {
    canvas_id: kind === "foundation" ? "foundation" : kind === "actors" ? "actors" : "services",
    canvas_kind: kind,
    service_ref: null,
    nodes,
    edges,
  };
}

const ANCHOR: AnchorPlacement = {
  x: 0,
  y: 0,
  width: 160,
  height: 160,
  color: "#fef3c7",
  shape: "circle",
};

function mount(doc: CanvasDoc, anchor: AnchorPlacement | null = ANCHOR) {
  return render(
    <ReactFlowProvider>
      <SketchCanvas
        doc={doc}
        onDocChange={() => {}}
        onUndo={() => {}}
        onRedo={() => {}}
        canUndo={false}
        canRedo={false}
        projectPath="/tmp/plot-test"
        projectId="test-project"
        projectAnchor={anchor}
        projectName="Test Project"
        onAnchorChange={() => {}}
      />
    </ReactFlowProvider>,
  );
}

describe("SketchCanvas regression — pin v0.13.2 reverts", () => {
  it("Foundation: no auto-edges between anchor and children when doc.edges is empty", () => {
    // D-2026-05-04-A — every line on the canvas is user-drawn.
    // Reproduces the auto-edge bug: 3 typed-text children + an anchor
    // used to render 3 synthetic dashed edges. SPEC §Edges now requires
    // 0.
    const doc = makeCanvas("foundation", [
      makeNode({ id: "mission", label: "Mission", kind: "mission" }),
      makeNode({ id: "cv1", label: "CV", kind: "core_value", x: 250 }),
      makeNode({ id: "id1", label: "Identity", kind: "identity", x: 500 }),
    ]);
    const { container } = mount(doc);
    expect(container.querySelectorAll(".react-flow__edge")).toHaveLength(0);
  });

  it("Foundation: anchor renders the four React Flow handles", () => {
    // D-2026-05-04-B — anchor is drawable from / connectable to like any
    // node. Reproduces the anchor-handle-suppression bug.
    const doc = makeCanvas("foundation");
    const { container } = mount(doc);
    const anchor = container.querySelector('[data-id="__project_anchor__"]');
    expect(anchor).toBeTruthy();
    // SketchNode renders Top / Left / Right / Bottom handles. Each is
    // a div.react-flow__handle. The anchor inherits them.
    const handles = anchor!.querySelectorAll(".react-flow__handle");
    expect(handles.length).toBe(4);
  });

  it("toolbar renders an 'Auto layout' button (enabled when anchor + at least one node)", () => {
    // D-2026-05-10-E — auto-layout restored as mindmap directional
    // tree. Button is enabled when an anchor exists on the canvas
    // and at least one non-anchor node is present.
    const doc = makeCanvas("foundation", [
      makeNode({ id: "mission", label: "Mission", kind: "mission" }),
    ]);
    const { queryByRole } = mount(doc);
    const btn = queryByRole("button", { name: /auto layout/i });
    expect(btn).not.toBeNull();
    expect(btn!.getAttribute("disabled")).toBeNull();
  });

  it("Inspector aside appears after a node click", () => {
    // SPEC §Inspector — clicking a non-anchor node opens the right
    // panel. Pinned so future refactors don't accidentally swallow the
    // click handler.
    const doc = makeCanvas("foundation", [
      makeNode({ id: "mission", label: "Mission", kind: "mission" }),
    ]);
    const { container } = mount(doc);
    // Pre-click: no Inspector aside.
    expect(container.querySelector("aside.right-0")).toBeNull();
    const node = container.querySelector('[data-id="mission"]');
    expect(node).toBeTruthy();
    fireEvent.click(node!);
    // Post-click: Inspector aside present (positioned absolute right-0).
    expect(container.querySelector("aside.right-0")).toBeTruthy();
  });
});
