/**
 * LayoutControls direction toggle — D-2026-06-03-C.
 *
 * The two separate ↔ (LR) / ↕ (TB) buttons are replaced by ONE toggle
 * button that (a) shows the CURRENT layout direction as its icon, and
 * (b) flips horizontal ↔ vertical on click. User 2026-06-03: the old
 * buttons gave no indication of the current direction — *"누를 때마다
 * 왔다 갔다 하는데 정렬 버튼에 어떤 상태를 표시해주면 좋을 것 같은데"*.
 *
 * Current direction is derived from the subject edge's sourceHandle
 * (the SSOT), via ``detectAnchorDirection(doc)``.
 */
import "@testing-library/jest-dom/vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import i18n from "../src/i18n";
import { LayoutControls } from "../src/canvases/sketch/LayoutControls";
import type { CanvasDoc } from "../src/types";

function docWithHandle(sourceHandle: string | null): CanvasDoc {
  return {
    canvas_id: "t",
    canvas_kind: "service_detail",
    service_ref: null,
    nodes: [
      {
        id: "a",
        label: "actor",
        x: 0,
        y: 0,
        width: 130,
        height: 130,
        color: "#fce7f3",
        shape: "circle",
        icon: "user",
        collapsed: false,
        is_root: false,
        details_path: null,
        owner: null,
        version: "v1.0",
        _publish_baseline: null,
        kind: "actor_ref",
        ref_actor_id: "m",
        side: "user",
        gives: "",
        receives: "",
      },
      {
        id: "s",
        label: "entry",
        x: 0,
        y: 0,
        width: 180,
        height: 70,
        color: "#fff",
        shape: "rounded",
        icon: null,
        collapsed: false,
        is_root: false,
        details_path: null,
        owner: null,
        version: "v1.0",
        _publish_baseline: null,
        kind: "step",
        order: 1,
        outcome: "",
        body: "",
      },
    ],
    edges: [
      {
        id: "e",
        source: "a",
        target: "s",
        sourceHandle,
        targetHandle: "l",
        label: "",
        style: "solid",
        directed: true,
        relation: "flow",
        action_verb: null,
        value_form: [],
      },
    ],
  } as unknown as CanvasDoc;
}

describe("LayoutControls direction toggle (D-2026-06-03-C)", () => {
  it("shows one toggle reflecting the current horizontal direction (LR → ↔) and flips to TB", () => {
    const onDirection = vi.fn();
    render(
      <LayoutControls
        layoutAlgo="tree"
        showDirectionSwitch
        doc={docWithHandle("r")}
        onLayout={() => {}}
        onDirection={onDirection}
      />,
    );
    const btn = screen.getByRole("button", { name: i18n.t("canvas.layoutNowLR") });
    expect(btn).toHaveTextContent("↔");
    // The legacy two-button layout is gone — no separate TB button.
    expect(
      screen.queryByRole("button", { name: i18n.t("canvas.layoutNowTB") }),
    ).toBeNull();
    fireEvent.click(btn);
    expect(onDirection).toHaveBeenCalledWith("TB");
  });

  it("reflects the current vertical direction (TB → ↕) and flips to LR", () => {
    const onDirection = vi.fn();
    render(
      <LayoutControls
        layoutAlgo="tree"
        showDirectionSwitch
        doc={docWithHandle("b")}
        onLayout={() => {}}
        onDirection={onDirection}
      />,
    );
    const btn = screen.getByRole("button", { name: i18n.t("canvas.layoutNowTB") });
    expect(btn).toHaveTextContent("↕");
    fireEvent.click(btn);
    expect(onDirection).toHaveBeenCalledWith("LR");
  });

  it("hides the toggle when showDirectionSwitch is false (Foundation / Actors)", () => {
    render(
      <LayoutControls
        layoutAlgo="tree"
        doc={docWithHandle("r")}
        onLayout={() => {}}
        onDirection={() => {}}
      />,
    );
    // ⊞ present, no direction toggle.
    expect(
      screen.getByRole("button", { name: i18n.t("canvas.autoLayout") }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: i18n.t("canvas.layoutNowLR") }),
    ).toBeNull();
  });
});
