// Node-creation helpers: addNodeAt for top-level nodes,
// addNestedNodeAt for sub-actor / sub-service drops onto an existing
// container. Both build a brand-new DocNode with all typed fields
// zeroed; the preset overrides shape/color/kind/etc. but the
// per-kind text fields stay empty until the user fills them in via
// the Inspector.
//
// Note: there's a heavy dose of repeated default-zero initialisation
// shared between the two functions; factoring it out
// (``makeBlankNode()``) is worth doing in a follow-up but kept verbatim
// here to keep the extraction byte-equal to the prior inline.
import { type MutableRefObject, useCallback } from "react";
import type { CanvasDoc, SketchNode as DocNode } from "../../types";
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
}

function freshId(prefix: "n" | "e"): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

export function useNodeCreation({
  docRef,
  onDocChange,
}: UseNodeCreationArgs): UseNodeCreationResult {
  const addNodeAt = useCallback(
    (x: number, y: number, preset?: NodePreset) => {
      const id = freshId("n");
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
    [docRef, onDocChange],
  );

  const addNestedNodeAt = useCallback(
    (args: {
      parentId: string;
      localX: number;
      localY: number;
      preset: NodePreset;
    }) => {
      const id = freshId("n");
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
      const newEdges = makeHierarchyEdge
        ? [
            ...current.edges,
            {
              id: freshId("e"),
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
    [docRef, onDocChange],
  );

  return { addNodeAt, addNestedNodeAt };
}
