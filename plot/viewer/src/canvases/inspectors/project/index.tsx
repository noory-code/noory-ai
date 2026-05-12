/**
 * Per-kind inspector for ``project`` Foundation anchor nodes.
 * v0.15 Phase 2.5.
 *
 * The project anchor has no kind-specific typed body — its label
 * mirrors ``ProjectDoc.name`` and the rest is BaseInspector chrome.
 */
import { BaseInspector } from "../BaseInspector";
import type { KindInspectorProps } from "../types";

export function ProjectInspector(props: KindInspectorProps) {
  // No per-kind body — the chrome (label input + DetailsSection) is
  // the entire panel for the project anchor.
  return <BaseInspector {...props} />;
}
