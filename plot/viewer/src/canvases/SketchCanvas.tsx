import { useCallback, useRef, useState } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlowProvider,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type Node,
  type NodeChange,
  type OnSelectionChangeParams,
  type ReactFlowInstance,
} from "reactflow";
import type {
  CanvasDoc,
  SketchEdge,
  SketchNode as DocNode,
} from "../types";
import { ActorRefPicker } from "./ActorRefPicker";
import {
  FoundationRefPicker,
  masterKindForRef,
  refIdFieldForKind,
  type FoundationRefMasterKind,
} from "./FoundationRefPicker";
import { SketchBodyModal } from "./SketchBodyModal";
import { SketchContextMenu } from "./SketchContextMenu";
import { SketchEdgeModal } from "./SketchEdgeModal";
import { SketchInspector } from "./SketchInspector";
import { SketchNode } from "./SketchNode";
import { SketchToolbar } from "./SketchToolbar";
import { useSketchClipboard } from "./useSketchClipboard";
import { applyAnchorChange } from "./sketch/applyAnchorChange";
import {
  DEFAULT_HEIGHT,
  DEFAULT_WIDTH,
  PROJECT_ANCHOR_ID,
} from "./sketch/constants";
import { useContextMenus } from "./sketch/useContextMenus";
import { useKeyboardShortcuts } from "./sketch/useKeyboardShortcuts";
import { useDragAndDrop } from "./sketch/useDragAndDrop";
import { useNodeCreation } from "./sketch/useNodeCreation";
import type { NodePreset } from "./sketch/types";
import { useCollapsedTree } from "./sketch/useCollapsedTree";
import { useEdgesMemo } from "./sketch/useEdgesMemo";
import { useInspectorRouting } from "./sketch/useInspectorRouting";
import { useNodesMemo } from "./sketch/useNodesMemo";
import { useOrphanActorRefs } from "./sketch/useOrphanActorRefs";
import { useValueFlow } from "./sketch/useValueFlow";

const NODE_TYPES = { sketch: SketchNode } as const;


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
}


export function SketchCanvas(props: SketchCanvasProps) {
  return (
    <ReactFlowProvider>
      <SketchCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

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
}: SketchCanvasProps) {
  const docRef = useRef<CanvasDoc>(doc);
  docRef.current = doc;
  const flowRef = useRef<ReactFlowInstance | null>(null);
  const selectedNodeIds = useRef<string[]>([]);
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
        nodes: current.nodes.map((n) => (n.id === nodeId ? { ...n, ...patch } : n)),
      });
    },
    [onDocChange],
  );

  const { childIdsByParent, nodeById, nearestCollapsedAncestor, toggleCollapsed, subtreeSize } =
    useCollapsedTree(doc.nodes, docRef, onDocChange);

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
  });

  const edges = useEdgesMemo({ doc, nearestCollapsedAncestor, valueFlowOn });

  // Apply every position change (including mid-drag) so the node visually
  // tracks the cursor. The debounced PUT in App.tsx coalesces the stream
  // down to one save per 400 ms, so drags don't flood the server.
  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      const posById = new Map<string, { x: number; y: number }>();
      const dimById = new Map<string, { width: number; height: number }>();
      for (const c of changes) {
        if (c.type === "position" && c.position) posById.set(c.id, c.position);
        // ``dimensions`` fires continuously during a NodeResizer drag.
        // Applying it live to our state keeps the node visually shrinking
        // while the handle is dragged, rather than snapping on release.
        // The ``resizing`` flag filters out React Flow's own post-mount
        // measurements so they don't clobber user-set sizes.
        if (
          c.type === "dimensions" &&
          c.resizing &&
          c.dimensions &&
          c.dimensions.width > 0 &&
          c.dimensions.height > 0
        ) {
          dimById.set(c.id, c.dimensions);
        }
      }
      if (posById.size === 0 && dimById.size === 0) return;
      // SPEC §Anchor: anchor mutations route via onAnchorChange.
      const anchorPatch = applyAnchorChange(posById, dimById);
      if (anchorPatch && onAnchorChange) onAnchorChange(anchorPatch);
      if (posById.size === 0 && dimById.size === 0) return;
      const current = docRef.current;
      onDocChange({
        ...current,
        nodes: current.nodes.map((n) => {
          const p = posById.get(n.id);
          const d = dimById.get(n.id);
          if (!p && !d) return n;
          return {
            ...n,
            ...(p ?? {}),
            ...(d ? { width: d.width, height: d.height } : {}),
          };
        }),
      });
    },
    [onDocChange, onAnchorChange],
  );

  const handleEdgesChange = useCallback((_changes: EdgeChange[]) => {
    // Selection and remove handled elsewhere.
  }, []);

  const handleConnect = useCallback(
    (connection: Connection) => {
      if (!connection.source || !connection.target) return;
      const current = docRef.current;
      const newEdge: SketchEdge = {
        id: `e_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`,
        source: connection.source,
        target: connection.target,
        sourceHandle: connection.sourceHandle ?? null,
        targetHandle: connection.targetHandle ?? null,
        label: "",
        style: "solid",
        action_verb: null,
        value_form: [],
      };
      onDocChange({ ...current, edges: [...current.edges, newEdge] });
    },
    [onDocChange],
  );

  const handleNodesDelete = useCallback(
    (deleted: Node[]) => {
      const current = docRef.current;
      // v0.13 Phase 0: synthetic project anchor isn't a real node — silently
      // ignore delete attempts. Legacy ``project`` kind nodes (any old data
      // still pre-eviction-migration) are also protected.
      const protectedIds = new Set(
        current.nodes.filter((n) => n.kind === "project").map((n) => n.id),
      );
      protectedIds.add(PROJECT_ANCHOR_ID);
      const ids = new Set(
        deleted.map((n) => n.id).filter((id) => !protectedIds.has(id)),
      );
      if (ids.size === 0) return;
      onDocChange({
        ...current,
        nodes: current.nodes.filter((n) => !ids.has(n.id)),
        edges: current.edges.filter((e) => !ids.has(e.source) && !ids.has(e.target)),
      });
    },
    [onDocChange],
  );

  const handleEdgesDelete = useCallback(
    (deleted: Edge[]) => {
      const ids = new Set(deleted.map((e) => e.id));
      const current = docRef.current;
      onDocChange({
        ...current,
        edges: current.edges.filter((e) => !ids.has(e.id)),
      });
    },
    [onDocChange],
  );

  const { addNodeAt, addNestedNodeAt } = useNodeCreation({ docRef, onDocChange });

  const handlePaneDoubleClick = useCallback(
    (event: React.MouseEvent) => {
      if (!flowRef.current) return;
      const target = event.target as HTMLElement;
      if (!target.classList.contains("react-flow__pane")) return;
      const pos = flowRef.current.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
      addNodeAt(pos.x - DEFAULT_WIDTH / 2, pos.y - DEFAULT_HEIGHT / 2);
    },
    [addNodeAt],
  );

  const handleSelectionChange = useCallback((sel: OnSelectionChangeParams) => {
    selectedNodeIds.current = sel.nodes.map((n) => n.id);
  }, []);

  // ---------------- Context menu ----------------

  const { menu, closeMenu, openNodeMenu, openEdgeMenu, openPaneMenu } = useContextMenus({
    docRef,
    flowRef,
    onDocChange,
    clipboard,
    handleNodesDelete,
    handleEdgesDelete,
    addNodeAt,
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
    nodeById,
    flowRef,
    addNodeAt,
    addNestedNodeAt,
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
        nodesConnectable
        nodesDraggable
        elementsSelectable
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
        }}
        fitView
        fitViewOptions={{ padding: 0.2 }}
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
        <MiniMap zoomable pannable />
        <Controls />
      </ReactFlow>
      {menu && (
        <SketchContextMenu
          x={menu.x}
          y={menu.y}
          items={menu.items}
          onClose={closeMenu}
        />
      )}
      {bodyModalNodeId && (() => {
        const target = doc.nodes.find((n) => n.id === bodyModalNodeId);
        if (!target) return null;
        return (
          <SketchBodyModal
            node={target}
            onCommit={(patch) => updateNode(target.id, patch)}
            onClose={() => setBodyModalNodeId(null)}
            onDelete={() => handleNodesDelete([{ id: target.id } as Node])}
          />
        );
      })()}
      {edgeModalId && (() => {
        const target = doc.edges.find((e) => e.id === edgeModalId);
        if (!target) return null;
        return (
          <SketchEdgeModal
            edge={target}
            onCommit={(patch) => {
              const current = docRef.current;
              onDocChange({
                ...current,
                edges: current.edges.map((e) =>
                  e.id === target.id ? { ...e, ...patch } : e,
                ),
              });
            }}
            onClose={() => setEdgeModalId(null)}
            onDelete={() => handleEdgesDelete([{ id: target.id } as Edge])}
          />
        );
      })()}
      {pendingFoundationRef && (() => {
        const masterKind: FoundationRefMasterKind | null = masterKindForRef(
          pendingFoundationRef.refKind,
        );
        if (!masterKind) return null;
        const masters =
          masterKind === "mission"
            ? availableMissions ?? []
            : masterKind === "core_value"
              ? availableValues ?? []
              : availableIdentities ?? [];
        const idField = refIdFieldForKind(pendingFoundationRef.refKind);
        if (!idField) return null;
        return (
          <FoundationRefPicker
            masterKind={masterKind}
            masters={masters}
            mode={pendingFoundationRef.mode}
            onCancel={() => setPendingFoundationRef(null)}
            onPick={(master) => {
              if (pendingFoundationRef.mode === "rewire") {
                updateNode(pendingFoundationRef.nodeId, {
                  [idField]: master.id,
                  label: `→ ${master.label || master.id}`,
                } as Partial<DocNode>);
                setPendingFoundationRef(null);
                return;
              }
              const { preset, pos, resolved } = pendingFoundationRef;
              const w = preset.width ?? DEFAULT_WIDTH;
              const h = preset.height ?? DEFAULT_HEIGHT;
              const resolvedPreset: NodePreset = {
                ...preset,
                label: `→ ${master.label || master.id}`,
                [idField]: master.id,
              };
              if (resolved.parentId) {
                const parent = nodeById.get(resolved.parentId)!;
                let ax = parent.x;
                let ay = parent.y;
                let cur: DocNode | undefined = parent;
                while (cur?.parent_id) {
                  const p = nodeById.get(cur.parent_id);
                  if (!p) break;
                  ax += p.x;
                  ay += p.y;
                  cur = p;
                }
                addNestedNodeAt({
                  parentId: resolved.parentId,
                  localX: Math.max(8, pos.x - ax - w / 2),
                  localY: Math.max(28, pos.y - ay - h / 2),
                  preset: resolvedPreset,
                });
              } else {
                addNodeAt(pos.x - w / 2, pos.y - h / 2, resolvedPreset);
              }
              setPendingFoundationRef(null);
            }}
          />
        );
      })()}
      {pendingActorRef && (
        <ActorRefPicker
          nodes={availableActors ?? doc.nodes}
          mode={pendingActorRef.mode}
          onCancel={() => setPendingActorRef(null)}
          onPick={(actor) => {
            if (pendingActorRef.mode === "rewire") {
              updateNode(pendingActorRef.nodeId, {
                ref_actor_id: actor.id,
                label: `→ ${actor.label || actor.id}`,
              });
              setPendingActorRef(null);
              return;
            }
            const { preset, pos, resolved } = pendingActorRef;
            const w = preset.width ?? DEFAULT_WIDTH;
            const h = preset.height ?? DEFAULT_HEIGHT;
            const resolvedPreset: NodePreset = {
              ...preset,
              label: `→ ${actor.label || actor.id}`,
              ref_actor_id: actor.id,
            };
            if (resolved.parentId) {
              const parent = nodeById.get(resolved.parentId)!;
              let ax = parent.x;
              let ay = parent.y;
              let cur: DocNode | undefined = parent;
              while (cur?.parent_id) {
                const p = nodeById.get(cur.parent_id);
                if (!p) break;
                ax += p.x;
                ay += p.y;
                cur = p;
              }
              addNestedNodeAt({
                parentId: resolved.parentId,
                localX: Math.max(8, pos.x - ax - w / 2),
                localY: Math.max(28, pos.y - ay - h / 2),
                preset: resolvedPreset,
              });
            } else {
              addNodeAt(pos.x - w / 2, pos.y - h / 2, resolvedPreset);
            }
            setPendingActorRef(null);
          }}
        />
      )}
      <SketchInspector
        node={
          inspectorNodeId
            ? doc.nodes.find((n) => n.id === inspectorNodeId) ?? null
            : null
        }
        allNodes={doc.nodes}
        availableActors={availableActors ?? doc.nodes.filter((n) => n.kind === "actor")}
        availableMissions={availableMissions}
        availableValues={availableValues}
        availableIdentities={availableIdentities}
        projectPath={projectPath}
        projectId={projectId}
        canvasKind={doc.canvas_kind}
        onRepickActorRef={(nodeId) => setPendingActorRef({ mode: "rewire", nodeId })}
        onRepickFoundationRef={(nodeId) => {
          // v0.11.1 — find the orphan ref's kind and open the picker.
          const target = doc.nodes.find((n) => n.id === nodeId);
          if (
            !target ||
            (target.kind !== "mission_ref" &&
              target.kind !== "value_ref" &&
              target.kind !== "identity_ref")
          ) {
            return;
          }
          setPendingFoundationRef({
            mode: "rewire",
            refKind: target.kind,
            nodeId,
          });
        }}
        onDeleteNode={(nodeId) => handleNodesDelete([{ id: nodeId } as Node])}
        onPatchNode={(patch) => {
          if (!inspectorNodeId) return;
          updateNode(inspectorNodeId, patch);
        }}
        onAddChild={(parentId, kind) => {
          const id = `n_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
          const current = docRef.current;
          const defaults = kind === "rule"
            ? { shape: "rectangle" as const, color: "#e7e5e4", icon: "shield" as const }
            : { shape: "hexagon" as const, color: "#ddd6fe", icon: "package" as const };
          const newNode: DocNode = {
            id,
            label: kind === "rule" ? "New rule" : "New content",
                x: 0, y: 0,
            width: 140,
            height: 60,
            color: defaults.color,
            shape: defaults.shape,
            icon: defaults.icon,
            kind,
            parent_id: parentId,
            collapsed: false,
            is_root: false,
            mission: "",
            core_values: "",
            identity: "",
            what_we_do: "",
            why: "",
            direction: "",
            definition: "",
            description: "",
            do: "",
            dont: "",
            ref_actor_id: null,
            ref_mission_id: null,
            ref_value_id: null,
            ref_identity_id: null,
            what: "",
            value_created: "",
            scope: "",
            trigger: "",
            how: "",
            outcome: "",
            target: "",
            measurement: "",
            order: null,
            policy: "",
            enforcement: "",
            actor_permissions: {},
            format: "",
            producer_actor_id: null,
            consumer_actor_id: null,
            motivation: "",
            pain: "",
            side: null,
            gives: "",
            receives: "",
            target_side: null,
            theme: "",
          };
          onDocChange({ ...current, nodes: [...current.nodes, newNode] });
        }}
        onPatchChild={(childId, patch) => updateNode(childId, patch)}
        onRemoveChild={(childId) => {
          const current = docRef.current;
          onDocChange({
            ...current,
            nodes: current.nodes.filter((n) => n.id !== childId),
          });
        }}
        onClose={() => setInspectorNodeId(null)}
      />
    </div>
  );
}

export { applyEdgeChanges, applyNodeChanges };
