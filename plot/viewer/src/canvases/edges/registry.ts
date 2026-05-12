/**
 * Custom React Flow edge types. Mirrors ``nodes/registry.ts`` —
 * a single ``EDGE_TYPES`` map consumed by ``SketchCanvas`` 's
 * ``edgeTypes`` prop. Adding a new edge type goes through this file
 * so the wiring stays SSOT.
 */
import type { EdgeTypes } from "reactflow";
import { SelfLoopEdge } from "./SelfLoopEdge";

export const EDGE_TYPES: EdgeTypes = {
  selfLoop: SelfLoopEdge,
};
