import { useCallback, useMemo, useState } from "react";
import { patchProjectAnchor } from "./app/project";
import { resolveWorkspaceRoot } from "./app/workspace";
import { ProjectPicker } from "./shell/ProjectPicker";
import { applyOptimisticAnchorPatch } from "./lib/anchorOptimistic";
import { ActorsCanvas } from "./canvases/ActorsCanvas";
import { EntitiesCanvas } from "./canvases/EntitiesCanvas";
import { FoundationCanvas } from "./canvases/FoundationCanvas";
import { FeatureDetailCanvas } from "./canvases/FeatureDetailCanvas";
import { FeatureDetailInspectorHost } from "./canvases/inspectors/FeatureDetailInspectorHost";
import { ServicesCanvas } from "./canvases/ServicesCanvas";
import { SketchSidebar } from "./canvases/SketchSidebar";
import { StencilDragProvider } from "./canvases/sketch/StencilDragContext";
import { useProjectHistory } from "./canvases/useProjectHistory";
import { useAppKeyboard } from "./hooks/useAppKeyboard";
import { useAvailableNodes } from "./hooks/useAvailableNodes";
import { useCanvasPersist } from "./hooks/useCanvasPersist";
import { useDirPicker } from "./hooks/useDirPicker";
import { useSnapshotView } from "./hooks/useSnapshotView";
import { useProject } from "./hooks/useProject";
import { useProjectSocket } from "./hooks/useProjectSocket";
import { useStableHandlers } from "./hooks/useStableHandlers";
import { useUrlSync } from "./hooks/useUrlSync";
import { CanvasTabs, type CanvasTab } from "./shell/CanvasTabs";
import { ChatDock } from "./shell/ChatDock";
import { WorkspacePanels } from "./shell/WorkspacePanels";
import { Header } from "./shell/Header";
import { HelpCheatsheet } from "./shell/HelpCheatsheet";
import { EmptyState, ErrorPanel, Loading } from "./shell/states";
import type {
  AnchorPlacement,
  CanvasDoc,
  CanvasKey,
  CanvasKind,
  ProjectDoc,
} from "./types";

function tabToKind(tab: CanvasTab): Exclude<CanvasKind, "feature"> {
  if (tab === "foundation") return "foundation";
  if (tab === "actors") return "actors";
  if (tab === "entities") return "entities";
  return "services";
}

/**
 * v0.13 Phase 0: pull the per-canvas project anchor placement out of a
 * ProjectDoc summary, falling back to defaults when the field is missing
 * (older v0.12 projects pre-eviction-migration). The synthetic anchor is
 * only injected on Foundation/Actors/Services tabs.
 */
function resolveProjectAnchor(
  proj: ProjectDoc | undefined,
  tab: CanvasTab,
): AnchorPlacement | null {
  if (!proj) return null;
  const fromDoc = proj.anchors?.[tab];
  if (fromDoc) return fromDoc;
  return {
    x: -75,
    y: -75,
    width: 150,
    height: 150,
    color: "#fef3c7",
    shape: "circle",
  };
}


export function App() {
  const workspaceRoot = useMemo(resolveWorkspaceRoot, []);
  const history = useProjectHistory();
  const [error, setError] = useState<string | null>(null);

  // ------- URL ⟷ canvas tab / drill / selection (extracted to useUrlSync) -------

  const {
    activeTab,
    detailFeatureId,
    detailActive,
    selectedNodeId,
    syncUrl,
    selectTab,
    drillIntoFeature,
    activateDetail,
    closeDetail,
    jumpToActor,
    consumeSelection,
    focusCanvas,
  } = useUrlSync();

  // ------- project state (extracted to useProject) -------

  const initialActiveId = useMemo(() => {
    const url = new URL(window.location.href);
    return url.searchParams.get("project") ?? url.searchParams.get("sketch");
  }, []);

  // v0.16.16 (D-2026-05-12-R) — stable callbacks prevent cascading
  // identity changes that previously caused a WS-driven refetch storm.
  const handleError = useCallback((err: string) => setError(err), []);
  const handleActiveIdChange = useCallback(
    (id: string | null) => syncUrl({ project: id, sketch: null }),
    [syncUrl],
  );

  const project = useProject({
    workspaceRoot,
    history,
    initialActiveId,
    onActiveIdChange: handleActiveIdChange,
    onError: handleError,
  });
  const {
    summaries, activeId, activeProjectPath, dirForId,
    canvasCache: liveCanvasCache, tags, migratedToast, phase,
    setCanvasCache, setFeatureDetails, setTags, loadList,
    create: handleCreate, rename: handleRename, remove: handleDelete,
    pick: handlePick,
    publishBlueprint: handlePublishBlueprint,
    publishNodeAction: handlePublishNode,
    unpublishNodeAction: handleUnpublishNode,
    deleteTag: handleDeleteTag, dismissToast,
  } = project;

  const { handleListStale, handleExternalCanvas, handleTagsRefresh, handleExternalChange } =
    useStableHandlers({ setCanvasCache, setTags, loadList, historyClear: history.clear });
  const dirPicker = useDirPicker({ workspaceRoot, onCreateInDir: handleCreate });

  // v0.16.19 (D-2026-05-12-U) — anchor change handler stable across
  // non-state-changing renders so useNodesMemo's data.onResize for the
  // synthetic anchor node keeps a stable ref.
  const handleAnchorChange = useCallback(
    (patch: Partial<AnchorPlacement>) => {
      if (!activeProjectPath || !activeId) return;
      const previous = summaries.find((p) => p.id === activeId);
      if (previous) {
        project.replaceSummary(
          applyOptimisticAnchorPatch(previous, activeTab, patch),
        );
      }
      void patchProjectAnchor(activeProjectPath, activeId, activeTab, patch).then(
        (refreshed) => project.replaceSummary(refreshed),
        (err) => {
          if (previous) project.replaceSummary(previous);
          setError(err instanceof Error ? err.message : String(err));
        },
      );
    },
    [activeProjectPath, activeId, activeTab, summaries, project],
  );

  // ------- persist + undo/redo (extracted to useCanvasPersist) -------

  const {
    echoGuard,
    applyEdit: liveApplyEdit,
    saveState,
    undo: historyUndo,
    redo: historyRedo,
  } = useCanvasPersist({
    projectPath: activeProjectPath,
    activeId,
    history,
    setCanvasCache,
    setFeatureDetails,
    onListStale: handleListStale,
    onError: handleError,
  });

  // v0.24.14 (D-2026-05-21-C) — snapshot view: when ``viewingTag`` is set,
  // the app renders the canvas state at that git tag. Edits are gated at
  // the App boundary so save / publish flows never operate on tag data.
  const { viewingTag, snapshotCache, enterTagView, exitTagView } =
    useSnapshotView(activeProjectPath, activeId, handleError);
  const canvasCache = viewingTag ? snapshotCache : liveCanvasCache;
  const applyEdit: typeof liveApplyEdit = viewingTag
    ? (() => {}) as typeof liveApplyEdit
    : liveApplyEdit;

  // ------- WebSocket (extracted to useProjectSocket) -------

  const socketStatus = useProjectSocket({
    projectPath: activeProjectPath,
    activeId,
    echoGuard,
    onListStale: handleListStale,
    onExternalCanvas: handleExternalCanvas,
    onTagsRefresh: handleTagsRefresh,
    onExternalChange: handleExternalChange,
    onError: handleError,
  });

  const handleUndo = useCallback(() => {
    const key = historyUndo();
    if (key) focusCanvas(key);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [historyUndo]);

  const handleRedo = useCallback(() => {
    const key = historyRedo();
    if (key) focusCanvas(key);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [historyRedo]);

  const [helpOpen, setHelpOpen] = useState(false);
  const [canvasSelectionIds, setCanvasSelectionIds] = useState<string[]>([]); // chat ctx (D-2026-06-15-A)

  useAppKeyboard({
    onUndo: handleUndo,
    onRedo: handleRedo,
    helpOpen,
    setHelpOpen,
  });

  // ------- current canvas selection -------

  // v0.12 — services-tab + detailFeatureId no longer swaps the main
  // canvas. The services canvas stays mounted; service detail opens
  // in a modal overlay instead. activeCanvasKey reflects only the
  // top-level tab choice.
  const activeCanvasKey: CanvasKey = useMemo(() => {
    const kind = tabToKind(activeTab);
    return kind as CanvasKey;
  }, [activeTab]);

  const activeCanvas = canvasCache.get(activeCanvasKey) ?? null;

  // v0.12 — service detail. Separate cache lookup so the detail canvas and the
  // underlying services canvas can both stay loaded. v0.78 (D-2026-06-15-H) —
  // rendered inline as a dynamic tab instead of a modal overlay.
  const detailCanvasKey: CanvasKey | null = useMemo(() => {
    if (!detailFeatureId) return null;
    return `feature:${detailFeatureId}` as CanvasKey;
  }, [detailFeatureId]);
  const detailCanvas = detailCanvasKey ? canvasCache.get(detailCanvasKey) ?? null : null;
  // Label for the {FeatureDetail} tab = the service node's label on the
  // Services canvas (falls back to the id).
  const detailLabel = useMemo(() => {
    if (!detailFeatureId) return null;
    const svc = (canvasCache.get("services")?.nodes ?? []).find((n) => n.id === detailFeatureId);
    return svc?.label ?? detailFeatureId;
  }, [canvasCache, detailFeatureId]);

  // D-2026-06-15-O — FeatureDetail's default right panel = the subject
  // service's read-only inspector (cross-doc; read from the Services canvas).
  // Memoised so the FeatureDetailCanvas prop identity stays stable across
  // App re-renders (the canvas is React.memo'd — an inline node would defeat
  // it and remount on every drag, see D-2026-05-27-C).
  const detailFallbackInspector = useMemo(
    () =>
      detailFeatureId ? (
        <FeatureDetailInspectorHost
          serviceId={detailFeatureId}
          servicesCanvas={canvasCache.get("services") ?? null}
          projectPath={activeProjectPath ?? ""}
          projectId={activeId ?? ""}
        />
      ) : null,
    [detailFeatureId, canvasCache, activeProjectPath, activeId],
  );

  // v0.10 Step 3 / v0.16.5 — cross-canvas "available master" lists for
  // pickers + orphan detection. Foundation canvas feeds the three
  // foundation-kind pickers; Actors canvas feeds the ActorRefPicker
  // + orphan check.
  const { availableActors, availableMissions, availableValues, availableIdentities } =
    useAvailableNodes(canvasCache);

  // v0.27.7 (D-2026-05-27-C) — inline arrow callbacks on the Canvas /
  // FeatureDetailCanvas elements were re-created on every App render,
  // including the 60fps drag loop. That made `<Canvas onDocChange={…}>`
  // a new prop every frame, causing React to treat SketchCanvas's
  // `<ReactFlowProvider>` subtree as a different element and remount it
  // — which reset `useNodesInitialized` and left every node stuck on
  // `visibility: hidden`. Hoist callbacks into `useCallback` so the
  // identity only changes when their actual dependencies change.

  const onMainDocChange = useCallback(
    (next: CanvasDoc) => {
      if (!activeCanvas) return;
      applyEdit(activeCanvasKey, activeCanvas, next);
    },
    [applyEdit, activeCanvasKey, activeCanvas],
  );

  const onMainPublishNode = useCallback(
    (id: string) => {
      void handlePublishNode(activeCanvasKey, id);
    },
    [handlePublishNode, activeCanvasKey],
  );

  const onMainUnpublishNode = useCallback(
    (id: string) => {
      void handleUnpublishNode(activeCanvasKey, id);
    },
    [handleUnpublishNode, activeCanvasKey],
  );

  const onMainNodeDrill = useCallback(
    (id: string) => {
      if (!activeCanvas) return;
      const n = activeCanvas.nodes.find((x) => x.id === id);
      if (!n) return;
      if (n.kind === "actor_ref" && n.ref_actor_id) {
        jumpToActor(n.ref_actor_id);
        return;
      }
      // D-2026-06-17-D — the feature is the drill target; a service shows its
      // inspector (no drill). drillIntoFeature still names the wire string
      // ``feature``; the id it carries is now a feature id.
      if (activeTab === "services" && n.kind === "feature") {
        drillIntoFeature(id);
      }
    },
    [activeCanvas, activeTab, jumpToActor, drillIntoFeature],
  );

  const onModalDocChange = useCallback(
    (next: CanvasDoc) => {
      if (!detailCanvasKey || !detailCanvas) return;
      applyEdit(detailCanvasKey, detailCanvas, next);
    },
    [applyEdit, detailCanvasKey, detailCanvas],
  );

  const onModalSelectionConsumed = useCallback(() => {}, []);

  const onModalNodeDrill = useCallback(
    (id: string) => {
      if (!detailCanvas) return;
      const n = detailCanvas.nodes.find((x) => x.id === id);
      if (n?.kind === "actor_ref" && n.ref_actor_id) jumpToActor(n.ref_actor_id);
    },
    [detailCanvas, jumpToActor],
  );

  const onModalPublishNode = useCallback(
    (id: string) => {
      if (detailCanvasKey) void handlePublishNode(detailCanvasKey, id);
    },
    [handlePublishNode, detailCanvasKey],
  );

  const onModalUnpublishNode = useCallback(
    (id: string) => {
      if (detailCanvasKey) void handleUnpublishNode(detailCanvasKey, id);
    },
    [handleUnpublishNode, detailCanvasKey],
  );

  // v0.27.18 (D-2026-05-28-L) — projectAnchor was computed inline on every
  // App render via ``resolveProjectAnchor(summaries.find(...), activeTab)``,
  // producing a fresh object reference every time. That defeated React.memo
  // on SketchCanvas and made the Services canvas's ReactFlow store fire
  // a full prop-cascade update on every modal action, even though the
  // Services canvas's underlying data was unchanged. Memoise both
  // projectAnchor and the project summary lookup so children get a stable
  // ref while the modal is open.
  const activeSummary = useMemo(
    () => summaries.find((p) => p.id === activeId) ?? null,
    [summaries, activeId],
  );
  const activeProjectAnchor = useMemo(
    () => resolveProjectAnchor(activeSummary ?? undefined, activeTab),
    [activeSummary, activeTab],
  );
  const activeProjectName = activeSummary?.name ?? null;

  if (!workspaceRoot) {
    return <ProjectPicker />;
  }

  // v0.78 (D-2026-06-15-H) — the feature canvas renders inline as a
  // dynamic tab, so it's "ready" when its tab is the active view and its doc
  // is loaded. (No more modal / inert backdrop.)
  const detailReady = detailActive && !!detailCanvas && !!detailCanvasKey;

  return (
    <StencilDragProvider>
    <div className="flex h-screen min-h-screen flex-col">
      <Header
        error={error}
        socketStatus={socketStatus}
        saveState={saveState}
        workspaceRoot={workspaceRoot}
        viewingTag={viewingTag}
        onExitTagView={exitTagView}
        onDismissToast={dismissToast}
        migratedToast={migratedToast}
      />
      {helpOpen && <HelpCheatsheet onClose={() => setHelpOpen(false)} />}
      <WorkspacePanels
        chat={<ChatDock onError={handleError} workspaceRoot={activeProjectPath ?? undefined} activeScope={detailActive ? (detailFeatureId ? `feature:${detailFeatureId}` : "services") : tabToKind(activeTab)} activeScopeLabel={detailActive ? detailLabel : undefined} selection={((detailActive ? detailCanvas : activeCanvas)?.nodes ?? []).filter((n) => canvasSelectionIds.includes(n.id)).map((n) => ({ id: n.id, kind: n.kind, label: n.label ?? "" }))} />}
        sidebar={
        <SketchSidebar
          projects={summaries}
          activeId={activeId}
          dirForId={dirForId}
          stencilCanvas={detailActive ? "feature" : activeTab}
          availableActors={availableActors}
          tags={tags}
          onPick={handlePick}
          onCreate={dirPicker.open}
          onRename={handleRename}
          onDelete={handleDelete}
          onDeleteTag={handleDeleteTag}
          onViewTag={enterTagView}
          viewingTag={viewingTag}
        />
        }
        canvas={
        <main className="flex h-full flex-col overflow-hidden">
          {phase === "ready" && (
            <CanvasTabs
              active={activeTab}
              onSelect={selectTab}
              projectName={activeProjectName}
              blueprintVersion={summaries.find((p) => p.id === activeId)?.blueprint_version ?? "v0.1.0"}
              onPublishBlueprint={handlePublishBlueprint}
              publishDisabled={!activeId}
              detailFeatureId={detailFeatureId}
              detailLabel={detailLabel}
              detailActive={detailActive}
              onSelectDetail={activateDetail}
              onCloseDetail={closeDetail}
            />
          )}
          <div className="relative flex-1 overflow-hidden">
            {phase === "loading" && <Loading />}
            {phase === "error" && <ErrorPanel message={error ?? "unknown"} />}
            {phase === "no-projects" && <EmptyState onCreate={dirPicker.open} />}
            {phase === "ready" && activeId && detailReady && (
              // v0.78 (D-2026-06-15-H) — the feature canvas renders
              // inline when its dynamic tab is active (was a modal overlay).
              <FeatureDetailCanvas
                key={`${activeId}:${detailCanvasKey}`}
                doc={detailCanvas!}
                onDocChange={onModalDocChange}
                onUndo={handleUndo}
                onRedo={handleRedo}
                canUndo={history.canUndo}
                canRedo={history.canRedo}
                projectPath={activeProjectPath ?? ""}
                projectId={activeId}
                availableActors={availableActors}
                availableMissions={availableMissions}
                availableValues={availableValues}
                availableIdentities={availableIdentities}
                selectNodeId={null}
                onSelectionConsumed={onModalSelectionConsumed}
                onSelectionChange={setCanvasSelectionIds}
                onNodeDrill={onModalNodeDrill}
                onPublishNode={onModalPublishNode}
                onUnpublishNode={onModalUnpublishNode}
                fallbackInspector={detailFallbackInspector}
              />
            )}
            {phase === "ready" && activeCanvas && activeId && !detailReady && (() => {
              // v0.15 Phase 3.3 — every F/A/S/E tab routes through its named
              // wrapper. SketchCanvas is no longer called directly from App.
              const Canvas =
                activeTab === "foundation"
                  ? FoundationCanvas
                  : activeTab === "actors"
                    ? ActorsCanvas
                    : activeTab === "entities"
                      ? EntitiesCanvas
                      : ServicesCanvas;
              return (
              <Canvas
                key={`${activeId}:${activeCanvasKey}`}
                doc={activeCanvas}
                onDocChange={onMainDocChange}
                onUndo={handleUndo}
                onRedo={handleRedo}
                canUndo={history.canUndo}
                canRedo={history.canRedo}
                projectPath={activeProjectPath ?? ""}
                projectId={activeId}
                availableActors={availableActors}
                availableMissions={availableMissions}
                availableValues={availableValues}
                availableIdentities={availableIdentities}
                selectNodeId={selectedNodeId}
                onSelectionConsumed={consumeSelection} onSelectionChange={setCanvasSelectionIds}
                projectAnchor={activeProjectAnchor}
                projectName={activeProjectName}
                onAnchorChange={handleAnchorChange}
                onPublishNode={onMainPublishNode}
                onUnpublishNode={onMainUnpublishNode}
                onNodeDrill={onMainNodeDrill}
              />
              );
            })()}
          </div>
        </main>
        }
      />
    </div>
    {dirPicker.modal}
    </StencilDragProvider>
  );
}



