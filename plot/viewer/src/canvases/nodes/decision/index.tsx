/**
 * Decision node renderer. v0.28.0 (D-2026-05-30-C).
 *
 * A flowchart decision: rendered as a diamond (forced at the
 * ``effectiveShape`` layer in BaseNode, the same way Symbol kinds
 * force a circle — the shape IS the semantic). The label is the
 * question (검증? / 방식 선택?); the branches are user-drawn labelled
 * outgoing edges, so the node itself carries no per-kind chrome.
 */
import type { NodeProps } from "reactflow";
import { BaseNode, type BaseNodeData } from "../BaseNode";

export function DecisionNode(props: NodeProps<BaseNodeData>) {
  // No kind tag: the diamond silhouette has no flat top-left corner to
  // host it (shouldShowKindTag returns false for diamond anyway).
  return <BaseNode {...props} />;
}
