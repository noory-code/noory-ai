/** Entity node renderer (D-2026-06-17-I). A product data object on the
 *  Entities canvas (글 / 댓글 / 사용자) — symmetric to ``actor``. Lean chrome
 *  (rounded rectangle); the inspector carries the one-line ``summary``. */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function EntityNode(props: NodeProps<BaseNodeData>) {
  return <BaseNode {...props} chrome={{}} />;
}
