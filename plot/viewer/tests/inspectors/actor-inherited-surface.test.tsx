/**
 * Actor inherited-surface caption shows the localized option label,
 * not the raw enum — v0.31.2 (D-2026-05-31-J).
 *
 * When a sub-actor's own `side` (Surface / 접점) is unset, it inherits
 * the parent's. The inherited caption must render the friendly option
 * label ("사용자 — 앱" / "user — app"), NOT the raw enum value "user" —
 * the enum is an implementation detail the user never typed.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import i18n from "../../src/i18n";
import { KindInspector } from "../../src/canvases/inspectors/KindInspector";
import type { SketchEdge, SketchNode } from "../../src/types";

function makeNode(overrides: Partial<SketchNode> & { kind: SketchNode["kind"] }): SketchNode {
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

function inheritEdge(child: string, parent: string): SketchEdge {
  return {
    id: `e_${child}_${parent}`,
    source: child,
    target: parent,
    sourceHandle: null,
    targetHandle: null,
    label: "",
    style: "solid",
    directed: true,
    relation: "inheritance",
    action_verb: null,
    value_form: [],
  } as SketchEdge;
}

describe("Actor inherited Surface caption (D-2026-05-31-J)", () => {
  it("shows the localized Surface label, not the raw enum, for an inherited side", () => {
    const hero = makeNode({ id: "hero", kind: "actor", label: "Hero", side: null });
    const bana = makeNode({ id: "bana", kind: "actor", label: "Bana", side: "user" });
    render(
      <KindInspector
        node={hero}
        allNodes={[hero, bana]}
        allEdges={[inheritEdge("hero", "bana")]}
        onPatchNode={vi.fn()}
        onDeleteNode={vi.fn()}
        onClose={vi.fn()}
        projectPath="/tmp/plot-test"
        projectId="test-project"
        canvasKind="actors"
      />,
    );

    // Own surface is unset.
    const select = screen.getByRole("combobox") as HTMLSelectElement;
    expect(select.value).toBe("");

    // The inherited caption renders the friendly option label …
    const userLabel = i18n.t("inspector.userOption");
    const fromBana = i18n.t("inspector.inheritedFrom", { from: "Bana" });
    expect(screen.getByText(`↳ ${fromBana}: ${userLabel}`)).toBeInTheDocument();

    // … and never the bare enum "user" as the inherited value.
    expect(screen.queryByText(`↳ ${fromBana}: user`)).not.toBeInTheDocument();
  });
});
