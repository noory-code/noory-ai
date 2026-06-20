/**
 * v0.27.19 (D-2026-05-30-A / D-2026-05-30-B) — FeatureDetail step
 * authoring affordances.
 *
 * Phase A (D-2026-05-30-A): ``step.outcome`` renders on the canvas
 * node (was Inspector-only) and is inline-editable.
 * Phase B (D-2026-05-30-B): a step with ≥ 2 outgoing directed edges
 * (a branch point per SPEC §"Service composition model") renders a
 * derived branch badge — no new field, the existing edge count is
 * the source of truth.
 */
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReactFlowProvider, type NodeProps } from "reactflow";
import { StepNode } from "../../src/canvases/nodes/step";
import type { BaseNodeData } from "../../src/canvases/nodes/BaseNode";

function makeProps(data: Partial<BaseNodeData>): NodeProps<BaseNodeData> {
  const full: BaseNodeData = {
    label: "Submit",
    body: "",
    color: "#fff",
    width: 180,
    height: 80,
    shape: "rectangle",
    icon: null,
    kind: "step",
    ...data,
  };
  return {
    id: "s1",
    data: full,
    selected: false,
    type: "step",
    zIndex: 0,
    isConnectable: true,
    xPos: 0,
    yPos: 0,
    dragging: false,
  } as unknown as NodeProps<BaseNodeData>;
}

function renderStep(data: Partial<BaseNodeData>) {
  return render(
    <ReactFlowProvider>
      <StepNode {...makeProps(data)} />
    </ReactFlowProvider>,
  );
}

describe("StepNode — outcome on canvas (Phase A)", () => {
  it("renders the outcome text below the label", () => {
    renderStep({ outcome: "Server verifies credentials" });
    expect(screen.getByText("Server verifies credentials")).toBeTruthy();
  });

  it("commits an inline outcome edit through onOutcomeChange", () => {
    const onOutcomeChange = vi.fn();
    renderStep({ outcome: "old outcome", onOutcomeChange });
    // EditableText exposes a role="button" span with the aria-label.
    const editable = screen.getByLabelText(/Outcome\. Click to edit\./i);
    fireEvent.click(editable);
    const textarea = screen.getByLabelText("Outcome") as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "new outcome" } });
    fireEvent.blur(textarea);
    expect(onOutcomeChange).toHaveBeenCalledWith("new outcome");
  });
});

describe("StepNode — branch badge (Phase B)", () => {
  it("renders a branch badge when branchCount ≥ 2", () => {
    renderStep({ branchCount: 3 });
    expect(screen.getByLabelText(/branch point/i)).toBeTruthy();
  });

  it("does NOT render a branch badge for a linear step (branchCount < 2)", () => {
    renderStep({ branchCount: 1 });
    expect(screen.queryByLabelText(/branch point/i)).toBeNull();
  });
});
