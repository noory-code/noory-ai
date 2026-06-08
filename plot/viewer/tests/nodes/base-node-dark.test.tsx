/**
 * D-2026-06-09-A — a node card carries the user's fixed background colour
 * (`data.color`), so its on-card text must read dark-on-light in BOTH themes.
 * The fix scopes the foreground vars to the card via a `node-card` class
 * (light-locked in `theme/tokens.css`). This guards that the card root div
 * actually carries that class — without it the on-card text would inherit the
 * theme `--fg*` vars and turn light in dark mode, vanishing on the light card
 * (the bug the user reported: "노드 안에 글자 색깔" invisible in dark).
 *
 * Note: JSDOM does not resolve Tailwind classes → computed colours (that is a
 * build-time PostCSS step), so we cannot assert the rendered colour directly.
 * This pairs with `theme-tokens.test.ts` ("node-card on-card colours are
 * theme-locked"), which proves `.node-card` re-declares those vars at the
 * light value. Together: the card carries the class (here) AND the class
 * locks the colours (there).
 */
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReactFlowProvider, type NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../../src/canvases/nodes/BaseNode";

function makeProps(data: Partial<BaseNodeData>): NodeProps<BaseNodeData> {
  const full: BaseNodeData = {
    label: "Card",
    body: "",
    color: "#fde68a", // a light user colour, as on a real canvas
    width: 160,
    height: 64,
    shape: "rounded",
    icon: null,
    kind: "mission",
    ...data,
  };
  return {
    id: "n1",
    data: full,
    selected: false,
    type: "mission",
    zIndex: 0,
    isConnectable: true,
    xPos: 0,
    yPos: 0,
    dragging: false,
  } as unknown as NodeProps<BaseNodeData>;
}

describe("BaseNode scopes on-card text to a light-locked node-card class (D-2026-06-09-A)", () => {
  it("the card root div carries the node-card class", () => {
    const { container } = render(
      <ReactFlowProvider>
        <BaseNode {...makeProps({})} />
      </ReactFlowProvider>,
    );
    const card = container.querySelector("[data-node-id='n1']");
    expect(card, "card root [data-node-id] not found").toBeTruthy();
    expect(card!.classList.contains("node-card")).toBe(true);
  });
});
