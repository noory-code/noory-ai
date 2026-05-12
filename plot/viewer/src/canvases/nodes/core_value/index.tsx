/** CoreValue Foundation node renderer. v0.15 Phase 3.1. */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData, shouldShowKindTag } from "../BaseNode";

export function CoreValueNode(props: NodeProps<BaseNodeData>) {
  return (
    <BaseNode
      {...props}
      chrome={{ showKindTag: shouldShowKindTag(props.data.shape) }}
    />
  );
}
