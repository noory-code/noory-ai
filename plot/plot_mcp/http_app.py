"""Starlette app composition — routes + WebSocket + static viewer."""

from __future__ import annotations

import logging

from starlette.applications import Starlette
from starlette.routing import BaseRoute, Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from plot_mcp.api_endpoints import (
    health_endpoint,
    sketch_delete_endpoint,
    sketch_get_endpoint,
    sketch_post_endpoint,
    sketch_put_endpoint,
    sketches_list_endpoint,
)
from plot_mcp.broadcast import BroadcastHub
from plot_mcp.workspace import find_viewer_dist, resolve_plot_root

_log = logging.getLogger(__name__)


def create_http_app(hub: BroadcastHub | None = None) -> Starlette:
    """Build the Starlette application exposing the browser-facing API."""
    target_hub = hub if hub is not None else BroadcastHub()

    async def ws_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        project_path = ws.query_params.get("project_path")
        if not project_path:
            await ws.close(code=1008, reason="project_path query param required")
            return
        try:
            plot_root = resolve_plot_root(project_path)
        except (FileNotFoundError, NotADirectoryError) as exc:
            await ws.close(code=1008, reason=str(exc))
            return
        await target_hub.subscribe(ws, plot_root)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            await target_hub.unsubscribe(ws, plot_root)

    routes: list[BaseRoute] = [
        Route("/api/health", health_endpoint),
        Route("/api/sketches", sketches_list_endpoint, methods=["GET"]),
        Route("/api/sketches", sketch_post_endpoint, methods=["POST"]),
        Route("/api/sketches/{sketch_id}", sketch_get_endpoint, methods=["GET"]),
        Route("/api/sketches/{sketch_id}", sketch_put_endpoint, methods=["PUT"]),
        Route("/api/sketches/{sketch_id}", sketch_delete_endpoint, methods=["DELETE"]),
        WebSocketRoute("/ws", ws_endpoint),
    ]
    viewer_dist = find_viewer_dist()
    if viewer_dist is not None:
        routes.append(Mount("/", app=StaticFiles(directory=viewer_dist, html=True)))
    else:
        _log.info("viewer dist not found; HTTP server will only expose /api and /ws")

    app = Starlette(routes=routes)
    app.state.hub = target_hub
    return app
