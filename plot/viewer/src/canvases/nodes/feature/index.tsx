/** Feature node renderer (D-2026-06-17-D). A capability under a service; the
 *  sole drill target. Lean chrome — the inspector carries the one-line
 *  ``proposed`` summary, the drill opens its Feature canvas. */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function FeatureNode(props: NodeProps<BaseNodeData>) {
  return <BaseNode {...props} chrome={{}} />;
}
