import { useCallback, useRef } from "react";
import type { CanvasDoc, SketchEdge, SketchNode } from "../types";

interface Clip {
  nodes: SketchNode[];
  edges: SketchEdge[];
}

function randomId(prefix: string): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

export interface SketchClipboard {
  copy: (doc: CanvasDoc, selectedNodeIds: string[]) => void;
  paste: (doc: CanvasDoc, offset?: { x: number; y: number }) => CanvasDoc;
  duplicate: (
    doc: CanvasDoc,
    selectedNodeIds: string[],
    offset?: { x: number; y: number },
  ) => CanvasDoc;
  hasClip: () => boolean;
}

/**
 * In-memory clipboard for nodes + their incident edges (both endpoints
 * must be in the selection). Paste creates fresh ids and offsets positions.
 */
export function useSketchClipboard(): SketchClipboard {
  const clipRef = useRef<Clip | null>(null);

  const copy = useCallback((doc: CanvasDoc, selectedNodeIds: string[]) => {
    const ids = new Set(selectedNodeIds);
    const nodes = doc.nodes.filter((n) => ids.has(n.id));
    const edges = doc.edges.filter((e) => ids.has(e.source) && ids.has(e.target));
    clipRef.current = { nodes, edges };
  }, []);

  const buildPaste = useCallback(
    (
      doc: CanvasDoc,
      clip: Clip,
      offset: { x: number; y: number },
    ): CanvasDoc => {
      const idMap: Record<string, string> = {};
      const newNodes: SketchNode[] = clip.nodes.map((n) => {
        const newId = randomId("n");
        idMap[n.id] = newId;
        return { ...n, id: newId, x: n.x + offset.x, y: n.y + offset.y };
      });
      const newEdges: SketchEdge[] = clip.edges.map((e) => ({
        ...e,
        id: randomId("e"),
        source: idMap[e.source],
        target: idMap[e.target],
      }));
      return {
        ...doc,
        nodes: [...doc.nodes, ...newNodes],
        edges: [...doc.edges, ...newEdges],
      };
    },
    [],
  );

  const paste = useCallback(
    (doc: CanvasDoc, offset = { x: 40, y: 40 }): CanvasDoc => {
      if (!clipRef.current || clipRef.current.nodes.length === 0) return doc;
      return buildPaste(doc, clipRef.current, offset);
    },
    [buildPaste],
  );

  const duplicate = useCallback(
    (
      doc: CanvasDoc,
      selectedNodeIds: string[],
      offset = { x: 40, y: 40 },
    ): CanvasDoc => {
      const ids = new Set(selectedNodeIds);
      const clip: Clip = {
        nodes: doc.nodes.filter((n) => ids.has(n.id)),
        edges: doc.edges.filter((e) => ids.has(e.source) && ids.has(e.target)),
      };
      if (clip.nodes.length === 0) return doc;
      return buildPaste(doc, clip, offset);
    },
    [buildPaste],
  );

  const hasClip = useCallback(
    () => clipRef.current !== null && clipRef.current.nodes.length > 0,
    [],
  );

  return { copy, paste, duplicate, hasClip };
}
