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
import { MdTextarea } from "../shared/MdTextarea";
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
        <div className="mb-4 rounded border border-special bg-special-soft/40 p-2 text-[11px]">
          <div className="mb-1 font-semibold uppercase tracking-wide text-special-fg">References</div>
          <div className="text-fg">
            <span className="text-fg-muted">Actor:</span>{" "}
            <span className="font-medium">{refTarget.label || refTarget.id}</span>
          </div>
          <div className="mt-0.5 font-mono text-[10px] text-fg-faint">{node.ref_actor_id}</div>
        </div>
      )}
      {isOrphan && (
        <div className="mb-4 rounded border border-danger bg-danger-soft p-2 text-[11px]">
          <div className="mb-1 font-semibold uppercase tracking-wide text-danger-fg">
            ⚠ Orphan — actor not found
          </div>
          <div className="mb-2 font-mono text-[10px] text-fg-muted">
            ref_actor_id: {node.ref_actor_id ?? "—"}
          </div>
          <div className="flex gap-2">
            {props.onRepickActorRef && (
              <button
                type="button"
                onClick={() => props.onRepickActorRef?.(node.id)}
                className="rounded border border-danger bg-surface px-2 py-1 text-[11px] font-medium text-danger-fg hover:bg-danger-soft"
              >
                Re-pick…
              </button>
            )}
            <button
              type="button"
              onClick={() => props.onDeleteNode(node.id)}
              className="rounded px-2 py-1 text-[11px] text-fg-secondary hover:bg-surface-subtle"
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
    <div className="mb-4 rounded border border-special bg-special-soft/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-special-fg">
        {t("inspector.valueFlowHeader")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-ok-fg">
          {t("inspector.field.gives")}
        </span>
        <span className="ml-1 text-[10px] text-fg-muted">— {t("inspector.fieldHint.gives")}</span>
        <MdTextarea
          value={node.gives ?? ""}
          onChange={(v) => onPatchNode({ gives: v })}
          placeholder="콘텐츠 / 시간 / 결제 / 주의 …"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-special-fg">
          {t("inspector.field.receives")}
        </span>
        <span className="ml-1 text-[10px] text-fg-muted">
          — {t("inspector.fieldHint.receives")}
        </span>
        <MdTextarea
          value={node.receives ?? ""}
          onChange={(v) => onPatchNode({ receives: v })}
          placeholder="피드백 / 신뢰 / 접근권 / 즐거움 …"
        />
      </label>
    </div>
  );
}
