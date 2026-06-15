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

import { ChatActivityIndicator } from "./ChatActivityIndicator";
import { getChatProvider, setChatProvider, type McpProviderName } from "../app/mcp";
import { useChatStream, type ChatMessage } from "../hooks/useChatStream";
import { useViewerContextBridge } from "../hooks/useViewerContextBridge";
import type { ChatScope, ChatSelectionNode } from "../types";
import { ChatProvidersPanel } from "./ChatProvidersPanel";
import { useDialog } from "./dialog/DialogProvider";

// D-2026-06-16-C — model suggestions per CLI for the model field's datalist.
// The field is free-text (you can type any model your CLI accepts); these are
// only autocomplete hints. We list ONLY values we can stand behind: the
// ``claude`` CLI documents these aliases in its own --help; codex / gemini
// model ids are version-specific and vendor-owned, so we offer no hardcoded
// (potentially stale) suggestions there — the user types the id their CLI
// supports. Empty selection = the CLI's own default.
const MODEL_SUGGESTIONS: Partial<Record<McpProviderName, string[]>> = {
  "claude-code": ["fable", "opus", "sonnet"],
};

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
  /** Human label for a parametric ``service_detail:<id>`` scope — the service's
   * name, shown on the switcher's canvas tab instead of the generic "Service
   * detail" (D-2026-06-15-H). Ignored for non-service-detail scopes. */
  activeScopeLabel?: string | null;
  /** Live canvas selection, injected as per-turn chat context (Layer 2,
   * D-2026-06-15-A). */
  selection?: ChatSelectionNode[];
}

export function ChatDock({
  onError,
  workspaceRoot,
  activeScope = "project",
  activeScopeLabel,
  selection = [],
}: ChatDockProps) {
  const { t } = useTranslation();
  // Report the canvas the user is looking at + their selection to the engine so
  // the external MCP agent can read it (D-2026-06-15-D). Uses ``activeScope``
  // (the canvas), not the chat-thread toggle — the agent wants what's on
  // screen. ChatDock stays mounted whenever a workspace is open (the panel
  // collapses to width 0, it does not unmount), so it is the bridge's home.
  useViewerContextBridge(workspaceRoot, activeScope, selection);
  const [activeProvider, setActiveProvider] =
    useState<McpProviderName | null>(null);
  // D-2026-06-16-C — the CLI model override for the active provider. null = the
  // CLI's own configured default. Reset to null when the provider changes.
  const [activeModel, setActiveModel] = useState<string | null>(null);
  // The chat switcher has exactly two tabs: the selected canvas | project
  // (D-2026-06-13-H). "canvas" mode follows the active canvas tab; "project"
  // pins the shared cross-canvas thread. (The v0.77.0 full picker was reverted
  // — the canvas tabs, not the chat dock, are where the user picks a canvas.)
  const [scopeMode, setScopeMode] = useState<"canvas" | "project">("canvas");
  const effectiveScope: ChatScope =
    scopeMode === "project" ? "project" : activeScope;
  // D-2026-06-14-D — provider connection is a setup step, not something to
  // stare at while chatting; keep it behind a compact bar, collapsed by
  // default. The bar shows the active CLI so the user knows what's connected
  // without expanding.
  const [providersOpen, setProvidersOpen] = useState(false);

  useEffect(() => {
    if (!workspaceRoot) return;
    void getChatProvider(workspaceRoot).then(
      // claude-code is selectable for in-app chat again (D-2026-06-14-B); the
      // double-billing tradeoff is surfaced as a warning banner, not a block.
      (sel) => {
        setActiveProvider(sel.provider);
        setActiveModel(sel.model ?? null);
      },
      (err) => onError(err instanceof Error ? err.message : String(err)),
    );
  }, [workspaceRoot, onError]);

  const handleSelectProvider = useCallback(
    (provider: McpProviderName | null) => {
      setActiveProvider(provider);
      // A model valid for one CLI is meaningless for another — clear it so the
      // new provider starts on its own default (D-2026-06-16-C).
      setActiveModel(null);
      if (!workspaceRoot) return;
      void setChatProvider(workspaceRoot, provider, null).catch((err) =>
        onError(err instanceof Error ? err.message : String(err)),
      );
    },
    [workspaceRoot, onError],
  );

  const handleSelectModel = useCallback(
    (model: string | null) => {
      const normalized = model && model.trim() ? model.trim() : null;
      setActiveModel(normalized);
      if (!workspaceRoot || !activeProvider) return;
      void setChatProvider(workspaceRoot, activeProvider, normalized).catch((err) =>
        onError(err instanceof Error ? err.message : String(err)),
      );
    },
    [workspaceRoot, activeProvider, onError],
  );

  const selectionProps = workspaceRoot
    ? { activeProvider, onSelectProvider: handleSelectProvider }
    : {};

  return (
    <aside
      aria-label={t("chat.dockTitle")}
      className="flex h-full w-full flex-col border-r border-line bg-surface"
    >
      <header className="flex items-center gap-2 border-b border-line px-3 py-2">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
          {t("chat.dockTitle")}
        </h2>
      </header>
      <div className="flex flex-1 flex-col overflow-hidden">
          <button
            type="button"
            aria-label={t("chat.providersBarLabel")}
            aria-expanded={providersOpen}
            data-connected={activeProvider ? "1" : "0"}
            onClick={() => setProvidersOpen((o) => !o)}
            className="flex items-center justify-between gap-2 border-b border-line px-3 py-2 text-xs text-fg-muted hover:bg-surface-muted hover:text-fg-strong"
          >
            {/* Persistent connection indicator so the connected agent is
                legible at a glance without expanding the panel
                (D-2026-06-15-F): a filled dot + the agent name in a readable
                colour when connected; a hollow dot + muted prompt when not. */}
            <span className="flex min-w-0 items-center gap-2">
              <span
                aria-hidden
                className={
                  activeProvider
                    ? "h-1.5 w-1.5 shrink-0 rounded-full bg-fg-strong"
                    : "h-1.5 w-1.5 shrink-0 rounded-full border border-fg-muted"
                }
              />
              <span
                className={
                  activeProvider
                    ? "truncate font-medium text-fg-strong"
                    : "truncate"
                }
              >
                {activeProvider
                  ? `${t(`chat.providers.${activeProvider}`)}${activeModel ? ` · ${activeModel}` : ""}`
                  : t("chat.providersTitle")}
              </span>
            </span>
            <span aria-hidden>{providersOpen ? "▾" : "▸"}</span>
          </button>
          {providersOpen && (
            <div className="overflow-y-auto border-b border-line p-3">
              <ChatProvidersPanel onError={onError} {...selectionProps} />
            </div>
          )}
          {activeProvider && workspaceRoot && (
            <ChatModelRow
              provider={activeProvider}
              model={activeModel}
              onChange={handleSelectModel}
            />
          )}
          {activeScope !== "project" && (
            <ChatScopeSwitcher
              canvasScope={activeScope}
              canvasLabel={activeScopeLabel}
              mode={scopeMode}
              onModeChange={setScopeMode}
            />
          )}
          <ChatMessageFrame
            workspaceRoot={workspaceRoot}
            activeProvider={activeProvider}
            scope={effectiveScope}
            selection={selection}
            onError={onError}
          />
      </div>
    </aside>
  );
}

/**
 * Model field for the active provider (D-2026-06-16-C). A free-text input
 * with a datalist of per-CLI suggestions — the user can pick a suggestion or
 * type any model id their CLI accepts. Empty commits ``null`` (the CLI's own
 * default). Commits on blur / Enter so a half-typed id isn't sent mid-stroke.
 */
function ChatModelRow({
  provider,
  model,
  onChange,
}: {
  provider: McpProviderName;
  model: string | null;
  onChange: (model: string | null) => void;
}) {
  const { t } = useTranslation();
  const [draft, setDraft] = useState(model ?? "");
  useEffect(() => setDraft(model ?? ""), [model]);
  const listId = `chat-models-${provider}`;
  const suggestions = MODEL_SUGGESTIONS[provider] ?? [];
  const commit = () => {
    const next = draft.trim() || null;
    if (next !== (model ?? null)) onChange(next);
  };
  return (
    <div className="flex items-center gap-2 border-b border-line px-3 py-2 text-[11px]">
      <label htmlFor={`${listId}-input`} className="shrink-0 text-fg-muted">
        {t("chat.modelLabel")}
      </label>
      <input
        id={`${listId}-input`}
        list={listId}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            commit();
          }
        }}
        placeholder={t("chat.modelPlaceholder")}
        className="min-w-0 flex-1 rounded border border-line bg-surface-muted px-2 py-1 text-fg"
      />
      <datalist id={listId}>
        {suggestions.map((s) => (
          <option key={s} value={s} />
        ))}
      </datalist>
    </div>
  );
}

/**
 * Two-tab chat scope switcher: the selected canvas | project
 * (D-2026-06-13-H). The "canvas" tab follows the active canvas tab; "project"
 * pins the shared cross-canvas thread. A parametric ``service_detail:<id>``
 * canvas is labelled with its base ``service_detail`` label (D-2026-06-15-B).
 */
function ChatScopeSwitcher({
  canvasScope,
  canvasLabel,
  mode,
  onModeChange,
}: {
  canvasScope: ChatScope;
  canvasLabel?: string | null;
  mode: "canvas" | "project";
  onModeChange: (mode: "canvas" | "project") => void;
}) {
  const { t } = useTranslation();
  const isServiceDetail = canvasScope.startsWith("service_detail:");
  // A service-detail tab shows the service's NAME (D-2026-06-15-H), falling
  // back to the generic label only when the name isn't available.
  const canvasTabLabel = isServiceDetail
    ? canvasLabel || t("chat.scope.service_detail")
    : t(`chat.scope.${canvasScope}`);
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
      {segment("canvas", canvasTabLabel)}
      {segment("project", t("chat.scope.project"))}
    </div>
  );
}

interface ChatMessageFrameProps {
  workspaceRoot?: string;
  activeProvider: McpProviderName | null;
  scope: ChatScope;
  selection: ChatSelectionNode[];
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
  selection,
  onError,
}: ChatMessageFrameProps) {
  const { t } = useTranslation();
  const dialog = useDialog();
  const { messages, socketStatus, isStreaming, send, reset, lastSendError } =
    useChatStream(workspaceRoot, scope, selection);
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
      {message.status === "streaming" && message.text === "" ? (
        // No tokens yet — the CLI is spawning / thinking. Show the live
        // activity indicator so the turn never looks frozen (D-2026-06-16-B).
        <ChatActivityIndicator />
      ) : (
        <p className="whitespace-pre-wrap text-fg-strong">
          {message.text}
          {message.status === "streaming" && (
            <span aria-hidden className="ml-0.5 inline-block animate-pulse">
              ▍
            </span>
          )}
        </p>
      )}
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
        {showDisconnected ? (
          t("chat.socketDisconnected")
        ) : isStreaming ? (
          <ChatActivityIndicator />
        ) : (
          ""
        )}
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
