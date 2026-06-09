/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Engine HTTP origin (e.g. "http://127.0.0.1:5190") when the frontend is
   *  bundled separately from the engine (Tauri desktop app). Unset = same-origin. */
  readonly VITE_PLOT_ENGINE?: string;
  /** Dev-only debug probe (D-2026-06-09-D): "1" enables the screen-snapshot
   *  POST to /api/debug. Also enabled by a `?debug` URL param. */
  readonly VITE_PLOT_DEBUG?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
