// Doc → React Flow nodes transform. Owns:
//  - the parents-before-children sort (SPEC §Rendering order)
//  - hidden-node rules (collapsed ancestor, rule/content kinds, the
//    service-detail's redundant root)
//  - orphan-actor_ref visual override (red tint + ⚠ prefix)
//  - master-derived label sync for ref kinds
//  - service.target_side body tint
//  - drill routing for the kinds the parent canvas wrapper opts in
//  - synthetic project anchor injection (SPEC §Anchor)
//
// v0.15 Phase 3.4 — the four canvas_kind switches that used to live
// here moved out to per-canvas wrapper props (hideRootServiceNode,
// shouldDrill, showFoldButton, injectAnchor). The transform itself
// no longer reads ``doc.canvas_kind``.
//
// Kept as a single hook (not a pure module + thin wrapper) because the
// transform reads ten-plus callbacks; a "pure" form would just shuffle
// arguments. See D-2026-05-08-B in DECISIONS.md.
import { type Dispatch, type SetStateAction, useMemo } from "react";
import { type Node } from "reactflow";
import type {
  AnchorPlacement,
  CanvasDoc,
  SketchNode as DocNode,
} from "../../types";
import type { BaseNodeData } from "../nodes/BaseNode";
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
  /** v0.15 Phase 3.4 — drop the canvas's root-service node from the
   *  rendered list (true on ServiceDetailCanvas where the modal
   *  header already names the service). */
  hideRootServiceNode: boolean;
  /** v0.15 Phase 3.4 — predicate the wrapper supplies to opt nodes
   *  into double-click drill. ServicesCanvas: ``service && !is_root``;
   *  ServiceDetailCanvas: ``actor_ref``. Foundation / Actors leave
   *  this undefined so no node drills. */
  shouldDrill: ((node: DocNode) => boolean) | undefined;
  /** v0.15 Phase 3.4 — render the fold (▾/▸) button on container
   *  nodes. Foundation lays pillars out as peers — fold has no
   *  meaning there. */
  showFoldButton: boolean;
  /** v0.15 Phase 3.4 — inject the synthetic project anchor at the
   *  top of the node list. False on ServiceDetailCanvas (the modal
   *  has its own header). */
  injectAnchor: boolean;
}

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
  hideRootServiceNode,
  shouldDrill,
  showFoldButton,
  injectAnchor,
}: UseNodesMemoArgs): Node<BaseNodeData>[] {
  return useMemo<Node<BaseNodeData>[]>(() => {
    // SPEC §Rendering order: parents first, children after. React
    // Flow uses array order to resolve parentNode references on the
    // first paint. v0.26.0 (D-2026-05-25-A): parent-child is now
    // derived from directed edges. A node is a "child" iff there's
    // an incoming directed edge.
    const childIds = new Set<string>();
    for (const e of doc.edges) {
      if (e.directed) childIds.add(e.target);
    }
    const ordered = [...doc.nodes].sort((a, b) => {
      const aChild = childIds.has(a.id);
      const bChild = childIds.has(b.id);
      if (!aChild && bChild) return -1;
      if (aChild && !bChild) return 1;
      return 0;
    });
    const out: Node<BaseNodeData>[] = [];
    for (const n of ordered) {
      // Hide nodes whose ancestor chain contains a collapsed container.
      if (nearestCollapsedAncestor(n.id)) continue;
      // v0.2 correction (2026-04-20): rule / content are edited
      // through the right-hand Inspector panel, never on the canvas.
      if (n.kind === "rule" || n.kind === "content") continue;
      // v0.12.2: inside the service-detail modal the service-root
      // is redundant — the modal header already names it. Wrapper
      // (ServiceDetailCanvas) opts in via ``hideRootServiceNode``.
      if (hideRootServiceNode && doc.service_ref && n.id === doc.service_ref) {
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
      // prefers drill when set. v0.15 Phase 3.4: per-canvas drill
      // predicate supplied by the wrapper.
      const drillThisNode = shouldDrill?.(n) ?? false;
      const onDrill = drillThisNode && onNodeDrill ? () => onNodeDrill(n.id) : undefined;
      out.push({
        id: n.id,
        // v0.15 Phase 3.5 — node ``type`` is the kind discriminator.
        // SketchCanvas's ``nodeTypes`` map (NODE_RENDERERS) dispatches
        // to the per-kind renderer. Replaces the v0.14 "sketch" god type.
        type: n.kind,
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
          // v0.15 Phase 3.4: per-canvas opt-in. Foundation lays pillars
          // out as peers and passes false; everywhere else passes true.
          // v0.27.5 (D-2026-05-26-I): the root-service node on the
          // ServiceDetail canvas is the design *subject*; folding it
          // hides every descendant, which empties the canvas wholesale
          // and reads to the user as "the nodes just vanished when I
          // touched the centre node." Suppress the fold button on
          // ``service && is_root`` regardless of the wrapper-level
          // ``showFoldButton`` opt-in. Other service / category /
          // actor / step containers keep their fold buttons.
          showFold: showFoldButton && !(n.kind === "service" && n.is_root),
          mdWarnings: n._md_warnings,
        },
      });
    }
    // SPEC §Anchor — synthetic project anchor. v0.15 Phase 3.4: each
    // wrapper opts in via ``injectAnchor`` (true on Foundation /
    // Actors / Services; false on ServiceDetailCanvas). Mutation
    // routes via onAnchorChange, NEVER via onDocChange.
    if (projectAnchor && injectAnchor) {
      out.unshift({
        id: PROJECT_ANCHOR_ID,
        // v0.15 Phase 3.5 — synthetic anchor uses the ProjectNode renderer.
        type: "project",
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
    hideRootServiceNode,
    shouldDrill,
    showFoldButton,
    injectAnchor,
  ]);
}
