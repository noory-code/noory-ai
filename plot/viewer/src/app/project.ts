/**
 * Project use-cases (D-2026-06-08-A, step 4).
 *
 * Application-layer seam over project-level engine mutations. Presentation
 * imports these from here, not from `../api`. Thin today; logic lands here.
 */
export { patchProjectAnchor } from "../api";
