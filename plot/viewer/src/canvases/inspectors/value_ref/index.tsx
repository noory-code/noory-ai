/**
 * Per-kind inspector for ``value_ref`` nodes. v0.15 Phase 2.7.
 */
import { BaseInspector } from "../BaseInspector";
import { FoundationRefBlock } from "../shared/FoundationRefBlock";
import type { KindInspectorProps } from "../types";

export function ValueRefInspector(props: KindInspectorProps) {
  if (props.node.kind !== "value_ref") return null;
  const node = props.node;
  return (
    <BaseInspector {...props}>
      <FoundationRefBlock
        node={node}
        availableMissions={props.availableMissions ?? []}
        availableValues={props.availableValues ?? []}
        availableIdentities={props.availableIdentities ?? []}
        onRepickFoundationRef={props.onRepickFoundationRef}
        onDeleteNode={props.onDeleteNode}
      />
    </BaseInspector>
  );
}
