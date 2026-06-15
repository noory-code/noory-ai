/**
 * ServiceDetail right-panel = Option 1 (D-2026-06-15-O).
 *
 *   ① detail tab default = the subject service's READ-ONLY inspector
 *      (cross-doc — read from the Services canvas; problem-centric).
 *   ② selecting a detail node → that node's editable inspector.
 *   ③ clicking empty space → back to the service (fallback).
 *
 * The seam: ``SketchInspectorBindings`` renders ``fallbackInspector`` in
 * place of the empty panel (its old ``return null``) when no node is
 * selected (or the selected node vanished). ``ServiceDetailInspectorHost``
 * builds the read-only service ``KindInspector`` from the Services canvas.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SketchInspectorBindings } from "../src/canvases/sketch/SketchInspectorBindings";
import { ServiceDetailInspectorHost } from "../src/canvases/inspectors/ServiceDetailInspectorHost";
import type { CanvasDoc, SketchNode } from "../src/types";

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
    notes_in_context: "",
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
  } as SketchNode;
}

function bindingsProps(over: Record<string, unknown> = {}) {
  const doc = {
    canvas_kind: "service_detail",
    service_ref: "svc-1",
    nodes: [] as SketchNode[],
    edges: [],
  } as unknown as CanvasDoc;
  return {
    doc,
    docRef: { current: doc },
    onDocChange: vi.fn(),
    inspectorNodeId: null,
    setInspectorNodeId: vi.fn(),
    updateNode: vi.fn(),
    handleNodesDelete: vi.fn(),
    addCompositionChild: vi.fn(),
    setPendingActorRef: vi.fn(),
    setPendingFoundationRef: vi.fn(),
    availableActors: [],
    availableMissions: [],
    availableValues: [],
    availableIdentities: [],
    projectPath: "/tmp/p",
    projectId: "pid",
    ...over,
  } as never;
}

describe("SketchInspectorBindings fallbackInspector (D-2026-06-15-O)", () => {
  it("renders the fallback when no node is selected", () => {
    render(
      <SketchInspectorBindings
        {...bindingsProps({ fallbackInspector: <div data-testid="fb">FB</div> })}
      />,
    );
    expect(screen.getByTestId("fb")).toBeInTheDocument();
  });

  it("renders the selected node's inspector — NOT the fallback", () => {
    const node = makeNode({ kind: "metric", id: "m1", label: "Latency" });
    const doc = {
      canvas_kind: "service_detail",
      service_ref: "svc-1",
      nodes: [node],
      edges: [],
    } as unknown as CanvasDoc;
    render(
      <SketchInspectorBindings
        {...bindingsProps({
          doc,
          docRef: { current: doc },
          inspectorNodeId: "m1",
          fallbackInspector: <div data-testid="fb">FB</div>,
        })}
      />,
    );
    expect(screen.getByDisplayValue("Latency")).toBeInTheDocument();
    expect(screen.queryByTestId("fb")).not.toBeInTheDocument();
  });

  it("falls back when the selected node has vanished (deleted)", () => {
    render(
      <SketchInspectorBindings
        {...bindingsProps({
          inspectorNodeId: "ghost",
          fallbackInspector: <div data-testid="fb">FB</div>,
        })}
      />,
    );
    expect(screen.getByTestId("fb")).toBeInTheDocument();
  });
});

describe("ServiceDetailInspectorHost (D-2026-06-15-O)", () => {
  const svc = makeNode({
    kind: "service",
    id: "svc-1",
    label: "Sign-up",
    problem: "가입이 너무 번거롭다",
    what: "신규 가입",
  });
  const servicesCanvas = {
    canvas_kind: "services",
    nodes: [svc],
    edges: [],
  } as unknown as CanvasDoc;

  it("renders the subject service read-only (label not editable, problem shown, no edit controls)", () => {
    render(
      <ServiceDetailInspectorHost
        serviceId="svc-1"
        servicesCanvas={servicesCanvas}
        projectPath="/tmp/p"
        projectId="pid"
      />,
    );
    // Label present but read-only.
    const label = screen.getByDisplayValue("Sign-up");
    expect(label).toHaveAttribute("readonly");
    // problem-centric content rendered (read-only display).
    expect(screen.getByText("가입이 너무 번거롭다")).toBeInTheDocument();
    // No editing affordances: the editable body's <select> is gone.
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
  });

  it("renders nothing when the service is missing (deleted / unknown id)", () => {
    const { container } = render(
      <ServiceDetailInspectorHost
        serviceId="ghost"
        servicesCanvas={servicesCanvas}
        projectPath="/tmp/p"
        projectId="pid"
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});
