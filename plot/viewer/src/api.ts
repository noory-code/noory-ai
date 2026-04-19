import type { SketchDoc, SketchSummary } from "./types";

const API_BASE = "";

export function resolveProjectPath(): string | null {
  const url = new URL(window.location.href);
  return url.searchParams.get("project_path");
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(body?.error ?? `HTTP ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function listSketches(projectPath: string): Promise<SketchSummary[]> {
  const url = `${API_BASE}/api/sketches?project_path=${encodeURIComponent(projectPath)}`;
  return json<SketchSummary[]>(await fetch(url));
}

export async function getSketch(projectPath: string, sketchId: string): Promise<SketchDoc> {
  const url = `${API_BASE}/api/sketches/${encodeURIComponent(
    sketchId,
  )}?project_path=${encodeURIComponent(projectPath)}`;
  return json<SketchDoc>(await fetch(url));
}

export async function createSketch(
  projectPath: string,
  sketchId: string,
  name: string,
): Promise<SketchDoc> {
  const url = `${API_BASE}/api/sketches?project_path=${encodeURIComponent(projectPath)}`;
  return json<SketchDoc>(
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: sketchId, name }),
    }),
  );
}

export async function putSketch(projectPath: string, doc: SketchDoc): Promise<void> {
  const url = `${API_BASE}/api/sketches/${encodeURIComponent(
    doc.id,
  )}?project_path=${encodeURIComponent(projectPath)}`;
  const res = await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(doc),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(body?.error ?? `HTTP ${res.status}`);
  }
}

export async function deleteSketch(projectPath: string, sketchId: string): Promise<void> {
  const url = `${API_BASE}/api/sketches/${encodeURIComponent(
    sketchId,
  )}?project_path=${encodeURIComponent(projectPath)}`;
  const res = await fetch(url, { method: "DELETE" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(body?.error ?? `HTTP ${res.status}`);
  }
}

// ---------------------------------------------------------------------------
// WebSocket
// ---------------------------------------------------------------------------

export type SocketStatus = "connecting" | "connected" | "reconnecting" | "disconnected";

export interface SocketEvent {
  event: "sketch_changed" | string;
}

interface SocketHandlers {
  onEvent: (msg: SocketEvent) => void;
  onStatus?: (status: SocketStatus) => void;
  onError?: (err: string) => void;
}

export interface SocketHandle {
  close(): void;
}

export function openSketchSocket(projectPath: string, handlers: SocketHandlers): SocketHandle {
  let closed = false;
  let backoff = 500;
  let current: WebSocket | null = null;

  const connect = () => {
    if (closed) return;
    handlers.onStatus?.("connecting");
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(
      `${proto}://${window.location.host}/ws?project_path=${encodeURIComponent(projectPath)}`,
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
      // Swallow — onclose fires right after with the real reconnect logic.
    };
    ws.onclose = () => {
      // Abandoned sockets (after caller.close()) don't touch status — the
      // new socket from a StrictMode remount owns the status now.
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
