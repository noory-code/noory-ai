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
  };
}

function makeProps(
  node: SketchNode,
  canvasKind: CanvasKind = "service_detail",
  allNodes: SketchNode[] = [node],
  allEdges: import("../../src/types").SketchEdge[] = [],
) {
  return {
    node,
    allNodes,
    allEdges,
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

describe("MissionInspector (Phase 2.4)", () => {
  it("renders with shared chrome + statement (v0.43.0)", () => {
    const node = makeNode({
      id: "m1",
      kind: "mission",
      label: "M",
      statement: "누구나 히어로가 되는 일상을 만든다",
    });
    render(<KindInspector {...makeProps(node, "foundation")} />);
    expect(screen.getByDisplayValue("M")).toBeInTheDocument();
    expect(screen.getByDisplayValue("누구나 히어로가 되는 일상을 만든다")).toBeInTheDocument();
  });
});

describe("ProjectInspector (Phase 2.5)", () => {
  it("renders BaseInspector chrome only (no per-kind body)", () => {
    const node = makeNode({ id: "project", kind: "project", label: "Plot" });
    render(<KindInspector {...makeProps(node, "foundation")} />);
    expect(screen.getByDisplayValue("Plot")).toBeInTheDocument();
  });
});

describe("ActorRefInspector (Phase 2.7)", () => {
  it("renders gives/receives + reference display when actor master exists", () => {
    const actor = makeNode({ id: "operator", kind: "actor", label: "Operator", side: "operator" });
    const ref = makeNode({
      id: "ref-1",
      kind: "actor_ref",
      label: "→ Op",
      ref_actor_id: "operator",
      gives: "mod",
      receives: "rep",
    });
    render(
      <KindInspector
        {...makeProps(ref, "service_detail", [ref, actor])}
        availableActors={[actor]}
      />,
    );
    expect(screen.getByDisplayValue("mod")).toBeInTheDocument();
    expect(screen.getByText(/Operator/)).toBeInTheDocument();
  });

  it("renders the orphan warning when ref_actor_id is unknown", () => {
    const ref = makeNode({
      id: "ref-1",
      kind: "actor_ref",
      label: "→ ?",
      ref_actor_id: "ghost",
    });
    render(
      <KindInspector {...makeProps(ref, "service_detail", [ref])} availableActors={[]} />,
    );
    expect(screen.getByText(/Orphan/i)).toBeInTheDocument();
  });
});

describe("Foundation ref inspectors (Phase 2.7)", () => {
  it("MissionRefInspector renders the master label when present", () => {
    const master = makeNode({ id: "m1", kind: "mission", label: "Plot 미션" });
    const ref = makeNode({
      id: "mref-1",
      kind: "mission_ref",
      label: "Plot 미션 참조",
      ref_mission_id: "m1",
    });
    render(
      <KindInspector
        {...makeProps(ref, "service_detail", [ref])}
        availableMissions={[master]}
      />,
    );
    expect(screen.getByText(/Plot 미션/)).toBeInTheDocument();
  });

  it("ValueRefInspector renders master-not-found when orphan", () => {
    const ref = makeNode({ id: "vref-1", kind: "value_ref", label: "?", ref_value_id: "ghost" });
    render(
      <KindInspector {...makeProps(ref, "service_detail", [ref])} availableValues={[]} />,
    );
    // i18n key inspector.masterNotFound — check by class on red rose text
    expect(screen.getByText(/id: ghost/)).toBeInTheDocument();
  });

  it("IdentityRefInspector renders without firing console.error", () => {
    const ref = makeNode({
      id: "iref-1",
      kind: "identity_ref",
      label: "Voice ref",
      ref_identity_id: "i1",
    });
    render(
      <KindInspector {...makeProps(ref, "service_detail", [ref])} availableIdentities={[]} />,
    );
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });
});

describe("ServiceInspector (Phase 2.9)", () => {
  it("renders Service typed fields + composition lists", () => {
    const svc = makeNode({
      id: "svc-1",
      kind: "service",
      label: "Sign-up",
      target_side: "user",
      what: "신규 가입",
      value_created: "access",
    });
    const rule = makeNode({
      id: "r1",
      kind: "rule",
      label: "GDPR",
      policy: "explicit consent",
    });
    // v0.26.0 (D-2026-05-25-A) — composition is now a directed edge.
    const compositionEdge = {
      id: "e-svc-r1",
      source: "svc-1",
      target: "r1",
      sourceHandle: null,
      targetHandle: null,
      label: "",
      style: "solid" as const,
      directed: true,
      action_verb: null,
      value_form: [],
    };
    render(
      <KindInspector
        {...makeProps(svc, "service_detail", [svc, rule], [compositionEdge])}
        onAddChild={vi.fn()}
        onPatchChild={vi.fn()}
        onRemoveChild={vi.fn()}
      />,
    );
    expect(screen.getByDisplayValue("Sign-up")).toBeInTheDocument();
    expect(screen.getByDisplayValue("신규 가입")).toBeInTheDocument();
    expect(screen.getByDisplayValue("access")).toBeInTheDocument();
    // Rule child label shows in the rules CompositionList
    expect(screen.getByDisplayValue("GDPR")).toBeInTheDocument();
  });

  it("hides composition lists when child callbacks are unset", () => {
    const svc = makeNode({ id: "svc-1", kind: "service", label: "Bare" });
    render(<KindInspector {...makeProps(svc, "service_detail", [svc])} />);
    // No "Add" button when callbacks aren't wired
    expect(screen.queryByText(/composition\.add/i)).not.toBeInTheDocument();
  });
});

describe("RuleInspector + ContentInspector (Phase 2.9)", () => {
  it("RuleInspector renders policy + enforcement + permissions", () => {
    const r = makeNode({
      id: "r1",
      kind: "rule",
      label: "Rule 1",
      policy: "consent",
      enforcement: "checkbox",
    });
    render(<KindInspector {...makeProps(r, "service_detail")} />);
    expect(screen.getByDisplayValue("consent")).toBeInTheDocument();
    expect(screen.getByDisplayValue("checkbox")).toBeInTheDocument();
  });

  it("ContentInspector renders format + producer/consumer pickers", () => {
    const c = makeNode({
      id: "c1",
      kind: "content",
      label: "Receipt",
      format: "application/json",
    });
    render(<KindInspector {...makeProps(c, "service_detail")} />);
    expect(screen.getByDisplayValue("application/json")).toBeInTheDocument();
  });
});

describe("ActorInspector (Phase 2.8)", () => {
  it("renders side select + motivation + pain", () => {
    const node = makeNode({
      id: "a1",
      kind: "actor",
      label: "User",
      side: "user",
      motivation: "수다",
      pain: "외로움",
    });
    render(<KindInspector {...makeProps(node, "actors")} />);
    expect(screen.getByDisplayValue("User")).toBeInTheDocument();
    expect(screen.getByDisplayValue("수다")).toBeInTheDocument();
    expect(screen.getByDisplayValue("외로움")).toBeInTheDocument();
  });

  // v0.24.11 (D-2026-05-19-D) — ActorCompositionPlaceholder removed.
  // The placeholder was a vague "v0.3 coming soon" notice gated on
  // actor.is_root, which itself was deprecated. Tests for that
  // placeholder removed alongside.
});

describe("CategoryInspector (Phase 2.6)", () => {
  it("renders chrome + theme + does NOT show empty-warning when child services exist", () => {
    const cat = makeNode({ id: "cat-1", kind: "category", label: "Admin", theme: "ops" });
    const child = makeNode({ id: "svc-1", kind: "service", label: "Manage" });
    // v0.26.0 (D-2026-05-25-A) — child is now expressed via a directed edge.
    const edge = {
      id: "e-cat-svc",
      source: "cat-1",
      target: "svc-1",
      sourceHandle: null,
      targetHandle: null,
      label: "",
      style: "solid" as const,
      directed: true,
      action_verb: null,
      value_form: [],
    };
    render(<KindInspector {...makeProps(cat, "services", [cat, child], [edge])} />);
    expect(screen.getByDisplayValue("ops")).toBeInTheDocument();
    expect(screen.queryByText(/이 카테고리에 service/)).not.toBeInTheDocument();
  });

  it("shows the empty-warning when childCount === 0", () => {
    const cat = makeNode({ id: "cat-1", kind: "category", label: "Empty" });
    render(<KindInspector {...makeProps(cat, "services", [cat])} />);
    expect(screen.getByText(/이 카테고리에 service/)).toBeInTheDocument();
  });
});
