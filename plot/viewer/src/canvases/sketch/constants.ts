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
// v0.24.2 (D-2026-05-17-N) — reduced from 180×80 to 140×60. Smaller
// default makes Foundation / Actors / Services canvases fit more
// nodes without scroll and reduces auto-layout overlap risk
// (smaller footprints sit comfortably inside the existing 32 px
// auto-layout padding). Existing nodes keep their own width/height
// stored in canvas.json; only the next stencil-drop or pane-double-
// click creates a 140×60 node.
export const DEFAULT_WIDTH = 140;
export const DEFAULT_HEIGHT = 60;
export const DEFAULT_COLOR = "#ffffff";
