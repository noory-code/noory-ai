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
    const node = makeNode({ id: "x1", kind: "category" });
    const { container } = render(<KindInspector {...makeProps(node, "services")} />);
    expect(container.firstChild).toBeNull();
  });
});

describe("StepInspector (Phase 2.2)", () => {
  it("renders with shared chrome + ordered step typed fields", () => {
    const node = makeNode({
      id: "s1",
      kind: "step",
      label: "Sign in",
      order: 1,
      outcome: "session token",
    });
    render(<KindInspector {...makeProps(node)} />);
    expect(screen.getByDisplayValue("Sign in")).toBeInTheDocument();
    expect(screen.getByDisplayValue("1")).toBeInTheDocument();
    expect(screen.getByDisplayValue("session token")).toBeInTheDocument();
  });

  it("renders an unordered step (order=null) without firing console.error", () => {
    const node = makeNode({ id: "s1", kind: "step", label: "Either path" });
    render(<KindInspector {...makeProps(node)} />);
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });
});

describe("CoreValueInspector (Phase 2.3)", () => {
  it("renders with shared chrome + definition + do/dont", () => {
    const node = makeNode({
      id: "cv1",
      kind: "core_value",
      label: "관용",
      definition: "다름을 인정하고 받아들임",
      do: "다른 의견을 먼저 듣는다",
      dont: "비난부터 한다",
    });
    render(<KindInspector {...makeProps(node, "foundation")} />);
    expect(screen.getByDisplayValue("관용")).toBeInTheDocument();
    expect(screen.getByDisplayValue("다름을 인정하고 받아들임")).toBeInTheDocument();
    expect(screen.getByDisplayValue("다른 의견을 먼저 듣는다")).toBeInTheDocument();
    expect(screen.getByDisplayValue("비난부터 한다")).toBeInTheDocument();
  });

  it("renders empty defaults without firing console.error", () => {
    const node = makeNode({ id: "cv1", kind: "core_value", label: "Empty" });
    render(<KindInspector {...makeProps(node, "foundation")} />);
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });
});

describe("IdentityInspector (Phase 2.3)", () => {
  it("renders with shared chrome + description + do/dont", () => {
    const node = makeNode({
      id: "id1",
      kind: "identity",
      label: "Voice",
      description: "따뜻하고 진솔하게",
      do: "이름을 부른다",
      dont: "공지글 같은 말투로 쓴다",
    });
    render(<KindInspector {...makeProps(node, "foundation")} />);
    expect(screen.getByDisplayValue("Voice")).toBeInTheDocument();
    expect(screen.getByDisplayValue("따뜻하고 진솔하게")).toBeInTheDocument();
  });
});
