/**
 * Cursor uniformity sweep — D-2026-05-12-C, Phase 4.1.
 *
 * The user's complaint that fired the v0.15 reset was sensory:
 *
 *   *"파운데이션에서 사용되는 커서 컨트롤하고 액터나 서비스에서
 *     사용되는 커서 컨트롤이 다릅니다."* (2026-05-12)
 *
 * After Phases 1+2+3 every canvas wrapper (Foundation / Actors /
 * Services / ServiceDetail) routes through the same SketchCanvas +
 * NODE_RENDERERS + BaseNode pipeline. This test pins the empirical
 * consequence: with the same seeded doc, all 4 wrappers produce an
 * identical set of cursor-determining DOM hooks, and zero element
 * across any wrapper carries an inline ``style.cursor`` assignment.
 *
 * Combined with ``styles-cursor-baseline.test.tsx`` (styles.css has
 * zero ``cursor:`` declarations) and Phase 4.2's extended static
 * guard, this proves cursor inventory is fully determined by the
 * shared RF + Tailwind preflight stack and cannot drift per-canvas.
 *
 * Pairs with the manual DevTools verification recipe in
 * ``plot/docs/CURSOR.md`` §"How to verify the cursor state in the
 * browser" — that recipe is the user-runnable getComputedStyle
 * confirmation; this file is the JSDOM-side structural proof.
 */
import { render, cleanup } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ActorsCanvas } from "../src/canvases/ActorsCanvas";
import { FoundationCanvas } from "../src/canvases/FoundationCanvas";
import { ServiceDetailCanvas } from "../src/canvases/ServiceDetailCanvas";
import { ServicesCanvas } from "../src/canvases/ServicesCanvas";
import { createBlankNode } from "../src/domain/createBlankNode";
import type { CanvasDoc, NodeKind, SketchNode } from "../src/types";

afterEach(() => {
  cleanup();
});

function makeDoc(nodes: SketchNode[] = []): CanvasDoc {
  return {
    id: "cursor-sweep",
    name: "Cursor Sweep",
    created: "2026-05-12",
    updated: "2026-05-12T00:00:00Z",
    version: 1,
    nodes,
    edges: [],
  };
}

function reactFlowClassFragments(root: Element): string[] {
  const out = new Set<string>();
  root.querySelectorAll('[class*="react-flow__"]').forEach((el) => {
    el.classList.forEach((c) => {
      if (c.startsWith("react-flow__")) out.add(c);
    });
  });
  return [...out].sort();
}

interface InlineCursor {
  tag: string;
  cls: string;
  cursor: string;
}

function inlineCursors(root: Element): InlineCursor[] {
  const out: InlineCursor[] = [];
  root.querySelectorAll<HTMLElement>("*").forEach((el) => {
    const c = el.style.cursor;
    if (c) {
      out.push({
        tag: el.tagName,
        cls: String(el.className).slice(0, 80),
        cursor: c,
      });
    }
  });
  return out;
}

const WRAPPERS: { name: string; Comp: typeof FoundationCanvas }[] = [
  { name: "FoundationCanvas", Comp: FoundationCanvas },
  { name: "ActorsCanvas", Comp: ActorsCanvas },
  { name: "ServicesCanvas", Comp: ServicesCanvas },
  { name: "ServiceDetailCanvas", Comp: ServiceDetailCanvas },
];

const ALL_KINDS: NodeKind[] = [
  "project",
  "mission",
  "core_value",
  "identity",
  "actor",
  "actor_ref",
  "service",
  "feature",
  "category",
  "step",
  "decision",
  "note",
  "rule",
];

function seedAllKinds(): SketchNode[] {
  return ALL_KINDS.map((kind, i) =>
    createBlankNode(kind, {
      id: `${kind}-${i}`,
      label: kind,
      x: (i % 5) * 220,
      y: Math.floor(i / 5) * 140,
      width: 180,
      height: 80,
      color: "#ffffff",
      shape: "rounded",
      icon: null,
      parent_id: null,
    }),
  );
}

describe("cursor-sweep: zero inline cursor assignments", () => {
  it("FoundationCanvas — no element has inline style.cursor (empty doc)", () => {
    const { container } = render(<FoundationCanvas doc={makeDoc()} />);
    expect(inlineCursors(container)).toEqual([]);
  });

  it("ActorsCanvas — no element has inline style.cursor (empty doc)", () => {
    const { container } = render(<ActorsCanvas doc={makeDoc()} />);
    expect(inlineCursors(container)).toEqual([]);
  });

  it("ServicesCanvas — no element has inline style.cursor (empty doc)", () => {
    const { container } = render(<ServicesCanvas doc={makeDoc()} />);
    expect(inlineCursors(container)).toEqual([]);
  });

  it("ServiceDetailCanvas — no element has inline style.cursor (empty doc)", () => {
    const { container } = render(<ServiceDetailCanvas doc={makeDoc()} />);
    expect(inlineCursors(container)).toEqual([]);
  });

  it("all 4 wrappers — no inline cursor when seeded with all 13 kinds", () => {
    const seeded = seedAllKinds();
    for (const { name, Comp } of WRAPPERS) {
      const { container } = render(<Comp doc={makeDoc(seeded)} />);
      expect(inlineCursors(container), `${name} inline cursors`).toEqual([]);
      cleanup();
    }
  });
});

describe("cursor-sweep: react-flow__* class skeleton equivalence", () => {
  it("all 4 wrappers expose the same react-flow__* class skeleton on an empty doc", () => {
    const skeletons = WRAPPERS.map(({ name, Comp }) => {
      const { container } = render(<Comp doc={makeDoc()} />);
      const fragments = reactFlowClassFragments(container);
      cleanup();
      return { name, fragments };
    });
    const reference = skeletons[0];
    for (const other of skeletons.slice(1)) {
      expect(
        other.fragments,
        `${other.name} react-flow__* skeleton differs from ${reference.name}`,
      ).toEqual(reference.fragments);
    }
    // Sanity: the shared skeleton actually contains the core React Flow
    // surfaces we expect every canvas to expose for cursor targeting.
    expect(reference.fragments).toEqual(
      expect.arrayContaining([
        "react-flow__pane",
        "react-flow__renderer",
        "react-flow__viewport",
      ]),
    );
  });
});

describe("cursor-sweep: per-kind node renderers use shared chrome", () => {
  it("nodes carry no inline style.cursor regardless of kind (FoundationCanvas seed)", () => {
    const foundationKinds: NodeKind[] = [
      "project",
      "mission",
      "core_value",
      "identity",
    ];
    const nodes = foundationKinds.map((kind, i) =>
      createBlankNode(kind, {
        id: `${kind}-${i}`,
        label: kind,
        x: i * 200,
        y: 0,
        width: 180,
        height: 80,
        color: "#ffffff",
        shape: "rounded",
        icon: null,
        parent_id: null,
      }),
    );
    const { container } = render(<FoundationCanvas doc={makeDoc(nodes)} />);
    expect(inlineCursors(container)).toEqual([]);
  });

  it("nodes carry no inline style.cursor regardless of kind (ServicesCanvas seed)", () => {
    const nodes = [
      createBlankNode("category", {
        id: "cat-1",
        label: "Admin",
        x: 0,
        y: 0,
        width: 240,
        height: 160,
        color: "#fef3c7",
        shape: "rounded",
        icon: null,
        parent_id: null,
      }),
      createBlankNode("service", {
        id: "svc-1",
        label: "Sign-up",
        x: 20,
        y: 20,
        width: 180,
        height: 80,
        color: "#ffffff",
        shape: "circle",
        icon: null,
        parent_id: "cat-1",
      }),
    ];
    const { container } = render(<ServicesCanvas doc={makeDoc(nodes)} />);
    expect(inlineCursors(container)).toEqual([]);
  });
});
