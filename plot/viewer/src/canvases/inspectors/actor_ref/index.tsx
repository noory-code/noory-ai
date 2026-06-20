/**
 * Per-kind inspector for ``actor_ref`` nodes — a **read-only anchor**
 * (D-2026-06-19-I). It marks the flow's subject ("who starts / who can") on the
 * Feature canvas; it does NOT edit role or value here. The former per-service
 * stake fields (gives / receives / motivation / pain) are retired — role-level
 * value lives on the Actors edges, aggregate value on the service. Shows which
 * actor master it points at (+ side), with an orphan re-pick / delete path when
 * the master is missing.
 */
import { useTranslation } from "react-i18next";
import { BaseInspector } from "../BaseInspector";
import type { KindInspectorProps } from "../types";

export function ActorRefInspector(props: KindInspectorProps) {
  if (props.node.kind !== "actor_ref") return null;
  const node = props.node;
  const { t } = useTranslation();
  const refTarget =
    node.ref_actor_id && props.availableActors
      ? (props.availableActors.find((n) => n.id === node.ref_actor_id) ?? null)
      : null;
  const isOrphan = !node.ref_actor_id || refTarget === null;
  return (
    <BaseInspector {...props}>
      {!isOrphan && refTarget && (
        <div className="mb-4 rounded border border-special bg-special-soft/40 p-2 text-[11px]">
          <div className="mb-1 font-semibold uppercase tracking-wide text-special-fg">
            {t("inspector.actorRef.anchorHeader")}
          </div>
          <div className="text-fg">
            <span className="text-fg-muted">{t("inspector.actorRef.actor")}:</span>{" "}
            <span className="font-medium">{refTarget.label || refTarget.id}</span>
            {node.side && <span className="ml-2 text-[10px] text-fg-muted">({node.side})</span>}
          </div>
          <div className="mt-0.5 font-mono text-[10px] text-fg-faint">{node.ref_actor_id}</div>
          <p className="mt-2 leading-snug text-fg-muted">{t("inspector.actorRef.readOnlyHint")}</p>
        </div>
      )}
      {isOrphan && (
        <div className="mb-4 rounded border border-danger bg-danger-soft p-2 text-[11px]">
          <div className="mb-1 font-semibold uppercase tracking-wide text-danger-fg">
            {t("inspector.actorRef.orphan")}
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
                {t("inspector.actorRef.repick")}
              </button>
            )}
            <button
              type="button"
              onClick={() => props.onDeleteNode(node.id)}
              className="rounded px-2 py-1 text-[11px] text-fg-secondary hover:bg-surface-subtle"
            >
              {t("inspector.actorRef.delete")}
            </button>
          </div>
        </div>
      )}
    </BaseInspector>
  );
}
