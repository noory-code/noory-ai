"""R7 chat — public surface (D-2026-06-12-D + v0.64.1).

Thin facade over ``plot_mcp.chat_providers/*``. Exports the wire types
(``ChatStreamEvent``, ``ChatStreamEventType``), the ABC (``ChatProvider``),
each concrete CLI driver (``ClaudeCodeProvider`` / ``CodexProvider`` /
``GeminiProvider``), and the per-process registry (``ChatSessionRegistry``
+ ``chat_registry()`` accessor). The split happened to keep every file
under the engine's 500-line module rule once Codex and Gemini joined the
party; callers see one import surface.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from plot_mcp.chat_providers.base import (
    ChatProvider,
    ChatStreamEvent,
    ChatStreamEventType,
)
from plot_mcp.chat_providers.claude_code import ClaudeCodeProvider, _parse_claude_line
from plot_mcp.chat_providers.codex import CodexProvider
from plot_mcp.chat_providers.gemini import GeminiProvider
from plot_mcp.mcp_registration import ProviderName

# Back-compat alias — v0.64.0 tests imported ``_parse_stream_line`` from
# this module. The concrete function lives in ``chat_providers.claude_code``
# now (which is the only caller that matters), but the alias stays so any
# external integration code keeps linking.
_parse_stream_line = _parse_claude_line


__all__ = [
    "ChatProvider",
    "ChatSessionRegistry",
    "ChatStreamEvent",
    "ChatStreamEventType",
    "ClaudeCodeProvider",
    "CodexProvider",
    "GeminiProvider",
    "chat_registry",
    "_parse_stream_line",
]


# ---------------------------------------------------------------------------
# Session registry — keyed by (workspace, provider) so the user can switch
# CLIs and come back without losing either conversation.
# ---------------------------------------------------------------------------


ProviderFactory = Callable[[Path, ProviderName], ChatProvider]


def _default_provider_factory(
    workspace_root: Path, provider_name: ProviderName
) -> ChatProvider:
    if provider_name == "claude-code":
        return ClaudeCodeProvider(workspace_root=workspace_root)
    if provider_name == "codex":
        return CodexProvider(workspace_root=workspace_root)
    if provider_name == "gemini":
        return GeminiProvider(workspace_root=workspace_root)
    # ``ProviderName`` is a Literal — mypy enforces; this is the runtime
    # safety net for an unexpected value (corrupt selection file, future
    # provider added to the literal but not here).
    raise ValueError(f"unsupported chat provider: {provider_name!r}")


class ChatSessionRegistry:
    """One ``ChatProvider`` instance per (resolved workspace path, provider).

    Keying on the pair (not just the path) means a user who switches Claude
    → Codex → Claude in one session resumes both Claude and Codex
    conversations cleanly, instead of overwriting whichever was cached. The
    registry's only responsibility is identity continuity — call
    ``get_or_create`` twice with the same pair and you get the same provider.
    """

    def __init__(self, *, factory: ProviderFactory | None = None) -> None:
        self._sessions: dict[tuple[Path, ProviderName], ChatProvider] = {}
        self._factory: ProviderFactory = factory or _default_provider_factory

    def get_or_create(
        self, workspace_root: Path, provider_name: ProviderName
    ) -> ChatProvider:
        key = (workspace_root.resolve(), provider_name)
        provider = self._sessions.get(key)
        if provider is None:
            provider = self._factory(key[0], provider_name)
            self._sessions[key] = provider
        return provider

    def reset(
        self,
        workspace_root: Path,
        provider_name: ProviderName | None = None,
    ) -> None:
        """Drop one provider's session — or every provider's session for the
        workspace if ``provider_name`` is ``None``. The endpoint's
        ``/api/chat/reset`` calls the all-providers form by default so the
        user gets a single "wipe my chat state" affordance instead of a
        per-CLI matrix in the dock.
        """
        resolved = workspace_root.resolve()
        if provider_name is None:
            self._sessions = {
                k: v for k, v in self._sessions.items() if k[0] != resolved
            }
        else:
            self._sessions.pop((resolved, provider_name), None)

    def session_count(self) -> int:
        return len(self._sessions)


# ---------------------------------------------------------------------------
# Module-level singleton — the engine has one registry per process.
# ---------------------------------------------------------------------------


_REGISTRY = ChatSessionRegistry()


def chat_registry() -> ChatSessionRegistry:
    return _REGISTRY
