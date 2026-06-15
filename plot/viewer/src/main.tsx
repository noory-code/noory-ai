import React from "react";
import ReactDOM from "react-dom/client";
import "reactflow/dist/style.css";
import { QueryClientProvider } from "@tanstack/react-query";
import { App } from "./App";
import { initEngineAuth } from "./app/auth";
import { queryClient } from "./app/queryClient";
import { DialogProvider } from "./shell/dialog/DialogProvider";
import { ThemeProvider } from "./theme/ThemeProvider";
import { startDebugProbe } from "./lib/debugProbe";
import "./i18n";
import "./styles.css";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("#root element missing");
}

// D-2026-06-12-F / D-2026-06-15-G — resolve + apply the engine auth token
// BEFORE the first render, awaited. The Tauri ``invoke('plot_auth_token')`` is
// an IPC round-trip; a fire-and-forget call loses the race against the first
// ``/api/projects`` effect under the bundled/dev shell → 401 → the workspace
// never loads. Awaiting trades a brief pre-token blank for a correct boot.
async function boot(rootEl: HTMLElement): Promise<void> {
  await initEngineAuth();
  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <DialogProvider>
            <App />
          </DialogProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </React.StrictMode>,
  );
  // D-2026-06-09-D — dev screen-snapshot probe (no-op unless VITE_PLOT_DEBUG=1 / ?debug)
  startDebugProbe();
}

void boot(root);
