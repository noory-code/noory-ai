export type SaveState = "idle" | "saving" | "saved" | "error";

export interface SketchToolbarProps {
  saveState: SaveState;
  onAddNode: () => void;
  onDownload: () => void;
  onUpload: () => void;
}

export function SketchToolbar({
  saveState,
  onAddNode,
  onDownload,
  onUpload,
}: SketchToolbarProps) {
  return (
    <div className="absolute right-4 top-4 z-10 flex items-center gap-2 rounded-md border border-slate-200 bg-white/95 px-2 py-1 text-xs shadow-sm backdrop-blur">
      <button
        type="button"
        onClick={onAddNode}
        className="rounded bg-slate-900 px-2 py-1 font-medium text-white hover:bg-slate-700"
        title="Add node (double-click canvas also works)"
      >
        + Node
      </button>
      <span className="h-4 w-px bg-slate-200" />
      <SaveIndicator state={saveState} />
      <span className="h-4 w-px bg-slate-200" />
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
        title="Import sketch JSON"
      >
        Upload
      </button>
    </div>
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
