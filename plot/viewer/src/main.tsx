import React from "react";
import ReactDOM from "react-dom/client";
import "reactflow/dist/style.css";
import { QueryClientProvider } from "@tanstack/react-query";
import { App } from "./App";
import { queryClient } from "./app/queryClient";
import { DialogProvider } from "./shell/dialog/DialogProvider";
import { ThemeProvider } from "./theme/ThemeProvider";
import "./i18n";
import "./styles.css";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("#root element missing");
}

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
