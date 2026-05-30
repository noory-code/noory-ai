// Node-creation helpers: addNodeAt for top-level nodes,
// addNestedNodeAt for sub-actor / sub-service drops onto an existing
// container, addCompositionChild for Inspector-driven rule / content
// children.
//
// v0.15 Phase 2.10 — uses the per-kind ``createBlankNode`` factory
// from ``../../domain`` instead of inlining the god-style 47-field
// initialiser. Each kind's defaults come from its own entity class's
// ``fromJson`` so the wire shape is always canonical.
import { type MutableRefObject, useCallback } from "react";
import { createBlankNode } from "../../domain";
import { classifyEdge } from "../../flow/edgeSemantics";
import type { CanvasDoc, NodeKind, SketchNode as DocNode } from "../../types";
import {
  anchorRadialPosition,
  countFoundationKinds,
  isFoundationRadialKind,
} from "./anchorRadialLayout";
import { DEFAULT_COLOR, DEFAULT_HEIGHT, DEFAULT_WIDTH } from "./constants";
import type { NodePreset } from "./types";

export interface UseNodeCreationArgs {
  docRef: MutableRefObject<CanvasDoc>;
  onDocChange: (next: CanvasDoc) => void;
  /** v0.16.12 (D-2026-05-12-O) — wrapper-supplied flag. True on
   *  FoundationCanvas: new Mission / CoreValue / Identity nodes snap
   *  to anchor-radial slots. False (default) on every other wrapper.
   *  Per D-2026-05-12-F structural-guards, sketch hooks must not
   *  read ``doc.canvas_kind`` — wrappers signal canvas-specific
   *  behaviour via explicit props. */
  applyAnchorRadialLayout?: boolean;
}

export interface UseNodeCreationResult {
  addNodeAt: (x: number, y: number, preset?: NodePreset) => void;
  addNestedNodeAt: (args: {
    parentId: string;
    localX: number;
    localY: number;
    preset: NodePreset;
  }) => void;
  /** Inspector "+ child" action. Creates a rule / content composition
   *  child of ``parentId`` with kind-specific defaults (shape / colour /
   *  icon / dimensions). No edge — composition is data-only. */
  addCompositionChild: (parentId: string, kind: "rule" | "content") => void;
}

function freshId(prefix: "n" | "e"): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

/** v0.15 Phase 2.10 — drag-from-stencil presets must always specify a
 *  kind. The legacy "kind: null" path is gone: a node without a kind
 *  has no domain meaning. */
function requirePresetKind(preset: NodePreset | undefined): NodeKind {
  if (!preset?.kind) {
    throw new Error(
      "useNodeCreation: preset.kind is required (the v0.14 untyped-node " +
        "path was retired in the v0.15 structural reset).",
    );
  }
  return preset.kind;
}

export function useNodeCreation({
  docRef,
  onDocChange,
  applyAnchorRadialLayout = false,
}: UseNodeCreationArgs): UseNodeCreationResult {
  const addNodeAt = useCallback(
    (x: number, y: number, preset?: NodePreset) => {
      const kind = requirePresetKind(preset);
      const current = docRef.current;
      const width = preset?.width ?? DEFAULT_WIDTH;
      const height = preset?.height ?? DEFAULT_HEIGHT;
      // v0.16.11 (D-2026-05-12-N) / v0.16.12 (D-2026-05-12-O):
      // when the wrapper opts in via ``applyAnchorRadialLayout``
      // (currently FoundationCanvas only), the three radial kinds
      // (mission / core_value / identity) snap to the anchor-radial
      // slot per the canonical Plot spec
      // ("프로젝트 노드 놓고 그 주변에 미션, 코어밸류, 아이덴티티
      //  붙이면 되요"). The drop x/y still bubbles up from the
      // drag-and-drop or context-menu handler; we override it only
      // when the wrapper flag + kind combination matches. Users can
      // drag the node anywhere afterward (positional hint, not constraint).
      const useRadial =
        applyAnchorRadialLayout && isFoundationRadialKind(kind);
      const { x: nx, y: ny } = useRadial
        ? anchorRadialPosition(
            kind,
            countFoundationKinds(current.nodes),
            width,
            height,
          )
        : { x, y };
      const node: DocNode = createBlankNode(
        kind,
        {
          id: freshId("n"),
          label: preset?.label ?? "",
          x: nx,
          y: ny,
          width,
          height,
          color: preset?.color ?? DEFAULT_COLOR,
          shape: preset?.shape ?? "rounded",
          icon: preset?.icon ?? null,
        },
        {
          ref_actor_id: preset?.ref_actor_id ?? null,
          ref_mission_id: preset?.ref_mission_id ?? null,
          ref_value_id: preset?.ref_value_id ?? null,
          ref_identity_id: preset?.ref_identity_id ?? null,
        },
      );
      onDocChange({ ...current, nodes: [...current.nodes, node] });
    },
    [docRef, onDocChange, applyAnchorRadialLayout],
  );

  const addNestedNodeAt = useCallback(
    (args: {
      parentId: string;
      localX: number;
      localY: number;
      preset: NodePreset;
    }) => {
      const { preset } = args;
      const kind = requirePresetKind(preset);
      const node: DocNode = createBlankNode(
        kind,
        {
          id: freshId("n"),
          label: preset.label ?? "",
          x: args.localX,
          y: args.localY,
          width: preset.width ?? DEFAULT_WIDTH,
          height: preset.height ?? DEFAULT_HEIGHT,
          color: preset.color ?? DEFAULT_COLOR,
          shape: preset.shape ?? "rounded",
          icon: preset.icon ?? null,
        },
        {
          ref_actor_id: preset?.ref_actor_id ?? null,
          ref_mission_id: preset?.ref_mission_id ?? null,
          ref_value_id: preset?.ref_value_id ?? null,
          ref_identity_id: preset?.ref_identity_id ?? null,
        },
      );
      // v0.26.0 (D-2026-05-25-A) — every nested-drop materialises a
      // directed edge from parent → child. This replaces the v0.25
      // ``parent_id`` field semantics for *all* kinds (not just
      // actor / service); rule / content / metric / step children
      // now also carry an explicit directed edge as the structural
      // signal.
      const current = docRef.current;
      const newEdges = [
        ...current.edges,
        {
          id: freshId("e"),
          source: args.parentId,
          target: node.id,
          sourceHandle: null,
          targetHandle: null,
          label: "decomposes",
          style: "dashed" as const,
          directed: true,
          relation: classifyEdge(
            current.canvas_kind,
            current.nodes.find((n) => n.id === args.parentId)?.kind,
          ),
          action_verb: "decomposes",
          value_form: [],
        },
      ];
      onDocChange({
        ...current,
        nodes: [...current.nodes, node],
        edges: newEdges,
      });
    },
    [docRef, onDocChange],
  );

  const addCompositionChild = useCallback(
    (parentId: string, kind: "rule" | "content") => {
      const defaults =
        kind === "rule"
          ? { shape: "rectangle" as const, color: "#e7e5e4", icon: "shield" }
          : { shape: "hexagon" as const, color: "#ddd6fe", icon: "package" };
      const node: DocNode = createBlankNode(kind, {
        id: freshId("n"),
        label: kind === "rule" ? "New rule" : "New content",
        x: 0,
        y: 0,
        width: 140,
        height: 60,
        color: defaults.color,
        shape: defaults.shape,
        icon: defaults.icon,
      });
      // v0.26.0 (D-2026-05-25-A) — composition child carries an
      // explicit directed edge from the parent service.
      const current = docRef.current;
      const newEdge = {
        id: freshId("e"),
        source: parentId,
        target: node.id,
        sourceHandle: null,
        targetHandle: null,
        label: "",
        style: "solid" as const,
        directed: true,
        relation: classifyEdge(
          current.canvas_kind,
          current.nodes.find((n) => n.id === parentId)?.kind,
        ),
        action_verb: null,
        value_form: [],
      };
      onDocChange({
        ...current,
        nodes: [...current.nodes, node],
        edges: [...current.edges, newEdge],
      });
    },
    [docRef, onDocChange],
  );

  return { addNodeAt, addNestedNodeAt, addCompositionChild };
}
