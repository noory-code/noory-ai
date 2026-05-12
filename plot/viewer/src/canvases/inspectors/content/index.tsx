/**
 * Per-kind inspector for ``content`` nodes. v0.15 Phase 2.9.
 * Direct-selection variant of the ContentFields used inside
 * ServiceInspector's CompositionList rows.
 */
import { BaseInspector } from "../BaseInspector";
import { ContentFields } from "../service/ContentFields";
import type { KindInspectorProps } from "../types";

export function ContentInspector(props: KindInspectorProps) {
  return (
    <BaseInspector {...props}>
      <ContentFields
        node={props.node}
        availableActors={props.availableActors ?? []}
        onPatchNode={props.onPatchNode}
      />
    </BaseInspector>
  );
}
