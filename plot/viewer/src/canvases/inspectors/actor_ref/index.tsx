/**
 * Per-kind inspector for ``actor_ref`` nodes — references an actor
 * master on the Actors canvas. Renders gives / receives value-flow
 * fields plus a reference display (or orphan-warning + re-pick when
 * the master is missing).
 *
 * v0.15 Phase 2.7.
 */
import { useTranslation } from "react-i18next";
import type { ActorRefJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import type { KindInspectorProps } from "../types";

export function ActorRefInspector(props: KindInspectorProps) {
  if (props.node.kind !== "actor_ref") return null;
  const node = props.node;
  const refTarget =
    node.ref_actor_id && props.availableActors
      ? props.availableActors.find((n) => n.id === node.ref_actor_id) ?? null
      : null;
  const isOrphan = !node.ref_actor_id || refTarget === null;
  return (
    <BaseInspector {...props}>
      <ActorRefFields node={node} onPatchNode={props.onPatchNode} />
      {!isOrphan && refTarget && (
        <div className="mb-4 rounded border border-pink-200 bg-pink-50/40 p-2 text-[11px]">
          <div className="mb-1 font-semibold uppercase tracking-wide text-pink-700">References</div>
          <div className="text-slate-700">
            <span className="text-slate-500">Actor:</span>{" "}
            <span className="font-medium">{refTarget.label || refTarget.id}</span>
          </div>
          <div className="mt-0.5 font-mono text-[10px] text-slate-400">{node.ref_actor_id}</div>
        </div>
      )}
      {isOrphan && (
        <div className="mb-4 rounded border border-red-300 bg-red-50 p-2 text-[11px]">
          <div className="mb-1 font-semibold uppercase tracking-wide text-red-700">
            ⚠ Orphan — actor not found
          </div>
          <div className="mb-2 font-mono text-[10px] text-slate-500">
            ref_actor_id: {node.ref_actor_id ?? "—"}
          </div>
          <div className="flex gap-2">
            {props.onRepickActorRef && (
              <button
                type="button"
                onClick={() => props.onRepickActorRef?.(node.id)}
                className="rounded border border-red-300 bg-white px-2 py-1 text-[11px] font-medium text-red-700 hover:bg-red-100"
              >
                Re-pick…
              </button>
            )}
            <button
              type="button"
              onClick={() => props.onDeleteNode(node.id)}
              className="rounded px-2 py-1 text-[11px] text-slate-600 hover:bg-slate-100"
            >
              Delete
            </button>
          </div>
        </div>
      )}
    </BaseInspector>
  );
}

interface ActorRefFieldsProps {
  node: ActorRefJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function ActorRefFields({ node, onPatchNode }: ActorRefFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-pink-200 bg-pink-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-pink-700">
        {t("inspector.valueFlowHeader")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-emerald-700">
          {t("inspector.field.gives")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.gives")}</span>
        <textarea
          rows={2}
          value={node.gives ?? ""}
          onChange={(e) => onPatchNode({ gives: e.target.value })}
          placeholder="콘텐츠 / 시간 / 결제 / 주의 …"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-emerald-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-violet-700">
          {t("inspector.field.receives")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.receives")}
        </span>
        <textarea
          rows={2}
          value={node.receives ?? ""}
          onChange={(e) => onPatchNode({ receives: e.target.value })}
          placeholder="피드백 / 신뢰 / 접근권 / 즐거움 …"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-violet-600 focus:outline-none"
        />
      </label>
    </div>
  );
}
