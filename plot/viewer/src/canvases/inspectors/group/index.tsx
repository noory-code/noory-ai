/**
 * Per-kind inspector for ``group`` nodes (a flow-chunk container).
 * v0.29.0 (D-2026-05-30-I).
 *
 * A group carries its label (the chunk name, edited via the header) +
 * its members (`member_ids`, shown read-only as a count — membership
 * is edited on the canvas via multi-select → Group) + optional body.
 */
import { useTranslation } from "react-i18next";
import type { GroupJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import type { KindInspectorProps } from "../types";

export function GroupInspector(props: KindInspectorProps) {
  if (props.node.kind !== "group") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <GroupFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface GroupFieldsProps {
  node: GroupJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function GroupFields({ node, onPatchNode }: GroupFieldsProps) {
  const { t } = useTranslation();
  const count = node.member_ids?.length ?? 0;
  return (
    <div className="mb-4 rounded border border-slate-300 bg-slate-50/60 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-slate-600">
        {t("kind.group")}
      </div>
      <p className="mb-2 text-[11px] leading-snug text-slate-500">
        {t("inspector.group.memberCount", { count })}
      </p>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
