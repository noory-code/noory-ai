import { useEffect, useRef, useState } from "react";
import {
  getCanvas,
  getProject,
  openProjectSocket,
  type SocketStatus,
} from "../api";
import { canvasKey } from "../lib/canvasKey";
import type { EchoGuard } from "../lib/echoGuard";
import type { CanvasDoc, CanvasKey, CanvasKind, ProjectTag } from "../types";

export interface UseProjectSocketArgs {
  projectPath: string | null;
  /** Currently open project id — live-tracked via ref so re-subscribing
   *  every tab switch isn't needed. */
  activeId: string | null;
  /** Self-echo guard shared with ``useCanvasPersist``. An incoming
   *  ``project_changed`` that ``consume()`` accepts is the server echoing our
   *  own write — skip it. (D-2026-06-08-A, step 3) */
  echoGuard: React.MutableRefObject<EchoGuard>;
  /** Refresh the sidebar project list (name / updated bumps). */
  onListStale: () => void;
  /** Apply a canvas refetched because another client changed it. */
  onExternalCanvas: (key: CanvasKey, canvas: CanvasDoc) => void;
  /** Refresh the tag list for the currently-open project. */
  onTagsRefresh: (tags: ProjectTag[]) => void;
  /** Called when an external change arrives — viewer clears in-memory
   *  undo history so a later ``undo`` can't replay stale state. */
  onExternalChange: () => void;
  onError: (err: string) => void;
}

/**
 * Holds the project-scoped WebSocket. One subscription per ``projectPath``;
 * re-subscribes only when the path itself changes.
 *
 * v0.33.0 (D-2026-05-31-M): ``projectPath`` is now the **effective project
 * path** (workspace root + the active project's dir). Switching to a project
 * in a **different directory** changes the path → the socket reconnects to
 * that dir's plot root. Switching between projects in the **same directory**
 * leaves the path unchanged → no reconnect; ``activeId`` filtering in the
 * event handler still scopes events to the open project.
 */
export function useProjectSocket(args: UseProjectSocketArgs): SocketStatus {
  const [status, setStatus] = useState<SocketStatus>("connecting");

  // Stash everything that can change without forcing a reconnect.
  const activeIdRef = useRef(args.activeId);
  activeIdRef.current = args.activeId;
  const handlersRef = useRef(args);
  handlersRef.current = args;

  const { projectPath } = args;
  useEffect(() => {
    if (!projectPath) return;
    const sock = openProjectSocket(projectPath, {
      onEvent: (msg) => {
        if (msg.event !== "project_changed") return;
        const payload = msg as {
          project_id?: string;
          canvas_kind?: CanvasKind;
          service_id?: string;
        };
        const pid = activeIdRef.current;
        const h = handlersRef.current;
        if (!pid) return;

        if (payload.project_id && payload.project_id !== pid) {
          // Different project changed — sidebar only.
          h.onListStale();
          return;
        }

        const key = payload.canvas_kind
          ? canvasKey(payload.canvas_kind, payload.service_id)
          : null;

        // Our own write echoing back? skip.
        if (key && h.echoGuard.current.consume(key)) {
          return;
        }

        // External write on the current project — drop history + refresh.
        h.onExternalChange();

        if (key) {
          void (async () => {
            try {
              const fresh = await getCanvas(
                projectPath,
                pid,
                payload.canvas_kind!,
                payload.service_id ?? null,
              );
              h.onExternalCanvas(key, fresh);
            } catch (err) {
              h.onError(err instanceof Error ? err.message : String(err));
            }
          })();
        } else {
          // Project-level event (e.g., new tag) — list + tags.
          h.onListStale();
          void getProject(projectPath, pid).then((p) => h.onTagsRefresh(p.tags));
        }
      },
      onStatus: setStatus,
      onError: (err) => handlersRef.current.onError(err),
    });
    return () => sock.close();
  }, [projectPath]);

  return status;
}
