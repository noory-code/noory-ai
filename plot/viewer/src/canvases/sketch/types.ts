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
  /**
   * v0.10 Step 3: set on Foundation ref drops once the picker resolves
   * the master node from the Foundation canvas.
   */
  ref_mission_id?: string | null;
  ref_value_id?: string | null;
  ref_identity_id?: string | null;
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

export type PendingFoundationRef =
  | {
      mode: "create";
      refKind: "mission_ref" | "value_ref" | "identity_ref";
      preset: NodePreset;
      pos: { x: number; y: number };
      resolved: { parentId: string | null };
    }
  | {
      mode: "rewire";
      refKind: "mission_ref" | "value_ref" | "identity_ref";
      nodeId: string;
    };
