import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReactFlowProvider } from "reactflow";
import { SketchCanvas } from "../src/canvases/SketchCanvas";
import type { SketchDoc } from "../src/types";

function makeDoc(overrides: Partial<SketchDoc> = {}): SketchDoc {
  return {
    id: "x",
    name: "X",
    created: "2026-04-20",
    updated: "2026-04-20T00:00:00Z",
    version: 1,
    nodes: [],
    edges: [],
    ...overrides,
  };
}

describe("SketchCanvas (smoke)", () => {
  it("mounts with empty document", () => {
    const { container } = render(
      <ReactFlowProvider>
        <SketchCanvas doc={makeDoc()} />
      </ReactFlowProvider>,
    );
    // React Flow attaches a container div — just verify mount succeeds.
    expect(container.querySelector(".react-flow")).toBeTruthy();
  });

  it("renders nodes and edges", () => {
    const doc = makeDoc({
      nodes: [
        {
          id: "a",
          label: "A",
          body: "",
          x: 0,
          y: 0,
          width: 180,
          height: 80,
          color: "#fff",
        },
        {
          id: "b",
          label: "B",
          body: "",
          x: 200,
          y: 0,
          width: 180,
          height: 80,
          color: "#fff",
        },
      ],
      edges: [
        {
          id: "e1",
          source: "a",
          target: "b",
          sourceHandle: null,
          targetHandle: null,
          label: "to",
          style: "solid",
        },
      ],
    });
    const { container } = render(
      <ReactFlowProvider>
        <SketchCanvas doc={doc} />
      </ReactFlowProvider>,
    );
    expect(container.querySelector(".react-flow")).toBeTruthy();
  });
});
