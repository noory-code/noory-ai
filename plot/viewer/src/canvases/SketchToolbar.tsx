// v0.11.6 — Download / Upload / save-state indicator removed per user
// feedback. Save is automatic and silent; the rare error case surfaces
// through the App-level error toast already, so the toolbar can stay
// focused on undo/redo + layout actions only.
import { useTranslation } from "react-i18next";

export type SaveState = "idle" | "saving" | "saved" | "error";

export interface SketchToolbarProps {
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  /** v0.2: edge colour toggle reflecting value_form. */
  valueFlowOn: boolean;
  onToggleValueFlow: () => void;
}

export function SketchToolbar({ canUndo, canRedo, onUndo, onRedo }: SketchToolbarProps) {
  const { t } = useTranslation();
  return (
    <div className="absolute right-4 top-4 z-10 flex items-center gap-1 rounded-md border border-line bg-surface/95 px-2 py-1 text-xs shadow-sm backdrop-blur">
      <IconBtn
        label={t("toolbar.undo")}
        enabled={canUndo}
        onClick={onUndo}
        hint={t("toolbar.shortcuts.undo")}
      >
        ↶
      </IconBtn>
      <IconBtn
        label={t("toolbar.redo")}
        enabled={canRedo}
        onClick={onRedo}
        hint={t("toolbar.shortcuts.redo")}
      >
        ↷
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
        enabled ? "text-fg hover:bg-surface-subtle" : "cursor-not-allowed text-fg-faint"
      }`}
      aria-label={label}
      title={`${label} (${hint})`}
    >
      {children}
    </button>
  );
}
