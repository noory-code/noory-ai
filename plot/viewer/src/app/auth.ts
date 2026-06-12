/**
 * Engine auth bootstrap (D-2026-06-12-F + TABLET_ARCH §"지금 만들 것").
 *
 * Application-layer entry point that resolves the engine auth token at app
 * boot and hands it to ``api.ts::setEngineAuthToken``. Source priority:
 *
 *   1. Tauri shell — ``invoke('plot_auth_token')`` returns the token the
 *      Rust ``setup`` hook minted and also injected into the sidecar's
 *      ``PLOT_AUTH_TOKEN`` env. Bundled desktop path.
 *   2. Dev opt-in — ``VITE_PLOT_AUTH_TOKEN`` at build time (the same value
 *      the contributor exported as ``PLOT_AUTH_TOKEN`` before launching
 *      the engine). Lets a developer rehearse the enforced path without
 *      Tauri.
 *   3. Fall through — no token. Engine is in dev mode (env unset), every
 *      request passes through; v0.64.x byte-identical behaviour.
 *
 * Presentation calls ``initEngineAuth`` once from ``main.tsx`` before the
 * first render. After that, ``api.ts`` adds ``Authorization: Bearer
 * <token>`` to every fetch and ``?auth=<token>`` to the WS URL.
 */
import { setEngineAuthToken } from "../api";

interface TauriInvokeable {
  invoke: (cmd: string, args?: Record<string, unknown>) => Promise<unknown>;
}

function getTauriInternals(): TauriInvokeable | null {
  // ``Window.__TAURI_INTERNALS__`` is declared as ``unknown`` elsewhere
  // (see ``shell/ProjectPicker.tsx``), so we narrow at the call site
  // instead of re-declaring the global with a tighter type.
  const raw = (window as { __TAURI_INTERNALS__?: unknown })
    .__TAURI_INTERNALS__;
  if (raw === undefined || raw === null) return null;
  const maybeInvoke = (raw as { invoke?: unknown }).invoke;
  if (typeof maybeInvoke !== "function") return null;
  return raw as TauriInvokeable;
}

const TAURI_COMMAND = "plot_auth_token";

async function resolveTauriToken(): Promise<string | null> {
  const internals = getTauriInternals();
  if (internals === null) return null;
  try {
    const value = await internals.invoke(TAURI_COMMAND);
    return typeof value === "string" && value.length > 0 ? value : null;
  } catch {
    // The shell may be older than the v0.65.0 invoke handler — fall through
    // silently. The bundled engine refuses requests in that case, but the
    // failure mode is "401" which is much louder than a swallowed error.
    return null;
  }
}

function resolveDevToken(): string | null {
  const raw = import.meta.env.VITE_PLOT_AUTH_TOKEN as string | undefined;
  return raw && raw.length > 0 ? raw : null;
}

/** Resolve + apply the auth token. Idempotent — calling twice is a no-op
 *  on the second call when both sources return the same value. */
export async function initEngineAuth(): Promise<void> {
  const tauri = await resolveTauriToken();
  if (tauri !== null) {
    setEngineAuthToken(tauri);
    return;
  }
  const dev = resolveDevToken();
  setEngineAuthToken(dev); // ``null`` is fine — keeps dev parity.
}
