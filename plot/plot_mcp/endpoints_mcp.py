"""External-CLI MCP registration endpoints (D-2026-06-11-E, Track 2.5).

Three URLs back the R7 chat panel's "connect Plot to your CLI" UX:

    GET  /api/mcp/providers              — list providers + status
    POST /api/mcp/providers/{name}/register
    POST /api/mcp/providers/{name}/unregister

Workspace-scoped via ``project_path`` so the endpoints sit alongside the
rest of the API surface, even though MCP registration itself is a
user-global edit to ``~/.<cli>/config…``.
"""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from plot_mcp.endpoints_common import _error
from plot_mcp.mcp_registration import (
    ProviderName,
    detect_providers,
    plot_plugin_root,
    register_plot,
    unregister_plot,
)


async def mcp_providers_endpoint(_request: Request) -> JSONResponse:
    """``GET /api/mcp/providers`` — one row per supported provider.

    Each row: ``{name, installed, registered, config_path}``. The viewer's
    chat panel reads this once on open and re-reads after a
    register/unregister to refresh button state.
    """
    statuses = detect_providers()
    return JSONResponse(
        {
            "providers": [
                {
                    "name": s.name,
                    "installed": s.installed,
                    "registered": s.registered,
                    "config_path": s.config_path,
                }
                for s in statuses.values()
            ]
        }
    )


_VALID_PROVIDERS: frozenset[str] = frozenset({"claude-code", "codex", "gemini"})


def _provider_from_path(request: Request) -> ProviderName | None:
    raw = request.path_params.get("provider", "")
    if raw == "claude-code":
        return "claude-code"
    if raw == "codex":
        return "codex"
    if raw == "gemini":
        return "gemini"
    return None


async def mcp_register_endpoint(request: Request) -> JSONResponse:
    """``POST /api/mcp/providers/{provider}/register`` — add the Plot mcp
    server entry to the named provider's config. Idempotent."""
    provider = _provider_from_path(request)
    if provider is None:
        return _error(f"unknown provider: {request.path_params.get('provider')!r}", status=404)
    try:
        register_plot(provider, plot_plugin_root())
    except OSError as exc:
        return _error(f"failed to write provider config: {exc}", status=500)
    return JSONResponse({"ok": True, "provider": provider}, status_code=201)


async def mcp_unregister_endpoint(request: Request) -> JSONResponse:
    """``POST /api/mcp/providers/{provider}/unregister`` — drop the Plot
    entry from the provider's config. Idempotent."""
    provider = _provider_from_path(request)
    if provider is None:
        return _error(f"unknown provider: {request.path_params.get('provider')!r}", status=404)
    try:
        unregister_plot(provider)
    except OSError as exc:
        return _error(f"failed to write provider config: {exc}", status=500)
    return JSONResponse({"ok": True, "provider": provider})
