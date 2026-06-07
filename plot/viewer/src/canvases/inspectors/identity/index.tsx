/**
 * Per-kind inspector for ``identity`` Foundation nodes.
 *
 * v0.17 Phase 1 (D-2026-05-16-A): ``description`` / ``body`` are MD-formatted
 * strings in JSON; the DetailsSection MD-editor surface is hidden (JSON SSOT).
 *
 * v0.44.0 (D-2026-06-07-A): identity is an **output** kind, so it carries
 * structural output-model fields — ``status`` (derive→confirm lifecycle) and
 * ``provenance`` (source node ids it was derived from). Both edit here.
 */
import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { IdentityJson, IdentityStatus } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

const STATUS_OPTIONS: readonly IdentityStatus[] = ["manual", "derived", "confirmed"];

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
    <div className="mb-4 rounded border border-special bg-special-soft/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-special-fg">
        {t("kind.identity")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-fg">
          {t("inspector.field.description")}
        </span>
        <span className="ml-1 text-[10px] text-fg-muted">
          — {t("inspector.fieldHint.description")}
        </span>
        <MdTextarea
          value={node.description ?? ""}
          onChange={(v) => onPatchNode({ description: v })}
          placeholder={t("inspector.fieldPlaceholder.identityDescription")}
        />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
      <StatusField
        value={node.status ?? "manual"}
        onChange={(status) => onPatchNode({ status })}
      />
      <ProvenanceField
        value={node.provenance ?? []}
        onChange={(provenance) => onPatchNode({ provenance })}
      />
    </div>
  );
}

interface StatusFieldProps {
  value: IdentityStatus;
  onChange: (status: IdentityStatus) => void;
}

function StatusField({ value, onChange }: StatusFieldProps) {
  const { t } = useTranslation();
  return (
    <label className="mb-2 block">
      <span className="text-xs font-semibold text-fg">
        {t("inspector.field.identityStatus")}
      </span>
      <span className="ml-1 text-[10px] text-fg-muted">
        — {t("inspector.fieldHint.identityStatus")}
      </span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as IdentityStatus)}
        className="mt-1 w-full rounded border border-line-strong px-2 py-1 text-sm focus:border-accent focus:outline-none"
      >
        {STATUS_OPTIONS.map((s) => (
          <option key={s} value={s}>
            {t(`inspector.identityStatus.${s}`)}
          </option>
        ))}
      </select>
    </label>
  );
}

interface ProvenanceFieldProps {
  value: string[];
  onChange: (provenance: string[]) => void;
}

function ProvenanceField({ value, onChange }: ProvenanceFieldProps) {
  const { t } = useTranslation();
  const [draft, setDraft] = useState("");

  const add = () => {
    const id = draft.trim();
    if (!id || value.includes(id)) return;
    onChange([...value, id]);
    setDraft("");
  };
  const remove = (id: string) => onChange(value.filter((v) => v !== id));

  return (
    <div className="mb-1 block">
      <span className="text-xs font-semibold text-fg">
        {t("inspector.field.provenance")}
      </span>
      <span className="ml-1 text-[10px] text-fg-muted">
        — {t("inspector.fieldHint.provenance")}
      </span>
      {value.length > 0 && (
        <div className="mt-1 flex flex-wrap gap-1">
          {value.map((id) => (
            <span
              key={id}
              className="inline-flex items-center gap-1 rounded bg-special-soft px-1.5 py-0.5 text-[11px] text-special-fg"
            >
              <span className="font-mono">{id}</span>
              <button
                type="button"
                onClick={() => remove(id)}
                aria-label={t("inspector.provenance.remove", { id })}
                className="text-special hover:text-special-fg"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      <div className="mt-1 flex gap-1">
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          placeholder={t("inspector.fieldPlaceholder.provenance")}
          className="min-w-0 flex-1 rounded border border-line-strong px-2 py-1 font-mono text-[11px] focus:border-accent focus:outline-none"
        />
        <button
          type="button"
          onClick={add}
          className="rounded border border-special px-2 py-1 text-[11px] text-special-fg hover:bg-special-soft"
        >
          {t("inspector.provenance.add")}
        </button>
      </div>
    </div>
  );
}
