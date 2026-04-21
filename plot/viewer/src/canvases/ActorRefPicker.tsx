import type { SketchNode } from "../types";
import { getIcon } from "./SketchIcons";

export interface ActorRefPickerProps {
  /**
   * Full node list so the picker can show both top-level and sub-actors
   * with their parent-chain label as context.
   */
  nodes: SketchNode[];
  /**
   * ``"create"`` (default) is the drag-drop flow: picking spawns a new
   * ``actor_ref`` node. ``"rewire"`` is the orphan-fix flow from the
   * Inspector: picking repoints an existing ref at the chosen actor.
   */
  mode?: "create" | "rewire";
  onPick: (actor: SketchNode) => void;
  onCancel: () => void;
}

/**
 * Modal opened when the user drops an ``actor_ref`` preset onto a Service
 * canvas, or re-picks an orphaned one from the Inspector. Lists every
 * actor from the Actor canvas; clicking one closes the modal and hands
 * back the pick.
 */
export function ActorRefPicker({ nodes, mode = "create", onPick, onCancel }: ActorRefPickerProps) {
  const actors = nodes.filter((n) => n.kind === "actor");
  const byId = new Map(nodes.map((n) => [n.id, n] as const));

  const parentLabel = (actor: SketchNode): string | null => {
    const p = actor.parent_id ? byId.get(actor.parent_id) : null;
    return p && p.kind === "actor" ? p.label : null;
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Pick an actor"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40"
      onClick={onCancel}
    >
      <div
        className="flex max-h-[70vh] w-96 flex-col overflow-hidden rounded-lg bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="border-b border-slate-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-slate-900">
            {mode === "rewire" ? "Re-pick actor" : "Reference an actor"}
          </h2>
          <p className="text-xs text-slate-500">
            {mode === "rewire"
              ? "Choose a replacement; the symbol on this canvas will update."
              : "The service canvas will show a symbol pointing at the original in the Actor canvas."}
          </p>
        </div>
        {actors.length === 0 ? (
          <div className="flex-1 px-4 py-8 text-center text-sm text-slate-500">
            No actors yet. Create one on the Actors canvas first.
          </div>
        ) : (
          <ul className="flex-1 divide-y divide-slate-100 overflow-y-auto">
            {actors.map((a) => {
              const Icon = getIcon(a.icon);
              const parent = parentLabel(a);
              return (
                <li key={a.id}>
                  <button
                    type="button"
                    onClick={() => onPick(a)}
                    className="flex w-full items-center gap-3 px-4 py-2.5 text-left hover:bg-slate-50"
                  >
                    <span
                      className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full"
                      style={{ backgroundColor: a.color || "#fecaca" }}
                    >
                      {Icon && <Icon size={12} className="text-slate-700" aria-hidden />}
                    </span>
                    <span className="flex min-w-0 flex-col">
                      <span className="truncate text-sm text-slate-900">
                        {a.label || a.id}
                      </span>
                      {parent && (
                        <span className="truncate text-[10px] text-slate-400">
                          inside {parent}
                        </span>
                      )}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
        <div className="flex justify-end border-t border-slate-200 px-4 py-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded px-3 py-1 text-xs text-slate-600 hover:bg-slate-100"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
