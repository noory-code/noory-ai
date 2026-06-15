/**
 * Viewer-context bridge use-case (D-2026-06-15-D).
 *
 * Application-layer seam over the engine's ``POST /api/viewer/context``.
 * Presentation imports ``reportViewerContext`` from here, never from
 * ``../api`` directly — the api-seam guard in ``structural-guards.test.tsx``
 * blocks the latter. Sibling to ``app/chat.ts``.
 */
export { reportViewerContext } from "../api";
