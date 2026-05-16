/**
 * Per-kind inspector for ``content`` nodes. v0.15 Phase 2.9.
 * Direct-selection variant of the ContentFields used inside
 * ServiceInspector's CompositionList rows.
 */
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { ContentFields } from "../service/ContentFields";
import type { KindInspectorProps } from "../types";

export function ContentInspector(props: KindInspectorProps) {
  if (props.node.kind !== "content") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <ContentFields
        node={node}
        availableActors={props.availableActors ?? []}
        onPatchNode={props.onPatchNode}
      />
      <BodyField value={node.body ?? ""} onChange={(body) => props.onPatchNode({ body })} />
    </BaseInspector>
  );
}
