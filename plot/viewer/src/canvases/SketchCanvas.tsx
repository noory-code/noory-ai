import { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
  NodeKind,
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
import { SketchContextMenu, type ContextMenuItem } from "./SketchContextMenu";
import { SketchEdgeModal, VALUE_FORM_COLORS } from "./SketchEdgeModal";
import { SketchInspector } from "./SketchInspector";
import { SketchNode } from "./SketchNode";
import { resolveDropTarget, type StencilPreset } from "./SketchStencil";
import { SketchToolbar } from "./SketchToolbar";
import { useSketchClipboard } from "./useSketchClipboard";
import { PROJECT_ANCHOR_ID } from "./sketch/constants";
import { useCollapsedTree } from "./sketch/useCollapsedTree";
import { useInspectorRouting } from "./sketch/useInspectorRouting";
import { useNodesMemo } from "./sketch/useNodesMemo";
import { useOrphanActorRefs } from "./sketch/useOrphanActorRefs";
import { useValueFlow } from "./sketch/useValueFlow";

const NODE_TYPES = { sketch: SketchNode } as const;

const DEFAULT_WIDTH = 180;
const DEFAULT_HEIGHT = 80;
const DEFAULT_COLOR = "#ffffff";

/**
 * Optional stencil preset used when a node is dropped from the palette or
 * created via the toolbar. ``undefined`` → caller gets a plain rounded
 * rectangle with the defaults above.
 */
export interface NodePreset {
  shape: DocNode["shape"];
  color: string;
  width?: number;
  height?: number;
  icon?: string | null;
  label?: string;
  /** v0.2: typed node kind. Used to constrain layer on drop and for AI. */
  kind?: NodeKind | null;
  /**
   * v0.2 multi-canvas: set on actor_ref drops once the picker has resolved
   * which actor in the Actor canvas this node points at.
   */
  ref_actor_id?: string | null;
  /**
   * v0.10 Step 3: set on Foundation ref drops once the picker resolves the
   * master node from the Foundation canvas.
   */
  ref_mission_id?: string | null;
  ref_value_id?: string | null;
  ref_identity_id?: string | null;
}

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

interface MenuState {
  x: number;
  y: number;
  items: ContextMenuItem[];
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
  const [menu, setMenu] = useState<MenuState | null>(null);
  const [bodyModalNodeId, setBodyModalNodeId] = useState<string | null>(null);
  const [edgeModalId, setEdgeModalId] = useState<string | null>(null);
  const { valueFlowOn, toggleValueFlow } = useValueFlow();
  // Create mode runs while the user is dropping a fresh Actor ref from the
  // stencil; rewire mode runs when the Inspector asks to repoint an
  // existing orphan actor_ref at a different actor.
  type PendingActorRef =
    | {
        mode: "create";
        preset: NodePreset;
        pos: { x: number; y: number };
        resolved: { parentId: string | null };
      }
    | { mode: "rewire"; nodeId: string };
  const [pendingActorRef, setPendingActorRef] = useState<PendingActorRef | null>(null);
  // v0.10 Step 3: same shape as PendingActorRef, but with the ref kind so
  // we know which master list to feed the picker and which id field to set.
  type PendingFoundationRef =
    | {
        mode: "create";
        refKind: "mission_ref" | "value_ref" | "identity_ref";
        preset: NodePreset;
        pos: { x: number; y: number };
        resolved: { parentId: string | null };
      }
    | {
        mode: "rewire";
        refKind: "mission_ref" | "value_ref" | "identity_ref";
        nodeId: string;
      };
  const [pendingFoundationRef, setPendingFoundationRef] =
    useState<PendingFoundationRef | null>(null);
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

  const edges = useMemo<Edge[]>(() => {
    const out: Edge[] = [];
    // v0.12.2 — same hide rule as the nodes memo: drop edges that point at
    // the modal's hidden service-root.
    const isHiddenRoot = (id: string): boolean =>
      doc.canvas_kind === "service_detail" &&
      !!doc.service_ref &&
      id === doc.service_ref;
    // User-drawn edges.
    for (const e of doc.edges) {
      if (isHiddenRoot(e.source) || isHiddenRoot(e.target)) continue;
      const sAncestor = nearestCollapsedAncestor(e.source);
      const tAncestor = nearestCollapsedAncestor(e.target);
      const src = sAncestor ?? e.source;
      const tgt = tAncestor ?? e.target;
      if (sAncestor && tAncestor && sAncestor === tAncestor) continue;
      if (src === tgt) continue;
      const stroke =
        valueFlowOn && e.value_form && e.value_form.length > 0
          ? VALUE_FORM_COLORS[e.value_form[0]]
          : undefined;
      out.push({
        id: e.id,
        source: src,
        target: tgt,
        sourceHandle: sAncestor ? undefined : e.sourceHandle ?? undefined,
        targetHandle: tAncestor ? undefined : e.targetHandle ?? undefined,
        label: e.label || undefined,
        style: {
          ...(e.style === "dashed" ? { strokeDasharray: "6 4" } : {}),
          ...(stroke ? { stroke, strokeWidth: e.value_form.length } : {}),
        },
      });
    }
    return out;
  }, [doc.edges, doc.canvas_kind, doc.service_ref, nearestCollapsedAncestor, valueFlowOn]);

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
      // v0.13 Phase 0: route synthetic project anchor changes to onAnchorChange.
      const anchorPos = posById.get(PROJECT_ANCHOR_ID);
      const anchorDim = dimById.get(PROJECT_ANCHOR_ID);
      if ((anchorPos || anchorDim) && onAnchorChange) {
        const patch: Partial<import("../types").AnchorPlacement> = {};
        if (anchorPos) {
          patch.x = anchorPos.x;
          patch.y = anchorPos.y;
        }
        if (anchorDim) {
          patch.width = anchorDim.width;
          patch.height = anchorDim.height;
        }
        onAnchorChange(patch);
        posById.delete(PROJECT_ANCHOR_ID);
        dimById.delete(PROJECT_ANCHOR_ID);
      }
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

  const addNodeAt = useCallback(
    (x: number, y: number, preset?: NodePreset) => {
      const id = `n_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
      const newNode: DocNode = {
        id,
        label: preset?.label ?? "",
        x,
        y,
        width: preset?.width ?? DEFAULT_WIDTH,
        height: preset?.height ?? DEFAULT_HEIGHT,
        color: preset?.color ?? DEFAULT_COLOR,
        shape: preset?.shape ?? "rounded",
        icon: preset?.icon ?? null,
        kind: preset?.kind ?? null,
        parent_id: null,
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
        ref_actor_id: preset?.ref_actor_id ?? null,
        ref_mission_id: preset?.ref_mission_id ?? null,
        ref_value_id: preset?.ref_value_id ?? null,
        ref_identity_id: preset?.ref_identity_id ?? null,
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
      const current = docRef.current;
      onDocChange({ ...current, nodes: [...current.nodes, newNode] });
    },
    [onDocChange],
  );

  const addNestedNodeAt = useCallback(
    (args: {
      parentId: string;
      localX: number;
      localY: number;
      preset: NodePreset;
    }) => {
      const id = `n_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
      const { preset } = args;
      const newNode: DocNode = {
        id,
        label: preset.label ?? "",
        x: args.localX,
        y: args.localY,
        width: preset.width ?? DEFAULT_WIDTH,
        height: preset.height ?? DEFAULT_HEIGHT,
        color: preset.color ?? DEFAULT_COLOR,
        shape: preset.shape ?? "rounded",
        icon: preset.icon ?? null,
        kind: preset.kind ?? null,
        parent_id: args.parentId,
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
        ref_actor_id: preset?.ref_actor_id ?? null,
        ref_mission_id: preset?.ref_mission_id ?? null,
        ref_value_id: preset?.ref_value_id ?? null,
        ref_identity_id: preset?.ref_identity_id ?? null,
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
      const current = docRef.current;
      // Rule / content are composition: edited via the Inspector, no edge.
      // Actor / service are hierarchy: materialise a real decomposition
      // edge so users can edit it (label, verb, value_form).
      const makeHierarchyEdge = preset.kind === "actor" || preset.kind === "service";
      const edgeId = `e_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
      const newEdges = makeHierarchyEdge
        ? [
            ...current.edges,
            {
              id: edgeId,
              source: args.parentId,
              target: id,
              sourceHandle: null,
              targetHandle: null,
              label: "decomposes",
              style: "dashed" as const,
              action_verb: "decomposes",
              value_form: [],
            },
          ]
        : current.edges;
      onDocChange({ ...current, nodes: [...current.nodes, newNode], edges: newEdges });
    },
    [onDocChange],
  );

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

  const closeMenu = useCallback(() => setMenu(null), []);

  const openNodeMenu = useCallback(
    (event: React.MouseEvent, node: Node) => {
      event.preventDefault();
      const colors = ["#ffffff", "#fecaca", "#fed7aa", "#fef08a", "#bbf7d0", "#bae6fd", "#ddd6fe"];
      const docNode = docRef.current.nodes.find((n) => n.id === node.id);
      const isProject = docNode?.kind === "project";
      setMenu({
        x: event.clientX,
        y: event.clientY,
        items: [
          {
            label: "Duplicate",
            disabled: isProject,
            onSelect: () => {
              if (isProject) return;
              const current = docRef.current;
              onDocChange(clipboard.duplicate(current, [node.id]));
            },
          },
          {
            label: "Copy",
            onSelect: () => {
              clipboard.copy(docRef.current, [node.id]);
            },
          },
          { label: "", divider: true, onSelect: () => {} },
          ...colors.map((hex) => ({
            label: `Color ${hex}`,
            onSelect: () => {
              const current = docRef.current;
              onDocChange({
                ...current,
                nodes: current.nodes.map((n) =>
                  n.id === node.id ? { ...n, color: hex } : n,
                ),
              });
            },
          })),
          { label: "", divider: true, onSelect: () => {} },
          {
            label: isProject ? "Delete (Project anchor is protected)" : "Delete",
            danger: !isProject,
            disabled: isProject,
            onSelect: () => {
              if (isProject) return;
              handleNodesDelete([node]);
            },
          },
        ],
      });
    },
    [onDocChange, clipboard, handleNodesDelete],
  );

  const openEdgeMenu = useCallback(
    (event: React.MouseEvent, edge: Edge) => {
      event.preventDefault();
      setMenu({
        x: event.clientX,
        y: event.clientY,
        items: [
          {
            label: "Toggle dashed/solid",
            onSelect: () => {
              const current = docRef.current;
              onDocChange({
                ...current,
                edges: current.edges.map((e) =>
                  e.id === edge.id
                    ? { ...e, style: e.style === "dashed" ? "solid" : "dashed" }
                    : e,
                ),
              });
            },
          },
          {
            label: "Set label",
            onSelect: () => {
              const newLabel = window.prompt("Edge label:", edge.label ? String(edge.label) : "");
              if (newLabel === null) return;
              const current = docRef.current;
              onDocChange({
                ...current,
                edges: current.edges.map((e) =>
                  e.id === edge.id ? { ...e, label: newLabel } : e,
                ),
              });
            },
          },
          { label: "", divider: true, onSelect: () => {} },
          {
            label: "Delete",
            danger: true,
            onSelect: () => handleEdgesDelete([edge]),
          },
        ],
      });
    },
    [onDocChange, handleEdgesDelete],
  );

  const openPaneMenu = useCallback(
    (event: React.MouseEvent) => {
      event.preventDefault();
      if (!flowRef.current) return;
      const flowPos = flowRef.current.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
      setMenu({
        x: event.clientX,
        y: event.clientY,
        items: [
          {
            label: "Add node here",
            onSelect: () =>
              addNodeAt(flowPos.x - DEFAULT_WIDTH / 2, flowPos.y - DEFAULT_HEIGHT / 2),
          },
          {
            label: "Paste",
            disabled: !clipboard.hasClip(),
            onSelect: () =>
              onDocChange(clipboard.paste(docRef.current, { x: 0, y: 0 })),
          },
        ],
      });
    },
    [addNodeAt, clipboard, onDocChange],
  );

  // ---------------- Keyboard shortcuts ----------------

  useEffect(() => {
    const isEditableTarget = (t: EventTarget | null) => {
      if (!(t instanceof HTMLElement)) return false;
      const tag = t.tagName;
      return tag === "INPUT" || tag === "TEXTAREA" || t.isContentEditable;
    };
    const onKey = (e: KeyboardEvent) => {
      if (isEditableTarget(e.target)) return;
      const meta = e.metaKey || e.ctrlKey;
      if (meta && !e.shiftKey && e.key.toLowerCase() === "z") {
        e.preventDefault();
        onUndo();
        return;
      }
      if ((meta && e.shiftKey && e.key.toLowerCase() === "z") || (meta && e.key.toLowerCase() === "y")) {
        e.preventDefault();
        onRedo();
        return;
      }
      if (meta && e.key.toLowerCase() === "c") {
        if (selectedNodeIds.current.length > 0) {
          e.preventDefault();
          clipboard.copy(docRef.current, selectedNodeIds.current);
        }
        return;
      }
      if (meta && e.key.toLowerCase() === "v") {
        if (clipboard.hasClip()) {
          e.preventDefault();
          onDocChange(clipboard.paste(docRef.current));
        }
        return;
      }
      if (meta && e.key.toLowerCase() === "d") {
        if (selectedNodeIds.current.length > 0) {
          e.preventDefault();
          onDocChange(clipboard.duplicate(docRef.current, selectedNodeIds.current));
        }
        return;
      }
      if (meta && e.key.toLowerCase() === "a") {
        e.preventDefault();
        if (flowRef.current) {
          flowRef.current.setNodes((ns) => ns.map((n) => ({ ...n, selected: true })));
          flowRef.current.setEdges((es) => es.map((edge) => ({ ...edge, selected: true })));
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [clipboard, onDocChange, onRedo, onUndo]);

  const handleDragOver = useCallback((event: React.DragEvent) => {
    if (event.dataTransfer.types.includes("application/plot-preset")) {
      event.preventDefault();
      event.dataTransfer.dropEffect = "copy";
    }
  }, []);

  /** Hit-test: first node (in reverse doc order so top-rendered wins)
   *  whose absolute bounding box contains the given flow point. */
  const containerAtFlowPoint = useCallback(
    (x: number, y: number): DocNode | null => {
      // Nodes with a parent position relative to the parent; compute absolute.
      const absPos = (n: DocNode): { x: number; y: number } => {
        let ax = n.x;
        let ay = n.y;
        let cur: DocNode | undefined = n;
        while (cur?.parent_id) {
          const parent = nodeById.get(cur.parent_id);
          if (!parent) break;
          ax += parent.x;
          ay += parent.y;
          cur = parent;
        }
        return { x: ax, y: ay };
      };
      // Iterate in reverse so later-drawn nodes (on top) win.
      for (let i = doc.nodes.length - 1; i >= 0; i--) {
        const n = doc.nodes[i];
        const { x: ax, y: ay } = absPos(n);
        if (x >= ax && x <= ax + n.width && y >= ay && y <= ay + n.height) {
          return n;
        }
      }
      return null;
    },
    [doc.nodes, nodeById],
  );

  /**
   * Slide a rectangle off siblings it overlaps. Walks diagonally by
   * ``OFFSET_STEP`` px up to ``MAX_STEPS`` tries. Caller passes the list
   * of existing node rects in the same coordinate space so nested drops
   * can use parent-local coords and free drops can use absolute coords.
   */
  const findFreeSpot = useCallback(
    (
      baseX: number,
      baseY: number,
      w: number,
      h: number,
      siblings: { x: number; y: number; width: number; height: number }[],
    ): { x: number; y: number } => {
      const OFFSET_STEP = 32;
      const MAX_STEPS = 24;
      const overlaps = (
        a: [number, number, number, number],
        b: [number, number, number, number],
      ): boolean =>
        !(a[2] <= b[0] || b[2] <= a[0] || a[3] <= b[1] || b[3] <= a[1]);
      let x = baseX;
      let y = baseY;
      for (let i = 0; i < MAX_STEPS; i++) {
        const mine: [number, number, number, number] = [x, y, x + w, y + h];
        const collision = siblings.some((s) =>
          overlaps(mine, [s.x, s.y, s.x + s.width, s.y + s.height]),
        );
        if (!collision) return { x, y };
        x += OFFSET_STEP;
        y += OFFSET_STEP;
      }
      return { x, y }; // gave up — place it at the final nudged position
    },
    [],
  );

  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      if (!flowRef.current) return;
      const raw = event.dataTransfer.getData("application/plot-preset");
      if (!raw) return;
      event.preventDefault();
      let preset: NodePreset;
      try {
        preset = JSON.parse(raw) as NodePreset;
      } catch {
        return;
      }
      const pos = flowRef.current.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
      const w = preset.width ?? DEFAULT_WIDTH;
      const h = preset.height ?? DEFAULT_HEIGHT;

      const container = containerAtFlowPoint(pos.x, pos.y);
      const resolved = resolveDropTarget(
        preset as StencilPreset,
        container ? { id: container.id, kind: container.kind } : null,
      );
      if ("error" in resolved) {
        window.alert(resolved.error);
        return;
      }
      // v0.11.5 — if the preset already carries the target master id (the
      // common case now that the stencil generates per-master presets),
      // skip the picker entirely and create the ref directly. The picker
      // is reserved for the rewire flow on orphan refs.
      const presetHasRefId =
        (preset.kind === "actor_ref" && preset.ref_actor_id) ||
        (preset.kind === "mission_ref" && preset.ref_mission_id) ||
        (preset.kind === "value_ref" && preset.ref_value_id) ||
        (preset.kind === "identity_ref" && preset.ref_identity_id);
      // actor_ref: only open picker if the preset has no ref_actor_id yet.
      if (preset.kind === "actor_ref" && !presetHasRefId) {
        setPendingActorRef({ mode: "create", preset, pos, resolved });
        return;
      }
      // Foundation refs: only open picker for legacy unbound presets.
      if (
        (preset.kind === "mission_ref" ||
          preset.kind === "value_ref" ||
          preset.kind === "identity_ref") &&
        !presetHasRefId
      ) {
        setPendingFoundationRef({
          mode: "create",
          refKind: preset.kind,
          preset,
          pos,
          resolved,
        });
        return;
      }
      if (resolved.parentId) {
        const parent = nodeById.get(resolved.parentId)!;
        // Position relative to parent's top-left.
        const parentAbs = (() => {
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
          return { x: ax, y: ay };
        })();
        const rawLocalX = Math.max(8, pos.x - parentAbs.x - w / 2);
        const rawLocalY = Math.max(28, pos.y - parentAbs.y - h / 2);
        const siblings = doc.nodes.filter((n) => n.parent_id === resolved.parentId);
        const spot = findFreeSpot(rawLocalX, rawLocalY, w, h, siblings);
        addNestedNodeAt({
          parentId: resolved.parentId,
          localX: spot.x,
          localY: spot.y,
          preset,
        });
      } else {
        const rawX = pos.x - w / 2;
        const rawY = pos.y - h / 2;
        const siblings = doc.nodes.filter((n) => n.parent_id === null);
        const spot = findFreeSpot(rawX, rawY, w, h, siblings);
        addNodeAt(spot.x, spot.y, preset);
      }
    },
    [addNodeAt, addNestedNodeAt, containerAtFlowPoint, doc.nodes, findFreeSpot, nodeById],
  );

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
