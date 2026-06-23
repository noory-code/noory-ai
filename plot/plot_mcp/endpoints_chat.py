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
from typing import Any, cast

from starlette.requests import Request
from starlette.responses import JSONResponse

from plot_mcp.broadcast import BroadcastHub
from plot_mcp.chat_context import (
    build_context_preamble,
    build_framing_preamble,
    build_system_prompt,
)
from plot_mcp.chat_models import list_models
from plot_mcp.chat_provider import read_selection
from plot_mcp.chat_providers.base import DEFAULT_CHAT_SCOPE, is_valid_scope
from plot_mcp.chat_selection import render_selection_detail
from plot_mcp.chat_session import ChatProvider, ChatSessionRegistry, chat_registry
from plot_mcp.mcp_registration import ProviderName
from plot_mcp.workspace import resolve_plot_root

# Re-exported for back-compat — callers/tests historically import these two
# builders from this module; the SSOT now lives in ``chat_context`` so the MCP
# path can share them without importing the HTTP layer (D-2026-06-15-D).
__all__ = [
    "build_context_preamble",
    "build_framing_preamble",
    "chat_send_endpoint",
    "chat_reset_endpoint",
    "chat_models_endpoint",
    "stream_chat_turn",
]

# Runtime guard for the `provider` query param (ProviderName is a static
# Literal, so this is its runtime mirror).
_MODEL_PROVIDERS: frozenset[str] = frozenset({"claude-code", "codex"})


async def chat_models_endpoint(request: Request) -> JSONResponse:
    """``GET /api/chat/models?provider=<name>`` — the model catalogue for one
    provider (D-2026-06-22-B), pulled live from the CLI's own source
    (``agy models`` / codex cache) or the static claude aliases. Fail-soft: a
    bad / absent source yields ``{"models": []}`` so the selector falls back to
    its Custom… entry. Unknown / missing provider → 400.
    """
    raw = request.query_params.get("provider", "")
    if raw not in _MODEL_PROVIDERS:
        return JSONResponse({"error": f"unknown chat provider: {raw!r}"}, status_code=400)
    provider = cast(ProviderName, raw)
    # list_models may shell out (gemini → `agy models`) or read a file (codex
    # cache), so run it off the event loop.
    models = await asyncio.to_thread(list_models, provider)
    return JSONResponse({"models": [m.model_dump() for m in models]})


def _read_scope(body: dict[str, Any]) -> str | None:
    """Pull ``scope`` from a request body.

    Missing → the shared ``project`` bucket (Postel, Q1). Present but not a
    well-formed scope → ``None`` to signal the caller should 400 (Fail Fast on
    a typo before it silently creates an unreachable session). A valid scope is
    a base member or a parametric ``feature:<id>`` (Layer 1,
    D-2026-06-15-B), returned verbatim as the session key.
    """
    raw = body.get("scope")
    if raw is None:
        return DEFAULT_CHAT_SCOPE
    if isinstance(raw, str) and is_valid_scope(raw):
        return raw
    return None


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
    scope: str = DEFAULT_CHAT_SCOPE,
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
        return JSONResponse({"error": "project_path required"}, status_code=400)
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
        return JSONResponse({"error": "no chat provider selected"}, status_code=400)
    # claude-code is allowed for in-app chat (D-2026-06-14-B, reversing
    # D-2026-06-13-H). Running it via ``claude -p`` bills separately from the
    # Claude subscription; that tradeoff is surfaced as a UI warning rather
    # than a hard server-side block, so the user opts in with eyes open.

    hub = _hub_from_request(request)
    if hub is None:
        return JSONResponse({"error": "broadcast hub not configured"}, status_code=500)

    registry = _registry_from_request(request)
    provider = registry.get_or_create(plot_root, selection.provider, scope)
    # Apply the workspace's model override (D-2026-06-16-C) before the turn —
    # ``None`` / empty leaves the CLI on its own configured default.
    provider.set_model(selection.model)
    # Lever 2 (docs/idea/chat/01-levers.md) — the Layer-3 framing + hallucination
    # guard go to the CLI as an authoritative system prompt, not glued into the
    # user message. The provider maps it per CLI (claude flag / codex prepend).
    provider.set_system_prompt(build_system_prompt(scope))

    # The user message carries Layer 2 ahead of the user's text: the selection
    # header (which canvas + what is selected) followed by the selected nodes'
    # actual content read engine-side (Lever 1a) so "polish this" resolves to the
    # real node text rather than something the agent invents. Each builder is ""
    # when it has nothing to add (e.g. the cross-canvas ``project`` scope), so
    # only non-empty parts are joined.
    selection_nodes = body.get("selection")
    context = build_context_preamble(scope, selection_nodes)
    detail = render_selection_detail(plot_root, scope, selection_nodes)
    full_message = "\n\n".join(p for p in (context, detail, message) if p)

    asyncio.create_task(stream_chat_turn(provider, hub, plot_root, full_message, scope))
    return JSONResponse({"accepted": True}, status_code=202)


async def chat_reset_endpoint(request: Request) -> JSONResponse:
    """``POST /api/chat/reset`` — drop the workspace's cached CLI session."""
    try:
        body: dict[str, Any] = await request.json()
    except ValueError:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)
    project_path = body.get("project_path")
    if not isinstance(project_path, str) or not project_path:
        return JSONResponse({"error": "project_path required"}, status_code=400)
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
