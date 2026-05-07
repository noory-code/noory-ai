// Shared constants for SketchCanvas hooks. Kept tiny and dependency-
// free so any extracted hook can import without pulling React Flow
// types or types.ts transitively.

/**
 * v0.13 Phase 0: id reserved for the synthetic project anchor node
 * injected into Foundation / Actors / Services canvases. Never
 * written to canvas.json — the position lives in
 * ``ProjectDoc.anchors``.
 */
export const PROJECT_ANCHOR_ID = "__project_anchor__";

/**
 * Defaults for newly created nodes (drag-from-stencil, double-click
 * pane, paste-into-pane, "Add node here" menu). Per-kind presets
 * override these in SketchStencil; the defaults are the fallback
 * applied when no preset matches.
 */
export const DEFAULT_WIDTH = 180;
export const DEFAULT_HEIGHT = 80;
export const DEFAULT_COLOR = "#ffffff";
