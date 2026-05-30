/**
 * Custom React Flow edge types. Mirrors ``nodes/registry.ts`` —
 * a single ``EDGE_TYPES`` map consumed by ``SketchCanvas`` 's
 * ``edgeTypes`` prop. Adding a new edge type goes through this file
 * so the wiring stays SSOT.
 */
import type { EdgeTypes } from "reactflow";
import { SelfLoopEdge } from "./SelfLoopEdge";
import { FloatingEdge } from "./FloatingEdge";

export const EDGE_TYPES: EdgeTypes = {
  selfLoop: SelfLoopEdge,
  // v0.30.3 (D-2026-05-31-F) — border-to-border floating edge; the
  // default type for every non-self-loop edge so a connection reads the
  // same from any side.
  floating: FloatingEdge,
};
