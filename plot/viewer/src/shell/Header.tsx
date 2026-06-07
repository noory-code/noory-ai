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
    <header className="flex flex-col border-b border-line bg-surface/80 backdrop-blur">
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center gap-4">
          <span className="text-sm font-semibold tracking-wide">PLOT</span>
          <span className="font-mono text-xs text-fg-muted" title={workspaceRoot}>
            {workspaceRoot}
          </span>
        </div>
        {/* v0.34.7 (D-2026-05-31-U) — no fixed width; items stay on one line
            (``whitespace-nowrap`` + ``shrink-0``) so "저장 중…" never wraps.
            The error is the only flexible item and truncates. */}
        <div className="flex min-w-0 items-center justify-end gap-3 pl-4 text-xs">
          {error && (
            <span className="min-w-0 truncate text-danger" title={error} aria-label="error">
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
        <div className="flex items-center justify-between border-t border-warn-line bg-warn-soft px-4 py-1.5 text-xs text-warn-fg">
          <span>
            👁 {t("snapshot.viewing", { tag: viewingTag })}
          </span>
          <button
            type="button"
            onClick={onExitTagView}
            className="rounded border border-warn-line bg-surface px-2 py-0.5 text-[11px] text-warn-fg hover:bg-warn-soft"
          >
            ✕ {t("snapshot.exit")}
          </button>
        </div>
      )}
      {migratedToast && migratedToast.length > 0 && (
        <div className="flex items-center justify-between border-t border-ok-line bg-ok-soft px-4 py-1.5 text-xs text-ok-fg">
          <span>
            Migrated {migratedToast.length} v0.1 sketch
            {migratedToast.length === 1 ? "" : "es"} to v0.4 format:
            <code className="ml-1">{migratedToast.join(", ")}</code>
          </span>
          <button
            type="button"
            onClick={onDismissToast}
            className="rounded px-1 text-ok-fg hover:bg-ok-soft"
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
      ? "text-fg-muted"
      : state === "saved"
        ? "text-ok-fg"
        : "text-danger";
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
    connecting: "bg-warn animate-pulse",
    connected: "bg-ok",
    reconnecting: "bg-warn animate-pulse",
    disconnected: "bg-fg-faint",
  }[status];
  const tone = {
    connecting: "text-warn-fg",
    connected: "text-ok-fg",
    reconnecting: "text-warn-fg",
    disconnected: "text-fg-secondary",
  }[status];
  return (
    <span className={`inline-flex items-center gap-1 whitespace-nowrap ${tone}`} title={label}>
      <span aria-hidden className={`h-2 w-2 rounded-full ${dot}`} />
      <span>{label}</span>
    </span>
  );
}
