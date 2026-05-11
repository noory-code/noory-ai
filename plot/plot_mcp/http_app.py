"""Starlette app composition — routes + WebSocket + static viewer."""

from __future__ import annotations

import logging

from starlette.applications import Starlette
from starlette.routing import BaseRoute, Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from plot_mcp.api_endpoints import (
    canvas_get_endpoint,
    canvas_put_endpoint,
    file_get_endpoint,
    file_put_endpoint,
    folder_post_endpoint,
    health_endpoint,
    project_anchor_patch_endpoint,
    project_delete_endpoint,
    project_get_endpoint,
    project_patch_endpoint,
    project_post_endpoint,
    projects_list_endpoint,
    tag_delete_endpoint,
    tag_post_endpoint,
    tags_list_endpoint,
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
        # v0.4 project + canvas + tag surface
        Route("/api/projects", projects_list_endpoint, methods=["GET"]),
        Route("/api/projects", project_post_endpoint, methods=["POST"]),
        Route("/api/projects/{project_id}", project_get_endpoint, methods=["GET"]),
        Route(
            "/api/projects/{project_id}",
            project_patch_endpoint,
            methods=["PATCH"],
        ),
        Route(
            "/api/projects/{project_id}",
            project_delete_endpoint,
            methods=["DELETE"],
        ),
        # v0.13 Phase 0 — anchor placement per canvas
        Route(
            "/api/projects/{project_id}/anchors/{canvas}",
            project_anchor_patch_endpoint,
            methods=["PATCH"],
        ),
        Route(
            "/api/projects/{project_id}/canvases/{kind}",
            canvas_get_endpoint,
            methods=["GET"],
        ),
        Route(
            "/api/projects/{project_id}/canvases/{kind}",
            canvas_put_endpoint,
            methods=["PUT"],
        ),
        # v0.7 file + folder surface (for Inspector MD editor)
        Route("/api/files", file_get_endpoint, methods=["GET"]),
        Route("/api/files", file_put_endpoint, methods=["PUT"]),
        Route("/api/folders", folder_post_endpoint, methods=["POST"]),
        Route(
            "/api/projects/{project_id}/tags",
            tags_list_endpoint,
            methods=["GET"],
        ),
        Route(
            "/api/projects/{project_id}/tags",
            tag_post_endpoint,
            methods=["POST"],
        ),
        Route(
            "/api/projects/{project_id}/tags/{tag_name}",
            tag_delete_endpoint,
            methods=["DELETE"],
        ),
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
