/**
 * R7 chat dock (D-2026-06-11-E + D-2026-06-12-D, Phase B → C).
 *
 * Right-side collapsible container that hosts the chat surface. Phase B
 * landed the chrome + providers panel + persisted CLI selection; Phase C
 * (this file) wires the message frame to the engine's
 * ``/api/chat/send`` + ``chat_stream_event`` WS, so user input lands as a
 * real CLI turn and assistant deltas stream in live.
 *
 * Collapse state persists across reloads via
 * ``localStorage["plot:chatDockCollapsed"]`` (``"1"`` = collapsed). When
 * collapsed, both the providers panel and the chat-stream subscription
 * unmount — keeps the screen-reader tree honest and avoids an idle WS.
 */
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { getChatProvider, setChatProvider, type McpProviderName } from "../app/mcp";
import { useChatStream, type ChatMessage } from "../hooks/useChatStream";
import type { ChatScope } from "../types";
import { ChatProvidersPanel } from "./ChatProvidersPanel";
import { useDialog } from "./dialog/DialogProvider";

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
   * choice through `/api/chat/provider` and opens a chat stream on
   * `<workspace>/.noory/plot/`. Tests omit it to verify the dock stays
   * inert without a workspace (e.g. during the ProjectPicker phase, though
   * in practice App.tsx unmounts the dock there). */
  workspaceRoot?: string;
  /** The canvas-derived chat scope the dock follows (D-2026-06-13-H). App
   * passes the active canvas kind (or `service_detail` when the modal is
   * open); the user can override it to the shared `project` scope via the
   * in-dock switcher. Defaults to `project` so workspace-less / test mounts
   * stay coherent. */
  activeScope?: ChatScope;
}

export function ChatDock({
  onError,
  workspaceRoot,
  activeScope = "project",
}: ChatDockProps) {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState<boolean>(readInitialCollapsed);
  const [activeProvider, setActiveProvider] =
    useState<McpProviderName | null>(null);
  // "canvas" follows the active canvas; "project" pins the shared cross-canvas
  // thread (Q2 — explicit toggle, not auto). The canvas mode resolves to
  // ``activeScope``; project mode always to ``project``.
  const [scopeMode, setScopeMode] = useState<"canvas" | "project">("canvas");
  const effectiveScope: ChatScope =
    scopeMode === "project" ? "project" : activeScope;

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
      // claude-code is selectable for in-app chat again (D-2026-06-14-B); the
      // double-billing tradeoff is surfaced as a warning banner, not a block.
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
          {activeScope !== "project" && (
            <ChatScopeSwitcher
              canvasScope={activeScope}
              mode={scopeMode}
              onModeChange={setScopeMode}
            />
          )}
          <ChatMessageFrame
            workspaceRoot={workspaceRoot}
            activeProvider={activeProvider}
            scope={effectiveScope}
            onError={onError}
          />
        </div>
      )}
    </aside>
  );
}

/**
 * Segmented switcher between the active-canvas thread and the shared
 * ``project`` thread (D-2026-06-13-H Q2 — explicit, not auto). Only rendered
 * when the active canvas is itself non-project, so the two segments are
 * always distinct.
 */
function ChatScopeSwitcher({
  canvasScope,
  mode,
  onModeChange,
}: {
  canvasScope: ChatScope;
  mode: "canvas" | "project";
  onModeChange: (mode: "canvas" | "project") => void;
}) {
  const { t } = useTranslation();
  const segment = (value: "canvas" | "project", label: string) => (
    <button
      type="button"
      role="tab"
      aria-selected={mode === value}
      onClick={() => onModeChange(value)}
      className={
        mode === value
          ? "flex-1 rounded px-2 py-1 text-[11px] font-medium bg-surface-muted text-fg-strong"
          : "flex-1 rounded px-2 py-1 text-[11px] text-fg-muted hover:text-fg-strong"
      }
    >
      {label}
    </button>
  );
  return (
    <div
      role="tablist"
      aria-label={t("chat.scopeLabel")}
      className="flex gap-1 border-b border-line px-3 py-2"
    >
      {segment("canvas", t(`chat.scope.${canvasScope}`))}
      {segment("project", t("chat.scope.project"))}
    </div>
  );
}

interface ChatMessageFrameProps {
  workspaceRoot?: string;
  activeProvider: McpProviderName | null;
  scope: ChatScope;
  onError: (message: string) => void;
}

/**
 * Live message surface — Phase C activation. Renders the chat list, the
 * input + Send button, and a one-line connection / streaming status bar.
 * The data-state attributes are stable hooks for the e2e smoke test.
 */
function ChatMessageFrame({
  workspaceRoot,
  activeProvider,
  scope,
  onError,
}: ChatMessageFrameProps) {
  const { t } = useTranslation();
  const dialog = useDialog();
  const { messages, socketStatus, isStreaming, send, reset, lastSendError } =
    useChatStream(workspaceRoot, scope);
  const [draft, setDraft] = useState("");

  const providerLabel = activeProvider
    ? t(`chat.providers.${activeProvider}`)
    : "";
  const placeholder = activeProvider
    ? t("chat.inputPlaceholder", { provider: providerLabel })
    : t("chat.inputPlaceholderUnselected");
  const canSubmit =
    Boolean(workspaceRoot) &&
    activeProvider !== null &&
    !isStreaming &&
    draft.trim().length > 0;

  useEffect(() => {
    if (lastSendError) onError(lastSendError);
  }, [lastSendError, onError]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!canSubmit) return;
      const text = draft;
      setDraft("");
      await send(text);
    },
    [canSubmit, draft, send],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Enter sends; Shift+Enter inserts a newline.
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (canSubmit) {
          const text = draft;
          setDraft("");
          void send(text);
        }
      }
    },
    [canSubmit, draft, send],
  );

  const handleReset = useCallback(async () => {
    if (!workspaceRoot) return;
    const ok = await dialog.confirm({ message: t("chat.confirmReset") });
    if (!ok) return;
    await reset();
  }, [dialog, reset, t, workspaceRoot]);

  return (
    <>
      {activeProvider === "claude-code" && (
        <p
          role="note"
          data-warning="claude-billing"
          className="border-b border-warn-line bg-warn-soft px-3 py-2 text-[11px] text-warn-fg"
        >
          {t("chat.claudeBillingWarning")}
        </p>
      )}
      <div
        role="log"
        aria-label={t("chat.messagesLogLabel")}
        data-streaming={isStreaming ? "1" : "0"}
        className="flex-1 space-y-3 overflow-y-auto p-3 text-xs"
      >
        {!workspaceRoot ? (
          <p className="text-fg-muted">{t("chat.noWorkspace")}</p>
        ) : messages.length === 0 ? (
          <p className="text-fg-muted">{t("chat.emptyMessages")}</p>
        ) : (
          messages.map((m) => <ChatMessageRow key={m.id} message={m} />)
        )}
      </div>
      <ChatStatusBar
        socketStatus={socketStatus}
        isStreaming={isStreaming}
        canReset={Boolean(workspaceRoot) && messages.length > 0}
        onReset={handleReset}
      />
      <form
        className="flex flex-col gap-2 border-t border-line p-3"
        onSubmit={handleSubmit}
      >
        <textarea
          aria-label={t("chat.inputLabel")}
          placeholder={placeholder}
          disabled={!workspaceRoot || activeProvider === null}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          className="resize-none rounded border border-line bg-surface-muted p-2 text-sm text-fg disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!canSubmit}
          data-state={isStreaming ? "streaming" : "idle"}
          className="self-end rounded border border-line-strong px-3 py-1 text-xs font-medium text-fg disabled:opacity-50"
        >
          {t("chat.send")}
        </button>
      </form>
    </>
  );
}

function ChatMessageRow({ message }: { message: ChatMessage }) {
  const { t } = useTranslation();
  const roleLabel =
    message.role === "user" ? t("chat.you") : t("chat.assistant");
  const isError = message.status === "error";
  return (
    <div
      data-role={message.role}
      data-status={message.status}
      className={
        message.role === "user"
          ? "rounded border border-line-strong bg-surface-muted p-2"
          : "rounded border border-line bg-surface p-2"
      }
    >
      <div className="mb-1 flex items-center justify-between gap-2 text-[10px] uppercase tracking-wide text-fg-muted">
        <span>{roleLabel}</span>
        {message.status === "streaming" && (
          <span aria-live="polite">{t("chat.streamingHint")}</span>
        )}
      </div>
      <p
        className={
          isError
            ? "whitespace-pre-wrap text-fg-strong"
            : "whitespace-pre-wrap text-fg-strong"
        }
      >
        {message.text}
      </p>
      {isError && message.errorMessage && (
        <p className="mt-1 text-[11px] text-fg-muted">
          {t("chat.errorPrefix")}
          {message.errorMessage}
        </p>
      )}
    </div>
  );
}

function ChatStatusBar({
  socketStatus,
  isStreaming,
  canReset,
  onReset,
}: {
  socketStatus: ReturnType<typeof useChatStream>["socketStatus"];
  isStreaming: boolean;
  canReset: boolean;
  onReset: () => void | Promise<void>;
}) {
  const { t } = useTranslation();
  const showDisconnected =
    socketStatus === "reconnecting" || socketStatus === "disconnected";
  return (
    <div className="flex items-center justify-between gap-2 border-t border-line px-3 py-1 text-[10px] text-fg-muted">
      <span aria-live="polite">
        {showDisconnected
          ? t("chat.socketDisconnected")
          : isStreaming
            ? t("chat.streamingHint")
            : ""}
      </span>
      <button
        type="button"
        onClick={onReset}
        disabled={!canReset}
        className="rounded px-2 py-0.5 text-fg-muted hover:bg-surface-muted hover:text-fg-strong disabled:opacity-40"
      >
        {t("chat.resetSession")}
      </button>
    </div>
  );
}
