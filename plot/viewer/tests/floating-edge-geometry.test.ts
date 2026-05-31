/**
 * Floating-edge geometry — v0.30.3 (D-2026-05-31-F).
 *
 * The edge attaches to the point on each node's border facing the
 * other node, so connection behaviour is identical from any side.
 */
import { describe, expect, it } from "vitest";
import {
  borderSide,
  nodeBorderPoint,
  floatingEndpoints,
} from "../src/flow/floatingEdgeGeometry";

const A = { x: 0, y: 0, width: 100, height: 100 }; // centre (50,50)

describe("borderSide (v0.34.5 — bezier control side)", () => {
  it("classifies each border point by side", () => {
    expect(borderSide(100, 50, A)).toBe("right");
    expect(borderSide(0, 50, A)).toBe("left");
    expect(borderSide(50, 0, A)).toBe("top");
    expect(borderSide(50, 100, A)).toBe("bottom");
  });
});

describe("nodeBorderPoint (D-2026-05-31-F)", () => {
  it("faces a node to the right → exits the right edge midpoint", () => {
    const right = { x: 300, y: 0, width: 100, height: 100 }; // centre (350,50)
    const p = nodeBorderPoint(A, right);
    expect(p.x).toBeCloseTo(100, 5); // right border
    expect(p.y).toBeCloseTo(50, 5); // vertical middle
  });

  it("faces a node to the left → exits the left edge midpoint", () => {
    const left = { x: -300, y: 0, width: 100, height: 100 };
    const p = nodeBorderPoint(A, left);
    expect(p.x).toBeCloseTo(0, 5); // left border
    expect(p.y).toBeCloseTo(50, 5);
  });

  it("faces a node above → exits the top edge midpoint", () => {
    const above = { x: 0, y: -300, width: 100, height: 100 };
    const p = nodeBorderPoint(A, above);
    expect(p.x).toBeCloseTo(50, 5);
    expect(p.y).toBeCloseTo(0, 5); // top border
  });

  it("faces a node below → exits the bottom edge midpoint", () => {
    const below = { x: 0, y: 300, width: 100, height: 100 };
    const p = nodeBorderPoint(A, below);
    expect(p.x).toBeCloseTo(50, 5);
    expect(p.y).toBeCloseTo(100, 5); // bottom border
  });

  it("coincident centres → returns the centre (no NaN)", () => {
    const p = nodeBorderPoint(A, A);
    expect(Number.isFinite(p.x)).toBe(true);
    expect(Number.isFinite(p.y)).toBe(true);
  });

  it("zero-size node → returns its centre", () => {
    const z = { x: 10, y: 20, width: 0, height: 0 };
    expect(nodeBorderPoint(z, A)).toEqual({ x: 10, y: 20 });
  });
});

describe("floatingEndpoints", () => {
  it("returns both facing border points (left node ↔ right node)", () => {
    const right = { x: 300, y: 0, width: 100, height: 100 };
    const { sx, sy, tx, ty } = floatingEndpoints(A, right);
    expect(sx).toBeCloseTo(100, 5); // A's right
    expect(sy).toBeCloseTo(50, 5);
    expect(tx).toBeCloseTo(300, 5); // right node's left border
    expect(ty).toBeCloseTo(50, 5);
  });
});
