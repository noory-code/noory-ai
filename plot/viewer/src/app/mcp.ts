/**
 * R7 MCP provider use-cases (D-2026-06-11-E, Track 2.5).
 *
 * The application-layer seam over the engine's `/api/mcp/*` endpoints.
 * Presentation imports MCP operations from here, never from `../api`
 * directly — same rule the rest of the use-case ring follows. Enforced by
 * the api-seam guard in `structural-guards.test.tsx`.
 */
export {
  getChatProvider,
  getMcpProviders,
  registerMcpProvider,
  setChatProvider,
  unregisterMcpProvider,
  type ChatProviderSelection,
  type McpProviderName,
  type McpProviderStatus,
} from "../api";
