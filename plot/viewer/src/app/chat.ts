/**
 * R7 chat streaming use-cases (D-2026-06-12-D, Phase C).
 *
 * Application-layer seam over the engine's ``/api/chat/send`` +
 * ``/api/chat/reset`` endpoints. Presentation imports the streaming
 * functions from here, never from ``../api`` directly — the api-seam guard
 * in ``structural-guards.test.tsx`` blocks the latter. Sibling to
 * ``app/mcp.ts`` (provider selection + registration); split because the
 * chat-streaming surface keeps growing (verbose Phase C, todo: tool-use
 * frames, model indicator) and the registration surface is feature-frozen.
 */
export {
  resetChatSession,
  sendChatMessage,
  type ChatStreamEventType,
  type ChatStreamPayload,
} from "../api";
