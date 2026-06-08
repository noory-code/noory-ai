/**
 * Shared test render helpers (D-2026-06-08-A, step 6).
 *
 * Components that use TanStack Query (`useQuery` / `useMutation`) need a
 * `QueryClientProvider` in the tree. `renderWithProviders` wraps render() with
 * a fresh, retry-disabled QueryClient so tests don't share cache or hang on
 * retries. Use it instead of bare `render()` for any component that reads
 * server state.
 */
import { type ReactElement, type ReactNode } from "react";
import { render, type RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export function makeTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
}

export function renderWithProviders(ui: ReactElement, options?: Omit<RenderOptions, "wrapper">) {
  const client = makeTestQueryClient();
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  }
  return { client, ...render(ui, { wrapper: Wrapper, ...options }) };
}

/** A `wrapper` for `renderHook`, bound to a fresh retry-disabled client.
 *  Use for hooks that read server state (e.g. `useProject`). */
export function makeQueryWrapper() {
  const client = makeTestQueryClient();
  return function QueryWrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  };
}
