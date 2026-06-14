/**
 * R7 chat provider panel (D-2026-06-11-E, Phase A + Phase B step B3).
 *
 * Lists the three external CLIs Plot can drive (Claude Code / Codex /
 * Gemini), surfaces install state + Plot-registration state, and exposes
 * one-click register / unregister buttons. Phase B step B3 adds an
 * optional active-provider radio per row (controlled by the parent —
 * persistence lives at the dock level so the panel stays a presentation
 * component).
 */
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  getMcpProviders,
  registerMcpProvider,
  unregisterMcpProvider,
  type McpProviderName,
  type McpProviderStatus,
} from "../app/mcp";

// claude-code is excluded from the in-app chat provider SELECTION
// (D-2026-06-13-H): driving it via ``claude -p`` double-charges a Claude
// subscriber. Its row stays so the user can still MCP-register it and connect
// their own interactive Claude session — only the chat radio is suppressed.
const CHAT_SELECTION_EXCLUDED: McpProviderName = "claude-code";

export interface ChatProvidersPanelProps {
  onError: (message: string) => void;
  /** When defined together with `onSelectProvider`, the panel shows a radio
   * per row for active-provider selection. Omit both to suppress the
   * selection UI (Phase A backwards-compat). */
  activeProvider?: McpProviderName | null;
  onSelectProvider?: (name: McpProviderName | null) => void;
}

export function ChatProvidersPanel({
  onError,
  activeProvider,
  onSelectProvider,
}: ChatProvidersPanelProps) {
  const { t } = useTranslation();
  const [providers, setProviders] = useState<McpProviderStatus[] | null>(null);
  const [busy, setBusy] = useState<McpProviderName | null>(null);

  const selectionEnabled = activeProvider !== undefined && onSelectProvider !== undefined;

  const refresh = async () => {
    try {
      setProviders(await getMcpProviders());
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
    }
  };

  useEffect(() => {
    void refresh();
    // refresh on mount only — the user explicitly toggles via the
    // register/unregister buttons, which call refresh themselves.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRegister = async (name: McpProviderName) => {
    setBusy(name);
    try {
      await registerMcpProvider(name);
      await refresh();
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(null);
    }
  };

  const handleUnregister = async (name: McpProviderName) => {
    setBusy(name);
    try {
      await unregisterMcpProvider(name);
      // If the row we just unregistered was the active provider, clear
      // the selection — the active choice must remain valid against the
      // user's current set of registered CLIs.
      if (selectionEnabled && activeProvider === name) {
        onSelectProvider!(null);
      }
      await refresh();
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(null);
    }
  };

  if (providers === null) {
    return (
      <div className="text-sm text-fg-muted" role="status">
        {t("chat.loadingProviders")}
      </div>
    );
  }

  return (
    <section aria-labelledby="chat-providers-heading" className="space-y-3">
      <header>
        <h2
          id="chat-providers-heading"
          className="text-sm font-semibold text-fg-strong"
        >
          {t("chat.providersTitle")}
        </h2>
        <p className="text-xs text-fg-muted">{t("chat.providersHint")}</p>
      </header>
      <ul className="space-y-2">
        {providers.map((p) => (
          <li
            key={p.name}
            className="flex items-center justify-between gap-2 rounded border border-line bg-surface px-3 py-2"
          >
            <div className="flex items-center gap-2">
              {selectionEnabled && p.name !== CHAT_SELECTION_EXCLUDED && (
                <input
                  type="radio"
                  name="chat-active-provider"
                  value={p.name}
                  checked={activeProvider === p.name}
                  disabled={!p.registered}
                  onChange={() => onSelectProvider!(p.name)}
                  aria-label={t("chat.selectActive", {
                    name: t(`chat.providers.${p.name}`),
                  })}
                  className="h-3.5 w-3.5"
                />
              )}
              <div>
                <div className="text-sm font-medium text-fg-strong">
                  {t(`chat.providers.${p.name}`)}
                </div>
                <ProviderStatusBadge status={p} />
              </div>
            </div>
            <ProviderActions
              status={p}
              busy={busy === p.name}
              onRegister={() => void handleRegister(p.name)}
              onUnregister={() => void handleUnregister(p.name)}
            />
          </li>
        ))}
      </ul>
    </section>
  );
}

function ProviderStatusBadge({ status }: { status: McpProviderStatus }) {
  const { t } = useTranslation();
  if (!status.installed) {
    return (
      <span className="text-xs text-fg-faint">
        {t("chat.providerNotInstalled")}
      </span>
    );
  }
  if (status.registered) {
    return <span className="text-xs text-ok-fg">{t("chat.providerRegistered")}</span>;
  }
  return <span className="text-xs text-fg-muted">{t("chat.providerInstalled")}</span>;
}

function ProviderActions({
  status,
  busy,
  onRegister,
  onUnregister,
}: {
  status: McpProviderStatus;
  busy: boolean;
  onRegister: () => void;
  onUnregister: () => void;
}) {
  const { t } = useTranslation();
  if (!status.installed) return null;
  if (status.registered) {
    return (
      <button
        type="button"
        onClick={onUnregister}
        disabled={busy}
        className="rounded border border-line-strong px-2 py-1 text-xs text-fg hover:bg-surface-muted disabled:opacity-50"
      >
        {t("chat.unregister")}
      </button>
    );
  }
  return (
    <button
      type="button"
      onClick={onRegister}
      disabled={busy}
      className="rounded border border-accent bg-accent-soft px-2 py-1 text-xs font-medium text-accent-fg hover:bg-accent hover:text-fg-inverse disabled:opacity-50"
    >
      {t("chat.register")}
    </button>
  );
}
