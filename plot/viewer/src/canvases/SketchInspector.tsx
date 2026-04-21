import { useMemo } from "react";
import type { SketchNode } from "../types";

export interface SketchInspectorProps {
  /** Currently selected node. Null → panel shows empty state. */
  node: SketchNode | null;
  /** All nodes so we can find composition children of a Service. */
  allNodes: SketchNode[];
  /**
   * v0.2 multi-canvas: actors across all canvases. Lets the Inspector
   * detect orphan ``actor_ref`` nodes without false positives caused by
   * the per-tab filtered view.
   */
  availableActors: SketchNode[];
  /** Patch the selected node's own fields. */
  onPatchNode: (patch: Partial<SketchNode>) => void;
  /** Create a new rule/content child under ``parentId``. */
  onAddChild: (parentId: string, kind: "rule" | "content") => void;
  /** Patch an existing child. */
  onPatchChild: (childId: string, patch: Partial<SketchNode>) => void;
  /** Remove a child. */
  onRemoveChild: (childId: string) => void;
  /** Open the ActorRefPicker in rewire mode to repoint an actor_ref. */
  onRepickActorRef: (nodeId: string) => void;
  /** Remove a node entirely (used by the orphan actor_ref "Delete" action). */
  onDeleteNode: (nodeId: string) => void;
  /** Close the panel. */
  onClose: () => void;
}

/**
 * Right-side detail panel.
 *
 * v0.2 correction (2026-04-20): composition elements (rules, contents)
 * are edited here, not as nodes on the canvas.
 */
export function SketchInspector({
  node,
  allNodes,
  availableActors,
  onPatchNode,
  onAddChild,
  onPatchChild,
  onRemoveChild,
  onRepickActorRef,
  onDeleteNode,
  onClose,
}: SketchInspectorProps) {
  const rules = useMemo(
    () => (node ? allNodes.filter((n) => n.parent_id === node.id && n.kind === "rule") : []),
    [node, allNodes],
  );
  const contents = useMemo(
    () => (node ? allNodes.filter((n) => n.parent_id === node.id && n.kind === "content") : []),
    [node, allNodes],
  );

  if (!node) {
    return (
      <aside className="pointer-events-auto absolute right-0 top-0 z-10 flex h-full w-80 flex-col border-l border-slate-200 bg-white/95 p-4 text-sm text-slate-500 shadow-sm backdrop-blur">
        <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
          Inspector
        </div>
        <div className="mt-4 italic">Select a node to see details.</div>
      </aside>
    );
  }

  // v0.2 multi-canvas (2026-04-21): Mission / Core Value / Identity are
  // now their own node kinds on the Core canvas, so the per-root text
  // fields were removed. ``showsIdentity`` kept only for historical
  // reference; the block that used it is gone.
  const canToggleRoot =
    !node.parent_id && (node.kind === "actor" || node.kind === "service");
  const refTarget =
    node.kind === "actor_ref" && node.ref_actor_id
      ? availableActors.find((n) => n.id === node.ref_actor_id) ?? null
      : null;
  const isOrphanActorRef =
    node.kind === "actor_ref" && (!node.ref_actor_id || refTarget === null);

  return (
    <aside className="pointer-events-auto absolute right-0 top-0 z-10 flex h-full w-80 flex-col border-l border-slate-200 bg-white/95 shadow-sm backdrop-blur">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2">
        <div className="flex items-center gap-2">
          <span
            className="inline-block h-3 w-3 shrink-0 rounded border border-slate-300"
            style={{ backgroundColor: node.color || "#ffffff" }}
            aria-hidden
          />
          <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
            {node.kind === "core"
              ? "Core Root"
              : node.is_root && node.kind === "actor"
                ? "Actor Root"
                : node.is_root && node.kind === "service"
                  ? "Service Root"
                  : node.kind ?? "Node"}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {/* Delete — available for any non-root, non-core node */}
          {node.kind !== "core" && !node.is_root && (
            <button
              type="button"
              onClick={() => {
                if (window.confirm(`Delete "${node.label || node.id}"?`)) {
                  onDeleteNode(node.id);
                }
              }}
              aria-label="Delete node"
              className="rounded px-2 text-[10px] text-rose-600 hover:bg-rose-50"
              title="Delete node"
            >
              ✕ delete
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            aria-label="Close inspector"
            className="rounded px-2 text-slate-400 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto p-3">
        {/* Label */}
        <label className="mb-3 block">
          <span className="text-xs font-semibold text-slate-600">Label</span>
          <input
            type="text"
            value={node.label}
            onChange={(e) => onPatchNode({ label: e.target.value })}
            className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
          />
        </label>

        {/* Body */}
        <label className="mb-4 block">
          <span className="text-xs font-semibold text-slate-600">Description</span>
          <textarea
            value={node.body}
            onChange={(e) => onPatchNode({ body: e.target.value })}
            rows={3}
            className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
            placeholder="Longer description, markdown supported"
          />
        </label>

        {/* Root toggle — only for top-level actor / service */}
        {canToggleRoot && (
          <label className="mb-4 flex items-center gap-2 text-xs text-slate-700">
            <input
              type="checkbox"
              checked={node.is_root}
              onChange={(e) => onPatchNode({ is_root: e.target.checked })}
              className="accent-indigo-600"
            />
            <span>
              Mark as <strong>{node.kind === "actor" ? "Actor Root" : "Service Root"}</strong>{" "}
              (centre of its tree)
            </span>
          </label>
        )}

        {/* Actor reference — link (or broken link) back to the Actor canvas node. */}
        {node.kind === "actor_ref" && !isOrphanActorRef && refTarget && (
          <div className="mb-4 rounded border border-pink-200 bg-pink-50/40 p-2 text-[11px]">
            <div className="mb-1 font-semibold uppercase tracking-wide text-pink-700">
              References
            </div>
            <div className="text-slate-700">
              <span className="text-slate-500">Actor:</span>{" "}
              <span className="font-medium">{refTarget.label || refTarget.id}</span>
            </div>
            <div className="mt-0.5 font-mono text-[10px] text-slate-400">
              {node.ref_actor_id}
            </div>
          </div>
        )}
        {node.kind === "actor_ref" && isOrphanActorRef && (
          <div className="mb-4 rounded border border-red-300 bg-red-50 p-2 text-[11px]">
            <div className="mb-1 font-semibold uppercase tracking-wide text-red-700">
              ⚠ Orphan — actor not found
            </div>
            <div className="mb-2 font-mono text-[10px] text-slate-500">
              ref_actor_id: {node.ref_actor_id ?? "—"}
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => onRepickActorRef(node.id)}
                className="rounded border border-red-300 bg-white px-2 py-1 text-[11px] font-medium text-red-700 hover:bg-red-100"
              >
                Re-pick…
              </button>
              <button
                type="button"
                onClick={() => onDeleteNode(node.id)}
                className="rounded px-2 py-1 text-[11px] text-slate-600 hover:bg-slate-100"
              >
                Delete
              </button>
            </div>
          </div>
        )}

        {/* Service-specific composition */}
        {node.kind === "service" && (
          <>
            <CompositionList
              title="Rules"
              subtitle="policies, constraints, SLAs"
              items={rules}
              onAdd={() => onAddChild(node.id, "rule")}
              onPatch={onPatchChild}
              onRemove={onRemoveChild}
            />
            <CompositionList
              title="Contents"
              subtitle="artifacts, outputs, assets"
              items={contents}
              onAdd={() => onAddChild(node.id, "content")}
              onPatch={onPatchChild}
              onRemove={onRemoveChild}
            />
          </>
        )}

        {/* Actor placeholder — v0.3 fields land here */}
        {node.kind === "actor" && !node.is_root && (
          <div className="rounded border border-dashed border-slate-300 p-3 text-xs italic text-slate-400">
            Actor composition (permissions / capabilities / goals / state) lands in v0.3.
          </div>
        )}
      </div>
    </aside>
  );
}

interface CompositionListProps {
  title: string;
  subtitle: string;
  items: SketchNode[];
  onAdd: () => void;
  onPatch: (childId: string, patch: Partial<SketchNode>) => void;
  onRemove: (childId: string) => void;
}

function CompositionList({
  title,
  subtitle,
  items,
  onAdd,
  onPatch,
  onRemove,
}: CompositionListProps) {
  return (
    <div className="mb-4">
      <div className="mb-1 flex items-baseline justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-700">{title}</div>
          <div className="text-[10px] italic text-slate-400">{subtitle}</div>
        </div>
        <button
          type="button"
          onClick={onAdd}
          className="rounded bg-slate-900 px-2 py-0.5 text-[10px] font-medium text-white hover:bg-slate-700"
        >
          + Add
        </button>
      </div>
      {items.length === 0 ? (
        <div className="rounded border border-dashed border-slate-200 p-2 text-[11px] italic text-slate-400">
          (none)
        </div>
      ) : (
        <ul className="space-y-1">
          {items.map((item) => (
            <li
              key={item.id}
              className="group flex items-start gap-1 rounded border border-slate-200 bg-white px-2 py-1"
            >
              <div className="flex-1">
                <input
                  type="text"
                  value={item.label}
                  onChange={(e) => onPatch(item.id, { label: e.target.value })}
                  placeholder="Name"
                  className="w-full border-none bg-transparent text-xs font-medium text-slate-800 focus:outline-none"
                />
                <textarea
                  value={item.body}
                  onChange={(e) => onPatch(item.id, { body: e.target.value })}
                  placeholder="Optional detail"
                  rows={1}
                  className="mt-0.5 w-full resize-y border-none bg-transparent text-[11px] text-slate-600 focus:outline-none"
                />
              </div>
              <button
                type="button"
                onClick={() => {
                  if (window.confirm(`Remove "${item.label || "(untitled)"}"?`)) {
                    onRemove(item.id);
                  }
                }}
                className="rounded px-1 text-[10px] text-rose-600 opacity-0 hover:bg-rose-50 group-hover:opacity-100"
                aria-label="Remove"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
