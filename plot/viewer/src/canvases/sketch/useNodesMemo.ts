// Doc → React Flow nodes transform. Owns:
//  - the parents-before-children sort (SPEC §Rendering order)
//  - hidden-node rules (collapsed ancestor, rule/content kinds, the
//    service-detail's redundant root)
//  - orphan-actor_ref visual override (red tint + ⚠ prefix)
//  - master-derived label sync for ref kinds
//  - service.target_side body tint
//  - drill routing for service / actor_ref kinds
//  - synthetic project anchor injection (SPEC §Anchor)
//
// Kept as a single hook (not a pure module + thin wrapper) because the
// transform reads ten-plus callbacks; a "pure" form would just shuffle
// arguments. See D-2026-05-08-B in DECISIONS.md.
import { type Dispatch, type SetStateAction, useMemo } from "react";
import { type Node } from "reactflow";
import type {
  AnchorPlacement,
  CanvasDoc,
  CanvasKind,
  SketchNode as DocNode,
} from "../../types";
import { type SketchNodeData } from "../SketchNode";
import { PROJECT_ANCHOR_ID } from "./constants";

export interface UseNodesMemoArgs {
  doc: CanvasDoc;
  childIdsByParent: Map<string, string[]>;
  nearestCollapsedAncestor: (id: string) => string | null;
  subtreeSize: (id: string) => number;
  toggleCollapsed: (id: string) => void;
  updateNode: (id: string, patch: Partial<DocNode>) => void;
  orphanActorRefIds: Set<string>;
  availableActors: DocNode[] | undefined;
  availableMissions: DocNode[] | undefined;
  availableValues: DocNode[] | undefined;
  availableIdentities: DocNode[] | undefined;
  onNodeDrill: ((nodeId: string) => void) | undefined;
  projectAnchor: AnchorPlacement | null | undefined;
  projectName: string | null | undefined;
  onAnchorChange:
    | ((patch: Partial<AnchorPlacement>) => void)
    | undefined;
  setBodyModalNodeId: Dispatch<SetStateAction<string | null>>;
}

const ANCHOR_KINDS: ReadonlySet<CanvasKind> = new Set([
  "foundation",
  "actors",
  "services",
]);

export function useNodesMemo({
  doc,
  childIdsByParent,
  nearestCollapsedAncestor,
  subtreeSize,
  toggleCollapsed,
  updateNode,
  orphanActorRefIds,
  availableActors,
  availableMissions,
  availableValues,
  availableIdentities,
  onNodeDrill,
  projectAnchor,
  projectName,
  onAnchorChange,
  setBodyModalNodeId,
}: UseNodesMemoArgs): Node<SketchNodeData>[] {
  return useMemo<Node<SketchNodeData>[]>(() => {
    // SPEC §Rendering order: parents first, children after. React
    // Flow uses array order to resolve parentNode references on the
    // first paint.
    const ordered = [...doc.nodes].sort((a, b) => {
      if (!a.parent_id && b.parent_id) return -1;
      if (a.parent_id && !b.parent_id) return 1;
      return 0;
    });
    const out: Node<SketchNodeData>[] = [];
    for (const n of ordered) {
      // Hide nodes whose ancestor chain contains a collapsed container.
      if (nearestCollapsedAncestor(n.id)) continue;
      // v0.2 correction (2026-04-20): rule / content are edited
      // through the right-hand Inspector panel, never on the canvas.
      if (n.kind === "rule" || n.kind === "content") continue;
      // v0.12.2: inside the service-detail modal the service-root
      // is redundant — the modal header already names it.
      if (
        doc.canvas_kind === "service_detail" &&
        doc.service_ref &&
        n.id === doc.service_ref
      ) {
        continue;
      }
      const hasChildren = (childIdsByParent.get(n.id)?.length ?? 0) > 0;
      const isOrphan = orphanActorRefIds.has(n.id);
      // v0.11.1 — for ref kinds, derive the displayed label from the
      // master so renames propagate without a server round-trip.
      const masterDerivedLabel = ((): string | null => {
        if (n.kind === "actor_ref" && n.ref_actor_id) {
          const m = (availableActors ?? doc.nodes).find((a) => a.id === n.ref_actor_id);
          if (m) return `→ ${m.label || m.id}`;
        }
        if (n.kind === "mission_ref" && n.ref_mission_id) {
          const m = (availableMissions ?? []).find((a) => a.id === n.ref_mission_id);
          if (m) return `→ ${m.label || m.id}`;
        }
        if (n.kind === "value_ref" && n.ref_value_id) {
          const m = (availableValues ?? []).find((a) => a.id === n.ref_value_id);
          if (m) return `→ ${m.label || m.id}`;
        }
        if (n.kind === "identity_ref" && n.ref_identity_id) {
          const m = (availableIdentities ?? []).find((a) => a.id === n.ref_identity_id);
          if (m) return `→ ${m.label || m.id}`;
        }
        return null;
      })();
      const baseLabel = masterDerivedLabel ?? n.label;
      // v0.11.4 — service.target_side tints the body so operator-
      // facing services and user-facing services read at a glance.
      let visualColor: string = isOrphan ? "#fee2e2" : n.color;
      if (!isOrphan && n.kind === "service" && n.target_side != null) {
        if (n.target_side === "operator") visualColor = "#dbeafe";
        else if (n.target_side === "user") visualColor = "#fee2e2";
        else if (n.target_side === "both") visualColor = "#ede9fe";
      }
      const visualLabel = isOrphan ? `⚠ ${baseLabel}` : baseLabel;
      // v0.12.1 — kinds whose double-click should drill (not open the
      // generic edit modal) get onDrill wired. SketchNode's dblclick
      // prefers drill when set.
      const drillThisNode =
        (doc.canvas_kind === "services" && n.kind === "service" && !n.is_root) ||
        (doc.canvas_kind === "service_detail" && n.kind === "actor_ref");
      const onDrill = drillThisNode && onNodeDrill ? () => onNodeDrill(n.id) : undefined;
      out.push({
        id: n.id,
        type: "sketch",
        position: { x: n.x, y: n.y },
        style: { width: n.width, height: n.height },
        data: {
          label: visualLabel,
          body: "",
          color: visualColor,
          width: n.width,
          height: n.height,
          shape: n.shape,
          icon: n.icon,
          kind: n.kind,
          onLabelChange: (next: string) => updateNode(n.id, { label: next }),
          onOpenBody: () => setBodyModalNodeId(n.id),
          onDrill,
          onResize: (w: number, h: number) => updateNode(n.id, { width: w, height: h }),
          hasChildren,
          collapsed: n.collapsed,
          childCount: hasChildren ? subtreeSize(n.id) : 0,
          onToggleCollapse: hasChildren ? () => toggleCollapsed(n.id) : undefined,
          // Foundation lays pillars out as peers — fold has no meaning.
          showFold: doc.canvas_kind !== "foundation",
          mdWarnings: n._md_warnings,
        },
      });
    }
    // SPEC §Anchor — synthetic project anchor injected on every primary
    // canvas kind (foundation / actors / services). Mutation routes via
    // onAnchorChange, NEVER via onDocChange.
    if (projectAnchor && ANCHOR_KINDS.has(doc.canvas_kind)) {
      out.unshift({
        id: PROJECT_ANCHOR_ID,
        type: "sketch",
        position: { x: projectAnchor.x, y: projectAnchor.y },
        style: { width: projectAnchor.width, height: projectAnchor.height },
        data: {
          label: projectName ?? "Project",
          body: "",
          color: projectAnchor.color,
          width: projectAnchor.width,
          height: projectAnchor.height,
          shape: projectAnchor.shape,
          icon: null,
          kind: "project",
          onResize: (w: number, h: number) => onAnchorChange?.({ width: w, height: h }),
          showFold: false,
        },
      });
    }
    return out;
  }, [
    doc.nodes,
    doc.canvas_kind,
    doc.service_ref,
    childIdsByParent,
    nearestCollapsedAncestor,
    subtreeSize,
    toggleCollapsed,
    updateNode,
    orphanActorRefIds,
    availableActors,
    availableMissions,
    availableValues,
    availableIdentities,
    onNodeDrill,
    projectAnchor,
    projectName,
    onAnchorChange,
    setBodyModalNodeId,
  ]);
}
