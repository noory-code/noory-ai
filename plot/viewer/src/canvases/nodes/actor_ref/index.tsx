/**
 * ActorRef node renderer. v0.15 Phase 3.1.
 * Same chrome as Actor — colour comes from the referenced actor's
 * side, not the kind itself.
 */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function ActorRefNode(props: NodeProps<BaseNodeData>) {
  return <BaseNode {...props} chrome={{}} />;
}
