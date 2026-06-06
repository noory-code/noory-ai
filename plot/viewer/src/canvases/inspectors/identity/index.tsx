/**
 * Per-kind inspector for ``identity`` Foundation nodes. v0.17 Phase 1
 * (D-2026-05-16-A): every typed-text field value (``description`` /
 * ``do`` / ``dont`` / ``body``) is an MD-formatted string in JSON.
 * The DetailsSection MD-editor surface is hidden — JSON SSOT means
 * no MD file editing.
 */
import { useTranslation } from "react-i18next";
import type { IdentityJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function IdentityInspector(props: KindInspectorProps) {
  if (props.node.kind !== "identity") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <IdentityFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface IdentityFieldsProps {
  node: IdentityJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function IdentityFields({ node, onPatchNode }: IdentityFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-violet-200 bg-violet-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-violet-700">
        {t("kind.identity")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.description")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.description")}
        </span>
        <MdTextarea
          value={node.description ?? ""}
          onChange={(v) => onPatchNode({ description: v })}
          placeholder="이 속성이 어떻게 드러나는가"
        />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
