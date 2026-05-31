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
import { useTranslation } from "react-i18next";
import type { Edge, Node, ReactFlowInstance } from "reactflow";
import type { CanvasDoc } from "../../types";
import { useDialog } from "../../shell/dialog/DialogProvider";
import { type ContextMenuItem } from "../SketchContextMenu";
import { type SketchClipboard } from "../useSketchClipboard";
import { DEFAULT_HEIGHT, DEFAULT_WIDTH } from "./constants";
import { classifyEdge } from "../../flow/edgeSemantics";
import { groupSelected, ungroup } from "./groupActions";

// v0.29.0 (D-2026-05-30-I) — fresh group id. Runtime-only app code, so
// Date.now / Math.random are fine here (mirrors useNodeCreation.freshId).
function freshGroupId(): string {
  return `g_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

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
  /** v0.29.0 (D-2026-05-30-I) — current canvas selection, for the
   *  "Group selected" action. */
  selectedNodeIds: MutableRefObject<string[]>;
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
  selectedNodeIds,
}: UseContextMenusArgs): UseContextMenusResult {
  const { t } = useTranslation();
  const dialog = useDialog();
  const [menu, setMenu] = useState<MenuState | null>(null);
  const closeMenu = useCallback(() => setMenu(null), []);

  const openNodeMenu = useCallback(
    (event: ReactMouseEvent, node: Node) => {
      event.preventDefault();
      const docNode = docRef.current.nodes.find((n) => n.id === node.id);
      const isProject = docNode?.kind === "project";
      const isGroup = docNode?.kind === "group";
      // v0.29.0 (D-2026-05-30-I) — "Group selected" appears when ≥ 2
      // nodes are selected; the right-clicked node is included if the
      // selection somehow missed it.
      const selection = Array.from(
        new Set([...selectedNodeIds.current, node.id]),
      );
      const canGroup = selection.length >= 2;
      const groupItems: ContextMenuItem[] = [];
      if (canGroup) {
        groupItems.push({
          label: `Group selected (${selection.length})`,
          onSelect: () =>
            onDocChange(groupSelected(docRef.current, selection, freshGroupId())),
        });
      }
      if (isGroup) {
        groupItems.push({
          label: "Ungroup",
          onSelect: () => onDocChange(ungroup(docRef.current, node.id)),
        });
      }
      if (groupItems.length > 0) {
        groupItems.push({ label: "", divider: true, onSelect: () => {} });
      }
      setMenu({
        x: event.clientX,
        y: event.clientY,
        items: [
          ...groupItems,
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
    [docRef, onDocChange, clipboard, handleNodesDelete, selectedNodeIds],
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
    [docRef, onDocChange, handleEdgesDelete, dialog, t],
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
