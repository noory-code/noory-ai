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
from typing import Any, get_args

from starlette.requests import Request
from starlette.responses import JSONResponse

from plot_mcp.broadcast import BroadcastHub
from plot_mcp.chat_provider import read_selection
from plot_mcp.chat_providers.base import DEFAULT_CHAT_SCOPE, ChatScope
from plot_mcp.chat_session import ChatProvider, ChatSessionRegistry, chat_registry
from plot_mcp.workspace import resolve_plot_root

_VALID_SCOPES: frozenset[str] = frozenset(get_args(ChatScope))


def _read_scope(body: dict[str, Any]) -> ChatScope | None:
    """Pull ``scope`` from a request body.

    Missing → the shared ``project`` bucket (Postel, Q1). Present but not a
    known scope → ``None`` to signal the caller should 400 (Fail Fast on a
    typo before it silently creates an unreachable session).
    """
    raw = body.get("scope")
    if raw is None:
        return DEFAULT_CHAT_SCOPE
    if isinstance(raw, str) and raw in _VALID_SCOPES:
        return raw  # type: ignore[return-value]
    return None

_log = logging.getLogger(__name__)

# Event name carried on the WS payload. Viewer demultiplexes on ``event``;
# the existing project_changed payload uses ``"project_changed"``.
_CHAT_EVENT = "chat_stream_event"

# Provider that the in-app chat refuses to spawn (D-2026-06-13-H). Kept in
# the MCP-registration surface, dropped from chat send.
_CHAT_EXCLUDED_PROVIDER = "claude-code"


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
    scope: ChatScope = DEFAULT_CHAT_SCOPE,
) -> None:
    """Pull stream events from ``provider`` and fan them out to ``plot_root``.

    Lives outside the endpoint so it stays directly testable. Each event is
    stamped with ``scope`` (overriding the provider's default) so the viewer
    can route it to the matching canvas thread (D-2026-06-13-H). Errors are
    caught + broadcast as an ``error`` event so the viewer can surface them
    instead of silently truncating the turn.
    """
    try:
        async for event in provider.stream_turn(user_message):
            payload = event.model_dump()
            payload["scope"] = scope
            await hub.notify_event(plot_root, _CHAT_EVENT, payload)
    except Exception as exc:  # noqa: BLE001 — boundary catch
        _log.exception("chat turn crashed for %s", plot_root)
        await hub.notify_event(
            plot_root,
            _CHAT_EVENT,
            {
                "type": "error",
                "turn_id": "",
                "error_message": f"chat turn crashed: {exc}",
                "scope": scope,
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

    scope = _read_scope(body)
    if scope is None:
        return JSONResponse({"error": "invalid chat scope"}, status_code=400)

    try:
        plot_root = resolve_plot_root(project_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)

    # The workspace's persisted CLI choice drives which provider runs the
    # turn. Without a choice the dock should be in its "pick a CLI" state
    # anyway — surface a 400 so a misbehaving viewer can't silently spawn a
    # default we never agreed on.
    selection = read_selection(plot_root)
    if selection.provider is None:
        return JSONResponse(
            {"error": "no chat provider selected"}, status_code=400
        )
    # claude-code is excluded from the in-app chat (D-2026-06-13-H): driving
    # it via ``claude -p`` bills a Claude subscriber a second time on top of
    # their subscription. It stays in the MCP-registration list so the user
    # can connect their own interactive Claude session — Plot just won't host
    # it. A viewer that never offers claude-code in the chat radio can't reach
    # here; this guard is the server-side backstop.
    if selection.provider == _CHAT_EXCLUDED_PROVIDER:
        return JSONResponse(
            {
                "error": (
                    "claude-code is not available for in-app chat; connect it "
                    "via MCP instead"
                )
            },
            status_code=400,
        )

    hub = _hub_from_request(request)
    if hub is None:
        return JSONResponse(
            {"error": "broadcast hub not configured"}, status_code=500
        )

    registry = _registry_from_request(request)
    provider = registry.get_or_create(plot_root, selection.provider, scope)

    asyncio.create_task(
        stream_chat_turn(provider, hub, plot_root, message, scope)
    )
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
    scope = _read_scope(body)
    if scope is None:
        return JSONResponse({"error": "invalid chat scope"}, status_code=400)
    try:
        plot_root = resolve_plot_root(project_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    registry = _registry_from_request(request)
    # Wipe only the active canvas thread across all providers (Q3); other
    # scopes' conversations survive.
    registry.reset(plot_root, scope=scope)
    return JSONResponse({"reset": True})
