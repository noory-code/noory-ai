/** Content composition node renderer. v0.15 Phase 3.1. */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function ContentNode(props: NodeProps<BaseNodeData>) {
  return <BaseNode {...props} chrome={{}} />;
}
