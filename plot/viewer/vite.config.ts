import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: false,
  },
  server: {
    port: 5193,
    proxy: {
      "/api": "http://127.0.0.1:5190",
      "/ws": {
        target: "ws://127.0.0.1:5190",
        ws: true,
      },
    },
  },
});
