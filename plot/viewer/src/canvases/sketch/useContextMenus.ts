// Three React Flow context menus (pane / node / edge), each with
// their own item list. State lives in this hook; the SC shell wires
// the four returned callbacks (open*Menu + closeMenu) to the
// matching React Flow props.
//
// The hook reads ``docRef.current`` (load-bearing freshness per the
// coupling map) directly inside each handler so menu actions always
// operate on the most recent doc state, even when fired mid-drag.
import {
  type MutableRefObject,
  type MouseEvent as ReactMouseEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { useTranslation } from "react-i18next";
import type { Edge, Node, ReactFlowInstance } from "reactflow";
import type { CanvasDoc } from "../../types";
import { useDialog } from "../../shell/dialog/DialogProvider";
import { type ContextMenuItem } from "../SketchContextMenu";
import { type SketchClipboard } from "../useSketchClipboard";
import { DEFAULT_HEIGHT, DEFAULT_WIDTH } from "./constants";
import { classifyEdge } from "../../flow/edgeSemantics";

export interface MenuState {
  x: number;
  y: number;
  items: ContextMenuItem[];
}

export interface UseContextMenusArgs {
  docRef: MutableRefObject<CanvasDoc>;
  flowRef: MutableRefObject<ReactFlowInstance | null>;
  onDocChange: (next: CanvasDoc) => void;
  clipboard: SketchClipboard;
  handleNodesDelete: (deleted: Node[]) => void;
  handleEdgesDelete: (deleted: Edge[]) => void;
  addNodeAt: (x: number, y: number) => void;
}

export interface UseContextMenusResult {
  menu: MenuState | null;
  closeMenu: () => void;
  openNodeMenu: (event: ReactMouseEvent, node: Node) => void;
  openEdgeMenu: (event: ReactMouseEvent, edge: Edge) => void;
  openPaneMenu: (event: ReactMouseEvent) => void;
}

const COLOR_PALETTE = [
  "#ffffff",
  "#fecaca",
  "#fed7aa",
  "#fef08a",
  "#bbf7d0",
  "#bae6fd",
  "#ddd6fe",
];

export function useContextMenus({
  docRef,
  flowRef,
  onDocChange,
  clipboard,
  handleNodesDelete,
  handleEdgesDelete,
  addNodeAt,
}: UseContextMenusArgs): UseContextMenusResult {
  const { t } = useTranslation();
  const dialog = useDialog();
  const [menu, setMenu] = useState<MenuState | null>(null);
  const closeMenu = useCallback(() => setMenu(null), []);

  // D-2026-06-15-N (broadened D-2026-06-16-A) — one-shot guard against the
  // trailing ``contextmenu`` WebKit emits after a macOS-trackpad
  // drag-release. We watch the RAW pointer gesture at the window level: a
  // ``pointerup`` that moved more than a few px from its ``pointerdown`` is a
  // DRAG, so the next ``contextmenu`` is swallowed. This is kind- and
  // canvas-agnostic — it does NOT depend on React Flow firing
  // ``onNodeDragStop`` per node (which left categories / detail canvases
  // uncovered). A real right-click never moves, so its menu still opens; and
  // each fresh pointerdown re-enables the menu (disarms).
  const suppressNextContextMenuRef = useRef(false);
  const pointerDownPosRef = useRef<{ x: number; y: number } | null>(null);
  useEffect(() => {
    const DRAG_THRESHOLD_PX = 5;
    const onDown = (e: PointerEvent) => {
      pointerDownPosRef.current = { x: e.clientX, y: e.clientY };
      suppressNextContextMenuRef.current = false;
    };
    const onUp = (e: PointerEvent) => {
      const start = pointerDownPosRef.current;
      pointerDownPosRef.current = null;
      if (!start) return;
      const moved =
        Math.hypot(e.clientX - start.x, e.clientY - start.y) > DRAG_THRESHOLD_PX;
      if (moved) suppressNextContextMenuRef.current = true;
    };
    const onCancel = () => {
      pointerDownPosRef.current = null;
    };
    window.addEventListener("pointerdown", onDown, true);
    window.addEventListener("pointerup", onUp, true);
    window.addEventListener("pointercancel", onCancel, true);
    return () => {
      window.removeEventListener("pointerdown", onDown, true);
      window.removeEventListener("pointerup", onUp, true);
      window.removeEventListener("pointercancel", onCancel, true);
    };
  }, []);
  const consumeDragSuppression = useCallback((event: ReactMouseEvent): boolean => {
    if (!suppressNextContextMenuRef.current) return false;
    suppressNextContextMenuRef.current = false;
    event.preventDefault();
    return true;
  }, []);

  const openNodeMenu = useCallback(
    (event: ReactMouseEvent, node: Node) => {
      event.preventDefault();
      if (consumeDragSuppression(event)) return;
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
          ...COLOR_PALETTE.map((hex) => ({
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
    [docRef, onDocChange, clipboard, handleNodesDelete, consumeDragSuppression],
  );

  const openEdgeMenu = useCallback(
    (event: ReactMouseEvent, edge: Edge) => {
      event.preventDefault();
      if (consumeDragSuppression(event)) return;
      // Look up the canonical doc edge for the current ``directed`` flag —
      // ``edge`` is the React-Flow projection (which may have a derived
      // markerEnd but doesn't carry the source ``directed`` field).
      const docEdge = docRef.current.edges.find((e) => e.id === edge.id);
      const isDirected = docEdge?.directed ?? true;
      setMenu({
        x: event.clientX,
        y: event.clientY,
        items: [
          {
            // v0.26.0 (D-2026-05-25-A) — toggle the directed flag.
            // Directed edges show an arrowhead at the target end and
            // participate in fold / parent-child derivation.
            label: isDirected ? "Remove direction (→ undirected)" : "Add direction (source → target)",
            onSelect: () => {
              const current = docRef.current;
              onDocChange({
                ...current,
                edges: current.edges.map((e) =>
                  e.id === edge.id ? { ...e, directed: !e.directed } : e,
                ),
              });
            },
          },
          {
            // v0.29.2 (D-2026-05-31-A) — flip orientation: swap
            // source↔target so the arrowhead points the other way.
            // Handles are typed by side (BaseNode: t/l = target-only,
            // r/b = source-only), so the old handle ids can't carry
            // over (a target handle can't act as a source). Null both
            // and let RF route through each node's default valid
            // handle. Orientation only; ``directed`` is preserved.
            // The edge stays user-drawn — this re-orients one already
            // drawn (Cmd+Z undoes it).
            label: "Flip direction (swap source ↔ target)",
            onSelect: () => {
              const current = docRef.current;
              // v0.30.0 (D-2026-05-31-C) — flipping changes the source,
              // so re-assign the stored ``relation`` from the new
              // source-node kind; otherwise a flipped edge keeps a stale
              // semantic (e.g. a backwards anchor→mission edge flipped to
              // mission→anchor would stay "flow" instead of "injection").
              // The new source is the *doc* edge's current target (the
              // ``edge`` arg is the RF projection and lacks source/target).
              onDocChange({
                ...current,
                edges: current.edges.map((e) =>
                  e.id === edge.id
                    ? {
                        ...e,
                        source: e.target,
                        target: e.source,
                        sourceHandle: null,
                        targetHandle: null,
                        relation: classifyEdge(
                          current.canvas_kind,
                          current.nodes.find((n) => n.id === e.target)?.kind,
                        ),
                      }
                    : e,
                ),
              });
            },
          },
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
            onSelect: async () => {
              const newLabel = await dialog.prompt({
                message: t("node.edgeLabelPrompt"),
                defaultValue: edge.label ? String(edge.label) : "",
              });
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
    [docRef, onDocChange, handleEdgesDelete, dialog, t, consumeDragSuppression],
  );

  const openPaneMenu = useCallback(
    (event: ReactMouseEvent) => {
      event.preventDefault();
      if (consumeDragSuppression(event)) return;
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
    [docRef, flowRef, addNodeAt, clipboard, onDocChange, consumeDragSuppression],
  );

  return { menu, closeMenu, openNodeMenu, openEdgeMenu, openPaneMenu };
}
