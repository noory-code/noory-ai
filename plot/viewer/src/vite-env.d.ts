/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Engine HTTP origin (e.g. "http://127.0.0.1:5190") when the frontend is
   *  bundled separately from the engine (Tauri desktop app). Unset = same-origin. */
  readonly VITE_PLOT_ENGINE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
