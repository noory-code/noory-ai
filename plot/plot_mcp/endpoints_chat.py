"""R7 chat — HTTP/WS endpoints (D-2026-06-12-D, Phase C step C2).

Two endpoints + the streaming bridge that ties them to ``BroadcastHub``:

  ``POST /api/chat/send``  — body ``{project_path, message}``. Validates the
                             workspace, schedules an async task that walks
                             ``ChatProvider.stream_turn`` and broadcasts each
                             event to every WS subscriber of that workspace,
                             then returns ``202 {accepted: true}``. The
                             viewer renders the user's own message
                             optimistically (no need to wait for the POST).
  ``POST /api/chat/reset`` — body ``{project_path}``. Drops the cached
                             provider so the next ``send`` starts a fresh
                             CLI session (new ``--session-id``).

The streaming bridge lives in :func:`stream_chat_turn` so the unit tests
can exercise it without going through HTTP — POST handlers stay thin.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from plot_mcp.broadcast import BroadcastHub
from plot_mcp.chat_session import ChatProvider, ChatSessionRegistry, chat_registry
from plot_mcp.workspace import resolve_plot_root

_log = logging.getLogger(__name__)

# Event name carried on the WS payload. Viewer demultiplexes on ``event``;
# the existing project_changed payload uses ``"project_changed"``.
_CHAT_EVENT = "chat_stream_event"


def _hub_from_request(request: Request) -> BroadcastHub | None:
    hub = getattr(request.app.state, "broadcast_hub", None)
    return hub if isinstance(hub, BroadcastHub) else None


def _registry_from_request(request: Request) -> ChatSessionRegistry:
    reg = getattr(request.app.state, "chat_registry", None)
    if isinstance(reg, ChatSessionRegistry):
        return reg
    return chat_registry()


async def stream_chat_turn(
    provider: ChatProvider,
    hub: BroadcastHub,
    plot_root: Path,
    user_message: str,
) -> None:
    """Pull stream events from ``provider`` and fan them out to ``plot_root``.

    Lives outside the endpoint so it stays directly testable. Errors are
    caught + broadcast as an ``error`` event so the viewer can surface them
    instead of silently truncating the turn.
    """
    try:
        async for event in provider.stream_turn(user_message):
            await hub.notify_event(
                plot_root,
                _CHAT_EVENT,
                event.model_dump(),
            )
    except Exception as exc:  # noqa: BLE001 — boundary catch
        _log.exception("chat turn crashed for %s", plot_root)
        await hub.notify_event(
            plot_root,
            _CHAT_EVENT,
            {
                "type": "error",
                "turn_id": "",
                "error_message": f"chat turn crashed: {exc}",
            },
        )


async def chat_send_endpoint(request: Request) -> JSONResponse:
    """``POST /api/chat/send`` — schedule one assistant turn against the CLI.

    Body shape::

        {"project_path": "<absolute workspace path>", "message": "<user text>"}

    Returns ``202 {"accepted": true}`` once the background task is scheduled.
    The actual streamed assistant output arrives on the workspace's WS
    channel as ``chat_stream_event`` payloads.
    """
    try:
        body: dict[str, Any] = await request.json()
    except ValueError:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    project_path = body.get("project_path")
    message = body.get("message")
    if not isinstance(project_path, str) or not project_path:
        return JSONResponse(
            {"error": "project_path required"}, status_code=400
        )
    if not isinstance(message, str) or not message.strip():
        return JSONResponse({"error": "message required"}, status_code=400)

    try:
        plot_root = resolve_plot_root(project_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)

    hub = _hub_from_request(request)
    if hub is None:
        return JSONResponse(
            {"error": "broadcast hub not configured"}, status_code=500
        )

    registry = _registry_from_request(request)
    provider = registry.get_or_create(plot_root)

    asyncio.create_task(stream_chat_turn(provider, hub, plot_root, message))
    return JSONResponse({"accepted": True}, status_code=202)


async def chat_reset_endpoint(request: Request) -> JSONResponse:
    """``POST /api/chat/reset`` — drop the workspace's cached CLI session."""
    try:
        body: dict[str, Any] = await request.json()
    except ValueError:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)
    project_path = body.get("project_path")
    if not isinstance(project_path, str) or not project_path:
        return JSONResponse(
            {"error": "project_path required"}, status_code=400
        )
    try:
        plot_root = resolve_plot_root(project_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    registry = _registry_from_request(request)
    registry.reset(plot_root)
    return JSONResponse({"reset": True})
