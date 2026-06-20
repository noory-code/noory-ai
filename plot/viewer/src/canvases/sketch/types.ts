// Shared types for sketch hooks. Kept React-free so hooks can import
// without dragging the whole SketchCanvas surface into their type
// graph. (Avoids the SketchCanvas → hook → SketchCanvas cycle when
// every extracted hook needs NodePreset.)
import type { NodeKind, SketchNode as DocNode } from "../../types";

/**
 * Optional stencil preset used when a node is dropped from the
 * palette or created via the toolbar. ``undefined`` → caller gets a
 * plain rounded rectangle with the defaults from ``constants.ts``.
 */
export interface NodePreset {
  shape: DocNode["shape"];
  color: string;
  width?: number;
  height?: number;
  icon?: string | null;
  label?: string;
  /** v0.2: typed node kind. Used to constrain layer on drop and for AI. */
  kind?: NodeKind | null;
  /**
   * v0.2 multi-canvas: set on actor_ref drops once the picker has
   * resolved which actor in the Actor canvas this node points at.
   */
  ref_actor_id?: string | null;
}

/**
 * Drag/drop intermediate state — set when a stencil drop opens a
 * picker modal, cleared when the user resolves or cancels the
 * modal.
 */
export type PendingActorRef =
  | {
      mode: "create";
      preset: NodePreset;
      pos: { x: number; y: number };
      resolved: { parentId: string | null };
    }
  | { mode: "rewire"; nodeId: string };

// PendingFoundationRef removed 2026-06-20 (D-2026-06-20-G) — the foundation
// refs + their picker are retired; refs are service-inspector chips now.
