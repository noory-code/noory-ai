/**
 * Custom React Flow edge types. Mirrors ``nodes/registry.ts`` —
 * a single ``EDGE_TYPES`` map consumed by ``SketchCanvas`` 's
 * ``edgeTypes`` prop. Adding a new edge type goes through this file
 * so the wiring stays SSOT.
 */
import type { EdgeTypes } from "reactflow";
import { SelfLoopEdge } from "./SelfLoopEdge";

// v0.40.0 (D-2026-06-01-E) — floating edges removed. Only self-loops
// need a custom renderer now; every other edge uses RF's default bezier.
export const EDGE_TYPES: EdgeTypes = {
  selfLoop: SelfLoopEdge,
};
