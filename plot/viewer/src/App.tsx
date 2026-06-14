import { useCallback, useMemo, useState } from "react";
import { patchProjectAnchor } from "./app/project";
import { resolveWorkspaceRoot } from "./app/workspace";
import { ProjectPicker } from "./shell/ProjectPicker";
import { applyOptimisticAnchorPatch } from "./lib/anchorOptimistic";
import { ActorsCanvas } from "./canvases/ActorsCanvas";
import { FoundationCanvas } from "./canvases/FoundationCanvas";
import { ServiceDetailCanvas } from "./canvases/ServiceDetailCanvas";
import { ServicesCanvas } from "./canvases/ServicesCanvas";
import { SketchSidebar } from "./canvases/SketchSidebar";
import { StencilDragProvider } from "./canvases/sketch/StencilDragContext";
import { parentIdOf } from "./canvases/sketch/hierarchy";
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
import { ServiceDetailModal } from "./shell/ServiceDetailModal";
import { ServiceDetailStencilPanel } from "./shell/ServiceDetailStencilPanel";
import { EmptyState, ErrorPanel, Loading } from "./shell/states";
import type {
  AnchorPlacement,
  CanvasDoc,
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
  const workspaceRoot = useMemo(resolveWorkspaceRoot, []);
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
    workspaceRoot,
    history,
    initialActiveId,
    onActiveIdChange: handleActiveIdChange,
    onError: handleError,
  });
  const {
    summaries, activeId, activeProjectPath, dirForId,
    canvasCache: liveCanvasCache, tags, migratedToast, phase,
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
    setServiceDetails,
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

  // v0.27.7 (D-2026-05-27-C) — inline arrow callbacks on the Canvas /
  // ServiceDetailCanvas elements were re-created on every App render,
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
      if (
        activeTab === "services" &&
        n.kind === "service" &&
        !n.is_root
      ) {
        drillIntoService(id);
      }
    },
    [activeCanvas, activeTab, jumpToActor, drillIntoService],
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

  const modalOpen = phase === "ready" && !!detailServiceId && !!detailCanvas && !!detailCanvasKey && !!activeId;

  return (
    <StencilDragProvider>
    <div
      className="flex h-screen min-h-screen flex-col"
      // v0.27.2 (D-2026-05-26-F) — when the ServiceDetail modal is
      // open, the rest of the app is inert: no clicks, no focus, no
      // drag, no keyboard. The modal sits OUTSIDE this div (sibling
      // below) so inert does not cascade into it.
      {...(modalOpen ? { inert: "" as unknown as undefined } : {})}
    >
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
        chat={<ChatDock onError={handleError} workspaceRoot={workspaceRoot} activeScope={modalOpen ? "service_detail" : tabToKind(activeTab)} selection={(activeCanvas?.nodes ?? []).filter((n) => canvasSelectionIds.includes(n.id)).map((n) => ({ id: n.id, kind: n.kind, label: n.label ?? "" }))} />}
        sidebar={
        <SketchSidebar
          projects={summaries}
          activeId={activeId}
          dirForId={dirForId}
          stencilCanvas={activeTab}
          availableActors={availableActors}
          availableMissions={availableMissions}
          availableValues={availableValues}
          availableIdentities={availableIdentities}
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
            />
          )}
          <div className="relative flex-1 overflow-hidden">
            {phase === "loading" && <Loading />}
            {phase === "error" && <ErrorPanel message={error ?? "unknown"} />}
            {phase === "no-projects" && <EmptyState onCreate={dirPicker.open} />}
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
    {/* v0.27.2 (D-2026-05-26-F) — modal sits OUTSIDE the inert root
        div so the user can still interact with it. fixed inset-0
        covers the whole viewport; everything behind it is inert. */}
    {modalOpen && (() => {
      const servicesCanvas = canvasCache.get("services");
      const servicesNodes = servicesCanvas?.nodes ?? [];
      const servicesEdges = servicesCanvas?.edges ?? [];
      const svcNode = servicesNodes.find((n) => n.id === detailServiceId);
      const categoryId = svcNode ? parentIdOf(servicesEdges, svcNode.id) : null;
      const categoryNode = categoryId ? servicesNodes.find((n) => n.id === categoryId) : undefined;
      return (
        <ServiceDetailModal
          serviceLabel={svcNode?.label ?? detailServiceId!}
          categoryLabel={categoryNode?.label ?? null}
          onClose={backToOverview}
          stencilSlot={<ServiceDetailStencilPanel availableActors={availableActors} availableMissions={availableMissions} availableValues={availableValues} availableIdentities={availableIdentities} />}
        >
          <ServiceDetailCanvas
            key={`${activeId}:${detailCanvasKey}`}
            doc={detailCanvas!}
            onDocChange={onModalDocChange}
            onUndo={handleUndo}
            onRedo={handleRedo}
            canUndo={history.canUndo}
            canRedo={history.canRedo}
            projectPath={activeProjectPath ?? ""}
            projectId={activeId!}
            availableActors={availableActors}
            availableMissions={availableMissions}
            availableValues={availableValues}
            availableIdentities={availableIdentities}
            selectNodeId={null}
            onSelectionConsumed={onModalSelectionConsumed}
            onNodeDrill={onModalNodeDrill}
            onPublishNode={onModalPublishNode}
            onUnpublishNode={onModalUnpublishNode}
          />
        </ServiceDetailModal>
      );
    })()}
    {dirPicker.modal}
    </StencilDragProvider>
  );
}



