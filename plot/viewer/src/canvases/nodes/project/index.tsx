/**
 * Project anchor node renderer. v0.15 Phase 3.1.
 * Foundation-canvas central anchor — gets the thicker slate-600
 * border to distinguish it from other Foundation nodes.
 */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData, shouldShowKindTag } from "../BaseNode";

export function ProjectNode(props: NodeProps<BaseNodeData>) {
  return (
    <BaseNode
      {...props}
      chrome={{
        isAnchor: true,
        showKindTag: shouldShowKindTag(props.data.shape),
      }}
    />
  );
}
