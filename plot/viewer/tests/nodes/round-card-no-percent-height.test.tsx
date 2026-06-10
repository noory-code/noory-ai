/**
 * D-2026-06-11-A — round shapes (circle/ellipse, incl. project anchor) must NOT
 * rely on a child's `h-full` to size themselves. WebKit (the Tauri WKWebView)
 * resolves the `width:fit-content + min-width + aspect-ratio + percentage-height
 * child` combination into a non-square box: with min-w-96 it produced
 * 96×132 anchors instead of 96×96 (132 = aspect-derived 96 content-h + py-4 32
 * + border-2 4 — the % child fed content-height back into the height resolution
 * loop, making it grow past the square).
 *
 * Live evidence (debug probe, 2026-06-11): the Banas anchor rendered
 * 192×264 at zoom 2 (= 96×132 layout) with `box-sizing: border-box`,
 * `aspect-ratio: 1/1`, and inner h-full = 96 — proving box-sizing was not the
 * cause and `h-full` was.
 *
 * Fix: the round card is itself `flex flex-col justify-center`, the inner
 * content div drops `h-full`. Vertical centering is then enforced by the card's
 * own flex layout, with no percentage height dependency.
 *
 * Guards (this file):
 *   1. The round card carries `flex flex-col justify-center` so it can
 *      vertical-center without h-full.
 *   2. No descendant of the round card uses `h-full` — that class on any inner
 *      div would re-introduce the WebKit aspect-ratio bug.
 *   3. Rectangular cards still NEVER carry `aspect-square` (sanity — only
 *      round shapes opt into the square auto-fit).
 */
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReactFlowProvider, type NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../../src/canvases/nodes/BaseNode";

function makeProps(data: Partial<BaseNodeData>): NodeProps<BaseNodeData> {
  const full: BaseNodeData = {
    label: "Card",
    body: "",
    color: "#fde68a",
    width: 96,
    height: 96,
    shape: "circle",
    icon: null,
    kind: "project",
    ...data,
  };
  return {
    id: "n1",
    data: full,
    selected: false,
    type: full.kind,
    zIndex: 0,
    isConnectable: true,
    xPos: 0,
    yPos: 0,
    dragging: false,
  } as unknown as NodeProps<BaseNodeData>;
}

function renderCard(data: Partial<BaseNodeData> = {}) {
  return render(
    <ReactFlowProvider>
      <BaseNode {...makeProps(data)} />
    </ReactFlowProvider>,
  );
}

describe("round card sizing (D-2026-06-11-A)", () => {
  it.each([["circle"], ["ellipse"]] as const)(
    "%s card is a flex column with justify-center (no percentage-height child needed)",
    (shape) => {
      const { container } = renderCard({ shape });
      const card = container.querySelector("[data-node-id='n1']")!;
      expect(card.classList.contains("flex")).toBe(true);
      expect(card.classList.contains("flex-col")).toBe(true);
      expect(card.classList.contains("justify-center")).toBe(true);
    },
  );

  it.each([["circle"], ["ellipse"]] as const)(
    "%s card has no descendant relying on h-full (WebKit aspect-ratio loop)",
    (shape) => {
      const { container } = renderCard({ shape });
      const card = container.querySelector("[data-node-id='n1']")!;
      const offenders: string[] = [];
      card.querySelectorAll("*").forEach((el) => {
        if (el.classList.contains("h-full")) {
          offenders.push(`${el.tagName.toLowerCase()}.${el.className}`);
        }
      });
      expect(offenders, `h-full inside round card re-introduces WebKit bug`).toEqual([]);
    },
  );

  it.each([
    ["rounded"],
    ["rectangle"],
    ["diamond"],
    ["hexagon"],
    ["octagon"],
  ] as const)("%s card does NOT carry aspect-square", (shape) => {
    const { container } = renderCard({ shape });
    const card = container.querySelector("[data-node-id='n1']")!;
    expect(card.classList.contains("aspect-square")).toBe(false);
  });
});
