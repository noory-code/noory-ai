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
  useState,
} from "react";
import type { Edge, Node, ReactFlowInstance } from "reactflow";
import type { CanvasDoc } from "../../types";
import { type ContextMenuItem } from "../SketchContextMenu";
import { type SketchClipboard } from "../useSketchClipboard";
import { DEFAULT_HEIGHT, DEFAULT_WIDTH } from "./constants";

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
  const [menu, setMenu] = useState<MenuState | null>(null);
  const closeMenu = useCallback(() => setMenu(null), []);

  const openNodeMenu = useCallback(
    (event: ReactMouseEvent, node: Node) => {
      event.preventDefault();
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
    [docRef, onDocChange, clipboard, handleNodesDelete],
  );

  const openEdgeMenu = useCallback(
    (event: ReactMouseEvent, edge: Edge) => {
      event.preventDefault();
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
              const newLabel = window.prompt(
                "Edge label:",
                edge.label ? String(edge.label) : "",
              );
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
    [docRef, onDocChange, handleEdgesDelete],
  );

  const openPaneMenu = useCallback(
    (event: ReactMouseEvent) => {
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
    [docRef, flowRef, addNodeAt, clipboard, onDocChange],
  );

  return { menu, closeMenu, openNodeMenu, openEdgeMenu, openPaneMenu };
}
