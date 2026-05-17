/**
 * v0.22.0 (D-2026-05-17-H) — Publish button dirty-gate tests.
 *
 * The button is disabled when the server-decorated ``_dirty: false``
 * arrives on the node; enabled otherwise. Missing ``_dirty`` is treated
 * as ``true`` (back-compat for pre-v0.22.0 server).
 */
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { KindInspector } from "../../src/canvases/inspectors/KindInspector";
import type { CanvasKind, SketchNode } from "../../src/types";

interface MakeNodeOverrides extends Partial<SketchNode> {
  kind: SketchNode["kind"];
}

function makeNode(overrides: MakeNodeOverrides): SketchNode {
  return {
    id: "id-1",
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
    version: "v1.0",
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
    body: "",
    ...overrides,
  };
}

function makeProps(node: SketchNode, canvasKind: CanvasKind = "foundation") {
  return {
    node,
    allNodes: [node],
    onPatchNode: vi.fn(),
    onDeleteNode: vi.fn(),
    onClose: vi.fn(),
    onPublishNode: vi.fn(),
    projectPath: "/tmp/plot-test",
    projectId: "test-project",
    canvasKind,
  };
}

describe("Publish button dirty gate (D-2026-05-17-H)", () => {
  it("is enabled when node._dirty is true", () => {
    const node = makeNode({
      id: "id-1",
      kind: "identity",
      label: "Voice",
      description: "warm",
      _dirty: true,
    });
    render(<KindInspector {...makeProps(node)} />);
    const button = screen.getByRole("button", { name: /publish version/i });
    expect(button).toBeEnabled();
  });

  it("is enabled when node._dirty is undefined (back-compat)", () => {
    const node = makeNode({
      id: "id-1",
      kind: "identity",
      label: "Voice",
      description: "warm",
      // _dirty omitted on purpose
    });
    render(<KindInspector {...makeProps(node)} />);
    const button = screen.getByRole("button", { name: /publish version/i });
    expect(button).toBeEnabled();
  });

  it("is disabled when node._dirty is false", () => {
    const node = makeNode({
      id: "id-1",
      kind: "identity",
      label: "Voice",
      description: "warm",
      _dirty: false,
      version: "v2.0",
    });
    render(<KindInspector {...makeProps(node)} />);
    const button = screen.getByRole("button", { name: /publish version/i });
    expect(button).toBeDisabled();
    // Localised tooltip names the last-published version.
    expect(button.getAttribute("title")).toContain("v2.0");
  });

  it("disabled button does not call onPublishNode on click", () => {
    const node = makeNode({
      id: "id-1",
      kind: "identity",
      label: "Voice",
      description: "warm",
      _dirty: false,
    });
    const props = makeProps(node);
    render(<KindInspector {...props} />);
    const button = screen.getByRole("button", { name: /publish version/i });
    // Disabled buttons swallow clicks at the browser level; verify
    // onPublishNode stays uncalled even if a click event is dispatched.
    button.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
    expect(props.onPublishNode).not.toHaveBeenCalled();
  });
});
