import type {
  CanvasDoc,
  CanvasKey,
  CanvasKind,
  ProjectChangedPayload,
  ProjectDoc,
  ProjectTag,
  SocketEvent,
} from "./types";

// Engine HTTP base. Empty = same-origin (web / engine-served / Vite-proxied dev).
// Set VITE_PLOT_ENGINE (e.g. "http://127.0.0.1:5190") when the frontend is
// bundled separately from the engine (Tauri desktop app). This is the single
// place the engine location is configured — the forward-compat seam for a
// future remote/relocated engine (tablet).
const API_BASE = (import.meta.env.VITE_PLOT_ENGINE as string | undefined) ?? "";

export function resolveProjectPath(): string | null {
  const url = new URL(window.location.href);
  return url.searchParams.get("project_path");
}

/** Alias — the launch URL param is the WORKSPACE ROOT (v0.33.0): used for
 *  recursive discovery + the dir-tree picker, not for per-project I/O. */
export const resolveWorkspaceRoot = resolveProjectPath;

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

// --- workspace discovery + dir-tree picker (v0.33.0, D-2026-05-31-M) ---
// TS mirrors of the Pydantic response models (plot_mcp/models.py); kept in
// sync by hand (outside the 15-kind schema-parity harness).

export interface DiscoveredProject {
  project: ProjectDoc;
  /** POSIX-relative dir under the workspace root; "." for root-level. */
  dir: string;
}

export interface WorkspaceDiscoveryResponse {
  projects: DiscoveredProject[];
  migrated: string[];
}

export interface DirTreeNode {
  name: string;
  rel: string;
  has_plot: boolean;
  children: DirTreeNode[];
}

export interface DirTreeResponse {
  root: DirTreeNode;
}

/** Recursively discover every project under the workspace root. */
export async function discoverWorkspace(
  workspaceRoot: string,
): Promise<WorkspaceDiscoveryResponse> {
  const url = `${API_BASE}/api/workspace/projects?project_path=${encodeURIComponent(
    workspaceRoot,
  )}`;
  return json<WorkspaceDiscoveryResponse>(await fetch(url));
}

/** Nested directory tree (with has_plot flags) for the new-project picker. */
export async function getDirTree(workspaceRoot: string): Promise<DirTreeResponse> {
  const url = `${API_BASE}/api/workspace/tree?project_path=${encodeURIComponent(
    workspaceRoot,
  )}`;
  return json<DirTreeResponse>(await fetch(url));
}

/** Create a new directory under the workspace root (v0.37.0, D-2026-05-31-AC) —
 *  the picker's "new folder" affordance. ``rel`` is POSIX-relative + path-safe;
 *  returns the created rel. */
export async function createWorkspaceDir(
  workspaceRoot: string,
  rel: string,
): Promise<{ rel: string }> {
  const url = `${API_BASE}/api/workspace/dir?project_path=${encodeURIComponent(
    workspaceRoot,
  )}`;
  return json<{ rel: string }>(
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rel }),
    }),
  );
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

/**
 * v0.13 Phase 0: PATCH the per-canvas project anchor placement. Body fields
 * are all optional; only supplied fields are updated. Returns the refreshed
 * ProjectDoc.
 */
export async function patchProjectAnchor(
  projectPath: string,
  projectId: string,
  canvas: CanvasKind,
  patch: Partial<{
    x: number;
    y: number;
    width: number;
    height: number;
    color: string;
    shape: string;
  }>,
): Promise<ProjectDoc> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}/anchors/${encodeURIComponent(canvas)}?project_path=${encodeURIComponent(
    projectPath,
  )}`;
  return json<ProjectDoc>(
    await fetch(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch),
    }),
  );
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
  /** v0.27.14 (D-2026-05-28-I) — ``skipped_archive`` lists service
   *  details that the server **refused to archive** because they
   *  carried user-authored content (a node beyond the default
   *  seed set, or any edge). The viewer should surface these to
   *  the user as a warning so they can decide whether to restore
   *  the service in the overview or explicitly delete the detail. */
  sync: { created: string[]; archived: string[]; skipped_archive?: string[] };
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
    ["foundation", getCanvas(projectPath, projectId, "foundation")],
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

// ---------------------------------------------------------------------------
// Snapshot view — v0.24.14 (D-2026-05-21-C)
// Read project + all canvases at a given git tag (read-only).
// ---------------------------------------------------------------------------

export interface ProjectAtTagResponse {
  project: ProjectDoc;
  canvases: Record<string, CanvasDoc>;
}

export async function getProjectAtTag(
  projectPath: string,
  projectId: string,
  tag: string,
): Promise<ProjectAtTagResponse> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}/at-tag/${encodeURIComponent(tag)}?project_path=${encodeURIComponent(projectPath)}`;
  return json<ProjectAtTagResponse>(await fetch(url));
}

// ---------------------------------------------------------------------------
// Project-level publish — v0.24.13 (D-2026-05-21-B)
// Bump blueprint semver (major/minor/patch) + create git tag.
// ---------------------------------------------------------------------------

export type BlueprintBump = "major" | "minor" | "patch";

export interface PublishProjectResponse {
  from_version: string;
  to_version: string;
  tag: ProjectTag;
}

export async function publishProject(
  projectPath: string,
  projectId: string,
  bump: BlueprintBump,
  message?: string,
): Promise<PublishProjectResponse> {
  const url = `${API_BASE}/api/projects/${encodeURIComponent(
    projectId,
  )}/publish?project_path=${encodeURIComponent(projectPath)}`;
  return json<PublishProjectResponse>(
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bump, message }),
    }),
  );
}

// ---------------------------------------------------------------------------
// Publish — D-2026-05-16-E (Phase 3, MAJOR) + D-2026-05-17-C (Phase 4, MINOR
// propagation)
// ---------------------------------------------------------------------------

export interface PublishPropagatedAncestor {
  node_id: string;
  from_version: string;
  to_version: string;
  /** Canvas keys this ancestor has file-presence in (e.g. ``services``,
   * ``service_detail:<sid>``). All canvases were bumped in lockstep. */
  canvases: string[];
}

export interface PublishNodeResponse {
  node_id: string;
  from_version: string;
  to_version: string;
  md_path: string;
  sha: string;
  /** v0.20.0: ancestors whose MINOR version was bumped by this publish.
   * Empty when the published node is a top-level peer (Foundation
   * mission / core_value / identity / Actors actor). */
  propagated: PublishPropagatedAncestor[];
}

export async function publishNode(
  projectPath: string,
  projectId: string,
  canvasKind: string,
  nodeId: string,
  serviceId?: string,
): Promise<PublishNodeResponse> {
  const params = new URLSearchParams({ project_path: projectPath });
  if (serviceId) params.set("service_id", serviceId);
  const url =
    `${API_BASE}/api/projects/${encodeURIComponent(projectId)}` +
    `/canvases/${encodeURIComponent(canvasKind)}` +
    `/nodes/${encodeURIComponent(nodeId)}/publish?${params.toString()}`;
  return json<PublishNodeResponse>(
    await fetch(url, { method: "POST" }),
  );
}

/** v0.23.x (D-2026-05-17-J) — unpublish (git revert) response. */
export interface UnpublishNodeResponse {
  node_id: string;
  from_version: string;
  to_version: string;
  reverted_sha: string;
  revert_commit_sha: string;
}

export async function unpublishNode(
  projectPath: string,
  projectId: string,
  canvasKind: string,
  nodeId: string,
  serviceId?: string,
): Promise<UnpublishNodeResponse> {
  const params = new URLSearchParams({ project_path: projectPath });
  if (serviceId) params.set("service_id", serviceId);
  const url =
    `${API_BASE}/api/projects/${encodeURIComponent(projectId)}` +
    `/canvases/${encodeURIComponent(canvasKind)}` +
    `/nodes/${encodeURIComponent(nodeId)}/unpublish?${params.toString()}`;
  return json<UnpublishNodeResponse>(await fetch(url, { method: "POST" }));
}

/** v0.23.0 (D-2026-05-17-I) — one published version's metadata. */
export interface PublishedVersion {
  version: string;
  path: string;
  published_at: string | null;
  sha: string | null;
  size: number;
}

export interface PublishedVersionsResponse {
  versions: PublishedVersion[];
}

/** v0.23.0 — list a node's published MD versions (newest first). */
export async function listPublishedVersions(
  projectPath: string,
  projectId: string,
  canvasKind: string,
  nodeId: string,
  serviceId?: string,
): Promise<PublishedVersion[]> {
  const params = new URLSearchParams({ project_path: projectPath });
  if (serviceId) params.set("service_id", serviceId);
  const url =
    `${API_BASE}/api/projects/${encodeURIComponent(projectId)}` +
    `/canvases/${encodeURIComponent(canvasKind)}` +
    `/nodes/${encodeURIComponent(nodeId)}/published?${params.toString()}`;
  const resp = await json<PublishedVersionsResponse>(await fetch(url));
  return resp.versions;
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
 * URL for the raw bytes of a project file — used by the markdown image embed
 * decorator (``/api/files/raw`` serves binary, unlike the JSON ``/api/files``).
 * Built through ``API_BASE`` so a separately-bundled desktop frontend
 * (tauri://) hits the configured engine origin, not its own. (D-2026-06-08-A)
 */
export function rawFileUrl(projectPath: string, projectId: string, path: string): string {
  const params = new URLSearchParams({
    project_path: projectPath,
    project_id: projectId,
    path,
  });
  return `${API_BASE}/api/files/raw?${params.toString()}`;
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
    // WS base mirrors API_BASE: when the engine is at an explicit origin
    // (bundled desktop app), derive ws(s):// from it; else same-origin host.
    const wsBase = API_BASE
      ? API_BASE.replace(/^http/, "ws")
      : `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`;
    const ws = new WebSocket(
      `${wsBase}/ws?project_path=${encodeURIComponent(projectPath)}`,
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
