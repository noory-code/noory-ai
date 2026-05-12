import { useCallback, useEffect, useMemo, useState } from "react";
import { patchProjectAnchor, resolveProjectPath } from "./api";
import { ActorsCanvas } from "./canvases/ActorsCanvas";
import { FoundationCanvas } from "./canvases/FoundationCanvas";
import { ServiceDetailCanvas } from "./canvases/ServiceDetailCanvas";
import { ServicesCanvas } from "./canvases/ServicesCanvas";
import { SketchSidebar } from "./canvases/SketchSidebar";
import { useProjectHistory } from "./canvases/useProjectHistory";
import { useCanvasPersist } from "./hooks/useCanvasPersist";
import { useProject } from "./hooks/useProject";
import { useProjectSocket } from "./hooks/useProjectSocket";
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
  SketchNode,
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

  const project = useProject({
    projectPath,
    history,
    initialActiveId,
    onActiveIdChange: (id) => {
      syncUrl({ project: id, sketch: null });
    },
    onError: (err) => setError(err),
  });

  const {
    summaries,
    activeId,
    canvasCache,
    tags,
    migratedToast,
    phase,
    setCanvasCache,
    setServiceDetails,
    setTags,
    loadList,
    create: handleCreate,
    rename: handleRename,
    remove: handleDelete,
    pick: handlePick,
    markSession: handleMarkSession,
    deleteTag: handleDeleteTag,
    dismissToast,
  } = project;

  // ------- persist + undo/redo (extracted to useCanvasPersist) -------

  const {
    pendingWrites,
    applyEdit,
    undo: historyUndo,
    redo: historyRedo,
  } = useCanvasPersist({
    projectPath,
    activeId,
    history,
    setCanvasCache,
    setServiceDetails,
    onListStale: () => {
      void loadList();
    },
    onError: (err) => setError(err),
  });

  // ------- WebSocket (extracted to useProjectSocket) -------

  const socketStatus = useProjectSocket({
    projectPath,
    activeId,
    pendingWrites,
    onListStale: () => {
      void loadList();
    },
    onExternalCanvas: (key, fresh) => {
      setCanvasCache((prev) => {
        const next = new Map(prev);
        next.set(key, fresh);
        return next;
      });
    },
    onTagsRefresh: (nextTags) => setTags(nextTags),
    onExternalChange: () => history.clear(),
    onError: (err) => setError(err),
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

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) {
        return;
      }
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
        return;
      }
      if (mod && ((e.key === "z" && e.shiftKey) || e.key === "y")) {
        e.preventDefault();
        handleRedo();
        return;
      }
      // ``?`` without modifiers → toggle help.
      if (!mod && !e.altKey && (e.key === "?" || (e.shiftKey && e.key === "/"))) {
        e.preventDefault();
        setHelpOpen((v) => !v);
        return;
      }
      if (!mod && e.key === "Escape" && helpOpen) {
        e.preventDefault();
        setHelpOpen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleUndo, handleRedo, helpOpen]);

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

  // actors canvas provides the orphan check list + picker source
  const actorsCanvas = canvasCache.get("actors");
  const availableActors: SketchNode[] = useMemo(() => {
    if (!actorsCanvas) return [];
    return actorsCanvas.nodes.filter((n) => n.kind === "actor");
  }, [actorsCanvas]);

  // v0.10 Step 3: foundation canvas feeds the FoundationRefPicker. The
  // three master kinds are filtered separately so each picker shows only
  // the relevant candidates.
  const foundationCanvas = canvasCache.get("foundation");
  const availableMissions: SketchNode[] = useMemo(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "mission");
  }, [foundationCanvas]);
  const availableValues: SketchNode[] = useMemo(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "core_value");
  }, [foundationCanvas]);
  const availableIdentities: SketchNode[] = useMemo(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "identity");
  }, [foundationCanvas]);

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
        projectName={summaries.find((p) => p.id === activeId)?.name ?? null}
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
        />
        <main className="flex flex-1 flex-col overflow-hidden">
          {phase === "ready" && (
            <CanvasTabs
              active={activeTab}
              onSelect={selectTab}
              onMarkSession={handleMarkSession}
            />
          )}
          <div className="flex-1 overflow-hidden">
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
                onAnchorChange={(patch) => {
                  if (!projectPath) return;
                  void patchProjectAnchor(projectPath, activeId, activeTab, patch).then(
                    (refreshed) => {
                      project.replaceSummary?.(refreshed);
                    },
                  );
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
          </div>
        </main>
      </div>
      {/* v0.12 — Service detail modal. Renders on top of the services
          canvas without unmounting it. Esc / backdrop click closes. */}
      {phase === "ready" && detailServiceId && detailCanvas && detailCanvasKey && activeId && (() => {
        const servicesNodes = canvasCache.get("services")?.nodes ?? [];
        const svcNode = servicesNodes.find((n) => n.id === detailServiceId);
        // v0.12.6 — surface the parent category so the modal header carries
        // drill context. parent_id on a service points at the category.
        const categoryNode = svcNode?.parent_id
          ? servicesNodes.find((n) => n.id === svcNode.parent_id)
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
          />
        </ServiceDetailModal>
        );
      })()}
    </div>
  );
}



