/**
 * Per-kind inspector for ``note`` nodes (D-2026-06-17-F). A canvas-global
 * ambient memo on the Feature canvas — a human-read guide AND context the AI
 * always lays under its work. Lean: a title (shared header) + the ``body``
 * memo text. A note is **edgeless** — it never connects to anything.
 */
import { useTranslation } from "react-i18next";
import type { NoteJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import type { KindInspectorProps } from "../types";

export function NoteInspector(props: KindInspectorProps) {
  if (props.node.kind !== "note") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <NoteFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface NoteFieldsProps {
  node: NoteJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function NoteFields({ node, onPatchNode }: NoteFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-warn-line bg-warn-soft/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-warn-fg">
        {t("kind.note")}
      </div>
      <p className="mb-2 text-[11px] leading-snug text-fg-muted">
        {t("inspector.note.ambientHint")}
      </p>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
