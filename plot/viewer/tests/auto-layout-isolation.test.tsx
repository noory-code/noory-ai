/**
 * v0.16.36 — Auto-layout isolation regression (D-2026-05-13-L).
 * v0.24.5 — Actor opt-in (D-2026-05-18-B).
 * v0.25.0 — ServiceDetail opt-in with radial algorithm
 *           (D-2026-05-24-B). ``enableAutoLayout`` boolean generalised
 *           to ``layoutAlgo: "tree" | "radial" | null``. ServicesCanvas
 *           briefly opted in too, then reverted same-day by
 *           D-2026-05-24-C — controls belong inside the per-service
 *           modal, not on the summary canvas.
 * v0.26.2 — ServicesCanvas opts back into ``"radial"`` (D-2026-05-25-C
 *           reverts D-2026-05-24-C). User direction was "서비스 메인
 *           캔버스에 정렬기능 빠져있는건 여전하고".
 * v0.27.0 — Services + ServiceDetail switch from ``"radial"`` to
 *           ``"tree"`` (D-2026-05-26-A). User direction *"정렬은 액터
 *           캔버스 참고하쇼"*. The tree algorithm follows user-drawn
 *           edge handle direction (T/R/B/L) and never collapses
 *           length-1 spoke chains onto a single line the way radial
 *           did. ``useAutoLayout`` hub selection extended to fall
 *           back to the root-service node when ``projectAnchor`` is
 *           null (mirrors ``useRadialLayout.pickHub``).
 *
 * Pins the 4-layer isolation contract for the auto-layout feature:
 *
 *   1. Wrapper opt-in only — wrappers that opt in pass their
 *      ``layoutAlgo``: Foundation / Actors → ``"tree"``;
 *      Services / ServiceDetail → ``"radial"``. SketchCanvas itself
 *      has no default — without a wrapper, no button.
 *   2. Conditional render — when ``layoutAlgo`` is null / undefined
 *      the auto-layout button is not in the DOM.
 *   3. Triggering the button mutates ``doc.nodes`` via the regular
 *      ``onDocChange`` path (one-shot apply; Cmd+Z undoes it). No
 *      hidden side effects on edges / anchor / other state.
 *   4. The trigger touches *positions only* — kind / label / parent_id
 *      / typed-text fields stay byte-identical, regardless of which
 *      algorithm the wrapper opted into.
 *
 * Layer 3 ("one-shot apply + Cmd+Z" — chose over the plan's
 * "preview/apply" pattern, see D-2026-05-13-L body): the explicit
 * user-consent guarantee comes from the button click itself, with
 * the regular undo stack as the safety net. Cheaper than a separate
 * preview state machine; equivalent isolation surface.
 */
import { fireEvent, render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActorsCanvas } from "../src/canvases/ActorsCanvas";
import { FoundationCanvas } from "../src/canvases/FoundationCanvas";
import { ServiceDetailCanvas } from "../src/canvases/ServiceDetailCanvas";
import { ServicesCanvas } from "../src/canvases/ServicesCanvas";
import type {
  AnchorPlacement,
  CanvasDoc,
  CanvasKind,
  SketchNode,
} from "../src/types";

function makeNode(
  overrides: Partial<SketchNode> & Pick<SketchNode, "id" | "label">,
): SketchNode {
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
    ref_actor_id: null,
    ref_mission_id: null,
    ref_value_id: null,
    ref_identity_id: null,
    details_path: null,
    owner: null,
    is_anchor: false,
    is_root_service: false,
    ...overrides,
  } as SketchNode;
}

function makeCanvas(kind: CanvasKind, nodes: SketchNode[]): CanvasDoc {
  return {
    canvas_id: kind,
    canvas_kind: kind,
    service_ref: kind === "service_detail" ? "svc-1" : null,
    nodes,
    edges: [],
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

function commonProps(doc: CanvasDoc, onDocChange: (d: CanvasDoc) => void) {
  return {
    doc,
    onDocChange,
    onUndo: () => {},
    onRedo: () => {},
    canUndo: false,
    canRedo: false,
    projectPath: "/tmp/test",
    projectId: "pj",
    projectAnchor: ANCHOR,
    projectName: "Test",
    onAnchorChange: () => {},
  };
}

describe("auto-layout isolation (D-2026-05-13-L)", () => {
  it("FoundationCanvas wrapper renders the Auto-layout button", () => {
    const doc = makeCanvas("foundation", [
      makeNode({ id: "m", label: "Mission", kind: "mission" }),
    ]);
    const { queryByRole } = render(
      <FoundationCanvas {...commonProps(doc, () => {})} />,
    );
    expect(
      queryByRole("button", { name: /layout/i }),
      "FoundationCanvas must opt into the auto-layout button.",
    ).not.toBeNull();
  });

  it("ActorsCanvas wrapper renders the Auto-layout button (D-2026-05-18-B)", () => {
    const doc = makeCanvas("actors", [
      makeNode({ id: "a", label: "Actor", kind: "actor" }),
    ]);
    const { queryByRole } = render(
      <ActorsCanvas {...commonProps(doc, () => {})} />,
    );
    expect(
      queryByRole("button", { name: /layout/i }),
      "ActorsCanvas opts into the auto-layout button per D-2026-05-18-B.",
    ).not.toBeNull();
  });

  it("ServicesCanvas wrapper renders the Auto-layout button (D-2026-05-26-A, tree)", () => {
    const doc = makeCanvas("services", [
      makeNode({ id: "s", label: "Service", kind: "service" }),
    ]);
    const { queryByRole } = render(
      <ServicesCanvas {...commonProps(doc, () => {})} />,
    );
    expect(
      queryByRole("button", { name: /layout/i }),
      "ServicesCanvas opts into the tree auto-layout button per D-2026-05-26-A (switched from radial after the v0.26.3 fan-out fix still collapsed length-1 chains).",
    ).not.toBeNull();
  });

  it("ServiceDetailCanvas wrapper renders the Auto-layout button (D-2026-05-26-A, tree)", () => {
    const doc = makeCanvas("service_detail", [
      makeNode({
        id: "svc-1",
        label: "Service Root",
        kind: "service",
        is_root: true,
      }),
    ]);
    const { queryByRole } = render(
      <ServiceDetailCanvas {...commonProps(doc, () => {})} />,
    );
    expect(
      queryByRole("button", { name: /layout/i }),
      "ServiceDetailCanvas opts into the tree auto-layout button per D-2026-05-26-A (switched from radial; root-service node serves as the BFS root via useAutoLayout's pickAnchor fallback).",
    ).not.toBeNull();
  });

  it("ServicesCanvas: Auto-layout touches positions only, not kind/label/typed-text (D-2026-05-26-A, tree)", () => {
    const original = makeNode({
      id: "s1",
      label: "Login",
      kind: "service",
      x: 50,
      y: 50,
      what: "log in",
      why: "auth",
    });
    const doc = makeCanvas("services", [
      original,
      makeNode({ id: "s2", label: "Logout", kind: "service", x: 200, y: 200 }),
    ]);
    let last: CanvasDoc | null = null;
    const { getByRole } = render(
      <ServicesCanvas
        {...commonProps(doc, (d) => {
          last = d;
        })}
      />,
    );
    fireEvent.click(getByRole("button", { name: /layout/i }));
    expect(last).not.toBeNull();
    const after = (last as unknown as CanvasDoc).nodes.find((n) => n.id === "s1");
    expect(after, "node 's1' must survive tree auto-layout").toBeTruthy();
    if (!after) return;
    expect(after.kind).toBe(original.kind);
    expect(after.label).toBe(original.label);
    expect((after as unknown as Record<string, unknown>).what).toBe("log in");
    expect((after as unknown as Record<string, unknown>).why).toBe("auth");
  });

  it("ServiceDetailCanvas: Auto-layout touches positions only (D-2026-05-26-A, tree, hidden root-service as BFS root)", () => {
    // ServiceDetail injects no anchor; the hub is the (hidden)
    // root-service. Add one ring-1 spoke so the algorithm has work to do.
    const original = makeNode({
      id: "step-1",
      label: "Step 1",
      kind: "step",
      x: 50,
      y: 50,
      how: "do thing",
      outcome: "thing-done",
    });
    const doc = makeCanvas("service_detail", [
      makeNode({
        id: "svc-1",
        label: "Login",
        kind: "service",
        is_root: true,
        x: 0,
        y: 0,
      }),
      original,
    ]);
    doc.edges = [
      {
        id: "e-svc-step",
        source: "svc-1",
        target: "step-1",
        sourceHandle: null,
        targetHandle: null,
        label: "",
        style: "solid",
        action_verb: null,
        value_form: [],
      },
    ];
    let last: CanvasDoc | null = null;
    const props = commonProps(doc, (d) => {
      last = d;
    });
    // ServiceDetail wrapper passes injectAnchor=false — clear projectAnchor
    // so useAutoLayout's pickAnchor falls back to the root-service node
    // (same hub-selection shape as useRadialLayout.pickHub).
    const { getByRole } = render(
      <ServiceDetailCanvas {...props} projectAnchor={null} />,
    );
    fireEvent.click(getByRole("button", { name: /layout/i }));
    expect(last).not.toBeNull();
    const after = (last as unknown as CanvasDoc).nodes.find(
      (n) => n.id === "step-1",
    );
    expect(after, "node 'step-1' must survive tree auto-layout").toBeTruthy();
    if (!after) return;
    expect(after.kind).toBe(original.kind);
    expect(after.label).toBe(original.label);
    expect((after as unknown as Record<string, unknown>).how).toBe("do thing");
    expect((after as unknown as Record<string, unknown>).outcome).toBe("thing-done");
  });

  it("FoundationCanvas: clicking Auto-layout calls onDocChange exactly once", () => {
    const doc = makeCanvas("foundation", [
      makeNode({ id: "m", label: "Mission", kind: "mission", x: 100, y: 100 }),
      makeNode({ id: "c", label: "Core", kind: "core_value", x: 200, y: 200 }),
    ]);
    const calls: CanvasDoc[] = [];
    const { getByRole } = render(
      <FoundationCanvas
        {...commonProps(doc, (d) => {
          calls.push(d);
        })}
      />,
    );
    const button = getByRole("button", { name: /layout/i });
    fireEvent.click(button);
    expect(
      calls.length,
      "Auto-layout button must call onDocChange exactly once " +
        "(one-shot apply + Cmd+Z is the user-consent contract).",
    ).toBe(1);
  });

  it("ActorsCanvas: Auto-layout touches positions only, not kind/label/typed-text (D-2026-05-18-B)", () => {
    const original = makeNode({
      id: "h",
      label: "Hero",
      kind: "actor",
      x: 100,
      y: 100,
      motivation: "find-heroes",
      pain: "discovery-friction",
      side: "operator",
    });
    const doc = makeCanvas("actors", [
      original,
      makeNode({ id: "f", label: "Fan", kind: "actor", x: 200, y: 200 }),
    ]);
    let last: CanvasDoc | null = null;
    const { getByRole } = render(
      <ActorsCanvas
        {...commonProps(doc, (d) => {
          last = d;
        })}
      />,
    );
    fireEvent.click(getByRole("button", { name: /layout/i }));
    expect(last).not.toBeNull();
    const after = (last as unknown as CanvasDoc).nodes.find(
      (n) => n.id === "h",
    );
    expect(after, "node 'h' must survive auto-layout").toBeTruthy();
    if (!after) return;
    expect(after.kind).toBe(original.kind);
    expect(after.label).toBe(original.label);
    expect(after.parent_id).toBe(original.parent_id);
    expect(
      (after as unknown as Record<string, unknown>).motivation,
    ).toBe("find-heroes");
    expect((after as unknown as Record<string, unknown>).pain).toBe(
      "discovery-friction",
    );
    expect((after as unknown as Record<string, unknown>).side).toBe(
      "operator",
    );
  });

  it("FoundationCanvas: Auto-layout touches positions only, not kind/label/typed-text", () => {
    const original = makeNode({
      id: "m",
      label: "Mission",
      kind: "mission",
      x: 100,
      y: 100,
      what_we_do: "doing-things",
      why: "the-why",
      direction: "north",
    });
    const doc = makeCanvas("foundation", [
      original,
      makeNode({ id: "c", label: "Core", kind: "core_value", x: 200, y: 200 }),
    ]);
    let last: CanvasDoc | null = null;
    const { getByRole } = render(
      <FoundationCanvas
        {...commonProps(doc, (d) => {
          last = d;
        })}
      />,
    );
    fireEvent.click(getByRole("button", { name: /layout/i }));
    expect(last).not.toBeNull();
    const after = (last as unknown as CanvasDoc).nodes.find(
      (n) => n.id === "m",
    );
    expect(after, "node 'm' must survive auto-layout").toBeTruthy();
    if (!after) return;
    // Positions may change.
    // Non-position fields must be byte-identical.
    expect(after.kind).toBe(original.kind);
    expect(after.label).toBe(original.label);
    expect(after.parent_id).toBe(original.parent_id);
    expect(
      (after as unknown as Record<string, unknown>).what_we_do,
    ).toBe("doing-things");
    expect((after as unknown as Record<string, unknown>).why).toBe(
      "the-why",
    );
    expect((after as unknown as Record<string, unknown>).direction).toBe(
      "north",
    );
  });
});
