/**
 * Edge semantic classifier — v0.30.0 (D-2026-05-31-C).
 *
 * `classifyEdge` is the DEFAULT assigner for the stored
 * `SketchEdge.relation` field. The stored value is the SSOT once set
 * (read by viewer fold/style AND server publish-propagation); this
 * function only decides the default when an edge is drawn / migrated.
 *
 * Rules (mirrored byte-for-byte in `plot_mcp/edge_semantics.py`):
 *  - actors canvas → every directed edge is `inheritance`
 *    (the actors canvas has a single edge type — user 2026-05-31).
 *  - source kind is an essence kind (mission / core_value / identity
 *    or their `*_ref`) → `injection` (essence flows into the target).
 *    `actor_ref` is excluded — it is the sequence subject, not an
 *    overlay (mirrors `foundationRefKinds`).
 *  - everything else → `flow`.
 */
import { describe, expect, it } from "vitest";
import { classifyEdge } from "../src/flow/edgeSemantics";

describe("classifyEdge (D-2026-05-31-C)", () => {
  it("classifies every actors-canvas edge as inheritance", () => {
    expect(classifyEdge("actors", "actor")).toBe("inheritance");
    // even an anchor-sourced (backwards) edge on actors is inheritance
    expect(classifyEdge("actors", "project")).toBe("inheritance");
  });

  it("classifies foundation essence-master sources as injection", () => {
    for (const k of ["mission", "core_value", "identity"]) {
      expect(classifyEdge("foundation", k)).toBe("injection");
    }
  });

  // mission_ref / value_ref / identity_ref retired 2026-06-20 (D-2026-06-20-G);
  // their injection-edge classification went with them.

  it("treats actor_ref (the subject) as flow, not injection", () => {
    expect(classifyEdge("service_detail", "actor_ref")).toBe("flow");
  });

  it("classifies step / service / category edges as flow", () => {
    expect(classifyEdge("service_detail", "step")).toBe("flow");
    expect(classifyEdge("service_detail", "decision")).toBe("flow");
    expect(classifyEdge("services", "service")).toBe("flow");
    expect(classifyEdge("services", "category")).toBe("flow");
  });

  it("defaults unknown/undefined sources to flow", () => {
    expect(classifyEdge("foundation", undefined)).toBe("flow");
    expect(classifyEdge("services", "bogus")).toBe("flow");
  });
});
