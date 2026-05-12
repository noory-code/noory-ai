/**
 * Foundation anchor-radial layout — v0.16.11 (D-2026-05-12-N).
 *
 * Pure-helper coverage. Verifies the canonical Plot spec mandate:
 *
 *   "프로젝트 노드 놓고(앵커) 그 주변에 미션, 코어밸류, 아이덴티티
 *    붙이면 되요. 뭐가 먼저고 말고는 없습니다."
 *
 * = anchor sits at canvas (0, 0); Mission / CoreValue / Identity
 * radiate from it 120° apart, no narrative ordering.
 *
 * Integration into ``useNodeCreation`` is exercised separately by
 * the existing SketchCanvas smoke / regression suites — anything
 * that mounts the Foundation canvas + creates a node touches this
 * code path.
 */
import { describe, expect, it } from "vitest";
import {
  FOUNDATION_RADIAL_KINDS,
  anchorRadialPosition,
  anchorRadialSlot,
  countFoundationKinds,
  isFoundationRadialKind,
} from "../src/canvases/sketch/anchorRadialLayout";

const R = 320; // canonical radius

function approx(a: number, b: number, eps = 0.5): boolean {
  return Math.abs(a - b) <= eps;
}

describe("FOUNDATION_RADIAL_KINDS", () => {
  it("covers exactly the three Foundation radial kinds", () => {
    expect([...FOUNDATION_RADIAL_KINDS].sort()).toEqual([
      "core_value",
      "identity",
      "mission",
    ]);
  });
});

describe("isFoundationRadialKind", () => {
  it("returns true for the three radial kinds", () => {
    expect(isFoundationRadialKind("mission")).toBe(true);
    expect(isFoundationRadialKind("core_value")).toBe(true);
    expect(isFoundationRadialKind("identity")).toBe(true);
  });

  it("returns false for non-radial kinds (project / actor / service / ref kinds / …)", () => {
    expect(isFoundationRadialKind("project")).toBe(false);
    expect(isFoundationRadialKind("actor")).toBe(false);
    expect(isFoundationRadialKind("service")).toBe(false);
    expect(isFoundationRadialKind("mission_ref")).toBe(false);
    expect(isFoundationRadialKind("metric")).toBe(false);
  });
});

describe("anchorRadialSlot — first node of each kind", () => {
  const empty = { mission: 0, core_value: 0, identity: 0 };

  it("places Mission at 270° (9 o'clock — left of anchor)", () => {
    const { x, y } = anchorRadialSlot("mission", empty);
    expect(approx(x, -R)).toBe(true);
    expect(approx(y, 0)).toBe(true);
  });

  it("places CoreValue at 30° (1 o'clock — upper-right of anchor)", () => {
    const { x, y } = anchorRadialSlot("core_value", empty);
    // sin30° = 0.5, cos30° ≈ 0.866 → (R/2, -R·0.866) = (160, -277.13)
    expect(approx(x, R * 0.5)).toBe(true);
    expect(approx(y, -R * Math.cos(Math.PI / 6))).toBe(true);
  });

  it("places Identity at 150° (5 o'clock — lower-right of anchor)", () => {
    const { x, y } = anchorRadialSlot("identity", empty);
    // sin150° = 0.5, cos150° = -0.866 → (R/2, R·0.866) = (160, +277.13)
    expect(approx(x, R * 0.5)).toBe(true);
    expect(approx(y, R * Math.cos(Math.PI / 6))).toBe(true);
  });

  it("places the three on a circle of radius 320 around (0, 0)", () => {
    for (const kind of FOUNDATION_RADIAL_KINDS) {
      const { x, y } = anchorRadialSlot(kind, empty);
      expect(approx(Math.hypot(x, y), R)).toBe(true);
    }
  });
});

describe("anchorRadialSlot — collision offset for repeated kinds", () => {
  it("offsets the 2nd Mission by 30° from the first", () => {
    const first = anchorRadialSlot("mission", { mission: 0, core_value: 0, identity: 0 });
    const second = anchorRadialSlot("mission", { mission: 1, core_value: 0, identity: 0 });
    // Two different positions on the same radius.
    expect(first).not.toEqual(second);
    expect(approx(Math.hypot(second.x, second.y), R)).toBe(true);
  });

  it("each additional same-kind node lands on the radius", () => {
    for (let i = 0; i < 5; i++) {
      const { x, y } = anchorRadialSlot("core_value", {
        mission: 0,
        core_value: i,
        identity: 0,
      });
      expect(approx(Math.hypot(x, y), R)).toBe(true);
    }
  });
});

describe("anchorRadialPosition — centres the node on the slot", () => {
  const empty = { mission: 0, core_value: 0, identity: 0 };
  const W = 180;
  const H = 80;

  it("returns top-left position so that node centre lands on the radial slot", () => {
    const slot = anchorRadialSlot("mission", empty);
    const topLeft = anchorRadialPosition("mission", empty, W, H);
    expect(topLeft.x).toBe(slot.x - W / 2);
    expect(topLeft.y).toBe(slot.y - H / 2);
  });
});

describe("countFoundationKinds", () => {
  it("ignores non-radial kinds", () => {
    const nodes = [
      { kind: "project" },
      { kind: "actor" },
      { kind: "mission" },
      { kind: "mission" },
      { kind: "core_value" },
      { kind: "identity" },
      { kind: "service" },
      { kind: "mission_ref" },
    ];
    expect(countFoundationKinds(nodes)).toEqual({
      mission: 2,
      core_value: 1,
      identity: 1,
    });
  });

  it("returns zeros for an empty canvas", () => {
    expect(countFoundationKinds([])).toEqual({
      mission: 0,
      core_value: 0,
      identity: 0,
    });
  });
});
