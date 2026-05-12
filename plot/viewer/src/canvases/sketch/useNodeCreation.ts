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
import type { CanvasDoc, NodeKind, SketchNode as DocNode } from "../../types";
import { DEFAULT_COLOR, DEFAULT_HEIGHT, DEFAULT_WIDTH } from "./constants";
import type { NodePreset } from "./types";

export interface UseNodeCreationArgs {
  docRef: MutableRefObject<CanvasDoc>;
  onDocChange: (next: CanvasDoc) => void;
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
}: UseNodeCreationArgs): UseNodeCreationResult {
  const addNodeAt = useCallback(
    (x: number, y: number, preset?: NodePreset) => {
      const kind = requirePresetKind(preset);
      const node: DocNode = createBlankNode(
        kind,
        {
          id: freshId("n"),
          label: preset?.label ?? "",
          x,
          y,
          width: preset?.width ?? DEFAULT_WIDTH,
          height: preset?.height ?? DEFAULT_HEIGHT,
          color: preset?.color ?? DEFAULT_COLOR,
          shape: preset?.shape ?? "rounded",
          icon: preset?.icon ?? null,
          parent_id: null,
        },
        {
          ref_actor_id: preset?.ref_actor_id ?? null,
          ref_mission_id: preset?.ref_mission_id ?? null,
          ref_value_id: preset?.ref_value_id ?? null,
          ref_identity_id: preset?.ref_identity_id ?? null,
        },
      );
      const current = docRef.current;
      onDocChange({ ...current, nodes: [...current.nodes, node] });
    },
    [docRef, onDocChange],
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
          parent_id: args.parentId,
        },
        {
          ref_actor_id: preset?.ref_actor_id ?? null,
          ref_mission_id: preset?.ref_mission_id ?? null,
          ref_value_id: preset?.ref_value_id ?? null,
          ref_identity_id: preset?.ref_identity_id ?? null,
        },
      );
      const current = docRef.current;
      // Rule / content are composition: edited via the Inspector, no edge.
      // Actor / service are hierarchy: materialise a real decomposition
      // edge so users can edit it (label, verb, value_form).
      const makeHierarchyEdge = preset.kind === "actor" || preset.kind === "service";
      const newEdges = makeHierarchyEdge
        ? [
            ...current.edges,
            {
              id: freshId("e"),
              source: args.parentId,
              target: node.id,
              sourceHandle: null,
              targetHandle: null,
              label: "decomposes",
              style: "dashed" as const,
              action_verb: "decomposes",
              value_form: [],
            },
          ]
        : current.edges;
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
        parent_id: parentId,
      });
      const current = docRef.current;
      onDocChange({ ...current, nodes: [...current.nodes, node] });
    },
    [docRef, onDocChange],
  );

  return { addNodeAt, addNestedNodeAt, addCompositionChild };
}
