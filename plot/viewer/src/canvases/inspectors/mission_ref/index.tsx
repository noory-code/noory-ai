/**
 * Per-kind inspector for ``mission_ref`` nodes. v0.15 Phase 2.7.
 * Renders the shared ``FoundationRefBlock`` body — no editable typed
 * fields, only the master-display + orphan handling.
 */
import { BaseInspector } from "../BaseInspector";
import { FoundationRefBlock } from "../shared/FoundationRefBlock";
import type { KindInspectorProps } from "../types";

export function MissionRefInspector(props: KindInspectorProps) {
  if (props.node.kind !== "mission_ref") return null;
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
