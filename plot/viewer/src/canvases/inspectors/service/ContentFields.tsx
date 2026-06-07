/**
 * ContentFields — typed-field editor for ``content`` composition rows.
 * Rendered inside a CompositionRow's expanded panel.
 *
 * Carries format + producer_actor_id + consumer_actor_id (both pickers
 * select from ``availableActors`` so the pick UX matches actor_ref).
 */
import { useTranslation } from "react-i18next";
import type { ContentJson } from "../../../domain";
import type { SketchNode } from "../../../types";

export interface ContentFieldsProps {
  node: ContentJson;
  availableActors: SketchNode[];
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

export function ContentFields({ node, availableActors, onPatchNode }: ContentFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="text-xs">
      <label className="mb-2 block">
        <span className="font-semibold text-fg">{t("inspector.field.format")}</span>
        <input
          type="text"
          value={node.format ?? ""}
          onChange={(e) => onPatchNode({ format: e.target.value })}
          placeholder="JSON / MD / image / token …"
          className="mt-1 w-full rounded border border-line-strong px-2 py-1 font-mono text-sm focus:border-special focus:outline-none"
        />
      </label>
      <ContentActorPicker
        label={t("inspector.field.producer")}
        hint={t("inspector.fieldHint.producer")}
        actorId={node.producer_actor_id ?? null}
        availableActors={availableActors}
        onChange={(id) => onPatchNode({ producer_actor_id: id })}
      />
      <ContentActorPicker
        label={t("inspector.field.consumer")}
        hint={t("inspector.fieldHint.consumer")}
        actorId={node.consumer_actor_id ?? null}
        availableActors={availableActors}
        onChange={(id) => onPatchNode({ consumer_actor_id: id })}
      />
    </div>
  );
}

interface ContentActorPickerProps {
  label: string;
  hint: string;
  actorId: string | null;
  availableActors: SketchNode[];
  onChange: (id: string | null) => void;
}

function ContentActorPicker({
  label,
  hint,
  actorId,
  availableActors,
  onChange,
}: ContentActorPickerProps) {
  const { t } = useTranslation();
  return (
    <label className="mb-2 block">
      <span className="font-semibold text-fg">{label}</span>
      <span className="ml-1 text-[10px] text-fg-muted">— {hint}</span>
      <select
        value={actorId ?? ""}
        onChange={(e) => onChange(e.target.value || null)}
        className="mt-1 w-full rounded border border-line-strong px-2 py-1 focus:border-special focus:outline-none"
      >
        <option value="">{t("inspector.unset")}</option>
        {availableActors.map((a) => (
          <option key={a.id} value={a.id}>
            {a.label || a.id}
          </option>
        ))}
      </select>
    </label>
  );
}
