/**
 * Inspector resolver. Picks the per-kind inspector component for the
 * currently-selected node and renders it.
 *
 * Phase 2.0: registry is empty, so this always returns ``null``. Callers
 * (legacy ``SketchInspector``, eventually ``SketchInspectorBindings``)
 * use the result as an "is this kind already migrated?" probe and fall
 * back to the legacy inline branches when ``null``.
 *
 * Phase 2.1+: each per-kind commit registers its inspector; this
 * component starts handing out the correct per-kind UI for those kinds.
 */
import { lookupKindInspector } from "./registry";
import type { KindInspectorProps } from "./types";

export function KindInspector(props: KindInspectorProps) {
  const Component = lookupKindInspector(props.node.kind);
  if (!Component) {
    return null;
  }
  return <Component {...props} />;
}
