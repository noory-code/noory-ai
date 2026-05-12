/**
 * URL ⟷ tab/drill/selection state — single source of truth for the
 * three browser-URL query params Plot keeps in sync:
 *
 *   ``?canvas=foundation|actors|services``   ← activeTab
 *   ``?detail=<serviceId>``                 ← detailServiceId
 *   ``?select=<nodeId>``                    ← selectedNodeId
 *
 * Extracted from ``App.tsx`` (v0.16.4) so the App component no
 * longer owns URL plumbing for the canvas tabs. Companion hooks
 * (``useCanvasPersist``, ``useProject``, ``useProjectSocket``) still
 * own their own concerns; this one wraps the navigation surface.
 */
import { useCallback, useState } from "react";
import { CANVAS_TAB_IDS, type CanvasTab } from "../shell/CanvasTabs";
import type { CanvasKey } from "../types";

export interface UrlSync {
  activeTab: CanvasTab;
  detailServiceId: string | null;
  selectedNodeId: string | null;
  /** Generic URL writer — also used by App.tsx to sync the
   *  ``?project=<id>`` param when ``useProject`` changes activeId. */
  syncUrl: (updates: Record<string, string | null | undefined>) => void;
  selectTab: (tab: CanvasTab) => void;
  drillIntoService: (serviceId: string) => void;
  backToOverview: () => void;
  jumpToActor: (actorId: string) => void;
  consumeSelection: () => void;
  focusCanvas: (key: CanvasKey) => void;
}

function readInitialTab(): CanvasTab {
  const raw = new URL(window.location.href).searchParams.get("canvas");
  return (CANVAS_TAB_IDS as readonly string[]).includes(raw ?? "")
    ? (raw as CanvasTab)
    : "services";
}

function readInitial(param: string): string | null {
  return new URL(window.location.href).searchParams.get(param);
}

export function useUrlSync(): UrlSync {
  const [activeTab, setActiveTab] = useState<CanvasTab>(readInitialTab);
  const [detailServiceId, setDetailServiceId] = useState<string | null>(() =>
    readInitial("detail"),
  );
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(() =>
    readInitial("select"),
  );

  const syncUrl = useCallback(
    (updates: Record<string, string | null | undefined>) => {
      const url = new URL(window.location.href);
      for (const [k, v] of Object.entries(updates)) {
        if (v == null || v === "") url.searchParams.delete(k);
        else url.searchParams.set(k, v);
      }
      window.history.replaceState(null, "", url.toString());
    },
    [],
  );

  const selectTab = useCallback(
    (tab: CanvasTab) => {
      setActiveTab(tab);
      setDetailServiceId(null);
      syncUrl({ canvas: tab, detail: null, select: null });
    },
    [syncUrl],
  );

  const drillIntoService = useCallback(
    (serviceId: string) => {
      setActiveTab("services");
      setDetailServiceId(serviceId);
      syncUrl({ canvas: "services", detail: serviceId });
    },
    [syncUrl],
  );

  const backToOverview = useCallback(() => {
    setDetailServiceId(null);
    syncUrl({ detail: null });
  }, [syncUrl]);

  const jumpToActor = useCallback(
    (actorId: string) => {
      setActiveTab("actors");
      setDetailServiceId(null);
      setSelectedNodeId(actorId);
      syncUrl({ canvas: "actors", detail: null, select: actorId });
    },
    [syncUrl],
  );

  const consumeSelection = useCallback(() => {
    setSelectedNodeId(null);
    syncUrl({ select: null });
  }, [syncUrl]);

  const focusCanvas = useCallback(
    (key: CanvasKey) => {
      if (key === "foundation") {
        setActiveTab("foundation");
        setDetailServiceId(null);
        syncUrl({ canvas: "foundation", detail: null });
      } else if (key === "actors") {
        setActiveTab("actors");
        setDetailServiceId(null);
        syncUrl({ canvas: "actors", detail: null });
      } else if (key === "services") {
        setActiveTab("services");
        setDetailServiceId(null);
        syncUrl({ canvas: "services", detail: null });
      } else {
        const sid = key.slice("service_detail:".length);
        setActiveTab("services");
        setDetailServiceId(sid);
        syncUrl({ canvas: "services", detail: sid });
      }
    },
    [syncUrl],
  );

  return {
    activeTab,
    detailServiceId,
    selectedNodeId,
    syncUrl,
    selectTab,
    drillIntoService,
    backToOverview,
    jumpToActor,
    consumeSelection,
    focusCanvas,
  };
}
