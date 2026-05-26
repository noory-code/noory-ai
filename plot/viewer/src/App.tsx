import { useCallback, useMemo, useState } from "react";
import { patchProjectAnchor, resolveProjectPath } from "./api";
import { applyOptimisticAnchorPatch } from "./lib/anchorOptimistic";
import { ActorsCanvas } from "./canvases/ActorsCanvas";
import { FoundationCanvas } from "./canvases/FoundationCanvas";
import { ServiceDetailCanvas } from "./canvases/ServiceDetailCanvas";
import { ServicesCanvas } from "./canvases/ServicesCanvas";
import { SketchSidebar } from "./canvases/SketchSidebar";
import { parentIdOf } from "./canvases/sketch/hierarchy";
import { useProjectHistory } from "./canvases/useProjectHistory";
import { useAppKeyboard } from "./hooks/useAppKeyboard";
import { useAvailableNodes } from "./hooks/useAvailableNodes";
import { useCanvasPersist } from "./hooks/useCanvasPersist";
import { useSnapshotView } from "./hooks/useSnapshotView";
import { useProject } from "./hooks/useProject";
import { useProjectSocket } from "./hooks/useProjectSocket";
import { useStableHandlers } from "./hooks/useStableHandlers";
import { useUrlSync } from "./hooks/useUrlSync";
import { CanvasTabs, type CanvasTab } from "./shell/CanvasTabs";
import { Header } from "./shell/Header";
import { HelpCheatsheet } from "./shell/HelpCheatsheet";
import { ServiceDetailModal } from "./shell/ServiceDetailModal";
import { EmptyState, ErrorPanel, Loading } from "./shell/states";
import type {
  AnchorPlacement,
  CanvasKey,
  CanvasKind,
  ProjectDoc,
} from "./types";

function tabToKind(tab: CanvasTab): CanvasKind {
  if (tab === "foundation") return "foundation";
  if (tab === "actors") return "actors";
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
  const projectPath = useMemo(resolveProjectPath, []);
  const history = useProjectHistory();
  const [error, setError] = useState<string | null>(null);

  // ------- URL ⟷ canvas tab / drill / selection (extracted to useUrlSync) -------

  const {
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
    projectPath,
    history,
    initialActiveId,
    onActiveIdChange: handleActiveIdChange,
    onError: handleError,
  });
  const {
    summaries, activeId, canvasCache: liveCanvasCache, tags, migratedToast, phase,
    setCanvasCache, setServiceDetails, setTags, loadList,
    create: handleCreate, rename: handleRename, remove: handleDelete,
    pick: handlePick,
    publishBlueprint: handlePublishBlueprint,
    publishNodeAction: handlePublishNode,
    unpublishNodeAction: handleUnpublishNode,
    deleteTag: handleDeleteTag, dismissToast,
  } = project;

  const { handleListStale, handleExternalCanvas, handleTagsRefresh, handleExternalChange } =
    useStableHandlers({ setCanvasCache, setTags, loadList, historyClear: history.clear });

  // v0.16.19 (D-2026-05-12-U) — anchor change handler stable across
  // non-state-changing renders so useNodesMemo's data.onResize for the
  // synthetic anchor node keeps a stable ref.
  const handleAnchorChange = useCallback(
    (patch: Partial<AnchorPlacement>) => {
      if (!projectPath || !activeId) return;
      const previous = summaries.find((p) => p.id === activeId);
      if (previous) {
        project.replaceSummary(
          applyOptimisticAnchorPatch(previous, activeTab, patch),
        );
      }
      void patchProjectAnchor(projectPath, activeId, activeTab, patch).then(
        (refreshed) => project.replaceSummary(refreshed),
        (err) => {
          if (previous) project.replaceSummary(previous);
          setError(err instanceof Error ? err.message : String(err));
        },
      );
    },
    [projectPath, activeId, activeTab, summaries, project],
  );

  // ------- persist + undo/redo (extracted to useCanvasPersist) -------

  const {
    pendingWrites,
    applyEdit: liveApplyEdit,
    saveState,
    undo: historyUndo,
    redo: historyRedo,
  } = useCanvasPersist({
    projectPath,
    activeId,
    history,
    setCanvasCache,
    setServiceDetails,
    onListStale: handleListStale,
    onError: handleError,
  });

  // v0.24.14 (D-2026-05-21-C) — snapshot view: when ``viewingTag`` is set,
  // the app renders the canvas state at that git tag. Edits are gated at
  // the App boundary so save / publish flows never operate on tag data.
  const { viewingTag, snapshotCache, enterTagView, exitTagView } =
    useSnapshotView(projectPath, activeId, handleError);
  const canvasCache = viewingTag ? snapshotCache : liveCanvasCache;
  const applyEdit: typeof liveApplyEdit = viewingTag
    ? (() => {}) as typeof liveApplyEdit
    : liveApplyEdit;

  // ------- WebSocket (extracted to useProjectSocket) -------

  const socketStatus = useProjectSocket({
    projectPath,
    activeId,
    pendingWrites,
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

  useAppKeyboard({
    onUndo: handleUndo,
    onRedo: handleRedo,
    helpOpen,
    setHelpOpen,
  });

  // ------- current canvas selection -------

  // v0.12 — services-tab + detailServiceId no longer swaps the main
  // canvas. The services canvas stays mounted; service detail opens
  // in a modal overlay instead. activeCanvasKey reflects only the
  // top-level tab choice.
  const activeCanvasKey: CanvasKey = useMemo(() => {
    const kind = tabToKind(activeTab);
    return kind as CanvasKey;
  }, [activeTab]);

  const activeCanvas = canvasCache.get(activeCanvasKey) ?? null;

  // v0.12 — service detail (modal). Separate cache lookup so the modal
  // and the underlying services canvas can render simultaneously.
  const detailCanvasKey: CanvasKey | null = useMemo(() => {
    if (!detailServiceId) return null;
    return `service_detail:${detailServiceId}` as CanvasKey;
  }, [detailServiceId]);
  const detailCanvas = detailCanvasKey ? canvasCache.get(detailCanvasKey) ?? null : null;

  // v0.10 Step 3 / v0.16.5 — cross-canvas "available master" lists for
  // pickers + orphan detection. Foundation canvas feeds the three
  // foundation-kind pickers; Actors canvas feeds the ActorRefPicker
  // + orphan check.
  const { availableActors, availableMissions, availableValues, availableIdentities } =
    useAvailableNodes(canvasCache);

  // v0.11.6 — download / upload toolbar buttons removed per user
  // feedback. Save is automatic; the toolbar focuses on undo/redo +
  // layout. Reintroducing JSON import/export should go through a
  // dedicated import/export flow if it returns at all.

  if (!projectPath) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-center">
        <div>
          <h1 className="mb-2 text-2xl font-semibold">Plot</h1>
          <p className="text-slate-500">
            Add <code>?project_path=/absolute/path/to/project</code> to the URL.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen min-h-screen flex-col">
      <Header
        projectPath={projectPath}
        error={error}
        socketStatus={socketStatus}
        saveState={saveState}
        projectName={summaries.find((p) => p.id === activeId)?.name ?? null}
        blueprintVersion={summaries.find((p) => p.id === activeId)?.blueprint_version ?? null}
        viewingTag={viewingTag}
        onExitTagView={exitTagView}
        onDismissToast={dismissToast}
        migratedToast={migratedToast}
      />
      {helpOpen && <HelpCheatsheet onClose={() => setHelpOpen(false)} />}
      <div className="flex flex-1 overflow-hidden">
        <SketchSidebar
          projects={summaries}
          activeId={activeId}
          stencilCanvas={
            activeTab === "services" && detailServiceId ? "service_detail" : activeTab
          }
          availableActors={availableActors}
          availableMissions={availableMissions}
          availableValues={availableValues}
          availableIdentities={availableIdentities}
          tags={tags}
          onPick={handlePick}
          onCreate={handleCreate}
          onRename={handleRename}
          onDelete={handleDelete}
          onDeleteTag={handleDeleteTag}
          onViewTag={enterTagView}
          viewingTag={viewingTag}
        />
        <main className="flex flex-1 flex-col overflow-hidden">
          {phase === "ready" && (
            <CanvasTabs
              active={activeTab}
              onSelect={selectTab}
              blueprintVersion={summaries.find((p) => p.id === activeId)?.blueprint_version ?? "v0.1.0"}
              onPublishBlueprint={handlePublishBlueprint}
              publishDisabled={!activeId}
            />
          )}
          <div className="relative flex-1 overflow-hidden">
            {phase === "loading" && <Loading />}
            {phase === "error" && <ErrorPanel message={error ?? "unknown"} />}
            {phase === "no-projects" && <EmptyState onCreate={handleCreate} />}
            {phase === "ready" && activeCanvas && activeId && (() => {
              // v0.15 Phase 3.3 — every tab routes through its named
              // wrapper. SketchCanvas is no longer called directly from
              // App.tsx; the wrappers each delegate to it for now and
              // Phase 3.4 / 3.5 absorbs the canvas-kind-specific
              // behaviour.
              const Canvas =
                activeTab === "foundation"
                  ? FoundationCanvas
                  : activeTab === "actors"
                    ? ActorsCanvas
                    : ServicesCanvas;
              return (
              <Canvas
                key={`${activeId}:${activeCanvasKey}`}
                doc={activeCanvas}
                onDocChange={(next) => {
                  applyEdit(activeCanvasKey, activeCanvas, next);
                }}
                onUndo={handleUndo}
                onRedo={handleRedo}
                canUndo={history.canUndo}
                canRedo={history.canRedo}
                projectPath={projectPath ?? ""}
                projectId={activeId}
                availableActors={availableActors}
                availableMissions={availableMissions}
                availableValues={availableValues}
                availableIdentities={availableIdentities}
                selectNodeId={selectedNodeId}
                onSelectionConsumed={consumeSelection}
                projectAnchor={resolveProjectAnchor(
                  summaries.find((p) => p.id === activeId),
                  activeTab,
                )}
                projectName={
                  summaries.find((p) => p.id === activeId)?.name ?? null
                }
                onAnchorChange={handleAnchorChange}
                onPublishNode={(id) => {
                  void handlePublishNode(activeCanvasKey, id);
                }}
                onUnpublishNode={(id) => {
                  void handleUnpublishNode(activeCanvasKey, id);
                }}
                onNodeDrill={(id) => {
                  const n = activeCanvas.nodes.find((x) => x.id === id);
                  if (!n) return;
                  if (n.kind === "actor_ref" && n.ref_actor_id) {
                    jumpToActor(n.ref_actor_id);
                    return;
                  }
                  // v0.12 — service double-click opens the detail in a
                  // modal overlay. The services canvas stays mounted
                  // beneath the modal.
                  if (
                    activeTab === "services" &&
                    n.kind === "service" &&
                    !n.is_root
                  ) {
                    drillIntoService(id);
                  }
                }}
              />
              );
            })()}
            {/* v0.12 — Service detail modal overlays the canvas. v0.26.4 (D-2026-05-26-B) — mounted inside the canvas container so the sidebar stays usable. */}
            {phase === "ready" && detailServiceId && detailCanvas && detailCanvasKey && activeId && (() => {
              const servicesCanvas = canvasCache.get("services");
              const servicesNodes = servicesCanvas?.nodes ?? [];
              const servicesEdges = servicesCanvas?.edges ?? [];
              const svcNode = servicesNodes.find((n) => n.id === detailServiceId);
              // v0.12.6 — surface the parent category so the modal header
              // carries drill context. v0.26.0 (D-2026-05-25-A): parent is
              // now the source of the first incoming directed edge.
              const categoryId = svcNode ? parentIdOf(servicesEdges, svcNode.id) : null;
              const categoryNode = categoryId
                ? servicesNodes.find((n) => n.id === categoryId)
                : undefined;
              return (
              <ServiceDetailModal
                serviceLabel={svcNode?.label ?? detailServiceId}
                categoryLabel={categoryNode?.label ?? null}
                onClose={backToOverview}
              >
                <ServiceDetailCanvas
                  key={`${activeId}:${detailCanvasKey}`}
                  doc={detailCanvas}
                  onDocChange={(next) => {
                    applyEdit(detailCanvasKey, detailCanvas, next);
                  }}
                  onUndo={handleUndo}
                  onRedo={handleRedo}
                  canUndo={history.canUndo}
                  canRedo={history.canRedo}
                  projectPath={projectPath ?? ""}
                  projectId={activeId}
                  availableActors={availableActors}
                  availableMissions={availableMissions}
                  availableValues={availableValues}
                  availableIdentities={availableIdentities}
                  selectNodeId={null}
                  onSelectionConsumed={() => {}}
                  onNodeDrill={(id) => {
                    const n = detailCanvas.nodes.find((x) => x.id === id);
                    if (n?.kind === "actor_ref" && n.ref_actor_id) {
                      jumpToActor(n.ref_actor_id);
                    }
                  }}
                  onPublishNode={(id) => {
                    void handlePublishNode(detailCanvasKey, id);
                  }}
                  onUnpublishNode={(id) => {
                    if (!detailCanvasKey) return;
                    void handleUnpublishNode(detailCanvasKey, id);
                  }}
                />
              </ServiceDetailModal>
              );
            })()}
          </div>
        </main>
      </div>
    </div>
  );
}



