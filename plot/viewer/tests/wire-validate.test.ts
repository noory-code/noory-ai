/**
 * D-2026-06-12-B / ROADMAP Track 1.4 — wire boundary domain validation.
 *
 * Every CanvasDoc that crosses the HTTP wire (getCanvas / getAllCanvases /
 * putCanvas response) is run through ``parseEntity`` so the discriminated
 * union's invariants gate at one place instead of leaking malformed
 * nodes deeper into the viewer. This pins:
 *
 *   1. Valid canvases pass through untouched (same nodes, same ref).
 *   2. Unknown ``kind`` discriminators throw ``DomainParseError`` at the
 *      boundary (not deep inside React Flow / Inspector).
 *   3. Per-kind invariants (e.g. ``actor_ref`` requires ``ref_actor_id``)
 *      throw too — the server's Pydantic models already enforce this on
 *      write, so a violation is a contract breach and should fail fast.
 *   4. ``validateCanvas`` is a no-op cost / no-clone for valid input —
 *      React Flow's prototype-stripping ``applyNodeChanges`` keeps
 *      working on the same plain-JSON shapes (per `domain/SketchNode.ts`).
 */
import { describe, expect, it } from "vitest";
import { DomainParseError } from "../src/domain/DomainParseError";
import type { CanvasDoc, SketchNode } from "../src/types";
import { validateCanvas } from "../src/api";

function makeCanvas(nodes: SketchNode[]): CanvasDoc {
  return {
    canvas_id: "foundation",
    canvas_kind: "foundation",
    nodes,
    edges: [],
  } as CanvasDoc;
}

const projectNode: SketchNode = {
  id: "p1",
  label: "Project",
  x: 0,
  y: 0,
  width: 96,
  height: 96,
  color: "#fef3c7",
  shape: "circle",
  icon: null,
  collapsed: false,
  is_root: false,
  details_path: null,
  version: "v1.0",
  kind: "project",
} as SketchNode;

const missionNode: SketchNode = {
  ...(projectNode as unknown as Record<string, unknown>),
  id: "m1",
  kind: "mission",
  statement: "",
  body: "",
} as unknown as SketchNode;

describe("validateCanvas", () => {
  it("passes a valid canvas through and returns the same reference", () => {
    const canvas = makeCanvas([projectNode, missionNode]);
    const out = validateCanvas(canvas);
    expect(out).toBe(canvas);
    expect(out.nodes).toBe(canvas.nodes);
  });

  it("throws DomainParseError on an unknown kind", () => {
    const canvas = makeCanvas([
      { ...projectNode, kind: "totally-not-a-kind" } as unknown as SketchNode,
    ]);
    expect(() => validateCanvas(canvas)).toThrow(DomainParseError);
  });

  it("throws DomainParseError on a malformed required field", () => {
    // ``ref_actor_id`` must be a string (or null). A number breaks the
    // ``readNullableString`` parser in ActorRef.fromJson.
    const badRef = {
      id: "ar1",
      label: "ref",
      x: 0,
      y: 0,
      width: 96,
      height: 96,
      color: "#fff",
      shape: "circle",
      icon: null,
      collapsed: false,
      is_root: false,
      details_path: null,
      version: "v1.0",
      kind: "actor_ref",
      ref_actor_id: 12345,
      gives: "",
      receives: "",
      side: "user",
    } as unknown as SketchNode;
    const canvas = makeCanvas([badRef]);
    expect(() => validateCanvas(canvas)).toThrow(DomainParseError);
  });

  it("throws DomainParseError on a missing kind discriminator", () => {
    const noKind = { ...(projectNode as unknown as Record<string, unknown>) };
    delete noKind.kind;
    const canvas = makeCanvas([noKind as unknown as SketchNode]);
    expect(() => validateCanvas(canvas)).toThrow(DomainParseError);
  });

  it("accepts an empty nodes array", () => {
    const canvas = makeCanvas([]);
    expect(() => validateCanvas(canvas)).not.toThrow();
  });
});
