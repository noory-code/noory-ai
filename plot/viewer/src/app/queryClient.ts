/**
 * TanStack Query client (D-2026-06-08-A, step 6).
 *
 * Server state (canvases, project list, published versions, dir tree) lives
 * here, ABOVE the `api.ts` engine seam — so when the engine moves in-process
 * (tablet, TS), only `api.ts` / `src/app` change, not the cache layer.
 *
 * Defaults tuned for a LOCAL engine: no refetch-on-window-focus (the WebSocket
 * already drives external-change refresh), short retry, modest staleTime.
 */
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30_000,
    },
  },
});
