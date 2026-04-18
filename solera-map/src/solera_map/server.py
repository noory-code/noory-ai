"""Combined MCP (stdio) + HTTP (localhost) server for solera-map.

A single asyncio event loop hosts two transports side-by-side:

- FastMCP over stdio for Claude Code tool calls
- Starlette + uvicorn over http://127.0.0.1:{port} for the browser viewer

Both transports read the same `Graph` built by `solera_map.graph.build_graph`
against a workspace directory supplied by the caller. The server holds no
process-wide project state — every request resolves its own `project_path`.

Port selection:
- Default 5170; override via `SOLERA_MAP_PORT`.
- If the port is in use, the HTTP server logs a warning and skips HTTP
  startup — the MCP transport remains usable so the plugin still works.
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
from pathlib import Path
from typing import Any

import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute, Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from solera_map.graph import Graph, build_graph
from solera_map.watcher import WorkspaceWatcher

_log = logging.getLogger(__name__)

DEFAULT_HTTP_PORT = 5170


# ---------------------------------------------------------------------------
# Project path resolution
# ---------------------------------------------------------------------------


def resolve_workspace(project_path: str) -> Path:
    """Resolve the `workspace/` directory under a Solera project path.

    Accepts either the project root (containing `workspace/`) or the workspace
    directory itself. Raises `FileNotFoundError` if neither form locates a
    Concepts-bearing workspace.
    """
    base = Path(project_path).expanduser().resolve()
    candidates = [base / "workspace", base]
    for candidate in candidates:
        if (candidate / "concepts").exists() or (candidate / "identity").exists():
            return candidate
    raise FileNotFoundError(
        f"No Solera workspace found under {project_path!r} "
        f"(looked for `workspace/` and bare directory)"
    )


def _graph_for(project_path: str) -> Graph:
    workspace = resolve_workspace(project_path)
    return build_graph(workspace)


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "solera-map",
    instructions=(
        "solera-map exposes a Solera workspace as a typed graph of Concepts, "
        "Concept↔Concept edges, Milestones, Stories, Action Items, and Releases. "
        "Use `get_map(project_path)` to read the full graph. Future tools will "
        "propose edges and concepts before they are persisted."
    ),
)


@mcp.tool()
def get_map(project_path: str) -> dict[str, Any]:
    """Return the Solera workspace graph for `project_path` as a JSON-ready dict.

    Args:
        project_path: Project root (containing `workspace/`) or the workspace
            directory itself.
    """
    return _graph_for(project_path).model_dump(by_alias=True)


@mcp.tool()
def open_map(project_path: str) -> str:
    """Open the Solera Map viewer in the user's default browser.

    Invoked by the `/map` slash command. Validates that `project_path` is a
    readable Solera workspace before opening, so the browser never lands on
    a blank error page.
    """
    import webbrowser

    resolve_workspace(project_path)  # raises if not a workspace
    port = _resolved_port()
    url = f"http://127.0.0.1:{port}/?project_path={project_path}"
    webbrowser.open(url)
    return f"Opened {url}"


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------


async def _graph_endpoint(request: Request) -> JSONResponse:
    project_path = request.query_params.get("project_path")
    if not project_path:
        return JSONResponse(
            {"error": "project_path query param is required"}, status_code=400
        )
    try:
        graph = _graph_for(project_path)
    except FileNotFoundError as exc:
        return JSONResponse({"error": str(exc)}, status_code=404)
    return JSONResponse(graph.model_dump(by_alias=True))


async def _health_endpoint(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "solera-map"})


class BroadcastHub:
    """Fan-out between workspace watchers and connected WebSocket clients.

    One watcher per workspace, created on the first subscription and torn
    down when the last client for that workspace disconnects. Broadcasts
    are idempotent — `notify(workspace)` can be called directly (by tests
    or future MCP triggers) without a real filesystem event.

    Tests that don't want a real filesystem watcher may pass
    `enable_watchers=False`; subscriptions still work and `notify` remains
    the event source.
    """

    def __init__(self, *, enable_watchers: bool = True) -> None:
        self._subs: dict[Path, set[WebSocket]] = {}
        self._watchers: dict[Path, WorkspaceWatcher] = {}
        self._lock = asyncio.Lock()
        self._enable_watchers = enable_watchers

    async def subscribe(self, ws: WebSocket, workspace: Path) -> None:
        async with self._lock:
            if workspace not in self._subs:
                self._subs[workspace] = set()
                if self._enable_watchers:
                    self._watchers[workspace] = self._start_watcher(workspace)
            self._subs[workspace].add(ws)

    async def unsubscribe(self, ws: WebSocket, workspace: Path) -> None:
        async with self._lock:
            subs = self._subs.get(workspace)
            if subs is None:
                return
            subs.discard(ws)
            if not subs:
                self._subs.pop(workspace, None)
                watcher = self._watchers.pop(workspace, None)
                if watcher is not None:
                    watcher.stop()

    async def notify(self, workspace: Path) -> None:
        """Broadcast a `graph_changed` event to all subscribers of workspace."""
        async with self._lock:
            targets = list(self._subs.get(workspace, ()))
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json({"event": "graph_changed"})
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                subs = self._subs.get(workspace)
                if subs is not None:
                    for ws in dead:
                        subs.discard(ws)

    def subscription_count(self, workspace: Path) -> int:
        return len(self._subs.get(workspace, ()))

    def _start_watcher(self, workspace: Path) -> WorkspaceWatcher:
        loop = asyncio.get_running_loop()

        async def on_change() -> None:
            await self.notify(workspace)

        watcher = WorkspaceWatcher(workspace, on_change=on_change, loop=loop)
        watcher.start()
        return watcher

    async def shutdown(self) -> None:
        async with self._lock:
            for watcher in self._watchers.values():
                watcher.stop()
            self._watchers.clear()
            self._subs.clear()


def create_http_app(hub: BroadcastHub | None = None) -> Starlette:
    """Build the Starlette application exposing the browser-facing API.

    If `hub` is omitted, a fresh `BroadcastHub` is created and attached to
    `app.state.hub` so callers (and tests) can reach it.
    """
    target_hub = hub if hub is not None else BroadcastHub()

    async def ws_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        project_path = ws.query_params.get("project_path")
        if not project_path:
            await ws.close(code=1008, reason="project_path query param required")
            return
        try:
            workspace = resolve_workspace(project_path)
        except FileNotFoundError as exc:
            await ws.close(code=1008, reason=str(exc))
            return
        await target_hub.subscribe(ws, workspace)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            await target_hub.unsubscribe(ws, workspace)

    routes: list[BaseRoute] = [
        Route("/api/health", _health_endpoint),
        Route("/api/graph", _graph_endpoint),
        WebSocketRoute("/ws", ws_endpoint),
    ]
    viewer_dist = _find_viewer_dist()
    if viewer_dist is not None:
        # SPA: html=True also serves index.html when a path 404s, so client
        # routes resolve without additional wiring.
        routes.append(Mount("/", app=StaticFiles(directory=viewer_dist, html=True)))
    else:
        _log.info("viewer dist not found; HTTP server will only expose /api and /ws")

    app = Starlette(routes=routes)
    app.state.hub = target_hub
    return app


def _find_viewer_dist() -> Path | None:
    """Locate `viewer/dist/` produced by Vite.

    Plugin runtime path: `${CLAUDE_PLUGIN_ROOT}/viewer/dist`
    Dev path: walk up from this file until we find `viewer/dist/index.html`.
    """
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        candidate = Path(env) / "viewer" / "dist"
        if (candidate / "index.html").exists():
            return candidate
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "viewer" / "dist"
        if (candidate / "index.html").exists():
            return candidate
    return None


def _port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _resolved_port() -> int:
    raw = os.environ.get("SOLERA_MAP_PORT")
    if not raw:
        return DEFAULT_HTTP_PORT
    try:
        return int(raw)
    except ValueError:
        _log.warning("Invalid SOLERA_MAP_PORT=%r; falling back to %d", raw, DEFAULT_HTTP_PORT)
        return DEFAULT_HTTP_PORT


async def _serve() -> None:
    hub = BroadcastHub()
    http_app = create_http_app(hub=hub)
    port = _resolved_port()

    tasks: list[asyncio.Task[None]] = [
        asyncio.create_task(mcp.run_stdio_async(), name="mcp-stdio"),
    ]

    if _port_is_free(port):
        http_config = uvicorn.Config(
            http_app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
        )
        http_server = uvicorn.Server(http_config)
        tasks.append(asyncio.create_task(http_server.serve(), name="http"))
    else:
        _log.warning(
            "HTTP port %d in use; another solera-map instance may already serve the browser. "
            "MCP stdio transport remains available.",
            port,
        )

    try:
        await asyncio.gather(*tasks)
    finally:
        await hub.shutdown()


def run() -> None:
    """Entry point invoked by `python -m solera_map`."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(_serve())
    except KeyboardInterrupt:
        pass


def run_http_only() -> None:
    """Run only the HTTP server — useful for `npm run dev` against an existing
    browser, or for manual end-to-end verification without an MCP client.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    hub = BroadcastHub()
    app = create_http_app(hub=hub)
    port = _resolved_port()
    try:
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
    except KeyboardInterrupt:
        pass
    finally:
        # Sync shutdown — acceptable since we own the loop.
        asyncio.run(hub.shutdown())
