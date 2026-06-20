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
// v0.24.15 (D-2026-05-24-A) — reduced from 140×60 to 80×36, follow-up to
// D-2026-05-17-N. Tighter default keeps Services / FeatureDetail canvases
// readable without overflow on hub-spoke layouts and matches the new label-
// plus-icon-only baseline. Existing nodes keep their stored width/height in
// canvas.json; only the next stencil-drop or pane-double-click creates an
// 80×36 node.
export const DEFAULT_WIDTH = 80;
export const DEFAULT_HEIGHT = 36;
export const DEFAULT_COLOR = "#ffffff";
