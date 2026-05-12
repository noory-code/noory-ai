/**
 * Actor node renderer. v0.15 Phase 3.1.
 * No kind tag — the user-icon + colour identify actors clearly.
 */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function ActorNode(props: NodeProps<BaseNodeData>) {
  return <BaseNode {...props} chrome={{}} />;
}
