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
import { LayerBackground } from "./LayerBackground";
import { SketchBodyModal } from "./SketchBodyModal";
import { SketchContextMenu, type ContextMenuItem } from "./SketchContextMenu";
import { SketchEdgeModal, VALUE_FORM_COLORS } from "./SketchEdgeModal";
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
}

/** Snap a flow y-coordinate into the correct layer for a given kind.
 *  Upper band = y < 0 = Services; lower band = y > 0 = Actors. */
function snapYToLayer(y: number, kind: NodeKind | null | undefined, nodeHeight: number): number {
  if (kind === "service") {
    // Clamp so the whole node stays strictly above the divider.
    const maxY = -20 - nodeHeight;
    return Math.min(y, maxY);
  }
  if (kind === "actor") {
    return Math.max(y, 20);
  }
  return y;
}

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
      const hasChildren = (childIdsByParent.get(n.id)?.length ?? 0) > 0;
      const base: Node<SketchNodeData> = {
        id: n.id,
        type: "sketch",
        position: { x: n.x, y: n.y },
        style: { width: n.width, height: n.height },
        data: {
          label: n.label,
          body: n.body,
          color: n.color,
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
      if (n.parent_id) {
        base.parentNode = n.parent_id;
        base.extent = "parent";
      }
      if (hasChildren && !n.collapsed) {
        base.style = { ...base.style, zIndex: -1 };
      }
      out.push(base);
    }
    return out;
  }, [doc.nodes, childIdsByParent, nearestCollapsedAncestor, subtreeSize, toggleCollapsed, updateNode]);

  const edges = useMemo<Edge[]>(() => {
    const out: Edge[] = [];
    for (const e of doc.edges) {
      const sAncestor = nearestCollapsedAncestor(e.source);
      const tAncestor = nearestCollapsedAncestor(e.target);
      const src = sAncestor ?? e.source;
      const tgt = tAncestor ?? e.target;
      if (sAncestor && tAncestor && sAncestor === tAncestor) continue;
      if (src === tgt) continue;
      // When Value Flow is on, paint the stroke using the first listed
      // value form's colour. Multi-form edges get the first form's colour
      // with a heavier weight so the user can at least eyeball them.
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
      const posById = new Map<string, { x: number; y: number; dragging?: boolean }>();
      for (const c of changes) {
        if (c.type === "position" && c.position) {
          posById.set(c.id, { ...c.position, dragging: c.dragging });
        }
      }
      if (posById.size === 0) return;
      const current = docRef.current;
      onDocChange({
        ...current,
        nodes: current.nodes.map((n) => {
          const p = posById.get(n.id);
          if (!p) return n;
          // On drag-stop (dragging === false or undefined), snap top-level
          // nodes back into their correct layer if the user crossed the
          // divider. Mid-drag frames stay unsnapped so the node visually
          // tracks the cursor.
          const isCommit = p.dragging !== true;
          if (isCommit && n.parent_id === null) {
            const snappedY = snapYToLayer(p.y, n.kind, n.height);
            return { ...n, x: p.x, y: snappedY };
          }
          return { ...n, x: p.x, y: p.y };
        }),
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
      const height = preset?.height ?? DEFAULT_HEIGHT;
      const snappedY = snapYToLayer(y, preset?.kind ?? null, height);
      const newNode: DocNode = {
        id,
        label: preset?.label ?? "",
        body: "",
        x,
        y: snappedY,
        width: preset?.width ?? DEFAULT_WIDTH,
        height,
        color: preset?.color ?? DEFAULT_COLOR,
        shape: preset?.shape ?? "rounded",
        icon: preset?.icon ?? null,
        kind: preset?.kind ?? null,
        parent_id: null,
        collapsed: false,
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
      };
      const current = docRef.current;
      onDocChange({ ...current, nodes: [...current.nodes, newNode] });
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

  const handleToolbarAdd = useCallback(() => {
    if (!flowRef.current) return;
    const { innerWidth, innerHeight } = window;
    const centre = flowRef.current.screenToFlowPosition({
      x: innerWidth / 2,
      y: innerHeight / 2,
    });
    addNodeAt(centre.x - DEFAULT_WIDTH / 2, centre.y - DEFAULT_HEIGHT / 2);
  }, [addNodeAt]);

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
        const localX = pos.x - parentAbs.x - w / 2;
        const localY = pos.y - parentAbs.y - h / 2;
        addNestedNodeAt({
          parentId: resolved.parentId,
          localX: Math.max(8, localX),
          localY: Math.max(28, localY),
          preset,
        });
      } else {
        addNodeAt(pos.x - w / 2, pos.y - h / 2, preset);
      }
    },
    [addNodeAt, addNestedNodeAt, containerAtFlowPoint, nodeById],
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
        onAddNode={handleToolbarAdd}
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
        onPaneContextMenu={openPaneMenu}
        onInit={(inst) => {
          flowRef.current = inst;
        }}
        fitView
        fitViewOptions={{ padding: 0.2 }}
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
        <LayerBackground />
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
    </div>
  );
}

export { applyEdgeChanges, applyNodeChanges };
