/**
 * RuleFields — typed-field editor for ``rule`` composition rows.
 * Rendered inside a CompositionRow's expanded panel.
 *
 * Carries policy + enforcement + an actor-id → permission-string
 * map (free-form; suggested vocabulary C / R / U / D).
 */
import { useTranslation } from "react-i18next";
import type { RuleJson } from "../../../domain";
import type { SketchNode } from "../../../types";

export interface RuleFieldsProps {
  node: RuleJson;
  availableActors: SketchNode[];
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

export function RuleFields({ node, availableActors, onPatchNode }: RuleFieldsProps) {
  const { t } = useTranslation();
  const permissions = node.actor_permissions ?? {};
  const usedIds = new Set(Object.keys(permissions));
  const candidates = availableActors.filter((a) => !usedIds.has(a.id));
  return (
    <div className="text-xs">
      <label className="mb-2 block">
        <span className="font-semibold text-slate-700">{t("inspector.field.policy")}</span>
        <textarea
          rows={2}
          value={node.policy ?? ""}
          onChange={(e) => onPatchNode({ policy: e.target.value })}
          placeholder="이 룰이 강제하는 것"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 focus:border-stone-500 focus:outline-none"
        />
      </label>
      <label className="mb-2 block">
        <span className="font-semibold text-slate-700">{t("inspector.field.enforcement")}</span>
        <textarea
          rows={2}
          value={node.enforcement ?? ""}
          onChange={(e) => onPatchNode({ enforcement: e.target.value })}
          placeholder="어디서/어떻게 강제?"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 focus:border-stone-500 focus:outline-none"
        />
      </label>
      <div className="mt-2">
        <div className="mb-1 font-semibold text-slate-700">
          {t("inspector.field.actorPermissions")}
        </div>
        <div
          className="mb-1 text-[10px] italic text-slate-400"
          dangerouslySetInnerHTML={{
            __html: t("inspector.fieldHint.actorPermissionsShorthand"),
          }}
        />

        {Object.entries(permissions).length === 0 && (
          <div className="rounded border border-dashed border-slate-200 p-1.5 text-[11px] italic text-slate-400">
            {t("inspector.empty")}
          </div>
        )}
        <ul className="space-y-1">
          {Object.entries(permissions).map(([actorId, perm]) => {
            const actor = availableActors.find((a) => a.id === actorId);
            return (
              <li key={actorId} className="flex items-center gap-1">
                <span
                  className="flex-1 truncate text-[11px] text-slate-700"
                  title={actorId}
                >
                  {actor?.label || actorId}
                </span>
                <input
                  type="text"
                  value={perm}
                  onChange={(e) =>
                    onPatchNode({
                      actor_permissions: {
                        ...permissions,
                        [actorId]: e.target.value,
                      },
                    })
                  }
                  placeholder="CRUD"
                  className="w-20 rounded border border-slate-300 px-1.5 py-0.5 text-[11px] focus:border-stone-500 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => {
                    const next = { ...permissions };
                    delete next[actorId];
                    onPatchNode({ actor_permissions: next });
                  }}
                  className="rounded px-1 text-[10px] text-rose-600 hover:bg-rose-50"
                  aria-label={t("inspector.permissionRemove")}
                >
                  ✕
                </button>
              </li>
            );
          })}
        </ul>
        {candidates.length > 0 && (
          <select
            value=""
            onChange={(e) => {
              const id = e.target.value;
              if (!id) return;
              onPatchNode({
                actor_permissions: { ...permissions, [id]: "" },
              });
            }}
            className="mt-1 w-full rounded border border-slate-300 px-1.5 py-0.5 text-[11px] focus:border-stone-500 focus:outline-none"
          >
            <option value="">{t("inspector.addActorPermission")}</option>
            {candidates.map((a) => (
              <option key={a.id} value={a.id}>
                {a.label || a.id}
              </option>
            ))}
          </select>
        )}
      </div>
    </div>
  );
}
