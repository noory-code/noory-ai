/**
 * Group node renderer. v0.29.0 (D-2026-05-30-I).
 *
 * A flow-chunk container. Renders as a labelled rounded box; the fold
 * (▾/▸) button + member count come from BaseNode's existing collapse
 * chrome, fed by ``member_ids`` in useNodesMemo. Collapsed → its
 * members are hidden (useNodesMemo) and only this node shows.
 */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function GroupNode(props: NodeProps<BaseNodeData>) {
  return <BaseNode {...props} chrome={{ labelAlignLeft: true }} />;
}
