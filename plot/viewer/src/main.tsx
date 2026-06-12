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

// D-2026-06-12-F — resolve + apply the engine auth token before any fetch
// fires. Failing to do so under the bundled Tauri shell would cause the
// initial /api/projects call to 401 → React Query retry → eventual recovery
// but with a visible flash. The promise is fire-and-forget; the first
// fetches are React effects that run after render anyway, so they always
// see the token by the time they evaluate.
void initEngineAuth();

ReactDOM.createRoot(root).render(
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

// D-2026-06-09-D — dev-only screen-snapshot probe (no-op unless VITE_PLOT_DEBUG=1 / ?debug)
startDebugProbe();
