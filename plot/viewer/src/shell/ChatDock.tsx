/**
 * R7 chat dock (D-2026-06-11-E, Phase B).
 *
 * Right-side collapsible container that hosts the chat surface. Phase B
 * step B1 wired up the dock chrome + collapse persistence + mounted the
 * existing `ChatProvidersPanel` inside. Step B2 added the message-list
 * frame; step B3 loads + persists the workspace's active chat-CLI
 * choice through `/api/chat/provider`. Phase C plugs subprocess
 * streaming into the same surface.
 *
 * Collapse state persists across reloads via
 * `localStorage["plot:chatDockCollapsed"]` ("1" = collapsed, "0" =
 * expanded). When collapsed, the embedded panels unmount — keeps the
 * screen-reader tree honest and skips the provider fetch.
 */
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { getChatProvider, setChatProvider, type McpProviderName } from "../app/mcp";
import { ChatProvidersPanel } from "./ChatProvidersPanel";

const COLLAPSE_STORAGE_KEY = "plot:chatDockCollapsed";

function readInitialCollapsed(): boolean {
  try {
    return localStorage.getItem(COLLAPSE_STORAGE_KEY) === "1";
  } catch {
    return false;
  }
}

export interface ChatDockProps {
  onError: (message: string) => void;
  /** When defined, the dock loads + persists the workspace's chat-CLI
   * choice through `/api/chat/provider`. Tests omit it to verify the dock
   * stays inert without a workspace (e.g. during the ProjectPicker
   * phase, though in practice App.tsx unmounts the dock there). */
  workspaceRoot?: string;
}

export function ChatDock({ onError, workspaceRoot }: ChatDockProps) {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState<boolean>(readInitialCollapsed);
  const [activeProvider, setActiveProvider] =
    useState<McpProviderName | null>(null);

  const toggle = useCallback(() => {
    setCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem(COLLAPSE_STORAGE_KEY, next ? "1" : "0");
      } catch {
        // localStorage unavailable (private mode, quota) — keep the
        // session-level state; persistence is best-effort.
      }
      return next;
    });
  }, []);

  useEffect(() => {
    if (!workspaceRoot || collapsed) return;
    void getChatProvider(workspaceRoot).then(
      (sel) => setActiveProvider(sel.provider),
      (err) => onError(err instanceof Error ? err.message : String(err)),
    );
  }, [workspaceRoot, collapsed, onError]);

  const handleSelectProvider = useCallback(
    (provider: McpProviderName | null) => {
      setActiveProvider(provider);
      if (!workspaceRoot) return;
      void setChatProvider(workspaceRoot, provider).catch((err) =>
        onError(err instanceof Error ? err.message : String(err)),
      );
    },
    [workspaceRoot, onError],
  );

  const selectionProps = workspaceRoot
    ? { activeProvider, onSelectProvider: handleSelectProvider }
    : {};

  return (
    <aside
      aria-label={t("chat.dockTitle")}
      data-collapsed={collapsed ? "1" : "0"}
      className={
        collapsed
          ? "flex w-10 flex-none flex-col border-l border-line bg-surface"
          : "flex w-80 flex-none flex-col border-l border-line bg-surface"
      }
    >
      <header className="flex items-center justify-between gap-2 border-b border-line px-2 py-2">
        {!collapsed && (
          <h2 className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
            {t("chat.dockTitle")}
          </h2>
        )}
        <button
          type="button"
          onClick={toggle}
          aria-label={collapsed ? t("chat.expand") : t("chat.collapse")}
          title={collapsed ? t("chat.expand") : t("chat.collapse")}
          className="rounded p-1 text-fg-muted hover:bg-surface-muted hover:text-fg-strong"
        >
          <span aria-hidden>{collapsed ? "‹" : "›"}</span>
        </button>
      </header>
      {!collapsed && (
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="overflow-y-auto border-b border-line p-3">
            <ChatProvidersPanel onError={onError} {...selectionProps} />
          </div>
          <ChatMessageFrame />
        </div>
      )}
    </aside>
  );
}

/**
 * Visual frame for the chat surface. Phase B step B2 — no message
 * state, no submit handler, no streaming. The textarea + send button
 * land disabled with copy that names Phase C as the activation step,
 * so the user sees the empty surface but understands it's intentionally
 * inert until Phase C wires up the CLI subprocess.
 */
function ChatMessageFrame() {
  const { t } = useTranslation();
  return (
    <>
      <div
        role="log"
        aria-label={t("chat.messagesLogLabel")}
        className="flex-1 overflow-y-auto p-3 text-xs text-fg-muted"
      >
        <p>{t("chat.emptyMessages")}</p>
      </div>
      <form
        className="flex flex-col gap-2 border-t border-line p-3"
        onSubmit={(e) => e.preventDefault()}
      >
        <textarea
          aria-label={t("chat.inputLabel")}
          placeholder={t("chat.inputPlaceholder")}
          disabled
          rows={2}
          className="resize-none rounded border border-line bg-surface-muted p-2 text-sm text-fg disabled:opacity-60"
        />
        <button
          type="submit"
          disabled
          className="self-end rounded border border-line-strong px-3 py-1 text-xs font-medium text-fg disabled:opacity-50"
        >
          {t("chat.send")}
        </button>
      </form>
    </>
  );
}
