/**
 * Top-of-page header — project path + name + socket status + save state
 * + error + migration toast. Extracted from ``App.tsx`` (v0.16.1) so the
 * App component owns wiring only, not chrome JSX.
 *
 * v0.24.12 (D-2026-05-21-A) — SaveIndicator added. ``useCanvasPersist``
 * already computed ``saveState`` ("idle" / "saving" / "saved" / "error")
 * but it was never rendered, leaving canvas auto-save without user
 * feedback. The indicator now sits next to the live socket dot.
 */
import { useTranslation } from "react-i18next";
import type { SocketStatus } from "../api";
import type { SaveState } from "../canvases/SketchToolbar";

interface HeaderProps {
  projectPath: string;
  error: string | null;
  socketStatus: SocketStatus;
  saveState: SaveState;
  projectName: string | null;
  migratedToast: string[] | null;
  onDismissToast: () => void;
}

export function Header({
  projectPath,
  error,
  socketStatus,
  saveState,
  projectName,
  migratedToast,
  onDismissToast,
}: HeaderProps) {
  return (
    <header className="flex flex-col border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center gap-4">
          <span className="text-sm font-semibold tracking-wide">PLOT</span>
          <span className="font-mono text-xs text-slate-500" title={projectPath}>
            {truncateMiddle(projectPath, 48)}
          </span>
          {projectName && (
            <span className="text-sm text-slate-700">· {projectName}</span>
          )}
        </div>
        <div className="flex w-72 items-center justify-end gap-2 text-right text-xs">
          <SaveIndicator state={saveState} />
          <SocketIndicator status={socketStatus} />
          {error && (
            <span
              className="truncate text-rose-600"
              title={error}
              aria-label="error"
            >
              {error}
            </span>
          )}
        </div>
      </div>
      {migratedToast && migratedToast.length > 0 && (
        <div className="flex items-center justify-between border-t border-emerald-200 bg-emerald-50 px-4 py-1.5 text-xs text-emerald-800">
          <span>
            Migrated {migratedToast.length} v0.1 sketch
            {migratedToast.length === 1 ? "" : "es"} to v0.4 format:
            <code className="ml-1">{migratedToast.join(", ")}</code>
          </span>
          <button
            type="button"
            onClick={onDismissToast}
            className="rounded px-1 text-emerald-700 hover:bg-emerald-100"
          >
            ✕
          </button>
        </div>
      )}
    </header>
  );
}

function SaveIndicator({ state }: { state: SaveState }) {
  const { t } = useTranslation();
  if (state === "idle") return null;
  const label = t(`header.saveState.${state}`);
  const tone =
    state === "saving"
      ? "text-slate-500"
      : state === "saved"
        ? "text-emerald-700"
        : "text-rose-600";
  const icon =
    state === "saving" ? "💾" : state === "saved" ? "✓" : "⚠";
  return (
    <span className={`inline-flex items-center gap-1 ${tone}`} title={label}>
      <span aria-hidden>{icon}</span>
      <span>{label}</span>
    </span>
  );
}

function SocketIndicator({ status }: { status: SocketStatus }) {
  const label = {
    connecting: "connecting…",
    connected: "live",
    reconnecting: "reconnecting…",
    disconnected: "offline",
  }[status];
  const dot = {
    connecting: "bg-amber-500 animate-pulse",
    connected: "bg-emerald-500",
    reconnecting: "bg-amber-500 animate-pulse",
    disconnected: "bg-slate-400",
  }[status];
  const tone = {
    connecting: "text-amber-700",
    connected: "text-emerald-700",
    reconnecting: "text-amber-700",
    disconnected: "text-slate-600",
  }[status];
  return (
    <span
      className={`inline-flex items-center gap-1 ${tone}`}
      title={`Server: ${label}`}
    >
      <span aria-hidden className={`h-2 w-2 rounded-full ${dot}`} />
      <span>{label}</span>
    </span>
  );
}

function truncateMiddle(s: string, max: number): string {
  if (s.length <= max) return s;
  const side = Math.floor((max - 1) / 2);
  return `${s.slice(0, side)}…${s.slice(-side)}`;
}
