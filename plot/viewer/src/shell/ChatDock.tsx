/**
 * R7 chat dock (D-2026-06-11-E … D-2026-06-16-D).
 *
 * Left-side resizable panel hosting the chat surface. v0.85.0 (D-2026-06-16-D)
 * reshaped the chrome to read like a modern chat app: a top conversation bar
 * with the **model selector** as the prominent control + a compact provider
 * chip, left/right-aligned message bubbles, and a single rounded composer with
 * an integrated send button. All prior behaviour is preserved — provider
 * connection (`/api/chat/provider`), per-canvas scope (2-tab), the
 * `chat_stream_event` stream (`useChatStream`), and the per-provider model
 * override (`set` via PUT).
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

// D-2026-06-16-C — model suggestions per CLI for the model dropdown. The
// control is a dropdown + "Custom…" free-text fallback, so these are only the
// pre-listed options. We list ONLY values we can stand behind: the ``claude``
// CLI documents these aliases in its own --help; codex / gemini model ids are
// version-specific and vendor-owned, so there are no hardcoded (potentially
// stale) options there — the user picks "Custom…" and types the id their CLI
// supports. Empty = the CLI's own default.
const MODEL_SUGGESTIONS: Partial<Record<McpProviderName, string[]>> = {
  "claude-code": ["fable", "opus", "sonnet"],
};

const CUSTOM_MODEL_OPTION = "__custom__";

export interface ChatDockProps {
  onError: (message: string) => void;
  /** When defined, the dock loads + persists the workspace's chat-CLI
   * choice through `/api/chat/provider` and opens a chat stream on
   * `<workspace>/.noory/plot/`. Tests omit it to verify the dock stays
   * inert without a workspace. */
  workspaceRoot?: string;
  /** The canvas-derived chat scope the dock follows (D-2026-06-13-H). */
  activeScope?: ChatScope;
  /** Human label for a parametric ``service_detail:<id>`` scope (D-2026-06-15-H). */
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
  // Report the canvas + selection to the engine so the external MCP agent can
  // read it (D-2026-06-15-D). Uses ``activeScope`` (the canvas), not the
  // chat-thread toggle.
  useViewerContextBridge(workspaceRoot, activeScope, selection);
  const [activeProvider, setActiveProvider] =
    useState<McpProviderName | null>(null);
  // D-2026-06-16-C — CLI model override for the active provider. null = the
  // CLI's own default. Reset when the provider changes.
  const [activeModel, setActiveModel] = useState<string | null>(null);
  // Two-tab scope: the selected canvas | project (D-2026-06-13-H).
  const [scopeMode, setScopeMode] = useState<"canvas" | "project">("canvas");
  const effectiveScope: ChatScope =
    scopeMode === "project" ? "project" : activeScope;
  // Provider connection is a setup step kept behind a compact chip, collapsed
  // by default (D-2026-06-14-D).
  const [providersOpen, setProvidersOpen] = useState(false);

  useEffect(() => {
    if (!workspaceRoot) return;
    void getChatProvider(workspaceRoot).then(
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
      // A model valid for one CLI is meaningless for another (D-2026-06-16-C).
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

  const connected = Boolean(activeProvider && workspaceRoot);

  return (
    <aside
      aria-label={t("chat.dockTitle")}
      className="flex h-full w-full flex-col bg-surface"
    >
      {/* Top conversation bar — model selector (the prominent control, like a
          modern chat app) on the left, the provider connection chip on the
          right. When no agent is connected the chip fills the bar as the
          call-to-connect. */}
      <div className="flex items-center gap-2 border-b border-line px-3 py-2">
        {connected && (
          <ChatModelSelector
            provider={activeProvider!}
            model={activeModel}
            onChange={handleSelectModel}
          />
        )}
        <button
          type="button"
          aria-label={t("chat.providersBarLabel")}
          aria-expanded={providersOpen}
          data-connected={activeProvider ? "1" : "0"}
          onClick={() => setProvidersOpen((o) => !o)}
          className={
            "flex items-center gap-2 rounded-md px-2 py-1 text-[11px] text-fg-muted hover:bg-surface-muted hover:text-fg-strong " +
            (connected ? "ml-auto shrink-0" : "w-full justify-between")
          }
          title={t("chat.providersBarLabel")}
        >
          <span className="flex min-w-0 items-center gap-1.5">
            <span
              aria-hidden
              className={
                activeProvider
                  ? "h-1.5 w-1.5 shrink-0 rounded-full bg-ok"
                  : "h-1.5 w-1.5 shrink-0 rounded-full border border-fg-muted"
              }
            />
            <span className={activeProvider ? "truncate font-medium text-fg-strong" : "truncate"}>
              {activeProvider ? t(`chat.providers.${activeProvider}`) : t("chat.providersTitle")}
            </span>
          </span>
          <span aria-hidden className="text-fg-faint">{providersOpen ? "▾" : "▸"}</span>
        </button>
      </div>

      {providersOpen && (
        <div className="overflow-y-auto border-b border-line p-3">
          <ChatProvidersPanel onError={onError} {...selectionProps} />
        </div>
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
    </aside>
  );
}

/**
 * Model selector (D-2026-06-16-C, reshaped as a top dropdown D-2026-06-16-D).
 * A dropdown of per-CLI suggestions + a "Custom…" entry that swaps to a
 * free-text input (so any model id the CLI accepts can be typed). The current
 * model — even a custom one — is always an option so the dropdown reflects it.
 * Empty = the CLI's own default.
 */
function ChatModelSelector({
  provider,
  model,
  onChange,
}: {
  provider: McpProviderName;
  model: string | null;
  onChange: (model: string | null) => void;
}) {
  const { t } = useTranslation();
  const suggestions = MODEL_SUGGESTIONS[provider] ?? [];
  const [customMode, setCustomMode] = useState(false);
  // Leaving custom mode whenever the provider changes keeps the control honest.
  useEffect(() => setCustomMode(false), [provider]);

  if (customMode) {
    const commit = (raw: string) => {
      setCustomMode(false);
      onChange(raw.trim() || null);
    };
    return (
      <input
        aria-label={t("chat.modelLabel")}
        autoFocus
        defaultValue={model ?? ""}
        placeholder={t("chat.modelPlaceholder")}
        onBlur={(e) => commit(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            commit((e.target as HTMLInputElement).value);
          } else if (e.key === "Escape") {
            setCustomMode(false);
          }
        }}
        className="min-w-0 max-w-[60%] flex-1 rounded-md border border-line bg-surface-muted px-2 py-1 text-[11px] text-fg focus:border-accent focus:outline-none"
      />
    );
  }

  return (
    <select
      aria-label={t("chat.modelLabel")}
      value={model ?? ""}
      onChange={(e) => {
        if (e.target.value === CUSTOM_MODEL_OPTION) {
          setCustomMode(true);
          return;
        }
        onChange(e.target.value || null);
      }}
      className="min-w-0 max-w-[60%] rounded-md border border-line bg-surface-muted px-2 py-1 text-[11px] font-medium text-fg-strong hover:bg-surface-subtle focus:border-accent focus:outline-none"
    >
      <option value="">{t("chat.modelDefaultShort")}</option>
      {suggestions.map((s) => (
        <option key={s} value={s}>
          {s}
        </option>
      ))}
      {model && !suggestions.includes(model) && <option value={model}>{model}</option>}
      <option value={CUSTOM_MODEL_OPTION}>{t("chat.modelCustom")}</option>
    </select>
  );
}

/**
 * Two-tab chat scope switcher: the selected canvas | project (D-2026-06-13-H).
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
 * Live message surface — the bubble list, the composer, and a thin status
 * line. The data-state / data-streaming attributes are stable e2e hooks.
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

  const providerLabel = activeProvider ? t(`chat.providers.${activeProvider}`) : "";
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

  const submit = useCallback(() => {
    if (!canSubmit) return;
    const text = draft;
    setDraft("");
    void send(text);
  }, [canSubmit, draft, send]);

  const handleSubmit = useCallback(
    (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      submit();
    },
    [submit],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Enter sends; Shift+Enter inserts a newline.
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submit();
      }
    },
    [submit],
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
        className="flex flex-1 flex-col gap-3 overflow-y-auto p-3"
      >
        {!workspaceRoot ? (
          <p className="m-auto max-w-[80%] text-center text-xs text-fg-muted">
            {t("chat.noWorkspace")}
          </p>
        ) : messages.length === 0 ? (
          <p className="m-auto max-w-[80%] text-center text-xs text-fg-muted">
            {t("chat.emptyMessages")}
          </p>
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
      <form className="border-t border-line p-3" onSubmit={handleSubmit}>
        <div className="flex items-end gap-2 rounded-2xl border border-line bg-surface-muted p-2 focus-within:border-accent">
          <textarea
            aria-label={t("chat.inputLabel")}
            placeholder={placeholder}
            disabled={!workspaceRoot || activeProvider === null}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            className="max-h-40 min-h-[1.75rem] flex-1 resize-none bg-transparent px-1 py-1 text-sm text-fg placeholder:text-fg-faint focus:outline-none disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={!canSubmit}
            aria-label={t("chat.send")}
            data-state={isStreaming ? "streaming" : "idle"}
            className={
              "grid h-8 w-8 shrink-0 place-items-center rounded-full text-sm font-semibold transition-opacity " +
              (canSubmit
                ? "bg-surface-inverse text-fg-inverse hover:opacity-90"
                : "cursor-not-allowed bg-surface-subtle text-fg-faint")
            }
          >
            <span aria-hidden>↑</span>
          </button>
        </div>
      </form>
    </>
  );
}

function ChatMessageRow({ message }: { message: ChatMessage }) {
  const { t } = useTranslation();
  const isUser = message.role === "user";
  const isError = message.status === "error";
  const bubble = isUser
    ? "rounded-br-sm bg-surface-inverse text-fg-inverse"
    : isError
      ? "rounded-bl-sm border border-warn-line bg-warn-soft text-warn-fg"
      : "rounded-bl-sm border border-line bg-surface-muted text-fg-strong";
  return (
    <div
      data-role={message.role}
      data-status={message.status}
      className={"flex flex-col " + (isUser ? "items-end" : "items-start")}
    >
      <span className="mb-0.5 px-1 text-[10px] font-medium uppercase tracking-wide text-fg-faint">
        {isUser ? t("chat.you") : t("chat.assistant")}
      </span>
      <div className={"max-w-[88%] rounded-2xl px-3 py-2 text-xs leading-relaxed " + bubble}>
        {message.status === "streaming" && message.text === "" ? (
          // No tokens yet — the CLI is spawning / thinking. Keep it alive
          // (D-2026-06-16-B).
          <ChatActivityIndicator />
        ) : (
          <p className="whitespace-pre-wrap break-words">
            {message.text}
            {message.status === "streaming" && (
              <span aria-hidden className="ml-0.5 inline-block animate-pulse">
                ▍
              </span>
            )}
          </p>
        )}
        {isError && message.errorMessage && (
          <p className="mt-1 text-[11px] opacity-80">
            {t("chat.errorPrefix")}
            {message.errorMessage}
          </p>
        )}
      </div>
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
    <div className="flex items-center justify-between gap-2 px-3 pb-0 pt-1 text-[10px] text-fg-muted">
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
