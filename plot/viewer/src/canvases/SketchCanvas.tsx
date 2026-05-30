import { memo, useCallback, useEffect, useRef, useState } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  ConnectionMode,
  Controls,
  ReactFlowProvider,
  useNodesInitialized,
  useReactFlow,
  type NodeChange,
  type ReactFlowInstance,
} from "reactflow";
import type {
  CanvasDoc,
  SketchNode as DocNode,
} from "../types";
import { SketchContextMenu } from "./SketchContextMenu";
import { EDGE_TYPES } from "./edges/registry";
import { NODE_RENDERERS } from "./nodes/registry";
import { SketchToolbar } from "./SketchToolbar";
import { useSketchClipboard } from "./useSketchClipboard";
import { SketchInspectorBindings } from "./sketch/SketchInspectorBindings";
import { SketchModals } from "./sketch/SketchModals";
import { applyAnchorChange } from "./sketch/applyAnchorChange";
import {
  applyNodeChangesToDoc,
  collectNodeChanges,
} from "./sketch/nodeChanges";
import { useContextMenus } from "./sketch/useContextMenus";
import { useKeyboardShortcuts } from "./sketch/useKeyboardShortcuts";
import { useDragAndDrop } from "./sketch/useDragAndDrop";
import { useFlowHandlers } from "./sketch/useFlowHandlers";
import { useNodeCreation } from "./sketch/useNodeCreation";
import { useCollapsedTree } from "./sketch/useCollapsedTree";
import { useEdgesMemo } from "./sketch/useEdgesMemo";
import { useInspectorRouting } from "./sketch/useInspectorRouting";
import { useNodesMemo } from "./sketch/useNodesMemo";
import { useOrphanActorRefs } from "./sketch/useOrphanActorRefs";
import { useAutoLayout } from "./sketch/useAutoLayout";
import { LayoutControls } from "./sketch/LayoutControls";
import { useRadialLayout } from "./sketch/useRadialLayout";
import { useValueFlow } from "./sketch/useValueFlow";

// v0.15 Phase 3.5 — per-kind React Flow node types come from the
// 15-kind ``NODE_RENDERERS`` registry. Each node's ``type`` in the
// React Flow node array is its kind discriminator (``"metric"`` /
// ``"service"`` / …) instead of the v0.14 ``"sketch"`` god type.
const NODE_TYPES = NODE_RENDERERS;


// Note (2026-04-20): the earlier implementation snapped services to an
// upper band and actors to a lower band. The user clarified that the
// "two layers" metaphor was conceptual, not spatial — services and
// actors coexist on the same 2D plane, differentiated by kind (shape /
// colour / icon), not by y position. Layer-snap helper removed.

export interface SketchCanvasProps {
  doc: CanvasDoc;
  onDocChange: (next: CanvasDoc) => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  /** v0.7: Inspector's MD editor + "Connect to folder" button need both to
   *  call the file/folder endpoints and to hint the server back for preview
   *  cache sync on save. */
  projectPath: string;
  projectId: string;
  /** v0.2 multi-canvas: double-click a node to drill into its Detail canvas (Services only). */
  onNodeDrill?: (nodeId: string) => void;
  /**
   * v0.2 multi-canvas: actors available in the ActorRefPicker. Supplied by
   * the App (it holds the unfiltered doc), because this canvas may itself
   * be showing a tab-filtered view that excludes the actors.
   */
  availableActors?: DocNode[];
  /**
   * v0.10 Step 3: Foundation masters available in the FoundationRefPicker.
   * Each list is the foundation canvas's nodes filtered by kind. App
   * supplies them so the Services canvas doesn't have to read across the
   * canvas boundary.
   */
  availableMissions?: DocNode[];
  availableValues?: DocNode[];
  availableIdentities?: DocNode[];
  /**
   * v0.2 multi-canvas: when set, the canvas selects this node on mount
   * (used for jumping from an actor_ref to its target in the Actors canvas).
   * Fires ``onSelectionConsumed`` once applied so the URL param can be cleared.
   */
  selectNodeId?: string | null;
  onSelectionConsumed?: () => void;
  /**
   * v0.13 Phase 0: per-canvas project anchor. The anchor is rendered as a
   * synthetic node injected by SketchCanvas (it does NOT live in
   * ``doc.nodes``). Drag updates flow through ``onAnchorChange`` instead of
   * the regular node update path; the canvas .json never carries a project
   * node.
   */
  projectAnchor?: import("../types").AnchorPlacement | null;
  /** v0.13 Phase 0: project name shown on the synthetic anchor's label. */
  projectName?: string | null;
  /** v0.13 Phase 0: callback when the user drags / resizes the anchor. */
  onAnchorChange?: (patch: Partial<import("../types").AnchorPlacement>) => void;
  /** v0.15 Phase 3.4 — drop the canvas's root-service node from
   *  the rendered list (true on ServiceDetailCanvas where the
   *  modal header already names the service). Default false. */
  hideRootServiceNode?: boolean;
  /** v0.15 Phase 3.4 — predicate that opts nodes into double-click
   *  drill. Each canvas wrapper supplies its own. Default ``undefined``
   *  = no drilling. */
  shouldDrill?: (node: DocNode) => boolean;
  /** v0.15 Phase 3.4 — render the fold (▾/▸) button on container
   *  nodes. Default true; FoundationCanvas passes false. */
  showFoldButton?: boolean;
  /** v0.15 Phase 3.4 — inject the synthetic project anchor at the top
   *  of the node list. Default true; ServiceDetailCanvas passes false. */
  injectAnchor?: boolean;
  /** v0.16.12 (D-2026-05-12-O) — when true, new ``mission`` /
   *  ``core_value`` / ``identity`` nodes snap to anchor-radial slots
   *  per the canonical Plot spec (Foundation only). Default false. */
  applyAnchorRadialLayout?: boolean;
  /** v0.25.0 (D-2026-05-24-B) — wrapper opt-in for the auto-layout
   *  button in RF Controls. Successor to ``enableAutoLayout`` (boolean).
   *  ``"tree"`` runs ``useAutoLayout`` (Foundation / Actors); ``"radial"``
   *  runs ``useRadialLayout`` (Services / ServiceDetail). ``null`` /
   *  undefined hides the button entirely. */
  layoutAlgo?: "tree" | "radial" | null;
  /** v0.28.3 (D-2026-05-30-F) — LR/TB direction-switch buttons (ServiceDetail). */
  showDirectionSwitch?: boolean;
  /** v0.18.0 Phase 3 (D-2026-05-16-E) — fire to publish a node. The
   *  Inspector renders the publish button; the callback wraps the
   *  HTTP POST + version refresh. Optional so canvases not yet wired
   *  (or tests) compile. */
  onPublishNode?: (nodeId: string) => void;
  /** v0.23.x (D-2026-05-17-J) — fire to unpublish (git revert) a node's
   *  most recent publish. Optional. */
  onUnpublishNode?: (nodeId: string) => void;
}


// v0.27.18 (D-2026-05-28-L) — wrap with React.memo so a parent re-render
// caused by an unrelated child (e.g. the ServiceDetail modal updating its
// own doc cache slice) doesn't sweep this SketchCanvas through a full
// re-render → ReactFlow prop-cascade. Combined with App.tsx's stabilised
// projectAnchor + projectName, the Services canvas behind the modal now
// stays quiet while the user works inside the modal.
function SketchCanvasImpl(props: SketchCanvasProps) {
  return (
    <ReactFlowProvider>
      <SketchCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

export const SketchCanvas = memo(SketchCanvasImpl);

function SketchCanvasInner({
  doc,
  onDocChange,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  projectPath,
  projectId,
  onNodeDrill,
  availableActors,
  availableMissions,
  availableValues,
  availableIdentities,
  selectNodeId,
  onSelectionConsumed,
  projectAnchor,
  projectName,
  onAnchorChange,
  hideRootServiceNode,
  shouldDrill,
  showFoldButton,
  injectAnchor,
  applyAnchorRadialLayout,
  layoutAlgo,
  showDirectionSwitch,
  onPublishNode,
  onUnpublishNode,
}: SketchCanvasProps) {
  const docRef = useRef<CanvasDoc>(doc);
  docRef.current = doc;
  const flowRef = useRef<ReactFlowInstance | null>(null);
  const selectedNodeIds = useRef<string[]>([]);
  // v0.18.3 (D-2026-05-17-A) — defer fitView until RF measures every
  // node's DOM box. The onInit path fit (0,0) before measurement.
  // v0.27.4 (D-2026-05-26-H) — `useNodesInitialized` occasionally stays
  // false when the canvas mounts inside a freshly opened modal (the
  // dialog's initial DOM measurement races with RF's internal measure
  // pass and the signal never flips). Without this fallback every node
  // stays ``visibility: hidden`` forever — the canvas looks empty even
  // though all nodes are mounted in the right positions. The timeout
  // gives RF 300 ms; if the signal hasn't arrived, fire fitView anyway
  // and force RF to honour the measured DOM rects.
  const rf = useReactFlow();
  const nodesInitialized = useNodesInitialized();
  const didInitialFitRef = useRef(false);
  useEffect(() => {
    if (didInitialFitRef.current) return;
    if (nodesInitialized) {
      rf.fitView({ padding: 0.2 });
      didInitialFitRef.current = true;
      return;
    }
    const t = setTimeout(() => {
      if (didInitialFitRef.current) return;
      rf.fitView({ padding: 0.2 });
      didInitialFitRef.current = true;
    }, 300);
    return () => clearTimeout(t);
  }, [nodesInitialized, rf]);
  const clipboard = useSketchClipboard();
  const [bodyModalNodeId, setBodyModalNodeId] = useState<string | null>(null);
  const [edgeModalId, setEdgeModalId] = useState<string | null>(null);
  const { valueFlowOn, toggleValueFlow } = useValueFlow();
  const {
    inspectorNodeId,
    setInspectorNodeId,
    onNodeClick: handleNodeClick,
    onNodeDoubleClick: handleNodeDoubleClick,
    onPaneClick: handlePaneClick,
  } = useInspectorRouting({
    nodes: doc.nodes,
    flowRef,
    selectNodeId,
    onSelectionConsumed,
    onNodeDrill,
  });

  const orphanActorRefIds = useOrphanActorRefs(doc.nodes, availableActors);

  const updateNode = useCallback(
    (nodeId: string, patch: Partial<DocNode>) => {
      const current = docRef.current;
      onDocChange({
        ...current,
        // v0.15: spread merge of a discriminated union loses the kind-narrowed
        // type; cast back to DocNode after the structural merge. Safe at
        // runtime because ``patch: Partial<DocNode>`` can only patch valid
        // fields.
        nodes: current.nodes.map((n) =>
          n.id === nodeId ? ({ ...n, ...patch } as DocNode) : n,
        ),
      });
    },
    [onDocChange],
  );

  const { childIdsByParent, nodeById, nearestCollapsedAncestor, toggleCollapsed, subtreeSize } =
    useCollapsedTree(doc.nodes, doc.edges, docRef, onDocChange);
  const treeLayout = useAutoLayout({ docRef, onDocChange, projectAnchor });
  const triggerRadialLayout = useRadialLayout({ docRef, onDocChange, projectAnchor });
  const triggerLayout = layoutAlgo === "radial" ? triggerRadialLayout : treeLayout.trigger;

  const nodes = useNodesMemo({
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
    hideRootServiceNode: hideRootServiceNode ?? false,
    shouldDrill,
    showFoldButton: showFoldButton ?? true,
    injectAnchor: injectAnchor ?? true,
  });

  const edges = useEdgesMemo({
    doc,
    nearestCollapsedAncestor,
    valueFlowOn,
    hideRootServiceNode: hideRootServiceNode ?? false,
  });

  // React Flow's onNodesChange must dispatch atomically per the
  // coupling map — keep this handler in the shell, but the pure
  // bits (collect + apply) live in sketch/nodeChanges.ts and the
  // anchor branch in sketch/applyAnchorChange.ts.
  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      const { posById, dimById } = collectNodeChanges(changes);
      if (posById.size === 0 && dimById.size === 0) return;
      const anchorPatch = applyAnchorChange(posById, dimById);
      if (anchorPatch && onAnchorChange) onAnchorChange(anchorPatch);
      if (posById.size === 0 && dimById.size === 0) return;
      onDocChange(applyNodeChangesToDoc(docRef.current, posById, dimById));
    },
    [onDocChange, onAnchorChange],
  );

  const { addNodeAt, addNestedNodeAt, addCompositionChild } = useNodeCreation({
    docRef,
    onDocChange,
    applyAnchorRadialLayout: applyAnchorRadialLayout ?? false,
  });

  const {
    handleConnect,
    handleEdgesChange,
    handleNodesDelete,
    handleEdgesDelete,
    handlePaneDoubleClick,
    handleSelectionChange,
  } = useFlowHandlers({
    docRef,
    flowRef,
    selectedNodeIds,
    onDocChange,
    addNodeAt,
  });

  // ---------------- Context menu ----------------

  const { menu, closeMenu, openNodeMenu, openEdgeMenu, openPaneMenu } = useContextMenus({
    docRef,
    flowRef,
    onDocChange,
    clipboard,
    handleNodesDelete,
    handleEdgesDelete,
    addNodeAt,
    selectedNodeIds,
  });

  useKeyboardShortcuts({
    docRef,
    flowRef,
    selectedNodeIds,
    clipboard,
    onUndo,
    onRedo,
    onDocChange,
  });

  const {
    handleDragOver,
    handleDrop,
    pendingActorRef,
    setPendingActorRef,
    pendingFoundationRef,
    setPendingFoundationRef,
  } = useDragAndDrop({
    nodes: doc.nodes,
    edges: doc.edges,
    nodeById,
    flowRef,
    addNodeAt,
    addNestedNodeAt,
    // v0.27.10 (D-2026-05-28-A) — drop-target resolution needs the
    // canvas context so ServiceDetail composition drops are free-form.
    canvasKind: doc.canvas_kind,
  });

  return (
    <div
      className="relative h-full w-full"
      onDoubleClick={handlePaneDoubleClick}
      onClick={closeMenu}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <SketchToolbar
        canUndo={canUndo}
        canRedo={canRedo}
        onUndo={onUndo}
        onRedo={onRedo}
        valueFlowOn={valueFlowOn}
        onToggleValueFlow={toggleValueFlow}
      />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={NODE_TYPES}
        edgeTypes={EDGE_TYPES}
        nodesConnectable
        nodesDraggable
        elementsSelectable
        panOnDrag
        connectionMode={ConnectionMode.Loose}
        multiSelectionKeyCode={["Meta", "Control"]}
        selectionKeyCode="Shift"
        deleteKeyCode={["Delete", "Backspace"]}
        nodeDragThreshold={4}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={handleConnect}
        onNodesDelete={handleNodesDelete}
        onEdgesDelete={handleEdgesDelete}
        onSelectionChange={handleSelectionChange}
        onNodeContextMenu={openNodeMenu}
        onEdgeContextMenu={openEdgeMenu}
        onEdgeDoubleClick={(_evt, edge) => setEdgeModalId(edge.id)}
        onNodeClick={handleNodeClick}
        onNodeDoubleClick={handleNodeDoubleClick}
        onPaneClick={handlePaneClick}
        onPaneContextMenu={openPaneMenu}
        onInit={(inst) => {
          flowRef.current = inst;
          // v0.18.3 (D-2026-05-17-A) — fitView moved out of onInit to
          // the ``useNodesInitialized`` effect above (DOM-measurement
          // race). v0.16.18 (D-2026-05-12-T) intent — fit once on
          // mount, not on every render — is preserved by the
          // ``didInitialFitRef`` gate. ``activeCanvasKey`` remount
          // path still re-fits (didInitialFitRef resets per remount).
        }}
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
        <Controls>
          <LayoutControls
            layoutAlgo={layoutAlgo}
            showDirectionSwitch={showDirectionSwitch}
            onLayout={triggerLayout}
            onDirection={treeLayout.layoutInDirection}
          />
        </Controls>
      </ReactFlow>
      {menu && (
        <SketchContextMenu
          x={menu.x}
          y={menu.y}
          items={menu.items}
          onClose={closeMenu}
        />
      )}
      <SketchModals
        doc={doc}
        docRef={docRef}
        onDocChange={onDocChange}
        nodeById={nodeById}
        updateNode={updateNode}
        handleNodesDelete={handleNodesDelete}
        handleEdgesDelete={handleEdgesDelete}
        addNodeAt={addNodeAt}
        addNestedNodeAt={addNestedNodeAt}
        bodyModalNodeId={bodyModalNodeId}
        setBodyModalNodeId={setBodyModalNodeId}
        edgeModalId={edgeModalId}
        setEdgeModalId={setEdgeModalId}
        pendingFoundationRef={pendingFoundationRef}
        setPendingFoundationRef={setPendingFoundationRef}
        pendingActorRef={pendingActorRef}
        setPendingActorRef={setPendingActorRef}
        availableActors={availableActors}
        availableMissions={availableMissions}
        availableValues={availableValues}
        availableIdentities={availableIdentities}
      />
      <SketchInspectorBindings
        doc={doc}
        docRef={docRef}
        onDocChange={onDocChange}
        inspectorNodeId={inspectorNodeId}
        setInspectorNodeId={setInspectorNodeId}
        updateNode={updateNode}
        handleNodesDelete={handleNodesDelete}
        addCompositionChild={addCompositionChild}
        setPendingActorRef={setPendingActorRef}
        setPendingFoundationRef={setPendingFoundationRef}
        availableActors={availableActors}
        availableMissions={availableMissions}
        availableValues={availableValues}
        availableIdentities={availableIdentities}
        projectPath={projectPath}
        projectId={projectId}
        onPublishNode={onPublishNode}
        onUnpublishNode={onUnpublishNode}
      />
    </div>
  );
}

