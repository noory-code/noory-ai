/**
 * Workspace use-cases (D-2026-06-08-A, step 4).
 *
 * Application-layer seam over the engine's workspace endpoints + the pure
 * URL-derived workspace root. Presentation imports these from here, not from
 * `../api`. Thin today; logic lands here, not in components.
 */
export { resolveWorkspaceRoot, getDirTree, createWorkspaceDir } from "../api";
export type { DirTreeNode, DirTreeResponse } from "../api";
