export type SaveState = "idle" | "saving" | "saved" | "error";

export interface SketchToolbarProps {
  saveState: SaveState;
  canUndo: boolean;
  canRedo: boolean;
  onAddNode: () => void;
  onUndo: () => void;
  onRedo: () => void;
  onAutoLayout: () => void;
  onDownload: () => void;
  onUpload: () => void;
  /** v0.2: edge colour toggle reflecting value_form. */
  valueFlowOn: boolean;
  onToggleValueFlow: () => void;
}

export function SketchToolbar({
  saveState,
  canUndo,
  canRedo,
  onAddNode,
  onUndo,
  onRedo,
  onAutoLayout,
  onDownload,
  onUpload,
}: SketchToolbarProps) {
  return (
    <div className="absolute right-4 top-4 z-10 flex items-center gap-1 rounded-md border border-slate-200 bg-white/95 px-2 py-1 text-xs shadow-sm backdrop-blur">
      <button
        type="button"
        onClick={onAddNode}
        className="rounded bg-slate-900 px-2 py-1 font-medium text-white hover:bg-slate-700"
        title="Add node (double-click canvas also works)"
      >
        + Node
      </button>
      <Divider />
      <IconBtn label="Undo" enabled={canUndo} onClick={onUndo} hint="Cmd+Z">
        ↶
      </IconBtn>
      <IconBtn label="Redo" enabled={canRedo} onClick={onRedo} hint="Shift+Cmd+Z">
        ↷
      </IconBtn>
      <Divider />
      <button
        type="button"
        onClick={onAutoLayout}
        className="rounded px-2 py-1 text-slate-700 hover:bg-slate-100"
        title="Auto layout (dagre LR)"
      >
        Auto layout
      </button>
      <Divider />
      <SaveIndicator state={saveState} />
      <Divider />
      <button
        type="button"
        onClick={onDownload}
        className="rounded px-2 py-1 text-slate-700 hover:bg-slate-100"
        title="Download sketch JSON"
      >
        Download
      </button>
      <button
        type="button"
        onClick={onUpload}
        className="rounded px-2 py-1 text-slate-700 hover:bg-slate-100"
        title="Replace sketch with uploaded JSON"
      >
        Upload
      </button>
    </div>
  );
}

function Divider() {
  return <span className="h-4 w-px bg-slate-200" aria-hidden />;
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

function SaveIndicator({ state }: { state: SaveState }) {
  if (state === "idle") return <span className="text-slate-400">·</span>;
  const label = {
    saving: "saving…",
    saved: "saved",
    error: "save failed",
  }[state];
  const tone = {
    saving: "text-slate-500",
    saved: "text-emerald-700",
    error: "text-rose-700",
  }[state];
  return (
    <span className={tone} role="status" aria-live="polite">
      {label}
    </span>
  );
}
