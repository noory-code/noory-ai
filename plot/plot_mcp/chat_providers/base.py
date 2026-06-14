"""Shared subprocess-driving base for every CLI chat provider.

This module owns the public wire types (``ChatStreamEvent``,
``ChatStreamEventType``, ``ChatProvider`` ABC) and the spawn-parse-yield
loop (``_SubprocessChatProvider``). Concrete per-CLI classes live in
sibling modules and only override two small hooks.
"""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable
from pathlib import Path
from typing import Any, Literal, Protocol
from uuid import uuid4

from pydantic import BaseModel

ChatStreamEventType = Literal["turn_start", "delta", "turn_complete", "error"]

# Conversation scope (D-2026-06-13-H). Chat threads are partitioned per
# canvas kind plus one shared ``project`` scope for cross-canvas work. The
# viewer sends the active scope on each turn and demultiplexes incoming
# events on it; the engine keys sessions on (workspace, provider, scope).
# Parity with the TS ``ChatScope`` union is pinned by
# ``tests/test_chat_scope_parity.py``.
ChatScope = Literal[
    "project",
    "foundation",
    "actors",
    "services",
    "service_detail",
]

# Scope assumed when a client omits it on the wire (Postel's Law,
# D-2026-06-13-H Q1) — cross-canvas work lands in the shared bucket.
DEFAULT_CHAT_SCOPE: ChatScope = "project"


class ChatStreamEvent(BaseModel):
    """One streamed event in a chat turn.

    The viewer renders ``turn_start`` as "an assistant turn is forming", each
    ``delta`` appends ``text`` to the active turn, ``turn_complete`` carries
    the full accumulated text (so a late-joining subscriber can reconcile),
    and ``error`` aborts the turn and surfaces ``error_message`` in the UI.

    ``scope`` echoes which conversation bucket the turn belongs to so the
    viewer can route the event to the matching canvas thread (D-2026-06-13-H).
    """

    type: ChatStreamEventType
    turn_id: str
    text: str = ""
    error_message: str | None = None
    scope: ChatScope = DEFAULT_CHAT_SCOPE


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


class _SubprocessChatProvider(ChatProvider):
    """Shared spawn → parse → yield loop for every CLI-backed provider.

    Subclasses override two hooks:

      * ``_build_command(user_message)`` — produce the argv. Subclasses use
        ``self._first_turn`` and ``self._session_id`` (which they may have
        captured from earlier output) to switch between "start a new
        session" and "resume the previous one".
      * ``_parse_line(turn_id, line, accumulator)`` — turn one stdout line
        into a ``ChatStreamEvent`` (``delta`` only — ``turn_start`` /
        ``turn_complete`` / ``error`` are emitted by this base). Subclasses
        may mutate ``self._session_id`` when they spot the CLI's
        session-id event (codex ``thread.started``, gemini ``init``, …).
    """

    def __init__(
        self,
        workspace_root: Path,
        *,
        cli_path: str,
        subprocess_factory: _SubprocessFactory | None = None,
    ) -> None:
        self._workspace = workspace_root
        self._cli_path = cli_path
        self._first_turn = True
        self._session_id: str | None = None
        self._spawn: _SubprocessFactory = (
            subprocess_factory
            if subprocess_factory is not None
            else _default_spawn
        )

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @abstractmethod
    def _build_command(self, user_message: str) -> list[str]: ...

    @abstractmethod
    def _parse_line(
        self, turn_id: str, line: bytes, accumulator: list[str]
    ) -> ChatStreamEvent | None: ...

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

        # Flip the first-turn flag before reading output so a crash mid-stream
        # still leaves the CLI's session store intact for the next turn.
        self._first_turn = False

        yield ChatStreamEvent(type="turn_start", turn_id=turn_id)
        accumulator: list[str] = []
        try:
            if proc.stdout is not None:
                async for line in proc.stdout:
                    event = self._parse_line(turn_id, line, accumulator)
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
                    error_message=stderr_text
                    or f"{self._cli_path} exited {rc}",
                )
            else:
                yield ChatStreamEvent(
                    type="turn_complete",
                    turn_id=turn_id,
                    text="".join(accumulator),
                )
        finally:
            if proc.returncode is None:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass


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


def _decode_jsonl(line: bytes) -> dict[str, Any] | None:
    """Strict line → dict decode. Skips blank lines + JSON errors silently."""
    raw = line.decode("utf-8", errors="replace").strip()
    if not raw:
        return None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    return obj
