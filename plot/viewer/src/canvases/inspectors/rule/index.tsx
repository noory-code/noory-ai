/**
 * Per-kind inspector for ``rule`` nodes. v0.15 Phase 2.9.
 *
 * Rule editing primarily happens inside the parent service's
 * CompositionList row. When a rule node is selected directly, this
 * inspector renders the same RuleFields panel inside BaseInspector
 * chrome — so direct selection of a rule doesn't dead-end.
 */
import { BaseInspector } from "../BaseInspector";
import { RuleFields } from "../service/RuleFields";
import type { KindInspectorProps } from "../types";

export function RuleInspector(props: KindInspectorProps) {
  if (props.node.kind !== "rule") return null;
  const node = props.node;
  return (
    <BaseInspector {...props}>
      <RuleFields
        node={node}
        availableActors={props.availableActors ?? []}
        onPatchNode={props.onPatchNode}
      />
    </BaseInspector>
  );
}
