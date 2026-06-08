/**
 * D-2026-06-09-B — the React Flow attribution watermark ("React Flow",
 * bottom-right of the canvas) is hidden via `proOptions={{ hideAttribution:
 * true }}`. Plot ships as a commercial desktop app; `reactflow` is MIT, so
 * removing the attribution (which xyflow *recommends* but does not *require*)
 * is licit. This guards that the canvas does not render the
 * `.react-flow__attribution` panel.
 */
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReactFlowProvider } from "reactflow";
import { SketchCanvas } from "../src/canvases/SketchCanvas";
import type { SketchDoc } from "../src/types";

function makeDoc(): SketchDoc {
  return {
    id: "x",
    name: "X",
    created: "2026-04-20",
    updated: "2026-04-20T00:00:00Z",
    version: 1,
    nodes: [],
    edges: [],
  };
}

describe("React Flow attribution (D-2026-06-09-B)", () => {
  it("does not render the attribution watermark", () => {
    const { container } = render(
      <ReactFlowProvider>
        <SketchCanvas doc={makeDoc()} />
      </ReactFlowProvider>,
    );
    expect(container.querySelector(".react-flow__attribution")).toBeNull();
  });
});
