/**
 * Category node renderer. v0.15 Phase 3.1.
 * Per v0.12.4 — category labels read as group headers, so they align
 * left instead of center. Also gets the kind tag.
 */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData, shouldShowKindTag } from "../BaseNode";

export function CategoryNode(props: NodeProps<BaseNodeData>) {
  return (
    <BaseNode
      {...props}
      chrome={{
        showKindTag: shouldShowKindTag(props.data.shape),
        labelAlignLeft: true,
      }}
    />
  );
}
