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
import { autoLayout } from "../flow/autoLayout";
import type { NodeKind, SketchDoc, SketchEdge, SketchNode as DocNode } from "../types";
import { ActorRefPicker } from "./ActorRefPicker";
import { SketchBodyModal } from "./SketchBodyModal";
import { SketchContextMenu, type ContextMenuItem } from "./SketchContextMenu";
import { SketchEdgeModal, VALUE_FORM_COLORS } from "./SketchEdgeModal";
import { SketchInspector } from "./SketchInspector";
import { SketchNode, type SketchNodeData } from "./SketchNode";
import { resolveDropTarget, type StencilPreset } from "./SketchStencil";
import { SketchToolbar, type SaveState } from "./SketchToolbar";
import { useSketchClipboard } from "./useSketchClipboard";

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
}

// Note (2026-04-20): the earlier implementation snapped services to an
// upper band and actors to a lower band. The user clarified that the
// "two layers" metaphor was conceptual, not spatial — services and
// actors coexist on the same 2D plane, differentiated by kind (shape /
// colour / icon), not by y position. Layer-snap helper removed.

export interface SketchCanvasProps {
  doc: SketchDoc;
  onDocChange: (next: SketchDoc) => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  saveState: SaveState;
  onDownload: () => void;
  onUpload: () => void;
  /** v0.2 multi-canvas: double-click a node to drill into its Detail canvas (Services only). */
  onNodeDrill?: (nodeId: string) => void;
  /**
   * v0.2 multi-canvas: actors available in the ActorRefPicker. Supplied by
   * the App (it holds the unfiltered doc), because this canvas may itself
   * be showing a tab-filtered view that excludes the actors.
   */
  availableActors?: DocNode[];
  /**
   * v0.2 multi-canvas: when set, the canvas selects this node on mount
   * (used for jumping from an actor_ref to its target in the Actors canvas).
   * Fires ``onSelectionConsumed`` once applied so the URL param can be cleared.
   */
  selectNodeId?: string | null;
  onSelectionConsumed?: () => void;
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
  saveState,
  onDownload,
  onUpload,
  onNodeDrill,
  availableActors,
  selectNodeId,
  onSelectionConsumed,
}: SketchCanvasProps) {
  const docRef = useRef<SketchDoc>(doc);
  docRef.current = doc;
  const flowRef = useRef<ReactFlowInstance | null>(null);
  const selectedNodeIds = useRef<string[]>([]);
  const clipboard = useSketchClipboard();
  const [menu, setMenu] = useState<MenuState | null>(null);
  const [bodyModalNodeId, setBodyModalNodeId] = useState<string | null>(null);
  const [edgeModalId, setEdgeModalId] = useState<string | null>(null);
  const [valueFlowOn, setValueFlowOn] = useState(false);
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
  const [inspectorNodeId, setInspectorNodeId] = useState<string | null>(null);

  // v0.2 multi-canvas: honour ``selectNodeId`` arrival (e.g., jumping from
  // an actor_ref on Services to its target on Actors). Runs once per
  // distinct incoming id; afterwards the App clears its URL param.
  const lastAppliedSelectRef = useRef<string | null>(null);
  useEffect(() => {
    if (!selectNodeId) return;
    if (lastAppliedSelectRef.current === selectNodeId) return;
    if (!doc.nodes.some((n) => n.id === selectNodeId)) return;
    setInspectorNodeId(selectNodeId);
    lastAppliedSelectRef.current = selectNodeId;
    // Centre the viewport on the node, best-effort.
    const inst = flowRef.current;
    if (inst) inst.fitView({ nodes: [{ id: selectNodeId }], padding: 0.5, duration: 300 });
    onSelectionConsumed?.();
  }, [selectNodeId, doc.nodes, onSelectionConsumed]);

  // Orphan detection: actor_refs whose target isn't in the available-actor
  // set (either never was, or was just deleted on the Actors canvas).
  const orphanActorRefIds = useMemo(() => {
    const validActorIds = new Set((availableActors ?? doc.nodes).filter((n) => n.kind === "actor").map((n) => n.id));
    const orphans = new Set<string>();
    for (const n of doc.nodes) {
      if (n.kind !== "actor_ref") continue;
      if (!n.ref_actor_id || !validActorIds.has(n.ref_actor_id)) {
        orphans.add(n.id);
      }
    }
    return orphans;
  }, [doc.nodes, availableActors]);

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

  // Precompute a parent → children map so we can render containers, sort
  // parents before children (React Flow requirement), and compute visibility
  // under collapse.
  const childIdsByParent = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const n of doc.nodes) {
      if (n.parent_id) {
        const arr = map.get(n.parent_id) ?? [];
        arr.push(n.id);
        map.set(n.parent_id, arr);
      }
    }
    return map;
  }, [doc.nodes]);

  const nodeById = useMemo(() => {
    const m = new Map<string, DocNode>();
    for (const n of doc.nodes) m.set(n.id, n);
    return m;
  }, [doc.nodes]);

  // Nearest collapsed ancestor of ``nodeId`` (not counting nodeId itself),
  // or null if nothing on the chain is collapsed.
  const nearestCollapsedAncestor = useCallback(
    (nodeId: string): string | null => {
      let current = nodeById.get(nodeId);
      while (current?.parent_id) {
        const parent = nodeById.get(current.parent_id);
        if (parent && parent.collapsed) return parent.id;
        current = parent;
      }
      return null;
    },
    [nodeById],
  );

  const toggleCollapsed = useCallback(
    (nodeId: string) => {
      const current = docRef.current;
      onDocChange({
        ...current,
        nodes: current.nodes.map((n) =>
          n.id === nodeId ? { ...n, collapsed: !n.collapsed } : n,
        ),
      });
    },
    [onDocChange],
  );

  // Subtree size (recursive descendant count) — shown on the collapsed
  // badge so user sees "how much is hidden".
  const subtreeSize = useCallback(
    (nodeId: string): number => {
      const direct = childIdsByParent.get(nodeId) ?? [];
      let total = direct.length;
      for (const c of direct) total += subtreeSize(c);
      return total;
    },
    [childIdsByParent],
  );

  const nodes = useMemo<Node<SketchNodeData>[]>(() => {
    // Parents first, children after — React Flow requirement.
    const ordered = [...doc.nodes].sort((a, b) => {
      if (!a.parent_id && b.parent_id) return -1;
      if (a.parent_id && !b.parent_id) return 1;
      return 0;
    });
    const out: Node<SketchNodeData>[] = [];
    for (const n of ordered) {
      // Hide nodes whose ancestor chain contains a collapsed container.
      if (nearestCollapsedAncestor(n.id)) continue;
      // v0.2 correction (2026-04-20): rule / content are edited through
      // the right-hand Inspector panel, never rendered on the canvas.
      if (n.kind === "rule" || n.kind === "content") continue;
      const hasChildren = (childIdsByParent.get(n.id)?.length ?? 0) > 0;
      // Orphan actor_ref visual override: red-tinted fill, "⚠ " prefix so the
      // break is obvious even at thumbnail scale. Rendering stays in the
      // normal SketchNode component — no branch in the renderer.
      const isOrphan = orphanActorRefIds.has(n.id);
      const visualColor = isOrphan ? "#fee2e2" : n.color;
      const visualLabel = isOrphan ? `⚠ ${n.label}` : n.label;
      const base: Node<SketchNodeData> = {
        id: n.id,
        type: "sketch",
        position: { x: n.x, y: n.y },
        style: { width: n.width, height: n.height },
        data: {
          label: visualLabel,
          body: n.body,
          color: visualColor,
          width: n.width,
          height: n.height,
          shape: n.shape,
          icon: n.icon,
          onLabelChange: (next: string) => updateNode(n.id, { label: next }),
          onOpenBody: () => setBodyModalNodeId(n.id),
          onResize: (w: number, h: number) => updateNode(n.id, { width: w, height: h }),
          hasChildren,
          collapsed: n.collapsed,
          childCount: hasChildren ? subtreeSize(n.id) : 0,
          onToggleCollapse: hasChildren ? () => toggleCollapsed(n.id) : undefined,
        },
      };
      // v0.2 correction (2026-04-20): parent_id is used for two distinct
      // semantic categories:
      //   - composition (rule, content) — data-only, Inspector panel.
      //   - hierarchy (sub-actor, sub-service) — rendered as a sibling
      //     with an auto-generated decomposition edge (see `edges` below).
      // In neither case do we use React Flow's parentNode nesting any
      // more: hierarchy is not "inside", it's "beside + linked".
      out.push(base);
    }
    return out;
  }, [
    doc.nodes,
    childIdsByParent,
    nearestCollapsedAncestor,
    subtreeSize,
    toggleCollapsed,
    updateNode,
    orphanActorRefIds,
  ]);

  const edges = useMemo<Edge[]>(() => {
    const out: Edge[] = [];
    // User-drawn edges.
    for (const e of doc.edges) {
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
  }, [doc.edges, nearestCollapsedAncestor, valueFlowOn]);

  // Apply every position change (including mid-drag) so the node visually
  // tracks the cursor. The debounced PUT in App.tsx coalesces the stream
  // down to one save per 400 ms, so drags don't flood the server.
  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      const posById = new Map<string, { x: number; y: number }>();
      for (const c of changes) {
        if (c.type === "position" && c.position) posById.set(c.id, c.position);
      }
      if (posById.size === 0) return;
      const current = docRef.current;
      onDocChange({
        ...current,
        nodes: current.nodes.map((n) =>
          posById.has(n.id) ? { ...n, ...posById.get(n.id)! } : n,
        ),
      });
    },
    [onDocChange],
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
      const ids = new Set(deleted.map((n) => n.id));
      const current = docRef.current;
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
        body: "",
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
        ref_actor_id: preset?.ref_actor_id ?? null,
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
        body: "",
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
        ref_actor_id: preset?.ref_actor_id ?? null,
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

  const handleAutoLayout = useCallback(() => {
    onDocChange(autoLayout(docRef.current));
  }, [onDocChange]);

  const handleSelectionChange = useCallback((sel: OnSelectionChangeParams) => {
    selectedNodeIds.current = sel.nodes.map((n) => n.id);
  }, []);

  // ---------------- Context menu ----------------

  const closeMenu = useCallback(() => setMenu(null), []);

  const openNodeMenu = useCallback(
    (event: React.MouseEvent, node: Node) => {
      event.preventDefault();
      const colors = ["#ffffff", "#fecaca", "#fed7aa", "#fef08a", "#bbf7d0", "#bae6fd", "#ddd6fe"];
      setMenu({
        x: event.clientX,
        y: event.clientY,
        items: [
          {
            label: "Duplicate",
            onSelect: () => {
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
            label: "Delete",
            danger: true,
            onSelect: () => handleNodesDelete([node]),
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
          { label: "", divider: true, onSelect: () => {} },
          {
            label: "Auto layout",
            onSelect: handleAutoLayout,
          },
        ],
      });
    },
    [addNodeAt, clipboard, onDocChange, handleAutoLayout],
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
      // actor_ref: defer creation until the picker modal resolves which
      // actor this reference points at.
      if (preset.kind === "actor_ref") {
        setPendingActorRef({ mode: "create", preset, pos, resolved });
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
        saveState={saveState}
        canUndo={canUndo}
        canRedo={canRedo}
        onUndo={onUndo}
        onRedo={onRedo}
        onAutoLayout={handleAutoLayout}
        onDownload={onDownload}
        onUpload={onUpload}
        valueFlowOn={valueFlowOn}
        onToggleValueFlow={() => setValueFlowOn((v) => !v)}
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
        onNodeClick={(_evt, n) => setInspectorNodeId(n.id)}
        onNodeDoubleClick={(_evt, n) => onNodeDrill?.(n.id)}
        onPaneClick={() => setInspectorNodeId(null)}
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
        onRepickActorRef={(nodeId) => setPendingActorRef({ mode: "rewire", nodeId })}
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
            body: "",
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
            ref_actor_id: null,
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
