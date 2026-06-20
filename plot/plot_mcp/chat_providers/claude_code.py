"""Claude Code CLI driver (``claude --print``).

The first turn passes ``--session-id <uuid>`` so Plot mints the
conversation id; every later turn passes ``--resume <uuid>`` so the CLI
loads its persisted transcript and the conversation continues naturally.
``--include-partial-messages`` flips the JSONL stream into incremental
``content_block_delta`` events so the dock shows text as it's produced.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from plot_mcp.chat_providers.base import (
    ChatStreamEvent,
    _decode_jsonl,
    _SubprocessChatProvider,
    _SubprocessFactory,
)


class ClaudeCodeProvider(_SubprocessChatProvider):
    """One subprocess per turn, conversation continuity via ``--session-id``."""

    def __init__(
        self,
        workspace_root: Path,
        *,
        session_id: str | None = None,
        cli_path: str = "claude",
        subprocess_factory: _SubprocessFactory | None = None,
    ) -> None:
        super().__init__(
            workspace_root,
            cli_path=cli_path,
            subprocess_factory=subprocess_factory,
        )
        # Claude is the only CLI where Plot mints the session id; the others
        # report theirs through the first event of the first turn.
        self._session_id = session_id or str(uuid4())

    def _build_command(self, user_message: str) -> list[str]:
        cmd = [
            self._cli_path,
            "--print",
            "--output-format",
            "stream-json",
            "--include-partial-messages",
            "--verbose",  # stream-json requires verbose mode
            *self._model_args(),
        ]
        if self._first_turn:
            assert self._session_id is not None  # ctor guarantees this
            cmd += ["--session-id", self._session_id]
        else:
            assert self._session_id is not None
            cmd += ["--resume", self._session_id]
        cmd.append(user_message)
        return cmd

    def _parse_line(
        self, turn_id: str, line: bytes, accumulator: list[str]
    ) -> ChatStreamEvent | None:
        return _parse_claude_line(turn_id, line, accumulator)


def _parse_claude_line(
    turn_id: str, line: bytes, accumulator: list[str]
) -> ChatStreamEvent | None:
    """Decode one Claude Code ``stream-json`` line into a ``delta`` event.

    Streaming text comes from the **partial** frames only (D-2026-06-21-B):
      ``{"type":"stream_event", "event":{"type":"content_block_delta",
         "delta":{"type":"text_delta", "text":"..."}}}``

    With ``--include-partial-messages`` the CLI ALSO emits a final full
    ``assistant`` recap message carrying the same complete block text. Counting
    both doubles the reply ("살펴볼게요.살펴볼게요."), so the recap is ignored
    here — the partials are the single source of the streamed text.
    """
    obj = _decode_jsonl(line)
    if obj is None:
        return None
    text = _extract_anthropic_text(obj)
    if not text:
        return None
    accumulator.append(text)
    return ChatStreamEvent(type="delta", turn_id=turn_id, text=text)


def _extract_anthropic_text(obj: dict[str, Any]) -> str:
    """Streamed text from a partial ``content_block_delta`` frame, or ``""``.

    The full ``assistant`` recap message is intentionally NOT a source — the
    partials already carry the complete text, and counting the recap doubles
    the reply (D-2026-06-21-B)."""
    event = obj.get("event")
    if isinstance(event, dict):
        delta = event.get("delta")
        if isinstance(delta, dict) and delta.get("type") == "text_delta":
            t = delta.get("text")
            if isinstance(t, str):
                return t
    return ""
