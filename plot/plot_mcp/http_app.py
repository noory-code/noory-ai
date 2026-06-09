"""Starlette app composition — routes + WebSocket + static viewer."""

from __future__ import annotations

import logging

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import BaseRoute, Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from plot_mcp.api_endpoints import (
    canvas_get_endpoint,
    canvas_put_endpoint,
    dir_create_endpoint,
    dir_tree_endpoint,
    file_get_endpoint,
    file_put_endpoint,
    file_raw_endpoint,
    folder_post_endpoint,
    health_endpoint,
    node_publish_endpoint,
    node_published_list_endpoint,
    node_unpublish_endpoint,
    project_anchor_patch_endpoint,
    project_at_tag_endpoint,
    project_delete_endpoint,
    project_get_endpoint,
    project_patch_endpoint,
    project_post_endpoint,
    project_publish_endpoint,
    projects_list_endpoint,
    tag_delete_endpoint,
    tag_post_endpoint,
    tags_list_endpoint,
    workspace_discover_endpoint,
)
from plot_mcp.broadcast import BroadcastHub
from plot_mcp.debug_endpoints import debug_get_endpoint, debug_post_endpoint
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
        # v0.54.0 (D-2026-06-09-D) — dev-only debug channel: the viewer POSTs a
        # screen snapshot; an external agent GETs it (WKWebView introspection,
        # since CDP tools can't attach to the Tauri webview on macOS).
        Route("/api/debug", debug_get_endpoint, methods=["GET"]),
        Route("/api/debug", debug_post_endpoint, methods=["POST"]),
        # v0.4 project + canvas + tag surface
        Route("/api/projects", projects_list_endpoint, methods=["GET"]),
        Route("/api/projects", project_post_endpoint, methods=["POST"]),
        # v0.32.0 — recursive workspace discovery + dir-tree picker
        Route("/api/workspace/projects", workspace_discover_endpoint, methods=["GET"]),
        Route("/api/workspace/tree", dir_tree_endpoint, methods=["GET"]),
        Route("/api/workspace/dir", dir_create_endpoint, methods=["POST"]),
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
        # v0.24.0 (D-2026-05-17-L) — raw image bytes for Live Preview embeds
        Route("/api/files/raw", file_raw_endpoint, methods=["GET"]),
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
        # v0.24.13 (D-2026-05-21-B) — project-level blueprint publish.
        # Replaces "세션 기록" UX with semver bump (major/minor/patch).
        Route(
            "/api/projects/{project_id}/publish",
            project_publish_endpoint,
            methods=["POST"],
        ),
        # v0.24.14 (D-2026-05-21-C) — read-only snapshot at git tag.
        Route(
            "/api/projects/{project_id}/at-tag/{tag}",
            project_at_tag_endpoint,
            methods=["GET"],
        ),
        # v0.18.0 Phase 3 (D-2026-05-16-E) — per-node publish
        Route(
            "/api/projects/{project_id}/canvases/{canvas_kind}/nodes/{node_id}/publish",
            node_publish_endpoint,
            methods=["POST"],
        ),
        # v0.23.0 (D-2026-05-17-I) — list a node's published versions
        Route(
            "/api/projects/{project_id}/canvases/{canvas_kind}/nodes/{node_id}/published",
            node_published_list_endpoint,
            methods=["GET"],
        ),
        # v0.23.x (D-2026-05-17-J) — unpublish (git revert most recent publish)
        Route(
            "/api/projects/{project_id}/canvases/{canvas_kind}/nodes/{node_id}/unpublish",
            node_unpublish_endpoint,
            methods=["POST"],
        ),
        WebSocketRoute("/ws", ws_endpoint),
    ]
    viewer_dist = find_viewer_dist()
    if viewer_dist is not None:
        routes.append(Mount("/", app=StaticFiles(directory=viewer_dist, html=True)))
    else:
        _log.info("viewer dist not found; HTTP server will only expose /api and /ws")

    # The engine binds 127.0.0.1 only; a bundled desktop frontend (Tauri,
    # origin tauri://localhost) calls it cross-origin, so allow any origin for
    # the local API. Auth/token hardening is a separate follow-up.
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    app = Starlette(routes=routes, middleware=middleware)
    app.state.hub = target_hub
    return app
