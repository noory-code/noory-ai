/**
 * Per-kind inspector for ``identity_ref`` nodes. v0.15 Phase 2.7.
 * v0.24.x (D-2026-05-17-M) — adds ``notes_in_context``.
 */
import { useTranslation } from "react-i18next";

import { BaseInspector } from "../BaseInspector";
import { FoundationRefBlock } from "../shared/FoundationRefBlock";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function IdentityRefInspector(props: KindInspectorProps) {
  const { t } = useTranslation();
  if (props.node.kind !== "identity_ref") return null;
  const node = props.node;
  const { onPatchNode } = props;
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
      <label className="mb-4 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.notesInContext")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.notesInContext")}
        </span>
        <MdTextarea
          value={node.notes_in_context ?? ""}
          onChange={(v) => onPatchNode({ notes_in_context: v })}
        />
      </label>
    </BaseInspector>
  );
}
