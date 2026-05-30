/**
 * foldEndpoints — semantic-aware fold parent/child — v0.30.1
 * (D-2026-05-31-D).
 *
 * Fold (collapse) hierarchy is derived from the edge's stored
 * ``relation``, not just ``directed``:
 *  - flow        → source = parent, target = child (unchanged).
 *  - inheritance → target = parent, source = child (INVERTED — the
 *    arrow points child→superclass, but collapsing the *superclass*
 *    must hide its subclasses).
 *  - injection   → null (an essence overlay doesn't *contain* its
 *    target; never participates in fold).
 *  - undirected  → null (no hierarchy).
 */
import { describe, expect, it } from "vitest";
import { foldEndpoints } from "../src/flow/foldHierarchy";
import type { SketchEdge } from "../src/types";

function edge(over: Partial<SketchEdge>): SketchEdge {
  return {
    id: "e",
    source: "s",
    target: "t",
    sourceHandle: null,
    targetHandle: null,
    label: "",
    style: "solid",
    directed: true,
    relation: "flow",
    action_verb: null,
    value_form: [],
    ...over,
  } as SketchEdge;
}

describe("foldEndpoints (D-2026-05-31-D)", () => {
  it("flow: source is parent, target is child", () => {
    expect(foldEndpoints(edge({ relation: "flow" }))).toEqual({
      parent: "s",
      child: "t",
    });
  });

  it("inheritance: target (superclass) is parent — inverted", () => {
    expect(foldEndpoints(edge({ relation: "inheritance" }))).toEqual({
      parent: "t",
      child: "s",
    });
  });

  it("injection: excluded from fold (null)", () => {
    expect(foldEndpoints(edge({ relation: "injection" }))).toBeNull();
  });

  it("undirected edges never define hierarchy (null)", () => {
    expect(foldEndpoints(edge({ directed: false, relation: "flow" }))).toBeNull();
    expect(
      foldEndpoints(edge({ directed: false, relation: "inheritance" })),
    ).toBeNull();
  });

  it("missing relation defaults to flow", () => {
    const e = edge({});
    // @ts-expect-error simulate a pre-v0.30 edge with no relation
    delete e.relation;
    expect(foldEndpoints(e)).toEqual({ parent: "s", child: "t" });
  });
});
