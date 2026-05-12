/** ValueRef node renderer. v0.15 Phase 3.1. */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function ValueRefNode(props: NodeProps<BaseNodeData>) {
  return <BaseNode {...props} chrome={{}} />;
}
