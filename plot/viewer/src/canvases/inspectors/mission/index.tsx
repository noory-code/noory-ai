/**
 * Per-kind inspector for ``mission`` Foundation nodes. v0.43.0
 * (D-2026-06-06-C): mission = ``label`` (the declaration) + ``body``
 * (free Markdown). The typed fields what_we_do / why / direction were
 * removed — a mission is one declaration, written as the label + body.
 * The DetailsSection MD-editor surface stays hidden (JSON SSOT).
 */
import { useTranslation } from "react-i18next";
import type { MissionJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function MissionInspector(props: KindInspectorProps) {
  if (props.node.kind !== "mission") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <MissionFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface MissionFieldsProps {
  node: MissionJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function MissionFields({ node, onPatchNode }: MissionFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-accent bg-accent-soft/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-accent-fg">
        {t("kind.mission")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-fg">
          {t("inspector.field.statement")}
        </span>
        <span className="ml-1 text-[10px] text-fg-muted">
          — {t("inspector.fieldHint.statement")}
        </span>
        <MdTextarea
          value={node.statement ?? ""}
          onChange={(v) => onPatchNode({ statement: v })}
          placeholder="이 프로젝트가 무엇을 위해 존재하는지 한 문장으로"
        />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
