import type {
  CanvasDoc,
  CanvasKey,
  CanvasKind,
  ProjectChangedPayload,
  ProjectDoc,
  ProjectTag,
  SocketEvent,
} from "./types";

const API_BASE = "";

export function resolveProjectPath(): string | null {
  const url = new URL(window.location.href);
  return url.searchParams.get("project_path");
}

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res
      .json()
      .catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(body?.error ?? `HTTP ${res.status}`);
  }
  return (await res.json()) as T;
}

async function ok(res: Response): Promise<void> {
  if (!res.ok) {
    const body = await res
      .json()
      .catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(body?.error ?? `HTTP ${res.status}`);
  }
}

function canvasPath(
  projectPath: string,
  projectId: string,
  kind: CanvasKind,
  serviceId?: string | null,
): string {
  const params = new URLSearchParams({ project_path: projectPath });
  if (serviceId) params.set("service_id", serviceId);
  return `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}/canvases/${kind}?${params.toString()}`;
}

// ---------------------------------------------------------------------------
// projects
// ---------------------------------------------------------------------------

export interface ListProjectsResponse {
  projects: ProjectDoc[];
  migrated: string[];
}

export async function listProjects(projectPath: string): Promise<ListProjectsResponse> {
  const url = `${API_BASE}/api/projects?project_path=${encodeURIComponent(
    projectPath,
  )}`;
  return json<ListProjectsResponse>(await fetch(url));
}

export interface GetProjectResponse extends ProjectDoc {
  service_details: string[];
  tags: ProjectTag[];
}

export async function getProject(
  projectPath: string,
  projectId: string,
): Promise<GetProjectResponse> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}?project_path=${encodeURIComponent(projectPath)}`;
  return json<GetProjectResponse>(await fetch(url));
}

export async function createProject(
  projectPath: string,
  projectId: string,
  name: string,
): Promise<ProjectDoc> {
  const url = `${API_BASE}/api/projects?project_path=${encodeURIComponent(
    projectPath,
  )}`;
  return json<ProjectDoc>(
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: projectId, name }),
    }),
  );
}

export async function renameProject(
  projectPath: string,
  projectId: string,
  name: string,
): Promise<ProjectDoc> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}?project_path=${encodeURIComponent(projectPath)}`;
  return json<ProjectDoc>(
    await fetch(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    }),
  );
}

export async function deleteProject(
  projectPath: string,
  projectId: string,
): Promise<void> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}?project_path=${encodeURIComponent(projectPath)}`;
  return ok(await fetch(url, { method: "DELETE" }));
}

// ---------------------------------------------------------------------------
// canvases
// ---------------------------------------------------------------------------

export async function getCanvas(
  projectPath: string,
  projectId: string,
  kind: CanvasKind,
  serviceId?: string | null,
): Promise<CanvasDoc> {
  return json<CanvasDoc>(
    await fetch(canvasPath(projectPath, projectId, kind, serviceId)),
  );
}

export interface PutCanvasResponse {
  canvas: CanvasDoc;
  sync: { created: string[]; archived: string[] };
}

export async function putCanvas(
  projectPath: string,
  projectId: string,
  canvas: CanvasDoc,
): Promise<PutCanvasResponse> {
  const serviceId =
    canvas.canvas_kind === "service_detail" ? canvas.service_ref : null;
  return json<PutCanvasResponse>(
    await fetch(
      canvasPath(projectPath, projectId, canvas.canvas_kind, serviceId),
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(canvas),
      },
    ),
  );
}

/** Load every canvas the project currently has. Used on project open. */
export async function getAllCanvases(
  projectPath: string,
  projectId: string,
  serviceDetails: string[],
): Promise<Map<CanvasKey, CanvasDoc>> {
  const entries: [CanvasKey, Promise<CanvasDoc>][] = [
    ["core", getCanvas(projectPath, projectId, "core")],
    ["actors", getCanvas(projectPath, projectId, "actors")],
    [
      "services",
      getCanvas(projectPath, projectId, "services"),
    ],
  ];
  for (const sid of serviceDetails) {
    entries.push([
      `service_detail:${sid}`,
      getCanvas(projectPath, projectId, "service_detail", sid),
    ]);
  }
  const resolved = await Promise.all(entries.map(([, p]) => p));
  const out = new Map<CanvasKey, CanvasDoc>();
  entries.forEach(([key], i) => out.set(key, resolved[i]));
  return out;
}

// ---------------------------------------------------------------------------
// tags (session bookmarks)
// ---------------------------------------------------------------------------

export async function listProjectTags(
  projectPath: string,
  projectId: string,
): Promise<ProjectTag[]> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}/tags?project_path=${encodeURIComponent(projectPath)}`;
  const body = await json<{ tags: ProjectTag[] }>(await fetch(url));
  return body.tags;
}

export async function tagProject(
  projectPath: string,
  projectId: string,
  name: string,
  message?: string,
): Promise<ProjectTag> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}/tags?project_path=${encodeURIComponent(projectPath)}`;
  return json<ProjectTag>(
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, message }),
    }),
  );
}

export async function deleteProjectTag(
  projectPath: string,
  projectId: string,
  name: string,
): Promise<void> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}/tags/${encodeURIComponent(name)}?project_path=${encodeURIComponent(
    projectPath,
  )}`;
  return ok(await fetch(url, { method: "DELETE" }));
}

// ---------------------------------------------------------------------------
// v0.7 files + folders (Inspector MD editor)
// ---------------------------------------------------------------------------

/**
 * v0.8: file/folder APIs are project-scoped. Paths are always resolved
 * relative to ``.plot/{projectId}/`` on the server, so a request can't
 * accidentally address another project's tree.
 */
export async function readFile(
  projectPath: string,
  projectId: string,
  path: string,
): Promise<string> {
  const params = new URLSearchParams({
    project_path: projectPath,
    project_id: projectId,
    path,
  });
  const url = `${API_BASE}/api/files?${params.toString()}`;
  const body = await json<{ content: string }>(await fetch(url));
  return body.content;
}

/**
 * Save an MD file. When ``nodeId`` is supplied for an ``index.md`` write,
 * the server also refreshes the node's summary cache so the on-canvas
 * preview stays current without a round-trip fetch.
 */
export async function writeFile(
  projectPath: string,
  projectId: string,
  path: string,
  content: string,
  hint?: {
    nodeId?: string;
    canvasKind?: string;
  },
): Promise<{ preview: string | null }> {
  const params = new URLSearchParams({
    project_path: projectPath,
    project_id: projectId,
    path,
  });
  if (hint?.nodeId) params.set("node_id", hint.nodeId);
  if (hint?.canvasKind) params.set("canvas_kind", hint.canvasKind);
  const url = `${API_BASE}/api/files?${params.toString()}`;
  const resp = await json<{ preview?: string | null }>(
    await fetch(url, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    }),
  );
  return { preview: resp.preview ?? null };
}

/**
 * Ask the server to create ``path`` under ``.plot/{projectId}/`` and seed
 * an empty ``index.md``. Returns the path actually created — may end with
 * ``-2``/``-3`` when the desired slug was taken.
 */
export async function createFolder(
  projectPath: string,
  projectId: string,
  path: string,
): Promise<string> {
  const url = `${API_BASE}/api/folders?project_path=${encodeURIComponent(
    projectPath,
  )}`;
  const body = await json<{ path: string }>(
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId, path }),
    }),
  );
  return body.path;
}

// ---------------------------------------------------------------------------
// WebSocket
// ---------------------------------------------------------------------------

export type SocketStatus =
  | "connecting"
  | "connected"
  | "reconnecting"
  | "disconnected";

interface SocketHandlers {
  onEvent: (msg: SocketEvent) => void;
  onStatus?: (status: SocketStatus) => void;
  onError?: (err: string) => void;
}

export interface SocketHandle {
  close(): void;
}

export function openProjectSocket(
  projectPath: string,
  handlers: SocketHandlers,
): SocketHandle {
  let closed = false;
  let backoff = 500;
  let current: WebSocket | null = null;

  const connect = () => {
    if (closed) return;
    handlers.onStatus?.("connecting");
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(
      `${proto}://${window.location.host}/ws?project_path=${encodeURIComponent(
        projectPath,
      )}`,
    );
    current = ws;
    ws.onopen = () => {
      if (closed) return;
      handlers.onStatus?.("connected");
      backoff = 500;
    };
    ws.onmessage = (ev) => {
      if (closed) return;
      try {
        const msg = JSON.parse(ev.data) as SocketEvent;
        handlers.onEvent(msg);
      } catch (err) {
        handlers.onError?.(err instanceof Error ? err.message : String(err));
      }
    };
    ws.onerror = () => {
      // Swallow — onclose fires right after.
    };
    ws.onclose = () => {
      if (closed) return;
      handlers.onStatus?.("reconnecting");
      setTimeout(connect, backoff);
      backoff = Math.min(backoff * 2, 15_000);
    };
  };

  connect();
  return {
    close(): void {
      closed = true;
      if (current && current.readyState <= WebSocket.OPEN) {
        current.close();
      }
    },
  };
}

export type { ProjectChangedPayload };
