// v0.11.6 — Download / Upload / save-state indicator removed per user
// feedback. Save is automatic and silent; the rare error case surfaces
// through the App-level error toast already, so the toolbar can stay
// focused on undo/redo + layout actions only.

export type SaveState = "idle" | "saving" | "saved" | "error";

export interface SketchToolbarProps {
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  /** v0.2: edge colour toggle reflecting value_form. */
  valueFlowOn: boolean;
  onToggleValueFlow: () => void;
  /** v0.13.9 — auto-layout (D-2026-05-10-E). Enabled when an anchor
   *  exists on the active canvas and at least one non-anchor node is
   *  present. Click ⇒ instant directional-tree layout via
   *  ``onDocChange`` (history-tracked, ``Cmd+Z`` reverses). */
  canAutoLayout: boolean;
  onAutoLayout: () => void;
}

export function SketchToolbar({
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  canAutoLayout,
  onAutoLayout,
}: SketchToolbarProps) {
  return (
    <div className="absolute right-4 top-4 z-10 flex items-center gap-1 rounded-md border border-slate-200 bg-white/95 px-2 py-1 text-xs shadow-sm backdrop-blur">
      <IconBtn label="Undo" enabled={canUndo} onClick={onUndo} hint="Cmd+Z">
        ↶
      </IconBtn>
      <IconBtn label="Redo" enabled={canRedo} onClick={onRedo} hint="Shift+Cmd+Z">
        ↷
      </IconBtn>
      <IconBtn label="Auto layout" enabled={canAutoLayout} onClick={onAutoLayout} hint="">
        ⊞
      </IconBtn>
    </div>
  );
}

function IconBtn({
  children,
  label,
  enabled,
  onClick,
  hint,
}: {
  children: React.ReactNode;
  label: string;
  enabled: boolean;
  onClick: () => void;
  hint: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={!enabled}
      className={`rounded px-2 py-1 ${
        enabled ? "text-slate-700 hover:bg-slate-100" : "cursor-not-allowed text-slate-300"
      }`}
      aria-label={label}
      title={`${label} (${hint})`}
    >
      {children}
    </button>
  );
}
