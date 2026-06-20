/** Note node renderer (D-2026-06-17-F). An ambient canvas-global memo on the
 *  Feature canvas — edgeless. Lean chrome; the inspector carries the body. */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function NoteNode(props: NodeProps<BaseNodeData>) {
  return <BaseNode {...props} chrome={{}} />;
}
