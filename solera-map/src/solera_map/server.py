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
from starlette.routing import Route

from solera_map.graph import Graph, build_graph

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


def create_http_app() -> Starlette:
    """Build the Starlette application exposing the browser-facing API."""
    return Starlette(
        routes=[
            Route("/api/health", _health_endpoint),
            Route("/api/graph", _graph_endpoint),
        ]
    )


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
    http_app = create_http_app()
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

    await asyncio.gather(*tasks)


def run() -> None:
    """Entry point invoked by `python -m solera_map`."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(_serve())
    except KeyboardInterrupt:
        pass
