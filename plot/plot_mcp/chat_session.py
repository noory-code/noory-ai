"""R7 chat — CLI subprocess driver (D-2026-06-12-D, Phase C step C1).

This is the engine-side seam that turns a user's chat message into a streamed
assistant response. The conversation *brain* is the user's external CLI
(``claude``, ``codex``, ``gemini`` — D-2026-06-11-E); Plot never touches API
keys or model selection.

Shape:

  ``ChatProvider``       — abstract per-CLI driver. One method,
                           ``stream_turn(user_message)``, yields
                           ``ChatStreamEvent`` instances.
  ``ClaudeCodeProvider`` — concrete: spawns
                           ``claude --print --output-format stream-json``
                           per turn, parses the JSON event stream, keeps
                           conversation continuity via ``--session-id`` +
                           ``--resume``.
  ``ChatSessionRegistry`` — one provider instance per workspace path, lazily
                            created on first use, dropped on ``reset``.

Subprocess invocation is injected (``subprocess_factory``) so tests stay
hermetic — only the end-to-end smoke (Phase C step C7) actually spawns
``claude``. The factory signature matches ``asyncio.create_subprocess_exec``.
"""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path
from typing import Any, Literal, Protocol
from uuid import uuid4

from pydantic import BaseModel

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Wire types
# ---------------------------------------------------------------------------


ChatStreamEventType = Literal["turn_start", "delta", "turn_complete", "error"]


class ChatStreamEvent(BaseModel):
    """One streamed event in a chat turn.

    The viewer renders ``turn_start`` as "an assistant turn is forming", each
    ``delta`` appends ``text`` to the active turn, ``turn_complete`` carries
    the full accumulated text (so a late-joining subscriber can reconcile),
    and ``error`` aborts the turn and surfaces ``error_message`` in the UI.
    """

    type: ChatStreamEventType
    turn_id: str
    text: str = ""
    error_message: str | None = None


# ---------------------------------------------------------------------------
# Provider abstract + Claude Code concrete
# ---------------------------------------------------------------------------


class _SubprocessFactory(Protocol):
    """Match the slice of ``asyncio.create_subprocess_exec`` we need.

    Defined as a Protocol so callers can pass a fake in tests without faking
    every keyword argument the stdlib version accepts.
    """

    def __call__(
        self,
        *cmd: str,
        cwd: str | None = ...,
        stdout: int | None = ...,
        stderr: int | None = ...,
    ) -> Awaitable[Any]: ...


class ChatProvider(ABC):
    """Drives one external CLI for one workspace."""

    @abstractmethod
    def stream_turn(self, user_message: str) -> AsyncIterator[ChatStreamEvent]:
        """Send one user message, yield assistant stream events.

        Implementations MUST yield ``turn_start`` first and end with either
        ``turn_complete`` (success) or ``error`` (failure). If the consumer
        closes the iterator early, the underlying process is killed.
        """
        ...


class ClaudeCodeProvider(ChatProvider):
    """One subprocess per turn, conversation continuity via ``--session-id``.

    ``claude --print`` reads its prompt as the trailing positional argument
    and emits one JSON object per line on stdout when called with
    ``--output-format stream-json --include-partial-messages``. The first
    turn passes ``--session-id <uuid>`` to mint a new conversation; every
    later turn passes ``--resume <uuid>`` so the CLI loads its persisted
    transcript and the conversation continues naturally.
    """

    def __init__(
        self,
        workspace_root: Path,
        *,
        session_id: str | None = None,
        cli_path: str = "claude",
        subprocess_factory: _SubprocessFactory | None = None,
    ) -> None:
        self._workspace = workspace_root
        self._session_id = session_id or str(uuid4())
        self._cli_path = cli_path
        self._first_turn = True
        # Resolve at call time so tests can swap in a fake. The default lambda
        # is intentionally typed loosely; the Protocol pins the call shape.
        self._spawn: _SubprocessFactory = (
            subprocess_factory
            if subprocess_factory is not None
            else _default_spawn
        )

    @property
    def session_id(self) -> str:
        return self._session_id

    async def stream_turn(
        self, user_message: str
    ) -> AsyncIterator[ChatStreamEvent]:
        turn_id = str(uuid4())
        cmd = self._build_command(user_message)

        proc = await self._spawn(
            *cmd,
            cwd=str(self._workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # After the first successful spawn, subsequent turns must --resume.
        # We flip the flag here (before reading output) so a crash mid-stream
        # still leaves the CLI's session store intact for the next turn.
        self._first_turn = False

        yield ChatStreamEvent(type="turn_start", turn_id=turn_id)
        accumulator: list[str] = []
        try:
            if proc.stdout is not None:
                async for line in proc.stdout:
                    event = _parse_stream_line(turn_id, line, accumulator)
                    if event is not None:
                        yield event
            rc = await proc.wait()
            if rc != 0:
                stderr_text = ""
                if proc.stderr is not None:
                    raw = await proc.stderr.read()
                    stderr_text = raw.decode("utf-8", errors="replace").strip()
                yield ChatStreamEvent(
                    type="error",
                    turn_id=turn_id,
                    error_message=stderr_text or f"{self._cli_path} exited {rc}",
                )
            else:
                yield ChatStreamEvent(
                    type="turn_complete",
                    turn_id=turn_id,
                    text="".join(accumulator),
                )
        finally:
            # If the consumer cancelled mid-stream the process may still be
            # alive; kill it so we don't leak a CLI invocation per abandoned
            # turn. ``returncode is None`` means ``wait`` never returned.
            if proc.returncode is None:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass

    def _build_command(self, user_message: str) -> list[str]:
        cmd = [
            self._cli_path,
            "--print",
            "--output-format",
            "stream-json",
            "--include-partial-messages",
            "--verbose",  # stream-json requires verbose mode
        ]
        if self._first_turn:
            cmd += ["--session-id", self._session_id]
        else:
            cmd += ["--resume", self._session_id]
        cmd.append(user_message)
        return cmd


async def _default_spawn(
    *cmd: str,
    cwd: str | None = None,
    stdout: int | None = None,
    stderr: int | None = None,
) -> asyncio.subprocess.Process:
    """Thin wrapper around ``asyncio.create_subprocess_exec`` so the type of
    the default factory exactly matches the ``_SubprocessFactory`` protocol.
    """
    return await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=stdout,
        stderr=stderr,
    )


# ---------------------------------------------------------------------------
# Stream-json parser
# ---------------------------------------------------------------------------


def _parse_stream_line(
    turn_id: str, line: bytes, accumulator: list[str]
) -> ChatStreamEvent | None:
    """Decode one ``stream-json`` line into a ``delta`` event or ``None``.

    Two text-bearing shapes survive the filter (the rest — ``system init``,
    ``tool_use``, ``result`` wrapper, etc. — produce ``None``):

      1. Full assistant message:
         ``{"type": "assistant", "message": {"content": [{"type":"text", ...}]}}``
      2. Partial delta (with ``--include-partial-messages``):
         ``{"type": "stream_event", "event": {"type":"content_block_delta",
           "delta": {"type":"text_delta", "text": "..."}}}``

    Any ``text`` extracted is appended to ``accumulator`` so the eventual
    ``turn_complete`` event can carry the full assistant message — useful for
    a late-joining viewer that missed earlier deltas.
    """
    raw = line.decode("utf-8", errors="replace").strip()
    if not raw:
        return None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    text = _extract_text(obj)
    if not text:
        return None
    accumulator.append(text)
    return ChatStreamEvent(type="delta", turn_id=turn_id, text=text)


def _extract_text(obj: dict[str, Any]) -> str:
    """Pull text out of any of the known assistant-text frame shapes."""
    msg = obj.get("message")
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "text":
                    continue
                t = item.get("text")
                if isinstance(t, str):
                    parts.append(t)
            if parts:
                return "".join(parts)
    event = obj.get("event")
    if isinstance(event, dict):
        delta = event.get("delta")
        if isinstance(delta, dict) and delta.get("type") == "text_delta":
            t = delta.get("text")
            if isinstance(t, str):
                return t
    return ""


# ---------------------------------------------------------------------------
# Session registry
# ---------------------------------------------------------------------------


ProviderFactory = Callable[[Path], ChatProvider]


class ChatSessionRegistry:
    """One ``ChatProvider`` instance per resolved workspace path.

    The registry's only responsibility is identity continuity — call
    ``get_or_create`` twice for the same workspace and you get the same
    provider, so the second turn correctly ``--resume``s the first turn's
    CLI session. ``reset`` drops the provider so the next call starts a
    fresh conversation.
    """

    def __init__(self, *, factory: ProviderFactory | None = None) -> None:
        self._sessions: dict[Path, ChatProvider] = {}
        self._factory: ProviderFactory = factory or (
            lambda root: ClaudeCodeProvider(workspace_root=root)
        )

    def get_or_create(self, workspace_root: Path) -> ChatProvider:
        key = workspace_root.resolve()
        provider = self._sessions.get(key)
        if provider is None:
            provider = self._factory(key)
            self._sessions[key] = provider
        return provider

    def reset(self, workspace_root: Path) -> None:
        self._sessions.pop(workspace_root.resolve(), None)

    def session_count(self) -> int:
        return len(self._sessions)


# ---------------------------------------------------------------------------
# Module-level singleton — the engine has one registry per process.
# ---------------------------------------------------------------------------


_REGISTRY = ChatSessionRegistry()


def chat_registry() -> ChatSessionRegistry:
    return _REGISTRY
