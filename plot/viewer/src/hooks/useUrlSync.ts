/**
 * URL ⟷ tab/drill/selection state — single source of truth for the
 * three browser-URL query params Plot keeps in sync:
 *
 *   ``?canvas=foundation|actors|services``   ← activeTab
 *   ``?detail=<serviceId>``                 ← detailFeatureId
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
  detailFeatureId: string | null;
  /** Whether the feature tab is the active view (D-2026-06-15-H). The
   *  ``{FeatureDetail}`` tab exists whenever ``detailFeatureId`` is set; this
   *  flag says it's the one currently showing (vs an F/A/S tab). */
  detailActive: boolean;
  selectedNodeId: string | null;
  /** Generic URL writer — also used by App.tsx to sync the
   *  ``?project=<id>`` param when ``useProject`` changes activeId. */
  syncUrl: (updates: Record<string, string | null | undefined>) => void;
  selectTab: (tab: CanvasTab) => void;
  drillIntoFeature: (serviceId: string) => void;
  /** Re-activate the existing feature tab (click its tab). */
  activateDetail: () => void;
  /** Remove the feature tab entirely (its × button). */
  closeDetail: () => void;
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
  const [detailFeatureId, setDetailFeatureId] = useState<string | null>(() =>
    readInitial("detail"),
  );
  // On load, a present ``?detail`` means the detail tab opens active (matches
  // the pre-v0.78 modal-auto-open behaviour).
  const [detailActive, setDetailActive] = useState<boolean>(
    () => readInitial("detail") !== null,
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
      // Switching to an F/A/S tab deactivates the detail view but KEEPS the
      // ``{FeatureDetail}`` tab around (D-2026-06-15-H) — it's closed only via
      // its × button. ``detail`` URL param is left intact so the tab persists.
      setActiveTab(tab);
      setDetailActive(false);
      syncUrl({ canvas: tab, select: null });
    },
    [syncUrl],
  );

  const drillIntoFeature = useCallback(
    (serviceId: string) => {
      // Selecting a service node adds the detail tab and makes it the active
      // view (D-2026-06-15-H — was a modal pre-v0.78).
      setActiveTab("services");
      setDetailFeatureId(serviceId);
      setDetailActive(true);
      syncUrl({ canvas: "services", detail: serviceId });
    },
    [syncUrl],
  );

  const activateDetail = useCallback(() => {
    setDetailActive(true);
  }, []);

  const closeDetail = useCallback(() => {
    setDetailFeatureId(null);
    setDetailActive(false);
    syncUrl({ detail: null });
  }, [syncUrl]);

  const backToOverview = useCallback(() => {
    setDetailFeatureId(null);
    setDetailActive(false);
    syncUrl({ detail: null });
  }, [syncUrl]);

  const jumpToActor = useCallback(
    (actorId: string) => {
      setActiveTab("actors");
      setDetailFeatureId(null);
      setDetailActive(false); // leaving the detail tab — keep tab state in sync (D-2026-06-15-L)
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
        setDetailFeatureId(null);
        syncUrl({ canvas: "foundation", detail: null });
      } else if (key === "actors") {
        setActiveTab("actors");
        setDetailFeatureId(null);
        syncUrl({ canvas: "actors", detail: null });
      } else if (key === "services") {
        setActiveTab("services");
        setDetailFeatureId(null);
        syncUrl({ canvas: "services", detail: null });
      } else {
        const sid = key.slice("feature:".length);
        setActiveTab("services");
        setDetailFeatureId(sid);
        setDetailActive(true);
        syncUrl({ canvas: "services", detail: sid });
      }
    },
    [syncUrl],
  );

  return {
    activeTab,
    detailFeatureId,
    detailActive,
    selectedNodeId,
    syncUrl,
    selectTab,
    drillIntoFeature,
    activateDetail,
    closeDetail,
    backToOverview,
    jumpToActor,
    consumeSelection,
    focusCanvas,
  };
}
