import type { Graph, Layout } from "./types";

const API_BASE = "";

export async function fetchGraph(projectPath: string): Promise<Graph> {
  const url = `${API_BASE}/api/graph?project_path=${encodeURIComponent(projectPath)}`;
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(body?.error ?? `HTTP ${res.status}`);
  }
  return (await res.json()) as Graph;
}

export async function fetchLayout(projectPath: string): Promise<Layout> {
  const url = `${API_BASE}/api/layout?project_path=${encodeURIComponent(projectPath)}`;
  const res = await fetch(url);
  if (!res.ok) {
    return { nodes: {} };
  }
  return (await res.json()) as Layout;
}

export async function saveLayout(projectPath: string, layout: Layout): Promise<void> {
  const url = `${API_BASE}/api/layout?project_path=${encodeURIComponent(projectPath)}`;
  const res = await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(layout),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(body?.error ?? `HTTP ${res.status}`);
  }
}

export async function patchConcept(
  projectPath: string,
  conceptId: string,
  patch: { parent?: string | null },
): Promise<void> {
  const url = `${API_BASE}/api/concept/${encodeURIComponent(
    conceptId,
  )}?project_path=${encodeURIComponent(projectPath)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(body?.error ?? `HTTP ${res.status}`);
  }
}

export interface GraphSocket {
  close(): void;
}

export function openGraphSocket(
  projectPath: string,
  onEvent: (event: { event: string }) => void,
  onError: (err: string) => void,
): GraphSocket {
  const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
  const host = window.location.host;
  const url = `${wsProto}://${host}/ws?project_path=${encodeURIComponent(projectPath)}`;
  const ws = new WebSocket(url);

  ws.onmessage = (e) => {
    try {
      onEvent(JSON.parse(e.data));
    } catch {
      onError("malformed message");
    }
  };
  ws.onerror = () => onError("websocket error");
  ws.onclose = (e) => {
    if (e.code !== 1000 && e.code !== 1001) {
      onError(`connection closed (${e.code})`);
    }
  };

  return { close: () => ws.close() };
}

export function resolveProjectPath(): string {
  const params = new URLSearchParams(window.location.search);
  return params.get("project_path") ?? params.get("project") ?? "";
}
