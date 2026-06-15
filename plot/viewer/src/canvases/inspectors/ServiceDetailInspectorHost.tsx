/**
 * ServiceDetail fallback inspector host (D-2026-06-15-O).
 *
 * The ServiceDetail canvas's default right panel = the subject service's
 * READ-ONLY inspector. The service node itself lives on the **Services**
 * canvas (the detail canvas only holds its actor/interaction/value peers —
 * D-2026-05-28-B), so this host reads it cross-doc from the Services
 * ``CanvasDoc`` the App already has cached and renders the regular
 * ``KindInspector`` with ``readOnly`` set.
 *
 * Mounted as ``SketchInspectorBindings``' ``fallbackInspector`` — shown when
 * no detail node is selected (selecting one swaps in that node's editable
 * inspector; clicking empty space returns here). Dependency direction is
 * clean: this is an Execution-context view reading Planning-context data
 * passed down as props — no cross-canvas import.
 *
 * Guard: renders nothing when the service is missing (deleted on the
 * Services canvas, or an unknown id) — the detail tab can outlive its
 * service.
 */
import type { CanvasDoc, SketchNode } from "../../types";
import { KindInspector } from "./KindInspector";

const NOOP = (): void => {};

export interface ServiceDetailInspectorHostProps {
  /** Id of the service this detail canvas belongs to (``doc.service_ref``). */
  serviceId: string;
  /** The cached Services ``CanvasDoc`` (App holds it; null while loading). */
  servicesCanvas: CanvasDoc | null;
  projectPath: string;
  projectId: string;
}

export function ServiceDetailInspectorHost({
  serviceId,
  servicesCanvas,
  projectPath,
  projectId,
}: ServiceDetailInspectorHostProps) {
  const nodes: SketchNode[] = servicesCanvas?.nodes ?? [];
  const service = nodes.find((n) => n.id === serviceId && n.kind === "service") ?? null;
  if (!service) return null;
  return (
    <KindInspector
      node={service}
      allNodes={nodes}
      allEdges={servicesCanvas?.edges ?? []}
      readOnly
      onPatchNode={NOOP}
      onDeleteNode={NOOP}
      onClose={NOOP}
      projectPath={projectPath}
      projectId={projectId}
      canvasKind="services"
    />
  );
}
