/**
 * Files use-cases (D-2026-06-08-A, step 4).
 *
 * The application-layer seam over the engine's file endpoints. Presentation
 * imports file operations from here, never from `../api` directly — so when
 * the engine moves in-process (tablet), only this layer + the data hooks
 * change. Enforced by the api-seam guard in `structural-guards.test.tsx`.
 *
 * Thin today (re-exports); use cases gain logic here, not in components.
 */
export { readFile, writeFile, createFolder, rawFileUrl } from "../api";
