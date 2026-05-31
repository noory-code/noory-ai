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
  error: string | null;
  socketStatus: SocketStatus;
  saveState: SaveState;
  /** Workspace ROOT absolute path — the repository the Plot plugin is
   *  installed in. Shown at the very top next to PLOT (v0.34.3,
   *  D-2026-05-31-Q). The project NAME + its blueprint version live in the
   *  tab-bar center; no per-project version belongs up here next to the
   *  repo path (v0.34.7, D-2026-05-31-U). */
  workspaceRoot: string;
  /** v0.24.14 (D-2026-05-21-C) — when set, the app is in snapshot mode at
   *  this git tag. Banner appears with an exit button; edits are blocked
   *  upstream. */
  viewingTag: string | null;
  onExitTagView: () => void;
  migratedToast: string[] | null;
  onDismissToast: () => void;
}

export function Header({
  error,
  socketStatus,
  saveState,
  workspaceRoot,
  viewingTag,
  onExitTagView,
  migratedToast,
  onDismissToast,
}: HeaderProps) {
  const { t } = useTranslation();
  return (
    <header className="flex flex-col border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center gap-4">
          <span className="text-sm font-semibold tracking-wide">PLOT</span>
          <span className="font-mono text-xs text-slate-500" title={workspaceRoot}>
            {workspaceRoot}
          </span>
        </div>
        {/* v0.34.7 (D-2026-05-31-U) — no fixed width; items stay on one line
            (``whitespace-nowrap`` + ``shrink-0``) so "저장 중…" never wraps.
            The error is the only flexible item and truncates. */}
        <div className="flex min-w-0 items-center justify-end gap-3 pl-4 text-xs">
          {error && (
            <span className="min-w-0 truncate text-rose-600" title={error} aria-label="error">
              {error}
            </span>
          )}
          <span className="shrink-0">
            <SaveIndicator state={saveState} />
          </span>
          <span className="shrink-0">
            <SocketIndicator status={socketStatus} />
          </span>
        </div>
      </div>
      {viewingTag && (
        <div className="flex items-center justify-between border-t border-amber-200 bg-amber-50 px-4 py-1.5 text-xs text-amber-900">
          <span>
            👁 {t("snapshot.viewing", { tag: viewingTag })}
          </span>
          <button
            type="button"
            onClick={onExitTagView}
            className="rounded border border-amber-300 bg-white px-2 py-0.5 text-[11px] text-amber-800 hover:bg-amber-100"
          >
            ✕ {t("snapshot.exit")}
          </button>
        </div>
      )}
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
    <span className={`inline-flex items-center gap-1 whitespace-nowrap ${tone}`} title={label}>
      <span aria-hidden>{icon}</span>
      <span>{label}</span>
    </span>
  );
}

function SocketIndicator({ status }: { status: SocketStatus }) {
  // The dot reflects the MCP server connection — prefix makes that explicit.
  const label = {
    connecting: "MCP: connecting…",
    connected: "MCP: live",
    reconnecting: "MCP: reconnecting…",
    disconnected: "MCP: offline",
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
    <span className={`inline-flex items-center gap-1 whitespace-nowrap ${tone}`} title={label}>
      <span aria-hidden className={`h-2 w-2 rounded-full ${dot}`} />
      <span>{label}</span>
    </span>
  );
}
